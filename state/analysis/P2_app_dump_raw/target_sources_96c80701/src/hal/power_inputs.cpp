// Owns fixed ADC calls and retains battery evidence with bounded source age.
// Shared fault latching prevents either input from outliving a failed ADC owner.
// Independent port, native-pair and Robot/MotorGate tests verify D093 behavior.
#include "power_inputs.h"
#include "../config.h"
#include <cmath>
#include <limits>

namespace power {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
constexpr std::uint16_t RAW_MAX = 16383U;

bool known(Status status, Shutdown shutdown) {
    return static_cast<unsigned>(status) <= static_cast<unsigned>(Status::NOT_ENABLED) &&
        static_cast<unsigned>(shutdown) <= static_cast<unsigned>(Shutdown::UNCONFIRMED);
}

InputFault sampleFault(Status status, Shutdown shutdown, bool valid) {
    if (!known(status, shutdown) || valid != (status == Status::OK)) return InputFault::SOURCE;
    if (status != Status::OK) return InputFault::ADC;
    return shutdown == Shutdown::NOT_ATTEMPTED ? InputFault::NONE : InputFault::SOURCE;
}

std::uint32_t addSaturated(std::uint32_t value, std::uint32_t delta) {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    return delta > maximum - value ? maximum : value + delta;
}

void increment(std::uint32_t& value) { value = addSaturated(value, 1U); }

void increment(std::uint64_t& value) {
    if (value != std::numeric_limits<std::uint64_t>::max()) ++value;
}

bool voltageMatches(const Sample& sample) {
    const float scaled = static_cast<float>(sample.raw) / 16383.0F *
        config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
    return std::isfinite(sample.voltage_v) && sample.voltage_v == scaled;
}
} // namespace

InputOwner::InputOwner(const InputPort& port) : port_(port) {}

bool InputOwner::validPort() const {
    return port_.beginWithButtons != nullptr && port_.readA0 != nullptr &&
        port_.readA1 != nullptr && port_.clockUs != nullptr;
}

bool InputOwner::validConfig() const {
    return config::VBAT_ADC_CONVERSION_US > 0U &&
        config::VBAT_ADC_CONVERSION_US <= config::VBAT_SAMPLE_PERIOD_US &&
        config::VBAT_SAMPLE_PERIOD_US < config::VBAT_SAMPLE_MAX_AGE_US &&
        config::VBAT_SAMPLE_MAX_AGE_US < HALF_RANGE &&
        std::isfinite(config::VBAT_ADC_REFERENCE_V) &&
        config::VBAT_ADC_REFERENCE_V > 2.4F && config::VBAT_ADC_REFERENCE_V <= 3.6F &&
        std::isfinite(config::VBAT_DIVIDER_RATIO) && config::VBAT_DIVIDER_RATIO >= 1.0F;
}

void InputOwner::fail(InputFault fault, InputOperation operation, Status status, Shutdown shutdown) {
    if (report_.fault != InputFault::NONE) return;
    report_.fault = fault;
    report_.fault_operation = operation;
    report_.first_status = status;
    report_.first_shutdown = shutdown;
    report_.ready = false;
    updateAvailability();
}

void InputOwner::updateAvailability() {
    const bool healthy = report_.ready && report_.fault == InputFault::NONE;
    report_.battery_available = healthy && battery_seen_ &&
        report_.battery_age_us < config::VBAT_SAMPLE_MAX_AGE_US;
    report_.battery_due = healthy && (!battery_seen_ ||
        report_.battery_age_us >= config::VBAT_SAMPLE_PERIOD_US);
}

bool InputOwner::advance(std::uint32_t now, InputOperation operation) {
    if (!report_.attempted || report_.fault != InputFault::NONE) return false;
    const auto delta = now - report_.observed_us;
    if (observed_ && delta >= HALF_RANGE) {
        fail(InputFault::CLOCK, operation, Status::NOT_INITIALIZED, Shutdown::NOT_ATTEMPTED);
        return false;
    }
    if (observed_ && battery_seen_)
        report_.battery_age_us = addSaturated(report_.battery_age_us, delta);
    observed_ = true;
    report_.observed_us = now;
    updateAvailability();
    return true;
}

bool InputOwner::interval(std::uint32_t before, std::uint32_t started,
                          std::uint32_t completed, std::uint32_t after) const {
    const auto duration = after - before;
    const auto start_offset = started - before;
    const auto completion_offset = completed - before;
    return duration < HALF_RANGE && start_offset <= completion_offset &&
        completion_offset <= duration && completed - started < config::VBAT_ADC_CONVERSION_US;
}

bool InputOwner::begin() {
    if (report_.attempted) return false;
    report_.attempted = true;
    if (!validPort() || !validConfig()) {
        fail(!validPort() ? InputFault::PORT : InputFault::CONFIG, InputOperation::SETUP,
             Status::NOT_INITIALIZED, Shutdown::NOT_ATTEMPTED);
        return false;
    }
    const auto before = port_.clockUs(port_.context);
    advance(before, InputOperation::SETUP);
    report_.setup = port_.beginWithButtons(port_.context);
    const auto after = port_.clockUs(port_.context);
    const auto setup = report_.setup;
    auto fault = InputFault::NONE;
    if (!known(setup.status, setup.shutdown)) fault = InputFault::SOURCE;
    else if (setup.status != Status::OK) fault = InputFault::SETUP;
    else if (!setup.ready || setup.shutdown != Shutdown::NOT_ATTEMPTED) fault = InputFault::SOURCE;
    if (fault == InputFault::NONE && after - before >= HALF_RANGE) fault = InputFault::CLOCK;
    if (after - before < HALF_RANGE) advance(after, InputOperation::SETUP);
    if (fault != InputFault::NONE) {
        fail(fault, InputOperation::SETUP, setup.status, setup.shutdown);
        return false;
    }
    report_.ready = true;
    updateAvailability();
    return true;
}

BatteryRead InputOwner::readBatteryIfDue(bool slot_granted) {
    BatteryRead result;
    if (!report_.ready || report_.fault != InputFault::NONE) return result;
    const auto before = port_.clockUs(port_.context);
    if (!advance(before, InputOperation::BATTERY) || !report_.battery_due) return result;
    if (!slot_granted) { increment(report_.battery_refused); return result; }
    increment(report_.battery_attempts);
    result.attempted = true;
    result.sample = port_.readA0(port_.context);
    const auto after = port_.clockUs(port_.context);
    const auto& sample = result.sample;
    auto fault = sampleFault(sample.status, sample.shutdown, sample.valid);
    if (fault == InputFault::NONE && after - before >= HALF_RANGE) fault = InputFault::CLOCK;
    if (after - before < HALF_RANGE) advance(after, InputOperation::BATTERY);
    if (fault == InputFault::NONE && (sample.raw > RAW_MAX || !voltageMatches(sample) ||
        !interval(before, sample.started_us, sample.completed_us, after))) fault = InputFault::SOURCE;
    if (fault != InputFault::NONE) {
        fail(fault, InputOperation::BATTERY, sample.status, sample.shutdown);
        return result;
    }
    report_.battery = sample;
    report_.battery_age_us = after - sample.started_us;
    battery_seen_ = true;
    increment(report_.battery_generation);
    result.accepted = true;
    updateAvailability();
    return result;
}

ButtonRead InputOwner::readButtons(bool slot_granted) {
    ButtonRead result;
    if (!report_.ready || report_.fault != InputFault::NONE) return result;
    const auto before = port_.clockUs(port_.context);
    if (!advance(before, InputOperation::BUTTONS)) return result;
    if (!slot_granted) { increment(report_.button_refused); return result; }
    increment(report_.button_attempts);
    result.attempted = true;
    result.sample = port_.readA1(port_.context);
    const auto after = port_.clockUs(port_.context);
    const auto& sample = result.sample;
    auto fault = sampleFault(sample.status, sample.shutdown, sample.valid);
    if (fault == InputFault::NONE && after - before >= HALF_RANGE) fault = InputFault::CLOCK;
    if (after - before < HALF_RANGE) advance(after, InputOperation::BUTTONS);
    const std::uint32_t expected = button_seen_ ? button_sequence_ + 1U : 1U;
    if (fault == InputFault::NONE && (sample.raw > RAW_MAX || sample.sequence != expected ||
        !interval(before, sample.started_us, sample.completed_us, after))) fault = InputFault::SOURCE;
    if (fault != InputFault::NONE) {
        fail(fault, InputOperation::BUTTONS, sample.status, sample.shutdown);
        return result;
    }
    button_sequence_ = sample.sequence;
    button_seen_ = true;
    result.accepted = true;
    return result;
}

InputReport InputOwner::observe(std::uint32_t decision_us) {
    if (report_.ready && report_.fault == InputFault::NONE)
        advance(decision_us, InputOperation::OBSERVE);
    return report_;
}

const InputReport& InputOwner::report() const { return report_; }

bool InputOwner::applyBattery(fsm::RobotInput& input) {
    observe(input.t_us);
    input.vbat_valid = report_.battery_available;
    input.vbat_v = report_.battery_available ? report_.battery.voltage_v : 0.0F;
    return report_.battery_available;
}

ui::ButtonQualification InputOwner::applyButtons(fsm::RobotInput& input, const ButtonRead& read) {
    observe(input.t_us);
    if (report_.fault == InputFault::NONE && !read.attempted && !read.accepted)
        return ui::applyButtons(input, ButtonSample{});
    if (report_.ready && report_.fault == InputFault::NONE && read.attempted && read.accepted)
        return ui::applyButtons(input, read.sample);
    ui::applyButtons(input, read.sample);
    input.buttons.presence = core::ButtonPresence::INVALID;
    input.buttons.contract_valid = false;
    return ui::ButtonQualification::INVALID;
}
} // namespace power

// Acquires four QTR RC intervals through a cooperative, checked native GPIO owner.
// Keeps uncertain edge timing and cleanup failures explicit without inferring color.
// Independent native substitutes and an inert target probe exercise this source.
#include "line_qtr.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <Arduino.h>
#include "native_pins.h"
#include <zephyr/drivers/gpio.h>
#include <stm32u5xx_ll_gpio.h>
#include <stm32u5xx_ll_exti.h>
#include <cstddef>

namespace line_qtr {
namespace {
constexpr std::uint8_t ALL_PADS = 0x0FU;
constexpr std::uint32_t EXTI_MASK = 0x101CU;
constexpr std::uint32_t TRACE_MASK = DBGMCU_CR_TRACE_IOEN |
    DBGMCU_CR_TRACE_CLKEN | DBGMCU_CR_TRACE_MODE;
constexpr std::uint32_t AFR_MASK = 0x780U;
constexpr std::uint32_t LATCH_MASK = 0x800U;
constexpr unsigned PAD_BITS[4] = {3U, 12U, 2U, 4U};
constexpr unsigned PIN_INDICES[4] = {2U, 4U, 7U, 8U};
constexpr IRQn_Type PAD_IRQS[4] = {EXTI3_IRQn, EXTI12_IRQn, EXTI2_IRQn, EXTI4_IRQn};
// Setup is serialized; a failed claimed owner keeps this latch until firmware reset.
bool qtr_claimed = false;

std::uint8_t padBit(unsigned index) { return static_cast<std::uint8_t>(1U << index); }
std::uint32_t clockUs() { return static_cast<std::uint32_t>(micros()); }
GPIO_TypeDef* registers(unsigned index) { return index == 1U ? GPIOA_NS : GPIOB_NS; }
const gpio_dt_spec& pad(unsigned index) {
    return native_pins::TABLE[config::QTR_INPUT_PINS[index]];
}

bool validSpec(const gpio_dt_spec& spec) {
    if (spec.port == nullptr || spec.port->config == nullptr || spec.port->data == nullptr ||
        spec.port->api == nullptr || spec.port->state == nullptr ||
        spec.dt_flags != 0U || spec.pin >= 16U) return false;
    const auto* cfg = static_cast<const gpio_driver_config*>(spec.port->config);
    const auto* api = static_cast<const gpio_driver_api*>(spec.port->api);
    return (cfg->port_pin_mask & (1U << spec.pin)) != 0U &&
        api->pin_configure != nullptr && api->port_get_raw != nullptr &&
        api->port_set_bits_raw != nullptr && api->port_clear_bits_raw != nullptr;
}

bool separatePin(std::uint32_t index) {
    if (index >= native_pins::COUNT) return false;
    const auto& other = native_pins::TABLE[index];
    if (!validSpec(other)) return false;
    if (other.port != DEVICE_DT_GET(DT_NODELABEL(gpioa)) &&
        other.port != DEVICE_DT_GET(DT_NODELABEL(gpiob)) &&
        other.port != DEVICE_DT_GET(DT_NODELABEL(gpioc))) return false;
    for (unsigned i = 0U; i < 4U; ++i)
        if (other.port == pad(i).port && other.pin == pad(i).pin) return false;
    return true;
}

bool metadataValid() {
    if (DT_REG_ADDR(DT_NODELABEL(gpioa)) != reinterpret_cast<std::uintptr_t>(GPIOA_NS) ||
        DT_REG_ADDR(DT_NODELABEL(gpiob)) != reinterpret_cast<std::uintptr_t>(GPIOB_NS))
        return false;
    for (unsigned i = 0U; i < 4U; ++i) {
        if (config::QTR_INPUT_PINS[i] != PIN_INDICES[i] ||
            config::QTR_INPUT_PINS[i] >= native_pins::COUNT) return false;
        const auto* expected = i == 1U ? DEVICE_DT_GET(DT_NODELABEL(gpioa)) :
                                        DEVICE_DT_GET(DT_NODELABEL(gpiob));
        if (!validSpec(pad(i)) || pad(i).port != expected || pad(i).pin != PAD_BITS[i])
            return false;
    }
    for (const auto index : config::MOTOR_PWM_PINS) if (!separatePin(index)) return false;
    for (const auto index : config::OPP_INPUT_PINS) if (!separatePin(index)) return false;
    return separatePin(config::MOTOR_ENABLE_PIN) && separatePin(config::VBAT_INPUT_PIN);
}

bool configValid() {
    const std::uint32_t limits[] = {config::QTR_QUANTIZATION_US,
        config::QTR_START_PERIOD_US, config::QTR_FRAME_MAX_US, config::QTR_CALL_MAX_US,
        config::QTR_CLEANUP_MAX_US, config::QTR_CHARGE_MAX_US, config::QTR_MAX_ADVANCES,
        config::QTR_CHARGE_US, config::QTR_TIMEOUT_US};
    for (const auto limit : limits) if (limit == 0U || limit >= 0x80000000U) return false;
    return static_cast<std::uint64_t>(config::QTR_CHARGE_US) +
        config::QTR_QUANTIZATION_US < config::QTR_CHARGE_MAX_US;
}

bool hardwareAvailable() {
    if (!device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpioa))) ||
        !device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpiob)))) return false;
    const auto clocks = RCC_AHB2ENR1_GPIOAEN | RCC_AHB2ENR1_GPIOBEN;
    const auto resets = RCC_AHB2RSTR1_GPIOARST | RCC_AHB2RSTR1_GPIOBRST;
    if ((RCC_NS->AHB2ENR1 & clocks) != clocks || (RCC_NS->AHB2RSTR1 & resets) != 0U)
        return false;
    if ((GPIOA_NS->LCKR & 0x1000U) != 0U || (GPIOB_NS->LCKR & 0x1CU) != 0U)
        return false;
    const auto exti = EXTI_NS->IMR1 | EXTI_NS->EMR1 | EXTI_NS->RTSR1 |
        EXTI_NS->FTSR1 | EXTI_NS->SWIER1 | EXTI_NS->RPR1 | EXTI_NS->FPR1;
    if ((exti & EXTI_MASK) != 0U || (DBGMCU->CR & DBGMCU_CR_TRACE_IOEN) != 0U)
        return false;
    for (const auto irq : PAD_IRQS)
        if (NVIC_GetEnableIRQ(irq) != 0U || NVIC_GetPendingIRQ(irq) != 0U ||
            NVIC_GetActive(irq) != 0U) return false;
    return true;
}

std::uint8_t route(unsigned index) {
    const auto pin = PAD_BITS[index];
    return static_cast<std::uint8_t>((EXTI_NS->EXTICR[pin / 4U] >>
                                      ((pin % 4U) * 8U)) & 0xFU);
}

std::uint32_t padState(unsigned index) {
    const auto* gpio = registers(index);
    const auto pin = PAD_BITS[index];
    const auto shift = pin * 2U;
    return ((gpio->MODER >> shift) & 3U) |
        (((gpio->OTYPER >> pin) & 1U) << 2U) |
        (((gpio->OSPEEDR >> shift) & 3U) << 3U) |
        (((gpio->PUPDR >> shift) & 3U) << 5U) |
        (((gpio->AFR[pin / 8U] >> ((pin % 8U) * 4U)) & 0xFU) << 7U) |
        (((gpio->ODR >> pin) & 1U) << 11U);
}

bool initialAllowed(unsigned index, std::uint32_t value) {
    const auto mode = value & 3U;
    return mode == 0U || mode == 3U ||
        ((index == 0U || index == 3U) && mode == 2U && (value & AFR_MASK) == 0U);
}

std::uint32_t requestedState(std::uint32_t value, bool output) {
    return (value & AFR_MASK) | (output ? (LATCH_MASK | 1U) : (value & LATCH_MASK));
}
} // namespace

bool Reader::globalOwned() const {
    if (!owned_ || !metadataValid() || !hardwareAvailable() ||
        (DBGMCU->CR & TRACE_MASK) != trace_) return false;
    for (unsigned i = 0U; i < 4U; ++i) if (route(i) != routes_[i]) return false;
    return true;
}

bool Reader::padOwned(unsigned index) const {
    const auto current = padState(index);
    if ((transition_mask_ & padBit(index)) != 0U)
        return current == old_state_[index] || current == requested_state_[index];
    return current == state_[index];
}

bool Reader::bankOwned() const {
    if (!globalOwned()) return false;
    for (unsigned i = 0U; i < 4U; ++i) if (!padOwned(i)) return false;
    return true;
}

bool Reader::captureTime(std::uint32_t now) {
    const auto increment = static_cast<std::uint32_t>(now - latest_us_);
    const bool forward = !have_time_ || increment < 0x80000000U;
    if (have_time_ && forward && timing_frame_) frame_elapsed_us_ += increment;
    latest_us_ = now;
    have_time_ = true;
    result_.checked_us = now;
    return forward;
}

Status Reader::checkTime(std::uint32_t now) {
    if (!captureTime(now)) return Status::TIME_ORDER;
    if (static_cast<std::uint32_t>(now - call_started_us_) >= config::QTR_CALL_MAX_US)
        return Status::CALL_DEADLINE;
    if (timing_frame_ && frame_elapsed_us_ >= config::QTR_FRAME_MAX_US)
        return Status::FRAME_DEADLINE;
    if (result_.phase == Phase::CHARGING && charge_timed_ &&
        static_cast<std::uint32_t>(now - result_.drive_completed_us) >=
            config::QTR_CHARGE_MAX_US) return Status::CHARGE_DEADLINE;
    return Status::OK;
}

Status Reader::configure(unsigned index, bool output) {
    if (!globalOwned() || !padOwned(index)) return Status::OWNERSHIP;
    old_state_[index] = padState(index);
    requested_state_[index] = requestedState(old_state_[index], output);
    transition_mask_ |= padBit(index);
    const auto before = clockUs();
    const auto before_status = checkTime(before);
    if (before_status != Status::OK) { transition_mask_ &= ~padBit(index); return before_status; }
    const int native = gpio_pin_configure_dt(&pad(index), output ? GPIO_OUTPUT_HIGH : GPIO_INPUT);
    const auto after = clockUs();
    const auto timed = checkTime(after);
    result_.status_by_pad[index] = native;
    if (!output && timing_frame_) {
        result_.pad[index].release_before_us = before;
        result_.pad[index].release_after_us = after;
    }
    if (native != 0) return Status::NATIVE_ERROR;
    if (timed != Status::OK) return timed;
    if (!globalOwned()) return Status::OWNERSHIP;
    if (padState(index) != requested_state_[index]) return Status::READBACK;
    state_[index] = requested_state_[index];
    transition_mask_ &= ~padBit(index);
    if (!output && timing_frame_) result_.released_mask |= padBit(index);
    return Status::OK;
}

Status Reader::setupBank() {
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto status = configure(i, false);
        if (status != Status::OK) return status;
    }
    const bool owned = bankOwned();
    const auto timed = checkTime(clockUs());
    return !owned ? Status::OWNERSHIP : timed;
}

Status Reader::begin(bool exclusive_pads) {
    if (attempted_) return Status::ALREADY_STARTED;
    attempted_ = true;
    if (!exclusive_pads || qtr_claimed) { fail(Status::OWNERSHIP); return result_.status; }
    call_started_us_ = clockUs();
    captureTime(call_started_us_);
    if (!configValid() || !metadataValid()) { fail(Status::INVALID_CONFIG); return result_.status; }
    if (!hardwareAvailable()) { fail(Status::OWNERSHIP); return result_.status; }
    for (unsigned i = 0U; i < 4U; ++i) {
        state_[i] = padState(i);
        if (!initialAllowed(i, state_[i])) { fail(Status::OWNERSHIP); return result_.status; }
        routes_[i] = route(i);
    }
    trace_ = DBGMCU->CR & TRACE_MASK;
    const auto preflight_time = checkTime(clockUs());
    if (preflight_time != Status::OK) { fail(preflight_time); return result_.status; }
    qtr_claimed = true;
    owned_ = true;
    const auto status = setupBank();
    if (status != Status::OK) { fail(status); return result_.status; }
    result_.phase = Phase::IDLE;
    result_.status = Status::OK;
    return Status::OK;
}

Status Reader::startBank() {
    if (!bankOwned()) return Status::OWNERSHIP;
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto status = configure(i, true);
        if (status != Status::OK) return status;
    }
    result_.drive_completed_us = latest_us_;
    charge_timed_ = true;
    const bool owned = bankOwned();
    const auto timed = checkTime(clockUs());
    return !owned ? Status::OWNERSHIP : timed;
}

Status Reader::start() {
    if (!attempted_) return Status::NOT_INITIALIZED;
    if (result_.phase == Phase::FAULT) return Status::FAULT_LATCHED;
    if (result_.phase == Phase::CHARGING || result_.phase == Phase::DISCHARGING)
        return Status::BUSY;
    const auto now = clockUs();
    if (have_time_ && static_cast<std::uint32_t>(now - latest_us_) >= 0x80000000U) {
        fail(Status::TIME_ORDER); return result_.status;
    }
    if (have_start_ && static_cast<std::uint32_t>(now - previous_start_us_) <
        config::QTR_START_PERIOD_US) return Status::NOT_DUE;
    result_ = {};
    result_.sequence = ++generation_;
    result_.phase = Phase::CHARGING;
    result_.status = Status::OK;
    result_.started_us = now;
    previous_start_us_ = now;
    have_start_ = true;
    timing_frame_ = false;
    captureTime(now);
    timing_frame_ = true;
    charge_timed_ = false;
    frame_elapsed_us_ = 0U;
    call_started_us_ = now;
    service_us_ = now;
    const auto status = startBank();
    if (status != Status::OK) fail(status);
    return result_.status;
}

Status Reader::readCharge(unsigned index) {
    if (!globalOwned() || !padOwned(index)) return Status::OWNERSHIP;
    const auto before = clockUs();
    const auto pre = checkTime(before);
    if (pre != Status::OK) return pre;
    const int native = gpio_pin_get_raw(pad(index).port, pad(index).pin);
    const auto post = checkTime(clockUs());
    result_.status_by_pad[index] = native;
    if (native != 0 && native != 1) return Status::NATIVE_ERROR;
    if (post != Status::OK) return post;
    if (!globalOwned() || !padOwned(index)) return Status::OWNERSHIP;
    return native == 1 ? Status::OK : Status::CHARGE_LOW;
}

Status Reader::releaseBank() {
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto status = readCharge(i);
        if (status != Status::OK) return status;
    }
    for (unsigned i = 0U; i < 4U; ++i) {
        const auto status = configure(i, false);
        if (status != Status::OK) return status;
    }
    result_.phase = Phase::DISCHARGING;
    return Status::OK;
}

Status Reader::readDischarge(unsigned index) {
    if (!globalOwned() || !padOwned(index)) return Status::OWNERSHIP;
    const auto before = clockUs();
    const auto pre = checkTime(before);
    if (pre != Status::OK) return pre;
    const int native = gpio_pin_get_raw(pad(index).port, pad(index).pin);
    const auto after = clockUs();
    const auto post = checkTime(after);
    result_.status_by_pad[index] = native;
    if (native != 0 && native != 1) return Status::NATIVE_ERROR;
    if (post != Status::OK) return post;
    if (!globalOwned() || !padOwned(index)) return Status::OWNERSHIP;
    auto& sample = result_.pad[index];
    if (native == 0) {
        sample.first_low_after_us = after;
        const auto duration = static_cast<std::uint32_t>(after - sample.release_before_us);
        sample.upper_us = static_cast<std::uint32_t>(static_cast<std::uint64_t>(duration) +
                                                    config::QTR_QUANTIZATION_US);
        result_.low_mask |= padBit(index);
    } else {
        sample.last_high_before_us = before;
        result_.high_mask |= padBit(index);
        const auto duration = static_cast<std::uint32_t>(before - sample.release_after_us);
        const auto widened = static_cast<std::uint64_t>(duration);
        sample.lower_us = widened > config::QTR_QUANTIZATION_US ?
            static_cast<std::uint32_t>(widened - config::QTR_QUANTIZATION_US) : 0U;
        if (sample.lower_us >= config::QTR_TIMEOUT_US) result_.timeout_mask |= padBit(index);
    }
    return Status::OK;
}

Status Reader::sampleBank() {
    for (unsigned i = 0U; i < 4U; ++i) {
        if (((result_.low_mask | result_.timeout_mask) & padBit(i)) != 0U) continue;
        const auto status = readDischarge(i);
        if (status != Status::OK) return status;
    }
    const bool owned = bankOwned();
    const auto timed = checkTime(clockUs());
    return !owned ? Status::OWNERSHIP : timed;
}

Status Reader::serviceFrame() {
    if (!bankOwned()) return Status::OWNERSHIP;
    if (result_.phase == Phase::CHARGING) {
        if (static_cast<std::uint32_t>(latest_us_ - result_.drive_completed_us) <
            config::QTR_CHARGE_US + config::QTR_QUANTIZATION_US)
            return checkTime(clockUs());
        const auto released = releaseBank();
        if (released != Status::OK) return released;
    }
    return sampleBank();
}

Snapshot Reader::advance() {
    if (result_.phase != Phase::CHARGING && result_.phase != Phase::DISCHARGING)
        return result_;
    const auto now = clockUs();
    call_started_us_ = now;
    const auto gap = static_cast<std::uint32_t>(now - service_us_);
    if (gap < 0x80000000U && gap > result_.max_service_gap_us) result_.max_service_gap_us = gap;
    service_us_ = now;
    ++result_.advances;
    auto status = checkTime(now);
    if (status == Status::OK) status = serviceFrame();
    if (status != Status::OK) { fail(status); return result_; }
    if ((result_.low_mask | result_.timeout_mask) == ALL_PADS) finish();
    else if (result_.advances >= config::QTR_MAX_ADVANCES) fail(Status::ADVANCE_LIMIT);
    return result_;
}

void Reader::cleanupPad(unsigned index) {
    auto& cleanup = result_.cleanup;
    if (!globalOwned() || !padOwned(index)) {
        cleanup.skipped_mask |= padBit(index);
        cleanup.nonneutral_mask |= padBit(index);
        return;
    }
    const auto expected = requestedState(padState(index), false);
    cleanup.attempted_mask |= padBit(index);
    const auto before = clockUs();
    if (!captureTime(before)) cleanup_time_valid_ = false;
    cleanup.status[index] = gpio_pin_configure_dt(&pad(index), GPIO_INPUT);
    const auto after = clockUs();
    if (!captureTime(after)) cleanup_time_valid_ = false;
    if (cleanup.status[index] != 0) cleanup.failed_mask |= padBit(index);
    if (!globalOwned() || padState(index) != expected) cleanup.nonneutral_mask |= padBit(index);
    else { state_[index] = expected; transition_mask_ &= ~padBit(index); }
    if (static_cast<std::uint32_t>(after - cleanup.started_us) >= config::QTR_CLEANUP_MAX_US)
        cleanup.deadline_exceeded = true;
}

bool Reader::cleanup() {
    auto& cleanup = result_.cleanup;
    cleanup = {};
    cleanup_time_valid_ = true;
    cleanup.started_us = clockUs();
    if (!captureTime(cleanup.started_us)) cleanup_time_valid_ = false;
    for (unsigned i = 0U; i < 4U; ++i) cleanupPad(i);
    const bool global = globalOwned();
    for (unsigned i = 0U; i < 4U; ++i)
        if (!global || padState(i) != requestedState(state_[i], false))
            cleanup.nonneutral_mask |= padBit(i);
    cleanup.completed_us = clockUs();
    if (!captureTime(cleanup.completed_us)) cleanup_time_valid_ = false;
    if (static_cast<std::uint32_t>(cleanup.completed_us - cleanup.started_us) >=
        config::QTR_CLEANUP_MAX_US) cleanup.deadline_exceeded = true;
    return cleanup_time_valid_ && !cleanup.deadline_exceeded &&
        cleanup.attempted_mask == ALL_PADS && cleanup.failed_mask == 0U &&
        cleanup.skipped_mask == 0U && cleanup.nonneutral_mask == 0U;
}

void Reader::fail(Status status) {
    result_.valid = false;
    result_.status = status;
    result_.phase = Phase::FAULT;
    if (owned_) cleanup();
    result_.completed_us = latest_us_;
    timing_frame_ = false;
}

void Reader::finish() {
    const bool clean = cleanup();
    result_.completed_us = latest_us_;
    result_.valid = clean && frame_elapsed_us_ < config::QTR_FRAME_MAX_US &&
        static_cast<std::uint32_t>(latest_us_ - call_started_us_) < config::QTR_CALL_MAX_US;
    result_.phase = result_.valid ? Phase::COMPLETE : Phase::FAULT;
    result_.status = !clean ? Status::CLEANUP :
        frame_elapsed_us_ >= config::QTR_FRAME_MAX_US ? Status::FRAME_DEADLINE :
        !result_.valid ? Status::CALL_DEADLINE : Status::OK;
    timing_frame_ = false;
}

Snapshot Reader::cancel() {
    if (result_.phase == Phase::CHARGING || result_.phase == Phase::DISCHARGING)
        fail(Status::CANCELLED);
    return result_;
}
} // namespace line_qtr
#endif

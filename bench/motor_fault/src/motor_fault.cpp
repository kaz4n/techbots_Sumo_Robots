// Records bounded callback evidence while the real Gate applies only zero outputs.
// Keeps cleanup from replacing the first failure and leaves native limits intact.
// Independent D162 tests exercise forwarding, failure retention and terminal safety.
#include "motor_fault.h"
#include <limits>

namespace motor_fault {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
std::uint32_t add(std::uint32_t value, std::uint32_t amount = 1U) {
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    return amount > maximum - value ? maximum : value + amount;
}
} // namespace

Trace::Trace(const motors::Port& native) : native_(native) {}

motors::Port Trace::port() {
    auto result = native_;
    result.context = this;
    result.configureEnableLow = native_.configureEnableLow ? configureEnable : nullptr;
    result.configurePwm = native_.configurePwm ? configurePwm : nullptr;
    result.writeEnable = native_.writeEnable ? enable : nullptr;
    result.writePwm = native_.writePwm ? pwm : nullptr;
    result.settle = native_.settle ? settle : nullptr;
    result.clockUs = native_.clockUs ? clock : nullptr;
    return result;
}

void Trace::context(Stage stage, std::uint32_t application) {
    stage_ = stage;
    application_ = application;
}

const TraceReport& Trace::report() const { return report_; }

std::uint32_t Trace::clock(void* context) {
    auto& self = *static_cast<Trace*>(context);
    if (!self.native_.clockUs) return 0U;
    self.report_.clock_reads = add(self.report_.clock_reads);
    return self.native_.clockUs(self.native_.context);
}

void Trace::start(Operation operation, motors::Channel channel, bool high,
                  std::uint32_t period, std::uint32_t pulse) {
    report_.current = Call{};
    auto& call = report_.current;
    call.stage = stage_;
    call.application = application_;
    call.operation = operation;
    call.channel = channel;
    call.requested_high = high;
    call.period_cycles = period;
    call.pulse_cycles = pulse;
    report_.has_current = true;
    if (native_.clockUs) call.started_us = clock(this);
}

bool Trace::finish(bool result) {
    auto& call = report_.current;
    call.returned = result;
    const bool first = !result && !report_.has_failure;
    if (first) {
        report_.has_failure = true;
        report_.first_failure = call; // Preserve false before any trailing clock work.
    }
    if (native_.clockUs) call.completed_us = clock(this);
    call.timing_valid = native_.clockUs && call.completed_us - call.started_us < HALF_RANGE;
    call.completed = true;
    if (!call.timing_valid) report_.timing_fault = true;
    if (first) report_.first_failure = call;
    if (report_.count < TRACE_CAPACITY) report_.calls[report_.count++] = call;
    else {
        report_.overflow = true;
        report_.rejected = add(report_.rejected);
    }
    return result;
}

bool Trace::configureEnable(void* context) {
    auto& self = *static_cast<Trace*>(context);
    self.start(Operation::CONFIGURE_ENABLE);
    self.report_.current.invoked = true;
    return self.finish(self.native_.configureEnableLow(self.native_.context));
}

bool Trace::configurePwm(void* context, motors::Channel channel) {
    auto& self = *static_cast<Trace*>(context);
    self.start(Operation::CONFIGURE_PWM, channel);
    self.report_.current.invoked = true;
    return self.finish(self.native_.configurePwm(self.native_.context, channel));
}

bool Trace::enable(void* context, bool high) {
    auto& self = *static_cast<Trace*>(context);
    self.start(Operation::ENABLE, motors::Channel::LEFT_FORWARD, high);
    if (high) return self.finish(false);
    self.report_.current.invoked = true;
    return self.finish(self.native_.writeEnable(self.native_.context, high));
}

bool Trace::pwm(void* context, motors::Channel channel, std::uint32_t period,
                std::uint32_t pulse) {
    auto& self = *static_cast<Trace*>(context);
    self.start(Operation::PWM, channel, false, period, pulse);
    if (pulse != 0U) return self.finish(false);
    self.report_.current.invoked = true;
    return self.finish(self.native_.writePwm(self.native_.context, channel, period, pulse));
}

bool Trace::settle(void* context) {
    auto& self = *static_cast<Trace*>(context);
    self.start(Operation::SETTLE);
    self.report_.current.invoked = true;
    return self.finish(self.native_.settle(self.native_.context));
}

Runner::Runner(const motors::Port& native)
    : trace_(native), port_(trace_.port()), gate_(port_) {}

bool Runner::traceValid() const {
    return !trace_.report().overflow && !trace_.report().timing_fault;
}

bool Runner::begin(const Grants& grants) {
    if (attempted_) return false;
    attempted_ = true;
    if (!grants.exclusive_motor_outputs) {
        report_.phase = Phase::DISABLED;
        return true;
    }
    trace_.context(Stage::SETUP);
    report_.begin_called = true;
    report_.begin_ok = gate_.begin();
    report_.begin_fault = gate_.fault();
    if (!report_.begin_ok) { stop(Failure::SETUP); return false; }
    if (!traceValid()) { stop(Failure::TRACE); return false; }
    last_us_ = port_.clockUs(port_.context);
    report_.next_release_us = last_us_;
    report_.phase = Phase::RUNNING;
    return true;
}

void Runner::stop(Failure reason) {
    if (report_.halt_called) return;
    report_.failure = reason;
    trace_.context(Stage::HALT);
    report_.halt_called = true;
    report_.halt = gate_.halt();
    const auto& halt = report_.halt;
    const bool good = halt.fresh && halt.attempted && halt.inhibition_confirmed &&
        halt.timing_valid && halt.fault == motors::Fault::STOPPED;
    if (report_.failure == Failure::NONE && !traceValid()) report_.failure = Failure::TRACE;
    if (report_.failure == Failure::NONE && !good) report_.failure = Failure::HALT;
    report_.phase = report_.failure == Failure::NONE ? Phase::COMPLETE : Phase::FAULT;
}

void Runner::poll(std::uint32_t now_us) {
    if (!active()) return;
    const auto elapsed = now_us - last_us_;
    if (elapsed >= HALF_RANGE) { stop(Failure::CLOCK); return; }
    equal_polls_ = elapsed == 0U ? add(equal_polls_) : 0U;
    if (equal_polls_ >= config::APP_CLOCK_STALL_MAX_POLLS) { stop(Failure::CLOCK); return; }
    last_us_ = now_us;
    const auto released = now_us - report_.next_release_us;
    if (released >= HALF_RANGE) return;
    const auto missed = released / config::TICK_US;
    report_.missed_releases = add(report_.missed_releases, missed);
    report_.next_release_us += (missed + 1U) * config::TICK_US;
    fsm::RobotResult command;
    command.fresh = true;
    command.token = report_.applications + 1U;
    command.outputs.ui_state = core::State::BOOT;
    command.lifecycle.gate.phase = countdown::Phase::IDLE;
    trace_.context(Stage::APPLY, report_.applications + 1U);
    auto& applied = report_.applied[report_.applications++];
    applied = gate_.apply(now_us, command);
    const auto& feedback = applied.feedback;
    if (!applied.consumed || applied.fault != motors::Fault::NONE ||
        !feedback.applied_valid || feedback.token != command.token || feedback.motors_enabled ||
        feedback.duty_l != 0.0F || feedback.duty_r != 0.0F) {
        stop(Failure::APPLICATION);
        return;
    }
    if (!traceValid()) { stop(Failure::TRACE); return; }
    if (report_.applications == APPLY_SAMPLES) stop(Failure::NONE);
}

bool Runner::active() const { return report_.phase == Phase::RUNNING; }
const Report& Runner::report() const { return report_; }
const TraceReport& Runner::trace() const { return trace_.report(); }
} // namespace motor_fault

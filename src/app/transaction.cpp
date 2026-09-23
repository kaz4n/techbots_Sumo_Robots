// Owns each actual Robot, MotorGate and recorder epoch from acquisition to close.
// Rejects invalid sequencing and clocks without fabricating application evidence.
// Independent D095 pipeline tests verify timing, interruption and inert lifetime.
#include "transaction.h"

namespace app {
Transaction::Transaction(const motors::Port& port) : port_(port), gate_(port) {}

bool Transaction::initialize() {
    if (report_.phase == Phase::FAULT) return false;
    if (attempted_) return true;
    attempted_ = true;
    if (!gate_.begin()) {
        // begin owns its setup cleanup; a second inhibit is not a new setup step.
        report_.phase = Phase::FAULT;
        report_.fault = Fault::SETUP;
        return false;
    }
    report_.phase = Phase::IDLE;
    return true;
}

bool Transaction::observe(std::uint32_t& now_us) {
    if (port_.clockUs == nullptr) return false;
    now_us = port_.clockUs(port_.context);
    if (time_seen_ && static_cast<std::uint32_t>(now_us - last_us_) >= 0x80000000U)
        return false;
    last_us_ = now_us;
    time_seen_ = true;
    return true;
}

void Transaction::fail(Fault fault) {
    if (report_.phase == Phase::FAULT) return;
    report_.fault = fault;
    report_.phase = Phase::FAULT;
    report_.halt = gate_.halt();
    // Halt changes output outside the ordinary token receipt. Preserve its facts
    // while withdrawing the acknowledgement that would authorize later use.
    previous_.applied_valid = false;
    previous_.duration_valid = false;
    report_.applied.feedback.applied_valid = false;
    report_.applied.feedback.duration_valid = false;
    recorder_.onRobotReset();
}

bool Transaction::open() {
    if (report_.phase == Phase::FAULT) return false;
    if (report_.phase != Phase::IDLE) { fail(Fault::ORDER); return false; }
    std::uint32_t now_us = 0U;
    if (!observe(now_us)) { fail(Fault::CLOCK); return false; }
    report_ = TransactionReport{};
    report_.started_us = now_us;
    report_.phase = Phase::ACQUIRING;
    return true;
}

bool Transaction::decide(fsm::RobotInput input) {
    if (report_.phase == Phase::FAULT) return false;
    if (report_.phase != Phase::ACQUIRING) { fail(Fault::ORDER); return false; }
    std::uint32_t now_us = 0U;
    if (!observe(now_us) || now_us - report_.started_us >= 0x80000000U ||
        (decision_seen_ && now_us == last_decision_us_)) {
        fail(Fault::CLOCK);
        return false;
    }
    report_.decision_us = now_us;
    input.t_us = now_us;
    input.timing = {true, true, report_.started_us};
    input.previous = previous_;
    report_.robot = robot_.step(input);
    if (!report_.robot.fresh || report_.robot.token == 0U ||
        report_.robot.token <= previous_.token) {
        fail(Fault::IDENTITY);
        return false;
    }
    decision_seen_ = true;
    last_decision_us_ = now_us;
    report_.applied = gate_.apply(now_us, report_.robot);
    if (!report_.applied.consumed || report_.applied.feedback.token != report_.robot.token) {
        fail(Fault::IDENTITY);
        return false;
    }
    report_.recorded = recorder_.consume(report_.robot);
    report_.decision_made = true;
    report_.phase = Phase::DECIDED;
    return true;
}

bool Transaction::finish() {
    if (report_.phase == Phase::FAULT) return false;
    if (report_.phase != Phase::DECIDED) { fail(Fault::ORDER); return false; }
    std::uint32_t now_us = 0U;
    if (!observe(now_us) || now_us - report_.started_us >= 0x80000000U) {
        fail(Fault::CLOCK);
        return false;
    }
    const auto decision_offset = report_.decision_us - report_.started_us;
    const auto applied_offset = report_.applied.feedback.applied_us - report_.started_us;
    const auto completed_offset = now_us - report_.started_us;
    if (applied_offset < decision_offset || applied_offset > completed_offset) {
        fail(Fault::RECEIPT);
        return false;
    }
    report_.completed_us = now_us;
    report_.execution_us = completed_offset;
    report_.timing_valid = true;
    report_.finished = true;
    previous_ = report_.applied.feedback;
    previous_.duration_valid = true;
    previous_.completed_us = now_us;
    previous_.execution_us = completed_offset;
    report_.phase = Phase::IDLE;
    return true;
}

void Transaction::abort() { fail(Fault::ABORTED); }
} // namespace app

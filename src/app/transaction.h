// Owns actual Robot, MotorGate and recorder transactions with complete timing.
// Prevents reordered work, forged receipts and unsafe clock-fault recovery.
// Independent actual-pipeline tests and an inert target probe verify D095.
#pragma once
#include "../hal/motors.h"
#include "../hal/recorder.h"

namespace app {
enum class Phase : std::uint8_t { NOT_INITIALIZED, IDLE, ACQUIRING, DECIDED, FAULT };
enum class Fault : std::uint8_t { NONE, SETUP, ORDER, CLOCK, IDENTITY, RECEIPT, ABORTED };
// D096 pure projection seam: called once after actual D, never acquires hardware.
struct DecisionSource {
    void* context = nullptr;
    fsm::RobotInput (*project)(void*, std::uint32_t decision_us) = nullptr;
    // Optional pure check of the source owner's additional clock chronology.
    bool (*clockAccepted)(void*) = nullptr;
};
struct TransactionReport {
    Phase phase = Phase::NOT_INITIALIZED;
    Fault fault = Fault::NONE;
    bool decision_made = false;
    bool finished = false;
    bool timing_valid = false;
    std::uint32_t started_us = 0U;
    std::uint32_t decision_us = 0U;
    std::uint32_t completed_us = 0U;
    std::uint32_t execution_us = 0U;
    fsm::RobotResult robot;
    motors::Result applied;
    motors::HaltResult halt;
    recorder::ConsumeStatus recorded = recorder::ConsumeStatus::OUTSIDE_ATTEMPT;
};
class Transaction {
public:
    // Port owner outlives this fixed object. Its clock is the sensor micros domain.
    explicit Transaction(const motors::Port& port);
    Transaction(const Transaction&) = delete;
    Transaction& operator=(const Transaction&) = delete;
    // Gate setup is the first hardware operation. One attempt; repeats passive.
    bool initialize();
    // Call before any acquisition/service belonging to this actual epoch.
    bool open();
    // Owns real decision time and prior feedback, overriding those caller fields.
    // True means one actual decision/application/record step, even if HAL failed.
    bool decide(fsm::RobotInput input);
    bool decideFrom(const DecisionSource& source);
    // Call after all admitted post-decision work, including output/cleanup.
    bool finish();
    // Additional actual outer observation must precede C and follow D/application.
    bool finishAfter(std::uint32_t last_observed_us);
    // Local end-of-stream/invariant abort; terminal, no fake Robot tick or reset.
    void abort();
    // D103: once only, after two real completed inhibited STOP epochs and open.
    // Keeps Gate STOPPED/native owners/retained evidence; resets Robot in S..C.
    // Wrong phase/history is passive false; no caller-supplied proof is accepted.
    bool resetStoppedRobotForService();
    const TransactionReport& report() const { return report_; }
    const recorder::AttemptRecorder& recording() const { return recorder_; }
    const fsm::PreviousTick& previous() const { return previous_; }
private:
    // Implementation owner may extend only private helpers/state.
    void fail(Fault fault);
    bool observe(std::uint32_t& now_us);
    bool beginDecision(std::uint32_t& now_us);
    bool applyDecision(fsm::RobotInput input, std::uint32_t now_us);
    bool complete(bool has_observation, std::uint32_t last_observed_us);
    motors::Port port_;
    motors::MotorGate gate_;
    fsm::Robot robot_;
    recorder::AttemptRecorder recorder_;
    TransactionReport report_;
    fsm::PreviousTick previous_;
    bool attempted_ = false;
    bool time_seen_ = false;
    bool decision_seen_ = false;
    std::uint32_t last_us_ = 0U;
    std::uint32_t last_decision_us_ = 0U;
};
} // namespace app

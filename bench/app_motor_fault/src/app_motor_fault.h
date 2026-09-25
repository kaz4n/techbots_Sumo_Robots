// Observes the real inhibited application through the existing MotorGate trace.
// Preserves the first failing callback and the application state before abort.
// Independent D186 public-contract tests verify bounded, passive terminal paths.
#pragma once
#include "motor_fault.h"
#include "app/runtime.h"

namespace app_motor_fault {
inline constexpr std::uint32_t EPOCH_SAMPLES = motor_fault::APPLY_SAMPLES;
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, FINALIZING, FROZEN };
enum class Reason : std::uint8_t {
    NONE, SETUP_FAILED, CALLBACK_FAILURE, TRACE_INVALID, APPLICATION_INVALID,
    RUNTIME_TERMINAL, EPOCH_LIMIT
};
struct Snapshot {
    app::RuntimeReport runtime;
    app::TransactionReport transaction;
    fsm::PreviousTick previous;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Reason reason = Reason::NONE;
    bool begin_called = false, begin_finished = false, begin_ok = false;
    bool before_abort_valid = false, abort_called = false, abort_returned = false;
    bool last_step_returned = false;
    Snapshot before_abort;
};
class Runner {
public:
    Runner(const motors::Port& motor, const power::InputPort& adc,
           const app::SourcePort& sources, const app::DumpPort& dump = {});
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    // One admission; all real application source/service grants remain absent.
    bool begin(const motor_fault::Grants& grant);
    // One existing Runtime::step; no synthetic request, epoch or external clock.
    void poll();
    bool active() const { return report_.phase == Phase::RUNNING; }
    const Report& report() const { return report_; }
    const motor_fault::TraceReport& trace() const { return trace_.report(); }
    const app::Runtime& runtime() const { return runtime_; }
private:
    Reason stopReason() const;
    bool applicationValid() const;
    void freeze(Reason reason);
    motor_fault::Trace trace_;
    app::Runtime runtime_;
    Report report_;
    bool attempted_ = false;
};
} // namespace app_motor_fault

// Observes bounded real application epochs with the existing inhibited trace.
// Retains prefix loss and the first failure without changing native callbacks.
// Independent D192 contract tests verify limits, priorities and terminal passivity.
#pragma once
#include "config.h"
#include "motor_fault.h"
#include "app/runtime.h"

static_assert(config::APP_MOTOR_OBSERVE_EPOCHS > 0U &&
              config::APP_MOTOR_OBSERVE_EPOCHS <= 10000000U &&
              config::APP_MOTOR_OBSERVE_MAX_POLLS > 0U &&
              config::APP_MOTOR_OBSERVE_MAX_POLLS <= 10000000U &&
              config::APP_MOTOR_OBSERVE_MAX_POLLS >= config::APP_MOTOR_OBSERVE_EPOCHS,
              "Application observation requires positive bounded epoch and poll counts");

namespace app_motor_observe {
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, FINALIZING, FROZEN };
enum class Reason : std::uint8_t {
    NONE, SETUP_FAILED, CALLBACK_FAILURE, TRACE_INVALID, APPLICATION_INVALID,
    RUNTIME_TERMINAL, EPOCH_LIMIT, POLL_LIMIT
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
    std::uint32_t polls = 0U;
    Snapshot before_abort;
};
class Runner {
public:
    Runner(const motors::Port& motor, const power::InputPort& adc,
           const app::SourcePort& sources, const app::DumpPort& dump = {});
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    // One admission; all application peripheral and service grants stay absent.
    bool begin(const motor_fault::Grants& grant);
    // One existing Runtime::step; the Runtime alone owns clocks and epochs.
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
} // namespace app_motor_observe

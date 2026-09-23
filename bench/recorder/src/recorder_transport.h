// Composes one synthetic 200-second recording with real inhibited IDLE transfer.
// Keeps native UART grants explicit and owns no physical motor or sensor backend.
// Independent public-contract tests exercise lifecycle, timing and receiver rows.
#pragma once
#include "app/transaction.h"
#include "app/dump_port.h"
#include <cstdint>

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "D116 requires an inert bench build");

namespace recorder_transport {
struct ClockPort {
    void* context = nullptr;
    std::uint32_t (*now_us)(void*) = nullptr;
};
enum class Phase : std::uint8_t {
    NOT_STARTED, DISABLED, STARTING, RECORDING, STOPPING, RESET_GESTURE,
    SERVICE_MENU, DUMPING, SENT_UNCONFIRMED, FAILED
};
enum class Failure : std::uint8_t {
    NONE, ORDER, PORT, GRANT, CONFIG, CLOCK, DEADLINE, MISSED_RELEASE, TRANSACTION,
    SCENARIO, RECORDING, RESET, DUMP_SETUP, DUMP
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Failure failure = Failure::NONE;
    // Actual begin return only. Live native status belongs to the external owner.
    recorder::dump::NativeStatus dump_setup = recorder::dump::NativeStatus::NOT_INITIALIZED;
    bool setup_completed = false; // Admitted final setup clock; timestamp may be0.
    bool go_seen = false;
    bool service_only = false;
    bool reset_pending = false;
    bool reset_done = false;
    bool counters_saturated = false;
    std::uint32_t setup_completed_us = 0U;
    std::uint32_t last_poll_us = 0U; // Last actual entry sample, even if rejected.
    std::uint32_t next_release_us = 0U;
    std::uint32_t epochs = 0U; // Successfully closed actual transactions only.
    std::uint32_t missed_releases = 0U;
    std::uint32_t maximum_lateness_us = 0U;
    // Completed Transaction S..C only; final publication and outer poll excluded.
    std::uint32_t maximum_execution_us = 0U;
    std::uint32_t release_us = 0U;
    std::uint32_t stop_us = 0U;
    std::uint32_t reset_epoch_started_us = 0U; // Actual S, not a reset-duration claim.
    std::uint32_t request_us = 0U;
    std::uint64_t release_token = 0U;
    std::uint64_t stop_token = 0U;
    std::uint64_t reset_from_token = 0U;
    std::uint64_t request_token = 0U;
    std::uint32_t configure_enable_calls = 0U;
    std::uint32_t configure_pwm_calls = 0U;
    std::uint32_t write_enable_calls = 0U;
    std::uint32_t write_pwm_calls = 0U;
    std::uint32_t settle_calls = 0U;
    std::uint32_t enabled_en = 0U; // Attempted HIGHs, including rejected calls.
    std::uint32_t nonzero_pwm = 0U; // Attempted nonzero pulses, including rejection.
    std::uint32_t invalid_motor_calls = 0U;
};
class Runner {
public:
    // Supplied port owners outlive this fixed object; construction is passive.
    explicit Runner(const ClockPort& clock, const app::DumpPort& dump = {});
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    // One attempt. True only for enabled setup success; disabled/repeated are false.
    bool begin(bool enabled = false, const recorder::dump::SetupGrant& grants = {});
    // At most one due actual epoch, with no catch-up or between-epoch transport.
    void poll();
    const Report& report() const;
    // References retain actual evidence, including a failed/unfinished transaction.
    const app::Transaction& transaction() const;
    const recorder::AttemptRecorder& source() const;
    const recorder::dump::Report& dump() const;
private:
    // Implementation-owned fixed members; public interface and semantics frozen.
};
} // namespace recorder_transport

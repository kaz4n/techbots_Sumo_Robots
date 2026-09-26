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
    enum class Stage : std::uint8_t {
        START_NEUTRAL, START_PRESS, START_RELEASE, RECORD, STOP_TAIL,
        RESET_NEUTRAL, RESET_PRESS, RESET_RELEASE, SERVICE_NEUTRAL,
        MENU_LONG, MENU_RELEASE, SELECT_PRESS, SELECT_RELEASE,
        REQUEST_PRESS, REQUEST_RELEASE, WAIT_DUMP
    };
    static constexpr std::uint32_t HALF_RANGE = 0x80000000U;
    static constexpr std::uint64_t DEBOUNCE_US = std::uint64_t{config::BTN_DEBOUNCE_MS} * 1000U;
    static constexpr std::uint64_t LONG_US = std::uint64_t{config::BTN_LONG_MS} * 1000U;
    static constexpr std::uint64_t G_US = DEBOUNCE_US + 4U * std::uint64_t{config::TICK_US};
    static constexpr std::uint64_t RECORD_US = std::uint64_t{config::LOG_FRAME_WINDOW_MS} * 1000U;
    static constexpr std::uint64_t TOTAL_US = RECORD_US +
        std::uint64_t{config::DUMP_TOTAL_MS} * 1000U + 2U * (LONG_US + G_US) +
        24U * G_US + config::BUTTON_SAMPLE_MAX_AGE_US + 4U * std::uint64_t{config::TICK_US};
    static motors::Port motorPort(Runner*);
    static bool configureEnable(void*);
    static bool configurePwm(void*, motors::Channel);
    static bool writeEnable(void*, bool);
    static bool writePwm(void*, motors::Channel, std::uint32_t, std::uint32_t);
    static bool settle(void*);
    static std::uint32_t ownerClock(void*);
    static fsm::RobotInput project(void*, std::uint32_t);
    static bool projectionClockAccepted(void*);
    bool validConfig() const;
    bool terminal() const;
    bool sample(std::uint32_t&);
    bool ownerResult(bool);
    void add(std::uint32_t&, std::uint64_t = 1U);
    void fail(Failure);
    void epoch();
    void closeEpoch();
    bool receiptValid() const;
    bool inhibitedIdle(std::uint32_t) const;
    bool transfer(std::uint32_t&);
    void enterStage(Stage, std::uint32_t);
    void advanceStage(std::uint32_t);
    std::uint64_t stageDuration() const;
    core::ButtonLevel stageButton() const;
    fsm::RobotInput input(std::uint32_t);
    bool observeDecision();
    bool observeRecording();
    bool observeService();
    void observeResetGesture();
    bool applyReset();
    bool sealed() const;
    ClockPort clock_;
    app::DumpPort dump_port_;
    Report report_;
    app::Transaction transaction_;
    recorder::dump::Transfer transfer_;
    Stage stage_ = Stage::START_NEUTRAL;
    core::ButtonLevel button_ = core::ButtonLevel::NONE;
    std::uint64_t elapsed_us_ = 0U;
    std::uint64_t pending_token_ = 0U;
    std::uint64_t session_ = 0U;
    std::uint32_t last_clock_us_ = 0U, previous_poll_us_ = 0U, equal_polls_ = 0U;
    std::uint32_t stage_started_us_ = 0U, sequence_ = 0U, reset_hold_us_ = 0U;
    std::uint32_t pending_source_us_ = 0U, pending_sequence_ = 0U;
    std::uint8_t short_pairs_ = 0U;
    bool attempted_ = false, initialized_ = false, clock_seen_ = false, clock_fault_ = false;
    bool stage_seen_ = false, scenario_fault_ = false, stop_projected_ = false;
    bool reset_neutral_ = false, reset_mode_ = false, reset_held_ = false;
    bool service_first_ = false, service_idle_seen_ = false, menu_is_log_ = false;
};
} // namespace recorder_transport

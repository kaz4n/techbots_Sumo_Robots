// Schedules the actual sensor, decision, motor and recording pipeline.
// Gives every source, cleanup and output operation one truthful tick lifetime.
// Independent scripted source tests and native target compilation verify D096.
#pragma once
#include "transaction.h"
#include "../hal/power_inputs.h"
#include "../hal/opp_sensors.h"
#include "../hal/imu_heading.h"
#include "../hal/imu_adapter.h"
#include "../hal/line_qtr_adapter.h"
#include "../hal/qtr_cal.h"
#include "../hal/ui_matrix_unoq.h"

namespace app {
// Fixed direct bindings to existing HAL owners, not an additional bus owner.
struct SourcePort {
    void* context = nullptr;
    opp_sensors::InitResult (*beginOpponents)(void*) = nullptr;
    opp_sensors::Snapshot (*readOpponents)(void*) = nullptr;
    line_qtr::Status (*beginLines)(void*, bool exclusive) = nullptr;
    line_qtr::Status (*startLines)(void*) = nullptr;
    line_qtr::Snapshot (*advanceLines)(void*) = nullptr;
    line_qtr::Snapshot (*cancelLines)(void*) = nullptr;
    line_qtr::Snapshot (*lines)(void*) = nullptr;
    imu::SetupReport (*startImu)(void*, std::uint32_t, bool power_confirmed) = nullptr;
    imu::SetupReport (*advanceImuSetup)(void*, std::uint32_t) = nullptr;
    imu::SampleProgress (*beginImu)(void*, std::uint32_t) = nullptr;
    imu::SampleProgress (*advanceImu)(void*, std::uint32_t) = nullptr;
    imu::SampleProgress (*cancelImu)(void*, std::uint32_t) = nullptr;
    imu::Sample (*imuSetupFailure)(void*, std::uint32_t) = nullptr;
    ui::MatrixStatus (*beginMatrix)(void*, ui::MatrixGrant) = nullptr;
    ui::MatrixStatus (*submitMatrix)(void*, std::uint32_t, const ui::Frame&) = nullptr;
};
struct SetupGrants {
    bool opponents = false;
    bool adc_pair = false;
    bool qtr_exclusive_pads = false;
    bool imu_enabled = false;
    bool imu_power_confirmed = false;
    imu::Mounting mounting;
    bool default_line_thresholds_confirmed = false;
    bool matrix_enabled = false;
    ui::MatrixGrant matrix;
};
enum class RuntimePhase : std::uint8_t { NOT_STARTED, RUNNING, STOPPED, FAULT };
enum class RuntimeFault : std::uint8_t { NONE, PORT, CLOCK, SERVICE_LIMIT, TRANSACTION, PROJECTION };
struct RuntimeReport {
    RuntimePhase phase = RuntimePhase::NOT_STARTED;
    RuntimeFault fault = RuntimeFault::NONE;
    bool fresh = false; // One step call finished a real transaction.
    bool initialization_complete = false;
    bool raw_lines = true;
    bool imu_expired = false;
    bool calibration_interrupted = false;
    std::uint32_t next_release_us = 0U;
    std::uint32_t missed_releases = 0U;
    std::uint32_t epochs = 0U;
    std::uint32_t service_passes = 0U;
    std::uint32_t maximum_execution_us = 0U;
    opp_sensors::InitResult opponents_setup;
    line_qtr::Status line_setup = line_qtr::Status::NOT_INITIALIZED;
    imu::SetupReport imu_setup;
    ui::MatrixStatus matrix_status = ui::MatrixStatus::NOT_INITIALIZED;
    qtr_cal::Report calibration;
    line_qtr::Snapshot line_shutdown;
    imu::SampleProgress imu_shutdown;
};
class Runtime {
public:
    Runtime(const motors::Port& motors, const power::InputPort& adc,
            const SourcePort& sources);
    Runtime(const Runtime&) = delete;
    Runtime& operator=(const Runtime&) = delete;
    // One setup attempt. Gate is first native operation; absent grants stay absent.
    bool begin(const SetupGrants& grants);
    // One due real epoch at most. Early calls do clock admission only, no sensor I/O.
    // No made-up catch-up ticks, delay, heap, background work or remote command.
    bool step();
    void abort();
    const RuntimeReport& report() const { return report_; }
    const Transaction& transaction() const { return transaction_; }
    const fsm::RobotInput& decisionInput() const { return decision_input_; }
    const line_qtr::Snapshot& lineEvidence() const { return decision_line_; }
    const imu::Estimate& imuEvidence() const { return imu_publication_; }
    const power::InputOwner& adcInputs() const { return adc_; }
private:
    // Implementation owner may extend private helpers/state only.
    bool validPorts() const;
    bool initializeSources();
    bool acceptClock(std::uint32_t now_us);
    bool clock(std::uint32_t& now_us);
    void fail(RuntimeFault fault);
    void cancelSources();
    bool releaseCharge();
    bool acquire();
    bool serviceImu();
    bool pump();
    bool servicePass();
    bool linesActive() const;
    bool linesUseful(std::uint32_t now_us) const;
    bool countPass();
    void rememberLines(const line_qtr::Snapshot& snapshot);
    void consumeImu(const imu::SampleProgress& progress);
    void publishImu(const imu::Sample& sample);
    void setupImuFault(std::uint32_t now_us);
    void skipBefore(std::uint32_t completed_us);
    bool completeEpoch();
    static fsm::RobotInput projectThunk(void* context, std::uint32_t now_us);
    static bool clockAcceptedThunk(void* context);
    fsm::RobotInput project(std::uint32_t now_us);
    void projectImu(std::uint32_t now_us, std::uint32_t elapsed_us);
    void projectLines(std::uint32_t now_us, std::uint32_t elapsed_us);
    bool opponentsFresh(std::uint32_t now_us) const;
    bool opponentsReady() const;
    bool postDecision();
    bool display();
    void selectLineMode();
    motors::Port motor_port_;
    power::InputPort adc_port_;
    SourcePort source_;
    Transaction transaction_;
    power::InputOwner adc_;
    imu::Estimator estimator_;
    qtr_cal::Calibration calibration_;
    SetupGrants grants_;
    RuntimeReport report_;
    fsm::RobotInput decision_input_;
    line_qtr::Snapshot decision_line_;
    imu::Estimate imu_publication_;
    power::ButtonRead buttons_;
    opp_sensors::Snapshot opponents_;
    line_qtr::Snapshot line_current_;
    line_qtr::Snapshot line_mailbox_;
    imu::SampleProgress imu_progress_;
    fsm::RobotResult last_robot_;
    bool attempted_ = false;
    bool clock_seen_ = false;
    bool clock_equal_ = false;
    bool decision_seen_ = false;
    bool projection_failed_ = false;
    bool estimator_ready_ = false;
    bool setup_fault_observed_ = false;
    bool imu_new_ = false;
    bool line_seen_ = false;
    bool line_new_ = false;
    bool line_expired_ = false;
    bool confirmed_bank_ = false;
    bool stop_tail_ = false;
    bool sources_cancelled_ = false;
    std::uint32_t last_clock_us_ = 0U;
    std::uint32_t last_decision_us_ = 0U;
    std::uint32_t idle_polls_ = 0U;
    std::uint32_t epoch_passes_ = 0U;
    std::uint32_t pump_started_us_ = 0U;
    std::uint32_t imu_age_us_ = 0U;
    std::uint32_t line_age_us_ = 0U;
};
} // namespace app

// Shows seven native opponent channels with explicit current and failed evidence.
// Provides a bounded motor-free P2 B1 bench with all native grants off by default.
// Independent literal-frame, timing, callback and native-binding tests verify D107.
#pragma once
#include "hal/opp_sensors.h"
#include "hal/ui_matrix_unoq.h"
#include <cstdint>

namespace opp_view {
enum class Phase : std::uint8_t { NOT_STARTED, DISABLED, RUNNING, FAULT };
enum class Fault : std::uint8_t { NONE, PORT, CONFIG, CLOCK, MATRIX };
struct Port {
    void* context = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
    opp_sensors::InitResult (*beginOpponents)(void*) = nullptr;
    opp_sensors::Snapshot (*readOpponents)(void*) = nullptr;
    ui::MatrixStatus (*beginMatrix)(void*, ui::MatrixGrant) = nullptr;
    ui::MatrixStatus (*submitMatrix)(void*, std::uint32_t, const ui::Frame&) = nullptr;
};
struct Grants {
    bool opponents = false;
    bool matrix = false;
    ui::MatrixGrant matrix_grant;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    Fault fault = Fault::NONE;
    bool fresh = false, current_available = false, sensor_error = false;
    bool counter_saturated = false, first_read_error_saved = false;
    std::uint8_t detection_mask = 0U;
    opp_sensors::InitResult setup;
    opp_sensors::Snapshot snapshot, first_read_error;
    ui::MatrixStatus matrix_setup = ui::MatrixStatus::NOT_INITIALIZED;
    ui::MatrixStatus matrix_status = ui::MatrixStatus::NOT_INITIALIZED;
    ui::Frame frame;
    std::uint32_t next_release_us = 0U;
    std::uint32_t read_attempts = 0U, valid_reads = 0U, invalid_reads = 0U;
    std::uint32_t missed_releases = 0U, completed_polls = 0U;
    std::uint32_t display_attempts = 0U, submissions = 0U, throttles = 0U;
    std::uint32_t last_read_us = 0U, maximum_read_us = 0U;
    std::uint32_t last_poll_us = 0U, maximum_poll_us = 0U;
};
class Runner {
public:
    explicit Runner(const Port& port);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    bool poll();
    const Report& report() const { return report_; }
private:
    // Implementation owner may add only private helpers and state.
    bool validPorts() const;
    bool clock(std::uint32_t& now_us);
    void fail(Fault fault);
    void add(std::uint32_t& counter, std::uint32_t amount = 1U);
    bool initialize();
    bool setupUsable() const;
    bool snapshotUsable(std::uint32_t before_us, std::uint32_t after_us) const;
    void invalidRead();
    bool read();
    void render();
    bool display();
    bool finish(std::uint32_t started_us, std::uint32_t next_release_us,
                std::uint32_t missed);
    Port port_;
    Grants grants_;
    Report report_;
    bool attempted_ = false;
    bool clock_seen_ = false;
    bool interval_active_ = false;
    bool sensors_ready_ = false;
    bool matrix_ready_ = false;
    bool display_attempted_ = false;
    std::uint32_t last_clock_us_ = 0U;
    std::uint32_t interval_elapsed_us_ = 0U;
    std::uint32_t last_display_us_ = 0U;
    std::uint32_t display_age_us_ = 0U;
};
} // namespace opp_view

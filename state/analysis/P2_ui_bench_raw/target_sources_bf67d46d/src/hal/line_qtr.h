// Acquires four RC timing intervals with bounded cooperative native operations.
// Preserves source identity, release skew and censored observations without guessing color.
// Independent native tests, core integration and an inert target probe test this boundary.
#pragma once
#include <cstdint>

namespace line_qtr {
enum class Phase : std::uint8_t { NOT_STARTED, IDLE, CHARGING, DISCHARGING, COMPLETE, FAULT };
enum class Status : std::uint8_t {
    OK, NOT_INITIALIZED, ALREADY_STARTED, BUSY, NOT_DUE, INVALID_CONFIG,
    OWNERSHIP, NATIVE_ERROR, READBACK, CHARGE_LOW, TIME_ORDER, CALL_DEADLINE,
    CHARGE_DEADLINE, FRAME_DEADLINE, ADVANCE_LIMIT, CLEANUP, CANCELLED, FAULT_LATCHED
};
struct Pad {
    std::uint32_t release_before_us = 0U;
    std::uint32_t release_after_us = 0U;
    std::uint32_t last_high_before_us = 0U;
    std::uint32_t first_low_after_us = 0U;
    std::uint32_t lower_us = 0U;
    std::uint32_t upper_us = 0U; // Exclusive; zero for timeout/no LOW, use masks.
};
struct Cleanup {
    std::uint8_t attempted_mask = 0U;
    std::uint8_t failed_mask = 0U;
    std::uint8_t skipped_mask = 0U;
    std::uint8_t nonneutral_mask = 0U;
    std::int32_t status[4] = {};
    std::uint32_t started_us = 0U;
    std::uint32_t completed_us = 0U;
    bool deadline_exceeded = false;
};
struct Snapshot {
    Phase phase = Phase::NOT_STARTED;
    Status status = Status::NOT_INITIALIZED;
    bool valid = false; // Complete raw evidence; color qualification is separate.
    std::uint32_t sequence = 0U;
    std::uint32_t started_us = 0U;
    std::uint32_t drive_completed_us = 0U;
    std::uint32_t checked_us = 0U;
    std::uint32_t completed_us = 0U;
    std::uint32_t advances = 0U;
    std::uint32_t max_service_gap_us = 0U;
    std::uint8_t released_mask = 0U;
    std::uint8_t high_mask = 0U;
    std::uint8_t low_mask = 0U;
    std::uint8_t timeout_mask = 0U;
    std::int32_t status_by_pad[4] = {};
    Pad pad[4];
    Cleanup cleanup;
};
class Reader {
public:
    Reader() = default;
    Reader(const Reader&) = delete;
    Reader& operator=(const Reader&) = delete;
    // One setup attempt. A caller grant is necessary, never proof of real handoff.
    Status begin(bool exclusive_pads = false);
    // BUSY/NOT_DUE do not replace the saved frame or manufacture a generation.
    Status start();
    Snapshot advance();
    Snapshot cancel(); // Active cancellation is a reset-only fault after cleanup.
    Snapshot report() const { return result_; }
private:
    bool globalOwned() const;
    bool padOwned(unsigned index) const;
    bool bankOwned() const;
    bool captureTime(std::uint32_t now);
    Status checkTime(std::uint32_t now);
    Status configure(unsigned index, bool output);
    Status readCharge(unsigned index);
    Status readDischarge(unsigned index);
    Status releaseBank();
    Status sampleBank();
    bool cleanup();
    void cleanupPad(unsigned index);
    void fail(Status status);
    void finish();
    Status setupBank();
    Status startBank();
    Status serviceFrame();
    Snapshot result_{};
    bool attempted_ = false;
    bool owned_ = false;
    bool have_time_ = false;
    bool have_start_ = false;
    std::uint32_t latest_us_ = 0U;
    std::uint32_t previous_start_us_ = 0U;
    std::uint32_t generation_ = 0U;
    std::uint32_t call_started_us_ = 0U;
    std::uint32_t service_us_ = 0U;
    std::uint32_t trace_ = 0U;
    std::uint32_t state_[4] = {};
    std::uint32_t old_state_[4] = {};
    std::uint32_t requested_state_[4] = {};
    std::uint8_t routes_[4] = {};
    std::uint8_t transition_mask_ = 0U;
    std::uint64_t frame_elapsed_us_ = 0U;
    bool timing_frame_ = false;
    bool charge_timed_ = false;
    bool cleanup_time_valid_ = true;
};
} // namespace line_qtr

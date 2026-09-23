// Collects B13 white/black RC intervals and atomically commits RAM thresholds.
// Genuine inhibited Robot service intents own each bounded capture stage.
// Independent interval, lifecycle, handover and exact export tests cover D089.
#pragma once
#include "line_qtr_adapter.h"
#include <cstddef>

namespace qtr_cal {
enum class Phase : std::uint8_t { INACTIVE, WAITING, COLLECTING, SUCCESS, REJECTED, CANCELLED };
enum class Reason : std::uint8_t {
    NONE, CONTEXT, TIME_ORDER, TOKEN_ORDER, INVALID_CONFIG, PROVIDER_FAULT,
    INVALID_RAW, STALE, SOURCE_ORDER, CONFLICTING_REPLAY, DEADLINE,
    CENSORED_WHITE, NO_SEPARATION, VERSION_EXHAUSTED
};
struct SensorEvidence {
    std::uint32_t white_upper_us = 0U;
    std::uint32_t black_lower_us = 0U;
    std::uint32_t white_count = 0U;
    std::uint32_t black_count = 0U;
    std::uint32_t black_censored = 0U;
};
struct Report {
    Phase phase = Phase::INACTIVE;
    Reason reason = Reason::NONE;
    std::uint8_t stage = 0U; // FLwhite,FLblack,FRwhite,FRblack,RLwhite,RLblack,RRwhite,RRblack.
    std::uint32_t samples = 0U;
    std::uint32_t capture_started_us = 0U;
    std::uint32_t completed_us = 0U;
    std::uint32_t last_source_us = 0U;
    std::uint32_t last_sequence = 0U;
    SensorEvidence sensors[4];
    line_qtr::Thresholds thresholds; // Last fully committed bank, not partial candidates.
    bool committed = false; // One-call publication pulse only.
};
class Calibration {
public:
    // Caller pairs the current actual Robot result and same native Snapshot with t_us.
    // One owner/reset domain. Duplicate result token is ignored; no I/O or motion.
    Report step(std::uint32_t t_us, const fsm::RobotResult& robot,
                const line_qtr::Snapshot& snapshot);
    const line_qtr::Thresholds& thresholds() const { return report_.thresholds; }
    void reset(); // Actual owner reset only; does not reset Robot or native Reader.
private:
    bool eligible(const fsm::RobotResult& robot) const;
    void reject(Reason reason);
    void start(std::uint32_t t_us);
    bool admit(std::uint32_t t_us, const line_qtr::Snapshot& snapshot);
    void collect(std::uint32_t t_us, const line_qtr::Snapshot& snapshot);
    void finishStage(std::uint32_t t_us);
    Report report_;
    line_qtr::Thresholds candidate_;
    line_qtr::Snapshot previous_;
    std::uint64_t last_token_ = 0U;
    std::uint32_t last_us_ = 0U;
    std::uint32_t capture_age_us_ = 0U;
    std::uint32_t source_age_us_ = 0U;
    bool observed_ = false;
    bool source_seen_ = false;
};
enum class FormatStatus : std::uint8_t { OK, UNAVAILABLE, INVALID, BUFFER_TOO_SMALL };
inline constexpr std::size_t CONFIG_SNIPPET_CAPACITY = 80U;
// On failure written=0 and output[0]=NUL when writable. Never emit a partial snippet.
FormatStatus formatConfig(const Report& report, char* output, std::size_t capacity,
                          std::size_t& written);
} // namespace qtr_cal

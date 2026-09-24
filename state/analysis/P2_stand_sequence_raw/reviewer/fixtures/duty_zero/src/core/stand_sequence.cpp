// Implements the finite P2 B4 directional request sequence from D119.
// Preserves observed brake/coast intervals without granting motor authority.
// Independent host contract tests cover timing, preemption and terminal states.
#include "stand_sequence.h"
#include "../config.h"

namespace stand_sequence {
namespace detail {
constexpr std::uint8_t SEGMENT_COUNT = 12U;
constexpr std::uint64_t SEGMENT_DURATION_US =
    static_cast<std::uint64_t>(config::STAND_SEGMENT_MS) * 1000U;
constexpr std::uint32_t CLOCK_HALF_RANGE_US = 0x80000000U;
static_assert(config::STAND_SEGMENT_MS > 0U, "Stand segments must have a duration");
static_assert(config::STAND_DUTY > 0.0F && config::STAND_DUTY < 1.0F,
              "Stand requests must be finite and strictly between zero and one");
static_assert(SEGMENT_COUNT * 2U * SEGMENT_DURATION_US < CLOCK_HALF_RANGE_US,
              "The complete observed sequence must fit below clock half range");

struct Segment {
    Phase phase;
    float duty_l;
    float duty_r;
};

constexpr Segment SEGMENTS[SEGMENT_COUNT] = {
    {Phase::DRIVE,  config::STAND_DUTY, 0.0F},
    {Phase::BRAKE,  0.0F, 0.0F},
    {Phase::COAST,  0.0F, 0.0F},
    {Phase::DRIVE, -config::STAND_DUTY, 0.0F},
    {Phase::BRAKE,  0.0F, 0.0F},
    {Phase::COAST,  0.0F, 0.0F},
    {Phase::DRIVE,  0.0F,  config::STAND_DUTY},
    {Phase::BRAKE,  0.0F, 0.0F},
    {Phase::COAST,  0.0F, 0.0F},
    {Phase::DRIVE,  0.0F, -config::STAND_DUTY},
    {Phase::BRAKE,  0.0F, 0.0F},
    {Phase::COAST,  0.0F, 0.0F}
};

bool isActive(Phase phase) {
    return phase == Phase::DRIVE || phase == Phase::BRAKE || phase == Phase::COAST;
}
} // namespace detail

bool Sequence::start(std::uint32_t t_us) {
    if (started_) return false;
    started_ = true;
    last_us_ = entered_us_ = t_us;
    report_.fresh = true;
    selectSegment();
    return true;
}

Report Sequence::step(std::uint32_t t_us, bool edge_required, bool stop_requested) {
    report_.fresh = false;
    report_.phase_changed = false;
    if (!started_ || !detail::isActive(report_.phase) || t_us == last_us_) {
        return report_;
    }

    const std::uint32_t delta_us = t_us - last_us_;
    last_us_ = t_us;
    report_.fresh = true;
    if (delta_us >= detail::CLOCK_HALF_RANGE_US) {
        terminate(Phase::FAULT, Reason::CLOCK_ORDER);
    } else if (stop_requested) {
        terminate(Phase::INTERRUPTED, Reason::STOP);
    } else if (edge_required) {
        terminate(Phase::INTERRUPTED, Reason::EDGE);
    } else if (delta_us >= detail::SEGMENT_DURATION_US) {
        terminate(Phase::FAULT, Reason::CLOCK_GAP);
    } else if (t_us - entered_us_ >= detail::SEGMENT_DURATION_US) {
        ++report_.segment;
        if (report_.segment == detail::SEGMENT_COUNT) {
            terminate(Phase::COMPLETE, Reason::NONE);
        } else {
            // Anchor here so a delayed observation cannot shorten the next row.
            entered_us_ = t_us;
            selectSegment();
        }
    }
    return report_;
}

void Sequence::selectSegment() {
    const detail::Segment& segment = detail::SEGMENTS[report_.segment];
    report_.phase = segment.phase;
    report_.reason = Reason::NONE;
    report_.duty_l = segment.duty_l;
    report_.duty_r = segment.duty_r;
    report_.phase_changed = true;
}

void Sequence::terminate(Phase phase, Reason reason) {
    report_.phase = phase;
    report_.reason = reason;
    report_.duty_l = 0.0F;
    report_.duty_r = 0.0F;
    report_.phase_changed = true;
}
} // namespace stand_sequence

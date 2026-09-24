
#include "src/core/stand_sequence.h"
#include <cmath>
#include <cstdint>
using namespace stand_sequence;
int main() {
    constexpr std::uint32_t d = 500000U;
    constexpr float duty = 0.125F;
    constexpr Phase phases[3] = {Phase::DRIVE, Phase::BRAKE, Phase::COAST};
    Sequence sequence;
    const std::uint32_t origin = 0xfff00000U;
    if (!sequence.start(origin)) return 1;
    auto entered = origin;
    for (unsigned row = 0; row < 12; ++row) {
        const auto report = sequence.report();
        const float signed_duty = (row == 0 || row == 6) ? duty : -duty;
        const float left = (row == 0 || row == 3) ? signed_duty : 0.0F;
        const float right = (row == 6 || row == 9) ? signed_duty : 0.0F;
        if (report.phase != phases[row % 3] || report.segment != row ||
            report.reason != Reason::NONE || report.duty_l != left ||
            report.duty_r != right || !std::isfinite(left) || !std::isfinite(right) ||
            !report.fresh || !report.phase_changed) return 2;
        const auto before = sequence.step(entered + d - 1U);
        if (before.segment != row || before.phase_changed || !before.fresh) return 3;
        entered += 2U * d - 2U;
        const auto after = sequence.step(entered);
        if (after.segment != row + 1U || !after.phase_changed || !after.fresh) return 4;
    }
    const auto complete = sequence.report();
    if (complete.phase != Phase::COMPLETE || complete.reason != Reason::NONE ||
        complete.duty_l != 0 || complete.duty_r != 0 ||
        static_cast<std::uint32_t>(entered - origin) != 12U * (2U * d - 2U)) return 5;
    if (sequence.start(0)) return 6;
    const auto passive = sequence.step(origin, true, true);
    if (passive.phase != Phase::COMPLETE || passive.reason != Reason::NONE ||
        passive.segment != 12 || passive.fresh || passive.phase_changed) return 7;
    Sequence gap;
    if (!gap.start(origin)) return 8;
    const auto failure = gap.step(origin + d);
    if (failure.phase != Phase::FAULT || failure.reason != Reason::CLOCK_GAP ||
        failure.duty_l != 0 || failure.duty_r != 0) return 9;
    return 0;
}

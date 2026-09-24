// Reviews directed turn requests against independent angle and lifetime properties.
// Keeps this synthetic host evidence separate from integration or physical claims.
// Compile only after the coordinator's public-oracle and source freeze.
#include "core/turn_trial.h"
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <limits>

namespace {
std::uint64_t checks = 0;
bool check(bool condition, const char* name) {
    ++checks;
    if (!condition) std::printf("FAIL %s at check %llu\n", name,
                               static_cast<unsigned long long>(checks));
    return condition;
}
#define VERIFY(expr) do { if (!check((expr), #expr)) return false; } while (false)
bool finite(const turn_trial::Report& r) {
    return std::isfinite(r.duty_l) && std::isfinite(r.duty_r) &&
           std::isfinite(r.signed_angle_deg) && std::abs(r.duty_l) <= 0.8F &&
           std::abs(r.duty_r) <= 0.8F;
}
bool angleProperties() {
    const float origins[] = {-720.5F, -0.5F, 0.0F, 123.5F, 1080.0F};
    for (float origin : origins) for (float angle : {90.0F, 180.0F}) {
        for (int eighths = -5760; eighths <= 5760; ++eighths) {
            const float progress = static_cast<float>(eighths) / 8.0F;
            turn_trial::Trial right, left;
            VERIFY(right.start(0xfffffff0U, origin, angle, true));
            VERIFY(left.start(0xfffffff0U, -origin, -angle, true));
            auto r = right.step({16U, origin + progress, true, false, false});
            auto l = left.step({16U, -origin - progress, true, false, false});
            // An independent shortest-angle convention: (-180,180], +180 tie.
            double error = std::remainder(static_cast<double>(angle) - progress, 360.0);
            if (error == -180.0) error = 180.0;
            const bool done = std::abs(error) < 5.0;
            double expected = std::abs(error) * 0.02F;
            if (expected < 0.25) expected = 0.25;
            if (expected > 0.8F) expected = 0.8F;
            if (error < 0.0) expected = -expected;
            if (done) expected = 0.0;
            VERIFY(finite(r) && finite(l));
            VERIFY(std::abs(r.duty_l - expected) < 0.000001);
            VERIFY(r.duty_r == -r.duty_l);
            VERIFY(l.duty_l == r.duty_r && l.duty_r == r.duty_l);
            VERIFY(r.phase == (done ? turn_trial::Phase::BRAKE : turn_trial::Phase::TURN));
            VERIFY(l.phase == r.phase && l.turn_status == r.turn_status);
            VERIFY(r.turn_finished == done && l.turn_finished == done);
            VERIFY(!r.finished && !l.finished && r.fresh && l.fresh);
            VERIFY(r.turn_finished_us == (done ? 16U : 0U));
        }
    }
    return true;
}
bool cancellationProperties() {
    const float nan = std::numeric_limits<float>::quiet_NaN();
    for (std::uint32_t start : {0U, 0xffffff00U, 0x80000000U}) {
        for (std::uint32_t elapsed = 1U; elapsed <= 700U; ++elapsed) {
            for (bool stop : {false, true}) {
                turn_trial::Trial trial;
                VERIFY(trial.start(start, 17.0F, -180.0F, false));
                const auto r = trial.step({start + elapsed * 1000U, nan, true, true, stop});
                VERIFY(r.phase == turn_trial::Phase::INTERRUPTED);
                VERIFY(r.reason == (stop ? turn_trial::Reason::STOP : turn_trial::Reason::EDGE));
                VERIFY(r.turn_status == motion::Status::ACTIVE && r.imu_fallback);
                VERIFY(!r.turn_finished && r.finished && r.finished_us == start + elapsed * 1000U);
                VERIFY(r.duty_l == 0.0F && r.duty_r == 0.0F && finite(r));
                const auto after = trial.step({start + elapsed * 1000U + 1U, 17.0F, true, false, false});
                VERIFY(after.phase == r.phase && after.reason == r.reason && !after.fresh);
                VERIFY(after.finished_us == r.finished_us && !after.phase_changed);
                VERIFY(!trial.start(start + 1U, 0.0F, 90.0F, true));
                VERIFY(trial.report().finished_us == r.finished_us && !trial.report().fresh);
            }
        }
    }
    return true;
}
bool boundaryProperties() {
    const float nan = std::numeric_limits<float>::quiet_NaN();
    for (std::uint32_t start : {0U, 0xffffff00U, 0x80000000U}) {
        turn_trial::Trial timeout;
        VERIFY(timeout.start(start, 0.0F, 90.0F, true));
        auto r = timeout.step({start + 700000U, nan, true, false, false});
        VERIFY(r.phase == turn_trial::Phase::BRAKE && r.turn_status == motion::Status::TIMED_OUT);
        VERIFY(r.turn_finished && !r.finished && r.turn_finished_us == start + 700000U);
        r = timeout.step({start + 1199999U, nan, true, false, false});
        VERIFY(r.phase == turn_trial::Phase::BRAKE && !r.finished);
        r = timeout.step({start + 1200000U, nan, true, false, false});
        VERIFY(r.phase == turn_trial::Phase::COMPLETE && r.finished && finite(r));
        VERIFY(r.turn_status == motion::Status::TIMED_OUT);
        turn_trial::Trial backwards;
        VERIFY(backwards.start(start, 0.0F, -90.0F, true));
        r = backwards.step({start + 0x80000000U, nan, true, true, true});
        VERIFY(r.phase == turn_trial::Phase::FAULT && r.reason == turn_trial::Reason::CLOCK_ORDER);
        VERIFY(r.turn_status == motion::Status::ACTIVE && !r.turn_finished && finite(r));
        turn_trial::Trial delayed;
        VERIFY(delayed.start(start, 0.0F, 180.0F, true));
        r = delayed.step({start + 0x7fffffffU, 0.0F, true, false, false});
        VERIFY(r.phase == turn_trial::Phase::BRAKE && !r.finished);
        VERIFY(r.turn_finished_us == start + 0x7fffffffU);
        r = delayed.step({start + 0x7fffffffU + 499999U, nan, true, false, false});
        VERIFY(r.phase == turn_trial::Phase::BRAKE && !r.finished);
        r = delayed.step({start + 0x7fffffffU + 500000U, nan, true, false, false});
        VERIFY(r.phase == turn_trial::Phase::COMPLETE && r.finished && finite(r));
    }
    return true;
}
} // namespace
int main() {
    if (!angleProperties() || !cancellationProperties() || !boundaryProperties()) return 1;
    std::printf("PASS 3 independent property groups; %llu checks\n",
                static_cast<unsigned long long>(checks));
}

// Tests the D124 finite P3 turn-trial contract through its public interface.
// Derives signed motion and safety boundaries from B7 without implementation reads.
// Frozen independent cases cover finite requests, reflected yaw and observed timing.
#include "doctest.h"
#include "config.h"
#include "core/turn_trial.h"
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <initializer_list>
#include <limits>

#define TURN_REQUIRE(...) do { const bool passed = (__VA_ARGS__); \
    CHECK_MESSAGE(passed, #__VA_ARGS__); if (!passed) std::abort(); } while (false)

namespace {
using turn_trial::Phase;
using turn_trial::Reason;
using turn_trial::Report;
using turn_trial::Trial;
using motion::Status;
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_YAW = std::numeric_limits<float>::infinity();
constexpr float ANGLES[] = {-180.0F, -90.0F, 90.0F, 180.0F};

Report step(Trial& trial, std::uint32_t time, float yaw, bool imu = true,
            bool edge = false, bool stop = false) {
    return trial.step({time, yaw, imu, edge, stop});
}
void bounded(const Report& r) {
    CHECK(std::isfinite(r.signed_angle_deg));
    CHECK(std::isfinite(r.duty_l)); CHECK(std::isfinite(r.duty_r));
    CHECK(std::fabs(r.duty_l) <= .80F); CHECK(std::fabs(r.duty_r) <= .80F);
    CHECK(r.duty_l == -r.duty_r);
    if (r.phase != Phase::TURN) { CHECK(r.duty_l == 0.0F); CHECK(r.duty_r == 0.0F); }
}
void same(const Report& actual, const Report& expected, bool preserve_pulses) {
    CHECK(actual.phase == expected.phase); CHECK(actual.reason == expected.reason);
    CHECK(actual.turn_status == expected.turn_status);
    CHECK(actual.signed_angle_deg == expected.signed_angle_deg);
    CHECK(actual.duty_l == expected.duty_l); CHECK(actual.duty_r == expected.duty_r);
    CHECK(actual.started_us == expected.started_us);
    CHECK(actual.turn_finished_us == expected.turn_finished_us);
    CHECK(actual.finished_us == expected.finished_us);
    CHECK(actual.imu_fallback == expected.imu_fallback);
    CHECK(actual.turn_finished == expected.turn_finished); CHECK(actual.finished == expected.finished);
    CHECK(actual.fresh == (preserve_pulses && expected.fresh));
    CHECK(actual.phase_changed == (preserve_pulses && expected.phase_changed)); bounded(actual);
}
void active(const Report& r, float left, bool changed = false) {
    CHECK(r.phase == Phase::TURN); CHECK(r.reason == Reason::NONE);
    CHECK(r.turn_status == Status::ACTIVE); CHECK(r.fresh); CHECK(r.phase_changed == changed);
    CHECK(r.duty_l == doctest::Approx(left)); CHECK(r.duty_r == doctest::Approx(-left));
    CHECK_FALSE(r.turn_finished); CHECK_FALSE(r.finished); bounded(r);
}
void brake(const Report& r, Status status, std::uint32_t observed, bool changed = true) {
    CHECK(r.phase == Phase::BRAKE); CHECK(r.reason == Reason::NONE);
    CHECK(r.turn_status == status); CHECK(r.turn_finished); CHECK_FALSE(r.finished);
    CHECK(r.turn_finished_us == observed); CHECK(r.fresh); CHECK(r.phase_changed == changed);
    bounded(r);
}
void complete(const Report& r, Status status, std::uint32_t turn_time, std::uint32_t time) {
    CHECK(r.phase == Phase::COMPLETE); CHECK(r.reason == Reason::NONE);
    CHECK(r.turn_status == status); CHECK(r.turn_finished); CHECK(r.finished);
    CHECK(r.turn_finished_us == turn_time); CHECK(r.finished_us == time);
    CHECK(r.fresh); CHECK(r.phase_changed); bounded(r);
}
void stopped(const Report& r, Phase phase, Reason reason, std::uint32_t time) {
    CHECK(r.phase == phase); CHECK(r.reason == reason); CHECK(r.finished);
    CHECK(r.finished_us == time); CHECK(r.fresh); CHECK(r.phase_changed); bounded(r);
}
} // namespace

TEST_CASE("B7 P3 D124 unstarted reports are inert and step cannot consume the one start") {
    Trial trial; const auto initial = trial.report();
    CHECK(initial.phase == Phase::NOT_STARTED); CHECK(initial.reason == Reason::NONE);
    CHECK(initial.turn_status == Status::IDLE); CHECK(initial.signed_angle_deg == 0.0F);
    CHECK(initial.started_us == 0U); CHECK(initial.turn_finished_us == 0U);
    CHECK(initial.finished_us == 0U); CHECK_FALSE(initial.finished);
    CHECK_FALSE(initial.turn_finished); CHECK_FALSE(initial.imu_fallback);
    CHECK_FALSE(initial.fresh); CHECK_FALSE(initial.phase_changed); bounded(initial);
    same(step(trial, 0xffffffffU, NAN_YAW, true, true, true), initial, false);
    same(step(trial, 0U, INF_YAW, false), initial, false);
    TURN_REQUIRE(trial.start(23U, 0.0F, 90.0F, true)); active(trial.report(), .8F, true);
    CHECK(config::TURN_TRIAL_BRAKE_MS == 500U); CHECK(config::TURN_TIMEOUT_MS == 700U);
    CHECK(config::TURN_MS_PER_DEG == 2.0F); CHECK(config::TURN_DUTY == .80F);
}

TEST_CASE("B7 P3 D124 exactly four signed starts retain actual half-turn direction at finite origins") {
    for (float angle : ANGLES) for (float origin : {0.0F, -0.0F, .000001F, -.000001F,
            170.0F, -170.0F, 36000000.0F, std::numeric_limits<float>::max(),
            -std::numeric_limits<float>::max()}) {
        CAPTURE(angle); CAPTURE(origin); Trial trial;
        TURN_REQUIRE(trial.start(4321U, origin, angle, true));
        const float direction = angle > 0.0F ? 1.0F : -1.0F;
        active(trial.report(), direction * .80F, true);
        CHECK(trial.report().signed_angle_deg == angle); CHECK(trial.report().started_us == 4321U);
        CHECK_FALSE(trial.report().imu_fallback);
        active(step(trial, 4322U, origin), direction * .80F);
    }
}

TEST_CASE("B7 P3 D124 invalid signed angles consume the only attempt without accepted start fields") {
    const float invalid[] = {0.0F, -0.0F, 1.0F, -1.0F, 45.0F, -45.0F, 360.0F, -360.0F,
        89.0F, 91.0F, 179.0F, 181.0F, NAN_YAW, INF_YAW, -INF_YAW,
        std::nextafter(90.0F, 0.0F), std::nextafter(90.0F, INF_YAW),
        std::nextafter(-90.0F, 0.0F), std::nextafter(-90.0F, -INF_YAW),
        std::nextafter(180.0F, 0.0F), std::nextafter(180.0F, INF_YAW),
        std::nextafter(-180.0F, 0.0F), std::nextafter(-180.0F, -INF_YAW)};
    for (float angle : invalid) {
        CAPTURE(angle); Trial trial; CHECK_FALSE(trial.start(12345U, 12.0F, angle, true));
        const auto rejected = trial.report(); stopped(rejected, Phase::FAULT, Reason::INVALID_START, 12345U);
        CHECK(rejected.turn_status == Status::IDLE);
        CHECK(rejected.signed_angle_deg == 0.0F); CHECK(rejected.started_us == 0U);
        CHECK_FALSE(rejected.turn_finished); CHECK(rejected.turn_finished_us == 0U);
        CHECK_FALSE(trial.start(12346U, 0.0F, 90.0F, true)); same(trial.report(), rejected, true);
        same(step(trial, 12346U, 90.0F), rejected, false);
    }
}

TEST_CASE("B7 P3 D124 nonfinite initial yaw is invalid even when the real IMU is unavailable") {
    for (float yaw : {NAN_YAW, INF_YAW, -INF_YAW}) for (bool imu : {false, true}) {
        Trial trial; CHECK_FALSE(trial.start(0U, yaw, -180.0F, imu));
        const auto rejected = trial.report(); stopped(rejected, Phase::FAULT, Reason::INVALID_START, 0U);
        CHECK(rejected.turn_status == Status::IDLE);
        CHECK(rejected.started_us == 0U); CHECK(rejected.signed_angle_deg == 0.0F);
        CHECK_FALSE(rejected.turn_finished); CHECK_FALSE(trial.start(1U, 0.0F, -180.0F, true));
        same(trial.report(), rejected, true);
    }
}

TEST_CASE("B7 P3 D124 repeated start is passive and preserves current report including action pulses") {
    Trial trial; TURN_REQUIRE(trial.start(100U, 10.0F, -90.0F, true));
    const auto initial = trial.report();
    CHECK_FALSE(trial.start(0U, NAN_YAW, 0.0F, false)); same(trial.report(), initial, true);
    active(step(trial, 101U, -60.0F), -.4F); const auto moving = trial.report();
    CHECK_FALSE(trial.start(1000000U, 0.0F, 180.0F, true)); same(trial.report(), moving, true);
    brake(step(trial, 102U, -80.0F), Status::DONE, 102U); const auto braking = trial.report();
    CHECK_FALSE(trial.start(102U, 0.0F, 90.0F, true)); same(trial.report(), braking, true);
    complete(step(trial, 500102U, NAN_YAW), Status::DONE, 102U, 500102U);
    const auto terminal = trial.report(); CHECK_FALSE(trial.start(500103U, 0.0F, 90.0F, true));
    same(trial.report(), terminal, true);
}

TEST_CASE("B7 P3 D124 strict five-degree tolerance preserves both adjacent floats around zero target") {
    for (float angle : ANGLES) for (float side : {-1.0F, 1.0F})
        for (float magnitude : {std::nextafter(5.0F, 0.0F), 5.0F, std::nextafter(5.0F, 6.0F)}) {
            CAPTURE(angle); CAPTURE(side); CAPTURE(magnitude); Trial trial;
            TURN_REQUIRE(trial.start(0U, -angle, angle, true));
            const auto result = step(trial, 1000U, side * magnitude);
            if (magnitude < 5.0F) brake(result, Status::DONE, 1000U);
            else active(result, -side * .25F);
        }
}

TEST_CASE("B7 P3 D124 real yaw sets proportional minimum maximum and overshoot correction") {
    constexpr float ERRORS[] = {5.0F, 10.0F, 20.0F, 40.0F, 60.0F};
    constexpr float DUTIES[] = {.25F, .25F, .40F, .80F, .80F};
    for (float angle : ANGLES) for (float side : {-1.0F, 1.0F})
        for (unsigned i = 0U; i < 5U; ++i) {
            Trial trial; TURN_REQUIRE(trial.start(0U, -angle, angle, true));
            active(step(trial, 1000U, -side * ERRORS[i]), side * DUTIES[i]);
        }
}

TEST_CASE("B7 P3 D124 left and right requests mirror the same actual trajectory and completion") {
    for (float angle : {90.0F, 180.0F}) for (float origin : {-170.0F, 0.0F, 123.0F}) {
        Trial right, left; TURN_REQUIRE(right.start(700U, origin, angle, true));
        TURN_REQUIRE(left.start(700U, -origin, -angle, true));
        const float progress[] = {0.0F, 30.0F, angle - 20.0F, angle - 5.0F, angle};
        for (unsigned i = 0U; i < 5U; ++i) {
            const auto r = step(right, 1700U + i * 1000U, origin + progress[i]);
            const auto l = step(left, 1700U + i * 1000U, -origin - progress[i]);
            CHECK(r.phase == l.phase); CHECK(r.turn_status == l.turn_status);
            CHECK(r.duty_l == l.duty_r); CHECK(r.duty_r == l.duty_l);
            CHECK(r.imu_fallback == l.imu_fallback); CHECK(r.turn_finished == l.turn_finished);
            bounded(r); bounded(l);
        }
        CHECK(right.report().turn_status == Status::DONE); CHECK(left.report().turn_status == Status::DONE);
    }
}

TEST_CASE("B7 P3 D124 wrapped and accumulated actual yaw preserve relative capture") {
    for (float direction : {-1.0F, 1.0F}) for (float revolutions : {-1080.0F, 0.0F, 1080.0F}) {
        Trial trial; TURN_REQUIRE(trial.start(0U, direction * 170.0F + revolutions,
                                             direction * 90.0F, true));
        active(step(trial, 1000U, -direction * 170.0F + revolutions), direction * .8F);
        active(step(trial, 2000U, -direction * 125.0F + revolutions), direction * .5F);
        brake(step(trial, 3000U, -direction * 104.0F + revolutions), Status::DONE, 3000U);
    }
}

TEST_CASE("B7 P3 D124 large finite origins keep the exact relative target without float addition loss") {
    for (float direction : {-1.0F, 1.0F}) {
        Trial trial; TURN_REQUIRE(trial.start(0U, direction * 67108864.0F,
                                             direction * 90.0F, true));
        brake(step(trial, 1000U, direction * 67108952.0F), Status::DONE, 1000U);
        Trial coarse; TURN_REQUIRE(coarse.start(0U, direction * 1073741824.0F,
                                                direction * 180.0F, true));
        active(step(coarse, 1000U, direction * 1073741952.0F), direction * .8F);
        active(step(coarse, 2000U, direction * 1073742080.0F), -direction * .8F);
        brake(step(coarse, 700000U, direction * 1073742080.0F), Status::TIMED_OUT, 700000U);
    }
}

TEST_CASE("B7 P3 D124 actual missing IMU uses full signed-angle fallback and ignores recovery target") {
    for (float angle : ANGLES) for (std::uint32_t base : {0U, 0xffff0000U}) {
        Trial trial; TURN_REQUIRE(trial.start(base, 10.0F, angle, false));
        const float direction = angle > 0.0F ? 1.0F : -1.0F;
        const std::uint32_t duration = std::fabs(angle) == 90.0F ? 180000U : 360000U;
        active(trial.report(), direction * .8F, true); CHECK(trial.report().imu_fallback);
        auto result = step(trial, base + 1U, 10.0F + angle, true);
        active(result, direction * .8F); CHECK(result.imu_fallback);
        result = step(trial, base + duration - 1U, NAN_YAW, false);
        active(result, direction * .8F); CHECK(result.imu_fallback);
        brake(step(trial, base + duration, INF_YAW, false), Status::DONE, base + duration);
        complete(step(trial, base + duration + 500000U, NAN_YAW), Status::DONE,
                 base + duration, base + duration + 500000U);
    }
}

TEST_CASE("B7 P3 D124 mid-turn loss latches last real remaining angle from first unavailable tick") {
    for (float angle : ANGLES) {
        const float direction = angle > 0.0F ? 1.0F : -1.0F;
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, angle, true));
        active(step(trial, 20000U, angle - direction * 30.0F), direction * .6F);
        auto result = step(trial, 30000U, NAN_YAW, false);
        active(result, direction * .8F); CHECK(result.imu_fallback);
        result = step(trial, 80000U, angle, true);
        active(result, direction * .8F); CHECK(result.imu_fallback);
        active(step(trial, 89999U, -INF_YAW, false), direction * .8F);
        brake(step(trial, 90000U, 0.0F, true), Status::DONE, 90000U);
    }
}

TEST_CASE("B7 P3 D124 fallback after overshoot retains actual corrective direction in both frames") {
    for (float angle : ANGLES) {
        const float direction = angle > 0.0F ? 1.0F : -1.0F;
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, angle, true));
        active(step(trial, 10000U, angle + direction * 10.0F), -direction * .25F);
        active(step(trial, 20000U, NAN_YAW, false), -direction * .8F);
        CHECK(trial.report().imu_fallback);
        active(step(trial, 39999U, angle, true), -direction * .8F);
        brake(step(trial, 40000U, angle, true), Status::DONE, 40000U);
    }
}

TEST_CASE("B7 P3 D124 original 700ms timeout wins exact healthy completion and stays distinct") {
    for (float angle : ANGLES) for (std::uint32_t base : {123U, 0xffff0000U}) {
        Trial trial; TURN_REQUIRE(trial.start(base, 0.0F, angle, true));
        active(step(trial, base + 699999U, 0.0F), angle > 0.0F ? .8F : -.8F);
        brake(step(trial, base + 700000U, angle), Status::TIMED_OUT, base + 700000U);
        complete(step(trial, base + 1200000U, angle), Status::TIMED_OUT,
                 base + 700000U, base + 1200000U);
    }
}

TEST_CASE("B7 P3 D124 original timeout wins fallback completion tie and healthy nonfinite deadline") {
    for (float angle : ANGLES) for (bool nonfinite_at_deadline : {false, true}) {
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, angle, true));
        const std::uint32_t lost = std::fabs(angle) == 90.0F ? 520000U : 340000U;
        active(step(trial, lost, NAN_YAW, false), angle > 0.0F ? .8F : -.8F);
        active(step(trial, 699999U, angle, true), angle > 0.0F ? .8F : -.8F);
        const auto done = step(trial, 700000U, nonfinite_at_deadline ? NAN_YAW : angle, true);
        brake(done, Status::TIMED_OUT, 700000U);
    }
}

TEST_CASE("B7 P3 D124 healthy nonfinite yaw faults active and latched-fallback turns before timeout") {
    for (float bad : {NAN_YAW, INF_YAW, -INF_YAW}) for (bool missing : {false, true}) {
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, -180.0F, !missing));
        const auto invalid = step(trial, 1000U, bad, true);
        stopped(invalid, Phase::FAULT, Reason::INVALID_HEADING, 1000U);
        CHECK(invalid.turn_status == Status::INVALID); CHECK_FALSE(invalid.turn_finished);
        same(step(trial, 2000U, -180.0F), invalid, false);
    }
}

TEST_CASE("B7 P3 D124 ordinary delayed observations enter a full new brake interval without backdating") {
    for (bool timed_out : {false, true}) {
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, 90.0F, true));
        const auto observed = timed_out ? 10000000U : 650000U;
        const auto status = timed_out ? Status::TIMED_OUT : Status::DONE;
        brake(step(trial, observed, 90.0F), status, observed);
        brake(step(trial, observed + 499999U, NAN_YAW), status, observed, false);
        complete(step(trial, observed + 500000U, INF_YAW), status, observed, observed + 500000U);
    }
}

TEST_CASE("B7 P3 D124 BRAKE ignores heading and real IMU changes for its entire requested interval") {
    Trial trial; TURN_REQUIRE(trial.start(100U, 0.0F, -90.0F, true));
    brake(step(trial, 101U, -90.0F), Status::DONE, 101U);
    const auto fallback = trial.report().imu_fallback;
    for (unsigned i = 0U; i < 6U; ++i) {
        const float headings[] = {NAN_YAW, INF_YAW, -INF_YAW, 1e30F, -1e30F, 180.0F};
        const auto result = step(trial, 102U + i * 50000U, headings[i], (i % 2U) != 0U);
        brake(result, Status::DONE, 101U, false); CHECK(result.imu_fallback == fallback);
    }
    complete(step(trial, 500101U, NAN_YAW), Status::DONE, 101U, 500101U);
}

TEST_CASE("B7 P3 D124 turn and trial completion flags distinguish actual timestamp zero") {
    Trial turn_zero; TURN_REQUIRE(turn_zero.start(0xfffffff0U, 0.0F, 90.0F, true));
    brake(step(turn_zero, 0U, 90.0F), Status::DONE, 0U);
    complete(step(turn_zero, 500000U, 90.0F), Status::DONE, 0U, 500000U);
    constexpr std::uint32_t brake_time = 0U - 500000U;
    Trial finish_zero; TURN_REQUIRE(finish_zero.start(brake_time - 1000U, 0.0F, -180.0F, true));
    brake(step(finish_zero, brake_time, -180.0F), Status::DONE, brake_time);
    complete(step(finish_zero, 0U, -180.0F), Status::DONE, brake_time, 0U);
}

TEST_CASE("B7 P3 D124 half-range and reversed clocks fault before local STOP edge or motion") {
    for (bool braking : {false, true}) for (std::uint32_t delta : {0x80000000U, 0x80000001U, 0xffffffffU}) {
        Trial trial; TURN_REQUIRE(trial.start(100U, 0.0F, 90.0F, true));
        std::uint32_t last = 100U;
        if (braking) { brake(step(trial, 101U, 90.0F), Status::DONE, 101U); last = 101U; }
        const auto fault = step(trial, last + delta, NAN_YAW, true, true, true);
        stopped(fault, Phase::FAULT, Reason::CLOCK_ORDER, last + delta);
        CHECK(fault.turn_status == (braking ? Status::DONE : Status::ACTIVE));
        CHECK_FALSE(fault.imu_fallback);
        CHECK(fault.turn_finished == braking);
        if (braking) CHECK(fault.turn_finished_us == 101U);
    }
    Trial forward; TURN_REQUIRE(forward.start(123U, 0.0F, 90.0F, true));
    constexpr std::uint32_t observed = 123U + 0x7fffffffU;
    brake(step(forward, observed, 0.0F), Status::TIMED_OUT, observed);
    complete(step(forward, observed + 0x7fffffffU, NAN_YAW), Status::TIMED_OUT,
             observed, observed + 0x7fffffffU);
}

TEST_CASE("B3 B4 B7 P3 D124 STOP wins edge and both preempt motion and brake completion") {
    for (bool braking : {false, true}) for (unsigned signals : {1U, 2U, 3U}) {
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, -90.0F, true));
        if (braking) brake(step(trial, 1000U, -90.0F), Status::DONE, 1000U);
        const auto time = braking ? 501000U : 700000U;
        const bool stop = (signals & 1U) != 0U, edge = (signals & 2U) != 0U;
        const auto result = step(trial, time, NAN_YAW, true, edge, stop);
        stopped(result, Phase::INTERRUPTED, stop ? Reason::STOP : Reason::EDGE, time);
        CHECK(result.turn_finished == braking);
        CHECK(result.turn_status == (braking ? Status::DONE : Status::ACTIVE));
        if (braking) { CHECK(result.turn_status == Status::DONE); CHECK(result.turn_finished_us == 1000U); }
    }
    for (unsigned path = 0U; path < 3U; ++path) {
        Trial trial; TURN_REQUIRE(trial.start(0U, 0.0F, -180.0F, false));
        const auto time = path == 2U ? 0x80000000U : 1U;
        const auto result = step(trial, time, NAN_YAW, true, path != 0U, path != 1U);
        CHECK(result.turn_status == Status::ACTIVE); CHECK(result.imu_fallback);
        CHECK_FALSE(result.turn_finished); CHECK(result.finished); bounded(result);
        CHECK(result.reason == (path == 2U ? Reason::CLOCK_ORDER : path == 0U ? Reason::STOP : Reason::EDGE));
    }
}

TEST_CASE("B3 B4 B7 P3 D124 duplicate timestamps ignore changed safety and yaw while clearing pulses") {
    for (bool braking : {false, true}) {
        Trial trial; TURN_REQUIRE(trial.start(100U, 0.0F, 90.0F, true));
        std::uint32_t now = 100U;
        if (braking) { brake(step(trial, 101U, 90.0F), Status::DONE, 101U); now = 101U; }
        const auto before = trial.report();
        same(step(trial, now, NAN_YAW, true, true, true), before, false);
        same(step(trial, now, 90.0F, false), before, false);
        const auto stopped_tick = step(trial, now + 1U, NAN_YAW, true, true, true);
        stopped(stopped_tick, Phase::INTERRUPTED, Reason::STOP, now + 1U);
        CHECK(stopped_tick.turn_finished == braking);
    }
}

TEST_CASE("B7 P3 D124 every terminal path permanently retains evidence despite future start or step") {
    for (unsigned terminal = 0U; terminal < 5U; ++terminal) {
        Trial trial;
        if (terminal == 4U) CHECK_FALSE(trial.start(100U, NAN_YAW, 90.0F, true));
        else {
            TURN_REQUIRE(trial.start(100U, 0.0F, 90.0F, true));
            if (terminal == 0U) { step(trial, 101U, 90.0F); step(trial, 500101U, 90.0F); }
            if (terminal == 1U) step(trial, 101U, 0.0F, true, false, true);
            if (terminal == 2U) step(trial, 101U, NAN_YAW, true);
            if (terminal == 3U) step(trial, 99U, 0.0F, true);
        }
        const auto ended = trial.report(); CHECK(ended.finished);
        CHECK_FALSE(trial.start(0U, 0.0F, -180.0F, false)); same(trial.report(), ended, true);
        for (auto time : {0U, 0x80000000U, 0xffffffffU, 123U}) {
            same(step(trial, time, NAN_YAW, true, true, true), ended, false);
            const auto passive = trial.report(); CHECK_FALSE(trial.start(time, 0.0F, 90.0F, true));
            same(trial.report(), passive, true);
        }
    }
}

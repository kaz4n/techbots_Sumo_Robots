// Tests D082 body coordinates and continuous yaw from the frozen public contract.
// Synthetic qualified samples and analytic traces do not establish mounting facts.
// Actual Estimator code is linked as opaque source without a Bus or hardware model.
#include "doctest.h"
#include "hal/imu_heading.h"
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <initializer_list>
#include <limits>
#include <type_traits>

namespace {
using imu::Estimate;
using imu::Estimator;
using imu::HeadingFault;
using imu::HeadingState;
using imu::Presence;
const imu::Mounting IDENTITY{{1, 2, 3}, true};
void must(bool condition) { CHECK(condition); if (!condition) std::abort(); }
imu::Sample sample(std::uint32_t time, std::uint32_t sequence = 1U, std::uint32_t gap = 0U) {
    imu::Sample s{}; s.state = imu::SampleState::OBSERVATION;
    s.bus_status = imu::BusStatus::OK; s.sequence = sequence; s.checked_us = time;
    s.had_previous_observation = sequence != 1U; s.observation_gap_us = gap;
    s.motion.status = imu::DecodeStatus::OK; s.motion.coherent = true;
    s.motion.completed_us = time; s.motion.started_us = time - 50U;
    s.motion.gyro_dps[0] = 10.0F; s.motion.gyro_dps[1] = 20.0F; s.motion.gyro_dps[2] = 30.0F;
    s.motion.accel_g[0] = 1.0F; s.motion.accel_g[1] = 2.0F; s.motion.accel_g[2] = 3.0F;
    return s;
}
imu::Sample absent(std::uint32_t time, std::uint32_t sequence = 0U) {
    imu::Sample s{}; s.state = imu::SampleState::NO_NEW;
    s.bus_status = imu::BusStatus::OK; s.checked_us = time; s.sequence = sequence; return s;
}
void equal(const Estimate& a, const Estimate& b) {
    CHECK(a.state == b.state); CHECK(a.fault == b.fault); CHECK(a.acquisition_fault == b.acquisition_fault);
    CHECK(a.gyro_observation == b.gyro_observation); CHECK(a.accel_observation == b.accel_observation);
    CHECK(a.heading_available == b.heading_available); CHECK(a.heading_updated == b.heading_updated);
    CHECK(a.heading_deg == b.heading_deg); CHECK(a.raw_gyro_z_dps == b.raw_gyro_z_dps);
    CHECK(a.gyro_z_dps == b.gyro_z_dps); CHECK(a.ax_g == b.ax_g); CHECK(a.ay_g == b.ay_g);
    CHECK(a.bias_dps == b.bias_dps); CHECK(a.checked_us == b.checked_us);
    CHECK(a.observation_us == b.observation_us); CHECK(a.sequence == b.sequence);
    CHECK(a.heading_age_us == b.heading_age_us);
}
void cleared(const Estimate& r) {
    CHECK_FALSE(r.heading_available); CHECK_FALSE(r.heading_updated); CHECK(r.heading_deg == 0.0F);
    CHECK(r.raw_gyro_z_dps == 0.0F); CHECK(r.gyro_z_dps == 0.0F); CHECK(r.ax_g == 0.0F);
    CHECK(r.ay_g == 0.0F); CHECK(r.observation_us == 0U); CHECK(r.heading_age_us == 0U);
}
void fault(Estimator& e, const Estimate& r, HeadingFault why, std::uint32_t sequence = 0U,
           std::uint32_t checked = 0U, float bias = 0.0F) {
    CHECK(r.state == HeadingState::FAULT); CHECK(r.fault == why); CHECK(r.sequence == sequence);
    CHECK(r.checked_us == checked); CHECK(r.bias_dps == bias); cleared(r);
    CHECK(r.gyro_observation == Presence::INVALID); CHECK(r.accel_observation == Presence::INVALID);
    CHECK_FALSE(e.begin(IDENTITY, 0.0F)); CHECK_FALSE(e.applyBias(1.0F));
    equal(e.observe(sample(checked + 1000U, sequence + 1U, 1000U)), r);
    equal(e.observe(absent(0xffffffffU, sequence)), r); equal(e.report(), r);
}
unsigned axis(std::int8_t encoded) { return static_cast<unsigned>(std::abs(int(encoded)) - 1); }
float mapped(const float (&values)[3], std::int8_t encoded) {
    return values[axis(encoded)] * (encoded < 0 ? -1.0F : 1.0F);
}
} // namespace

TEST_CASE("B3 D082 default lifecycle does no work and bias cannot configure before begin") {
    Estimator e; const auto original = e.report(); CHECK(original.state == HeadingState::NOT_STARTED);
    CHECK(original.fault == HeadingFault::NONE); CHECK(original.sequence == 0U); cleared(original);
    CHECK_FALSE(std::is_copy_constructible<Estimator>::value);
    CHECK_FALSE(e.applyBias(12.0F)); equal(e.report(), original);
    equal(e.observe(sample(123U)), original); equal(e.observe(absent(0xffffffffU)), original);
    CHECK(e.begin(IDENTITY, 3.0F)); const auto waiting = e.report();
    CHECK(waiting.state == HeadingState::WAITING); CHECK(waiting.bias_dps == 3.0F); cleared(waiting);
    CHECK(e.begin(imu::Mounting{}, std::numeric_limits<float>::quiet_NaN())); equal(e.report(), waiting);
}

TEST_CASE("B3 D082 requires mounting confirmation then a proper map before initial bias") {
    { Estimator e; CHECK_FALSE(e.begin(imu::Mounting{}, std::numeric_limits<float>::quiet_NaN()));
      fault(e, e.report(), HeadingFault::MOUNTING_UNCONFIRMED); }
    const std::int8_t bad[][3] = {{0,2,3},{1,0,3},{1,2,0},{1,1,3},{1,-1,3},{4,2,3},
                                {-4,2,3},{127,2,3},{-128,2,3},{1,2,2}};
    for (const auto& axes : bad) {
        Estimator e; imu::Mounting m{{axes[0], axes[1], axes[2]}, true};
        CHECK_FALSE(e.begin(m, std::numeric_limits<float>::quiet_NaN()));
        fault(e, e.report(), HeadingFault::MOUNTING_INVALID);
    }
}

TEST_CASE("B3 D082 accepts exactly24 proper maps and rejects all24 reflected permutations") {
    unsigned accepted = 0U, rejected = 0U;
    for (int x = 1; x <= 3; ++x) for (int y = 1; y <= 3; ++y) for (int z = 1; z <= 3; ++z) {
        if (x == y || x == z || y == z) continue;
        const int parity = ((x > y) + (x > z) + (y > z)) % 2 ? -1 : 1;
        for (int signs = 0; signs < 8; ++signs) {
            const int sx = signs & 1 ? -1 : 1, sy = signs & 2 ? -1 : 1, sz = signs & 4 ? -1 : 1;
            const imu::Mounting m{{std::int8_t(x*sx), std::int8_t(y*sy), std::int8_t(z*sz)}, true};
            Estimator e; const bool proper = parity * sx * sy * sz == 1;
            CHECK(e.begin(m, 2.5F) == proper);
            if (!proper) { ++rejected; fault(e, e.report(), HeadingFault::MOUNTING_INVALID); continue; }
            ++accepted; const auto s = sample(1000U); const auto r = e.observe(s);
            CHECK(r.state == HeadingState::READY); CHECK(r.raw_gyro_z_dps == mapped(s.motion.gyro_dps, m.body_axis[2]));
            CHECK(r.gyro_z_dps == r.raw_gyro_z_dps - 2.5F);
            CHECK(r.ax_g == mapped(s.motion.accel_g, m.body_axis[0]));
            CHECK(r.ay_g == mapped(s.motion.accel_g, m.body_axis[1]));
            CHECK(r.heading_deg == 0.0F); CHECK(r.sequence == 1U);
        }
    }
    CHECK(accepted == 24U); CHECK(rejected == 24U);
}

TEST_CASE("B3 D082 positive bodyZ is clockwise and continuous yaw passes positive and negative360") {
    for (float rate : {1000.0F, -1000.0F}) {
        Estimator e; must(e.begin(IDENTITY, 0.0F));
        for (std::uint32_t i = 0U; i <= 1000U; ++i) {
            auto s = sample(500U + i * 1000U, i + 1U, i ? 1000U : 0U);
            s.motion.gyro_dps[2] = rate; const auto r = e.observe(s);
            CHECK(r.state == HeadingState::READY); CHECK(r.heading_deg == doctest::Approx(rate * i / 1000.0));
            CHECK(r.heading_available); CHECK(r.heading_updated); CHECK(r.heading_age_us == 0U);
            CHECK(r.observation_us == s.checked_us); CHECK(r.checked_us == s.checked_us);
        }
        CHECK(std::fabs(e.report().heading_deg) == 1000.0F);
    }
}

TEST_CASE("B3 D082 trapezoidal ramp matches analytic area rather than rectangular integration") {
    Estimator e; must(e.begin(IDENTITY, 4.0F));
    for (std::uint32_t i = 0U; i <= 100U; ++i) {
        auto s = sample(10000U + i * 2000U, i + 1U, i ? 2000U : 0U);
        s.motion.gyro_dps[2] = static_cast<float>(10U + 2U * i);
        const double t = i * 0.002; const double area = 6.0 * t + 500.0 * t * t;
        const auto r = e.observe(s); CHECK(r.state == HeadingState::READY);
        CHECK(r.heading_deg == doctest::Approx(area).epsilon(0.000001));
    }
}

TEST_CASE("B3 D082 retains double accumulation when small increments follow a large heading") {
    Estimator e; must(e.begin(IDENTITY, 0.0F)); double area = 0.0; float last = 1000.0F;
    for (std::uint32_t i = 0U; i <= 40000U; ++i) {
        const float rate = i < 30000U ? 1000.0F : 0.01F;
        auto s = sample(i * 2000U, i + 1U, i ? 2000U : 0U); s.motion.gyro_dps[2] = rate;
        if (i) area += (double(last) + rate) * 0.001;
        const auto r = e.observe(s); must(r.state == HeadingState::READY); last = rate;
        if (i % 5000U == 0U) CHECK(r.heading_deg == static_cast<float>(area));
    }
    CHECK(e.report().heading_deg == static_cast<float>(area)); CHECK(std::isfinite(e.report().heading_deg));
}

TEST_CASE("B3 D082 applying bias preserves the whole old report except bias and affects next interval") {
    Estimator e; must(e.begin(IDENTITY, 0.0F)); auto first = sample(1000U);
    first.motion.gyro_dps[2] = 100.0F; auto before = e.observe(first);
    CHECK(e.applyBias(10.0F)); before.bias_dps = 10.0F; equal(e.report(), before);
    auto second = sample(3000U, 2U, 2000U); second.motion.gyro_dps[2] = 200.0F;
    const auto r = e.observe(second); CHECK(r.heading_deg == doctest::Approx(0.28));
    CHECK(r.raw_gyro_z_dps == 200.0F); CHECK(r.gyro_z_dps == 190.0F);
    auto absent_report = e.observe(absent(4000U, 2U));
    CHECK(e.applyBias(-1000.0F)); absent_report.bias_dps = -1000.0F; equal(e.report(), absent_report);
    CHECK(e.applyBias(1000.0F)); absent_report.bias_dps = 1000.0F; equal(e.report(), absent_report);
}

TEST_CASE("B3 D082 invalid initial or active bias faults without replacing the accepted bias") {
    const float invalid[] = {std::numeric_limits<float>::quiet_NaN(),
        std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity(),
        std::nextafter(1000.0F, 2000.0F), std::nextafter(-1000.0F, -2000.0F)};
    for (float bias : invalid) {
        { Estimator e; CHECK_FALSE(e.begin(IDENTITY, bias)); fault(e, e.report(), HeadingFault::BIAS); }
        { Estimator e; must(e.begin(IDENTITY, 5.0F)); e.observe(sample(1000U));
          CHECK_FALSE(e.applyBias(bias)); fault(e, e.report(), HeadingFault::BIAS, 1U, 1000U, 5.0F); }
    }
}

TEST_CASE("B3 D082 NO_NEW publishes no cached sensor values and retains original heading age") {
    Estimator e; must(e.begin(IDENTITY, 1.0F));
    auto waiting = e.observe(absent(900U)); CHECK(waiting.state == HeadingState::WAITING);
    CHECK(waiting.checked_us == 900U); cleared(waiting);
    e.observe(sample(1000U)); const auto previous = e.observe(sample(2000U, 2U, 1000U));
    for (auto gap : {0U, 1999U, 2000U}) {
        auto s = absent(2000U + gap, 2U);
        s.motion.gyro_dps[2] = std::numeric_limits<float>::quiet_NaN(); s.motion.accel_g[0] = 8.0F;
        s.motion.started_us = s.motion.completed_us = 0xffffffffU; s.readiness_completed_us = 99U;
        s.motion_started_us = 88U; s.motion.rail_mask = 255U;
        const auto r = e.observe(s); CHECK(r.state == HeadingState::READY);
        CHECK(r.heading_deg == previous.heading_deg); CHECK(r.observation_us == 2000U);
        CHECK(r.heading_available); CHECK_FALSE(r.heading_updated); CHECK(r.heading_age_us == gap);
        CHECK(r.checked_us == 2000U + gap); CHECK(r.sequence == 2U);
        CHECK(r.gyro_observation == Presence::ABSENT); CHECK(r.accel_observation == Presence::ABSENT);
        CHECK(r.raw_gyro_z_dps == 0.0F); CHECK(r.gyro_z_dps == 0.0F); CHECK(r.ax_g == 0.0F); CHECK(r.ay_g == 0.0F);
    }
    const auto r = e.observe(sample(4000U, 3U, 2000U)); CHECK(r.state == HeadingState::READY);
    CHECK(r.heading_deg == doctest::Approx(0.087));
}

TEST_CASE("B3 D082 NOT_READY ignores timestamps before profile and is input fault afterward") {
    for (bool have_observation : {false, true}) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(0xffffffffU);
        s.state = imu::SampleState::NOT_READY; const auto prior = e.report(); equal(e.observe(s), prior);
        if (have_observation) e.observe(sample(100U)); else e.observe(absent(100U));
        const auto r = e.observe(s); fault(e, r, HeadingFault::INPUT, have_observation ? 1U : 0U, 100U);
    }
}

TEST_CASE("B3 D082 known acquisition faults preserve only their source cause and never trust source time") {
    for (unsigned code = 0U; code <= 8U; ++code) {
        Estimator e; must(e.begin(IDENTITY, 7.0F)); e.observe(sample(100U));
        auto s = sample(2000U); s.state = imu::SampleState::FAULT; s.fault = static_cast<imu::SampleFault>(code);
        const bool known = code >= 1U && code <= static_cast<unsigned>(imu::SampleFault::SILENCE);
        const auto r = e.observe(s); CHECK(r.acquisition_fault == (known ? s.fault : imu::SampleFault::NONE));
        fault(e, r, known ? HeadingFault::SOURCE : HeadingFault::INPUT, 1U, 100U, 7.0F);
    }
    Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(100U);
    s.state = static_cast<imu::SampleState>(255U); fault(e, e.observe(s), HeadingFault::INPUT);
}

TEST_CASE("B3 D082 invalid source envelope rejects before time and source-sequence validation") {
    for (bool new_data : {false, true}) for (unsigned bad = 0U; bad < 4U; ++bad) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(sample(100U));
        auto s = new_data ? sample(200U, 2U, 100U) : absent(200U, 1U);
        if (bad == 0U) s.fault = imu::SampleFault::RESPONSE;
        if (bad == 1U) s.bus_status = imu::BusStatus::NACK;
        if (bad == 2U) s.cleanup = imu::BusCleanup::DISABLED;
        if (bad == 3U) s.error_flags = 1U;
        fault(e, e.observe(s), HeadingFault::INPUT, 1U, 100U);
    }
}

TEST_CASE("B3 D082 first sequence must be one and reconstructing estimator cannot resume sequence2") {
    for (auto sequence : {0U, 2U, 0xffffffffU}) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(100U, sequence);
        s.had_previous_observation = false; s.observation_gap_us = 0U;
        fault(e, e.observe(s), HeadingFault::SEQUENCE, 0U, 100U);
    }
    for (unsigned defect = 0U; defect < 2U; ++defect) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(100U);
        if (defect == 0U) s.had_previous_observation = true; else s.observation_gap_us = 1U;
        fault(e, e.observe(s), HeadingFault::SEQUENCE, 0U, 100U);
    }
}

TEST_CASE("B3 D082 later sequence metadata rejects duplicates skips resets and wrong gaps") {
    for (unsigned defect = 0U; defect < 6U; ++defect) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(sample(100U));
        auto s = sample(200U, 2U, 100U);
        if (defect < 3U) s.sequence = defect == 0U ? 1U : defect == 1U ? 3U : 0U;
        if (defect == 3U) s.had_previous_observation = false;
        if (defect == 4U) s.observation_gap_us = 99U;
        if (defect == 5U) s.observation_gap_us = 101U;
        fault(e, e.observe(s), HeadingFault::SEQUENCE, 1U, 200U);
    }
}

TEST_CASE("B3 D082 NO_NEW validates accepted sequence and only the explicit absence fields") {
    for (unsigned defect = 0U; defect < 4U; ++defect) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(sample(100U));
        auto s = absent(200U, 1U);
        if (defect == 0U) s.sequence = 2U;
        if (defect == 1U) s.motion.coherent = true;
        if (defect == 2U) s.had_previous_observation = true;
        if (defect == 3U) s.observation_gap_us = 1U;
        fault(e, e.observe(s), defect == 0U ? HeadingFault::SEQUENCE : HeadingFault::INPUT, 1U, 200U);
    }
}

TEST_CASE("B3 D082 exact2000us gap accepts while2001 faults no-new and new before sequence checks") {
    for (bool new_data : {false, true}) for (auto gap : {1999U, 2000U, 2001U}) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(sample(100U));
        auto s = new_data ? sample(100U + gap, 2U, gap) : absent(100U + gap, 1U);
        if (gap > 2000U) s.sequence = 999U;
        const auto r = e.observe(s);
        if (gap > 2000U) fault(e, r, HeadingFault::GAP, 1U, 2101U);
        else CHECK(r.state == HeadingState::READY);
    }
}

TEST_CASE("B3 D082 time wraps and rejects backward half-range ambiguity without advancing checked time") {
    { Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(sample(0xffffff00U));
      auto r = e.observe(sample(744U, 2U, 1000U)); CHECK(r.state == HeadingState::READY);
      CHECK(r.checked_us == 744U); CHECK(r.heading_deg == doctest::Approx(0.03)); }
    for (auto delta : {0xffffffffU, 0x80000000U, 0x80000001U}) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(absent(100U));
        fault(e, e.observe(absent(100U + delta)), HeadingFault::TIME_ORDER, 0U, 100U);
    }
    Estimator e; must(e.begin(IDENTITY, 0.0F)); e.observe(sample(100U));
    fault(e, e.observe(sample(100U, 2U, 0U)), HeadingFault::TIME_ORDER, 1U, 100U);
}

TEST_CASE("B3 D082 malformed coherent payload and every unexpected status bit invalidate observation") {
    for (unsigned defect = 0U; defect < 14U; ++defect) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(1000U);
        if (defect == 0U) s.motion.coherent = false;
        if (defect == 1U) s.motion.status = imu::DecodeStatus::RESPONSE;
        if (defect == 2U) s.motion.completed_us = 1001U;
        if (defect == 3U) s.motion.started_us = 400U;
        if (defect == 4U) s.motion.started_us = 1001U;
        if (defect == 5U) s.motion.started_us = 1000U - 0x80000000U;
        if (defect == 6U) s.motion.rail_mask = 0x80U;
        if (defect >= 7U) s.motion.interrupt_status = std::uint8_t(1U << (defect - 6U));
        fault(e, e.observe(s), HeadingFault::INPUT, 0U, 1000U);
    }
    for (auto duration : {0U, 599U}) for (auto status : {0U, 1U}) {
        Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(1000U);
        s.motion.started_us = 1000U - duration; s.motion.interrupt_status = status;
        CHECK(e.observe(s).state == HeadingState::READY);
    }
}

TEST_CASE("B3 D082 all scaled components require finite inclusive range even on unused axes") {
    for (bool gyro : {false, true}) for (unsigned component = 0U; component < 3U; ++component) {
        const float limit = gyro ? 1000.0F : 8.0F;
        const float invalid[] = {std::numeric_limits<float>::quiet_NaN(),
            std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity(),
            std::nextafter(limit, 2.0F * limit), std::nextafter(-limit, -2.0F * limit)};
        for (float value : invalid) {
            Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(100U);
            (gyro ? s.motion.gyro_dps : s.motion.accel_g)[component] = value;
            fault(e, e.observe(s), HeadingFault::INPUT, 0U, 100U);
        }
        for (float value : {-limit, limit}) {
            Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(100U);
            (gyro ? s.motion.gyro_dps : s.motion.accel_g)[component] = value;
            CHECK(e.observe(s).state == HeadingState::READY);
        }
    }
}

TEST_CASE("B3 D082 rail handling follows selected axes and horizontal saturation preserves yaw") {
    const imu::Mounting maps[] = {{{1,2,3},true},{{2,3,1},true},{{3,1,2},true},{{-2,-1,-3},true}};
    for (const auto& m : maps) for (unsigned bit = 0U; bit < 7U; ++bit) {
        Estimator e; must(e.begin(m, 0.0F)); e.observe(sample(100U));
        auto s = sample(1100U, 2U, 1000U); s.motion.rail_mask = std::uint8_t(1U << bit);
        const auto r = e.observe(s);
        if (bit == axis(m.body_axis[2]) + 4U) {
            fault(e, r, HeadingFault::SATURATION, 1U, 1100U); continue;
        }
        CHECK(r.state == HeadingState::READY); CHECK(r.gyro_observation == Presence::VALID);
        CHECK(r.heading_available); CHECK(r.heading_updated);
        CHECK(r.heading_deg == doctest::Approx(mapped(s.motion.gyro_dps, m.body_axis[2]) * 0.001));
        const bool horizontal = bit == axis(m.body_axis[0]) || bit == axis(m.body_axis[1]);
        CHECK(r.accel_observation == (horizontal ? Presence::INVALID : Presence::VALID));
        CHECK(r.ax_g == (horizontal ? 0.0F : mapped(s.motion.accel_g, m.body_axis[0])));
        CHECK(r.ay_g == (horizontal ? 0.0F : mapped(s.motion.accel_g, m.body_axis[1])));
    }
}

TEST_CASE("B3 D082 raw arrays and native phase timestamps are not reinterpreted by numerical consumer") {
    Estimator e; must(e.begin(IDENTITY, 0.0F)); auto s = sample(123U);
    for (auto& raw : s.motion.gyro_raw) raw = std::numeric_limits<std::int32_t>::max();
    for (auto& raw : s.motion.accel_raw) raw = std::numeric_limits<std::int32_t>::min();
    s.motion.temperature_raw = std::numeric_limits<std::int32_t>::min();
    s.motion_started_us = 0xffffffffU; s.readiness_completed_us = 0xffffffffU;
    const auto r = e.observe(s); CHECK(r.state == HeadingState::READY);
    CHECK(r.raw_gyro_z_dps == 30.0F); CHECK(r.ax_g == 1.0F); CHECK(r.ay_g == 2.0F);
}

TEST_CASE("B3 D082 repeated begin cannot reset yaw change mapping or swap bias") {
    Estimator e; must(e.begin(IDENTITY, 2.0F)); e.observe(sample(100U));
    const auto before = e.observe(sample(1100U, 2U, 1000U));
    CHECK(e.begin(imu::Mounting{{3,2,-1},true}, 40.0F)); equal(e.report(), before);
    CHECK(e.begin(imu::Mounting{}, std::numeric_limits<float>::infinity())); equal(e.report(), before);
    const auto after = e.observe(sample(2100U, 3U, 1000U));
    CHECK(after.heading_deg == doctest::Approx(0.056)); CHECK(after.raw_gyro_z_dps == 30.0F);
    CHECK(after.bias_dps == 2.0F);
}

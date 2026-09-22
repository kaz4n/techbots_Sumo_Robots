// Checks B0/B3/B14 match-heading ownership and provenance under D-059.
// Separates continuous raw Fusion evidence from logical match coordinates and projections.
// Independent tests cover numeric boundaries, reset-only faults and unchanged motion timing.
#include "doctest.h"
#include "core/countdown.h"
#include "core/fsm.h"
#include "core/opp_fusion.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
using Origin = fsm::HeadingOrigin;
constexpr float NAN_YAW = std::numeric_limits<float>::quiet_NaN();
constexpr float INF_YAW = std::numeric_limits<float>::infinity();
constexpr float MAX_YAW = std::numeric_limits<float>::max();

void invalid(const fsm::HeadingProjection& result) {
    CHECK_FALSE(result.valid);
    CHECK(result.heading_deg == 0.0F);
    CHECK(std::isfinite(result.heading_deg));
}

void projection(const fsm::HeadingProjection& result, float expected) {
    CHECK(result.valid);
    CHECK(result.heading_deg == doctest::Approx(expected));
    CHECK(std::isfinite(result.heading_deg));
}

void current(const fsm::HeadingResult& result, float heading, Origin origin,
             std::uint32_t source_time, bool imu = true, bool changed = false) {
    CHECK(result.heading_deg == heading);
    CHECK(result.match_started);
    CHECK(result.imu_ok == imu);
    CHECK_FALSE(result.fault);
    CHECK(result.origin == origin);
    CHECK(result.origin_t_us == source_time);
    CHECK(result.origin_changed == changed);
    CHECK(std::isfinite(result.heading_deg));
}

void preGo(const fsm::HeadingResult& result) {
    CHECK(result.heading_deg == 0.0F);
    CHECK_FALSE(result.match_started);
    CHECK_FALSE(result.imu_ok);
    CHECK_FALSE(result.fault);
    CHECK_FALSE(result.origin_changed);
    CHECK(result.origin == Origin::NONE);
    CHECK(result.origin_t_us == 0U);
}

void faulted(fsm::HeadingReference& reference, const fsm::HeadingResult& result,
             float retained_heading) {
    CHECK(result.fault);
    CHECK_FALSE(result.imu_ok);
    CHECK_FALSE(result.origin_changed);
    CHECK(result.heading_deg == retained_heading);
    CHECK(std::isfinite(result.heading_deg));
    invalid(reference.worldBearing(15.0F));
    invalid(reference.projectWorld(15.0F));
    invalid(reference.projectHeading(15.0F));
}

void same(const fsm::HeadingResult& a, const fsm::HeadingResult& b) {
    CHECK(a.heading_deg == b.heading_deg);
    CHECK(a.imu_ok == b.imu_ok);
    CHECK(a.match_started == b.match_started);
    CHECK(a.origin_changed == b.origin_changed);
    CHECK(a.fault == b.fault);
    CHECK(a.origin == b.origin);
    CHECK(a.origin_t_us == b.origin_t_us);
}

opp_fusion::FusionObservation fusionTick(opp_fusion::Fusion& fusion, std::uint32_t time,
        float raw_heading, std::uint8_t logical = 2U, bool edge = false,
        core::State prior = core::State::COUNTDOWN) {
    opp_fusion::FusionSample sample;
    sample.t_us = time;
    sample.raw_mask = static_cast<std::uint8_t>(logical ^ 0x78U);
    sample.heading_deg = raw_heading;
    sample.imu_ok = true;
    sample.edge_event = edge;
    sample.prior_state = prior;
    const auto result = fusion.observe(sample);
    CHECK(result.fresh);
    CHECK(fusion.commit(prior).valid);
    return result;
}

void activeTurn(const motion::Result& result, bool fallback) {
    CHECK(result.status == motion::Status::ACTIVE);
    CHECK(result.duty_l == doctest::Approx(0.8F));
    CHECK(result.duty_r == doctest::Approx(-0.8F));
    CHECK(result.imu_fallback == fallback);
}
} // namespace

TEST_CASE("B0 D059 default and pre-GO history expose no measured match heading or projection") {
    const fsm::HeadingResult initial;
    preGo(initial);
    fsm::HeadingReference reference;
    invalid(reference.worldBearing(15.0F));
    invalid(reference.projectWorld(15.0F));
    invalid(reference.projectHeading(725.0F));
    preGo(reference.step(0U, 720.0F, true));
    preGo(reference.step(100U, 730.0F, true));
    preGo(reference.step(200U, NAN_YAW, false));
    invalid(reference.worldBearing(15.0F));
    invalid(reference.projectWorld(15.0F));
}

TEST_CASE("B3 D059 GO captures the current healthy sample and keeps continuous signed motion") {
    fsm::HeadingReference reference;
    preGo(reference.step(100U, 1000.0F, true));
    current(reference.step(200U, 1010.0F, true, true), 0.0F, Origin::CURRENT_GO, 200U, true, true);
    current(reference.step(201U, 1012.0F, true), 2.0F, Origin::CURRENT_GO, 200U);
    current(reference.step(202U, 1000.0F, true), -10.0F, Origin::CURRENT_GO, 200U);
    current(reference.step(203U, 1370.0F, true), 360.0F, Origin::CURRENT_GO, 200U);
    current(reference.step(204U, 2090.0F, true), 1080.0F, Origin::CURRENT_GO, 200U);
    projection(reference.projectHeading(1005.0F), -5.0F);
}

TEST_CASE("B3 B14 D059 unavailable GO uses the last genuine healthy source and does not re-zero recovery") {
    fsm::HeadingReference reference;
    preGo(reference.step(10U, 400.0F, true));
    preGo(reference.step(20U, 999.0F, false));
    current(reference.step(30U, NAN_YAW, false, true), 0.0F, Origin::LAST_KNOWN, 10U, false, true);
    invalid(reference.worldBearing(15.0F));
    projection(reference.projectWorld(55.0F), 15.0F);
    current(reference.step(40U, 450.0F, true), 50.0F, Origin::LAST_KNOWN, 10U);
    current(reference.step(50U, -999.0F, false), 50.0F, Origin::LAST_KNOWN, 10U, false);
    current(reference.step(60U, 460.0F, true), 60.0F, Origin::LAST_KNOWN, 10U);
}

TEST_CASE("B14 D059 missing-at-boot GO uses pending zero and only first healthy recovery resolves it") {
    fsm::HeadingReference reference;
    preGo(reference.step(0U, MAX_YAW, false));
    current(reference.step(100U, NAN_YAW, false, true), 0.0F, Origin::NOMINAL_PENDING, 100U, false, true);
    invalid(reference.worldBearing(15.0F));
    invalid(reference.projectWorld(15.0F));
    invalid(reference.projectHeading(0.0F));
    current(reference.step(200U, 900.0F, false), 0.0F, Origin::NOMINAL_PENDING, 100U, false);
    current(reference.step(300U, 725.0F, true), 0.0F, Origin::FIRST_RECOVERY, 300U, true, true);
    current(reference.step(301U, 730.0F, true), 5.0F, Origin::FIRST_RECOVERY, 300U);
    current(reference.step(302U, INF_YAW, false), 5.0F, Origin::FIRST_RECOVERY, 300U, false);
    current(reference.step(303U, 735.0F, true), 10.0F, Origin::FIRST_RECOVERY, 300U);
}

TEST_CASE("B14 D059 unavailable arbitrary payload never updates history or faults") {
    for (const auto payload : {NAN_YAW, INF_YAW, -INF_YAW, MAX_YAW, -MAX_YAW, 12345.0F}) {
        fsm::HeadingReference reference;
        preGo(reference.step(0U, 20.0F, true));
        preGo(reference.step(1U, payload, false));
        current(reference.step(2U, payload, false, true), 0.0F, Origin::LAST_KNOWN, 0U, false, true);
        current(reference.step(3U, 25.0F, true), 5.0F, Origin::LAST_KNOWN, 0U);
        current(reference.step(4U, payload, false), 5.0F, Origin::LAST_KNOWN, 0U, false);
        invalid(reference.worldBearing(0.0F));
        projection(reference.projectHeading(30.0F), 10.0F);
    }
}

TEST_CASE("B0 B14 D059 healthy NaN and infinities latch before GO without inventing an origin") {
    for (const auto bad : {NAN_YAW, INF_YAW, -INF_YAW}) {
        fsm::HeadingReference reference;
        faulted(reference, reference.step(0U, bad, true), 0.0F);
        faulted(reference, reference.step(1U, 720.0F, true, true), 0.0F);
        faulted(reference, reference.step(2U, 0.0F, false), 0.0F);
    }
}

TEST_CASE("B14 D059 healthy malformed yaw after GO preserves the finite coordinate until reset") {
    for (const auto bad : {NAN_YAW, INF_YAW, -INF_YAW}) {
        for (const bool initially_missing : {false, true}) {
            fsm::HeadingReference reference;
            reference.step(0U, 100.0F, !initially_missing, true);
            const float retained = initially_missing ? 0.0F : 5.0F;
            if (!initially_missing) reference.step(1U, 105.0F, true);
            faulted(reference, reference.step(2U, bad, true), retained);
            faulted(reference, reference.step(3U, 110.0F, true), retained);
            faulted(reference, reference.step(4U, bad, false), retained);
            reference.reset();
            current(reference.step(4U, 110.0F, true, true), 0.0F, Origin::CURRENT_GO, 4U, true, true);
        }
    }
}

TEST_CASE("B0 D059 maximum representable difference succeeds and its adjacent larger difference faults") {
    for (const auto sign : {-1.0F, 1.0F}) {
        fsm::HeadingReference reference;
        const float half = MAX_YAW / 2.0F;
        reference.step(0U, -sign * half, true, true);
        const auto exact = reference.step(1U, sign * half, true);
        current(exact, sign * MAX_YAW, Origin::CURRENT_GO, 0U);
        const float outside = sign * std::nextafter(half, MAX_YAW);
        CHECK(std::fabs(static_cast<double>(outside) + static_cast<double>(sign * half)) >
              static_cast<double>(MAX_YAW));
        faulted(reference, reference.step(2U, outside, true), sign * MAX_YAW);
        faulted(reference, reference.step(3U, 0.0F, true), sign * MAX_YAW);
    }
}

TEST_CASE("B0 D059 equal huge finite GO samples give exact zero without intermediate overflow") {
    for (const auto raw : {MAX_YAW, -MAX_YAW, 1.0e30F, -1.0e30F}) {
        fsm::HeadingReference reference;
        current(reference.step(0U, raw, true, true), 0.0F, Origin::CURRENT_GO, 0U, true, true);
        current(reference.step(1U, raw, true), 0.0F, Origin::CURRENT_GO, 0U);
        projection(reference.worldBearing(15.0F), 15.0F);
        projection(reference.worldBearing(-15.0F), -15.0F);
        projection(reference.projectHeading(raw), 0.0F);
    }
}

TEST_CASE("B3 D059 second distinct GO faults while an immediate duplicate ignores changed GO data") {
    for (const bool healthy : {false, true}) {
        fsm::HeadingReference reference;
        current(reference.step(10U, 50.0F, true, true), 0.0F, Origin::CURRENT_GO, 10U, true, true);
        current(reference.step(10U, NAN_YAW, false, true), 0.0F, Origin::CURRENT_GO, 10U);
        current(reference.step(11U, 55.0F, true), 5.0F, Origin::CURRENT_GO, 10U);
        faulted(reference, reference.step(12U, 100.0F, healthy, true), 5.0F);
        faulted(reference, reference.step(13U, 100.0F, false), 5.0F);
    }
}

TEST_CASE("B3 D059 duplicate pre-GO and first-recovery observations cannot replace source history") {
    fsm::HeadingReference reference;
    preGo(reference.step(0U, 100.0F, true));
    preGo(reference.step(0U, NAN_YAW, true, true));
    current(reference.step(1U, 999.0F, false, true), 0.0F, Origin::LAST_KNOWN, 0U, false, true);
    reference.reset();
    reference.step(0U, NAN_YAW, false, true);
    current(reference.step(1U, 720.0F, true), 0.0F, Origin::FIRST_RECOVERY, 1U, true, true);
    current(reference.step(1U, 1080.0F, true, true), 0.0F, Origin::FIRST_RECOVERY, 1U);
    current(reference.step(2U, 730.0F, true), 10.0F, Origin::FIRST_RECOVERY, 1U);
}

TEST_CASE("B0 B3 D059 reset clears origin provenance raw history fault and duplicate identity") {
    fsm::HeadingReference reference;
    reference.step(1U, 100.0F, true);
    reference.step(2U, NAN_YAW, false, true);
    reference.step(3U, NAN_YAW, true);
    reference.reset();
    invalid(reference.projectWorld(15.0F));
    invalid(reference.projectHeading(100.0F));
    current(reference.step(3U, 100.0F, false, true), 0.0F, Origin::NOMINAL_PENDING, 3U, false, true);
    current(reference.step(4U, 1000.0F, true), 0.0F, Origin::FIRST_RECOVERY, 4U, true, true);
}

TEST_CASE("B0 D059 source timestamps and fixed origin survive repeated micros wraps") {
    fsm::HeadingReference reference;
    const std::uint32_t source = 0xfffffff0U;
    preGo(reference.step(source, 720.0F, true));
    current(reference.step(5U, NAN_YAW, false, true), 0.0F, Origin::LAST_KNOWN, source, false, true);
    std::uint64_t time = 5U;
    for (unsigned cycle = 0U; cycle < 5U; ++cycle) {
        time += 0xffffffffULL;
        current(reference.step(static_cast<std::uint32_t>(time), 730.0F, true),
                10.0F, Origin::LAST_KNOWN, source);
    }
}

TEST_CASE("B0 D059 worldBearing preserves literal directional ties and unwrapped local yaw") {
    struct Case { float yaw; float relative; float expected; };
    for (const auto test : {Case{179.0F, 1.0F, 180.0F}, Case{-179.0F, -1.0F, 180.0F},
        Case{181.0F, -1.0F, 180.0F}, Case{-181.0F, 1.0F, 180.0F},
        Case{179.0F, 15.0F, -166.0F}, Case{-179.0F, -15.0F, 166.0F},
        Case{720.0F, 15.0F, 15.0F}}) {
        fsm::HeadingReference reference;
        reference.step(0U, 0.0F, true, true);
        current(reference.step(1U, test.yaw, true), test.yaw, Origin::CURRENT_GO, 0U);
        projection(reference.worldBearing(test.relative), test.expected);
    }
}

TEST_CASE("B0 D059 retained raw world projections subtract the origin without wrapping continuous evidence") {
    struct Case { float origin; float world; float expected; };
    for (const auto test : {Case{90.0F, -90.0F, 180.0F}, Case{-90.0F, 90.0F, 180.0F},
        Case{180.0F, 0.0F, 180.0F}, Case{720.0F, -90.0F, -90.0F},
        Case{1010.0F, -65.0F, 5.0F}, Case{725.0F, 15.0F, 10.0F}}) {
        fsm::HeadingReference reference;
        reference.step(0U, test.origin, true, true);
        projection(reference.projectWorld(test.world), test.expected);
        projection(reference.projectHeading(test.origin + 360.0F), 360.0F);
    }
}

TEST_CASE("B0 D059 directional inputs reject noncanonical values without faulting the coordinate") {
    fsm::HeadingReference reference;
    reference.step(0U, 0.0F, true, true);
    for (const auto bad : {-180.0F, -181.0F, 181.0F, std::nextafter(180.0F, INF_YAW),
                           NAN_YAW, INF_YAW, -INF_YAW, MAX_YAW}) {
        invalid(reference.worldBearing(bad));
        invalid(reference.projectWorld(bad));
    }
    projection(reference.worldBearing(180.0F), 180.0F);
    projection(reference.projectWorld(std::nextafter(-180.0F, 0.0F)), std::nextafter(-180.0F, 0.0F));
    current(reference.step(1U, 0.0F, true), 0.0F, Origin::CURRENT_GO, 0U);
}

TEST_CASE("B0 D059 small bearings survive reduction of large exact full-turn multiples") {
    const float huge = std::ldexp(360.0F, 80);
    for (const auto sign : {-1.0F, 1.0F}) {
        fsm::HeadingReference reference;
        reference.step(0U, 0.0F, true, true);
        reference.step(1U, sign * huge, true);
        for (const auto angle : {-15.0F, -1.0e-6F, 1.0e-6F, 15.0F}) {
            const auto result = reference.worldBearing(angle);
            CHECK(result.valid);
            CHECK(result.heading_deg == angle);
        }
        reference.reset();
        reference.step(0U, sign * huge, true, true);
        projection(reference.projectWorld(15.0F), 15.0F);
    }
}

TEST_CASE("B0 D059 current world direction uses checked double difference before public float rounding") {
    fsm::HeadingReference reference;
    reference.step(0U, -1.0F, true, true);
    current(reference.step(1U, 16777216.0F, true), 16777216.0F, Origin::CURRENT_GO, 0U);
    projection(reference.worldBearing(15.0F), 152.0F);
    projection(reference.projectWorld(136.0F), 137.0F);
    projection(reference.projectHeading(16777216.0F), 16777216.0F);
}

TEST_CASE("B0 D059 near negative antipode retains LEFT side when float rounding reaches excluded minus180") {
    fsm::HeadingReference reference;
    reference.step(0U, -1.0e-6F, true, true);
    reference.step(1U, 0.0F, true);
    const auto current_world = reference.worldBearing(180.0F);
    const auto retained_world = reference.projectWorld(180.0F);
    CHECK(current_world.valid);
    CHECK(retained_world.valid);
    CHECK(current_world.heading_deg == std::nextafter(-180.0F, 0.0F));
    CHECK(retained_world.heading_deg == std::nextafter(-180.0F, 0.0F));
    reference.reset();
    reference.step(0U, 0.0F, true, true);
    projection(reference.worldBearing(180.0F), 180.0F);
    reference.step(1U, 180.0F, true);
    projection(reference.worldBearing(0.0F), 180.0F);
}

TEST_CASE("B0 B14 D059 unavailable current yaw inhibits only current world measurement") {
    fsm::HeadingReference reference;
    reference.step(0U, 1010.0F, true, true);
    reference.step(1U, 1015.0F, true);
    current(reference.step(2U, NAN_YAW, false), 5.0F, Origin::CURRENT_GO, 0U, false);
    invalid(reference.worldBearing(15.0F));
    projection(reference.projectWorld(-65.0F), 5.0F);
    projection(reference.projectHeading(1005.0F), -5.0F);
    current(reference.step(3U, 1020.0F, true), 10.0F, Origin::CURRENT_GO, 0U);
    projection(reference.worldBearing(15.0F), 25.0F);
}

TEST_CASE("B0 D059 read-only invalid projections cannot latch faults or replace sample freshness") {
    fsm::HeadingReference queried;
    fsm::HeadingReference control;
    same(queried.step(0U, MAX_YAW / 2.0F, true, true), control.step(0U, MAX_YAW / 2.0F, true, true));
    const fsm::HeadingReference& view = queried;
    for (unsigned read = 0U; read < 4U; ++read) {
        invalid(view.worldBearing(NAN_YAW));
        invalid(view.projectWorld(-180.0F));
        invalid(view.projectHeading(-MAX_YAW));
        invalid(view.projectHeading(INF_YAW));
        projection(view.projectHeading(MAX_YAW / 2.0F), 0.0F);
    }
    same(queried.step(0U, NAN_YAW, true, true), control.step(0U, NAN_YAW, true, true));
    same(queried.step(1U, MAX_YAW / 2.0F, true), control.step(1U, MAX_YAW / 2.0F, true));
}

TEST_CASE("B3 D059 actual Gate cancellation or STOP produces no heading epoch at the GO deadline") {
    for (const bool stop : {false, true}) {
        countdown::Gate gate;
        fsm::HeadingReference reference;
        CHECK(gate.step(0U, {true, false, false}).start_release);
        preGo(reference.step(0U, 720.0F, true));
        const auto canceled = gate.step(5100000U, {false, !stop, stop});
        CHECK_FALSE(canceled.go);
        CHECK_FALSE(canceled.motion_permitted);
        preGo(reference.step(5100000U, 725.0F, true, canceled.go));
    }
}

TEST_CASE("B3 B5 D059 raw Fusion yaw stays constant across GO without fabricating stuck span") {
    fsm::HeadingReference reference;
    opp_fusion::Fusion fusion;
    for (const auto time : {0U, 1000U, 5000999U, 5001000U, 6001000U}) {
        const auto heading = reference.step(time, 720.0F, true, time == 5001000U);
        const auto observation = fusionTick(fusion, time, 720.0F);
        CHECK(observation.stuck.fault_mask == 0U);
        CHECK(observation.stuck.new_fault_mask == 0U);
        CHECK(observation.confirmed_mask == (time == 0U ? 0U : 2U));
        CHECK(heading.heading_deg == 0.0F);
        CHECK(heading.match_started == (time >= 5001000U));
    }
}

TEST_CASE("B3 B5 D059 live raw candidate survives GO and retains strict 360 degree stuck threshold") {
    fsm::HeadingReference reference;
    opp_fusion::Fusion fusion;
    reference.step(0U, 0.0F, true);
    fusionTick(fusion, 0U, 0.0F);
    reference.step(1000U, 0.0F, true);
    fusionTick(fusion, 1000U, 0.0F);
    reference.step(2501000U, 180.0F, true, true);
    CHECK(fusionTick(fusion, 2501000U, 180.0F).stuck.fault_mask == 0U);
    CHECK(fusionTick(fusion, 5000999U, 360.0F).stuck.fault_mask == 0U);
    CHECK(fusionTick(fusion, 5001000U, 360.0F).stuck.fault_mask == 0U);
    const float beyond = std::nextafter(360.0F, INF_YAW);
    const auto local = reference.step(5001001U, beyond, true);
    CHECK(local.heading_deg > 180.0F);
    const auto fault = fusionTick(fusion, 5001001U, beyond);
    CHECK(fault.stuck.fault_mask == 2U);
    CHECK(fault.stuck.new_fault_mask == 2U);
    CHECK(fault.phantom.filtered_mask == 0U);
}

TEST_CASE("B3 B5 D059 existing reset-only Fusion faults survive GO and input clearing") {
    fsm::HeadingReference reference;
    opp_fusion::Fusion fusion;
    fusionTick(fusion, 0U, 0.0F);
    fusionTick(fusion, 1000U, 0.0F);
    CHECK(fusionTick(fusion, 5001000U, 361.0F).stuck.new_fault_mask == 2U);
    current(reference.step(5001001U, 361.0F, true, true), 0.0F, Origin::CURRENT_GO, 5001001U, true, true);
    auto observation = fusionTick(fusion, 5001001U, 361.0F);
    CHECK(observation.stuck.fault_mask == 2U);
    CHECK(observation.stuck.new_fault_mask == 0U);
    fusionTick(fusion, 5001002U, 361.0F, 0U);
    observation = fusionTick(fusion, 5031002U, 361.0F, 0U);
    CHECK(observation.confirmed_mask == 0U);
    CHECK(observation.stuck.fault_mask == 2U);
    reference.reset();
    CHECK(fusionTick(fusion, 5031003U, 361.0F, 0U).stuck.fault_mask == 2U);
    fusion.reset();
    CHECK(fusionTick(fusion, 5031004U, 361.0F, 0U).stuck.fault_mask == 0U);
}

TEST_CASE("B3 B5 D059 phantom marker stays raw and its age is not refreshed by GO projection") {
    fsm::HeadingReference reference;
    opp_fusion::Fusion fusion;
    fusionTick(fusion, 0U, 1000.0F, 2U, false, core::State::TRACK);
    fusionTick(fusion, 1000U, 1000.0F, 2U, false, core::State::TRACK);
    const auto marked = fusionTick(fusion, 2000U, 1000.0F, 2U, true, core::State::TRACK);
    CHECK(marked.phantom.phantom_set);
    CHECK(marked.phantom.world_deg == -80.0F);
    reference.step(3000U, 1000.0F, true, true);
    const auto after = fusionTick(fusion, 3000U, 1000.0F, 2U, false, core::State::EDGE_ESCAPE);
    CHECK(after.phantom.active);
    CHECK_FALSE(after.phantom.phantom_set);
    CHECK(after.phantom.filtered_mask == 0U);
    CHECK(after.phantom.world_deg == -80.0F);
    projection(reference.projectWorld(after.phantom.world_deg), 0.0F);
    CHECK(fusionTick(fusion, 3001999U, 1000.0F, 2U).phantom.active);
    CHECK_FALSE(fusionTick(fusion, 3002000U, 1000.0F, 2U).phantom.active);
}

TEST_CASE("B3 B5 B8 D059 retained world projection preserves evidence timestamp and cannot renew expired memory") {
    opp_fusion::Fusion fusion;
    fusionTick(fusion, 0U, 1000.0F, 4U);
    fusionTick(fusion, 1000U, 1000.0F, 4U);
    const auto evidence = fusion.memory();
    CHECK(evidence.world_valid);
    CHECK(evidence.last_world_bearing_deg == -65.0F);
    fsm::HeadingReference reference;
    reference.step(2000U, 1010.0F, true, true);
    const auto world = reference.projectWorld(evidence.last_world_bearing_deg);
    projection(world, 5.0F);
    CHECK(fusion.memory().last_seen_us == 1000U);
    CHECK(fusion.memory().last_world_bearing_deg == -65.0F);
    const auto now = reference.step(4000000U, 1010.0F, true);
    for (const std::uint64_t age : {std::uint64_t{2999999U}, std::uint64_t{3000000U}}) {
        fsm::Search search;
        fsm::SearchContext context;
        context.world_valid = evidence.world_valid && world.valid;
        context.world_bearing_deg = world.heading_deg;
        context.world_age_us = age;
        CHECK(search.start(4000000U, now.heading_deg, now.imu_ok, context));
        const auto result = search.step(4000000U, now.heading_deg, now.imu_ok, 0U);
        CHECK(result.phase == (age < 3000000U ? fsm::SearchPhase::MEMORY_TURN : fsm::SearchPhase::SCAN));
    }
}

TEST_CASE("B3 B7 B14 D059 nominal recovery cannot restart or shorten an already timed turn") {
    fsm::HeadingReference reference;
    auto h = reference.step(0U, NAN_YAW, false, true);
    motion::Turn turn;
    CHECK(turn.startRelative(0U, h.heading_deg, 90.0F, 0.8F, h.imu_ok));
    activeTurn(turn.step(0U, h.heading_deg, h.imu_ok), true);
    h = reference.step(90000U, 1000.0F, true);
    current(h, 0.0F, Origin::FIRST_RECOVERY, 90000U, true, true);
    activeTurn(turn.step(90000U, h.heading_deg, h.imu_ok), true);
    h = reference.step(179999U, 1090.0F, true);
    activeTurn(turn.step(179999U, h.heading_deg, h.imu_ok), true);
    h = reference.step(180000U, 1090.0F, true);
    const auto done = turn.step(180000U, h.heading_deg, h.imu_ok);
    CHECK(done.status == motion::Status::DONE);
    CHECK(done.duty_l == 0.0F);
    CHECK(done.duty_r == 0.0F);
}

TEST_CASE("B3 B8 B14 D059 missing-at-boot Search keeps original 720ms scan fallback across recovery") {
    fsm::HeadingReference reference;
    auto h = reference.step(0U, NAN_YAW, false, true);
    fsm::Search search;
    CHECK(search.start(0U, h.heading_deg, h.imu_ok, {}));
    h = reference.step(100000U, 1000.0F, true);
    CHECK(h.heading_deg == 0.0F);
    auto scan = search.step(100000U, h.heading_deg, h.imu_ok, 0U);
    CHECK(scan.phase == fsm::SearchPhase::SCAN);
    CHECK(scan.motion.imu_fallback);
    h = reference.step(719999U, 1360.0F, true);
    scan = search.step(719999U, h.heading_deg, h.imu_ok, 0U);
    CHECK(scan.phase == fsm::SearchPhase::SCAN);
    CHECK(scan.motion.imu_fallback);
    h = reference.step(720000U, 1360.0F, true);
    const auto advance = search.step(720000U, h.heading_deg, h.imu_ok, 0U);
    CHECK(advance.phase == fsm::SearchPhase::ADVANCE);
    CHECK(advance.motion.duty_l == doctest::Approx(0.3F));
    CHECK(advance.motion.duty_r == doctest::Approx(0.3F));
    CHECK_FALSE(advance.turn_timed_out);
}

TEST_CASE("B3 B7 B14 D059 Straight keeps nominal reference and original duration after first recovery") {
    fsm::HeadingReference reference;
    auto h = reference.step(0U, NAN_YAW, false, true);
    motion::Straight straight;
    CHECK(straight.start(0U, h.heading_deg, 0.5F, 250U));
    h = reference.step(100000U, 725.0F, true);
    auto request = straight.step(100000U, h.heading_deg, h.imu_ok);
    CHECK(request.duty_l == doctest::Approx(0.5F));
    CHECK(request.duty_r == doctest::Approx(0.5F));
    h = reference.step(150000U, 730.0F, true);
    request = straight.step(150000U, h.heading_deg, h.imu_ok);
    CHECK(request.duty_l == doctest::Approx(0.4F));
    CHECK(request.duty_r == doctest::Approx(0.6F));
    h = reference.step(249999U, NAN_YAW, false);
    CHECK(straight.step(249999U, h.heading_deg, h.imu_ok).status == motion::Status::ACTIVE);
    h = reference.step(250000U, 735.0F, true);
    CHECK(straight.step(250000U, h.heading_deg, h.imu_ok).status == motion::Status::DONE);
}

TEST_CASE("B3 B7 B14 D059 Arc recovery credits no unobserved rotation and preserves timeout precedence") {
    for (const auto end : {399999U, 400000U}) {
        fsm::HeadingReference reference;
        auto h = reference.step(0U, NAN_YAW, false, true);
        motion::Arc arc;
        CHECK(arc.start(0U, h.heading_deg, motion::Direction::RIGHT, 0.4F, 0.7F, 90.0F, 400U));
        h = reference.step(200000U, 9999.0F, false);
        CHECK(arc.step(200000U, h.heading_deg, h.imu_ok).imu_fallback);
        h = reference.step(300000U, 500.0F, true);
        CHECK(h.heading_deg == 0.0F);
        CHECK(arc.step(300000U, h.heading_deg, h.imu_ok).status == motion::Status::ACTIVE);
        h = reference.step(350000U, 589.0F, true);
        CHECK(arc.step(350000U, h.heading_deg, h.imu_ok).status == motion::Status::ACTIVE);
        h = reference.step(end, 590.0F, true);
        const auto result = arc.step(end, h.heading_deg, h.imu_ok);
        CHECK(result.status == (end == 400000U ? motion::Status::TIMED_OUT : motion::Status::DONE));
        CHECK(result.duty_l == 0.0F);
        CHECK(result.duty_r == 0.0F);
    }
}

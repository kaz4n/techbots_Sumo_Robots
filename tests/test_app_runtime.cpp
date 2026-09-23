// Tests native application scheduling from the D096 frozen public contract.
// Uses actual Runtime/Transaction/Robot/Gate/InputOwner/Estimator/Calibration.
// Typed fake sources exercise both motor builds without physical hardware claims.
#include "doctest.h"
#include "fixtures/app_runtime_fixture.h"
#include <algorithm>

using namespace runtime_test;
#define RT_REQUIRE(...) do { const bool ok = (__VA_ARGS__); CHECK_MESSAGE(ok, #__VA_ARGS__, \
    " runtimefault=", int(rig.owner.report().fault), " txfault=", int(rig.owner.transaction().report().fault), \
    " robotfault=", rig.owner.transaction().report().robot.contract_faults, \
    " state=", int(rig.owner.transaction().report().robot.outputs.ui_state)); \
    if (!ok) return; } while (false)

namespace {
void inhibited(const Rig& rig) {
    CHECK_FALSE(rig.fake.enabled);
    for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
void pureIdle(Rig& rig, std::uint32_t at) {
    const auto calls = rig.fake.count, epochs = rig.owner.report().epochs;
    rig.fake.now = at; CHECK_FALSE(rig.owner.step());
    CHECK(rig.fake.count == calls); CHECK(rig.owner.report().epochs == epochs);
    CHECK_FALSE(rig.owner.report().fresh);
}
}

TEST_CASE("B0 D096 constructor default grants and repeated begin perform no source operations") {
    Rig rig; CHECK(rig.fake.count == 0U); CHECK(rig.fake.clocks == 0U);
    CHECK_FALSE(rig.owner.step()); CHECK(rig.fake.count == 0U);
    RT_REQUIRE(rig.owner.begin({})); CHECK(rig.fake.trace[0].kind == Call::ENABLE_SETUP);
    CHECK(rig.fake.seen(Call::ADC_SETUP) == 0U); CHECK(rig.fake.seen(Call::OPP_SETUP) == 0U);
    CHECK(rig.fake.seen(Call::LINE_SETUP) == 0U); CHECK(rig.fake.imu_setups == 0U);
    const auto count = rig.fake.count; CHECK_FALSE(rig.begin(true, true)); CHECK(rig.fake.count == count);
    RT_REQUIRE(rig.next()); CHECK(rig.owner.report().epochs == 1U);
    CHECK_FALSE(rig.owner.report().initialization_complete);
    CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::BOOT);
    const auto& input = rig.owner.decisionInput();
    CHECK(input.line.explicit_values); CHECK(input.imu.explicit_values); CHECK(input.buttons.explicit_values);
    CHECK(input.line.presence == core::LinePresence::ABSENT); CHECK_FALSE(input.vbat_valid);
    CHECK(rig.fake.opponents == 0U); CHECK(rig.fake.buttons == 0U); inhibited(rig);
}

TEST_CASE("B0 D096 required callbacks are validated after gate before source setup") {
    for (unsigned missing = 0U; missing < 19U; ++missing) {
        Fake f; auto source = f.sourcePort(); auto adc = f.adcPort();
        if (missing == 0U) source.beginOpponents = nullptr;
        if (missing == 1U) source.readOpponents = nullptr;
        if (missing == 2U) source.beginLines = nullptr;
        if (missing == 3U) source.startLines = nullptr;
        if (missing == 4U) source.advanceLines = nullptr;
        if (missing == 5U) source.cancelLines = nullptr;
        if (missing == 6U) source.lines = nullptr;
        if (missing == 7U) source.startImu = nullptr;
        if (missing == 8U) source.advanceImuSetup = nullptr;
        if (missing == 9U) source.beginImu = nullptr;
        if (missing == 10U) source.advanceImu = nullptr;
        if (missing == 11U) source.cancelImu = nullptr;
        if (missing == 12U) source.imuSetupFailure = nullptr;
        if (missing == 13U) adc.beginWithButtons = nullptr;
        if (missing == 14U) adc.readA0 = nullptr;
        if (missing == 15U) adc.readA1 = nullptr;
        if (missing == 16U) adc.clockUs = nullptr;
        if (missing == 17U) source.beginMatrix = nullptr;
        if (missing == 18U) source.submitMatrix = nullptr;
        auto g = grants(false, true); g.matrix_enabled = true; g.matrix = {true, true};
        app::Runtime owner(f.motorPort(), adc, source); CHECK_FALSE(owner.begin(g));
        CHECK(f.trace[0].kind == Call::ENABLE_SETUP); CHECK(owner.report().fault == app::RuntimeFault::PORT);
        CHECK(f.seen(Call::ADC_SETUP) == 0U); CHECK(f.seen(Call::OPP_SETUP) == 0U);
        const auto calls = f.count; CHECK_FALSE(owner.step()); CHECK_FALSE(owner.begin({}));
        owner.abort(); CHECK(f.count == calls);
    }
}

TEST_CASE("B0 D096 null source and ADC ports are permitted only when ungranted") {
    Fake f; app::Runtime owner(f.motorPort(), {}, {});
    CHECK(owner.begin({})); CHECK(owner.step());
    CHECK(owner.report().phase == app::RuntimePhase::RUNNING);
    CHECK(owner.transaction().report().robot.outputs.ui_state == core::State::BOOT);
    CHECK(f.seen(Call::ADC_SETUP) == 0U); CHECK(f.seen(Call::OPP_SETUP) == 0U);
}

TEST_CASE("B0 D096 setup is Gate matrix ADC opponents exclusive QTR then explicit IMU") {
    Rig rig; auto g = grants(false, true); g.matrix_enabled = true; g.matrix = {true, true};
    RT_REQUIRE(rig.owner.begin(g));
    const Call expected[] = {Call::MATRIX_SETUP, Call::ADC_SETUP, Call::OPP_SETUP,
        Call::LINE_SETUP, Call::IMU_SETUP};
    unsigned selected = 0U;
    for (unsigned i = 0U; i < rig.fake.count; ++i) {
        if (selected < 5U && rig.fake.trace[i].kind == expected[selected]) ++selected;
    }
    CHECK(selected == 5U); CHECK(rig.fake.exclusive); CHECK(rig.fake.power_grant);
    CHECK(rig.fake.buttons == 0U); CHECK(rig.fake.opponents == 0U);
    CHECK(rig.fake.line_advances == 0U); CHECK(rig.fake.imu_begins == 0U);
}

TEST_CASE("B0 D096 gate failure and native setup failures retain evidence without retries") {
    { Rig rig; rig.fake.gate_ok = false; CHECK_FALSE(rig.begin());
      CHECK(rig.owner.report().fault == app::RuntimeFault::TRANSACTION);
      CHECK(rig.fake.seen(Call::ADC_SETUP) == 0U); }
    for (unsigned failure = 0U; failure < 3U; ++failure) {
        Rig rig;
        if (failure == 0U) rig.fake.adc_result = {power::Status::OWNERSHIP, power::Shutdown::UNCONFIRMED, false};
        if (failure == 1U) { rig.fake.opp_result.ready = false; rig.fake.opp_result.status[2] = -17; }
        if (failure == 2U) rig.fake.line_result = line_qtr::Status::OWNERSHIP;
        rig.owner.begin(grants()); rig.next(); CHECK_FALSE(rig.owner.report().initialization_complete);
        if (failure == 0U) CHECK(rig.owner.adcInputs().report().setup.status == power::Status::OWNERSHIP);
        if (failure == 1U) CHECK(rig.owner.report().opponents_setup.status[2] == -17);
        if (failure == 2U) CHECK(rig.owner.report().line_setup == line_qtr::Status::OWNERSHIP);
        CHECK(rig.fake.seen(Call::ADC_SETUP) <= 1U); CHECK(rig.fake.seen(Call::LINE_SETUP) <= 1U);
        inhibited(rig);
    }
}

TEST_CASE("B14 D096 immediate anchor early polls and latest released original grid never replay") {
    Rig rig; RT_REQUIRE(rig.owner.begin({})); const auto anchor = rig.owner.report().next_release_us;
    RT_REQUIRE(rig.owner.step()); CHECK(rig.owner.transaction().report().started_us == anchor);
    CHECK(rig.owner.report().next_release_us == anchor + 1000U);
    pureIdle(rig, anchor + 999U); rig.fake.now = anchor + 4500U; RT_REQUIRE(rig.owner.step());
    CHECK(rig.owner.report().missed_releases == 3U); CHECK(rig.owner.report().epochs == 2U);
    CHECK(rig.owner.transaction().report().started_us == anchor + 4500U);
    CHECK(rig.owner.report().next_release_us == anchor + 5000U);
    pureIdle(rig, anchor + 4500U);
}

TEST_CASE("B14 D096 C exact grid remains eligible while strict earlier releases are skipped") {
    for (auto duration : {999U, 1000U, 1001U, 2400U}) {
        Rig rig; auto g = app::SetupGrants{}; g.matrix_enabled = true; g.matrix = {true, true};
        RT_REQUIRE(rig.owner.begin(g)); const auto anchor = rig.owner.report().next_release_us;
        rig.fake.matrix_work = duration; RT_REQUIRE(rig.owner.step());
        const auto& report = rig.owner.transaction().report();
        CHECK(report.execution_us == duration); CHECK(report.completed_us == anchor + duration);
        CHECK(rig.owner.report().maximum_execution_us == duration);
        const auto slots = (duration - 1U) / 1000U;
        CHECK(rig.owner.report().missed_releases == slots);
        CHECK(rig.owner.report().next_release_us == anchor + (slots + 1U) * 1000U);
        CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
    }
}

TEST_CASE("B14 D096 release and complete timing cross natural wrap without inferred sensor time") {
    Rig rig; rig.fake.now = 0xFFFFFF00U; auto g = app::SetupGrants{};
    g.matrix_enabled = true; g.matrix = {true, true}; RT_REQUIRE(rig.owner.begin(g));
    rig.fake.matrix_work = 400U; RT_REQUIRE(rig.owner.step());
    CHECK(rig.owner.transaction().report().completed_us == 144U);
    CHECK(rig.owner.report().next_release_us == 744U); RT_REQUIRE(rig.next());
    CHECK(rig.owner.transaction().report().started_us == 744U);
}

TEST_CASE("B14 D096 backward half range and finitely frozen idle clocks halt once") {
    for (auto delta : {0xFFFFFFFFU, 0x80000000U}) {
        Rig rig; RT_REQUIRE(rig.owner.begin({})); rig.fake.now += delta;
        CHECK_FALSE(rig.owner.step()); CHECK(rig.owner.report().fault == app::RuntimeFault::CLOCK);
        const auto count = rig.fake.count; rig.owner.abort(); CHECK_FALSE(rig.owner.step());
        CHECK(rig.fake.count == count); inhibited(rig);
    }
    Rig rig; RT_REQUIRE(rig.owner.begin({})); RT_REQUIRE(rig.owner.step());
    unsigned calls = 0U;
    while (rig.owner.report().phase == app::RuntimePhase::RUNNING && calls < 65538U) {
        CHECK_FALSE(rig.owner.step()); ++calls;
    }
    CHECK(calls <= 65536U); CHECK(calls >= 65535U);
    CHECK(rig.owner.report().fault == app::RuntimeFault::CLOCK); CHECK(rig.owner.report().epochs == 1U);
}

TEST_CASE("B14 D096 original grid missed release counters saturate across observed wraps") {
    Rig rig; RT_REQUIRE(rig.owner.begin({})); RT_REQUIRE(rig.next());
    for (unsigned i = 0U; i < 2200U; ++i) {
        rig.fake.now += 0x7FFFF000U; RT_REQUIRE(rig.owner.step());
    }
    CHECK(rig.owner.report().missed_releases == 0xFFFFFFFFU);
    CHECK(rig.owner.report().epochs == 2201U); CHECK(rig.owner.report().fault == app::RuntimeFault::NONE);
}

TEST_CASE("B14 D096 actual D backward from acquisition completion aborts before any Robot decision") {
    Rig rig; rig.fake.reverse_decision_clock = true; RT_REQUIRE(rig.begin());
    CHECK_FALSE(rig.next()); CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
    CHECK(rig.owner.transaction().report().fault == app::Fault::CLOCK);
    CHECK_FALSE(rig.owner.transaction().report().decision_made);
    CHECK(rig.owner.transaction().report().robot.token == 0U); inhibited(rig);
}

TEST_CASE("B4 B14 D096 charging is exclusive and pending IMU interleaves discharge before opponent snapshot") {
    Rig rig; RT_REQUIRE(rig.begin(false, true)); RT_REQUIRE(rig.next());
    CHECK(rig.fake.violations == 0U); CHECK(rig.fake.imu_begins == 1U);
    CHECK(rig.fake.imu_advances == 3U); CHECK(rig.fake.line_starts == 1U);
    CHECK(rig.fake.line.phase == line_qtr::Phase::COMPLETE);
    CHECK(rig.owner.lineEvidence().sequence == 1U);
    CHECK(rig.owner.imuEvidence().heading_updated);
    CHECK(rig.owner.decisionInput().imu.gyro == core::ImuPresence::VALID);
    const auto& tx = rig.owner.transaction().report();
    CHECK(tx.started_us <= rig.owner.lineEvidence().started_us);
    CHECK(rig.owner.lineEvidence().completed_us <= tx.decision_us);
    CHECK(tx.decision_us <= tx.applied.feedback.applied_us);
    CHECK(tx.applied.feedback.applied_us <= tx.completed_us);
    CHECK(tx.execution_us == tx.completed_us - tx.started_us);
    unsigned last_source = 0U, first_gate = 0U;
    for (unsigned i = 0U; i < rig.fake.count; ++i) {
        if (rig.fake.trace[i].kind == Call::OPP) last_source = i;
        if (i > last_source && rig.fake.trace[i].kind == Call::ENABLE) first_gate = i;
    }
    CHECK(first_gate > last_source); CHECK(rig.fake.opponents == 1U);
}

TEST_CASE("B4 D096 CONTROL preserves completed mailbox before destructive new frame start") {
    Rig rig; RT_REQUIRE(rig.begin(true));
    RT_REQUIRE(rig.next()); CHECK(rig.fake.line.phase == line_qtr::Phase::DISCHARGING);
    RT_REQUIRE(rig.next()); CHECK(rig.owner.lineEvidence().sequence == 1U);
    const auto original = rig.owner.lineEvidence(); RT_REQUIRE(rig.next());
    if (rig.fake.line_sequence == 1U) RT_REQUIRE(rig.next());
    CHECK(rig.fake.line_sequence == 2U); CHECK(rig.owner.lineEvidence().sequence == original.sequence);
    CHECK(rig.owner.lineEvidence().started_us == original.started_us);
    CHECK(rig.owner.lineEvidence().completed_us == original.completed_us);
    CHECK(rig.owner.lineEvidence().max_service_gap_us > 500U);
}

TEST_CASE("B4 B14 D096 frozen active pump is finite and active cancellation follows Gate halt") {
    Rig rig; rig.fake.qtr_never_release = true; rig.fake.line_work = 0U;
    RT_REQUIRE(rig.begin()); CHECK_FALSE(rig.next());
    CHECK(rig.owner.report().fault == app::RuntimeFault::SERVICE_LIMIT);
    CHECK(rig.fake.line_advances <= 8192U); CHECK(rig.fake.line_advances >= 8191U);
    CHECK(rig.fake.line_cancels == 1U); CHECK(rig.owner.report().epochs == 0U);
    CHECK(rig.owner.transaction().report().phase == app::Phase::FAULT);
    unsigned cancel = 0U, halt = 0U;
    for (unsigned i = 0U; i < rig.fake.count; ++i) {
        if (rig.fake.trace[i].kind == Call::LINE_CANCEL) cancel = i;
        if (rig.fake.trace[i].kind == Call::SETTLE) halt = i;
    }
    CHECK(halt < cancel); const auto count = rig.fake.count;
    rig.owner.abort(); rig.owner.abort(); CHECK_FALSE(rig.owner.step()); CHECK(rig.fake.count == count);
}

TEST_CASE("B14 D096 pending IMU consumes one operation and finite original pump budget before cancel") {
    Rig rig; rig.fake.qtr_no_start = true; rig.fake.imu_never_complete = true; rig.fake.imu_work = 0U;
    RT_REQUIRE(rig.begin(false, true)); CHECK_FALSE(rig.next());
    CHECK(rig.owner.report().fault == app::RuntimeFault::SERVICE_LIMIT);
    CHECK(rig.fake.imu_begins == 1U); CHECK(rig.fake.imu_advances <= 8192U);
    CHECK(rig.fake.imu_cancels == 1U); CHECK(rig.fake.line_cancels == 0U);
    CHECK(rig.owner.imuEvidence().state == imu::HeadingState::WAITING);
    const auto count = rig.fake.count; CHECK_FALSE(rig.owner.step()); CHECK(rig.fake.count == count);
}

TEST_CASE("B14 D096 setup is advanced once per due epoch and real setup failure is consumed once") {
    Rig rig; rig.fake.setup_pending = true; RT_REQUIRE(rig.begin(false, true));
    rig.run(3U); CHECK(rig.fake.setup_advances == 3U); CHECK(rig.fake.imu_begins == 0U);
    pureIdle(rig, rig.fake.now); CHECK(rig.fake.setup_advances == 3U);
    rig.fake.setup_fault = true; rig.next();
    CHECK(rig.owner.report().imu_setup.fault == imu::SetupFault::TRANSPORT);
    CHECK(rig.fake.setup_failures == 1U); CHECK(rig.owner.imuEvidence().state == imu::HeadingState::FAULT);
    rig.run(2U); CHECK(rig.fake.setup_failures == 1U); CHECK(rig.fake.setup_advances == 4U);
}

TEST_CASE("B14 D096 completed observation survives genuine NO_NEW before first possible Robot admission") {
    Rig rig; RT_REQUIRE(rig.begin(false, true)); RT_REQUIRE(rig.next());
    const auto first = rig.owner.imuEvidence(); CHECK(first.heading_updated);
    rig.fake.imu_no_new = true; RT_REQUIRE(rig.next());
    const auto after = rig.owner.imuEvidence(); CHECK(after.heading_updated);
    CHECK(after.sequence == first.sequence); CHECK(after.observation_us == first.observation_us);
    CHECK(after.checked_us == first.checked_us); CHECK(after.raw_gyro_z_dps == first.raw_gyro_z_dps);
    CHECK(rig.owner.decisionInput().imu.heading_updated);
    CHECK(rig.fake.imu_begins == 2U); CHECK(rig.fake.imu_advances == 6U);
}

TEST_CASE("B14 D096 invalid IMU payload remains fault evidence even after expiry") {
    Rig rig; rig.fake.imu_bad_payload = true; RT_REQUIRE(rig.begin(false, true));
    RT_REQUIRE(rig.next()); CHECK(rig.owner.imuEvidence().state == imu::HeadingState::FAULT);
    CHECK(rig.owner.decisionInput().imu.gyro == core::ImuPresence::INVALID);
    CHECK_FALSE(rig.owner.decisionInput().imu.heading_available);
    rig.fake.imu_no_operation = true; rig.fake.now += 10000U; rig.owner.step();
    CHECK(rig.owner.imuEvidence().state == imu::HeadingState::FAULT);
    CHECK(rig.owner.imuEvidence().fault == imu::HeadingFault::INPUT);
}

TEST_CASE("B14 D096 actual D admits age1999 and2000 and expires2001 after earlier source completion") {
    for (auto age : {1999U, 2000U, 2001U}) {
        Rig rig; rig.fake.qtr_no_start = true; rig.fake.opponent_work = age;
        RT_REQUIRE(rig.begin(false, true)); RT_REQUIRE(rig.next());
        const auto& original = rig.owner.imuEvidence(); const auto& input = rig.owner.decisionInput();
        CHECK(original.heading_updated); CHECK(original.heading_available);
        CHECK(input.t_us - original.observation_us == age);
        CHECK(rig.owner.transaction().report().decision_us == input.t_us);
        CHECK(input.imu.heading_available == (age <= 2000U));
        CHECK(rig.owner.report().imu_expired == (age > 2000U));
        if (age > 2000U) {
            CHECK(input.imu.gyro == core::ImuPresence::INVALID);
            CHECK(input.imu.accel == core::ImuPresence::INVALID);
            CHECK(input.imu.sequence == 0U); CHECK(input.imu.observation_us == 0U);
            CHECK(input.raw_gyro_z_dps == 0.0F); CHECK(input.ax_g == 0.0F);
        }
    }
}

TEST_CASE("B14 D096 expired IMU publication never revives after a full clock wrap") {
    Rig rig; rig.fake.qtr_no_start = true; rig.fake.opponent_work = 2001U;
    auto g = grants(false, true); g.adc_pair = false;
    RT_REQUIRE(rig.owner.begin(g)); RT_REQUIRE(rig.next());
    const auto original = rig.owner.imuEvidence(); CHECK(rig.owner.report().imu_expired);
    rig.fake.imu_no_operation = true; rig.fake.opponent_work = 0U;
    const std::uint32_t before = rig.fake.now;
    rig.fake.now = before + 0x60000000U; RT_REQUIRE(rig.owner.step());
    CHECK_FALSE(rig.owner.decisionInput().imu.heading_available);
    rig.fake.now = before + 0xC0000000U; RT_REQUIRE(rig.owner.step());
    CHECK_FALSE(rig.owner.decisionInput().imu.heading_available);
    rig.fake.now = before + 0xFFFFFFF0U; RT_REQUIRE(rig.owner.step());
    rig.fake.now = before + 2000U; RT_REQUIRE(rig.owner.step());
    CHECK(rig.owner.report().imu_expired); CHECK_FALSE(rig.owner.decisionInput().imu.heading_available);
    CHECK(rig.owner.imuEvidence().sequence == original.sequence);
    CHECK(rig.owner.imuEvidence().observation_us == original.observation_us);
}

TEST_CASE("B4 B13 D096 completed line expires to absence without reviving after clock wrap") {
    Rig rig; auto g = grants(); g.adc_pair = false;
    RT_REQUIRE(rig.owner.begin(g)); RT_REQUIRE(rig.next());
    const auto first = rig.owner.lineEvidence(); CHECK(first.valid);
    rig.fake.qtr_no_start = true;
    rig.fake.now = first.started_us + 5999U; RT_REQUIRE(rig.owner.step());
    // Actual D includes current ADC/opponent work, so the 5999 start poll can already expire.
    CHECK(rig.owner.decisionInput().line.presence == core::LinePresence::ABSENT);
    for (auto delta : {0x60000000U, 0x60000000U, 0x40000000U}) {
        rig.fake.now += delta; RT_REQUIRE(rig.owner.step());
        CHECK(rig.owner.decisionInput().line.presence == core::LinePresence::ABSENT);
    }
}

TEST_CASE("B4 B13 D096 line source age5999 remains present and actual D6000 expires") {
    for (auto age : {5999U, 6000U, 6001U}) {
        Rig rig; auto g = grants(); g.adc_pair = false; rig.fake.opponent_work = 0U;
        RT_REQUIRE(rig.owner.begin(g)); RT_REQUIRE(rig.next());
        const auto source = rig.owner.lineEvidence(); rig.fake.qtr_no_start = true;
        rig.fake.now = source.started_us + age; RT_REQUIRE(rig.owner.step());
        CHECK(rig.owner.transaction().report().decision_us == source.started_us + age);
        CHECK(rig.owner.decisionInput().line.presence == (age < 6000U ?
            core::LinePresence::VALID : core::LinePresence::ABSENT));
        if (age >= 6000U) CHECK(rig.owner.decisionInput().line.sequence == 0U);
    }
}

TEST_CASE("B5 D096 incomplete failed future and out of epoch opponents never become fresh") {
    for (unsigned variant = 1U; variant <= 6U; ++variant) {
        Rig rig; rig.fake.opponent_error = variant;
        if (variant == 5U) rig.fake.opponent_shift = 100U;
        if (variant == 6U) rig.fake.opponent_shift = 0xFFFFF000U;
        RT_REQUIRE(rig.begin()); RT_REQUIRE(rig.next());
        CHECK_FALSE(rig.owner.decisionInput().opponent_fresh);
        CHECK_FALSE(rig.owner.report().initialization_complete); inhibited(rig);
    }
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B6 D096 battery cadence is one bounded A0 call per ten ms and shared faults invalidate buttons") {
    Rig rig; RT_REQUIRE(rig.begin()); rig.run(10U);
    CHECK(rig.fake.batteries == 1U); CHECK(rig.fake.buttons == 10U);
    rig.fake.adc_failure = true; RT_REQUIRE(rig.next()); CHECK(rig.fake.batteries == 2U);
    CHECK_FALSE(rig.owner.decisionInput().vbat_valid);
    CHECK(rig.owner.decisionInput().buttons.presence == core::ButtonPresence::INVALID);
    CHECK(rig.owner.adcInputs().report().first_status == power::Status::OVERRUN);
    const auto count = rig.fake.buttons; rig.run(2U); CHECK(rig.fake.buttons == count);
}
#endif

TEST_CASE("B13 D096 raw boot has no fabricated color and default windows cannot initialize") {
    Rig rig; rig.fake.line_lower = 299U; RT_REQUIRE(rig.begin()); RT_REQUIRE(rig.next());
    CHECK(rig.owner.decisionInput().line.use == core::LineUse::CALIBRATION);
    CHECK(rig.owner.decisionInput().line.white_candidates == 0U);
    CHECK_FALSE(rig.owner.transaction().report().robot.line_available);
#ifndef APP_TEST_CONFIGURED_BUTTONS
    CHECK_FALSE(rig.owner.report().initialization_complete);
    CHECK(rig.owner.decisionInput().buttons.presence == core::ButtonPresence::ABSENT);
    CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::BOOT);
#else
    CHECK(rig.owner.report().initialization_complete);
    CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::IDLE);
#endif
    inhibited(rig);
}

#ifndef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B13 D096 explicitly granting unconfigured button windows cannot initialize or release") {
    Rig rig; RT_REQUIRE(rig.owner.begin(grants())); RT_REQUIRE(rig.next());
    CHECK_FALSE(rig.owner.report().initialization_complete);
    CHECK(rig.owner.decisionInput().buttons.presence == core::ButtonPresence::INVALID);
    CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::STOPPED);
    inhibited(rig);
}
#endif

#ifdef APP_TEST_CONFIGURED_BUTTONS
namespace {
std::uint32_t releaseMatch(Rig& rig) {
    rig.run(35U); rig.run(30U, 1000U);
    std::uint32_t released = 0U; rig.fake.button_raw = 50U;
    for (unsigned i = 0U; i < 30U; ++i) {
        rig.next(); const auto& tx = rig.owner.transaction().report();
        if (tx.robot.lifecycle.gate.start_release) released = tx.robot.lifecycle.gate.release_us;
    }
    return released;
}
void modeLong(Rig& rig) { rig.run(35U); rig.run(1030U, 2000U); rig.run(35U); }
void modeShort(Rig& rig) { rig.run(35U); rig.run(30U, 2000U); rig.run(35U); }
void serviceRequest(Rig& rig) { rig.run(30U, 1000U); rig.run(30U); }
}

TEST_CASE("B3 B15 D096 actual configured Runtime holds5100ms applies bias and seals real STOP tail") {
    Rig rig; RT_REQUIRE(rig.begin(true, true)); const auto released = releaseMatch(rig);
    RT_REQUIRE(released != 0U); bool go = false; std::uint32_t go_at = 0U;
    for (unsigned i = 0U; i < 5200U && !go; ++i) {
        RT_REQUIRE(rig.next()); const auto& tx = rig.owner.transaction().report();
        if (tx.decision_us - released < 5100000U) { inhibited(rig);
            CHECK(tx.robot.outputs.ui_state == core::State::COUNTDOWN); }
        if (tx.robot.lifecycle.gate.go) { go = true; go_at = tx.decision_us; }
    }
    RT_REQUIRE(go); CHECK(go_at - released >= 5100000U); CHECK(go_at - released < 5101000U);
    CHECK(rig.owner.transaction().report().robot.lifecycle.services.calibration_samples >= config::CAL_MIN_SAMPLES);
    CHECK(rig.owner.imuEvidence().bias_dps == doctest::Approx(2.0F));
    CHECK(rig.owner.imuEvidence().heading_deg > 2.0F);
    CHECK(rig.owner.transaction().report().robot.heading.heading_deg == doctest::Approx(0.0F));
    rig.fake.button_raw = 3000U; bool stopped = false;
    for (unsigned i = 0U; i < 1100U; ++i) {
        RT_REQUIRE(rig.next());
        if (rig.owner.transaction().report().robot.outputs.ui_state == core::State::STOPPED) { stopped = true; break; }
    }
    RT_REQUIRE(stopped); inhibited(rig);
    CHECK(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::DRAINING);
    const auto token = rig.owner.transaction().report().robot.token;
    const auto buttons = rig.fake.buttons, opponents = rig.fake.opponents;
    const auto qtr_starts = rig.fake.line_starts, imu_starts = rig.fake.imu_begins;
    RT_REQUIRE(rig.next()); CHECK(rig.owner.transaction().report().robot.token == token + 1U);
    CHECK(rig.fake.buttons == buttons + 1U); CHECK(rig.fake.opponents == opponents + 1U);
    CHECK(rig.fake.line_starts == qtr_starts); CHECK(rig.fake.imu_begins == imu_starts);
    CHECK(rig.owner.decisionInput().line.presence == core::LinePresence::ABSENT);
    CHECK(rig.owner.report().phase == app::RuntimePhase::STOPPED);
    CHECK(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK_FALSE(rig.owner.transaction().recording().incomplete());
    const auto calls = rig.fake.count; rig.fake.now += 100000U;
    CHECK_FALSE(rig.owner.step()); CHECK(rig.fake.count == calls); inhibited(rig);
}

TEST_CASE("B4 B15 D096 actual allwhite guard enters inhibited edge and seals its own fault receipt") {
    Rig rig; RT_REQUIRE(rig.begin(true)); RT_REQUIRE(releaseMatch(rig) != 0U);
    rig.run(5150U); rig.fake.line_lower = 100U;
    bool escaped = false, fault = false;
    for (unsigned i = 0U; i < 8U; ++i) {
        RT_REQUIRE(rig.next()); const auto& robot = rig.owner.transaction().report().robot;
        escaped = escaped || robot.outputs.ui_state == core::State::EDGE_ESCAPE;
        fault = fault || robot.escape_fault != edge::EscapeFault::NONE;
    }
    CHECK(escaped); CHECK(fault); inhibited(rig);
    CHECK(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK_FALSE(rig.owner.transaction().recording().incomplete());
}

TEST_CASE("B3 D096 absent IMU does not block real initialization and stale buttons cannot release START") {
    Rig rig; RT_REQUIRE(rig.begin(true)); rig.run(40U);
    CHECK(rig.owner.report().initialization_complete); CHECK_FALSE(rig.owner.decisionInput().imu_ok);
    rig.run(30U, 1000U); rig.fake.freeze_buttons = true; rig.fake.button_raw = 50U;
    rig.run(40U); CHECK_FALSE(rig.owner.transaction().report().robot.lifecycle.gate.start_release);
    CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::STOPPED);
    inhibited(rig);
}

TEST_CASE("B13 D096 raw bootstrap eight genuine menu capture stages commit and require new control neutral") {
    Rig rig; RT_REQUIRE(rig.begin()); rig.run(40U);
    CHECK(rig.owner.report().initialization_complete);
    CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::IDLE);
    CHECK(releaseMatch(rig) == 0U); inhibited(rig);
    modeLong(rig); CHECK(rig.owner.transaction().report().robot.menu.selection.service_menu);
    modeShort(rig);
    RT_REQUIRE(rig.owner.transaction().report().robot.menu.selection.service == countdown::Service::QTR_CAL);
    for (unsigned stage = 0U; stage < 8U; ++stage) {
        rig.fake.line_lower = (stage & 1U) == 0U ? 197U : 500U;
        serviceRequest(rig);
        for (unsigned i = 0U; i < 60U && rig.owner.report().calibration.phase == qtr_cal::Phase::COLLECTING; ++i)
            rig.next();
        const auto& cal = rig.owner.report().calibration;
        CHECK(cal.reason == qtr_cal::Reason::NONE);
        CHECK(cal.phase == (stage == 7U ? qtr_cal::Phase::SUCCESS : qtr_cal::Phase::WAITING));
        if (stage < 7U) CHECK(cal.thresholds.version == 0U);
        inhibited(rig);
    }
    const auto bank = rig.owner.report().calibration.thresholds;
    CHECK(bank.version == 1U); for (auto threshold : bank.white_us) CHECK(threshold == 350U);
    CHECK(rig.owner.report().raw_lines); CHECK(rig.owner.decisionInput().line.threshold_version == 0U);
    rig.fake.line_lower = 800U; modeLong(rig);
    CHECK_FALSE(rig.owner.transaction().report().robot.menu.selection.service_menu);
    CHECK_FALSE(rig.owner.report().raw_lines); CHECK_FALSE(rig.owner.transaction().report().robot.line_calibration_hold);
    CHECK(rig.owner.transaction().report().robot.line_threshold_version == 1U);
    CHECK_FALSE(rig.owner.transaction().report().robot.line_start_rearming);
    CHECK(releaseMatch(rig) != 0U); CHECK(rig.owner.transaction().report().robot.outputs.ui_state == core::State::COUNTDOWN);
    inhibited(rig);
}

TEST_CASE("B13 D096 terminal interruption preserves active calibration report instead of forging cancellation") {
    Rig rig; RT_REQUIRE(rig.begin()); rig.run(40U); modeLong(rig); modeShort(rig);
    rig.fake.qtr_no_start = true; serviceRequest(rig);
    RT_REQUIRE(rig.owner.report().calibration.phase == qtr_cal::Phase::COLLECTING);
    const auto before = rig.owner.report().calibration;
    rig.owner.abort(); CHECK(rig.owner.report().calibration_interrupted);
    CHECK(rig.owner.report().calibration.phase == before.phase);
    CHECK(rig.owner.report().calibration.samples == before.samples);
    CHECK(rig.owner.report().calibration.thresholds.version == before.thresholds.version);
}

TEST_CASE("B14 B15 D096 matrix overrun is inside receipt and logged without a runtime800us stop") {
    Rig rig; auto g = grants(true); g.matrix_enabled = true; g.matrix = {true, true};
    RT_REQUIRE(rig.owner.begin(g)); const auto released = releaseMatch(rig); RT_REQUIRE(released != 0U);
    for (unsigned i = 0U; i < 5150U; ++i) rig.next();
    rig.fake.matrix_work = 1200U; RT_REQUIRE(rig.next());
    const auto duration = rig.owner.transaction().report().execution_us;
    CHECK(duration >= 1200U); CHECK(rig.owner.report().maximum_execution_us >= duration);
    CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
    rig.fake.matrix_work = 7U; RT_REQUIRE(rig.next());
    CHECK(rig.owner.transaction().report().robot.ticks.overruns >= 1U);
    CHECK(rig.owner.transaction().report().robot.ticks.max_us >= duration);
}
#endif

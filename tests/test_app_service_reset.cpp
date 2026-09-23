// Tests D103 inhibited local service access from the frozen contract alone.
// Actual Runtime and Transaction own Robot, MotorGate, recording and chronology.
// Scripted callbacks cover both motor profiles; no private state is seeded.
#include "doctest.h"
#include "fixtures/app_service_reset/fixture.h"
#include "fixtures/app_transaction_fixture.h"
#include <cstring>

using namespace service_reset_test;
#define SR_CHECK(...) do { const bool passed = (__VA_ARGS__); \
    CHECK_MESSAGE(passed, #__VA_ARGS__); if (!passed) return; } while (false)

namespace {
[[maybe_unused]] void inhibited(const Rig& rig) {
    const auto& tx = rig.owner.transaction().report();
    CHECK(tx.applied.consumed); CHECK(tx.applied.feedback.applied_valid);
    CHECK(tx.applied.fault == motors::Fault::STOPPED);
    CHECK(tx.applied.feedback.token == tx.robot.token);
    CHECK_FALSE(tx.applied.feedback.motors_enabled);
    CHECK(tx.applied.feedback.duty_l == 0.0F); CHECK(tx.applied.feedback.duty_r == 0.0F);
    CHECK_FALSE(tx.robot.outputs.motors_enabled);
    CHECK(tx.robot.outputs.duty_l == 0.0F); CHECK(tx.robot.outputs.duty_r == 0.0F);
    CHECK_FALSE(rig.fake.enabled); for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
struct TransactionRig {
    app_test::Port port;
    app::Transaction owner{port.port()};
    fsm::RobotInput source = app_test::input();
    std::uint32_t now = 1000U;
    bool tick() {
        now += 1000U; port.now = now;
        return owner.open() && owner.decide(source) && owner.finish();
    }
    bool stop() { source.stop_requested = true; return tick(); }
    bool open() { now += 1000U; port.now = now; return owner.open(); }
    bool startAttempt() {
        if (!owner.initialize() || !tick()) return false;
        for (unsigned i = 0; i < 25U; ++i) if (!tick()) return false;
        source.button = core::ButtonLevel::START;
        for (unsigned i = 0; i < 25U; ++i) if (!tick()) return false;
        source.button = core::ButtonLevel::NONE;
        for (unsigned i = 0; i < 25U; ++i) if (!tick()) return false;
        return owner.recording().phase() == recorder::AttemptPhase::RECORDING;
    }
};
void noMutation(TransactionRig& rig) {
    const auto report = rig.owner.report(); const auto feedback = rig.owner.previous();
    const auto calls = rig.port.count; const auto phase = rig.owner.recording().phase();
    CHECK_FALSE(rig.owner.resetStoppedRobotForService());
    CHECK(rig.owner.report().phase == report.phase); CHECK(rig.owner.report().fault == report.fault);
    CHECK(rig.owner.report().robot.token == report.robot.token);
    CHECK(rig.owner.previous().token == feedback.token);
    CHECK(rig.owner.previous().applied_valid == feedback.applied_valid);
    CHECK(rig.owner.recording().phase() == phase); CHECK(rig.port.count == calls);
}
}

TEST_CASE("B0 B13 D103 service grant and public reports default inert") {
    app::SetupGrants grants; app::RuntimeReport report; ui::DisplaySample sample;
    CHECK_FALSE(grants.local_service_reset); CHECK_FALSE(report.service_only);
    CHECK_FALSE(report.service_reset_pending); CHECK_FALSE(report.service_reset_fresh);
    CHECK(report.reset_from_token == 0U); CHECK_FALSE(report.service_action.fresh);
    CHECK(report.service_action.status == app::ServiceActionStatus::NONE);
    CHECK_FALSE(sample.service_unavailable);
}

TEST_CASE("B3 B13 D103 Transaction refuses every wrong phase without owner mutation") {
    TransactionRig rig; noMutation(rig); SR_CHECK(rig.owner.initialize()); noMutation(rig);
    SR_CHECK(rig.open()); noMutation(rig); SR_CHECK(rig.owner.decide(rig.source));
    noMutation(rig); SR_CHECK(rig.owner.finish()); noMutation(rig);
    rig.owner.abort(); noMutation(rig); CHECK(rig.owner.report().phase == app::Phase::FAULT);
}

TEST_CASE("B3 B15 D103 EMPTY still requires two genuine complete STOP receipts") {
    TransactionRig rig; SR_CHECK(rig.owner.initialize()); SR_CHECK(rig.stop());
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
    noMutation(rig); SR_CHECK(rig.open()); noMutation(rig);
    SR_CHECK(rig.owner.decide(rig.source)); noMutation(rig); SR_CHECK(rig.owner.finish());
    const auto token = rig.owner.report().robot.token; const auto calls = rig.port.count;
    noMutation(rig); SR_CHECK(rig.open()); const auto started = rig.owner.report().started_us;
    SR_CHECK(rig.owner.resetStoppedRobotForService());
    CHECK(rig.port.count == calls + 1U); CHECK(rig.owner.report().phase == app::Phase::ACQUIRING);
    CHECK(rig.owner.report().started_us == started); CHECK_FALSE(rig.owner.previous().applied_valid);
    CHECK_FALSE(rig.owner.previous().duration_valid); noMutation(rig);
    rig.source.stop_requested = false; SR_CHECK(rig.owner.decide(rig.source));
    SR_CHECK(rig.owner.finish()); CHECK(rig.owner.report().robot.token == token + 1U);
    CHECK(rig.owner.report().applied.fault == motors::Fault::STOPPED);
    CHECK(rig.owner.report().applied.feedback.applied_valid);
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::EMPTY);
    SR_CHECK(rig.stop()); SR_CHECK(rig.tick()); SR_CHECK(rig.open()); noMutation(rig);
}

TEST_CASE("B3 B15 D103 recording and draining refuse until real STOP tail seals") {
    TransactionRig rig; SR_CHECK(rig.startAttempt()); SR_CHECK(rig.open()); noMutation(rig);
    SR_CHECK(rig.owner.decide(rig.source)); SR_CHECK(rig.owner.finish()); SR_CHECK(rig.stop());
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::DRAINING);
    SR_CHECK(rig.open()); noMutation(rig); SR_CHECK(rig.owner.decide(rig.source));
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED); noMutation(rig);
    SR_CHECK(rig.owner.finish()); std::string frames, events, summary;
    SR_CHECK(csv(rig.owner.recording(), frames, events, summary));
    SR_CHECK(rig.open()); SR_CHECK(rig.owner.resetStoppedRobotForService());
    std::string f, e, s; SR_CHECK(csv(rig.owner.recording(), f, e, s));
    CHECK(f == frames); CHECK(e == events); CHECK(s == summary);
}

TEST_CASE("B3 B15 D103 old SEALED attempt is not proof of a new STOP tail") {
    TransactionRig rig; SR_CHECK(rig.startAttempt()); rig.source.button = core::ButtonLevel::MODE;
    for (unsigned i = 0U; i < 25U; ++i) SR_CHECK(rig.tick());
    SR_CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    SR_CHECK(rig.stop()); SR_CHECK(rig.open()); noMutation(rig);
    SR_CHECK(rig.owner.decide(rig.source)); SR_CHECK(rig.owner.finish());
    SR_CHECK(rig.open()); SR_CHECK(rig.owner.resetStoppedRobotForService());
}

TEST_CASE("B14 B15 D103 failed completion or interrupted recorder cannot reset") {
    for (unsigned reason = 0; reason < 3U; ++reason) {
        TransactionRig rig; SR_CHECK(rig.startAttempt()); SR_CHECK(rig.stop());
        SR_CHECK(rig.open()); SR_CHECK(rig.owner.decide(rig.source));
        if (reason == 0U) { rig.port.now -= 1U; CHECK_FALSE(rig.owner.finish()); }
        else if (reason == 1U) rig.owner.abort();
        else { SR_CHECK(rig.owner.finish()); SR_CHECK(rig.open()); rig.owner.abort(); }
        noMutation(rig); CHECK(rig.owner.report().phase == app::Phase::FAULT);
    }
}

TEST_CASE("B3 D103 failed actual motor inhibition never supplies guarded reset proof") {
    TransactionRig rig; SR_CHECK(rig.owner.initialize()); SR_CHECK(rig.stop());
    SR_CHECK(rig.open()); rig.port.fail_at = rig.port.operations + 1U;
    SR_CHECK(rig.owner.decide(rig.source)); CHECK_FALSE(rig.owner.report().applied.feedback.applied_valid);
    SR_CHECK(rig.owner.finish()); SR_CHECK(rig.open()); noMutation(rig);
}

TEST_CASE("B15 D103 actual recorder interruption remains terminal and unavailable to reset") {
    for (bool draining : {false, true}) {
        TransactionRig rig; SR_CHECK(rig.startAttempt());
        if (draining) SR_CHECK(rig.stop());
        CHECK(rig.owner.recording().phase() == (draining ? recorder::AttemptPhase::DRAINING :
            recorder::AttemptPhase::RECORDING));
        rig.owner.abort(); CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::INTERRUPTED);
        CHECK(rig.owner.recording().summary().interrupted); noMutation(rig);
    }
}

TEST_CASE("B13 D103 unavailable calibration glyph is C plus existing cross only") {
    ui::DisplaySample sample; sample.state = core::State::IDLE;
    sample.service_menu = true; sample.service = countdown::Service::QTR_CAL;
    ui::Frame regular, unavailable, drive;
    SR_CHECK(ui::render(sample, regular) == ui::RenderStatus::OK);
    sample.service_unavailable = true;
    SR_CHECK(ui::render(sample, unavailable) == ui::RenderStatus::OK);
    sample.service = countdown::Service::DRIVE_TEST;
    SR_CHECK(ui::render(sample, drive) == ui::RenderStatus::OK);
    bool changed = false;
    for (unsigned y = 0U; y < 8U; ++y) for (unsigned x = 0U; x < 13U; ++x) {
        const auto at = y * 13U + x;
        if (x >= 4U && x <= 8U && y < 7U) {
            CHECK(unavailable.pixels[at] == drive.pixels[at]);
            changed |= unavailable.pixels[at] != regular.pixels[at];
        } else CHECK(unavailable.pixels[at] == regular.pixels[at]);
    }
    CHECK(changed);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B3 B15 D103 default off stops after exact real tail and remains passive") {
    Rig rig; SR_CHECK(rig.stopped(true, false, false));
    CHECK(rig.owner.report().phase == app::RuntimePhase::STOPPED);
    CHECK(rig.owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED);
    CHECK(rig.owner.transaction().recording().summary().go_seen);
    const auto token = rig.robot().token; const auto calls = rig.fake.count;
    const auto epochs = rig.owner.report().epochs; const auto clocks = rig.fake.clocks;
    for (unsigned i = 0U; i < 10U; ++i) { CHECK_FALSE(rig.next()); CHECK_FALSE(rig.owner.report().fresh); }
    CHECK(rig.robot().token == token); CHECK(rig.fake.count == calls);
    CHECK(rig.fake.clocks == clocks); CHECK(rig.owner.report().epochs == epochs); inhibited(rig);
}

TEST_CASE("B3 B4 B15 D103 enabled STOP observation is actual CONTROL and honest expired QTR") {
    Rig rig; SR_CHECK(rig.begin()); SR_CHECK(rig.run(35U)); SR_CHECK(rig.firstStop());
    const auto first = rig.robot().token; CHECK(rig.owner.report().phase != app::RuntimePhase::STOP_OBSERVING);
    SR_CHECK(rig.next()); CHECK(rig.robot().token == first + 1U);
    SR_CHECK(rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING);
    const auto starts = rig.fake.line_starts, advances = rig.fake.line_advances;
    const auto cancels = rig.fake.line_cancels, buttons = rig.fake.buttons;
    const auto opponents = rig.fake.opponents; SR_CHECK(rig.run(20U));
    CHECK(rig.fake.buttons == buttons + 20U); CHECK(rig.fake.opponents == opponents + 20U);
    CHECK(rig.fake.line_starts == starts); CHECK(rig.fake.line_advances == advances);
    CHECK(rig.fake.line_cancels == cancels); CHECK((rig.robot().contract_faults & fsm::LINE_CONTRACT) != 0U);
    CHECK(rig.owner.decisionInput().line.use == core::LineUse::CONTROL);
    CHECK(rig.owner.decisionInput().line.presence != core::LinePresence::VALID);
    CHECK_FALSE(rig.robot().line_updated); CHECK(rig.owner.transaction().report().finished);
    CHECK(rig.owner.transaction().report().timing_valid); inhibited(rig);
    const auto calls = rig.fake.count; const auto token = rig.robot().token;
    CHECK_FALSE(rig.owner.step()); CHECK(rig.fake.count == calls); CHECK(rig.robot().token == token);
}

TEST_CASE("B3 B13 D103 pending is delayed to real next S and preserves source and owner lifetime") {
    Rig rig; SR_CHECK(rig.stopped(true, true)); SR_CHECK(rig.pending());
    const auto before = rig.owner.report(); const auto token = rig.robot().token;
    const auto old_faults = rig.robot().contract_faults;
    const auto button = rig.owner.decisionInput().buttons;
    const auto buttons = rig.fake.buttons, opponents = rig.fake.opponents;
    const auto starts = rig.fake.line_starts, advances = rig.fake.line_advances;
    const auto imu = rig.fake.imu_begins, imu_advance = rig.fake.imu_advances;
    const auto high = rig.fake.highs, nonzero = rig.fake.nonzero;
    const auto input_report = rig.owner.adcInputs().report();
    const auto imu_diagnostic = rig.owner.imuEvidence();
    std::string f, e, s; SR_CHECK(csv(rig.owner.transaction().recording(), f, e, s));
    CHECK_FALSE(before.service_only); CHECK_FALSE(before.service_reset_fresh);
    CHECK(rig.owner.transaction().report().finished); inhibited(rig);
    CHECK_FALSE(rig.owner.step()); CHECK(rig.owner.report().service_reset_pending);
    SR_CHECK(rig.next()); CHECK(rig.owner.report().service_only);
    CHECK(rig.owner.report().service_reset_fresh); CHECK_FALSE(rig.owner.report().service_reset_pending);
    CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
    CHECK(rig.owner.report().reset_from_token == token);
    CHECK(rig.owner.report().pre_service_contract_faults == old_faults);
    CHECK((rig.owner.report().pre_service_contract_faults & fsm::LINE_CONTRACT) != 0U);
    CHECK(rig.robot().token == token + 1U); CHECK(rig.fake.buttons == buttons + 1U);
    CHECK(rig.fake.opponents == opponents + 1U);
    CHECK(rig.owner.decisionInput().buttons.sequence == button.sequence + 1U);
    CHECK(rig.owner.decisionInput().buttons.started_us != button.started_us);
    CHECK(rig.owner.adcInputs().report().button_attempts == input_report.button_attempts + 1U);
    CHECK(rig.fake.line_starts == starts); CHECK(rig.fake.line_advances == advances);
    CHECK(rig.fake.imu_begins == imu); CHECK(rig.fake.imu_advances == imu_advance);
    CHECK(rig.fake.adc_setups == 1U); CHECK(rig.fake.opp_setups == 1U);
    CHECK(rig.fake.line_setups == 1U); CHECK(rig.fake.imu_setups == 1U);
    CHECK(rig.fake.enable_setups == 1U); CHECK(rig.fake.pwm_setups == 4U);
    CHECK(rig.fake.highs == high); CHECK(rig.fake.nonzero == nonzero);
    CHECK(rig.owner.report().line_shutdown.status == before.line_shutdown.status);
    CHECK(rig.owner.report().imu_shutdown.state == before.imu_shutdown.state);
    CHECK(rig.owner.imuEvidence().observation_us == imu_diagnostic.observation_us);
    const auto& input = rig.owner.decisionInput();
    CHECK(input.initialization_complete); CHECK(input.opponent_fresh); CHECK(input.vbat_valid);
    CHECK(input.buttons.explicit_values); CHECK(input.buttons.presence == core::ButtonPresence::VALID);
    CHECK(input.line.explicit_values); CHECK(input.line.use == core::LineUse::CALIBRATION);
    CHECK(input.line.presence == core::LinePresence::ABSENT); CHECK(input.line.sequence == 0U);
    CHECK(input.line.started_us == 0U); CHECK(input.line.completed_us == 0U);
    CHECK(input.line.threshold_version == 0U); CHECK_FALSE(input.imu_ok);
    CHECK(input.imu.explicit_values); CHECK(input.imu.gyro == core::ImuPresence::ABSENT);
    CHECK(input.imu.accel == core::ImuPresence::ABSENT); CHECK(input.imu.sequence == 0U);
    CHECK(input.imu.observation_us == 0U); CHECK(input.imu.checked_us == 0U);
    CHECK_FALSE(input.imu.heading_available); CHECK_FALSE(input.imu.heading_updated);
    CHECK(input.raw_heading_deg == 0.0F); CHECK(input.raw_gyro_z_dps == 0.0F);
    CHECK(input.ax_g == 0.0F); CHECK(input.ay_g == 0.0F);
    CHECK(input.reset_cause == fsm::ResetCause::UNKNOWN); inhibited(rig);
    std::string f2, e2, s2; SR_CHECK(csv(rig.owner.transaction().recording(), f2, e2, s2));
    CHECK(f == f2); CHECK(e == e2); CHECK(s == s2);
    CHECK_FALSE(rig.owner.step()); CHECK_FALSE(rig.owner.report().service_reset_fresh);
    CHECK(rig.owner.report().service_only);
}

TEST_CASE("B13 D103 pending age uses real release source start at 4999 5000 5001 us") {
    for (auto battery_work : {0U, 5U}) for (auto age : {4995U, 4996U, 4999U, 5000U, 5001U}) {
        CAPTURE(age); CAPTURE(battery_work); Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.pending());
        const auto source = rig.owner.decisionInput().buttons.started_us;
        const auto token = rig.robot().token; rig.fake.now = source + age;
        const auto old_decision = rig.owner.transaction().report().decision_us;
        const auto old_completion = rig.owner.transaction().report().completed_us;
        const auto batteries = rig.fake.batteries; rig.fake.adc_work = battery_work;
        const bool completed = rig.owner.step();
        const auto actual_source_gap = rig.owner.decisionInput().buttons.started_us - source;
        const auto decision_gap = rig.owner.transaction().report().decision_us - old_decision;
        CAPTURE(source); CAPTURE(old_decision); CAPTURE(old_completion); CAPTURE(actual_source_gap);
        CAPTURE(rig.owner.decisionInput().buttons.started_us);
        CAPTURE(rig.owner.decisionInput().buttons.completed_us);
        CAPTURE(rig.owner.transaction().report().started_us);
        CAPTURE(rig.owner.transaction().report().decision_us);
        CAPTURE(int(rig.owner.report().fault)); CAPTURE(int(rig.owner.transaction().report().fault));
        CAPTURE(rig.robot().contract_faults); CAPTURE(int(rig.owner.adcInputs().report().fault));
        CHECK(rig.owner.report().service_only == (age <= 5000U));
        CHECK(rig.owner.report().service_reset_fresh == (age <= 5000U));
        CHECK_FALSE(rig.owner.report().service_reset_pending);
        CHECK(rig.robot().token == token + 1U);
        CHECK(rig.fake.batteries == batteries + 1U); CHECK(actual_source_gap == age);
        CHECK(decision_gap == age + battery_work);
        if (age <= 5000U && (actual_source_gap > 5000U || decision_gap > 5000U)) {
            CHECK_FALSE(completed); CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
            CHECK_FALSE(rig.owner.transaction().report().finished);
            CHECK_FALSE(rig.owner.transaction().report().timing_valid);
        } else { CHECK(completed); inhibited(rig); }
        if (age > 5000U) {
            CHECK(rig.owner.report().reset_from_token == 0U);
            CHECK((rig.robot().contract_faults & fsm::BUTTON_CONTRACT) != 0U);
        }
    }
}

TEST_CASE("B13 D103 held MODE on entry cannot skip genuine neutral qualification") {
    Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(1100U, MODE));
    SR_CHECK(rig.run(30U)); CHECK_FALSE(rig.owner.report().service_only);
    CHECK_FALSE(rig.owner.report().service_reset_pending); SR_CHECK(rig.pending());
    SR_CHECK(rig.next()); CHECK(rig.owner.report().service_only); inhibited(rig);
}

TEST_CASE("B13 D103 eligible pending S cannot erase real first postreset source gap") {
    for (auto age : {4999U, 5000U}) {
        Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.pending());
        const auto release = rig.owner.decisionInput().buttons;
        const auto token = rig.robot().token;
        rig.fake.button_delay = 11U; rig.fake.now = release.started_us + age;
        CHECK_FALSE(rig.owner.step()); CHECK(rig.owner.report().service_reset_fresh);
        CHECK(rig.owner.report().service_only); CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
        CHECK(rig.owner.decisionInput().buttons.started_us - release.started_us > 5000U);
        CHECK(rig.owner.decisionInput().buttons.sequence == release.sequence + 1U);
        CHECK(rig.robot().token == token + 1U); CHECK(rig.owner.transaction().report().decision_made);
        CHECK_FALSE(rig.owner.transaction().report().finished);
        CHECK_FALSE(rig.owner.transaction().report().timing_valid);
        CHECK(rig.owner.transaction().report().halt.attempted);
    }
}

TEST_CASE("B13 D103 first service BOOT readiness uses real current ADC and opponents") {
    for (unsigned absent = 0U; absent < 2U; ++absent) {
        Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.pending());
        if (absent == 0U) rig.fake.buttons_failure = true;
        if (absent == 1U) rig.fake.opponent_error = 1U;
        rig.next(); CHECK(rig.owner.report().service_reset_fresh);
        CHECK_FALSE(rig.owner.decisionInput().initialization_complete);
        CHECK_FALSE(rig.owner.report().initialization_complete);
        CHECK_FALSE(rig.fake.enabled);
    }
}

TEST_CASE("B13 D103 neutral source debounce accepts 20000 and 20001 but rejects 19999 us") {
    for (int delta : {-1, 0, 1}) {
        CAPTURE(delta); Rig rig; SR_CHECK(rig.stopped());
        rig.fake.button_work = delta < 0 ? 6U : 5U; SR_CHECK(rig.run(1U));
        const auto source = rig.owner.decisionInput().buttons.completed_us;
        rig.fake.button_work = 5U; SR_CHECK(rig.run(19U));
        rig.fake.button_work = delta > 0 ? 6U : 5U; SR_CHECK(rig.run(1U));
        CHECK(rig.owner.decisionInput().buttons.completed_us - source ==
            static_cast<std::uint32_t>(20000 + delta));
        rig.fake.button_work = 5U; SR_CHECK(rig.run(1040U, MODE)); SR_CHECK(rig.run(25U));
        CHECK(rig.owner.report().service_only == (delta >= 0));
    }
}

TEST_CASE("B13 D103 release source debounce creates pending at 20000 and 20001 not 19999 us") {
    for (int delta : {-1, 0, 1}) {
        CAPTURE(delta); Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(30U));
        SR_CHECK(rig.run(1040U, MODE)); rig.fake.button_work = delta < 0 ? 6U : 5U;
        SR_CHECK(rig.run(1U)); const auto source = rig.owner.decisionInput().buttons.completed_us;
        rig.fake.button_work = 5U; SR_CHECK(rig.run(19U));
        rig.fake.button_work = delta > 0 ? 6U : 5U; SR_CHECK(rig.run(1U));
        CHECK(rig.owner.decisionInput().buttons.completed_us - source ==
            static_cast<std::uint32_t>(20000 + delta));
        CHECK(rig.owner.report().service_reset_pending == (delta >= 0));
        CHECK_FALSE(rig.owner.report().service_only);
    }
}

TEST_CASE("B13 D103 MODE debounce completion fixes the nonbackdated long anchor") {
    for (int delta : {-1, 0, 1}) {
        CAPTURE(delta); Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(30U));
        rig.fake.button_work = delta < 0 ? 6U : 5U; SR_CHECK(rig.run(1U, MODE));
        const auto source = rig.owner.decisionInput().buttons.completed_us;
        rig.fake.button_work = 5U; SR_CHECK(rig.run(19U, MODE));
        rig.fake.button_work = delta > 0 ? 6U : 5U; SR_CHECK(rig.run(1U, MODE));
        CHECK(rig.owner.decisionInput().buttons.completed_us - source ==
            static_cast<std::uint32_t>(20000 + delta));
        const auto candidate_decision = rig.owner.transaction().report().decision_us;
        rig.fake.button_work = 5U; SR_CHECK(rig.run(999U, MODE));
        const auto offset = rig.owner.decisionInput().buttons.completed_us -
            rig.owner.transaction().report().started_us;
        rig.fake.now = candidate_decision + 1000000U - offset;
        SR_CHECK(rig.owner.step()); SR_CHECK(rig.run(25U));
        CHECK(rig.owner.report().service_only == (delta >= 0));
    }
}

TEST_CASE("B13 D103 early release and release contamination cancel instead of retrospectively holding") {
    for (unsigned scenario = 0U; scenario < 5U; ++scenario) {
        CAPTURE(scenario); Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(30U));
        SR_CHECK(rig.run(scenario == 0U ? 1020U : 1040U, MODE));
        if (scenario != 0U) { SR_CHECK(rig.run(10U));
            SR_CHECK(rig.run(1U, scenario == 1U ? MODE : scenario == 2U ? START : BOTH)); }
        SR_CHECK(rig.run(35U)); CHECK_FALSE(rig.owner.report().service_reset_pending);
        CHECK_FALSE(rig.owner.report().service_only);
        SR_CHECK(rig.pending()); SR_CHECK(rig.next()); CHECK(rig.owner.report().service_only);
    }
}

TEST_CASE("B13 D103 source completion before decision anchor cannot underflow into long hold") {
    Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(30U));
    rig.fake.opponent_work = 500U; SR_CHECK(rig.run(21U, MODE));
    const auto anchor = rig.owner.transaction().report().decision_us;
    CHECK(anchor - rig.owner.decisionInput().buttons.completed_us >= 500U);
    rig.fake.opponent_work = 5U; SR_CHECK(rig.run(1U, MODE)); SR_CHECK(rig.run(30U));
    CHECK_FALSE(rig.owner.report().service_reset_pending); CHECK_FALSE(rig.owner.report().service_only);
}

TEST_CASE("B13 D103 long boundary requires a MODE observation and release wins at equality") {
    for (unsigned release_at = 0U; release_at < 2U; ++release_at) {
        Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(30U)); SR_CHECK(rig.run(21U, MODE));
        const auto anchor = rig.owner.transaction().report().decision_us;
        SR_CHECK(rig.run(999U, MODE)); rig.fake.button_raw = release_at ? MODE : NONE;
        const auto completion_offset = rig.owner.decisionInput().buttons.completed_us -
            rig.owner.transaction().report().started_us;
        rig.fake.now = anchor + config::BTN_LONG_MS * 1000U - completion_offset;
        SR_CHECK(rig.owner.step()); CHECK(rig.owner.decisionInput().buttons.completed_us ==
            anchor + config::BTN_LONG_MS * 1000U);
        SR_CHECK(rig.run(25U));
        CHECK(rig.owner.report().service_only == (release_at != 0U));
    }
}

TEST_CASE("B13 D103 replay stale invalid or ADC failure never create neutral observations") {
    for (unsigned scenario = 0U; scenario < 4U; ++scenario) {
        CAPTURE(scenario); Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.run(30U));
        SR_CHECK(rig.run(1040U, MODE)); SR_CHECK(rig.run(1U));
        if (scenario == 0U) rig.fake.freeze_buttons = true;
        if (scenario == 1U) rig.fake.button_raw = 16000U;
        if (scenario == 2U) rig.fake.buttons_failure = true;
        if (scenario == 3U) rig.fake.adc_failure = true;
        for (unsigned i = 0U; i < 120U; ++i) {
            rig.next(); CHECK_FALSE(rig.owner.report().service_reset_fresh);
            CHECK_FALSE(rig.owner.report().service_only);
        }
        CHECK_FALSE(rig.owner.report().service_reset_pending);
        CHECK((rig.owner.adcInputs().report().fault != power::InputFault::NONE ||
            (rig.robot().contract_faults & fsm::BUTTON_CONTRACT) != 0U));
    }
}

TEST_CASE("B14 D103 original C next S and postreset clock failures cannot fabricate completion") {
    for (unsigned boundary = 0U; boundary < 3U; ++boundary) {
        CAPTURE(boundary); Rig rig; SR_CHECK(rig.stopped());
        app::TransactionReport prior;
        if (boundary == 0U) {
            SR_CHECK(rig.run(30U)); SR_CHECK(rig.run(1040U, MODE)); SR_CHECK(rig.run(20U));
            rig.fake.reverse_matrix = true; CHECK_FALSE(rig.next());
        } else {
            SR_CHECK(rig.pending());
            prior = rig.owner.transaction().report();
            if (boundary == 1U) rig.fake.now = rig.owner.transaction().report().completed_us - 1U;
            else { rig.fake.now = rig.owner.report().next_release_us;
                rig.fake.clock_reversal_countdown = 3U; }
            CHECK_FALSE(rig.owner.step());
        }
        CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
        CHECK_FALSE(rig.owner.report().fresh);
        if (boundary == 1U) {
            CHECK(rig.owner.transaction().report().completed_us == prior.completed_us);
            CHECK(rig.owner.transaction().report().robot.token == prior.robot.token);
        } else {
            CHECK_FALSE(rig.owner.transaction().report().finished);
            CHECK_FALSE(rig.owner.transaction().report().timing_valid);
        }
        CHECK(rig.owner.report().service_reset_fresh == (boundary == 2U));
        const auto calls = rig.fake.count; CHECK_FALSE(rig.next()); CHECK(rig.fake.count == calls);
        CHECK_FALSE(rig.owner.report().service_reset_fresh);
    }
}

TEST_CASE("B3 D103 actual failed stopped inhibition is terminal before any service recovery") {
    for (unsigned service = 0U; service < 2U; ++service) {
        Rig rig; SR_CHECK(service ? rig.reset() : rig.stopped());
        rig.fake.reject_enable = true; CHECK_FALSE(rig.next());
        CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
        CHECK_FALSE(rig.owner.transaction().report().applied.feedback.applied_valid);
        const auto calls = rig.fake.count; CHECK_FALSE(rig.next()); CHECK(rig.fake.count == calls);
        CHECK_FALSE(rig.owner.report().service_reset_pending);
    }
}

TEST_CASE("B13 D103 fresh reset acquisition handles a new START without match permission") {
    Rig rig; SR_CHECK(rig.stopped()); SR_CHECK(rig.pending()); rig.fake.button_raw = START;
    SR_CHECK(rig.next()); CHECK(rig.owner.report().service_only);
    CHECK(rig.owner.decisionInput().buttons.level == core::ButtonLevel::START);
    SR_CHECK(rig.run(40U, START)); SR_CHECK(rig.run(40U));
    CHECK(rig.robot().outputs.ui_state == core::State::IDLE);
    CHECK_FALSE(rig.robot().lifecycle.gate.start_release); inhibited(rig);
    for (unsigned mode = 0U; mode < 6U; ++mode) {
        SR_CHECK(rig.run(30U, MODE)); SR_CHECK(rig.run(30U));
        SR_CHECK(rig.run(30U, START)); SR_CHECK(rig.run(30U));
        CHECK(rig.robot().outputs.ui_state == core::State::IDLE);
        CHECK_FALSE(rig.robot().lifecycle.gate.start_release); inhibited(rig);
    }
}

TEST_CASE("B13 D103 unavailable service requests preserve genuine intent calibration and fresh pulses") {
    for (unsigned item : {1U, 2U}) {
        Rig rig; SR_CHECK(rig.reset()); SR_CHECK(rig.select(item));
        const auto selected = item == 1U ? countdown::Service::QTR_CAL : countdown::Service::DRIVE_TEST;
        SR_CHECK(rig.robot().menu.selection.service == selected);
        const auto calibration = rig.owner.report().calibration;
        SR_CHECK(rig.request(selected)); const auto action = rig.owner.report().service_action;
        CHECK(action.fresh); CHECK(action.service == selected);
        CHECK(action.request_token == rig.robot().token);
        CHECK(action.status == app::ServiceActionStatus::UNAVAILABLE);
        CHECK(rig.robot().menu.request == selected); CHECK(rig.owner.report().calibration.phase == calibration.phase);
        CHECK(rig.owner.report().calibration.samples == calibration.samples);
        CHECK(rig.owner.report().calibration.reason == calibration.reason);
        CHECK(rig.owner.report().calibration.thresholds.version == calibration.thresholds.version);
        auto sample = ui::displaySample(rig.owner.decisionInput(), rig.robot());
        ui::applyCalibration(sample, calibration); sample.service_unavailable = true;
        ui::Frame expected; SR_CHECK(ui::render(sample, expected) == ui::RenderStatus::OK);
        CHECK(std::memcmp(expected.pixels, rig.fake.displayed.pixels, sizeof(expected.pixels)) == 0);
        CHECK_FALSE(rig.owner.step()); CHECK_FALSE(rig.owner.report().service_action.fresh);
        CHECK(rig.owner.report().service_action.request_token == action.request_token);
        CHECK(rig.owner.report().service_action.status == action.status); inhibited(rig);
    }
}

TEST_CASE("B4 B13 D103 actual committed nondefault calibration bank survives forced service RAW") {
    Rig rig; SR_CHECK(rig.begin(true, false)); SR_CHECK(rig.run(40U)); SR_CHECK(rig.select(1U));
    SR_CHECK(rig.robot().menu.selection.service == countdown::Service::QTR_CAL);
    for (unsigned stage = 0U; stage < 8U; ++stage) {
        rig.fake.line_lower = (stage & 1U) == 0U ? 197U : 500U;
        SR_CHECK(rig.request(countdown::Service::QTR_CAL));
        for (unsigned i = 0U; i < 60U && rig.owner.report().calibration.phase == qtr_cal::Phase::COLLECTING; ++i)
            SR_CHECK(rig.next());
        SR_CHECK(rig.owner.report().calibration.reason == qtr_cal::Reason::NONE);
        SR_CHECK(rig.run(30U));
    }
    const auto bank = rig.owner.report().calibration;
    CHECK(bank.phase == qtr_cal::Phase::SUCCESS); CHECK(bank.thresholds.version == 1U);
    for (const auto value : bank.thresholds.white_us) CHECK(value == 350U);
    SR_CHECK(rig.firstStop()); SR_CHECK(rig.next()); SR_CHECK(rig.pending()); SR_CHECK(rig.next());
    CHECK(rig.owner.report().service_only); CHECK(rig.owner.decisionInput().line.use == core::LineUse::CALIBRATION);
    CHECK(rig.owner.decisionInput().line.threshold_version == 0U);
    SR_CHECK(rig.select(1U)); SR_CHECK(rig.request(countdown::Service::QTR_CAL));
    const auto& after = rig.owner.report().calibration;
    CHECK(after.phase == bank.phase); CHECK(after.reason == bank.reason);
    CHECK(after.samples == bank.samples); CHECK(after.capture_started_us == bank.capture_started_us);
    CHECK(after.completed_us == bank.completed_us); CHECK(after.last_source_us == bank.last_source_us);
    CHECK(after.last_sequence == bank.last_sequence); CHECK(after.thresholds.version == 1U);
    for (unsigned i = 0U; i < 4U; ++i) {
        CHECK(after.thresholds.white_us[i] == bank.thresholds.white_us[i]);
        CHECK(after.sensors[i].white_count == bank.sensors[i].white_count);
        CHECK(after.sensors[i].black_count == bank.sensors[i].black_count);
    }
    CHECK(rig.owner.report().service_action.status == app::ServiceActionStatus::UNAVAILABLE);
}

TEST_CASE("B13 D103 SENSOR_VIEW contains fresh opponents and explicitly unavailable line pixels") {
    Rig rig; SR_CHECK(rig.reset()); rig.fake.opponent_mask = 0x7aU; SR_CHECK(rig.select(0U));
    SR_CHECK(rig.run(5U)); const auto sample = ui::displaySample(rig.owner.decisionInput(), rig.robot());
    CHECK(sample.opponents_available); CHECK_FALSE(sample.lines_available);
    CHECK((sample.opponent_mask & 2U) != 0U); CHECK(rig.fake.displayed.pixels[1U * 13U + 0U] == 3U);
    CHECK(rig.fake.displayed.pixels[1U * 13U + 8U] == 3U);
    CHECK(rig.owner.report().service_action.status == app::ServiceActionStatus::NONE);
}

TEST_CASE("B3 B15 D103 second real STOP gets one CONTROL absent tail then permanent passivity") {
    Rig rig; SR_CHECK(rig.reset(true)); SR_CHECK(rig.run(40U)); SR_CHECK(rig.firstStop());
    const auto first = rig.robot().token; SR_CHECK(rig.next()); CHECK(rig.robot().token == first + 1U);
    CHECK(rig.owner.decisionInput().line.use == core::LineUse::CONTROL);
    CHECK(rig.owner.decisionInput().line.presence == core::LinePresence::ABSENT);
    CHECK(rig.owner.report().phase == app::RuntimePhase::STOPPED);
    CHECK(rig.owner.report().service_only); CHECK_FALSE(rig.owner.report().service_reset_pending);
    const auto calls = rig.fake.count, clocks = rig.fake.clocks;
    for (unsigned i = 0U; i < 1100U; ++i) CHECK_FALSE(rig.next());
    CHECK(rig.fake.count == calls); CHECK(rig.fake.clocks == clocks); inhibited(rig);
}

TEST_CASE("B0 B13 D103 complete gesture and pending age naturally cross uint32 clock wrap") {
    Rig rig; rig.fake.now = 0xffe00000U; SR_CHECK(rig.stopped()); SR_CHECK(rig.pending());
    SR_CHECK(rig.next()); CHECK(rig.owner.report().service_only);
    CHECK(rig.owner.transaction().report().timing_valid); CHECK(rig.fake.now < 0xffe00000U);
    inhibited(rig);
}

TEST_CASE("B13 B15 D103 real GO STOP service reset and genuine LOG_DUMP retain complete saved CSV") {
    Rig rig; SR_CHECK(rig.stopped(true));
    const auto& recording = rig.owner.transaction().recording();
    CHECK(recording.phase() == recorder::AttemptPhase::SEALED); CHECK(recording.summary().go_seen);
    CHECK_FALSE(recording.summary().final_frame_missing); CHECK_FALSE(recording.incomplete());
    std::string f, e, s; SR_CHECK(csv(recording, f, e, s));
    SR_CHECK(rig.pending()); SR_CHECK(rig.next()); SR_CHECK(rig.select(3U));
    SR_CHECK(rig.request(countdown::Service::LOG_DUMP)); const auto token = rig.robot().token;
    SR_CHECK(rig.finishDump()); CHECK(rig.owner.report().dump.session == token);
    CHECK(rig.owner.report().dump.epoch == recording.summary().epoch_token);
    CHECK(rig.owner.report().dump.bytes == rig.sink.bytes.size()); CHECK(rig.sink.cancels == 0U);
    std::string f2, e2, s2; SR_CHECK(csv(recording, f2, e2, s2));
    CHECK(f == f2); CHECK(e == e2); CHECK(s == s2); inhibited(rig);
    for (const auto& call : rig.sink.calls) if (call.kind == app_dump_test::Kind::WRITE) {
        CHECK(call.transaction == app::Phase::DECIDED); CHECK(call.state == core::State::IDLE);
        CHECK(call.consumed); CHECK(call.applied_valid); CHECK_FALSE(call.enabled);
        CHECK(call.left == 0.0F); CHECK(call.right == 0.0F);
    }
}

TEST_CASE("B13 B15 D103 unavailable native dump owner stays poisoned after logical service reset") {
    Rig rig; rig.sink.setup = recorder::dump::NativeStatus::POISONED;
    SR_CHECK(rig.reset(true)); SR_CHECK(rig.select(3U)); SR_CHECK(rig.request(countdown::Service::LOG_DUMP));
    CHECK(rig.owner.report().dump_setup == recorder::dump::NativeStatus::POISONED);
    CHECK(rig.owner.report().dump.phase == recorder::dump::Phase::REFUSED);
    CHECK(rig.sink.begins == 1U); CHECK(rig.sink.readies == 0U); CHECK(rig.sink.writes == 0U);
}

TEST_CASE("B3 B15 D103 failed actual service inhibition cancels active transport once") {
    Rig rig; SR_CHECK(rig.reset(true)); SR_CHECK(rig.select(3U));
    SR_CHECK(rig.request(countdown::Service::LOG_DUMP));
    SR_CHECK(rig.owner.report().dump.phase == recorder::dump::Phase::ACTIVE);
    const auto writes = rig.sink.writes, ready = rig.sink.readies;
    rig.fake.reject_enable = true; CHECK_FALSE(rig.next());
    CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
    CHECK(rig.owner.report().dump.phase == recorder::dump::Phase::CANCELLED);
    CHECK(rig.sink.writes == writes); CHECK(rig.sink.readies == ready); CHECK(rig.sink.cancels == 1U);
    CHECK_FALSE(rig.next()); rig.owner.abort(); CHECK(rig.sink.cancels == 1U);
}
#endif

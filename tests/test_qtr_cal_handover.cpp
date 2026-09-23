// Checks D089 raw-only Robot preparation and safe classified handover.
// Uses actual adapter, menu requests and calibration bank through public APIs.
// Host synthetic streams test ownership and timing without native hardware.
#include "doctest.h"
#include "fixtures/qtr_cal_fixture.h"

using namespace qtr_cal_test;

TEST_CASE("B13 D089 boot ambiguity uses actual raw mode without fabricating black") {
    Pipeline p;
    p.now += 2000U;
    p.snapshot = frame(p.now - 1700U, ++p.sequence, 299U, 302U);
    fsm::RobotInput classified;
    CHECK(line_qtr::applySnapshot(classified, p.snapshot) == line_qtr::Qualification::AMBIGUOUS);
    p.apply();
    CHECK(p.result.contract_faults == 0U);
    CHECK(p.result.outputs.ui_state == core::State::IDLE);
    CHECK(p.result.line_raw_mode);
    CHECK(p.result.line_calibration_hold);
    CHECK_FALSE(p.result.line_available);
    CHECK_FALSE(p.result.line_updated);
    CHECK(p.result.line_mask == 0U);
    CHECK(p.writes.enabled == 0U);
    CHECK(p.writes.nonzero == 0U);
    p.tick(core::ButtonLevel::NONE, 100000000U);
    CHECK(p.result.contract_faults == 0U);
    CHECK(p.result.line_calibration_hold);
}

TEST_CASE("B13 D089 genuine eight menu requests feed actual calibration atomically") {
    Pipeline p;
    p.selectCalibration();
    QTR_REQUIRE(p.result.menu.selection.service_menu);
    QTR_REQUIRE(p.result.menu.selection.service == countdown::Service::QTR_CAL);
    for (unsigned stage = 0U; stage < 8U; ++stage) {
        p.captureStage(stage);
        CHECK(p.requests == stage + 1U);
        CHECK(p.result.contract_faults == 0U);
        CHECK(p.result.line_raw_mode);
        CHECK_FALSE(p.result.outputs.motors_enabled);
        CHECK(p.report.phase == (stage == 7U ? qtr_cal::Phase::SUCCESS : qtr_cal::Phase::WAITING));
        CHECK(p.calibration.thresholds().version == (stage == 7U ? 1U : 0U));
    }
    CHECK(p.writes.nonzero == 0U);
    CHECK(p.writes.enabled == 0U);
    for (const auto value : p.calibration.thresholds().white_us) CHECK(value == 500U);
}

TEST_CASE("B4 B13 D089 cached reclassification cannot adopt version or release hold") {
    Pipeline p;
    p.completeCalibration();
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::SUCCESS);
    const auto captured = p.snapshot;
    p.raw = false;
    p.now += 1000U;
    p.snapshot = captured;
    p.apply();
    CHECK(p.result.contract_faults == 0U);
    CHECK(p.result.line_threshold_version == 0U);
    CHECK(p.result.line_calibration_hold);
    CHECK_FALSE(p.result.line_available);
    for (std::uint32_t i = 0U; i < config::QTR_CONFIRM_TICKS; ++i) {
        p.tick(core::ButtonLevel::START, 2000U, true);
        CHECK(p.result.contract_faults == 0U);
        CHECK(p.result.line_threshold_version == 1U);
        CHECK(p.result.line_calibration_hold == (i + 1U < config::QTR_CONFIRM_TICKS));
        CHECK_FALSE(p.result.lifecycle.gate.start_release);
        CHECK_FALSE(p.result.outputs.motors_enabled);
    }
    CHECK(p.result.line_start_rearming);
    p.hold(core::ButtonLevel::START, 24000U, true);
    CHECK(p.result.line_start_rearming);
    p.hold(core::ButtonLevel::NONE, 24000U, true);
    CHECK_FALSE(p.result.line_start_rearming);
    CHECK_FALSE(p.result.lifecycle.gate.start_release);
}

TEST_CASE("B4 D089 later classifier uses committed values and distinct confirmation only") {
    Pipeline p;
    p.completeCalibration();
    p.requalify();
    QTR_REQUIRE_FALSE(p.result.line_calibration_hold);
    for (std::uint32_t n = 0U; n < config::QTR_CONFIRM_TICKS; ++n)
        p.tick(core::ButtonLevel::NONE, 2000U, true, 397U, 400U);
    CHECK(p.result.line_mask == 15U);
    CHECK(p.result.line_threshold_version == 1U);
    const auto same = p.snapshot;
    p.now += 1000U;
    p.snapshot = same;
    p.apply();
    CHECK_FALSE(p.result.line_updated);
    CHECK(p.result.line_mask == 15U);
    p.input.line.threshold_version = 2U;
    p.input.t_us = p.writes.now = p.now + 1U;
    const auto forged = p.robot.step(p.input);
    CHECK((forged.contract_faults & fsm::LINE_CONTRACT) != 0U);
    CHECK_FALSE(forged.outputs.motors_enabled);
}

TEST_CASE("B13 D089 raw invalidity and active STOP cancel a genuine collecting run") {
    for (bool stop : {false, true}) {
        Pipeline p;
        p.selectCalibration();
        p.requestStage();
        QTR_REQUIRE(p.report.phase == qtr_cal::Phase::COLLECTING);
        if (stop) {
            p.input.stop_requested = true;
            p.tick();
            CHECK(p.result.lifecycle.gate.phase == countdown::Phase::STOPPED);
        } else {
            p.now += 2000U;
            p.snapshot = frame(p.now - 1700U, ++p.sequence,197U,200U);
            ++p.snapshot.pad[1].upper_us;
            p.apply();
            CHECK((p.result.contract_faults & fsm::LINE_CONTRACT) != 0U);
        }
        CHECK(p.report.phase == qtr_cal::Phase::CANCELLED);
        CHECK(p.calibration.thresholds().version == 0U);
        CHECK_FALSE(p.writes.en);
        CHECK(p.writes.nonzero == 0U);
    }
}

TEST_CASE("B13 D089 raw handover cannot revive a pre-transition source after wrap") {
    Pipeline p;
    p.tick(core::ButtonLevel::NONE, 2000U, true);
    const auto old = p.snapshot;
    for (unsigned i = 0U; i < 4U; ++i) p.tick(core::ButtonLevel::NONE, 1000000000U);
    p.raw = false;
    p.now = old.started_us + 1700U;
    p.snapshot = old;
    p.apply();
    CHECK_FALSE(p.result.line_available);
    CHECK(p.result.line_calibration_hold);
    CHECK_FALSE(p.result.outputs.motors_enabled);
}

TEST_CASE("B13 D089 explicit fresh neutral rearming is independent of retained buttons") {
    Pipeline p;
    p.explicit_buttons = true;
    p.completeCalibration();
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::SUCCESS);
    p.requalify();
    QTR_REQUIRE(p.result.line_start_rearming);
    const auto retained = p.input.buttons;
    for (unsigned i = 0U; i < 4U; ++i) {
        p.now += 1000U;
        p.snapshot = {};
        p.explicit_buttons = false;
        p.input.buttons = retained;
        p.apply();
        CHECK(p.result.line_start_rearming);
        CHECK_FALSE(p.result.button_updated);
    }
    p.explicit_buttons = true;
    p.tick(core::ButtonLevel::NONE, 1000U, true);
    CHECK(p.result.contract_faults == 0U);
    p.hold(core::ButtonLevel::NONE, 24000U, true);
    CHECK_FALSE(p.result.line_start_rearming);
}

TEST_CASE("B13 D089 Robot unseen old source cannot cross a full-wrap absence") {
    for (bool control : {false, true}) {
        Pipeline p;
        p.tick(core::ButtonLevel::NONE, 2000U, true);
        const auto old_start = p.snapshot.started_us;
        for (unsigned i = 0U; i < 4U; ++i) {
            p.tick(core::ButtonLevel::NONE, 1000000000U);
            CHECK(p.result.contract_faults == 0U);
        }
        p.raw = !control;
        p.now = old_start + 4000U + 1700U;
        p.snapshot = frame(old_start + 4000U, ++p.sequence);
        p.apply();
        CHECK((p.result.contract_faults & fsm::LINE_CONTRACT) != 0U);
        CHECK_FALSE(p.result.outputs.motors_enabled);
        CHECK(p.result.line_threshold_version == 0U);
    }
}

TEST_CASE("B13 D089 Robot source and handover eras enforce exact half-range bounds") {
    for (bool history : {false, true}) {
        for (std::uint32_t age : {0x7FFFFFFFU, 0x80000000U}) {
            Pipeline p;
            p.tick(core::ButtonLevel::NONE, 2000U, history);
            p.raw = false;
            const auto initial_age = history ? 1700U : 0U;
            p.tick(core::ButtonLevel::NONE, age - initial_age - 1U);
            CHECK(p.result.contract_faults == 0U);
            p.tick(core::ButtonLevel::NONE, 1U, true);
            CHECK(((p.result.contract_faults & fsm::LINE_CONTRACT) != 0U) == (age == 0x80000000U));
            CHECK_FALSE(p.result.outputs.motors_enabled);
        }
    }
}

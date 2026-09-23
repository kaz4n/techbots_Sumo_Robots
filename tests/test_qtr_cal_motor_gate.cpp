// Exercises D089 calibration through actual inhibited and enabled MotorGate writes.
// Host callbacks record commands without connecting to a board or motor.
// The enabled host target proves the new bank cannot bypass fresh START/full hold.
#include "doctest.h"
#include "fixtures/qtr_cal_fixture.h"

TEST_CASE("B3 B4 B13 D089 actual calibration bank handover retains full motor hold") {
    qtr_cal_test::Pipeline p;
    p.completeCalibration();
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::SUCCESS);
    QTR_REQUIRE(p.requests == 8U);
    CHECK(p.writes.enabled == 0U);
    CHECK(p.writes.nonzero == 0U);
    p.requalify();
    QTR_REQUIRE_FALSE(p.result.line_calibration_hold);
    p.leaveServiceMenu();
    QTR_REQUIRE_FALSE(p.result.menu.selection.service_menu);
    QTR_REQUIRE_FALSE(p.result.line_start_rearming);
    p.hold(core::ButtonLevel::START, 24000U, true);
    p.hold(core::ButtonLevel::NONE, 24000U, true);
    QTR_REQUIRE(p.result.lifecycle.gate.phase == countdown::Phase::HOLDING);
    const auto deadline = p.result.lifecycle.gate.release_us +
        (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
    while (deadline - p.now > 2000U) p.tick(core::ButtonLevel::NONE, 2000U, true);
    if (deadline - p.now > 1U) p.tick(core::ButtonLevel::NONE, deadline - p.now - 1U);
    CHECK_FALSE(p.result.outputs.motors_enabled);
    CHECK(p.writes.enabled == 0U);
    CHECK(p.writes.nonzero == 0U);
    p.tick(core::ButtonLevel::NONE, 1U);
    CHECK(p.result.lifecycle.gate.go);
    CHECK(p.result.contract_faults == 0U);
    p.hold(core::ButtonLevel::NONE, 6000U, true);
#if MOTORS_ALLOWED
    CHECK(p.writes.enabled > 0U);
    CHECK(p.writes.nonzero > 0U);
#else
    CHECK(p.writes.enabled == 0U);
    CHECK(p.writes.nonzero == 0U);
#endif
    const auto before = p.writes.nonzero;
    p.input.stop_requested = true;
    p.tick(core::ButtonLevel::NONE, 2000U, true);
    CHECK_FALSE(p.writes.en);
    CHECK(p.writes.nonzero == before);
    CHECK(p.result.outputs.ui_state == core::State::STOPPED);
}

// Probes the explicitly selected D131 extension to D129 timing exclusions.
// Distinguishes first arm eligibility from an already armed deferred-white trial.
// Private actual-Gate tests require immediate exclusion and prohibit later retry.
#include "p4_timing_fixture.h"

namespace {
void excludedAndNeverRetried(p4_time::Rig& rig, const fsm::RobotResult& white) {
    CHECK(white.outputs.ui_state == core::State::ATTACK);
    CHECK(white.line_mask == 1U);
    CHECK(p4_time::count(white, p4_time::Detail::INTERRUPTED_EDGE) == (MOTORS_ALLOWED ? 1U : 0U));
    rig.white(0U); rig.step(rig.now + 1000U);
    rig.opponent(0U); const auto first_loss = rig.step(rig.now + 1000U);
    const auto brake = rig.step(rig.now + 30000U);
    const auto receipt = rig.step(rig.now + 1000U);
    for (const auto& r : {first_loss, brake, receipt}) {
        CHECK(p4_time::count(r, p4_time::Detail::LOSS_READ_START) == 0U);
        CHECK(p4_time::count(r, p4_time::Detail::LOSS_BRAKE_DECISION) == 0U);
        CHECK(p4_time::count(r, p4_time::Detail::LOSS_ZERO_APPLIED) == 0U);
    }
}
}

TEST_CASE("Private D131 policy extension first arm eligible deferredwhite excludes immediately") {
    if (config::EDGE_PUSH_THROUGH_MS == 0U) return;
    p4_time::Rig rig(true); rig.opponent(10U); const auto go = rig.go();
    APP_REQUIRE(rig.step(go + 1000U).outputs.ui_state == core::State::TRACK);
    APP_REQUIRE(rig.step(go + 2000U).outputs.ui_state == core::State::TRACK);
    APP_REQUIRE(rig.step(go + 3000U).outputs.ui_state == core::State::ATTACK);
    rig.white(1U);
    excludedAndNeverRetried(rig, rig.step(go + 4000U));
}

TEST_CASE("Private D131 policy extension already armed deferredwhite closes sole trial") {
    if (config::EDGE_PUSH_THROUGH_MS == 0U) return;
    p4_time::Rig rig(true); rig.approach(0U, 10U); rig.white(1U);
    excludedAndNeverRetried(rig, rig.step(rig.now + 1000U));
}

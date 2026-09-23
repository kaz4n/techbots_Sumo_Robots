// Probes D089 raw admission and START handover through the actual Robot.
// Supplies synthetic evidence and acknowledged disabled/application receipts only.
// Built independently of registered suites as an implementation-side supplement.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "robot_scenario.h"

namespace {
using Button = core::ButtonLevel;
class RawRig : public robot_test::Rig {
public:
    RawRig() {
        input.line.explicit_values = true;
        input.line.use = core::LineUse::CALIBRATION;
        input.opponent_fresh = true;
        input.observations_fresh = false;
    }
    fsm::RobotResult next(Button button = Button::NONE, bool fresh = true) {
        now += 1000U;
        if (fresh && (!source_seen || now - input.line.started_us >= 2100U)) {
            input.line.presence = core::LinePresence::VALID;
            input.line.sequence = ++sequence;
            input.line.started_us = now - 100U;
            input.line.completed_us = now - 50U;
            source_seen = true;
        }
        return step(now, button);
    }
    void span(unsigned count, Button button = Button::NONE) {
        for (unsigned i = 0U; i < count; ++i) {
            const auto r = next(button);
            CHECK(r.contract_faults == 0U);
        }
    }
    void control(std::uint32_t version = 1U) {
        input.line.use = core::LineUse::CONTROL;
        input.line.threshold_version = version;
    }
    std::uint32_t now = 0U;
    std::uint32_t sequence = 0U;
    bool source_seen = false;
};
}

TEST_CASE("D089 raw START is consumed and later START receives all5100ms") {
    RawRig rig;
    rig.span(25);
    rig.span(25, Button::START);
    rig.span(25);
    CHECK(rig.last.outputs.ui_state == core::State::IDLE);
    CHECK(rig.last.line_raw_mode);
    CHECK_FALSE(rig.last.line_available);
    rig.control();
    rig.span(30, Button::START);
    CHECK(rig.last.line_available);
    CHECK(rig.last.line_start_rearming);
    CHECK_FALSE(rig.last.line_calibration_hold);
    rig.span(25);
    CHECK_FALSE(rig.last.line_start_rearming);
    CHECK(rig.last.outputs.ui_state == core::State::IDLE);
    rig.span(25, Button::START);
    rig.next();
    rig.span(19);
    CHECK(rig.last.outputs.ui_state == core::State::IDLE);
    const auto release = rig.next();
    CHECK(release.lifecycle.gate.start_release);
    const auto release_us = rig.now;
    rig.span(5099);
    robot_test::zero(rig.last);
    CHECK(rig.last.lifecycle.gate.release_us == release_us);
    CHECK(rig.next().lifecycle.gate.go);
}

TEST_CASE("D089 cached reclassification never adopts bank or qualifies line") {
    RawRig rig;
    rig.next();
    rig.control();
    const auto cached = rig.next(Button::NONE, false);
    CHECK(cached.contract_faults == 0U);
    CHECK(cached.line_calibration_hold);
    CHECK_FALSE(cached.line_available);
    CHECK(cached.line_threshold_version == 0U);
    const auto later = rig.next();
    CHECK(later.contract_faults == 0U);
    CHECK(later.line_available);
    CHECK(later.line_threshold_version == 1U);
    CHECK(later.line_start_rearming);
}

TEST_CASE("D089 BOTH stop qualification survives raw-to-control handover") {
    RawRig rig;
    rig.span(50);
    rig.span(900, Button::BOTH);
    rig.control();
    rig.span(120, Button::BOTH);
    CHECK(rig.last.outputs.ui_state == core::State::IDLE);
    const auto stop = rig.next(Button::BOTH);
    CHECK(stop.outputs.ui_state == core::State::STOPPED);
    CHECK(stop.lifecycle.gate.phase == countdown::Phase::STOPPED);
    robot_test::zero(stop);
}

TEST_CASE("D089 raw absence waits but a replay cannot resurrect after wrap") {
    RawRig rig;
    rig.next();
    const auto retained = rig.input.line;
    rig.input.line.presence = core::LinePresence::ABSENT;
    for (unsigned i = 0U; i < 4U; ++i) {
        rig.now += 0x40000000U;
        const auto absent = rig.step(rig.now);
        CHECK(absent.contract_faults == 0U);
        CHECK(absent.line_calibration_hold);
        CHECK_FALSE(absent.line_available);
    }
    rig.input.line = retained;
    rig.now += 1U;
    const auto replay = rig.step(rig.now);
    CHECK((replay.contract_faults & fsm::LINE_CONTRACT) != 0U);
    CHECK(replay.outputs.ui_state == core::State::STOPPED);
}

TEST_CASE("D089 raw entry cannot bypass a running countdown or native-invalid frame") {
    RawRig rig;
    rig.input.line.use = core::LineUse::CONTROL;
    rig.span(25);
    rig.span(25, Button::START);
    rig.span(25);
    CHECK(rig.last.outputs.ui_state == core::State::COUNTDOWN);
    rig.input.line.use = core::LineUse::CALIBRATION;
    CHECK((rig.next().contract_faults & fsm::LINE_CONTRACT) != 0U);
    RawRig invalid;
    invalid.input.line.presence = core::LinePresence::INVALID;
    CHECK((invalid.next(Button::NONE, false).contract_faults & fsm::LINE_CONTRACT) != 0U);
}

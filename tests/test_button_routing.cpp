// Exercises B3/B13 explicit button admission using D087 source-time evidence.
// Independent contract expectations distinguish new observations from retained levels.
// Host normal and sanitizer runs cover Robot gestures, continuity, faults and reset.
#include "robot_scenario.h"
#include <limits>
#include <initializer_list>

namespace {
using Button = core::ButtonLevel;
using State = core::State;
constexpr std::uint32_t AGE = config::BUTTON_SAMPLE_MAX_AGE_US;
struct ButtonsRig : robot_test::Rig {
    std::uint32_t sequence = 0U;
    core::ButtonEvidence cached;
    fsm::RobotResult fresh(std::uint32_t time, Button level = Button::NONE,
                           std::uint32_t latency = 0U) {
        cached = {};
        cached.explicit_values = true;
        cached.presence = core::ButtonPresence::VALID;
        cached.level = level;
        cached.raw = static_cast<std::uint16_t>(100U + static_cast<unsigned>(level));
        cached.sequence = sequence++;
        cached.completed_us = time - latency;
        cached.started_us = cached.completed_us - 20U;
        return evidence(time, cached);
    }
    fsm::RobotResult evidence(std::uint32_t time, const core::ButtonEvidence& value) {
        auto next = at(time);
        next.buttons = value;
        return submit(next);
    }
    fsm::RobotResult absent(std::uint32_t time) {
        core::ButtonEvidence empty;
        empty.explicit_values = true;
        return evidence(time, empty);
    }
    fsm::RobotResult run(std::uint32_t begin, std::uint32_t end,
                        Button level = Button::NONE, std::uint32_t latency = 0U) {
        for (std::uint32_t elapsed = 0U; elapsed <= end - begin; elapsed += 1000U)
            fresh(begin + elapsed, level, latency);
        return last;
    }
    std::uint32_t start(std::uint32_t base = 0U) {
        run(base, base + 30000U);
        run(base + 31000U, base + 51000U, Button::START);
        run(base + 52000U, base + 71000U);
        CHECK_FALSE(last.lifecycle.gate.start_release);
        fresh(base + 72000U);
        CHECK(last.lifecycle.gate.start_release);
        CHECK(last.contract_faults == 0U);
        return base + 72000U;
    }
};
void fault(const fsm::RobotResult& value) {
    CHECK((value.contract_faults & fsm::BUTTON_CONTRACT) != 0U);
    CHECK(value.outputs.ui_state == State::STOPPED);
    CHECK_FALSE(value.button_available);
    robot_test::zero(value);
}
}

TEST_CASE("B3 D087 explicit canonical ABSENT waits in BOOT but cannot initialize") {
    ButtonsRig rig;
    rig.input.initialization_complete = false;
    CHECK(rig.absent(0U).outputs.ui_state == State::BOOT);
    CHECK(rig.absent(10000U).contract_faults == 0U);
    rig.input.initialization_complete = true;
    fault(rig.absent(11000U));
}

TEST_CASE("B3 D087 first sequence zero publishes actual source and identity") {
    ButtonsRig rig;
    const auto out = rig.fresh(1000U, Button::NONE, 50U);
    CHECK(out.outputs.ui_state == State::IDLE);
    CHECK(out.button_available);
    CHECK(out.button_updated);
    CHECK(out.button_level == Button::NONE);
    CHECK(out.button_source_us == 930U);
    CHECK(out.button_age_us == 70U);
    CHECK(out.button_sequence == 0U);
}

TEST_CASE("B3 D087 ABSENT and exact replay preserve bounded history without refreshing it") {
    for (const bool replay : {false, true}) {
        ButtonsRig rig;
        rig.fresh(1000U);
        const auto source = rig.cached;
        const auto at_limit = replay ? rig.evidence(5980U, source) : rig.absent(5980U);
        CHECK(at_limit.button_available);
        CHECK_FALSE(at_limit.button_updated);
        CHECK(at_limit.button_age_us == AGE);
        fault(replay ? rig.evidence(5981U, source) : rig.absent(5981U));
        fault(rig.fresh(6000U));
    }
}

TEST_CASE("B3 D087 exact duplicate decision ignores changed evidence and clears pulses") {
    ButtonsRig rig;
    rig.fresh(1000U);
    auto changed = rig.cached;
    changed.presence = core::ButtonPresence::INVALID;
    const auto same = rig.evidence(1000U, changed);
    CHECK_FALSE(same.fresh);
    CHECK_FALSE(same.button_updated);
    CHECK_FALSE(same.lifecycle.gate.start_release);
    CHECK_FALSE(same.menu.selection_changed);
    CHECK(same.contract_faults == 0U);
    CHECK(same.events.count == 0U);
    CHECK(rig.fresh(2000U).contract_faults == 0U);
}

TEST_CASE("B3 D087 invalid explicit shape always inhibits and reset alone recovers") {
    for (unsigned mutation = 0U; mutation < 12U; ++mutation) {
        CAPTURE(mutation);
        ButtonsRig rig;
        rig.fresh(1000U);
        auto bad = rig.cached;
        ++bad.sequence;
        bad.started_us = 1980U;
        bad.completed_us = 2000U;
        if (mutation == 0U) bad.contract_valid = false;
        if (mutation == 1U) bad.presence = core::ButtonPresence::INVALID;
        if (mutation == 2U) bad.presence = static_cast<core::ButtonPresence>(0U);
        if (mutation == 3U) bad.level = static_cast<Button>(4U);
        if (mutation == 4U) bad.raw = 16384U;
        if (mutation == 5U) bad.started_us = 1900U;
        if (mutation == 6U) bad.completed_us = 2001U;
        if (mutation == 7U) bad.started_us = 2001U;
        if (mutation == 8U) bad.explicit_values = false;
        if (mutation == 9U) bad.presence = core::ButtonPresence::ABSENT;
        if (mutation == 10U) bad.completed_us = 1900U;
        if (mutation == 11U) bad.started_us = 2000U - AGE - 1U;
        fault(rig.evidence(2000U, bad));
        fault(rig.fresh(3000U));
        rig.reset();
        CHECK(rig.fresh(4000U).contract_faults == 0U);
        CHECK_FALSE(rig.last.lifecycle.gate.start_release);
    }
}

TEST_CASE("B3 D087 changing any payload under the same sequence is a contract fault") {
    for (unsigned mutation = 0U; mutation < 4U; ++mutation) {
        ButtonsRig rig;
        rig.fresh(1000U);
        auto bad = rig.cached;
        if (mutation == 0U) ++bad.raw;
        if (mutation == 1U) bad.level = Button::START;
        if (mutation == 2U) ++bad.started_us;
        if (mutation == 3U) --bad.completed_us;
        fault(rig.evidence(2000U, bad));
    }
}

TEST_CASE("B3 D087 source continuity rejects stale reversed overlapping and half-range identities") {
    for (unsigned mutation = 0U; mutation < 7U; ++mutation) {
        CAPTURE(mutation);
        ButtonsRig rig;
        rig.sequence = 12U;
        rig.fresh(1000U);
        auto bad = rig.cached;
        ++bad.sequence;
        bad.started_us = 1980U;
        bad.completed_us = 2000U;
        if (mutation == 0U) bad.sequence -= 2U;
        if (mutation == 1U) bad.sequence += 0x7fffffffU;
        if (mutation == 2U) bad.completed_us = 1000U;
        if (mutation == 3U) { bad.started_us = 999U; bad.completed_us = 1010U; }
        if (mutation == 4U) { bad.started_us = 6000U; bad.completed_us = 6020U; }
        if (mutation == 5U) { bad.started_us = 998U; bad.completed_us = 999U; }
        if (mutation == 6U) { bad.started_us += 0x80000000U; bad.completed_us += 0x80000000U; }
        fault(rig.evidence(mutation == 4U ? 6020U : 2000U, bad));
    }
}

TEST_CASE("B3 D087 a new bounded sample can replace old history before expiry evaluation") {
    ButtonsRig rig;
    rig.fresh(1000U);
    CHECK(rig.fresh(6000U).contract_faults == 0U);
    CHECK(rig.last.button_updated);
    CHECK(rig.last.button_age_us == 20U);
    fault(rig.fresh(11001U));
}

TEST_CASE("B3 D087 consecutive acquisition may start at previous completion") {
    ButtonsRig rig;
    rig.fresh(1000U);
    auto touching = rig.cached;
    ++touching.sequence;
    touching.started_us = 1000U;
    touching.completed_us = 1020U;
    CHECK(rig.evidence(1020U, touching).contract_faults == 0U);
}

TEST_CASE("B3 D087 initial age boundary and skipped forward sequence preserve exact limits") {
    for (const auto age : {AGE, AGE + 1U}) {
        ButtonsRig rig;
        const auto out = rig.fresh(10000U, Button::NONE, age - 20U);
        if (age == AGE) {
            CHECK(out.contract_faults == 0U);
            CHECK(out.button_available);
            CHECK(out.button_age_us == AGE);
        } else fault(out);
    }
    ButtonsRig rig;
    rig.fresh(1000U);
    rig.sequence = 0x7fffffffU;
    CHECK(rig.fresh(2000U).contract_faults == 0U);
    CHECK(rig.last.button_sequence == 0x7fffffffU);
}

TEST_CASE("B3 D087 source decision and sequence wraps remain usable within the bound") {
    ButtonsRig rig;
    rig.sequence = std::numeric_limits<std::uint32_t>::max();
    rig.fresh(0xfffffff0U);
    const auto out = rig.fresh(984U);
    CHECK(out.contract_faults == 0U);
    CHECK(out.button_sequence == 0U);
    CHECK(out.button_age_us == 20U);
    CHECK(out.button_updated);
}

TEST_CASE("B3 D087 backward and half-range decision time cannot revive cached data") {
    for (const auto delta : {0x80000000U, 0xffffffffU, 0x7fffffffU}) {
        ButtonsRig rig;
        rig.fresh(1000U);
        fault(rig.absent(1000U + delta));
        fault(rig.evidence(2000U, rig.cached));
    }
}

TEST_CASE("B3 D087 legacy explicit mixing faults in either direction until reset") {
    ButtonsRig rig;
    CHECK(rig.step(0U).contract_faults == 0U);
    fault(rig.fresh(1000U));
    rig.reset();
    CHECK(rig.fresh(2000U).contract_faults == 0U);
    fault(rig.step(3000U));
}

TEST_CASE("B3 D087 boot-held START and insufficient neutral cannot manufacture release") {
    ButtonsRig rig;
    rig.run(0U, 50000U, Button::START);
    rig.run(51000U, 70000U);
    rig.run(71000U, 100000U, Button::START);
    rig.run(101000U, 131000U);
    CHECK_FALSE(rig.last.lifecycle.gate.start_release);
    CHECK(rig.last.outputs.ui_state == State::IDLE);
    rig.run(132000U, 152000U, Button::START);
    rig.run(153000U, 173000U);
    CHECK(rig.last.lifecycle.gate.start_release);
    CHECK(rig.last.lifecycle.gate.release_us == 173000U);
}

TEST_CASE("B3 D087 source release qualifies once and full hold advances on ABSENT") {
    ButtonsRig rig;
    const auto anchor = rig.start(0xffff0000U);
    CHECK(rig.last.lifecycle.gate.release_us == anchor);
    rig.run(anchor + 1000U, anchor + 5099000U);
    CHECK_FALSE(rig.last.lifecycle.gate.motion_permitted);
    const auto go = rig.absent(anchor + 5100000U);
    CHECK(go.lifecycle.gate.go);
    CHECK(go.lifecycle.gate.motion_permitted);
    CHECK(go.lifecycle.services.finished);
    CHECK(go.contract_faults == 0U);
    CHECK_FALSE(go.button_updated);
    CHECK_FALSE(rig.absent(anchor + 5101000U).lifecycle.gate.go);
}

TEST_CASE("B3 D087 release qualification is anchored to decision not delayed source") {
    ButtonsRig rig;
    rig.run(10000U, 40000U, Button::NONE, 2000U);
    rig.run(41000U, 61000U, Button::START, 2000U);
    rig.run(62000U, 82000U, Button::NONE, 2000U);
    CHECK(rig.last.lifecycle.gate.start_release);
    CHECK(rig.last.lifecycle.gate.release_us == 82000U);
    rig.run(83000U, 5180000U, Button::NONE, 2000U);
    CHECK_FALSE(rig.last.lifecycle.gate.motion_permitted);
    rig.fresh(5181000U, Button::NONE, 2000U);
    CHECK_FALSE(rig.last.lifecycle.gate.motion_permitted);
    CHECK(rig.absent(5182000U).lifecycle.gate.go);
}

TEST_CASE("B3 D087 MODE cancels countdown only on a fresh qualified observation") {
    ButtonsRig rig;
    const auto anchor = rig.start();
    rig.run(anchor + 1000U, anchor + 20000U, Button::MODE);
    CHECK(rig.absent(anchor + 21000U).outputs.ui_state == State::COUNTDOWN);
    CHECK(rig.fresh(anchor + 22000U, Button::MODE).outputs.ui_state == State::IDLE);
    CHECK_FALSE(rig.last.menu.selection_changed);
}

TEST_CASE("B13 D087 MODE cycles six modes and START captures the selected mode") {
    ButtonsRig rig;
    rig.run(0U, 30000U);
    std::uint32_t now = 31000U;
    for (unsigned mode = 2U; mode <= 7U; ++mode) {
        rig.run(now, now + 20000U, Button::MODE);
        rig.run(now + 21000U, now + 41000U);
        CHECK(rig.last.menu.selection_changed);
        CHECK(static_cast<unsigned>(rig.last.menu.selection.mode) == ((mode - 1U) % 6U) + 1U);
        now += 42000U;
    }
    rig.run(now, now + 20000U, Button::START);
    rig.run(now + 21000U, now + 41000U);
    CHECK(rig.last.lifecycle.gate.start_release);
    CHECK(rig.last.running_mode == core::Mode::SIDESTEP_R);
}

TEST_CASE("B13 D087 service menu cycles all intents and consumes START without match start") {
    for (unsigned service = 1U; service <= 4U; ++service) {
        ButtonsRig rig;
        rig.run(0U, 30000U);
        rig.run(31000U, 1051000U, Button::MODE);
        CHECK(rig.last.menu.menu_toggled);
        CHECK(rig.last.menu.selection.service_menu);
        rig.run(1052000U, 1072000U);
        std::uint32_t now = 1073000U;
        for (unsigned item = 1U; item < service; ++item) {
            rig.run(now, now + 20000U, Button::MODE);
            rig.run(now + 21000U, now + 41000U);
            now += 42000U;
        }
        rig.run(now, now + 20000U, Button::START);
        rig.run(now + 21000U, now + 41000U);
        CHECK(rig.last.menu.request == static_cast<countdown::Service>(service));
        CHECK(rig.last.menu.request_unavailable == (service == 3U));
        CHECK_FALSE(rig.last.lifecycle.gate.start_release);
        CHECK_FALSE(rig.last.lifecycle.services.active);
        CHECK(rig.last.outputs.ui_state == State::IDLE);
        CHECK(rig.absent(now + 42000U).menu.request == countdown::Service::NONE);
    }
}

TEST_CASE("B13 D087 boot-held BOTH stops after full decision anchored hold and reset clears") {
    ButtonsRig rig;
    rig.input.initialization_complete = false;
    rig.run(10000U, 1031000U, Button::BOTH, 2000U);
    CHECK(rig.last.outputs.ui_state == State::BOOT);
    CHECK(rig.fresh(1032000U, Button::BOTH, 2000U).outputs.ui_state == State::STOPPED);
    rig.fresh(1033000U);
    CHECK(rig.last.outputs.ui_state == State::STOPPED);
    rig.reset();
    rig.input.initialization_complete = true;
    CHECK(rig.fresh(1034000U).outputs.ui_state == State::IDLE);
}

TEST_CASE("B13 D087 fresh release on BOTH hold deadline cancels unfinished STOP") {
    ButtonsRig rig;
    rig.run(0U, 1019000U, Button::BOTH);
    CHECK(rig.last.outputs.ui_state == State::IDLE);
    CHECK(rig.fresh(1020000U).outputs.ui_state == State::IDLE);
    CHECK(rig.fresh(1021000U).contract_faults == 0U);
}

TEST_CASE("B13 D087 qualified external STOP runs on no-new data and does not auto recover") {
    ButtonsRig rig;
    rig.fresh(1000U);
    rig.input.stop_requested = true;
    CHECK(rig.absent(2000U).outputs.ui_state == State::STOPPED);
    rig.input.stop_requested = false;
    CHECK(rig.fresh(3000U).outputs.ui_state == State::STOPPED);
}

TEST_CASE("B3 D087 valid button history never suppresses unrelated receipt fault") {
    ButtonsRig rig;
    rig.fresh(1000U);
    auto input = rig.at(2000U);
    input.buttons = rig.cached;
    input.previous.applied_valid = false;
    const auto out = rig.submit(input);
    CHECK((out.contract_faults & fsm::APPLICATION_CONTRACT) != 0U);
    robot_test::zero(out);
}

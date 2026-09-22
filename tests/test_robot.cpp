// Exercises the production Robot against B0-B13 and the D-060 transaction contract.
// Uses explicit synthetic acquisition/application receipts without an alternate arbiter.
// Independent expectations cover routing, actual-duty dependencies and reset-only faults.
#include "robot_scenario.h"
#include <array>
#include <limits>

using namespace robot_test;

namespace {
std::uint32_t finishReflank(Rig& rig, std::uint32_t start, unsigned direction) {
    const auto swing = rig.step(start + 150000U);
    CHECK(swing.outputs.ui_state == State::REFLANK);
    CHECK(event(swing, core::Event::REFLANK_PHASE, 2).value == direction);
    CHECK(rig.step(start + 850000U).outputs.ui_state == State::REFLANK);
    CHECK(rig.step(start + 1250000U).outputs.ui_state == State::TRACK);
    CHECK(rig.step(start + 1251000U).outputs.ui_state == State::TRACK);
    rig.input.ax_g = 2.0F;
    CHECK(rig.step(start + 1252000U).outputs.ui_state == State::ATTACK);
    CHECK(rig.last.contact);
    rig.input.ax_g = 0.0F;
    rig.step(start + 1302000U);
    CHECK(rig.last.outputs.duty_l == doctest::Approx(1.0F));
    CHECK(rig.last.outputs.duty_r == doctest::Approx(1.0F));
    return start + 1302000U;
}
} // namespace

TEST_CASE("B0 D060 Robot waits in BOOT and latches initialization") {
    Rig rig;
    rig.input.initialization_complete = false;
    rig.input.observations_fresh = false;
    rig.input.vbat_valid = false;
    auto result = rig.step(0U);
    CHECK(result.outputs.ui_state == State::BOOT);
    zero(result);
    CHECK(result.contract_faults == 0U);
    rig.input.initialization_complete = true;
    rig.input.observations_fresh = true;
    rig.input.vbat_valid = true;
    result = rig.step(1000U);
    CHECK(result.outputs.ui_state == State::IDLE);
    rig.input.initialization_complete = false;
    result = rig.step(2000U);
    CHECK(result.outputs.ui_state == State::IDLE);
    zero(result);
}

TEST_CASE("B0 D057 Robot consumes a BOOT-entry START without replay") {
    Rig rig;
    rig.input.initialization_complete = false;
    rig.step(0U);
    rig.step(21000U);
    rig.step(22000U, Button::START);
    rig.step(42000U, Button::START);
    rig.step(43000U);
    rig.input.initialization_complete = true;
    const auto initial = rig.step(63000U);
    CHECK(initial.outputs.ui_state == State::IDLE);
    CHECK_FALSE(initial.lifecycle.gate.start_release);
    CHECK(count(initial, core::Event::START_RELEASE) == 0U);
    CHECK_FALSE(rig.step(64000U).lifecycle.gate.start_release);
    release(rig, 84000U);
}

TEST_CASE("B13 D060 Robot captures each of six modes only at accepted release") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        CAPTURE(mode);
        Rig rig;
        const auto selected = select(rig, static_cast<Mode>(mode));
        CHECK(rig.last.running_mode == Mode::SIDESTEP_R);
        const auto anchor = release(rig, selected);
        CHECK(rig.last.running_mode == static_cast<Mode>(mode));
        rig.step(anchor + 1500000U);
        rig.step(anchor + 1501000U);
        rig.step(anchor + 4500000U);
        const auto result = rig.step(anchor + 5100000U);
        CHECK(result.lifecycle.gate.go);
        CHECK(result.outputs.ui_state == State::OPENER);
        CHECK(result.running_mode == static_cast<Mode>(mode));
        CHECK(result.contract_faults == 0U);
        if (mode == 6U) zero(result, false);
        bounded(result);
    }
}

TEST_CASE("B13 D058 Robot service intents never enter countdown or calibrate") {
    for (unsigned service = 1U; service <= 4U; ++service) {
        CAPTURE(service);
        Rig rig;
        auto time = longMode(rig, idle(rig) + 1U);
        for (unsigned selected = 1U; selected < service; ++selected)
            time = shortMode(rig, time + 1U);
        rig.input.previous_bias_dps = std::numeric_limits<float>::quiet_NaN();
        rig.step(time + 1000U, Button::START);
        rig.step(time + 21000U, Button::START);
        rig.step(time + 22000U);
        const auto result = rig.step(time + 42000U);
        CHECK(result.menu.request == static_cast<countdown::Service>(service));
        CHECK(result.menu.request_unavailable == (service == 3U));
        CHECK(result.outputs.ui_state == State::IDLE);
        CHECK_FALSE(result.lifecycle.gate.start_release);
        CHECK_FALSE(result.lifecycle.heading_reset_requested);
        CHECK_FALSE(result.lifecycle.services.active);
        CHECK_FALSE(result.lifecycle.service_start_failed);
        CHECK(result.lifecycle.services.calibration_samples == 0U);
        CHECK(count(result, core::Event::START_RELEASE) == 0U);
        CHECK(result.contract_faults == 0U);
        zero(result);
        CHECK(rig.step(time + 43000U).menu.request == countdown::Service::NONE);
    }
}

TEST_CASE("B5 B9 Robot needs three current centered observations after DIRECT exit") {
    Rig rig;
    rig.opponent(2U);
    const auto time = go(rig, Mode::DIRECT);
    CHECK(rig.last.outputs.ui_state == State::TRACK);
    CHECK_FALSE(rig.last.contact);
    CHECK(rig.step(time + 1000U).outputs.ui_state == State::TRACK);
    const auto third = rig.step(time + 2000U);
    CHECK(third.outputs.ui_state == State::ATTACK);
    CHECK_FALSE(third.contact);
    const auto approach = rig.step(time + 12000U);
    CHECK(approach.outputs.duty_l <= 0.60F);
    CHECK(approach.outputs.duty_r <= 0.60F);
    CHECK_FALSE(approach.contact);
}

TEST_CASE("B5 B9 Robot commits same-tick centered ATTACK impact once") {
    Rig rig;
    rig.opponent(2U);
    const auto time = go(rig, Mode::DIRECT);
    rig.step(time + 1000U);
    rig.input.ax_g = 1.51F;
    const auto third = rig.step(time + 2000U);
    CHECK(third.outputs.ui_state == State::ATTACK);
    CHECK(third.contact);
    CHECK(count(third, core::Event::CONTACT) == 1U);
    CHECK(event(third, core::Event::CONTACT).detail == 2U);
    rig.input.ax_g = 0.0F;
    const auto next = rig.step(time + 3000U);
    CHECK(next.contact);
    CHECK(count(next, core::Event::CONTACT) == 0U);
}

TEST_CASE("B2 B9 Robot off-center front beats side but cannot authorize contact duty") {
    for (const std::uint8_t mask : {std::uint8_t{1U}, std::uint8_t{4U}, std::uint8_t{0x79U}}) {
        Rig rig;
        rig.opponent(mask);
        const auto time = go(rig, Mode::DIRECT);
        rig.input.ax_g = 2.0F;
        const auto result = rig.step(time + 100000U);
        CHECK(result.outputs.ui_state == State::TRACK);
        CHECK_FALSE(result.contact);
        CHECK(std::fabs(result.outputs.duty_l) <= 0.80F);
        CHECK(std::fabs(result.outputs.duty_r) <= 0.80F);
        CHECK(count(result, core::Event::CONTACT) == 0U);
    }
}

TEST_CASE("B9 D046 Robot front loss brakes immediately then routes current residual") {
    for (const std::uint8_t residual : {std::uint8_t{0U}, std::uint8_t{8U}, std::uint8_t{64U}}) {
        Rig rig;
        const auto time = attack(rig);
        rig.opponent(residual);
        rig.step(time + 1000U);
        const auto before = rig.step(time + 30999U);
        CHECK(before.opponent_mask == static_cast<std::uint8_t>(residual | 2U));
        const auto lost = rig.step(time + 31000U);
        CHECK(lost.opponent_mask == residual);
        CHECK(lost.outputs.ui_state == (residual == 0U ? State::SEARCH : State::DEFEND_TURN));
        zero(lost, false);
        CHECK_FALSE(lost.contact);
        const auto next = rig.step(time + 81000U);
        CHECK(next.outputs.ui_state == (residual == 0U ? State::SEARCH : State::DEFEND_TURN));
        CHECK(std::fabs(next.outputs.duty_l) + std::fabs(next.outputs.duty_r) > 0.0F);
        CHECK_FALSE(next.contact);
    }
}

TEST_CASE("B12 D033 D034 Robot mirrored flank pivots ignore front until traverse") {
    for (const auto mode : {Mode::SIDESTEP_R, Mode::SIDESTEP_L, Mode::ARC_R, Mode::ARC_L}) {
        Rig rig;
        rig.opponent(2U);
        const auto time = go(rig, mode);
        CHECK(rig.last.outputs.ui_state == State::OPENER);
        rig.step(time + 1000U);
        CHECK(rig.last.outputs.ui_state == State::OPENER);
        const float sign = mode == Mode::SIDESTEP_L || mode == Mode::ARC_L ? -1.0F : 1.0F;
        rig.input.raw_heading_deg = sign * (mode == Mode::ARC_R || mode == Mode::ARC_L ? 80.0F : 50.0F);
        const auto exit = rig.step(time + 2000U);
        CHECK(exit.outputs.ui_state == State::TRACK);
        CHECK_FALSE(exit.contact);
        CHECK(rig.step(time + 3000U).outputs.ui_state == State::TRACK);
        CHECK(rig.step(time + 4000U).outputs.ui_state == State::ATTACK);
    }
}

TEST_CASE("B12 D055 Robot WAIT consumes ordered confirmed cue then complete right pivot") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT);
    zero(rig.last, false);
    rig.opponent(2U);
    rig.step(time + 1000U);
    zero(rig.step(time + 2000U), false);
    rig.opponent(3U);
    rig.step(time + 3000U);
    const auto cue = rig.step(time + 4000U);
    CHECK(cue.outputs.ui_state == State::OPENER);
    CHECK(cue.outputs.duty_l > 0.0F);
    CHECK(cue.outputs.duty_r < 0.0F);
    rig.input.raw_heading_deg = 50.0F;
    CHECK(rig.step(time + 5000U).outputs.ui_state == State::TRACK);
}

TEST_CASE("B12 Robot natural DIRECT and WAIT expiration enter SEARCH at exact deadlines") {
    for (const auto mode : {Mode::DIRECT, Mode::WAIT}) {
        Rig rig;
        const auto time = go(rig, mode);
        const std::uint32_t duration = mode == Mode::DIRECT ? 400000U : 2000000U;
        CHECK(rig.step(time + duration - 1U).outputs.ui_state == State::OPENER);
        const auto result = rig.step(time + duration);
        CHECK(result.outputs.ui_state == State::SEARCH);
        CHECK(result.contract_faults == 0U);
    }
}

TEST_CASE("B7 D059 Robot permits absent IMU and preserves initial fallback deadline") {
    Rig rig;
    rig.input.imu_ok = false;
    rig.input.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
    const auto time = go(rig);
    const auto pivot = rig.step(time + 99999U);
    CHECK(pivot.outputs.ui_state == State::OPENER);
    CHECK(pivot.outputs.duty_l > 0.0F);
    CHECK(pivot.outputs.duty_r < 0.0F);
    const auto traverse = rig.step(time + 100000U);
    CHECK(traverse.outputs.ui_state == State::OPENER);
    CHECK(traverse.contract_faults == 0U);
    const auto forward = rig.step(time + 150000U);
    CHECK(forward.outputs.duty_l > 0.0F);
    CHECK(forward.outputs.duty_r > 0.0F);
    CHECK_FALSE(forward.heading.imu_ok);
}

TEST_CASE("B11 D060 Robot stalls from previous actual duties not requests") {
    Rig rig;
    const auto time = attack(rig);
    rig.apply_enabled = false;
    CHECK(rig.step(time + 1000U).outputs.ui_state == State::ATTACK);
    const auto inhibited = rig.step(time + 1001000U);
    CHECK(inhibited.outputs.ui_state == State::ATTACK);
    CHECK(count(inhibited, core::Event::STALL) == 0U);
    rig.apply_enabled = true;
    rig.step(time + 1002000U);
    CHECK(rig.step(time + 2001999U).outputs.ui_state == State::ATTACK);
    const auto stalled = rig.step(time + 2002000U);
    CHECK(stalled.outputs.ui_state == State::REFLANK);
    CHECK_FALSE(stalled.contact);
    CHECK(event(stalled, core::Event::STALL).detail == 5U);
    CHECK(event(stalled, core::Event::REFLANK_PHASE).detail == 1U);
}

TEST_CASE("B4 D049 Robot pushed-out selection consumes actual forward receipt") {
    for (const bool applied : {false, true}) {
        Rig rig;
        const auto time = attack(rig);
        rig.apply_enabled = applied;
        rig.lines(12U);
        const auto result = rig.step(time + 1000U);
        CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
        CHECK_FALSE(result.contact);
        CHECK((event(result, core::Event::EDGE).detail & 16U) == (applied ? 16U : 0U));
    }
}

TEST_CASE("B10 D060 Robot DEFEND timeout starts SEARCH for one tick despite side") {
    Rig rig;
    rig.opponent(8U);
    const auto time = go(rig, Mode::DIRECT);
    CHECK(rig.last.outputs.ui_state == State::DEFEND_TURN);
    CHECK(rig.step(time + 799999U).outputs.ui_state == State::DEFEND_TURN);
    CHECK(rig.step(time + 800000U).outputs.ui_state == State::SEARCH);
    CHECK(rig.step(time + 801000U).outputs.ui_state == State::DEFEND_TURN);
}

TEST_CASE("D060 Robot duplicate ignores changed STOP observations and receipts") {
    Rig rig;
    const auto time = go(rig);
    const auto original = rig.last;
    auto changed = rig.at(time);
    changed.stop_requested = true;
    changed.observations_fresh = false;
    changed.previous.applied_valid = false;
    changed.raw_heading_deg = std::numeric_limits<float>::infinity();
    const auto duplicate = rig.submit(changed);
    CHECK_FALSE(duplicate.fresh);
    CHECK(duplicate.token == original.token);
    CHECK(duplicate.outputs.ui_state == original.outputs.ui_state);
    CHECK(duplicate.outputs.duty_l == original.outputs.duty_l);
    CHECK(duplicate.outputs.duty_r == original.outputs.duty_r);
    CHECK(duplicate.contract_faults == original.contract_faults);
    CHECK_FALSE(duplicate.lifecycle.gate.go);
    CHECK_FALSE(duplicate.lifecycle.heading_reset_requested);
    CHECK_FALSE(duplicate.heading.origin_changed);
    CHECK_FALSE(duplicate.bias_update_requested);
    CHECK_FALSE(duplicate.frame_ready);
    CHECK(duplicate.events.count == 0U);
    CHECK(rig.step(time + 1000U).contract_faults == 0U);
}

TEST_CASE("D060 Robot reset keeps token identity and rejects stale predecessor evidence") {
    Rig rig;
    idle(rig);
    const auto old = rig.last.token;
    rig.reset();
    auto fresh = rig.at(0U);
    fresh.previous.applied_valid = true;
    fresh.previous.token = old;
    fresh.previous.duty_l = std::numeric_limits<float>::quiet_NaN();
    CHECK(rig.submit(fresh).contract_faults == 0U);
    CHECK(rig.last.token > old);
    auto stale = rig.at(1000U);
    stale.previous.token = old;
    const auto result = rig.submit(stale);
    CHECK((result.contract_faults & fsm::APPLICATION_CONTRACT) != 0U);
    CHECK(result.outputs.ui_state == State::STOPPED);
    zero(result);
}

TEST_CASE("D060 Robot rejects malformed or missing application evidence without assuming zero") {
    for (unsigned variant = 0U; variant < 6U; ++variant) {
        CAPTURE(variant);
        Rig rig;
        idle(rig);
        auto sample = rig.at(22000U);
        if (variant == 0U) sample.previous.applied_valid = false;
        if (variant == 1U) ++sample.previous.token;
        if (variant == 2U) sample.previous.duty_l = std::numeric_limits<float>::quiet_NaN();
        if (variant == 3U) sample.previous.duty_l = 0.01F;
        if (variant == 4U) sample.previous.motors_enabled = true;
        if (variant == 5U) sample.previous.applied_us = 22001U;
        const auto result = rig.submit(sample);
        CHECK((result.contract_faults & fsm::APPLICATION_CONTRACT) != 0U);
        CHECK(result.outputs.ui_state == State::STOPPED);
        zero(result);
        CHECK(rig.step(23000U).outputs.ui_state == State::STOPPED);
    }
}

TEST_CASE("D060 Robot accepts inhibition and downward application but rejects larger or reversed duty") {
    for (unsigned variant = 0U; variant < 5U; ++variant) {
        Rig rig;
        const auto time = go(rig, Mode::DIRECT);
        rig.step(time + 50000U);
        auto sample = rig.at(time + 51000U);
        if (variant == 0U) {
            sample.previous.motors_enabled = false;
            sample.previous.duty_l = sample.previous.duty_r = 0.0F;
        }
        if (variant == 1U) sample.previous.duty_l = sample.previous.duty_r = 0.0F;
        if (variant == 2U) { sample.previous.duty_l *= 0.5F; sample.previous.duty_r *= 0.5F; }
        if (variant == 3U) sample.previous.duty_l = -sample.previous.duty_l;
        if (variant == 4U) sample.previous.duty_r += 0.001F;
        const auto result = rig.submit(sample);
        CHECK(((result.contract_faults & fsm::APPLICATION_CONTRACT) != 0U) == (variant >= 3U));
        if (variant >= 3U) zero(result);
    }
}

TEST_CASE("B14 D060 Robot stale observations latch STOP before calibration can sample") {
    Rig rig;
    const auto anchor = release(rig, idle(rig));
    rig.input.observations_fresh = false;
    const auto result = rig.step(anchor + 1500000U);
    CHECK((result.contract_faults & fsm::STALE_SENSORS) != 0U);
    CHECK(result.outputs.ui_state == State::STOPPED);
    CHECK(result.lifecycle.services.calibration_samples == 0U);
    zero(result);
    rig.input.observations_fresh = true;
    CHECK(rig.step(anchor + 5100000U).outputs.ui_state == State::STOPPED);
    rig.reset();
    CHECK(rig.step(0U).outputs.ui_state == State::IDLE);
}

TEST_CASE("D060 Robot invalid battery samples inhibit after setup") {
    for (unsigned variant = 0U; variant < 4U; ++variant) {
        Rig rig;
        idle(rig);
        if (variant == 0U) rig.input.vbat_valid = false;
        if (variant == 1U) rig.input.vbat_v = std::numeric_limits<float>::quiet_NaN();
        if (variant == 2U) rig.input.vbat_v = std::numeric_limits<float>::infinity();
        if (variant == 3U) rig.input.vbat_v = -std::numeric_limits<float>::infinity();
        const auto result = rig.step(22000U);
        CHECK(result.contract_faults != 0U);
        CHECK(result.outputs.ui_state == State::STOPPED);
        zero(result);
    }
}

TEST_CASE("D059 D060 healthy invalid yaw faults while unavailable payload is ignored") {
    for (const bool healthy : {false, true}) {
        Rig rig;
        const auto time = go(rig);
        rig.input.imu_ok = healthy;
        rig.input.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
        const auto result = rig.step(time + 1000U);
        CHECK(((result.contract_faults & fsm::HEADING_CONTRACT) != 0U) == healthy);
        CHECK(result.outputs.ui_state == (healthy ? State::STOPPED : State::OPENER));
        bounded(result);
        if (healthy) zero(result);
    }
}

TEST_CASE("D024 D060 service failure is diagnostic and cannot shorten or veto hold") {
    Rig rig;
    rig.input.previous_bias_dps = std::numeric_limits<float>::quiet_NaN();
    const auto anchor = release(rig, idle(rig));
    CHECK(rig.last.lifecycle.service_start_failed);
    CHECK(rig.last.contract_faults == 0U);
    zero(rig.step(anchor + 5099999U));
    const auto result = rig.step(anchor + 5100000U);
    CHECK(result.lifecycle.gate.go);
    CHECK(result.outputs.ui_state == State::OPENER);
    CHECK(result.contract_faults == 0U);
}

TEST_CASE("B12 Robot specified left right opener pairs mirror governed output") {
    for (const bool arc : {false, true}) {
        Rig right;
        Rig left;
        const auto tr = go(right, arc ? Mode::ARC_R : Mode::SIDESTEP_R);
        const auto tl = go(left, arc ? Mode::ARC_L : Mode::SIDESTEP_L);
        auto r = right.step(tr + 50000U);
        auto l = left.step(tl + 50000U);
        CHECK(r.outputs.duty_l == doctest::Approx(l.outputs.duty_r));
        CHECK(r.outputs.duty_r == doctest::Approx(l.outputs.duty_l));
        right.input.raw_heading_deg = arc ? 80.0F : 50.0F;
        left.input.raw_heading_deg = -right.input.raw_heading_deg;
        right.step(tr + 51000U);
        left.step(tl + 51000U);
        r = right.step(tr + 101000U);
        l = left.step(tl + 101000U);
        CHECK(r.outputs.duty_l == doctest::Approx(l.outputs.duty_r));
        CHECK(r.outputs.duty_r == doctest::Approx(l.outputs.duty_l));
        CHECK(r.contract_faults == 0U);
        CHECK(l.contract_faults == 0U);
    }
}

TEST_CASE("B5 Robot contact20 counts confirmed new observations once despite duplicates") {
    Rig rig;
    const auto time = go(rig, Mode::DIRECT);
    rig.opponent(7U);
    CHECK(rig.step(time + 1000U).opponent_mask == 0U);
    for (unsigned observation = 1U; observation <= 20U; ++observation) {
        const auto result = rig.step(time + (observation + 1U) * 1000U);
        CHECK(result.opponent_mask == 7U);
        CHECK(result.contact == (observation == 20U));
        CHECK(count(result, core::Event::CONTACT) == (observation == 20U ? 1U : 0U));
        if (observation == 2U) {
            for (unsigned duplicate = 0U; duplicate < 25U; ++duplicate) {
                const auto repeated = rig.step(time + 3000U);
                CHECK_FALSE(repeated.fresh);
                CHECK_FALSE(repeated.contact);
                CHECK(count(repeated, core::Event::CONTACT) == 0U);
            }
        }
    }
    CHECK(event(rig.last, core::Event::CONTACT).detail == 1U);
    CHECK(event(rig.last, core::Event::CONTACT).value == 7U);
}

TEST_CASE("B5 D059 Robot keeps continuous raw stuck history across local GO reset") {
    Rig rig;
    rig.opponent(2U);
    rig.input.raw_heading_deg = 720.0F;
    const auto time = go(rig, Mode::DIRECT);
    CHECK(rig.last.opponent_fault_mask == 0U);
    CHECK(rig.last.opponent_mask == 2U);
    CHECK(rig.last.heading.heading_deg == 0.0F);
    rig.input.raw_heading_deg = 1080.0F;
    CHECK(rig.step(time + 1000U).opponent_fault_mask == 0U);
    rig.input.raw_heading_deg = 1081.0F;
    const auto stuck = rig.step(time + 2000U);
    CHECK(stuck.opponent_fault_mask == 2U);
    CHECK(stuck.opponent_mask == 0U);
    CHECK_FALSE(stuck.contact);
    CHECK(event(stuck, core::Event::FAULT, 2).value == 2U);
    rig.opponent(0U);
    CHECK(rig.step(time + 40000U).opponent_fault_mask == 2U);
    CHECK(count(rig.last, core::Event::FAULT, 2) == 0U);
    rig.reset();
    CHECK(rig.step(0U).opponent_fault_mask == 0U);
}

TEST_CASE("B11 D025 Robot two actual swings alternate then ALL_IN preserves edge safety") {
    Rig rig;
    auto time = attack(rig);
    for (unsigned attempt = 1U; attempt <= 2U; ++attempt) {
        rig.input.raw_heading_deg += 26.0F;
        time += 1000U;
        const auto entered = rig.step(time);
        CHECK(entered.outputs.ui_state == State::REFLANK);
        CHECK_FALSE(entered.contact);
        const auto stall = event(entered, core::Event::STALL);
        CHECK(stall.detail == 6U); // Deflection route plus admitted.
        CHECK(stall.value == attempt);
        CHECK(event(entered, core::Event::REFLANK_PHASE, 1).value == (attempt == 1U ? 1U : 2U));
        time = finishReflank(rig, time, attempt == 1U ? 1U : 2U);
    }
    rig.input.raw_heading_deg += 26.0F;
    const auto denied = rig.step(time + 1000U);
    CHECK(denied.outputs.ui_state == State::ATTACK);
    CHECK(denied.contact);
    CHECK(denied.all_in);
    CHECK(event(denied, core::Event::STALL).detail == 10U);
    CHECK(event(denied, core::Event::STALL).value == 2U);
    CHECK(count(denied, core::Event::REFLANK_PHASE) == 0U);
    rig.lines(15U);
    const auto edge = rig.step(time + 2000U);
    CHECK(edge.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(edge.all_in);
    CHECK_FALSE(edge.contact);
    zero(edge);
}

TEST_CASE("B6 Robot low-voltage compensation cannot exceed phase or contact caps") {
    Rig rig;
    rig.input.vbat_v = 9.0F;
    rig.opponent(2U);
    const auto time = go(rig, Mode::DIRECT);
    rig.step(time + 1000U);
    rig.step(time + 2000U);
    auto result = rig.step(time + 52000U);
    CHECK(result.outputs.duty_l == doctest::Approx(0.60F));
    CHECK(result.outputs.duty_r == doctest::Approx(0.60F));
    CHECK_FALSE(result.contact);
    rig.input.ax_g = 2.0F;
    rig.step(time + 53000U);
    rig.input.ax_g = 0.0F;
    result = rig.step(time + 103000U);
    CHECK(result.contact);
    CHECK(result.outputs.duty_l == doctest::Approx(1.0F));
    CHECK(result.outputs.duty_r == doctest::Approx(1.0F));
    rig.lines(1U);
    zero(rig.step(time + 104000U), false);
    rig.step(time + 105000U);
    result = rig.step(time + 155000U);
    CHECK(result.outputs.duty_l == doctest::Approx(-0.80F));
    CHECK(result.outputs.duty_r == doctest::Approx(-0.80F));
    CHECK_FALSE(result.contact);
}

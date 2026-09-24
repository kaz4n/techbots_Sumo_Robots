// Tests literal P4 SEARCH-at-GO routing followed by unchanged reactive behaviors.
// Derives transitions and timing from D128 and public B5-B11 contracts.
// Actual Transaction/Gate observations run independently in M0 and M1 profiles.
#include "fixtures/reactive_profile_fixture.h"
#include <limits>

using namespace reactive_test;

TEST_CASE("B1 B13 D128 immutable reactive identity preserves every existing profile default") {
    CHECK(SUMOX_P4_REACTIVE == 1); CHECK(MATCH == 0); CHECK(SUMOX_B4_STAND == 0);
    CHECK(SUMOX_P3_DRIVE_TEST == 0); CHECK(SUMOX_P3_TURN_TRIAL == 0); CHECK(SUMOX_P3_STOP_TRIAL == 0);
    CHECK(fsm::RobotResult::REACTIVE_PROFILE); CHECK_FALSE(fsm::RobotResult::STAND_PROFILE);
    CHECK_FALSE(fsm::RobotResult::DRIVE_TEST_PROFILE); CHECK_FALSE(fsm::RobotResult::TURN_TRIAL_PROFILE);
    CHECK_FALSE(fsm::RobotResult::STOP_TRIAL_PROFILE); CHECK(config::EDGE_PUSH_THROUGH_MS == 0U);
    CHECK(config::SEARCH_DUTY_MAX == .30F); CHECK(config::ATTACK_APPROACH_DUTY == .60F);
    CHECK(config::ATTACK_DUTY == 1.0F);
}

TEST_CASE("B2 B5 B9 D128 all6 modes and128 effective masks start literal SEARCH then normal perception") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) for (unsigned mask = 0U; mask < 128U; ++mask) {
        CAPTURE(mode); CAPTURE(mask); Rig rig; rig.opponent(mask); const auto go = rig.goMatch(mode);
        const auto entry = rig.owner.report(); active(rig, entry);
        CHECK(entry.robot.outputs.ui_state == State::SEARCH); CHECK(entry.robot.opponent_mask == mask);
        CHECK(entry.robot.running_mode == static_cast<Mode>(mode)); CHECK_FALSE(entry.robot.contact);
        if (mask != 0U) brake(rig, entry);
        const unsigned front = mask & 7U;
        const auto expected = front ? State::TRACK : (mask ? State::DEFEND_TURN : State::SEARCH);
        for (unsigned sample = 1U; sample <= 3U; ++sample) {
            const auto r = rig.at(go + sample * 1000U); active(rig, r);
            const bool centered = front == 2U || front == 3U || front == 5U || front == 6U || front == 7U;
            CHECK(r.robot.outputs.ui_state == ((sample == 3U && centered) ? State::ATTACK : expected));
            CHECK(r.robot.running_mode == static_cast<Mode>(mode)); CHECK(r.robot.opponent_mask == mask);
            if (sample < 3U || !centered) CHECK_FALSE(r.robot.contact);
        }
    }
}

TEST_CASE("B5 D128 a new raw target at GO is not a confirmed effective target") {
    Rig rig; const auto release = rig.releaseMatch(); rig.at(release + 5099999U); rig.opponent(2U);
    const auto go = release + 5100000U; const auto r = rig.at(go);
    CHECK(r.robot.outputs.ui_state == State::SEARCH); CHECK(r.robot.opponent_mask == 0U); active(rig, r);
    CHECK(rig.next().robot.outputs.ui_state == State::TRACK); CHECK(rig.owner.report().robot.opponent_mask == 2U);
    CHECK(rig.next().robot.outputs.ui_state == State::TRACK);
    CHECK(rig.next().robot.outputs.ui_state == State::ATTACK);
}

TEST_CASE("B5 D128 a genuinely stuck raw target is removed before GO Search sees perception") {
    Rig rig; rig.opponent(2U); const auto release = rig.releaseMatch();
    rig.at(release + 4500000U); rig.source.raw_heading_deg = 361.0F;
    const auto before = rig.at(release + 5099999U);
    CHECK(before.robot.opponent_fault_mask == 2U); CHECK(before.robot.opponent_mask == 0U);
    const auto go = rig.next(1U); CHECK(go.robot.lifecycle.gate.go);
    CHECK(go.robot.outputs.ui_state == State::SEARCH); CHECK(go.robot.opponent_mask == 0U);
    const auto later = rig.next(50000U); active(rig, later);
    CHECK(later.robot.outputs.ui_state == State::SEARCH); CHECK(later.robot.opponent_fault_mask == 2U);
}

TEST_CASE("B8 D128 empty GO captures healthy scan heading before the next observation") {
    for (unsigned mode = 1U; mode <= 6U; ++mode) {
        Rig rig; rig.source.raw_heading_deg = 170.0F; const auto go = rig.goMatch(mode);
        rig.source.raw_heading_deg = 529.0F; const auto scan = rig.at(go + 50000U); active(rig, scan);
        CHECK(scan.robot.outputs.duty_l == .45F); CHECK(scan.robot.outputs.duty_r == -.45F);
        rig.source.raw_heading_deg = 530.0F; const auto advance = rig.next(); active(rig, advance);
        CHECK(advance.robot.outputs.ui_state == State::SEARCH);
        CHECK(advance.robot.outputs.duty_l == .30F); CHECK(advance.robot.outputs.duty_r == 0.0F);
        const auto forward = rig.next(50000U); CHECK(forward.robot.outputs.duty_l == .30F);
        CHECK(forward.robot.outputs.duty_r == .30F);
    }
}

TEST_CASE("B7 B8 D128 initial real IMU absence retains full720ms scan then300ms forward and alternation") {
    Rig rig; rig.source.imu_ok = false; rig.source.raw_heading_deg = std::numeric_limits<float>::quiet_NaN();
    const auto go = rig.goMatch(); const auto scan = rig.at(go + 719999U); active(rig, scan);
    CHECK(scan.robot.outputs.duty_l == .45F); CHECK(scan.robot.outputs.duty_r == -.45F);
    const auto advance = rig.at(go + 720000U); active(rig, advance);
    CHECK(advance.robot.outputs.duty_l == .30F); CHECK(advance.robot.outputs.duty_r == 0.0F);
    const auto forward = rig.at(go + 1019999U); CHECK(forward.robot.outputs.duty_l == .30F);
    CHECK(forward.robot.outputs.duty_r == .30F); const auto left = rig.at(go + 1020000U);
    CHECK(left.robot.outputs.duty_l == 0.0F); CHECK(left.robot.outputs.duty_r > 0.0F);
    const auto full = rig.next(50000U); CHECK(full.robot.outputs.duty_l == -.45F);
    CHECK(full.robot.outputs.duty_r == .45F); CHECK_FALSE(full.robot.heading.imu_ok);
}

TEST_CASE("B7 B8 D128 midscan loss retains remaining fallback time through real recovery") {
    Rig rig; const auto go = rig.goMatch(); rig.source.raw_heading_deg = 180.0F; rig.next();
    rig.source.imu_ok = false; rig.at(go + 100000U);
    rig.source.imu_ok = true; rig.source.raw_heading_deg = 720.0F; rig.at(go + 200000U);
    const auto before = rig.at(go + 459999U); active(rig, before);
    CHECK(before.robot.outputs.duty_l == .45F); CHECK(before.robot.outputs.duty_r == -.45F);
    const auto after = rig.at(go + 460000U); active(rig, after);
    CHECK(after.robot.outputs.duty_l == .30F); CHECK(after.robot.outputs.duty_r == 0.0F);
}

TEST_CASE("B5 B6 B9 D128 centered ATTACK requires third postGO sample before current impact contact") {
    Rig rig; rig.opponent(2U); rig.source.ax_g = 2.0F; rig.source.vbat_v = 9.0F;
    const auto go = rig.goMatch(); brake(rig, rig.owner.report()); CHECK_FALSE(rig.owner.report().robot.contact);
    for (unsigned i = 1U; i <= 2U; ++i) { const auto r = rig.at(go + i * 1000U);
        CHECK(r.robot.outputs.ui_state == State::TRACK); CHECK_FALSE(r.robot.contact);
        CHECK(count(r.robot, core::Event::CONTACT) == 0U); }
    const auto attack = rig.at(go + 3000U); CHECK(attack.robot.outputs.ui_state == State::ATTACK);
    CHECK(attack.robot.contact); CHECK(count(attack.robot, core::Event::CONTACT) == 1U);
    rig.source.ax_g = 0.0F; const auto full = rig.at(go + 53000U); active(rig, full);
    CHECK(full.robot.outputs.duty_l == 1.0F); CHECK(full.robot.outputs.duty_r == 1.0F);
    CHECK(full.applied.feedback.duty_l == (MOTORS_ALLOWED ? 1.0F : 0.0F));
    CHECK(full.applied.feedback.duty_r == (MOTORS_ALLOWED ? 1.0F : 0.0F));
    CHECK(count(full.robot, core::Event::CONTACT) == 0U);
}

TEST_CASE("B6 B9 D128 lowvoltage approach and offcenter TRACK retain final electrical caps and steering") {
    Rig centered; centered.source.vbat_v = 9.0F; centered.attack();
    const auto r = centered.owner.report(); active(centered, r); CHECK_FALSE(r.robot.contact);
    CHECK(r.robot.outputs.duty_l == .60F); CHECK(r.robot.outputs.duty_r == .60F);
    for (unsigned mask : {1U, 4U}) {
        Rig rig; rig.source.vbat_v = 9.0F; rig.source.ax_g = 2.0F; rig.opponent(mask);
        const auto go = rig.goMatch(); rig.next(); const auto track = rig.at(go + 51000U); active(rig, track);
        CHECK(track.robot.outputs.ui_state == State::TRACK); CHECK_FALSE(track.robot.contact);
        if (mask == 1U) { CHECK(track.robot.outputs.duty_l < 0.0F); CHECK(track.robot.outputs.duty_r == .30F); }
        else { CHECK(track.robot.outputs.duty_l == .30F); CHECK(track.robot.outputs.duty_r < 0.0F); }
        CHECK(std::fabs(track.robot.outputs.duty_l) <= .30F);
        CHECK(std::fabs(track.robot.outputs.duty_r) <= .30F);
    }
}

TEST_CASE("B5 D128 close-contact cues count actual20 fresh observations independently of elapsed time") {
    Rig rig; const auto go = rig.goMatch(); rig.opponent(7U); rig.next();
    for (unsigned sample = 1U; sample <= 19U; ++sample) {
        const auto r = rig.next(); CHECK_FALSE(r.robot.contact);
        CHECK(count(r.robot, core::Event::CONTACT) == 0U);
    }
    const auto contacted = rig.next(); CHECK(contacted.robot.outputs.ui_state == State::ATTACK);
    CHECK(contacted.robot.contact); CHECK(count(contacted.robot, core::Event::CONTACT) == 1U);
    CHECK(rig.now == go + 21000U);
}

TEST_CASE("B5 B9 D128 offcenter loss clears contact and fresh recentering cannot reuse its old latch") {
    Rig rig; const auto time = rig.attack(true); rig.opponent(1U); rig.next();
    const auto offcenter = rig.at(time + 31000U); CHECK(offcenter.robot.opponent_mask == 1U);
    CHECK(offcenter.robot.outputs.ui_state == State::TRACK); CHECK_FALSE(offcenter.robot.contact);
    rig.opponent(0U); rig.next(); rig.at(time + 62000U);
    rig.opponent(2U); rig.next(); const auto first = rig.next();
    CHECK(first.robot.opponent_mask == 2U); CHECK(first.robot.outputs.ui_state == State::TRACK);
    CHECK(rig.next().robot.outputs.ui_state == State::TRACK);
    const auto attack = rig.next(); CHECK(attack.robot.outputs.ui_state == State::ATTACK);
    CHECK_FALSE(attack.robot.contact); CHECK(attack.robot.outputs.duty_l <= .60F);
}

TEST_CASE("B9 D046 D128 front loss brakes at exact30ms clear then executes residual perception next tick") {
    for (unsigned residual : {0U, 8U, 64U}) {
        Rig rig; const auto time = rig.attack(true); rig.opponent(residual); rig.next();
        const auto before = rig.at(time + 30999U); CHECK(before.robot.opponent_mask == (residual | 2U));
        CHECK(before.robot.outputs.ui_state == State::ATTACK);
        const auto lost = rig.at(time + 31000U); brake(rig, lost); CHECK_FALSE(lost.robot.contact);
        const auto expected = residual ? State::DEFEND_TURN : State::SEARCH;
        CHECK(lost.robot.outputs.ui_state == expected); CHECK(lost.robot.opponent_mask == residual);
        const auto resumed = rig.next(50000U); active(rig, resumed);
        CHECK(resumed.robot.outputs.ui_state == expected);
        CHECK(std::fabs(resumed.robot.outputs.duty_l) + std::fabs(resumed.robot.outputs.duty_r) > 0.0F);
    }
}

TEST_CASE("B10 D128 side defense captures once and ambiguous bearings keep bounded800ms zero wait") {
    for (unsigned mask : {8U, 16U, 32U, 64U, 24U, 96U}) {
        Rig rig; rig.opponent(mask); const auto go = rig.goMatch(); brake(rig, rig.owner.report());
        const auto entered = rig.next(); CHECK(entered.robot.outputs.ui_state == State::DEFEND_TURN);
        const auto time = rig.now; const auto moving = rig.at(time + 50000U); active(rig, moving);
        if (mask == 24U || mask == 96U) brake(rig, moving);
        else { CHECK((moving.robot.outputs.duty_l < 0.0F) == (mask == 8U || mask == 32U));
            CHECK(std::fabs(moving.robot.outputs.duty_l) > 0.0F); }
        CHECK(rig.at(time + 799999U).robot.outputs.ui_state == State::DEFEND_TURN);
        CHECK(rig.at(time + 800000U).robot.outputs.ui_state == State::SEARCH);
        CHECK(rig.next().robot.outputs.ui_state == State::DEFEND_TURN); CHECK(time == go + 1000U);
    }
}

TEST_CASE("B11 D128 actual applied receipts qualify stall and a complete reflank returns through reacquisition") {
    Rig rig; const auto full = rig.attack(true); rig.next();
    const auto qualified = full + 1000U; const auto before = rig.at(qualified + 999999U);
    CHECK(before.robot.outputs.ui_state == State::ATTACK);
    const auto stalled = rig.at(qualified + 1000000U); active(rig, stalled);
    if (!MOTORS_ALLOWED) { CHECK(stalled.robot.outputs.ui_state == State::ATTACK);
        CHECK(count(stalled.robot, core::Event::STALL) == 0U); CHECK_FALSE(stalled.robot.all_in); return; }
    CHECK(stalled.robot.outputs.ui_state == State::REFLANK); CHECK_FALSE(stalled.robot.contact);
    CHECK(count(stalled.robot, core::Event::STALL, 5U) == 1U);
    CHECK(count(stalled.robot, core::Event::REFLANK_PHASE, 1U) == 1U);
    const auto start = rig.now; const auto back = rig.next(50000U); active(rig, back);
    CHECK(back.robot.outputs.duty_l == -.8F); CHECK(back.robot.outputs.duty_r == -.8F);
    CHECK(rig.at(start + 149999U).robot.outputs.ui_state == State::REFLANK);
    const auto swing = rig.at(start + 150000U); CHECK(count(swing.robot, core::Event::REFLANK_PHASE, 2U) == 1U);
    rig.at(start + 850000U); const auto exit = rig.at(start + 1250000U);
    CHECK(exit.robot.outputs.ui_state == State::TRACK); CHECK_FALSE(exit.robot.contact);
    CHECK(rig.next().robot.outputs.ui_state == State::TRACK);
    const auto attack = rig.next(); CHECK(attack.robot.outputs.ui_state == State::ATTACK); CHECK_FALSE(attack.robot.contact);
}

TEST_CASE("B11 D128 strictly greater25degree deflection still requires actual forward duty receipts") {
    Rig rig; const auto time = rig.attack(true); rig.source.raw_heading_deg = 25.0F;
    const auto equal = rig.at(time + 1000U); CHECK(equal.robot.outputs.ui_state == State::ATTACK);
    rig.source.raw_heading_deg = std::nextafter(25.0F, std::numeric_limits<float>::infinity());
    const auto beyond = rig.next(1U); active(rig, beyond);
    CHECK(beyond.robot.outputs.ui_state == (MOTORS_ALLOWED ? State::REFLANK : State::ATTACK));
    CHECK(count(beyond.robot, core::Event::STALL) == (MOTORS_ALLOWED ? 1U : 0U));
}

TEST_CASE("B15 D128 records literal GO SEARCH and true first applied duty without opener events") {
    Rig rig; rig.opponent(2U); const auto release = rig.releaseMatch(6U); const auto go = release + 5100000U;
    brake(rig, rig.at(go)); bool seen = false; std::uint32_t first = 0U;
    for (unsigned i = 1U; i <= 50U; ++i) {
        const auto r = rig.at(go + i * 1000U); noOpener(r.robot);
        if (!seen && (r.applied.feedback.duty_l != 0.0F || r.applied.feedback.duty_r != 0.0F)) {
            seen = true; first = r.applied.feedback.applied_us;
        }
    }
    rig.source.stop_requested = true; rig.next(); rig.next();
    CHECK(rig.owner.recording().phase() == recorder::AttemptPhase::SEALED);
    std::uint32_t logged = 0U;
    CHECK(drive_test::eventCount(rig.owner.recording(), core::Event::FIRST_NONZERO_DUTY, &logged)
          == (MOTORS_ALLOWED ? 1U : 0U));
    if (MOTORS_ALLOWED) { CHECK(seen); CHECK(logged == first); CHECK(first - release >= 5100000U); }
    else CHECK_FALSE(seen);
    for (std::size_t i = 0U; i < rig.owner.recording().frames().size(); ++i) {
        recorder::StoredFrame frame; APP_REQUIRE(rig.owner.recording().frames().read(i, frame));
        CHECK(frame.bytes.data[4] != static_cast<unsigned>(State::OPENER));
    }
}

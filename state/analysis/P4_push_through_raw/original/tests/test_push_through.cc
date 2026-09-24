// Tests D131 bounded push-through from the adopted B9.4 public contract.
// Protects finite lifecycle and observable Robot accounting across copied settings.
// Independent default/20/100ms runs use actual Gate receipts and no implementation reads.
#include "fixtures/push_through_fixture.h"
#if SUMOX_TIMING_EVIDENCE
#include "p4_timing_fixture.h"
#endif

using namespace push_test;

TEST_CASE("B9.4 D131 shipped or copied duration is the sole bounded configuration") {
    CHECK(config::EDGE_PUSH_THROUGH_MS <= 100U); CHECK(SUMOX_P4_REACTIVE == 1);
    CHECK(MATCH == 0); edge::Escape owner; CHECK_FALSE(owner.pushThroughActive());
    edge::EscapeSample inert; CHECK_FALSE(inert.push_eligible);
    const auto r = owner.step(inert); CHECK_FALSE(r.escape_required); CHECK(r.inhibit_motion);
}

TEST_CASE("B9.4 D131 all front masks use exact original deadline including uint32 wrap") {
    for (auto base : {100000U, 0xfffff000U}) for (unsigned mask : {1U, 2U, 3U}) {
        CAPTURE(base); CAPTURE(mask); edge::Escape owner; auto s = sample(base, mask);
        auto r = owner.step(s);
        if (!ENABLED) { actualEntry(owner, r, mask); continue; }
        deferred(owner, r);
        for (auto age : {1U, WINDOW_US - 1000U, WINDOW_US - 1U}) {
            s.t_us = base + age; deferred(owner, owner.step(s));
        }
        s.t_us = base + WINDOW_US; r = owner.step(s); actualEntry(owner, r, mask);
        CHECK(r.row.phase == edge::ScriptPhase::BRAKE); CHECK(r.row.brake);
        s.t_us += 1U; r = owner.step(s); CHECK(r.escape_required); CHECK_FALSE(r.entered);
    }
}

TEST_CASE("B9.4 D131 front-bit changes contact context and duplicates never renew the anchor") {
    if (!ENABLED) return;
    edge::Escape owner; auto s = sample(); const auto start = s.t_us; deferred(owner, owner.step(s));
    for (unsigned i = 1U; i < config::EDGE_PUSH_THROUGH_MS; ++i) {
        s.t_us = start + i * 1000U; s.line_mask = static_cast<std::uint8_t>(1U + i % 3U);
        s.opponent_side = (i & 1U) ? motion::Direction::LEFT : motion::Direction::RIGHT;
        s.applied_duty_l = s.applied_duty_r = (i & 1U) ? 1.0F : 0.0F;
        deferred(owner, owner.step(s)); deferred(owner, owner.step(s));
    }
    s.t_us = start + WINDOW_US; actualEntry(owner, owner.step(s), s.line_mask);
}

TEST_CASE("B9.4 D131 retained white cannot start but retains only the original running timer") {
    edge::Escape retained; auto s = sample(); s.line_updated = false;
    actualEntry(retained, retained.step(s), 1U);
    if (!ENABLED) return;
    edge::Escape active; s.line_updated = true; deferred(active, active.step(s));
    s.line_updated = false; s.t_us += WINDOW_US - 1U; deferred(active, active.step(s));
    ++s.t_us; actualEntry(active, active.step(s), 1U);
}

TEST_CASE("B9.4 D131 fresh black consumes allowance without escape exit or inward evidence") {
    if (!ENABLED) return;
    for (bool expire_black : {false, true}) {
        edge::Escape owner; auto s = sample(); deferred(owner, owner.step(s));
        s.line_mask = 0U; s.t_us += expire_black ? WINDOW_US : 1000U;
        const auto black = owner.step(s); CHECK_FALSE(owner.pushThroughActive());
        CHECK_FALSE(black.escape_required); CHECK_FALSE(black.entered); CHECK_FALSE(black.exited);
        CHECK_FALSE(black.inward_valid); CHECK(black.replans == 0U);
        s.line_mask = 2U; s.t_us += 1000U; actualEntry(owner, owner.step(s), 2U);
    }
}

TEST_CASE("B9.4 D131 eligibility loss cannot retry and permission loss consumes deferred allowance") {
    if (!ENABLED) return;
    for (bool permission : {false, true}) {
        edge::Escape owner; auto s = sample(); deferred(owner, owner.step(s)); ++s.t_us;
        if (permission) s.motion_permitted = false; else s.push_eligible = false;
        const auto lost = owner.step(s); CHECK_FALSE(owner.pushThroughActive());
        if (permission) { CHECK(lost.inhibit_motion); CHECK_FALSE(lost.escape_required);
            CHECK(lost.fault == edge::EscapeFault::NONE); }
        else actualEntry(owner, lost, 1U);
        ++s.t_us; s.motion_permitted = s.push_eligible = true;
        const auto next = owner.step(s); CHECK(next.escape_required); CHECK_FALSE(owner.pushThroughActive());
    }
}

TEST_CASE("B4 B9.4 D131 only real completed fresh-black escape exit rearms allowance") {
    if (!ENABLED) return;
    edge::Escape owner; auto s = sample(); deferred(owner, owner.step(s));
    s.line_mask = 0U; s.t_us += 1000U; owner.step(s);
    s.line_mask = 1U; s.t_us += 1000U; actualEntry(owner, owner.step(s), 1U);
    const auto entered = s.t_us; s.line_mask = 0U; s.t_us += config::TICK_US; owner.step(s);
    s.t_us = entered + config::TICK_US + config::EDGE_BACK_MS * 1000U; owner.step(s);
    s.t_us += static_cast<std::uint32_t>(config::EDGE_TURN_DEG * config::TURN_MS_PER_DEG * 1000.0F);
    s.line_updated = false; const auto retained = owner.step(s);
    CHECK(retained.escape_required); CHECK_FALSE(retained.exited);
    ++s.t_us; s.line_updated = true; const auto exit = owner.step(s);
    CHECK(exit.exited); CHECK_FALSE(exit.escape_required); CHECK_FALSE(exit.inward_valid);
    ++s.t_us; s.line_mask = 2U; deferred(owner, owner.step(s));
}

TEST_CASE("B4 B9.4 D131 deferral costs no replan and real entry retains all three replacements") {
    edge::Escape owner; auto s = sample(); auto r = owner.step(s);
    if (ENABLED) { s.t_us += WINDOW_US; r = owner.step(s); }
    actualEntry(owner, r, 1U);
    for (unsigned i = 1U; i <= config::EDGE_MAX_REPLANS; ++i) {
        ++s.t_us; s.line_mask = (i & 1U) ? 2U : 1U; r = owner.step(s);
        CHECK(r.replanned); CHECK(r.replans == i); CHECK(r.fault == edge::EscapeFault::NONE);
    }
    ++s.t_us; s.line_mask = 1U; r = owner.step(s);
    CHECK(r.fault == edge::EscapeFault::REPLAN_LIMIT); CHECK(r.inhibit_motion);
    CHECK_FALSE(r.replanned); CHECK(r.replans == config::EDGE_MAX_REPLANS);
}

TEST_CASE("B9.4 D131 reset alone restores a spent allowance without inherited timestamp") {
    if (!ENABLED) return;
    edge::Escape owner; auto s = sample(); deferred(owner, owner.step(s));
    s.line_mask = 0U; ++s.t_us; owner.step(s); owner.reset();
    CHECK_FALSE(owner.pushThroughActive()); s.line_mask = 3U; s.t_us += 777U;
    deferred(owner, owner.step(s)); s.t_us += WINDOW_US; actualEntry(owner, owner.step(s), 3U);
}

TEST_CASE("B4 B9.4 D131 freshblack does not consume unused invalid row context") {
    if (!ENABLED) return;
    edge::Escape owner; auto s = sample(); deferred(owner, owner.step(s));
    ++s.t_us; s.line_mask = 0U; s.imu_ok = true;
    s.heading_deg = std::numeric_limits<float>::quiet_NaN();
    s.opponent_side = static_cast<motion::Direction>(255U); const auto black = owner.step(s);
    CHECK_FALSE(owner.pushThroughActive()); CHECK_FALSE(black.escape_required);
    CHECK(black.fault == edge::EscapeFault::NONE); CHECK_FALSE(black.inward_valid);
}

TEST_CASE("B5 B9.4 D131 raw FC clears immediately even while confirmed FC remains on") {
    for (unsigned residual : {0U, 1U, 4U, 5U, 8U, 64U}) {
        Rig rig; rig.attack(); rig.white(1U); const auto first = rig.next();
        if (!ENABLED) { escaped(rig, first, 1U); continue; }
        attacking(rig, first, 1U); rig.opponent(residual); const auto lost = rig.next();
        CHECK((lost.opponent_mask & 2U) != 0U); escaped(rig, lost, 1U);
        CHECK((edgeFlags(lost) & logframe::ENTERED) != 0U);
    }
}

TEST_CASE("B5 B6 B9.4 D131 confirmed centered FC is required and contact is not required") {
    for (unsigned target : {2U, 3U, 5U, 6U, 7U}) {
        Rig rig; rig.input.imu_ok = false; rig.attack(false, 0U, target);
        rig.white(2U); const auto r = rig.next(); CHECK_FALSE(r.contact);
        if (ENABLED && target != 5U) { attacking(rig, r, 2U);
            CHECK(r.outputs.duty_l <= config::ATTACK_APPROACH_DUTY);
            CHECK(r.outputs.duty_r <= config::ATTACK_APPROACH_DUTY); }
        else escaped(rig, r, 2U);
    }
}

TEST_CASE("B5 B9.4 D131 phantom-filtered FC cannot be rescued by raw electrical detection") {
    Rig rig; rig.attack(false); rig.white(1U); const auto r = rig.next();
    CHECK(eventCount(r, core::Event::PHANTOM_SET) == 1U);
    CHECK(r.opponent_mask == 0U); escaped(rig, r, 1U);
}

TEST_CASE("B9.4 B15 D131 deferral records true new-white but no executed escape pulses") {
    Rig rig; const auto start = rig.attack(); rig.white(3U); const auto first = rig.next();
    CHECK((edgeFlags(first) & logframe::NEW_WHITE) != 0U); CHECK(first.line_mask == 3U);
    if (!ENABLED) { escaped(rig, first, 3U); return; }
    attacking(rig, first, 3U); const auto deadline = start + 1000U + WINDOW_US;
    attacking(rig, rig.at(deadline - 1U), 3U);
    const auto end = rig.at(deadline); escaped(rig, end, 3U);
    CHECK((edgeFlags(end) & logframe::ENTERED) != 0U);
    CHECK((edgeFlags(end) & (logframe::REPLANNED | logframe::EXITED)) == 0U);
    const auto after = rig.next(); CHECK((edgeFlags(after) & logframe::ENTERED) == 0U);
}

TEST_CASE("B9.4 D131 actual Robot duplicate cannot process changed input or renew push deadline") {
    if (!ENABLED) return;
    Rig rig; rig.attack(); rig.white(1U); attacking(rig, rig.next(), 1U);
    const auto start = rig.now, writes = rig.port.operations; rig.white(15U);
    rig.input.stop_requested = true; const auto duplicate = rig.at(start);
    CHECK_FALSE(duplicate.fresh); CHECK(duplicate.events.count == 0U);
    CHECK(duplicate.outputs.ui_state == State::ATTACK); CHECK(rig.port.operations == writes);
    rig.input.stop_requested = false; rig.white(1U);
    attacking(rig, rig.at(start + WINDOW_US - 1U), 1U);
    escaped(rig, rig.at(start + WINDOW_US), 1U);
}

TEST_CASE("B4 B9.4 D131 explicit retained source continues but expires at exact source-age bound") {
    if (!ENABLED) return;
    Rig rig(true); rig.attack(); rig.white(1U); const auto first = rig.next(2000U);
    APP_REQUIRE(first.line_updated); attacking(rig, first, 1U); const auto start = rig.now;
    rig.deliver = false; const auto retained = rig.at(start + 5899U);
    CHECK_FALSE(retained.line_updated); CHECK(retained.line_available); attacking(rig, retained, 1U);
    const auto expired = rig.at(start + 5900U); CHECK_FALSE(expired.line_available);
    CHECK(expired.contract_faults != 0U); CHECK(expired.outputs.ui_state == State::STOPPED);
    stopped(rig, expired);
}

TEST_CASE("B4 B9.4 D131 explicit fresh cadence cannot slide deadline on retained final tick") {
    if (!ENABLED) return;
    for (auto base : {0U, 0xfff00000U}) {
        Rig rig(true); rig.attack(true, base); rig.white(2U); rig.next(2000U);
        APP_REQUIRE(rig.last.line_updated); const auto start = rig.now;
        for (unsigned age = 1000U; age < WINDOW_US; age += 1000U)
            attacking(rig, rig.at(start + age), 2U);
        rig.deliver = false; const auto end = rig.at(start + WINDOW_US);
        CHECK_FALSE(end.line_updated); escaped(rig, end, 2U);
    }
}

TEST_CASE("B11 B9.4 D131 preserved new-white event permanently disqualifies old contact stall") {
    if (!ENABLED) return;
    Rig rig; rig.attack(); rig.white(1U); attacking(rig, rig.next(), 1U);
    rig.input.raw_heading_deg = 26.0F; const auto deflected = rig.next();
    attacking(rig, deflected, 1U); CHECK(eventCount(deflected, core::Event::STALL) == 0U);
    rig.white(0U); const auto clear = rig.next(); CHECK(clear.contact);
    const auto later = rig.next(config::STALL_MS * 1000U + 1000U);
    CHECK(later.outputs.ui_state == State::ATTACK); CHECK(eventCount(later, core::Event::STALL) == 0U);
}

TEST_CASE("B11 B9.4 D131 later contact and deflection revoke before any executed stall or limiter slot") {
    if (!ENABLED) return;
    Rig rig; rig.attack(false, 0U, 10U); rig.white(1U); attacking(rig, rig.next(), 1U);
    rig.input.ax_g = 2.0F; const auto contact = rig.next(); APP_REQUIRE(contact.contact);
    rig.input.ax_g = 0.0F;
    // Approach .60 reaches qualifying .80 after ten 1ms slew steps.
    for (unsigned i = 0U; i < 10U; ++i) rig.next();
    rig.input.raw_heading_deg = 26.0F; const auto result = rig.next();
    if (MOTORS_ALLOWED) { escaped(rig, result, 1U);
        CHECK((edgeFlags(result) & logframe::ENTERED) != 0U); }
    else attacking(rig, result, 1U);
    CHECK(eventCount(result, core::Event::STALL) == 0U);
    CHECK(eventCount(result, core::Event::REFLANK_PHASE) == 0U); CHECK_FALSE(result.all_in);
    if (!MOTORS_ALLOWED) return;
    freshContactAfterEscape(rig, rig.now);
    for (unsigned attempt = 0U; attempt < config::REFLANK_MAX_PER_10S; ++attempt) {
        rig.input.raw_heading_deg += 26.0F; const auto real = rig.next();
        CHECK(real.outputs.ui_state == State::REFLANK); CHECK_FALSE(real.all_in);
        CHECK(eventCount(real, core::Event::STALL) == 1U);
        freshContactAfterReflank(rig, rig.now);
    }
    rig.input.raw_heading_deg += 26.0F; CHECK(rig.next().all_in);
    rig.white(2U); attacking(rig, rig.next(), 2U); const auto anchor = rig.now;
    CHECK(rig.last.all_in); attacking(rig, rig.at(anchor + WINDOW_US - 1U), 2U);
    escaped(rig, rig.at(anchor + WINDOW_US), 2U);
}

TEST_CASE("B9.4 D131 real black chatter remains spent until a completed escape rearms") {
    if (!ENABLED) return;
    Rig rig; rig.attack(); rig.white(1U); attacking(rig, rig.next(), 1U);
    rig.white(0U); const auto black = rig.next(); CHECK(black.outputs.ui_state == State::ATTACK);
    CHECK((edgeFlags(black) & logframe::EXITED) == 0U);
    rig.white(1U); escaped(rig, rig.next(), 1U); freshContactAfterEscape(rig, rig.now);
    rig.white(2U); attacking(rig, rig.next(), 2U);
}

TEST_CASE("B9.4 B15 D131 due recorder frame preserves deferred state and actual white mask") {
    if (!ENABLED) return;
    Rig rig; const auto full = rig.attack();
    constexpr auto elapsed = (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U + 53000U;
    constexpr auto period = 1000000U / config::LOG_HZ;
    const auto due = full + period - elapsed % period;
    rig.at(due - 1000U); rig.white(3U); attacking(rig, rig.at(due), 3U);
    const auto r = rig.next(); APP_REQUIRE(r.frame_ready);
    CHECK(r.frame.data[4] == static_cast<unsigned>(State::ATTACK)); CHECK(r.frame.data[6] == 3U);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B9.4 D131 real Runtime fresh and retained frames reach the unchanged MotorGate") {
    RuntimeRig rig; rig.attack(); rig.fake.white_mask = 1U;
    bool saw = false; std::uint32_t anchor = 0U;
    for (unsigned i = 0U; i < config::EDGE_PUSH_THROUGH_MS + 8U; ++i) {
        APP_REQUIRE(rig.next()); const auto& r = rig.robot();
        if (r.line_mask == 0U) continue;
        if (!saw) { anchor = rig.owner.transaction().report().applied.feedback.applied_us; saw = true; }
        if (!ENABLED || r.outputs.ui_state == State::EDGE_ESCAPE) {
            CHECK(r.outputs.ui_state == State::EDGE_ESCAPE);
            for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
            if (ENABLED) CHECK(rig.owner.transaction().report().applied.feedback.applied_us - anchor >= WINDOW_US);
            return;
        }
        CHECK(r.outputs.ui_state == State::ATTACK); CHECK(r.line_mask == 1U);
        CHECK(rig.fake.enabled == (MOTORS_ALLOWED != 0)); CHECK(r.contract_faults == 0U);
    }
    CHECK_MESSAGE(false, "Runtime must observe front white then enter ordinary escape by the bound");
}

TEST_CASE("B14 B9.4 D131 Runtime opponentfault within deferral inhibits actual PWM and EN") {
    if (!ENABLED) return;
    RuntimeRig rig; rig.attack(); rig.fake.white_mask = 2U;
    bool seen = false;
    for (unsigned i = 0U; i < 6U; ++i) {
        APP_REQUIRE(rig.next());
        if (rig.robot().line_mask == 2U) { seen = true; break; }
    }
    APP_REQUIRE(seen); APP_REQUIRE(rig.robot().outputs.ui_state == State::ATTACK);
    rig.fake.opponent_error = 1U; rig.next();
    CHECK_FALSE(rig.robot().outputs.motors_enabled); CHECK_FALSE(rig.fake.enabled);
    for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
#endif

#if SUMOX_TIMING_EVIDENCE
TEST_CASE("B9.4 B15 D131 deferredwhite remains an edge exclusion for actual targetloss timing") {
    if (!ENABLED) return;
    p4_time::Rig rig(true); rig.approach(0U, 10U); rig.white(1U);
    const auto r = rig.step(rig.now + 1000U); CHECK(r.outputs.ui_state == State::ATTACK);
    CHECK(r.line_mask == 1U);
    CHECK(p4_time::count(r, p4_time::Detail::INTERRUPTED_EDGE) == (MOTORS_ALLOWED ? 1U : 0U));
    CHECK(p4_time::count(r, p4_time::Detail::LOSS_BRAKE_DECISION) == 0U);
    CHECK(p4_time::count(r, p4_time::Detail::LOSS_ZERO_APPLIED) == 0U);
}
#endif

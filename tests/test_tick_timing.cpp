// Tests D092 complete-tick accounting from the frozen public timing contract.
// Separates acquisition evidence from motor authority and decision/source clocks.
// Independent literal chronology, wire maxima and real Gate/recorder composition.
#include "fixtures/tick_timing_fixture.h"
#include <array>
#include <limits>
using namespace timing_test;

TEST_CASE("B14 D092 acquisition600 plus later401 counts1001 and warns at completion") {
    Rig rig;
    const auto decision = rig.go(600U), start = decision - 600U;
    const auto result = rig.submit(rig.receipt(start + 1100U, start + 1200U,
                                              decision, start + 1001U, 1001U));
    cleanTiming(result, 1001U);
    CHECK(event(result, core::Event::FAULT, 9).t_us == start + 1001U);
    CHECK(event(result, core::Event::FAULT, 9).value == 1U);
}

TEST_CASE("B14 D092 strict overrun threshold retains79980080199910001001 durations") {
    for (auto duration : {799U, 800U, 801U, 999U, 1000U, 1001U}) {
        Rig rig;
        const auto decision = rig.go(600U), start = decision - 600U;
        const auto result = rig.submit(rig.receipt(start + 1100U, start + 1200U,
                                                  decision, start + duration, duration));
        cleanTiming(result, duration);
        CHECK(count(result, core::Event::FAULT, 9) == (duration > 1000U ? 1U : 0U));
    }
}

TEST_CASE("B14 D092 equality is legal at every complete chronology boundary") {
    struct Row { std::uint32_t d, a, c, n, e; };
    const std::array<Row, 6> rows{{{0,0,0,0,1},{10,10,10,10,11},{10,11,11,11,11},
                                  {10,11,12,12,12},{10,11,12,13,13},{10,11,12,13,14}}};
    for (const auto row : rows) {
        Rig rig;
        const auto decision = rig.go(row.d), start = decision - row.d;
        cleanTiming(rig.submit(rig.receipt(start + row.n, start + row.e,
                                           start + row.a, start + row.c, row.c)), row.c);
    }
}

TEST_CASE("B14 D092 malformed duration chronology does not invalidate actual motor receipt") {
    for (unsigned variant = 0; variant < 8; ++variant) {
        Rig rig;
        const auto d = rig.go(600U), s = d - 600U;
        auto next = rig.receipt(s + 1100U, s + 1200U, d + 10U, s + 1001U, 1001U);
        if (variant == 0) next.previous.duration_valid = false;
        if (variant == 1) next.previous.execution_us = 1000U;
        if (variant == 2) next.previous.completed_us = d + 9U;
        if (variant == 3) next.timing.started_us = s + 1000U;
        if (variant == 4) next.timing.start_valid = false;
        if (variant == 5) next.timing.started_us = next.t_us + 1U;
        if (variant == 6) next.previous.completed_us = next.t_us + 1U;
        if (variant == 7) next.timing.started_us = s - 1U;
        badTiming(rig.submit(next), next.t_us);
    }
}

TEST_CASE("B14 D092 invalid pending start never falls back to decision clock") {
    for (unsigned variant = 0; variant < 4; ++variant) {
        Rig rig;
        const auto d = rig.go();
        auto pending = rig.at(d + 1000U, d + 900U);
        if (variant == 0) pending.timing.start_valid = false;
        if (variant == 1) pending.timing.started_us = pending.t_us + 1U;
        if (variant == 2) pending.timing.started_us = pending.t_us - 0x80000000U;
        if (variant == 3) pending.timing.started_us = pending.t_us - 0x80000001U;
        rig.submit(pending);
        auto next = rig.at(d + 2000U, d + 1900U);
        next.previous.execution_us = 0U;
        next.previous.completed_us = d + 1000U;
        const auto result = rig.submit(next);
        CHECK(result.ticks.ticks == 0U);
        CHECK(result.timing_incomplete);
        CHECK(result.contract_faults == 0U);
    }
}

TEST_CASE("B14 D092 common start anchor rejects half range even when adjacent legs are short") {
    for (auto span : {0x7FFFFFFFU, 0x80000000U, 0x80000001U}) {
        Rig rig;
        const auto d = rig.go(600U), s = d - 600U;
        const auto result = rig.submit(rig.receipt(s + span - 1U, s + span, d, s + 1001U, 1001U));
        if (span == 0x7FFFFFFFU) cleanTiming(result, 1001U);
        else badTiming(result, s + span);
    }
}

TEST_CASE("B14 D092 large unambiguous full durations remain counted without invented ceiling") {
    Rig rig;
    const auto d = rig.go(600U), s = d - 600U;
    cleanTiming(rig.submit(rig.receipt(s + 0x7FFFFFFFU, s + 0x7FFFFFFFU,
                                      d, s + 0x7FFFFFFFU, 0x7FFFFFFFU)), 0x7FFFFFFFU);
}

TEST_CASE("B14 D092 natural wrap preserves duration and completion event before current STOP") {
    Rig rig;
    const auto d = rig.go(600U, 0U - 5163020U), s = d - 600U;
    CHECK(d == 0xFFFFFFECU);
    auto next = rig.receipt(s + 1100U, s + 1200U, d + 10U, s + 1001U, 1001U);
    next.stop_requested = true;
    const auto result = rig.submit(next);
    cleanTiming(result, 1001U);
    CHECK(result.outputs.ui_state == core::State::STOPPED);
    CHECK(event(result, core::Event::FAULT, 9).t_us == s + 1001U);
    CHECK(event(result, core::Event::STATE_CHANGE).t_us == s + 1200U);
    unsigned warning = 99, state = 99;
    for (unsigned i = 0; i < result.events.count; ++i) {
        if (result.events.entries[i].type == core::Event::FAULT && result.events.entries[i].detail == 9) warning = i;
        if (result.events.entries[i].type == core::Event::STATE_CHANGE) state = i;
    }
    CHECK(warning < state);
}

TEST_CASE("B14 D092 legacy mode ignores acquisition garbage and preserves decision duration") {
    Rig rig(false);
    rig.input.timing.start_valid = false;
    const auto d = rig.go(0x80000000U);
    auto next = rig.receipt(d - 1U, d + 2000U, d, d + 1001U, 1001U);
    next.timing.start_valid = false;
    cleanTiming(rig.submit(next), 1001U);
}

TEST_CASE("B14 D092 fixed selector mismatch rejects bounded receipts but recovery counts later") {
    for (const bool selected : {false, true}) {
        Rig rig(selected);
        const auto d = rig.go();
        auto mismatch = rig.at(d + 1000U, d + 1000U);
        mismatch.timing.explicit_start = !selected;
        badTiming(rig.submit(mismatch), mismatch.t_us);
        auto result = rig.submit(rig.at(d + 2000U, d + 2000U));
        CHECK(result.ticks.ticks == 0U);
        CHECK(result.timing_incomplete);
        CHECK(count(result, core::Event::FAULT, 9) == 0U);
        result = rig.submit(rig.at(d + 3000U, d + 3000U));
        CHECK(result.ticks.ticks == 1U);
        CHECK(result.timing_incomplete);
        CHECK(result.contract_faults == 0U);
    }
}

TEST_CASE("B14 D092 BOOT first admission selects timing even before initialization") {
    Rig rig;
    rig.input.initialization_complete = false;
    CHECK(rig.step(0U).outputs.ui_state == core::State::BOOT);
    rig.input.initialization_complete = true;
    rig.input.timing.explicit_start = false;
    const auto d = rig.go(0U, 1000U);
    const auto result = rig.step(d + 1000U);
    badTiming(result, d + 1000U);
}

TEST_CASE("B14 D092 duplicate decision cannot replace saved start mode or count a receipt") {
    Rig rig;
    const auto d = rig.go(600U), s = d - 600U;
    auto duplicate = rig.at(d, d + 1U);
    duplicate.timing.explicit_start = false;
    duplicate.timing.start_valid = false;
    duplicate.previous.token = 0;
    duplicate.stop_requested = true;
    const auto repeated = rig.submit(duplicate);
    CHECK_FALSE(repeated.fresh);
    CHECK(repeated.token == rig.last.token);
    CHECK_FALSE(repeated.frame_ready);
    CHECK(repeated.events.count == 0U);
    CHECK(repeated.ticks.ticks == 0U);
    cleanTiming(rig.submit(rig.receipt(s + 1100U, s + 1200U, d, s + 1001U, 1001U)), 1001U);
}

TEST_CASE("B14 D092 bad token and application time remain motor faults despite valid timing shape") {
    for (unsigned variant = 0; variant < 4; ++variant) {
        Rig rig;
        const auto d = rig.go(600U), s = d - 600U;
        auto next = rig.receipt(s + 1100U, s + 1200U, d, s + 1001U, 1001U);
        if (variant == 0) --next.previous.token;
        if (variant == 1) ++next.previous.token;
        if (variant == 2) next.previous.applied_us = d - 1U;
        if (variant == 3) next.previous.applied_us = next.t_us + 1U;
        const auto result = rig.submit(next);
        CHECK((result.contract_faults & fsm::APPLICATION_CONTRACT) != 0U);
        CHECK(result.outputs.ui_state == core::State::STOPPED);
        CHECK(result.ticks.ticks == 0U);
        CHECK(result.timing_incomplete);
    }
}

TEST_CASE("B14 D092 duty-invalid receipt retains identity-time timing count and motor fault") {
    Rig rig;
    const auto d = rig.go(600U), s = d - 600U;
    auto next = rig.receipt(s + 1100U, s + 1200U, d, s + 1001U, 1001U);
    next.previous.duty_l = std::numeric_limits<float>::quiet_NaN();
    const auto result = rig.submit(next);
    CHECK((result.contract_faults & fsm::APPLICATION_CONTRACT) != 0U);
    CHECK(result.outputs.ui_state == core::State::STOPPED);
    CHECK(result.ticks.ticks == 1U);
    CHECK(result.ticks.max_us == 1001U);
    CHECK_FALSE(result.timing_incomplete);
}

TEST_CASE("B14 D092 preGO malformed timing is excluded and GO acquisition is included later") {
    Rig rig;
    const auto release = rig.release();
    auto countdown = rig.at(release + 5099000U, release + 5099001U);
    countdown.timing.start_valid = false;
    rig.submit(countdown);
    const auto d = release + 5100000U, s = d - 600U;
    auto go = rig.at(d, s);
    go.previous.duration_valid = false;
    const auto result = rig.submit(go);
    CHECK(result.lifecycle.gate.go);
    CHECK(event(result, core::Event::GO).t_us == d);
    CHECK(result.ticks.ticks == 0U);
    CHECK_FALSE(result.timing_incomplete);
    cleanTiming(rig.submit(rig.receipt(s + 1100U, s + 1200U, d, s + 1001U, 1001U)), 1001U);
}

TEST_CASE("B3 B14 D092 STOP at GO deadline suppresses GO and counts no match timing") {
    Rig rig;
    const auto release = rig.release();
    auto stop = rig.at(release + 5100000U, release + 5099400U);
    stop.stop_requested = true;
    stop.previous.duration_valid = false;
    const auto result = rig.submit(stop);
    CHECK_FALSE(result.lifecycle.gate.go);
    CHECK(count(result, core::Event::GO) == 0U);
    CHECK(result.outputs.ui_state == core::State::STOPPED);
    const auto tail = rig.step(stop.t_us + 2000U);
    CHECK(tail.ticks.ticks == 0U);
    CHECK_FALSE(tail.timing_incomplete);
}

TEST_CASE("B15 D092 cancellation final receipt stays excluded even with malformed timing") {
    Rig rig;
    const auto release = rig.release();
    rig.step(release + 1000U, core::ButtonLevel::MODE);
    auto cancel = rig.at(release + 21000U, release + 21001U);
    cancel.button = core::ButtonLevel::MODE;
    const auto result = rig.submit(cancel);
    CHECK(result.outputs.ui_state == core::State::IDLE);
    auto tail = rig.at(release + 22000U, release + 22000U);
    tail.previous.duration_valid = false;
    const auto final = rig.submit(tail);
    CHECK(final.frame_ready);
    CHECK(final.ticks.ticks == 0U);
    CHECK_FALSE(final.timing_incomplete);
    CHECK(rig.source.phase() == recorder::AttemptPhase::SEALED);
}

TEST_CASE("B14 D092 accepted START after cancellation preserves lifetime timing selector") {
    for (const bool selected : {false, true}) {
        Rig rig(selected);
        const auto released = rig.release();
        rig.step(released + 1000U, core::ButtonLevel::MODE);
        auto cancel = rig.at(released + 21000U, released + 21001U);
        cancel.button = core::ButtonLevel::MODE;
        cancel.timing.explicit_start = !selected;
        CHECK(rig.submit(cancel).outputs.ui_state == core::State::IDLE);
        auto tail = rig.at(released + 22000U, released + 22000U);
        tail.previous.duration_valid = false;
        CHECK_FALSE(rig.submit(tail).timing_incomplete);
        rig.input.timing.explicit_start = !selected;
        const auto next_go = rig.go(0U, released + 23000U);
        CHECK(rig.last.ticks.ticks == 0U);
        CHECK_FALSE(rig.last.timing_incomplete);
        badTiming(rig.step(next_go + 1000U), next_go + 1000U);
    }
}

TEST_CASE("B14 D092 fresh and retained IMU source age remains anchored to post-acquisition decision") {
    Rig rig(true, false, true);
    const auto release = rig.release();
    const auto d = release + 5100000U, s = d - 600U;
    auto go = rig.at(d, s);
    go.imu.checked_us = d - 100U;
    go.imu.observation_us = d - 100U;
    const auto result = rig.submit(go);
    CHECK(result.lifecycle.gate.go);
    CHECK(result.contract_faults == 0U);
    CHECK(result.heading.origin_t_us == d - 100U);
    CHECK(result.heading.heading_age_us == 100U);
    auto retained = rig.receipt(d + 900U, d + 1000U, d, d + 401U, 1001U);
    retained.imu.heading_updated = false;
    retained.imu.gyro = core::ImuPresence::ABSENT;
    retained.imu.accel = core::ImuPresence::ABSENT;
    retained.imu.observation_us = go.imu.observation_us;
    retained.imu.sequence = go.imu.sequence;
    const auto next = rig.submit(retained);
    cleanTiming(next, 1001U);
    CHECK(next.heading.heading_age_us == 1100U);
    CHECK_FALSE(next.heading.heading_updated);
    CHECK(next.imu_available);
}

TEST_CASE("B15 D092 complete duration65535 versus65536 preserves maxima and frame status") {
    for (auto duration : {65535U, 65536U}) {
        Rig rig;
        const auto d = rig.go(600U), s = d - 600U;
        auto stop = rig.receipt(s + duration, s + duration + 1U, d, s + duration, duration);
        stop.stop_requested = true;
        rig.submit(stop);
        const auto tail = rig.step(stop.t_us + 1000U);
        CHECK(tail.frame_ready);
        CHECK(tail.ticks.max_us == duration);
        CHECK(tail.frame.data[23] == 255U);
        CHECK(tail.frame.data[24] == 255U);
        CHECK(tail.frame_status == (duration == 65535U ? logframe::PackStatus::OK : logframe::PackStatus::CLAMPED));
        CHECK(rig.source.summary().ticks.max_us == duration);
        CHECK(rig.source.frames().clampedCount() == (duration == 65536U ? 1U : 0U));
    }
}

TEST_CASE("B14 B15 D092 real MotorGate receipt and final STOP duration reach sealed recorder") {
    Rig rig(true, true);
    const auto d = rig.go(600U), s = d - 600U;
    CHECK(rig.previous.applied_us == d);
    auto active = rig.at(d + 1000U, d + 800U);
    active.previous.completed_us = d + 401U;
    active.previous.execution_us = 1001U;
    CHECK(rig.submit(active, 11U, 21U).ticks.max_us == 1001U);
    auto stop = rig.at(d + 3000U, d + 1600U);
    stop.stop_requested = true;
    const auto stopping = rig.submit(stop, 15U, 25U);
    CHECK(stopping.outputs.ui_state == core::State::STOPPED);
    CHECK(rig.source.phase() == recorder::AttemptPhase::DRAINING);
    CHECK(rig.previous.applied_us == stop.t_us + 15U);
    const auto tail = rig.submit(rig.at(d + 4000U, d + 3900U));
    CHECK(tail.frame_ready);
    CHECK(tail.frame_token == stopping.token);
    CHECK(tail.ticks.ticks == 3U);
    CHECK(tail.ticks.max_us == 1425U); // Final STOP acquisition1400 + remaining25.
    CHECK(tail.ticks.overruns == 2U);
    CHECK(tail.frame.data[23] == 145U);
    CHECK(tail.frame.data[24] == 5U);
    CHECK(rig.source.phase() == recorder::AttemptPhase::SEALED);
    CHECK(rig.source.summary().ticks.ticks == 3U);
    CHECK(rig.source.summary().ticks.max_us == 1425U);
    CHECK(rig.source.summary().ticks.overruns == 2U);
    CHECK_FALSE(rig.source.summary().final_frame_missing);
    CHECK_FALSE(rig.source.summary().timing_incomplete);
    CHECK(rig.source.summary().identity_rejected == 0U);
    CHECK(rig.source.frames().at(rig.source.frames().size() - 1U)->bytes.data[4] == 10U);
    const auto more = rig.step(d + 5000U);
    CHECK(more.ticks.ticks == 3U);
    CHECK_FALSE(more.frame_ready);
#if MOTORS_ALLOWED
    CHECK(rig.port.nonzero_writes > 0U);
#else
    CHECK(rig.port.nonzero_writes == 0U);
#endif
    CHECK_FALSE(rig.port.enabled);
    CHECK(s == d - 600U);
}

TEST_CASE("B14 D092 reset clears timing selection and pending start while tokens and recorder persist") {
    Rig rig;
    const auto d = rig.go(600U);
    rig.submit(rig.receipt(d + 500U, d + 600U, d, d + 401U, 1001U));
    const auto old_token = rig.last.token, old_epoch = rig.source.summary().epoch_token;
    const auto old_frames = rig.source.frames().size();
    rig.source.onRobotReset();
    rig.robot.reset();
    rig.input.timing.explicit_start = false;
    rig.input.timing.start_valid = false;
    auto first = rig.at(d + 2000U, d + 2001U);
    first.previous.token = old_token;
    const auto restarted = rig.submit(first);
    CHECK(restarted.token > old_token);
    CHECK(restarted.contract_faults == 0U);
    CHECK(restarted.ticks.ticks == 0U);
    CHECK_FALSE(restarted.timing_incomplete);
    CHECK(rig.source.summary().epoch_token == old_epoch);
    CHECK(rig.source.frames().size() == old_frames);
    CHECK(rig.source.phase() == recorder::AttemptPhase::INTERRUPTED);
    const auto next_go = rig.go(0U, d + 3000U);
    cleanTiming(rig.submit(rig.receipt(next_go + 2000U, next_go + 2000U,
                                     next_go, next_go + 1001U, 1001U)), 1001U);
}

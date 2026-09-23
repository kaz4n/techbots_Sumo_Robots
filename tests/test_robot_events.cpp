// Checks D-060 event metadata and delayed frame/duration evidence on the real Robot.
// Synthetic receipts are explicit settings and duration fixtures, never board measurements.
// Literal wire fields, ordering, phase cadence and evidence loss are independently asserted.
#include "robot_scenario.h"
#include <array>
#include <limits>

using namespace robot_test;

namespace {
unsigned indexOf(const fsm::RobotResult& result, core::Event type, int detail = -1) {
    for (unsigned index = 0U; index < result.events.count && index < 21U; ++index) {
        const auto& entry = result.events.entries[index];
        if (entry.type == type && (detail < 0 || entry.detail == static_cast<unsigned>(detail))) return index;
    }
    CHECK(false);
    return 21U;
}

fsm::RobotResult timedReceipt(Rig& rig, std::uint32_t now, std::uint32_t execution) {
    auto input = rig.at(now);
    input.previous.completed_us = rig.last_time + execution;
    input.previous.execution_us = execution;
    return rig.submit(input);
}
} // namespace

TEST_CASE("B15 Robot START GO and state metadata preserve qualified source times") {
    Rig rig;
    const auto anchor = release(rig, select(rig, Mode::ARC_L));
    const auto start = event(rig.last, core::Event::START_RELEASE);
    CHECK(start.t_us == anchor);
    CHECK(start.detail == 5U);
    CHECK(start.value == 0U);
    const auto state = event(rig.last, core::Event::STATE_CHANGE);
    CHECK(state.detail == static_cast<unsigned>(State::IDLE));
    CHECK(state.value == static_cast<unsigned>(State::COUNTDOWN));
    CHECK(indexOf(rig.last, core::Event::START_RELEASE) < indexOf(rig.last, core::Event::STATE_CHANGE));
    const auto go = rig.step(anchor + 5100000U);
    const auto departure = event(go, core::Event::GO);
    CHECK(departure.t_us == anchor + 5100000U);
    CHECK(departure.detail == 5U);
    CHECK(departure.value == 0U);
    CHECK(indexOf(go, core::Event::GO) < indexOf(go, core::Event::STATE_CHANGE));
    CHECK(event(go, core::Event::STATE_CHANGE).detail == static_cast<unsigned>(State::COUNTDOWN));
    CHECK(event(go, core::Event::STATE_CHANGE).value == static_cast<unsigned>(State::OPENER));
}

TEST_CASE("B15 Robot persistent line at GO reports entered without invented new white") {
    Rig rig;
    rig.lines(1U);
    const auto time = go(rig);
    const auto edge = event(rig.last, core::Event::EDGE);
    CHECK(edge.t_us == time);
    CHECK(edge.detail == 2U);
    CHECK(edge.value == 1U);
    CHECK(indexOf(rig.last, core::Event::GO) < indexOf(rig.last, core::Event::EDGE));
    CHECK(indexOf(rig.last, core::Event::EDGE) < indexOf(rig.last, core::Event::STATE_CHANGE));
    CHECK(count(rig.step(time + 1U), core::Event::EDGE) == 0U);
}

TEST_CASE("B15 Robot FIRST_NONZERO waits for actual enabled application and records scaled bytes") {
    Rig rig;
    rig.apply_enabled = false;
    const auto time = go(rig, Mode::DIRECT);
    CHECK(count(rig.last, core::Event::FIRST_NONZERO_DUTY) == 0U);
    CHECK(count(rig.step(time + 50000U), core::Event::FIRST_NONZERO_DUTY) == 0U);
    CHECK(rig.last.outputs.duty_l == doctest::Approx(0.85F));
    rig.apply_enabled = true;
    rig.applied_scale = 0.5F;
    auto sample = rig.at(time + 51000U);
    sample.previous.applied_us = time + 50017U;
    sample.previous.completed_us = time + 50023U;
    sample.previous.execution_us = 23U;
    const auto result = rig.submit(sample);
    const auto applied = event(result, core::Event::FIRST_NONZERO_DUTY);
    CHECK(applied.t_us == time + 50017U);
    CHECK(applied.detail == 3U);
    CHECK(applied.value == 0x3636U); // round(0.425*127)=54 per side.
    CHECK(count(rig.step(time + 52000U), core::Event::FIRST_NONZERO_DUTY) == 0U);
}

TEST_CASE("B15 Robot tiny actual nonzero keeps wheel evidence even when both bytes round zero") {
    Rig rig;
    const auto time = go(rig, Mode::DIRECT);
    CHECK(rig.last.outputs.duty_l > 0.0F);
    CHECK(rig.last.outputs.duty_l < 0.001F);
    const auto result = rig.step(time + 1000U);
    const auto applied = event(result, core::Event::FIRST_NONZERO_DUTY);
    CHECK(applied.t_us == time);
    CHECK(applied.detail == 3U);
    CHECK(applied.value == 0U);
}

TEST_CASE("B15 Robot receipt events precede current STOP across numeric timestamp wrap") {
    Rig rig;
    rig.apply_enabled = false;
    const std::uint32_t base = 0U - 5163020U;
    const auto time = go(rig, Mode::SIDESTEP_R, base);
    CHECK(time == 0xffffffecU);
    rig.apply_enabled = true;
    auto sample = rig.at(1000U);
    sample.previous.applied_us = 0xfffffff6U;
    sample.previous.completed_us = 0xfffffff7U;
    sample.previous.execution_us = 11U;
    sample.stop_requested = true;
    const auto result = rig.submit(sample);
    CHECK(event(result, core::Event::FIRST_NONZERO_DUTY).t_us == 0xfffffff6U);
    CHECK(event(result, core::Event::STATE_CHANGE).t_us == 1000U);
    CHECK(indexOf(result, core::Event::FIRST_NONZERO_DUTY) < indexOf(result, core::Event::STATE_CHANGE));
    CHECK(result.outputs.ui_state == State::STOPPED);
    CHECK(result.contract_faults == 0U);
    zero(result);
}

TEST_CASE("B15 Robot final arbitration suppresses provisional contact on STOP or edge") {
    for (const bool stop : {false, true}) {
        Rig rig;
        rig.opponent(2U);
        const auto time = go(rig, Mode::DIRECT);
        rig.step(time + 1000U);
        rig.input.ax_g = 2.0F;
        rig.input.stop_requested = stop;
        if (!stop) rig.lines(1U);
        const auto result = rig.step(time + 2000U);
        CHECK(result.outputs.ui_state == (stop ? State::STOPPED : State::EDGE_ESCAPE));
        CHECK_FALSE(result.contact);
        CHECK(count(result, core::Event::CONTACT) == 0U);
        CHECK(count(result, core::Event::PHANTOM_SET) == 0U); // Current impact blocks marking.
    }
}

TEST_CASE("B15 D059 Robot PHANTOM_SET projects raw memory into match world angle") {
    Rig rig;
    rig.input.raw_heading_deg = 1010.0F;
    rig.opponent(3U);
    const auto time = go(rig, Mode::DIRECT);
    CHECK(rig.last.outputs.ui_state == State::TRACK);
    rig.step(time + 1000U);
    rig.lines(1U);
    const auto result = rig.step(time + 2000U);
    const auto phantom = event(result, core::Event::PHANTOM_SET);
    CHECK(phantom.detail == 0U);
    CHECK(phantom.value == static_cast<std::uint16_t>(-600));
    CHECK(phantom.t_us == time + 2000U);
    CHECK(result.opponent_mask == 0U);
    CHECK(indexOf(result, core::Event::EDGE) < indexOf(result, core::Event::PHANTOM_SET));
    CHECK(count(rig.step(time + 3000U), core::Event::PHANTOM_SET) == 0U);
}

TEST_CASE("B15 Robot START frame waits for matching application and uses raw preGO yaw") {
    Rig rig;
    rig.input.raw_heading_deg = 720.0F;
    const auto anchor = release(rig, idle(rig));
    const auto token = rig.last.token;
    CHECK_FALSE(rig.last.frame_ready);
    const auto result = rig.step(anchor + 1000U);
    CHECK(result.frame_ready);
    CHECK(result.frame_token == token);
    CHECK(result.frame_status == logframe::PackStatus::OK);
    CHECK(u32(result.frame, 0U) == 0U);
    CHECK(result.frame.data[4] == static_cast<unsigned>(State::COUNTDOWN));
    CHECK(result.frame.data[5] == 1U);
    CHECK(u32(result.frame, 8U) == 72000U);
    CHECK(result.frame.data[18] == 0U);
    CHECK(result.frame.data[19] == 0U);
    CHECK(result.skipped_frames == 0U);
}

TEST_CASE("B15 Robot25Hz frame cadence is phase anchored and delayed calls count missing slots") {
    Rig rig;
    const auto anchor = release(rig, idle(rig));
    CHECK(rig.step(anchor + 1U).frame_ready);
    CHECK_FALSE(rig.step(anchor + 39999U).frame_ready);
    CHECK_FALSE(rig.step(anchor + 40000U).frame_ready);
    const auto due_token = rig.last.token;
    const auto due = rig.step(anchor + 40001U);
    CHECK(due.frame_ready);
    CHECK(due.frame_token == due_token);
    CHECK(u32(due.frame, 0U) == 40U);
    CHECK_FALSE(rig.step(anchor + 200000U).frame_ready);
    CHECK(rig.last.skipped_frames == 3U); //80,120,160ms;200ms captures current data once.
    const auto delayed_token = rig.last.token;
    const auto delayed = rig.step(anchor + 200001U);
    CHECK(delayed.frame_ready);
    CHECK(delayed.frame_token == delayed_token);
    CHECK(u32(delayed.frame, 0U) == 200U);
    CHECK(delayed.skipped_frames == 3U);
}

TEST_CASE("B15 Robot match frames contain match yaw and actual downscaled duty") {
    Rig rig;
    rig.input.raw_heading_deg = 720.0F;
    const auto time = go(rig, Mode::DIRECT);
    rig.step(time + 20000U);
    rig.input.raw_heading_deg = 721.0F;
    // GO is 20ms after a START-anchored 40ms slot; GO+60ms is the next slot.
    rig.step(time + 60000U);
    const auto prior = rig.last;
    rig.applied_scale = 0.5F;
    const auto result = rig.step(time + 60001U);
    CHECK(result.frame_ready);
    CHECK(result.frame_token == prior.token);
    CHECK(u32(result.frame, 8U) == 100U);
    CHECK(result.frame.data[18] == static_cast<unsigned>(std::floor(prior.outputs.duty_l * 0.5F * 127.0F + 0.5F)));
    CHECK(result.frame.data[19] == static_cast<unsigned>(std::floor(prior.outputs.duty_r * 0.5F * 127.0F + 0.5F)));
    CHECK((result.frame.data[22] & 1U) != 0U);
}

TEST_CASE("B15 Robot emitted invalid frame retains codec status zero bytes and loss evidence") {
    Rig rig;
    rig.input.raw_gyro_z_dps = std::numeric_limits<float>::quiet_NaN();
    const auto anchor = release(rig, idle(rig));
    const auto result = rig.step(anchor + 1000U);
    CHECK(result.frame_ready);
    CHECK(result.frame_status == logframe::PackStatus::INVALID);
    CHECK(result.recording_incomplete);
    CHECK(result.skipped_frames == 0U);
    CHECK(result.contract_faults == 0U);
    for (const auto byte : result.frame.data) CHECK(byte == 0U);
}

TEST_CASE("B15 D060 Robot frame gyro explicitly preserves raw pre-bias input") {
    Rig rig;
    rig.input.previous_bias_dps = 5.0F;
    rig.input.raw_gyro_z_dps = 123.0F;
    const auto anchor = release(rig, idle(rig));
    const auto result = rig.step(anchor + 1000U);
    CHECK(result.frame_ready);
    CHECK(result.frame_status == logframe::PackStatus::OK);
    CHECK(result.frame.data[12] == 0xceU); //1230 = 0x04ce, not1180.
    CHECK(result.frame.data[13] == 0x04U);
    CHECK(result.contract_faults == 0U);
}

TEST_CASE("B15 Robot emitted clamped frame is explicit without a skipped candidate") {
    Rig rig;
    rig.input.raw_heading_deg = 30000000.0F;
    const auto anchor = release(rig, idle(rig));
    const auto result = rig.step(anchor + 1000U);
    CHECK(result.frame_ready);
    CHECK(result.frame_status == logframe::PackStatus::CLAMPED);
    CHECK(result.recording_incomplete);
    CHECK(result.skipped_frames == 0U);
    CHECK(result.contract_faults == 0U);
    CHECK(u32(result.frame, 8U) == 0x7fffffffU);
}

TEST_CASE("B15 Robot missing application loses pending frame rather than inventing duty") {
    Rig rig;
    const auto anchor = release(rig, idle(rig));
    auto sample = rig.at(anchor + 1000U);
    sample.previous.applied_valid = false;
    const auto result = rig.submit(sample);
    CHECK_FALSE(result.frame_ready);
    CHECK(result.skipped_frames == 1U);
    CHECK(result.recording_incomplete);
    CHECK((result.contract_faults & fsm::APPLICATION_CONTRACT) != 0U);
    CHECK(result.outputs.ui_state == State::STOPPED);
    zero(result);
}

TEST_CASE("B14 B15 Robot timing includes GO and one final inhibited stop receipt only") {
    Rig rig;
    const auto time = go(rig, Mode::WAIT);
    CHECK(rig.last.ticks.ticks == 0U);
    CHECK(rig.step(time + 1000U).ticks.ticks == 1U);
    rig.input.stop_requested = true;
    const auto stopped = rig.step(time + 2000U);
    CHECK(stopped.ticks.ticks == 2U);
    const auto stopped_token = stopped.token;
    rig.input.stop_requested = false;
    const auto flush = rig.step(time + 3000U);
    CHECK(flush.ticks.ticks == 3U);
    CHECK(flush.frame_ready);
    CHECK(flush.frame_token == stopped_token);
    CHECK(flush.frame.data[4] == static_cast<unsigned>(State::STOPPED));
    CHECK(flush.frame.data[18] == 0U);
    CHECK(flush.frame.data[19] == 0U);
    const auto later = rig.step(time + 100000U);
    CHECK(later.ticks.ticks == 3U);
    CHECK_FALSE(later.frame_ready);
    CHECK_FALSE(later.timing_incomplete);
}

TEST_CASE("B14 Robot1000us overrun is strict and uses supplied completion timestamp") {
    for (const std::uint32_t duration : {999U, 1000U, 1001U}) {
        Rig rig;
        const auto time = go(rig, Mode::WAIT);
        const auto result = timedReceipt(rig, time + 2000U, duration);
        CHECK(result.ticks.ticks == 1U);
        CHECK(result.ticks.overruns == (duration > 1000U ? 1U : 0U));
        CHECK(result.ticks.max_us == duration);
        CHECK_FALSE(result.timing_incomplete);
        CHECK(count(result, core::Event::FAULT, 9) == (duration > 1000U ? 1U : 0U));
        if (duration > 1000U) {
            const auto warning = event(result, core::Event::FAULT, 9);
            CHECK(warning.t_us == time + duration);
            CHECK(warning.value == 1U);
        }
        CHECK(result.contract_faults == 0U);
    }
}

TEST_CASE("B14 D060 Robot malformed match duration is incomplete evidence without motor fault") {
    for (unsigned variant = 0U; variant < 4U; ++variant) {
        Rig rig;
        const auto time = go(rig, Mode::WAIT);
        auto sample = rig.at(time + 2000U);
        if (variant == 0U) sample.previous.duration_valid = false;
        if (variant == 1U) sample.previous.completed_us = time + 2001U;
        if (variant == 2U) sample.previous.execution_us = 1U;
        if (variant == 3U) {
            sample.previous.applied_us = time + 10U;
            sample.previous.completed_us = time + 9U;
            sample.previous.execution_us = 9U;
        }
        const auto result = rig.submit(sample);
        CHECK(result.timing_incomplete);
        CHECK(result.ticks.ticks == 0U);
        CHECK(result.contract_faults == 0U);
        CHECK(result.outputs.ui_state == State::OPENER);
        const auto warning = event(result, core::Event::FAULT, 9);
        CHECK(warning.value == 4U);
        CHECK(warning.t_us == time + 2000U);
        auto again = rig.at(time + 3000U);
        again.previous.duration_valid = false;
        CHECK(count(rig.submit(again), core::Event::FAULT, 9) == 0U);
    }
}

TEST_CASE("B14 D060 Robot preGO missing duration neither counts nor marks match incomplete") {
    Rig rig;
    const auto anchor = release(rig, idle(rig));
    auto sample = rig.at(anchor + 1000U);
    sample.previous.duration_valid = false;
    const auto result = rig.submit(sample);
    CHECK_FALSE(result.timing_incomplete);
    CHECK(result.ticks.ticks == 0U);
    CHECK(count(result, core::Event::FAULT, 9) == 0U);
    sample = rig.at(anchor + 2000U);
    sample.previous.execution_us = 5000U;
    CHECK_FALSE(rig.submit(sample).timing_incomplete);
}

TEST_CASE("B15 Robot countdown cancellation flushes one final frame and no match timing") {
    Rig rig;
    const auto anchor = release(rig, idle(rig));
    rig.step(anchor + 1000U, Button::MODE);
    const auto canceled = rig.step(anchor + 21000U, Button::MODE);
    CHECK(canceled.outputs.ui_state == State::IDLE);
    const auto token = canceled.token;
    const auto flush = rig.step(anchor + 22000U);
    CHECK(flush.frame_ready);
    CHECK(flush.frame_token == token);
    CHECK(flush.frame.data[4] == static_cast<unsigned>(State::IDLE));
    CHECK(flush.ticks.ticks == 0U);
    CHECK_FALSE(flush.timing_incomplete);
    CHECK_FALSE(rig.step(anchor + 100000U).frame_ready);
}

TEST_CASE("B14 B15 Robot IMU low-battery and watchdog warnings have explicit episodes") {
    Rig rig;
    rig.input.imu_ok = false;
    rig.input.vbat_v = 10.799F;
    rig.input.reset_cause = fsm::ResetCause::WATCHDOG;
    auto result = rig.step(0U);
    CHECK(event(result, core::Event::FAULT, 1).value == 0U);
    CHECK(event(result, core::Event::FAULT, 4).value == 0U);
    CHECK(event(result, core::Event::FAULT, 10).value == 1U);
    CHECK(indexOf(result, core::Event::FAULT, 1) < indexOf(result, core::Event::FAULT, 4));
    CHECK(indexOf(result, core::Event::FAULT, 4) < indexOf(result, core::Event::FAULT, 10));
    CHECK(count(rig.step(1000U), core::Event::FAULT) == 0U);
    rig.input.imu_ok = true;
    rig.input.vbat_v = 10.8F;
    result = rig.step(2000U);
    CHECK_FALSE(result.low_battery);
    CHECK(count(result, core::Event::FAULT) == 0U);
    rig.input.imu_ok = false;
    rig.input.vbat_v = 10.79F;
    result = rig.step(3000U);
    CHECK(count(result, core::Event::FAULT, 1) == 1U);
    CHECK(count(result, core::Event::FAULT, 4) == 1U);
    CHECK(count(result, core::Event::FAULT, 10) == 0U);
    CHECK(result.contract_faults == 0U);
    zero(result);
}

TEST_CASE("B15 Robot core faults report new reason bits once without event floods") {
    Rig rig;
    idle(rig);
    rig.input.observations_fresh = false;
    auto result = rig.step(22000U);
    CHECK(event(result, core::Event::FAULT, 7).value == 32U);
    CHECK(count(rig.step(23000U), core::Event::FAULT, 7) == 0U);
    auto sample = rig.at(24000U);
    sample.previous.applied_valid = false;
    result = rig.submit(sample);
    CHECK(event(result, core::Event::FAULT, 7).value == 16U);
    CHECK(result.contract_faults == 48U);
    CHECK(count(rig.step(25000U), core::Event::FAULT, 7) == 0U);
}

TEST_CASE("B15 D060 metadata accepts literal canonical payloads for every event family") {
    const std::array<logframe::EventInput, 21U> valid{{
        {0U, core::Event::START_RELEASE, 1U, 0U}, {0U, core::Event::GO, 6U, 0U},
        {0U, core::Event::FIRST_NONZERO_DUTY, 3U, 0U},
        {0U, core::Event::FIRST_NONZERO_DUTY, 3U, 0x8166U},
        {0U, core::Event::STATE_CHANGE, 2U, 8U},
        {0U, core::Event::EDGE, 3U, 0x0011U}, {0U, core::Event::EDGE, 4U, 0x0308U},
        {0U, core::Event::EDGE, 8U, 0U}, {0U, core::Event::CONTACT, 3U, 7U},
        {0U, core::Event::STALL, 5U, 1U}, {0U, core::Event::STALL, 10U, 2U},
        {0U, core::Event::REFLANK_PHASE, 3U, 2U},
        {0U, core::Event::PHANTOM_SET, 0U, 18000U},
        {0U, core::Event::FAULT, 1U, 0U}, {0U, core::Event::FAULT, 2U, 127U},
        {0U, core::Event::FAULT, 3U, 15U}, {0U, core::Event::FAULT, 5U, 3U},
        {0U, core::Event::FAULT, 6U, 4U}, {0U, core::Event::FAULT, 7U, 255U},
        {0U, core::Event::FAULT, 8U, 31U}, {0U, core::Event::FAULT, 9U, 7U}
    }};
    for (const auto& item : valid) CHECK(logframe::validEventMetadata(item));
    CHECK(logframe::validEventMetadata({0U, core::Event::FAULT, 4U, 0U}));
    CHECK(logframe::validEventMetadata({0U, core::Event::FAULT, 10U, 1U}));
}

TEST_CASE("B15 D060 metadata rejects reserved bits invalid codes and noncanonical angle") {
    const std::array<logframe::EventInput, 22U> invalid{{
        {0U, static_cast<core::Event>(255U), 0U, 0U},
        {0U, core::Event::START_RELEASE, 0U, 0U}, {0U, core::Event::GO, 7U, 0U},
        {0U, core::Event::GO, 1U, 1U}, {0U, core::Event::FIRST_NONZERO_DUTY, 4U, 0U},
        {0U, core::Event::FIRST_NONZERO_DUTY, 3U, 0x0080U},
        {0U, core::Event::STATE_CHANGE, 12U, 1U},
        {0U, core::Event::STATE_CHANGE, 1U, 0x0102U},
        {0U, core::Event::EDGE, 32U, 1U}, {0U, core::Event::CONTACT, 4U, 7U},
        {0U, core::Event::CONTACT, 1U, 128U}, {0U, core::Event::STALL, 16U, 1U},
        {0U, core::Event::REFLANK_PHASE, 4U, 1U}, {0U, core::Event::REFLANK_PHASE, 1U, 0U},
        {0U, core::Event::PHANTOM_SET, 1U, 0U},
        {0U, core::Event::PHANTOM_SET, 0U, static_cast<std::uint16_t>(-18000)},
        {0U, core::Event::FAULT, 0U, 0U}, {0U, core::Event::FAULT, 2U, 128U},
        {0U, core::Event::FAULT, 3U, 16U}, {0U, core::Event::FAULT, 7U, 256U},
        {0U, core::Event::FAULT, 9U, 8U}, {0U, core::Event::FAULT, 10U, 2U}
    }};
    for (const auto& item : invalid) CHECK_FALSE(logframe::validEventMetadata(item));
}

TEST_CASE("B15 D060 EventBatch retains exactly21 ordered events with separate rejection causes") {
    logframe::EventBatch batch;
    CHECK(logframe::ROBOT_EVENT_CAPACITY == 21U);
    for (unsigned index = 0U; index < 21U; ++index) {
        const std::uint32_t time = index < 10U ? 0xfffffff0U + index : index - 10U;
        CHECK(logframe::appendEvent(batch, {time, core::Event::GO, 1U, 0U}));
    }
    CHECK_FALSE(logframe::appendEvent(batch, {1U, core::Event::GO, 1U, 0U}));
    CHECK(batch.count == 21U);
    CHECK(batch.overflowed);
    CHECK(batch.rejected == 1U);
    CHECK_FALSE(logframe::appendEvent(batch, {2U, core::Event::GO, 9U, 0U}));
    CHECK(batch.invalid_metadata == 1U);
    CHECK(batch.rejected == 1U);
    for (unsigned index = 0U; index < 21U; ++index) {
        const std::uint32_t time = index < 10U ? 0xfffffff0U + index : index - 10U;
        CHECK(batch.entries[index].t_us == time);
        CHECK(batch.entries[index].type == core::Event::GO);
        CHECK(batch.entries[index].detail == 1U);
        CHECK(batch.entries[index].value == 0U);
    }
}

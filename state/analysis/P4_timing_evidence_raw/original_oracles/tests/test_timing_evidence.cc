// Tests D129 event grammar and source-to-application timing from public contracts.
// Keeps explicitly synthetic receipt arithmetic distinct from physical evidence.
// Dedicated M0/M1 profiles exercise boundaries without inspecting implementation.
#include "p4_timing_fixture.h"

using namespace p4_time;

TEST_CASE("B15 D129 timing profile has conditional identity exact codes and unchanged retention") {
    CHECK(SUMOX_TIMING_EVIDENCE == 1); CHECK(SUMOX_P4_REACTIVE == 1);
    CHECK(fsm::RobotResult::TIMING_EVIDENCE_PROFILE); CHECK(fsm::RobotResult::REACTIVE_PROFILE);
    CHECK(static_cast<unsigned>(core::Event::TIMING) == 10U);
    CHECK(static_cast<unsigned>(core::Event::START_RELEASE) == 0U);
    CHECK(static_cast<unsigned>(core::Event::GO) == 1U);
    CHECK(static_cast<unsigned>(core::Event::FIRST_NONZERO_DUTY) == 2U);
    CHECK(static_cast<unsigned>(core::Event::FAULT) == 9U);
    const Detail details[] = {Detail::HEADER, Detail::LOSS_READ_START, Detail::LOSS_READ_END,
        Detail::LOSS_BRAKE_DECISION, Detail::LOSS_ZERO_APPLIED, Detail::EXCLUDED_TRANSIENT,
        Detail::EXCLUDED_FILTER, Detail::EXCLUDED_CONTACT_ROUTE, Detail::INTERRUPTED_EDGE,
        Detail::INTERRUPTED_STOP_FAULT, Detail::INVALID_SOURCE_TIME, Detail::INVALID_RECEIPT,
        Detail::EXCLUDED_NO_APPROACH};
    for (unsigned i = 0U; i < 13U; ++i) CHECK(static_cast<unsigned>(details[i]) == i);
    CHECK(logframe::ROBOT_EVENT_CAPACITY == 26U); CHECK(logframe::EVENT_BYTES == 8U);
    CHECK(config::LOG_EVENT_CAPACITY == 4096U); CHECK(config::LOG_HZ == 25U);
    CHECK(config::LOG_FRAME_WINDOW_MS == 200000U);
    fsm::RobotInput input; CHECK_FALSE(input.opponent_read.valid);
    CHECK(input.opponent_read.started_us == 0U); CHECK(input.opponent_read.completed_us == 0U);
}

TEST_CASE("B15 D129 exact TIMING metadata accepts either header motor bit and no reserved combination") {
    for (unsigned detail = 0U; detail < 256U; ++detail) {
        for (unsigned value : {0U, 1U, 2U, 0x0100U, 0x0101U, 0x0102U, 0x0104U, 0x0105U, 0x0106U, 65535U}) {
            const bool valid = detail == 0U ? (value == 0x0101U || value == 0x0105U) :
                (detail <= 12U && value == 1U);
            const logframe::EventInput e{9U, core::Event::TIMING, static_cast<std::uint8_t>(detail),
                static_cast<std::uint16_t>(value)};
            CHECK(logframe::validEventMetadata(e) == valid);
        }
    }
}

TEST_CASE("B15 D129 eight byte codec is literal little endian and packing remains enum-only") {
    logframe::EventBytes bytes;
    CHECK(logframe::packEvent({0x12345678U, core::Event::TIMING, 3U, 1U}, bytes) == logframe::PackStatus::OK);
    const std::uint8_t expected[] = {0x78U, 0x56U, 0x34U, 0x12U, 10U, 3U, 1U, 0U};
    for (unsigned i = 0U; i < 8U; ++i) CHECK(bytes.data[i] == expected[i]);
    CHECK(logframe::packEvent({0U, core::Event::TIMING, 255U, 65535U}, bytes) == logframe::PackStatus::OK);
    for (unsigned code = 11U; code < 256U; ++code) {
        CHECK(logframe::packEvent({1U, static_cast<core::Event>(code), 0U, 0U}, bytes) == logframe::PackStatus::INVALID);
        for (auto byte : bytes.data) CHECK(byte == 0U);
    }
}

TEST_CASE("B15 D129 batch26 and first4096 ring retain order and explicit overflow independently") {
    logframe::EventBatch batch;
    CHECK_FALSE(logframe::appendEvent(batch, {0U, core::Event::TIMING, 0U, 1U}));
    CHECK(batch.count == 0U); CHECK(batch.invalid_metadata == 1U); CHECK_FALSE(batch.overflowed);
    for (unsigned i = 0U; i < 26U; ++i)
        APP_REQUIRE(logframe::appendEvent(batch, {100U - i, core::Event::TIMING, 1U, 1U}));
    CHECK_FALSE(logframe::appendEvent(batch, {1U, core::Event::TIMING, 2U, 1U}));
    CHECK(batch.count == 26U); CHECK(batch.overflowed); CHECK(batch.rejected == 1U);
    CHECK(batch.entries[0].t_us == 100U); CHECK(batch.entries[25].t_us == 75U);
    logframe::EventBuffer ring;
    for (unsigned i = 0U; i < 4096U; ++i) {
        logframe::EventBytes encoded;
        APP_REQUIRE(logframe::packEvent({0xffffff00U + i, core::Event::TIMING, 1U, 1U}, encoded) == logframe::PackStatus::OK);
        APP_REQUIRE(ring.append(encoded));
    }
    logframe::EventBytes extra; CHECK_FALSE(ring.append(extra)); CHECK_FALSE(ring.append(extra));
    CHECK(ring.size() == 4096U); CHECK(ring.overflowed()); CHECK(ring.rejectedCount() == 2U);
    APP_REQUIRE(ring.at(0U)); APP_REQUIRE(ring.at(4095U)); CHECK(ring.at(4096U) == nullptr);
    CHECK(app_test::u32(ring.at(0U)->data) == 0xffffff00U);
    CHECK(app_test::u32(ring.at(4095U)->data) == 0xffffff00U + 4095U);
}

TEST_CASE("B3 B15 D129 HEADER immediately follows authentic accepted START with compiled profile") {
    Rig rig; const auto release = rig.release(); const auto& r = rig.last;
    const auto header = event(r, Detail::HEADER); CHECK(header.t_us == release);
    CHECK(header.value == (MOTORS_ALLOWED ? 0x0105U : 0x0101U)); CHECK(rig.trace_size == 1U);
    bool paired = false;
    for (unsigned i = 0U; i + 1U < r.events.count; ++i) if (r.events.entries[i].type == core::Event::START_RELEASE) {
        CHECK(r.events.entries[i + 1U].type == core::Event::TIMING);
        CHECK(r.events.entries[i + 1U].detail == 0U); paired = true;
    }
    CHECK(paired); CHECK(count(rig.step(release + 1000U)) == 0U);
}

TEST_CASE("B5 B9 B15 D129 synthetic SEARCH and DEFEND loss preserves exact source decision and receipt timestamps") {
    for (unsigned residual : {0U, 8U, 64U}) {
        Rig rig; rig.approach(); const auto loss = rig.onset(residual);
        pair(rig.last, loss - 150U, loss - 120U); CHECK(count(rig.last) == 2U);
        CHECK(rig.last.outputs.ui_state == State::ATTACK); CHECK_FALSE(rig.last.contact);
        CHECK(count(rig.step(loss + 29999U)) == 0U);
        const auto decision = rig.brake(loss, 40U, 80U);
        CHECK(rig.last.outputs.ui_state == (residual ? State::DEFEND_TURN : State::SEARCH));
        CHECK(rig.last.outputs.motors_enabled); terminal(rig.last, Detail::LOSS_BRAKE_DECISION, decision);
        const auto completed = rig.step(decision + 1000U);
        CHECK(event(completed, Detail::LOSS_ZERO_APPLIED).t_us == decision + 40U);
        CHECK(event(completed, Detail::LOSS_ZERO_APPLIED).value == 1U);
        CHECK(rig.trace_size == 5U); CHECK(completed.contract_faults == 0U);
        CHECK_FALSE(completed.timing_incomplete);
        CHECK(count(rig.step(decision + 2000U)) == 0U);
    }
}

TEST_CASE("B5 B15 D129 synthetic source acquisition and completion preserve natural clock wrap") {
    const auto offset = 5217000U;
    Rig wrapped; wrapped.approach(0U - offset); const auto loss = wrapped.onset();
    CHECK(loss == 0U); pair(wrapped.last, 0U - 150U, 0U - 120U);
    const auto decision = wrapped.brake(loss, 7U, 11U);
    const auto done = wrapped.step(decision + 1000U);
    CHECK(event(done, Detail::LOSS_ZERO_APPLIED).t_us == 30007U); CHECK(wrapped.trace_size == 5U);
    CHECK(done.contract_faults == 0U); CHECK_FALSE(done.timing_incomplete);
    Rig zero; zero.approach(0U - offset); zero.opponent(0U);
    auto first = zero.at(50U, 100U); first.opponent_read = {true, 0U, 20U};
    pair(zero.submit(first), 0U, 20U); const auto d = zero.brake(50U);
    CHECK(event(zero.step(d + 1000U), Detail::LOSS_ZERO_APPLIED).t_us == d);
    CHECK(zero.trace_size == 5U);
}

TEST_CASE("B9 B15 D129 a late valid synthetic zero remains recorded without a35ms cutoff") {
    Rig rig; rig.approach(); const auto loss = rig.onset();
    const auto decision = rig.brake(loss, 50000U, 50020U);
    const auto done = rig.step(decision + 51000U);
    CHECK(event(done, Detail::LOSS_ZERO_APPLIED).t_us == decision + 50000U);
    CHECK(rig.trace_size == 5U); CHECK(done.contract_faults == 0U);
    CHECK_FALSE(done.timing_incomplete); CHECK(done.ticks.max_us == 50020U);
}

TEST_CASE("B5 B9 D129 staggered front debounce may TRACK without moving the original all-clear source") {
    Rig rig; const auto start = rig.approach(0U, 3U); rig.opponent(1U);
    CHECK(count(rig.step(start + 1000U)) == 0U); rig.opponent(0U);
    const auto loss = start + 11000U; const auto first = rig.step(loss); pair(first, loss, loss);
    const auto track = rig.step(start + 31000U); CHECK(track.outputs.ui_state == State::TRACK);
    CHECK(track.opponent_mask == 1U); CHECK(count(track) == 0U);
    const auto decision = rig.brake(loss); CHECK(rig.last.outputs.ui_state == State::SEARCH);
    terminal(rig.last, Detail::LOSS_BRAKE_DECISION, decision);
    CHECK(count(rig.step(decision + 1000U), Detail::LOSS_ZERO_APPLIED) == 1U);
    CHECK(rig.trace_size == 5U);
}

TEST_CASE("B5 D129 any raw front reassertion closes one synthetic candidate with no retry") {
    for (unsigned raw : {1U, 2U, 4U}) {
        Rig rig; rig.approach(); const auto loss = rig.onset(); rig.opponent(raw);
        terminal(rig.step(loss + 1000U), Detail::EXCLUDED_TRANSIENT, loss + 1000U);
        rig.opponent(0U); CHECK(count(rig.step(loss + 2000U)) == 0U);
        CHECK(count(rig.step(loss + 32000U)) == 0U); CHECK(count(rig.step(loss + 33000U)) == 0U);
        CHECK(rig.trace_size == 4U);
    }
}

TEST_CASE("B5 B15 D129 first clear keeps its pair when the immediately prior applied approach ceases") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        Rig rig; rig.approach();
        if (scenario == 0U) rig.previous.duty_l = 0.0F;
        if (scenario == 1U) rig.previous.duty_r = 0.0F;
        if (scenario == 2U) { rig.previous.motors_enabled = false; rig.previous.duty_l = rig.previous.duty_r = 0.0F; }
        const auto loss = rig.onset(); pair(rig.last, loss - 150U, loss - 120U);
        CHECK(count(rig.last) == 3U); CHECK(event(rig.last, Detail::EXCLUDED_NO_APPROACH).t_us == loss);
        CHECK(rig.last.contract_faults == 0U); rig.step(loss + 30000U); rig.step(loss + 31000U);
        CHECK(rig.trace_size == 4U);
    }
}

TEST_CASE("B14 B15 D129 malformed current source windows close once without changing motion") {
    for (unsigned scenario = 0U; scenario < 7U; ++scenario) {
        Rig rig; const auto t = rig.approach() + 1000U; auto bad = rig.at(t, 200U);
        bad.opponent_read = {true, t - 150U, t - 120U};
        if (scenario == 0U) bad.opponent_read.valid = false;
        if (scenario == 1U) bad.opponent_read.started_us = t - 201U;
        if (scenario == 2U) bad.opponent_read.completed_us = t - 151U;
        if (scenario == 3U) bad.opponent_read.completed_us = t + 1U;
        if (scenario == 4U) bad.timing.start_valid = false;
        if (scenario == 5U) bad.timing.started_us = t - 0x80000000U;
        if (scenario == 6U) bad.opponent_read.started_us = t - 0x80000000U;
        const auto r = rig.submit(bad); terminal(r, Detail::INVALID_SOURCE_TIME, t);
        CHECK(r.contract_faults == 0U); CHECK(r.outputs.ui_state == State::ATTACK);
        CHECK(r.outputs.motors_enabled); CHECK(r.outputs.duty_l == .60F); CHECK(r.outputs.duty_r == .60F);
        rig.onset(); CHECK(count(rig.last) == 0U); CHECK(rig.trace_size == 2U);
    }
}

TEST_CASE("B14 D092 D129 active source qualification requires uninterrupted prior explicit receipt chronology") {
    for (bool observing : {false, true}) for (unsigned scenario = 0U; scenario < 4U; ++scenario) {
        Rig rig; rig.approach(); if (observing) rig.onset(); const auto t = rig.now + 1000U;
        auto value = rig.at(t, 200U); value.opponent_read = {true, t - 150U, t - 120U};
        if (scenario == 0U) value.timing.started_us = rig.previous.completed_us - 1U;
        if (scenario == 1U) value.previous.duration_valid = false;
        if (scenario == 2U) ++value.previous.execution_us;
        if (scenario == 3U) value.previous.completed_us = value.previous.applied_us - 1U;
        const auto r = rig.submit(value); terminal(r, Detail::INVALID_SOURCE_TIME, t);
        CHECK(r.timing_incomplete); CHECK(r.contract_faults == 0U);
        CHECK(r.outputs.motors_enabled); const auto size = rig.trace_size;
        rig.opponent(0U); rig.step(t + 1000U); rig.step(t + 31000U); rig.step(t + 32000U);
        CHECK(rig.trace_size == size);
    }
}

TEST_CASE("B5 B14 D129 missing legacy timing or source evidence never qualifies but preserves reactive motion") {
    for (bool missing_timing : {false, true}) {
        Rig rig;
        if (missing_timing) rig.input.timing.explicit_start = false;
        else rig.source_window = false;
        rig.approach(); const auto loss = rig.onset(); CHECK(count(rig.last) == 0U);
        const auto d = rig.brake(loss); CHECK(rig.last.outputs.ui_state == State::SEARCH);
        CHECK(count(rig.step(d + 1000U)) == 0U); CHECK(rig.trace_size == 1U);
        CHECK(rig.last.contract_faults == 0U);
    }
}

TEST_CASE("B5 D129 front stuck exclusion occurs before a pair and never resumes") {
    Rig rig; const auto t = rig.approach() + 1000U; rig.input.raw_heading_deg = 361.0F;
    const auto r = rig.step(t); APP_REQUIRE(r.opponent_fault_mask == 2U);
    terminal(r, Detail::EXCLUDED_FILTER, t); rig.onset(); CHECK(count(rig.last) == 0U);
    CHECK(rig.trace_size == 2U); CHECK(r.contract_faults == 0U);
}

TEST_CASE("B3 B15 D129 reset leaves an unfinished synthetic tail uncompleted and permits a new attempt") {
    Rig rig; rig.approach(); const auto loss = rig.onset(); rig.brake(loss);
    CHECK(rig.trace_size == 4U); const auto token = rig.last.token; const auto restart = rig.now + 10000U;
    rig.robot.reset(); rig.previous = {}; rig.approach(restart);
    CHECK(rig.last.token > token); CHECK(rig.trace_size == 5U);
    const auto loss2 = rig.onset(); const auto d2 = rig.brake(loss2); rig.step(d2 + 1000U);
    CHECK(rig.trace_size == 9U); CHECK(rig.trace[4].detail == 0U);
    CHECK(rig.trace[8].detail == 4U); CHECK(rig.trace[8].value == 1U);
}

TEST_CASE("B3 D129 cancelled countdown has only its header and next genuine START begins new evidence") {
    Rig rig; const auto release = rig.release(); rig.step(release + 1000U, Button::MODE);
    const auto cancel = rig.step(release + 21000U, Button::MODE);
    CHECK_FALSE(cancel.outputs.motors_enabled); CHECK_FALSE(cancel.lifecycle.gate.go);
    CHECK(rig.trace_size == 1U); rig.step(release + 22000U); rig.step(release + 42000U);
    rig.step(release + 43000U, Button::START); rig.step(release + 63000U, Button::START);
    rig.step(release + 64000U); const auto second = rig.step(release + 84000U);
    APP_REQUIRE(second.lifecycle.gate.start_release); CHECK(rig.trace_size == 2U);
    CHECK(event(second, Detail::HEADER).t_us == release + 84000U);
    CHECK(count(second, Detail::LOSS_READ_START) == 0U);
}

TEST_CASE("B15 D129 duplicates do not replay source pairs decision pulses or consume a pending receipt") {
    Rig rig; rig.approach(); const auto loss = rig.onset(); const auto before = rig.trace_size;
    auto changed = rig.at(loss); changed.stop_requested = true; changed.previous.token ^= (1ULL << 32U);
    const auto duplicate = rig.submit(changed); CHECK_FALSE(duplicate.fresh); CHECK(duplicate.events.count == 0U);
    CHECK(rig.trace_size == before); const auto d = rig.brake(loss);
    const auto repeated = rig.step(d); CHECK_FALSE(repeated.fresh); CHECK(repeated.events.count == 0U);
    CHECK(rig.trace_size == 4U); CHECK(count(rig.step(d + 1000U), Detail::LOSS_ZERO_APPLIED) == 1U);
    CHECK_FALSE(rig.step(d + 1000U).fresh); CHECK(rig.trace_size == 5U);
}

TEST_CASE("B5 B9 D129 first ATTACK with only a prior TRACK receipt cannot arm an early loss") {
    Rig rig; rig.opponent(2U); const auto g = rig.go();
    rig.step(g + 1000U); rig.step(g + 2000U);
    APP_REQUIRE(rig.last.outputs.ui_state == State::TRACK);
    APP_REQUIRE(rig.previous.duty_l > 0.0F && rig.previous.duty_r > 0.0F);
    APP_REQUIRE(rig.step(g + 3000U).outputs.ui_state == State::ATTACK);
    const auto loss = rig.onset(); CHECK(count(rig.last) == 0U);
    const auto d = rig.brake(loss); CHECK(count(rig.step(d + 1000U)) == 0U);
    CHECK(rig.trace_size == 1U);
}

TEST_CASE("B5 D129 a side-only stuck fault does not exclude an otherwise qualified front loss") {
    Rig rig; rig.opponent(16U); const auto g = rig.go(); rig.opponent(18U);
    rig.step(g + 1000U); rig.step(g + 2000U); rig.step(g + 3000U);
    APP_REQUIRE(rig.step(g + 4000U).outputs.ui_state == State::ATTACK);
    rig.step(g + 5000U); rig.input.raw_heading_deg = 361.0F;
    const auto stuck = rig.step(g + 6000U); APP_REQUIRE(stuck.opponent_fault_mask == 16U);
    CHECK(stuck.opponent_mask == 2U); CHECK(count(stuck) == 0U);
    rig.step(g + 56000U); const auto loss = rig.onset(16U);
    pair(rig.last, loss - 150U, loss - 120U); const auto d = rig.brake(loss);
    CHECK(count(rig.step(d + 1000U), Detail::LOSS_ZERO_APPLIED) == 1U);
    CHECK(rig.trace_size == 5U);
}

static std::uint32_t phantomApproach(Rig& rig) {
    rig.source_window = false; rig.opponent(2U); const auto g = rig.go();
    rig.step(g + 1000U); rig.step(g + 2000U); rig.step(g + 3000U);
    rig.white(1U); const auto edge = g + 4000U; const auto marked = rig.step(edge);
    unsigned markers = 0U;
    for (unsigned i = 0U; i < marked.events.count; ++i)
        if (marked.events.entries[i].type == core::Event::PHANTOM_SET) ++markers;
    APP_REQUIRE(markers == 1U); CHECK(rig.trace_size == 1U);
    rig.white(0U); rig.input.imu_ok = false; rig.opponent(18U);
    rig.step(edge + 1000U); rig.step(edge + 121000U); rig.step(edge + 360999U);
    rig.input.imu_ok = true; rig.source_window = true;
    APP_REQUIRE(rig.step(edge + 361000U).outputs.ui_state == State::TRACK);
    rig.step(edge + 362000U); APP_REQUIRE(rig.step(edge + 363000U).outputs.ui_state == State::ATTACK);
    rig.step(edge + 364000U); rig.step(edge + 414000U);
    APP_REQUIRE(!rig.last.contact); APP_REQUIRE(rig.last.opponent_mask == 18U); return rig.now;
}

TEST_CASE("B5 D129 active phantom excludes only actual front removal while a nonmasking marker permits loss") {
    for (bool masking : {false, true}) {
        Rig rig; const auto start = phantomApproach(rig); rig.opponent(2U);
        if (!masking) rig.input.raw_heading_deg = 90.0F;
        CHECK(count(rig.step(start + 1000U)) == 0U);
        const auto filtered = rig.step(start + 31000U);
        if (masking) {
            APP_REQUIRE(filtered.opponent_mask == 0U);
            terminal(filtered, Detail::EXCLUDED_FILTER, start + 31000U); CHECK(rig.trace_size == 2U);
        } else {
            APP_REQUIRE(filtered.opponent_mask == 2U); CHECK(count(filtered) == 0U);
            const auto loss = rig.onset(); pair(rig.last, loss - 150U, loss - 120U);
            const auto d = rig.brake(loss); CHECK(count(rig.step(d + 1000U), Detail::LOSS_ZERO_APPLIED) == 1U);
            CHECK(rig.trace_size == 5U);
        }
    }
}

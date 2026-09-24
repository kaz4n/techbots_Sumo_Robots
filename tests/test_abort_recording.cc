// Tests D135 loss propagation by composing public event batches and AttemptRecorder.
// Synthetic envelopes test storage grammar only; they are never presented as Robot receipts.
// Draft cases retain partial prefixes, malformed evidence, ring loss and unfinished tails.
#include "fixtures/p5_abort_fixture.h"

using namespace p5_abort;
namespace {
fsm::RobotResult envelope(std::uint64_t token) {
    fsm::RobotResult r; r.token = token; r.fresh = true; r.running_mode = Mode::DIRECT;
    r.outputs.ui_state = State::TRACK; return r;
}
void append(fsm::RobotResult& r, logframe::EventInput event) {
    APP_REQUIRE(logframe::appendEvent(r.events, event));
}
void begin(recorder::AttemptRecorder& owner) {
    auto r = envelope(1U); r.outputs.ui_state = State::COUNTDOWN;
    r.lifecycle.gate.start_release = true; r.lifecycle.gate.release_us = 100U;
    append(r, {100U, core::Event::START_RELEASE, 3U, 0U});
    append(r, {100U, TIMING, HEADER, 0x0201U});
    APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
    r = envelope(2U); r.outputs.ui_state = State::OPENER; r.lifecycle.gate.go = true;
    append(r, {5100100U, core::Event::GO, 3U, 0U});
    APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
}
void candidate(fsm::RobotResult& r) {
    // Attempt all four appends even when an earlier one was rejected.
    logframe::appendEvent(r.events, {5101100U, TIMING, READ_START, 1U});
    logframe::appendEvent(r.events, {5101110U, TIMING, READ_END, 1U});
    logframe::appendEvent(r.events, {5101200U, TIMING, QUALIFIED, cue(3U, 0U, 1U, 2U)});
    logframe::appendEvent(r.events, {5101200U, TIMING, HANDOVER, 5U});
}
void frame(fsm::RobotResult& r) {
    logframe::FrameInput input; input.state = State::TRACK; input.mode = Mode::DIRECT;
    input.t_ms = 5101U; input.opp_mask = 2U; input.vbat_v = 11.1F;
    r.frame_status = logframe::packFrame(input, r.frame); APP_REQUIRE(r.frame_status == logframe::PackStatus::OK);
    r.frame_ready = true; r.frame_token = r.token - 1U;
}
void applied(recorder::AttemptRecorder& owner, std::uint64_t token) {
    auto r = envelope(token); append(r, {5101240U, TIMING, APPLIED, 1U}); frame(r);
    APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
}
} // namespace

TEST_CASE("B15 D135 partial qualification suffix loss survives later visible APPLIED without rollback") {
    for (unsigned occupied = 17U; occupied <= 21U; ++occupied) {
        recorder::AttemptRecorder owner; begin(owner); auto r = envelope(3U);
        for (unsigned i = 0U; i < occupied; ++i)
            append(r, {5101000U + i, core::Event::STATE_CHANGE, 4U, 5U});
        candidate(r); frame(r); APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
        CHECK(owner.summary().upstream_event_rejected == occupied - 17U);
        CHECK(owner.summary().upstream_event_overflow == (occupied > 17U));
        CHECK(owner.events().size() == 24U); CHECK(owner.frames().size() == 1U);
        for (unsigned i = 0U; i < occupied; ++i) {
            const auto* e = owner.events().at(3U + i); APP_REQUIRE(e != nullptr);
            CHECK(e->data[4] == static_cast<unsigned>(core::Event::STATE_CHANGE));
            CHECK(app_test::u32(e->data) == 5101000U + i);
        }
        applied(owner, 4U); CHECK(stored(owner, APPLIED) == 1U);
        CHECK(owner.incomplete() == (occupied > 17U)); CHECK(owner.frames().size() == 2U);
        CHECK(owner.summary().upstream_event_rejected == occupied - 17U);
        const auto retained = owner.events().size(); CHECK(owner.consume(r) == recorder::ConsumeStatus::REJECTED);
        CHECK(owner.events().size() == retained); CHECK(owner.incomplete());
    }
}

TEST_CASE("B15 D135 event ring retains exact prefix while rejected abort suffix and frames remain explicit") {
    recorder::AttemptRecorder owner; begin(owner); std::uint64_t token = 3U;
    unsigned remaining = 4091U;
    while (remaining != 0U) {
        auto r = envelope(token++); const unsigned batch = remaining < 21U ? remaining : 21U;
        for (unsigned i = 0U; i < batch; ++i)
            append(r, {static_cast<std::uint32_t>(token), core::Event::STATE_CHANGE, 4U, 5U});
        APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED); remaining -= batch;
    }
    APP_REQUIRE(owner.events().size() == 4094U);
    const auto first = *owner.events().at(0U); auto r = envelope(token++); candidate(r); frame(r);
    APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 4096U); CHECK(owner.events().rejectedCount() == 2U);
    CHECK(stored(owner, READ_START) == 1U); CHECK(stored(owner, READ_END) == 1U);
    CHECK(stored(owner, QUALIFIED) == 0U); CHECK(stored(owner, HANDOVER) == 0U);
    CHECK(owner.frames().size() == 1U); applied(owner, token);
    CHECK(owner.events().rejectedCount() == 3U); CHECK(owner.events().overflowed());
    CHECK(stored(owner, APPLIED) == 0U); CHECK(owner.frames().size() == 2U); CHECK(owner.incomplete());
    for (unsigned i = 0U; i < 8U; ++i) CHECK(owner.events().at(0U)->data[i] == first.data[i]);
    CHECK(owner.summary().upstream_event_rejected == 0U);
}

TEST_CASE("B15 D135 malformed batch and invalid cue metadata cannot become clean recording evidence") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        recorder::AttemptRecorder owner; begin(owner); auto r = envelope(3U); candidate(r); frame(r);
        if (scenario == 0U) r.events.count = 22U;
        if (scenario == 1U) r.events.entries[2].value = cue(3U, 1U, 1U, 2U);
        if (scenario == 2U) {
            r.events.invalid_metadata = 1U; r.events.entries[2].value = cue(6U, 4U, 1U, 2U);
        }
        APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
        CHECK(owner.summary().malformed_batches == (scenario == 0U ? 1U : 0U));
        CHECK(owner.summary().event_semantic_rejected == (scenario == 0U ? 0U : 1U));
        CHECK(owner.summary().upstream_event_invalid == (scenario == 2U ? 1U : 0U));
        CHECK(stored(owner, QUALIFIED) == 0U); CHECK(owner.frames().size() == 1U);
        applied(owner, 4U); CHECK(stored(owner, APPLIED) == 1U); CHECK(owner.incomplete());
    }
}

TEST_CASE("B15 D135 unfinished recorder prefix and reset retain bytes without manufacturing a terminal") {
    recorder::AttemptRecorder owner; begin(owner); auto r = envelope(3U); candidate(r);
    APP_REQUIRE(owner.consume(r) == recorder::ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == recorder::AttemptPhase::RECORDING); CHECK_FALSE(owner.incomplete());
    CHECK(stored(owner, APPLIED) == 0U); const auto retained = owner.events().size();
    owner.onRobotReset(); CHECK(owner.phase() == recorder::AttemptPhase::INTERRUPTED);
    CHECK(owner.incomplete()); CHECK(owner.events().size() == retained);
    CHECK(stored(owner, APPLIED) == 0U); CHECK(stored(owner, INVALID_RECEIPT) == 0U);
    CHECK(owner.summary().interrupted); CHECK(owner.summary().timing_incomplete);
    owner.onRobotReset(); CHECK(owner.events().size() == retained);
}

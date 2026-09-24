// Tests the adopted D135 numeric event grammar independently of producer branches.
// Preserves every historical mode ID and rejects unlisted phase/cause combinations.
// Isolated draft host cases exhaust all packed cue values and exact bounded retention.
#include "fixtures/p5_abort_fixture.h"

using namespace p5_abort;

TEST_CASE("B15 D135 profile identity and unchanged21-event5001-frame4096-event capacities") {
    CHECK(fsm::RobotResult::OPENER_TIMING_PROFILE);
    CHECK_FALSE(fsm::RobotResult::TIMING_EVIDENCE_PROFILE);
    CHECK_FALSE(fsm::RobotResult::REACTIVE_PROFILE);
    CHECK(SUMOX_P4_REACTIVE == 0); CHECK(SUMOX_TIMING_EVIDENCE == 0); CHECK(MATCH == 0);
    CHECK(logframe::ROBOT_EVENT_CAPACITY == 21U); CHECK(logframe::EVENT_BYTES == 8U);
    CHECK(config::LOG_EVENT_CAPACITY == 4096U); CHECK(config::LOG_FRAME_CAPACITY == 5001U);
    CHECK(config::LOG_HZ == 25U); CHECK(static_cast<unsigned>(core::Event::FAULT) == 9U);
    openers::AbortEvidence empty;
    CHECK(empty.phase == Phase::DIRECT); CHECK(empty.cause == Cause::NONE);
    CHECK(empty.effective_mask == 0U); CHECK_FALSE(empty.snapshot_front_present);
    CHECK(static_cast<unsigned>(Phase::WAIT_HOLD) == 4U);
    CHECK(static_cast<unsigned>(Cause::NATURAL_END) == 4U);
}

TEST_CASE("B15 D135 all65536 cue words follow the independent mode phase cause mask table") {
    for (unsigned value = 0U; value < 65536U; ++value) {
        const unsigned mode = value & 7U, phase = (value >> 3U) & 7U;
        const unsigned cause = (value >> 6U) & 3U, mask = (value >> 8U) & 127U;
        const bool snapshot = (value & 0x8000U) != 0U;
        const logframe::EventInput e{0U, TIMING, 18U, static_cast<std::uint16_t>(value)};
        CHECK_MESSAGE(logframe::validEventMetadata(e) == permittedCue(mode, phase, cause, mask, snapshot),
                      "packed cue = ", value);
    }
}

TEST_CASE("B15 D135 every detail and boundary noncue values reject P4 and reserved grammar") {
    for (unsigned detail = 0U; detail < 256U; ++detail) {
        if (detail == QUALIFIED) continue;
        for (unsigned value : {0U, 1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U, 9U, 10U, 11U,
                              12U, 255U, 256U, 0x0101U, 0x0105U, 0x0200U, 0x0201U,
                              0x0202U, 0x0204U, 0x0205U, 0x0206U, 65535U}) {
            bool valid = detail == HEADER && (value == 0x0201U || value == 0x0205U);
            valid |= (detail == READ_START || detail == READ_END || detail == APPLIED ||
                      detail == INVALID_SOURCE || detail == INVALID_RECEIPT) && value == 1U;
            valid |= detail == HANDOVER && (value == 5U || value == 6U || value == 7U);
            valid |= (detail == NOT_ABORT || detail == INTERRUPTED) && (value == 1U || value == 2U);
            valid |= detail == HANDOVER_FAILED && value <= 11U;
            CHECK_MESSAGE(logframe::validEventMetadata({0U, TIMING, static_cast<std::uint8_t>(detail),
                          static_cast<std::uint16_t>(value)}) == valid, detail, ":", value);
        }
    }
}

TEST_CASE("B15 D135 exact little endian packing remains separate from semantic validation") {
    const logframe::EventInput input{0x12345678U, TIMING, 18U, cue(3U, 0U, 1U, 2U, true)};
    CHECK(input.value == 0x8243U); CHECK(logframe::validEventMetadata(input));
    logframe::EventBytes bytes;
    CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
    const std::uint8_t expected[] = {0x78U, 0x56U, 0x34U, 0x12U, 10U, 18U, 0x43U, 0x82U};
    for (unsigned i = 0U; i < 8U; ++i) CHECK(bytes.data[i] == expected[i]);
    CHECK(logframe::packEvent({0U, TIMING, 255U, 65535U}, bytes) == logframe::PackStatus::OK);
    CHECK_FALSE(logframe::validEventMetadata({0U, TIMING, 255U, 65535U}));
    for (unsigned code = 11U; code < 256U; ++code) {
        CHECK(logframe::packEvent({1U, static_cast<core::Event>(code), 0U, 0U}, bytes) ==
              logframe::PackStatus::INVALID);
        for (auto byte : bytes.data) CHECK(byte == 0U);
    }
}

TEST_CASE("B15 D135 saturated21 event batches attempt every suffix append without rollback") {
    for (unsigned occupied = 17U; occupied <= 21U; ++occupied) {
        logframe::EventBatch batch;
        for (unsigned i = 0U; i < occupied; ++i)
            APP_REQUIRE(logframe::appendEvent(batch, {i, core::Event::STATE_CHANGE, 4U, 5U}));
        const logframe::EventInput suffix[] = {{100U, TIMING, 16U, 1U}, {110U, TIMING, 17U, 1U},
            {200U, TIMING, 18U, cue(3U, 0U, 1U, 2U)}, {200U, TIMING, 19U, 5U}};
        unsigned accepted = 0U;
        for (const auto& event : suffix) if (logframe::appendEvent(batch, event)) ++accepted;
        CHECK(accepted == 21U - occupied); CHECK(batch.count == 21U);
        CHECK(batch.rejected == occupied - 17U); CHECK(batch.overflowed == (occupied != 17U));
        CHECK(batch.invalid_metadata == 0U);
        for (unsigned i = 0U; i < occupied; ++i) {
            CHECK(batch.entries[i].type == core::Event::STATE_CHANGE); CHECK(batch.entries[i].t_us == i);
        }
        for (unsigned i = 0U; i < accepted; ++i) {
            CHECK(batch.entries[occupied + i].detail == 16U + i);
            CHECK(batch.entries[occupied + i].t_us == suffix[i].t_us);
        }
    }
}

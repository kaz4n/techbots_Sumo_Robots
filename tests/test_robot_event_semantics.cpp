// Checks D027/B5 semantic relations inside the public CONTACT event payload.
// Prevents a well-formed wire record from falsely asserting impossible contact evidence.
// Independent literal tables cover every front pattern, cue flag and harmless lower group.
#include "doctest.h"
#include "core/logframe.h"
#include <array>
#include <cstdint>

TEST_CASE("B5 D027 CONTACT metadata needs centered front and a compatible current cue") {
    // Columns: close only, impact only, both. Rows: literal B5 front masks0..7.
    const bool valid[8][3] = {
        {false, false, false}, //000: no front.
        {false, false, false}, //001: FL15 alone is off center.
        {false, true, false},  //010: centered FC, without close pattern.
        {false, true, false},  //011: centered FL15+FC, without close pattern.
        {false, false, false}, //100: FR15 alone is off center.
        {true, true, true},    //101: centered straddle, close pattern.
        {false, true, false},  //110: centered FC+FR15, without close pattern.
        {true, true, true}     //111: centered full front, close pattern.
    };
    for (unsigned front = 0U; front < 8U; ++front) {
        for (unsigned detail = 1U; detail <= 3U; ++detail) {
            for (unsigned lower_groups = 0U; lower_groups < 16U; ++lower_groups) {
                const auto mask = static_cast<std::uint16_t>(front | (lower_groups << 3U));
                const logframe::EventInput input{123U, core::Event::CONTACT,
                    static_cast<std::uint8_t>(detail), mask};
                CAPTURE(front);
                CAPTURE(detail);
                CAPTURE(lower_groups);
                CHECK(logframe::validEventMetadata(input) == valid[front][detail - 1U]);
            }
        }
    }
}

TEST_CASE("B15 CONTACT semantic checks still reject absent cues and reserved bits") {
    const std::array<logframe::EventInput, 7U> invalid{{
        {0U, core::Event::CONTACT, 0U, 7U},
        {0U, core::Event::CONTACT, 4U, 7U},
        {0U, core::Event::CONTACT, 255U, 7U},
        {0U, core::Event::CONTACT, 1U, 0x0085U},
        {0U, core::Event::CONTACT, 2U, 0x0082U},
        {0U, core::Event::CONTACT, 3U, 0x0107U},
        {0U, core::Event::CONTACT, 2U, 0xffffU}
    }};
    for (const auto& input : invalid) CHECK_FALSE(logframe::validEventMetadata(input));
}

TEST_CASE("B15 impossible CONTACT payloads increment semantic loss without entering EventBatch") {
    logframe::EventBatch batch;
    CHECK_FALSE(logframe::appendEvent(batch, {10U, core::Event::CONTACT, 1U, 2U}));
    CHECK_FALSE(logframe::appendEvent(batch, {11U, core::Event::CONTACT, 2U, 1U}));
    CHECK(batch.count == 0U);
    CHECK(batch.invalid_metadata == 2U);
    CHECK(batch.rejected == 0U);
    CHECK_FALSE(batch.overflowed);
    CHECK(logframe::appendEvent(batch, {12U, core::Event::CONTACT, 2U, 2U}));
    CHECK(logframe::appendEvent(batch, {13U, core::Event::CONTACT, 1U, 5U}));
    CHECK(batch.count == 2U);
    CHECK(batch.invalid_metadata == 2U);
    CHECK(batch.entries[0].t_us == 12U);
    CHECK(batch.entries[0].detail == 2U);
    CHECK(batch.entries[0].value == 2U);
    CHECK(batch.entries[1].t_us == 13U);
    CHECK(batch.entries[1].detail == 1U);
    CHECK(batch.entries[1].value == 5U);
}

// Checks B15 extended contract metadata and actual Robot-to-recorder propagation.
// D087 preserves legacy detail7 while retaining LINE256 and BUTTON512 as detail11.
// Exhaustive mask tests and literal event/CSV bytes form independent wire evidence.
#include "robot_scenario.h"
#include "hal/recorder_csv.h"
#include <cstdio>
#include <cstring>
#include <initializer_list>

TEST_CASE("B15 D087 extended fault11 accepts exactly known masks containing a high bit") {
    for (std::uint32_t mask = 0U; mask <= 65535U; ++mask) {
        const logframe::EventInput event{42U, core::Event::FAULT, 11U,
                                       static_cast<std::uint16_t>(mask)};
        const bool allowed = (mask & 0x300U) != 0U && (mask & ~0x3ffU) == 0U;
        CHECK(logframe::validEventMetadata(event) == allowed);
    }
    CHECK(logframe::EVENT_BYTES == 8U);
    CHECK(logframe::ROBOT_EVENT_CAPACITY == 21U);
}

TEST_CASE("B15 D087 legacy fault7 retains exact one-through255 acceptance") {
    for (std::uint32_t mask = 0U; mask <= 1024U; ++mask) {
        const logframe::EventInput event{42U, core::Event::FAULT, 7U,
                                       static_cast<std::uint16_t>(mask)};
        CHECK(logframe::validEventMetadata(event) == (mask >= 1U && mask <= 255U));
    }
}

TEST_CASE("B15 D087 actual LINE BUTTON and combined masks reach recorder and exact CSV") {
    for (const auto high : {256U, 512U, 768U}) {
        robot_test::Rig rig;
        const auto anchor = robot_test::release(rig, robot_test::idle(rig));
        recorder::AttemptRecorder owner;
        CHECK(owner.consume(rig.last) == recorder::ConsumeStatus::ACCEPTED);
        auto next = rig.at(anchor + 1000U);
        next.previous.applied_valid = false;
        if ((high & 256U) != 0U) {
            next.line.explicit_values = true;
            next.line.presence = core::LinePresence::INVALID;
            next.opponent_fresh = true;
        }
        if ((high & 512U) != 0U) {
            next.buttons.explicit_values = true;
            next.buttons.presence = core::ButtonPresence::INVALID;
        }
        const auto out = rig.submit(next);
        const auto expected = static_cast<std::uint16_t>(high | fsm::APPLICATION_CONTRACT);
        CHECK(out.contract_faults == expected);
        CHECK(robot_test::count(out, core::Event::FAULT, 11) == 1U);
        CHECK(robot_test::count(out, core::Event::FAULT, 7) == 0U);
        CHECK(robot_test::event(out, core::Event::FAULT, 11).value == expected);
        CHECK(out.events.invalid_metadata == 0U);
        CHECK(owner.consume(out) == recorder::ConsumeStatus::ACCEPTED);
        CHECK(owner.summary().event_semantic_rejected == 0U);
        unsigned found = 0U;
        for (std::size_t index = 0U; index < owner.events().size(); ++index) {
            const auto* encoded = owner.events().at(index);
            if (encoded == nullptr || encoded->data[4] != 9U || encoded->data[5] != 11U) continue;
            ++found;
            CHECK(encoded->data[6] == static_cast<std::uint8_t>(expected));
            CHECK(encoded->data[7] == static_cast<std::uint8_t>(expected >> 8U));
            char row[recorder::csv::MAX_LINE_BYTES] = {};
            const auto formatted = recorder::csv::eventRow(*encoded, index, row, sizeof(row));
            CHECK(formatted.status == recorder::csv::FormatStatus::OK);
            char prefix[128] = {};
            std::snprintf(prefix, sizeof(prefix), "1,%zu,%u,9,11,%u,", index, anchor + 1000U, expected);
            CHECK(std::strncmp(row, prefix, std::strlen(prefix)) == 0);
            CHECK(row[formatted.size - 1U] == '\n');
        }
        CHECK(found == 1U);
        CHECK(robot_test::count(rig.step(anchor + 2000U), core::Event::FAULT, 11) == 0U);
    }
}

TEST_CASE("B15 D087 invalid high masks are rejected before retention with explicit loss") {
    logframe::EventBatch batch;
    for (const auto mask : {0U, 255U, 1024U, 1280U, 65535U}) {
        CHECK_FALSE(logframe::appendEvent(batch, {0U, core::Event::FAULT, 11U,
                                                static_cast<std::uint16_t>(mask)}));
    }
    CHECK(batch.count == 0U);
    CHECK(batch.invalid_metadata == 5U);
    CHECK(batch.rejected == 0U);
    CHECK(logframe::appendEvent(batch, {0U, core::Event::FAULT, 11U, 1023U}));
    CHECK(batch.count == 1U);
}

// Exercises the actual inert memory query through public attempt-owner inputs.
// Guards caller ownership, absent-frame honesty and unchanged 96-byte ABI fields.
// Added only to the isolated reviewer sanitizer executable.
#include "doctest.h"
#include "memory_probe.h"
#include <cstring>
#include <limits>
#include <type_traits>

TEST_CASE("Reviewer D102 actual memory query owns snapshots and declares absence") {
    using namespace memory_probe;
    static_assert(std::is_same<decltype(View::frame), recorder::StoredFrame>::value);
    static_assert(sizeof(Abi) == 96U);
    View saved{};
    recorder::StoredFrame expected;
    {
        recorder::AttemptRecorder owner;
        fsm::RobotResult release;
        release.token = 1U;
        release.fresh = true;
        release.running_mode = core::Mode::DIRECT;
        release.outputs.ui_state = core::State::COUNTDOWN;
        release.lifecycle.gate.start_release = true;
        release.lifecycle.gate.release_us = 5000U;
        release.events.count = 1U;
        release.events.entries[0] = {5000U, core::Event::START_RELEASE, 3U, 0U};
        CHECK(owner.consume(release) == recorder::ConsumeStatus::ACCEPTED);
        probeQuery(owner, 0U, saved);
        CHECK_FALSE(saved.frame_present);
        CHECK(saved.event == owner.events().at(0U));
        CHECK(saved.event_count == 1U);
        CHECK(saved.frame_count == 0U);
        fsm::RobotResult result;
        result.token = 2U;
        result.fresh = true;
        result.running_mode = core::Mode::DIRECT;
        result.outputs.ui_state = core::State::SEARCH;
        result.frame_ready = true;
        result.frame_token = 1U;
        result.frame_status = logframe::PackStatus::INVALID;
        for (unsigned byte = 0; byte < 25; ++byte) result.frame.data[byte] = byte * 7U;
        CHECK(owner.consume(result) == recorder::ConsumeStatus::ACCEPTED);
        expected = {result.frame, result.frame_status};
        probeQuery(owner, 0U, saved);
        CHECK(saved.frame_present);
        CHECK(saved.frame.status == expected.status);
        CHECK(std::memcmp(saved.frame.bytes.data, expected.bytes.data, 25U) == 0);
        CHECK(saved.frame_count == 1U);
        CHECK(saved.incomplete);
        View absent = saved;
        probeQuery(owner, std::numeric_limits<std::size_t>::max(), absent);
        CHECK_FALSE(absent.frame_present);
        CHECK(absent.event == nullptr);
        CHECK(absent.frame.status == expected.status);
        CHECK(std::memcmp(absent.frame.bytes.data, expected.bytes.data, 25U) == 0);
        release.token = 3U;
        CHECK(owner.consume(release) == recorder::ConsumeStatus::ACCEPTED);
        View restarted{};
        probeQuery(owner, 0U, restarted);
        CHECK_FALSE(restarted.frame_present);
        CHECK(restarted.frame_count == 0U);
        CHECK(saved.frame.status == expected.status);
        CHECK(std::memcmp(saved.frame.bytes.data, expected.bytes.data, 25U) == 0);
    }
    CHECK(saved.frame.status == expected.status);
    CHECK(std::memcmp(saved.frame.bytes.data, expected.bytes.data, 25U) == 0);
    CHECK(abi.version == 1U);
    CHECK(abi.record_bytes == 96U);
    CHECK(abi.log_hz == 25U);
    CHECK(abi.frame_capacity == 5001U);
    CHECK(abi.event_capacity == 4096U);
    CHECK(abi.sizes[FRAME_BUFFER] == sizeof(recorder::FrameBuffer));
    CHECK(abi.alignments[FRAME_BUFFER] == alignof(recorder::FrameBuffer));
    CHECK(abi.sizes[STORED_FRAME] == 26U);
}

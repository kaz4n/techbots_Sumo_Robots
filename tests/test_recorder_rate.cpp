// Checks the D-072 adopted 25 Hz rate against B15 and frozen public contracts.
// Promotes the six independent D-071 cases without altering their historical artifact.
// Tested in the normal host suite with real core and recorder sources.
#include "doctest.h"
#include "hal/recorder.h"
#include "robot_scenario.h"
#include <cstdint>
#include <initializer_list>

namespace {
logframe::FrameBytes timestamp(std::uint32_t ms) {
    logframe::FrameBytes frame;
    for (unsigned i = 0; i < 4; ++i)
        frame.data[i] = static_cast<std::uint8_t>(ms >> (i * 8U));
    return frame;
}
void checkTime(const recorder::FrameBuffer& frames, std::size_t index, std::uint32_t ms) {
    const auto* frame = frames.at(index);
    CHECK(frame != nullptr);
    if (!frame) return;
    CHECK(frame->status == logframe::PackStatus::OK);
    CHECK(robot_test::u32(frame->bytes, 0U) == ms);
}
}

TEST_CASE("D072 B15 adopted rate configuration has literal25Hz5001frame capacity") {
    CHECK(config::LOG_HZ == 25U);
    CHECK(config::LOG_FRAME_WINDOW_MS == 200000U);
    CHECK(config::LOG_FRAME_CAPACITY == 5001U);
    CHECK(config::LOG_EVENT_CAPACITY == 4096U);
    CHECK(sizeof(recorder::StoredFrame) == 26U);
}

TEST_CASE("D072 B15 adopted rate retains every40ms endpoint0through200000 without overwrite") {
    recorder::FrameBuffer frames;
    for (std::uint32_t i = 0U; i <= 5000U; ++i)
        CHECK(frames.append(timestamp(i * 40U), logframe::PackStatus::OK));
    CHECK(frames.size() == 5001U);
    CHECK(frames.overwrittenCount() == 0U);
    CHECK_FALSE(frames.incomplete());
    for (std::uint32_t i = 0U; i <= 5000U; ++i) checkTime(frames, i, i * 40U);
    CHECK(frames.at(5001U) == nullptr);
    CHECK(frames.append(timestamp(200040U), logframe::PackStatus::OK));
    CHECK(frames.size() == 5001U);
    CHECK(frames.overwrittenCount() == 1U);
    CHECK(frames.incomplete());
    checkTime(frames, 0U, 40U);
    checkTime(frames, 5000U, 200040U);
}

TEST_CASE("D072 B15 adopted rate permits one offcadence final endpoint within capacity") {
    recorder::FrameBuffer frames;
    for (std::uint32_t i = 0U; i < 5000U; ++i)
        CHECK(frames.append(timestamp(i * 40U), logframe::PackStatus::OK));
    CHECK(frames.append(timestamp(199999U), logframe::PackStatus::OK));
    CHECK(frames.size() == 5001U);
    CHECK_FALSE(frames.incomplete());
    checkTime(frames, 0U, 0U);
    checkTime(frames, 5000U, 199999U);
}

TEST_CASE("D072 B15 real Robot adopted rate emits phaseanchored40ms frames after receipts") {
    robot_test::Rig rig;
    const auto anchor = robot_test::release(rig, robot_test::idle(rig));
    unsigned frames = 0U;
    for (std::uint32_t elapsed = 1000U; elapsed <= 121000U; elapsed += 1000U) {
        const auto result = rig.step(anchor + elapsed);
        const bool expected = (elapsed == 1000U || elapsed == 41000U ||
                               elapsed == 81000U || elapsed == 121000U);
        CHECK(result.frame_ready == expected);
        CHECK(result.skipped_frames == 0U);
        CHECK(result.contract_faults == 0U);
        if (result.frame_ready) {
            CHECK(robot_test::u32(result.frame, 0U) == frames * 40U);
            CHECK(result.frame_status == logframe::PackStatus::OK);
            ++frames;
        }
    }
    CHECK(frames == 4U);
}

TEST_CASE("D072 B15 real Robot adopted rate skipped40ms slots remain explicit without replay") {
    robot_test::Rig rig;
    const auto anchor = robot_test::release(rig, robot_test::idle(rig));
    CHECK(rig.step(anchor + 1000U).frame_ready);
    const auto gap = rig.step(anchor + 125000U);
    CHECK_FALSE(gap.frame_ready);
    CHECK(gap.skipped_frames == 2U); //40 and80ms lost; current125ms represents120ms slot.
    const auto received = rig.step(anchor + 126000U);
    CHECK(received.frame_ready);
    CHECK(robot_test::u32(received.frame, 0U) == 125U);
    CHECK(received.skipped_frames == 2U);
    CHECK_FALSE(rig.step(anchor + 159999U).frame_ready);
    CHECK_FALSE(rig.step(anchor + 160000U).frame_ready);
    const auto next = rig.step(anchor + 160001U);
    CHECK(next.frame_ready);
    CHECK(robot_test::u32(next.frame, 0U) == 160U);
    CHECK(next.skipped_frames == 2U);
    CHECK(next.contract_faults == 0U);
}

TEST_CASE("D072 B15 adopted rate forced final frame coalesces at cadence and seals with receipt") {
    for (const std::uint32_t stop : {39000U, 40000U, 41000U}) {
        robot_test::Rig rig;
        recorder::AttemptRecorder owner;
        const auto anchor = robot_test::release(rig, robot_test::idle(rig));
        CHECK(owner.consume(rig.last) == recorder::ConsumeStatus::ACCEPTED);
        CHECK(owner.consume(rig.step(anchor + 1000U)) == recorder::ConsumeStatus::ACCEPTED);
        rig.input.stop_requested = true;
        const auto stopped = rig.step(anchor + stop);
        CHECK(stopped.outputs.ui_state == core::State::STOPPED);
        CHECK(owner.consume(stopped) == recorder::ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == recorder::AttemptPhase::DRAINING);
        const auto flushed = rig.step(anchor + stop + 1U);
        CHECK(flushed.frame_ready);
        CHECK(flushed.frame_token == stopped.token);
        CHECK(owner.consume(flushed) == recorder::ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == recorder::AttemptPhase::SEALED);
        CHECK(owner.frames().size() == 2U);
        checkTime(owner.frames(), 0U, 0U);
        checkTime(owner.frames(), 1U, stop / 1000U);
        CHECK(owner.frames().overwrittenCount() == 0U);
        CHECK(owner.summary().skipped_frames == 0U);
        CHECK_FALSE(owner.summary().final_frame_missing);
        CHECK_FALSE(rig.step(anchor + stop + 100000U).frame_ready);
    }
}

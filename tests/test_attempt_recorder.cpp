// Checks the B15/D-070 attempt owner from its committed contract and public types.
// Preserves independent expectations for lifecycle, identities and evidence loss.
// Host-only byte fixtures and a fixed-seed oracle cover malformed and boundary data.
#include "doctest.h"
#include "hal/recorder.h"
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <deque>
#include <initializer_list>
#include <limits>
#include <type_traits>
#include <vector>

namespace {
using recorder::AttemptPhase;
using recorder::ConsumeStatus;
using logframe::PackStatus;
constexpr std::uint64_t MAX_TOKEN = std::numeric_limits<std::uint64_t>::max();
constexpr std::uint32_t MAX_COUNT = std::numeric_limits<std::uint32_t>::max();

fsm::RobotResult resultAt(std::uint64_t token, core::State state = core::State::SEARCH) {
    fsm::RobotResult result;
    result.token = token;
    result.fresh = true;
    result.outputs.ui_state = state;
    result.running_mode = core::Mode::DIRECT;
    return result;
}

logframe::EventInput goEvent(std::uint32_t time, std::uint8_t mode = 3U) {
    return {time, core::Event::GO, mode, 0U};
}

fsm::RobotResult startAt(std::uint64_t token, std::uint32_t release = 0x12345678U,
                         core::Mode mode = core::Mode::DIRECT) {
    auto result = resultAt(token, core::State::COUNTDOWN);
    result.running_mode = mode;
    result.lifecycle.gate.start_release = true;
    result.lifecycle.gate.release_us = release;
    result.events.count = 1U;
    result.events.entries[0] = {release, core::Event::START_RELEASE,
                               static_cast<std::uint8_t>(mode), 0U};
    return result;
}

logframe::FrameBytes markedFrame(std::uint32_t marker) {
    logframe::FrameBytes bytes{{
        0x78, 0x56, 0x34, 0x12, 6, 3, 9, 0x45, 0x1F, 0x50, 0xFF, 0xFF,
        0x83, 0xFF, 0xE2, 4, 0x0C, 0xFE, 0x40, 0xC0, 0xE2, 4, 15, 0x34, 0x12}};
    for (std::size_t index = 0U; index < 4U; ++index) {
        bytes.data[index] = static_cast<std::uint8_t>(marker >> (8U * index));
    }
    return bytes;
}

void giveFrame(fsm::RobotResult& result, std::uint64_t token,
               PackStatus status = PackStatus::OK, std::uint32_t marker = 0x12345678U) {
    result.frame_ready = true;
    result.frame_token = token;
    result.frame_status = status;
    result.frame = markedFrame(marker);
}

logframe::EventBytes eventWire(const logframe::EventInput& event) {
    return {{static_cast<std::uint8_t>(event.t_us),
             static_cast<std::uint8_t>(event.t_us >> 8U),
             static_cast<std::uint8_t>(event.t_us >> 16U),
             static_cast<std::uint8_t>(event.t_us >> 24U),
             static_cast<std::uint8_t>(event.type), event.detail,
             static_cast<std::uint8_t>(event.value),
             static_cast<std::uint8_t>(event.value >> 8U)}};
}

void checkEvent(const recorder::AttemptRecorder& owner, std::size_t index,
                const logframe::EventBytes& expected) {
    CAPTURE(index);
    const auto* event = owner.events().at(index);
    CHECK(event != nullptr);
    if (event == nullptr) return;
    for (std::size_t byte = 0U; byte < 8U; ++byte) {
        CAPTURE(byte);
        CHECK(event->data[byte] == expected.data[byte]);
    }
}

void checkFrame(const recorder::AttemptRecorder& owner, std::size_t index,
                const logframe::FrameBytes& expected, PackStatus status = PackStatus::OK) {
    CAPTURE(index);
    const auto* frame = owner.frames().at(index);
    CHECK(frame != nullptr);
    if (frame == nullptr) return;
    CHECK(std::memcmp(frame->bytes.data, expected.data, 25U) == 0);
    CHECK(frame->status == status);
}

void checkSummary(const recorder::AttemptSummary& actual,
                  const recorder::AttemptSummary& expected) {
    CHECK(actual.epoch_token == expected.epoch_token);
    CHECK(actual.last_frame_token == expected.last_frame_token);
    CHECK(actual.release_us == expected.release_us);
    CHECK(actual.mode == expected.mode);
    CHECK(actual.observed_results == expected.observed_results);
    CHECK(actual.missing_results == expected.missing_results);
    CHECK(actual.rejected_results == expected.rejected_results);
    CHECK(actual.identity_rejected == expected.identity_rejected);
    CHECK(actual.malformed_batches == expected.malformed_batches);
    CHECK(actual.event_semantic_rejected == expected.event_semantic_rejected);
    CHECK(actual.upstream_event_rejected == expected.upstream_event_rejected);
    CHECK(actual.upstream_event_invalid == expected.upstream_event_invalid);
    CHECK(actual.source_regressions == expected.source_regressions);
    CHECK(actual.skipped_frames == expected.skipped_frames);
    CHECK(actual.ticks.ticks == expected.ticks.ticks);
    CHECK(actual.ticks.overruns == expected.ticks.overruns);
    CHECK(actual.ticks.max_us == expected.ticks.max_us);
    CHECK(actual.ticks.saturated == expected.ticks.saturated);
    CHECK(actual.upstream_event_overflow == expected.upstream_event_overflow);
    CHECK(actual.timing_incomplete == expected.timing_incomplete);
    CHECK(actual.recording_incomplete == expected.recording_incomplete);
    CHECK(actual.go_seen == expected.go_seen);
    CHECK(actual.final_frame_missing == expected.final_frame_missing);
    CHECK(actual.interrupted == expected.interrupted);
    CHECK(actual.terminal_exhausted == expected.terminal_exhausted);
}

struct SavedAttempt {
    recorder::AttemptSummary summary;
    AttemptPhase phase = AttemptPhase::EMPTY;
    bool incomplete = false;
    std::vector<recorder::StoredFrame> frames;
    std::vector<logframe::EventBytes> events;
    std::uint32_t overwritten = 0U;
    std::uint32_t rejected_status = 0U;
    std::uint32_t clamped = 0U;
    std::uint32_t invalid = 0U;
    std::uint32_t event_rejected = 0U;
    bool event_overflow = false;
};

SavedAttempt saveAttempt(const recorder::AttemptRecorder& owner) {
    SavedAttempt saved;
    saved.summary = owner.summary();
    saved.phase = owner.phase();
    saved.incomplete = owner.incomplete();
    saved.overwritten = owner.frames().overwrittenCount();
    saved.rejected_status = owner.frames().rejectedStatusCount();
    saved.clamped = owner.frames().clampedCount();
    saved.invalid = owner.frames().invalidCount();
    saved.event_rejected = owner.events().rejectedCount();
    saved.event_overflow = owner.events().overflowed();
    for (std::size_t index = 0U; index < owner.frames().size(); ++index) {
        const auto* frame = owner.frames().at(index);
        CHECK(frame != nullptr);
        if (frame == nullptr) return saved;
        saved.frames.push_back(*frame);
    }
    for (std::size_t index = 0U; index < owner.events().size(); ++index) {
        const auto* event = owner.events().at(index);
        CHECK(event != nullptr);
        if (event == nullptr) return saved;
        saved.events.push_back(*event);
    }
    return saved;
}

void checkSaved(const recorder::AttemptRecorder& owner, const SavedAttempt& saved) {
    checkSummary(owner.summary(), saved.summary);
    CHECK(owner.phase() == saved.phase);
    CHECK(owner.incomplete() == saved.incomplete);
    CHECK(owner.frames().size() == saved.frames.size());
    CHECK(owner.events().size() == saved.events.size());
    CHECK(owner.frames().overwrittenCount() == saved.overwritten);
    CHECK(owner.frames().rejectedStatusCount() == saved.rejected_status);
    CHECK(owner.frames().clampedCount() == saved.clamped);
    CHECK(owner.frames().invalidCount() == saved.invalid);
    CHECK(owner.events().rejectedCount() == saved.event_rejected);
    CHECK(owner.events().overflowed() == saved.event_overflow);
    for (std::size_t index = 0U; index < saved.frames.size(); ++index) {
        checkFrame(owner, index, saved.frames[index].bytes, saved.frames[index].status);
    }
    for (std::size_t index = 0U; index < saved.events.size(); ++index) {
        checkEvent(owner, index, saved.events[index]);
    }
}

void startOwner(recorder::AttemptRecorder& owner, std::uint64_t token = 1U) {
    CHECK(owner.consume(startAt(token)) == ConsumeStatus::ACCEPTED);
}

void sealOwner(recorder::AttemptRecorder& owner) {
    startOwner(owner);
    auto stop = resultAt(2U, core::State::STOPPED);
    giveFrame(stop, 1U);
    CHECK(owner.consume(stop) == ConsumeStatus::ACCEPTED);
    auto tail = resultAt(3U, core::State::IDLE);
    giveFrame(tail, 2U);
    CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::SEALED);
}

fsm::RobotResult terminalResult() {
    auto result = resultAt(0U, core::State::STOPPED);
    result.fresh = false;
    result.contract_faults = fsm::TOKEN_EXHAUSTED;
    return result;
}

std::uint32_t randomNext(std::uint32_t& seed) {
    seed = 1664525U * seed + 1013904223U;
    return seed;
}
} // namespace

TEST_CASE("B15 D070 empty owner is read only noncopyable and reset preserves its defaults") {
    recorder::AttemptRecorder owner;
    CHECK_FALSE(std::is_copy_constructible<recorder::AttemptRecorder>::value);
    CHECK_FALSE(std::is_copy_assignable<recorder::AttemptRecorder>::value);
    CHECK(owner.phase() == AttemptPhase::EMPTY);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.events().size() == 0U);
    CHECK_FALSE(owner.incomplete());
    checkSummary(owner.summary(), recorder::AttemptSummary{});
    const auto saved = saveAttempt(owner);
    owner.onRobotReset();
    checkSaved(owner, saved);
}

TEST_CASE("B15 D070 saturated loss addition handles uint32 and uint64 exact limits") {
    CHECK(recorder::saturatedAdd(0U, 0U) == 0U);
    CHECK(recorder::saturatedAdd(0U, MAX_COUNT - 1U) == MAX_COUNT - 1U);
    CHECK(recorder::saturatedAdd(0U, MAX_COUNT) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(0U, static_cast<std::uint64_t>(MAX_COUNT) + 1U) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(MAX_COUNT - 7U, 6U) == MAX_COUNT - 1U);
    CHECK(recorder::saturatedAdd(MAX_COUNT - 7U, 7U) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(MAX_COUNT - 7U, 8U) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(MAX_COUNT, 0U) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(MAX_COUNT, 1U) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(0U, MAX_TOKEN) == MAX_COUNT);
    CHECK(recorder::saturatedAdd(MAX_COUNT, MAX_TOKEN) == MAX_COUNT);
    std::uint32_t seed = 0xB150D070U;
    for (std::size_t trial = 0U; trial < 10000U; ++trial) {
        const auto value = randomNext(seed);
        const std::uint64_t added = randomNext(seed);
        const auto expected = std::min(static_cast<std::uint64_t>(value) + added,
                                       static_cast<std::uint64_t>(MAX_COUNT));
        CHECK(recorder::saturatedAdd(value, added) == expected);
    }
}

TEST_CASE("B15 D070 outside envelopes track identity but ignore arbitrary payload and service intents") {
    recorder::AttemptRecorder owner;
    const auto saved = saveAttempt(owner);
    auto result = resultAt(10U, static_cast<core::State>(255U));
    result.events.count = 255U;
    result.events.rejected = MAX_COUNT;
    result.menu.request = countdown::Service::LOG_DUMP;
    result.lifecycle.gate.go = true;
    result.timing_incomplete = true;
    giveFrame(result, 9U, PackStatus::INVALID);
    CHECK(owner.consume(result) == ConsumeStatus::OUTSIDE_ATTEMPT);
    checkSaved(owner, saved);
    CHECK(owner.consume(startAt(10U)) == ConsumeStatus::IGNORED_DUPLICATE);
    CHECK(owner.consume(startAt(9U)) == ConsumeStatus::REJECTED);
    checkSaved(owner, saved);
    CHECK(owner.consume(startAt(11U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().epoch_token == 11U);
    CHECK(owner.summary().missing_results == 0U);
}

TEST_CASE("B15 D070 accepted START stores literal marker and initializes one clean result") {
    recorder::AttemptRecorder owner;
    startOwner(owner, 41U);
    recorder::AttemptSummary expected;
    expected.epoch_token = 41U;
    expected.release_us = 0x12345678U;
    expected.mode = core::Mode::DIRECT;
    expected.observed_results = 1U;
    checkSummary(owner.summary(), expected);
    CHECK(owner.phase() == AttemptPhase::RECORDING);
    CHECK(owner.events().size() == 1U);
    checkEvent(owner, 0U, {{0x78, 0x56, 0x34, 0x12, 0, 3, 0, 0}});
    CHECK(owner.frames().size() == 0U);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 epoch boundary drops prior ready frame and prefix but imports envelope losses") {
    recorder::AttemptRecorder owner;
    sealOwner(owner);
    auto start = startAt(100U, 0x01020304U, core::Mode::WAIT);
    start.events.entries[0] = {7U, static_cast<core::Event>(255U), 255U, 65535U};
    start.events.entries[1] = {0x01020304U, core::Event::START_RELEASE, 6U, 0U};
    start.events.entries[2] = goEvent(0x01020305U, 6U);
    start.events.count = 3U;
    start.events.rejected = 4U;
    start.events.invalid_metadata = 5U;
    start.events.overflowed = true;
    start.skipped_frames = 6U;
    start.ticks = {7U, 1U, 1001U, false};
    start.lifecycle.gate.go = true;
    giveFrame(start, 99U, static_cast<PackStatus>(255U));
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 2U);
    checkEvent(owner, 0U, {{4, 3, 2, 1, 0, 6, 0, 0}});
    checkEvent(owner, 1U, {{5, 3, 2, 1, 1, 6, 0, 0}});
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.frames().rejectedStatusCount() == 0U);
    CHECK(owner.summary().identity_rejected == 0U);
    CHECK(owner.summary().event_semantic_rejected == 0U);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.summary().upstream_event_rejected == 4U);
    CHECK(owner.summary().upstream_event_invalid == 5U);
    CHECK(owner.summary().upstream_event_overflow);
    CHECK(owner.summary().skipped_frames == 6U);
    CHECK(owner.summary().ticks.ticks == 7U);
    CHECK(owner.summary().go_seen);
    CHECK(owner.summary().observed_results == 1U);
}

TEST_CASE("B15 D070 equal highest token is immutable even when replay fabricates START and faults") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U);
    giveFrame(result, 1U, PackStatus::CLAMPED);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    const auto saved = saveAttempt(owner);
    auto replay = startAt(2U, 999U, core::Mode::WAIT);
    replay.events.count = 255U;
    replay.outputs.ui_state = static_cast<core::State>(255U);
    replay.skipped_frames = MAX_COUNT;
    replay.ticks = {MAX_TOKEN, MAX_TOKEN, MAX_COUNT, true};
    giveFrame(replay, MAX_TOKEN, PackStatus::INVALID);
    CHECK(owner.consume(replay) == ConsumeStatus::IGNORED_DUPLICATE);
    checkSaved(owner, saved);
    replay.fresh = false;
    CHECK(owner.consume(replay) == ConsumeStatus::IGNORED_DUPLICATE);
    checkSaved(owner, saved);
}

TEST_CASE("B15 D070 zero lower and newer nonfresh results reject without consuming new identity") {
    recorder::AttemptRecorder owner;
    startOwner(owner, 10U);
    for (auto token : {0ULL, 9ULL, 100ULL}) {
        auto result = startAt(token);
        if (token == 100U) result.fresh = false;
        CHECK(owner.consume(result) == ConsumeStatus::REJECTED);
    }
    CHECK(owner.summary().rejected_results == 3U);
    CHECK(owner.summary().observed_results == 1U);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.events().size() == 1U);
    CHECK(owner.consume(resultAt(11U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.consume(startAt(100U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().epoch_token == 100U);
    CHECK(owner.summary().rejected_results == 0U);
    CHECK(owner.summary().missing_results == 0U);
}

TEST_CASE("B15 D070 malformed START envelopes preserve old evidence and consume fresh identities") {
    recorder::AttemptRecorder owner;
    sealOwner(owner);
    const auto saved = saveAttempt(owner);
    for (unsigned fault = 0U; fault < 9U; ++fault) {
        auto start = startAt(10U + fault);
        switch (fault) {
        case 0U: start.outputs.ui_state = static_cast<core::State>(12U); break;
        case 1U: start.running_mode = static_cast<core::Mode>(0U); break;
        case 2U: start.running_mode = static_cast<core::Mode>(7U); break;
        case 3U: start.events.count = 255U; break;
        case 4U: start.events.count = 0U; break;
        case 5U:
            start.events.count = 2U;
            start.events.entries[1] = start.events.entries[0];
            break;
        case 6U: start.events.entries[0].value = 1U; break;
        case 7U: start.events.entries[0].detail = 2U; break;
        case 8U: ++start.events.entries[0].t_us; break;
        default: break;
        }
        CAPTURE(fault);
        CHECK(owner.consume(start) == ConsumeStatus::REJECTED);
        checkSaved(owner, saved);
        CHECK(owner.consume(startAt(10U + fault)) == ConsumeStatus::IGNORED_DUPLICATE);
        checkSaved(owner, saved);
    }
    CHECK(owner.consume(startAt(19U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().epoch_token == 19U);
}

TEST_CASE("B15 D070 every unknown state and mode rejects a replacement without clearing active data") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    std::uint64_t token = 1U;
    std::uint32_t rejections = 0U;
    for (unsigned state = 12U; state <= 255U; ++state) {
        auto start = startAt(++token);
        start.outputs.ui_state = static_cast<core::State>(state);
        CHECK(owner.consume(start) == ConsumeStatus::REJECTED);
        ++rejections;
    }
    for (unsigned mode = 0U; mode <= 255U; ++mode) {
        if (mode >= 1U && mode <= 6U) continue;
        auto start = startAt(++token);
        start.running_mode = static_cast<core::Mode>(mode);
        start.events.entries[0].detail = static_cast<std::uint8_t>(mode);
        CHECK(owner.consume(start) == ConsumeStatus::REJECTED);
        ++rejections;
    }
    CHECK(owner.summary().epoch_token == 1U);
    CHECK(owner.summary().rejected_results == rejections);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.summary().observed_results == 1U);
    CHECK(owner.events().size() == 1U);
    CHECK(owner.phase() == AttemptPhase::RECORDING);
}

TEST_CASE("B15 D070 invalid ordinary state rejects the whole payload but its gap and identity remain") {
    recorder::AttemptRecorder owner;
    startOwner(owner, 10U);
    auto bad = resultAt(14U, static_cast<core::State>(255U));
    bad.events.count = 1U;
    bad.events.entries[0] = goEvent(9U);
    bad.events.rejected = 25U;
    bad.skipped_frames = 30U;
    bad.lifecycle.gate.go = true;
    giveFrame(bad, 13U);
    CHECK(owner.consume(bad) == ConsumeStatus::REJECTED);
    CHECK(owner.summary().missing_results == 3U);
    CHECK(owner.summary().rejected_results == 1U);
    CHECK(owner.summary().observed_results == 1U);
    CHECK(owner.summary().upstream_event_rejected == 0U);
    CHECK(owner.summary().skipped_frames == 0U);
    CHECK_FALSE(owner.summary().go_seen);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.events().size() == 1U);
    bad.outputs.ui_state = core::State::SEARCH;
    CHECK(owner.consume(bad) == ConsumeStatus::IGNORED_DUPLICATE);
    CHECK(owner.consume(resultAt(15U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().missing_results == 3U);
    CHECK(owner.summary().observed_results == 2U);
}

TEST_CASE("B15 D070 token gaps saturate without narrowing and a valid START replaces the gap epoch") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    CHECK(owner.consume(resultAt(4U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().missing_results == 2U);
    CHECK(owner.consume(resultAt(MAX_TOKEN - 1U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().missing_results == MAX_COUNT);
    CHECK(owner.incomplete());
    CHECK(owner.consume(startAt(MAX_TOKEN)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().epoch_token == MAX_TOKEN);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.summary().observed_results == 1U);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 services mode changes and heading reset requests never erase recording") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U);
    giveFrame(result, 1U);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    std::uint64_t token = 2U;
    for (auto service : {countdown::Service::SENSOR_VIEW, countdown::Service::QTR_CAL,
                         countdown::Service::DRIVE_TEST, countdown::Service::LOG_DUMP}) {
        result = resultAt(++token);
        result.menu.request = service;
        result.menu.menu_toggled = true;
        result.menu.selection_changed = true;
        result.running_mode = core::Mode::WAIT;
        result.lifecycle.heading_reset_requested = true;
        result.lifecycle.services.active = true;
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    }
    CHECK(owner.phase() == AttemptPhase::RECORDING);
    CHECK(owner.summary().epoch_token == 1U);
    CHECK(owner.summary().mode == core::Mode::DIRECT);
    CHECK(owner.summary().observed_results == 6U);
    CHECK(owner.frames().size() == 1U);
    checkFrame(owner, 0U, markedFrame(0x12345678U));
    CHECK(owner.events().size() == 1U);
    CHECK_FALSE(owner.summary().go_seen);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 only an explicit GO pulse latches GO despite requested duty and GO events") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U, core::State::ATTACK);
    result.outputs.motors_enabled = true;
    result.outputs.duty_l = 1.0F;
    result.outputs.duty_r = 1.0F;
    result.events.count = 1U;
    result.events.entries[0] = goEvent(22U);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK_FALSE(owner.summary().go_seen);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.summary().ticks.ticks == 0U);
    result = resultAt(3U);
    result.lifecycle.gate.go = true;
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().go_seen);
    CHECK(owner.consume(resultAt(4U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().go_seen);
}

TEST_CASE("B15 D070 frame receipts retain literal bytes and all known statuses without reencoding") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    const PackStatus statuses[] = {PackStatus::OK, PackStatus::CLAMPED, PackStatus::INVALID};
    for (std::size_t index = 0U; index < 3U; ++index) {
        auto result = resultAt(index + 2U);
        giveFrame(result, index + 1U, statuses[index]);
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
        for (auto& byte : result.frame.data) byte = 0U;
        checkFrame(owner, index, markedFrame(0x12345678U), statuses[index]);
    }
    CHECK(owner.frames().size() == 3U);
    CHECK(owner.frames().clampedCount() == 1U);
    CHECK(owner.frames().invalidCount() == 1U);
    CHECK(owner.summary().last_frame_token == 3U);
    CHECK(owner.summary().identity_rejected == 0U);
    CHECK(owner.incomplete());
}

TEST_CASE("B15 D070 frame identity rejects prior epoch current future and repeated receipts only") {
    recorder::AttemptRecorder owner;
    startOwner(owner, 100U);
    const std::uint64_t frame_tokens[] = {99U, 102U, 999U, 100U};
    for (std::size_t index = 0U; index < 4U; ++index) {
        auto result = resultAt(101U + index);
        giveFrame(result, frame_tokens[index]);
        result.events.count = 1U;
        result.events.entries[0] = goEvent(static_cast<std::uint32_t>(index));
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    }
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.summary().identity_rejected == 4U);
    CHECK(owner.summary().last_frame_token == 0U);
    CHECK(owner.events().size() == 5U);
    auto valid = resultAt(105U);
    giveFrame(valid, 104U);
    CHECK(owner.consume(valid) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().last_frame_token == 104U);
    CHECK(owner.frames().size() == 1U);
    auto duplicate = resultAt(106U);
    giveFrame(duplicate, 104U);
    CHECK(owner.consume(duplicate) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().identity_rejected == 5U);
    CHECK(owner.summary().last_frame_token == 104U);
}

TEST_CASE("B15 D070 absent ready pulse ignores frame bytes token and invalid status") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U);
    giveFrame(result, MAX_TOKEN, static_cast<PackStatus>(255U));
    result.frame_ready = false;
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.frames().rejectedStatusCount() == 0U);
    CHECK(owner.summary().identity_rejected == 0U);
    CHECK(owner.summary().last_frame_token == 0U);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 unknown status rejects only the frame while events and source summary continue") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U);
    giveFrame(result, 1U, static_cast<PackStatus>(255U));
    result.events.count = 1U;
    result.events.entries[0] = goEvent(17U);
    result.skipped_frames = 2U;
    result.ticks = {3U, 1U, 1001U, false};
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.frames().rejectedStatusCount() == 1U);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.events().size() == 2U);
    CHECK(owner.summary().identity_rejected == 0U);
    CHECK(owner.summary().last_frame_token == 0U);
    CHECK(owner.summary().skipped_frames == 2U);
    CHECK(owner.summary().ticks.ticks == 3U);
    CHECK(owner.summary().observed_results == 2U);
    CHECK(owner.incomplete());
}

TEST_CASE("B15 D070 all 21 event positions preserve exact bytes and wrapped insertion order") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U);
    result.events.count = 21U;
    for (std::size_t index = 0U; index < 21U; ++index) {
        const auto time = index < 2U ? 0xFFFFFFFEU + static_cast<std::uint32_t>(index) :
                                      static_cast<std::uint32_t>(21U - index);
        result.events.entries[index] = goEvent(time, static_cast<std::uint8_t>(index % 6U + 1U));
    }
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 22U);
    checkEvent(owner, 1U, {{0xFE, 0xFF, 0xFF, 0xFF, 1, 1, 0, 0}});
    checkEvent(owner, 2U, {{0xFF, 0xFF, 0xFF, 0xFF, 1, 2, 0, 0}});
    for (std::size_t index = 0U; index < 21U; ++index) {
        checkEvent(owner, index + 1U, eventWire(result.events.entries[index]));
    }
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 count 22 and 255 never index event entries but frames and losses continue") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    std::uint64_t token = 1U;
    for (auto count : {22U, 23U, 255U}) {
        auto result = resultAt(++token);
        result.events.count = static_cast<std::uint8_t>(count);
        result.events.entries[0] = goEvent(77U);
        result.events.rejected = 2U;
        result.events.invalid_metadata = 3U;
        result.events.overflowed = true;
        result.skipped_frames = 4U;
        giveFrame(result, token - 1U);
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    }
    CHECK(owner.events().size() == 1U);
    CHECK(owner.frames().size() == 3U);
    CHECK(owner.summary().malformed_batches == 3U);
    CHECK(owner.summary().upstream_event_rejected == 6U);
    CHECK(owner.summary().upstream_event_invalid == 9U);
    CHECK(owner.summary().upstream_event_overflow);
    CHECK(owner.summary().skipped_frames == 4U);
    CHECK(owner.summary().observed_results == 4U);
}

TEST_CASE("B15 D070 malformed event metadata is excluded without suppressing neighboring events or frames") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(2U);
    result.events.count = 6U;
    result.events.entries[0] = goEvent(0U);
    result.events.entries[1] = {1U, core::Event::GO, 0U, 0U};
    result.events.entries[2] = {2U, core::Event::START_RELEASE, 3U, 1U};
    result.events.entries[3] = {3U, static_cast<core::Event>(255U), 0U, 0U};
    result.events.entries[4] = {4U, core::Event::STATE_CHANGE, 12U, 2U};
    result.events.entries[5] = goEvent(0xFFFFFFFFU, 6U);
    giveFrame(result, 1U);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 3U);
    checkEvent(owner, 1U, {{0, 0, 0, 0, 1, 3, 0, 0}});
    checkEvent(owner, 2U, {{0xFF, 0xFF, 0xFF, 0xFF, 1, 6, 0, 0}});
    CHECK(owner.summary().event_semantic_rejected == 4U);
    CHECK(owner.frames().size() == 1U);
    CHECK(owner.summary().observed_results == 2U);
    CHECK(owner.incomplete());
}

TEST_CASE("B15 D070 per-envelope upstream losses accumulate once saturate separately and latch overflow") {
    recorder::AttemptRecorder owner;
    auto start = startAt(1U);
    start.events.rejected = MAX_COUNT - 2U;
    start.events.invalid_metadata = MAX_COUNT - 1U;
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    auto result = resultAt(2U);
    result.events.rejected = 1U;
    result.events.invalid_metadata = 1U;
    result.events.overflowed = true;
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().upstream_event_rejected == MAX_COUNT - 1U);
    CHECK(owner.summary().upstream_event_invalid == MAX_COUNT);
    const auto saved = saveAttempt(owner);
    CHECK(owner.consume(result) == ConsumeStatus::IGNORED_DUPLICATE);
    checkSaved(owner, saved);
    result.token = 3U;
    result.events.rejected = 2U;
    result.events.overflowed = false;
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().upstream_event_rejected == MAX_COUNT);
    CHECK(owner.summary().upstream_event_invalid == MAX_COUNT);
    CHECK(owner.summary().upstream_event_overflow);
}

TEST_CASE("B15 D070 core counters are cumulative snapshots rather than repeated increments") {
    recorder::AttemptRecorder owner;
    auto start = startAt(1U);
    start.skipped_frames = 5U;
    start.ticks = {100U, 2U, 1234U, false};
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    for (std::uint64_t token = 2U; token <= 5U; ++token) {
        auto result = resultAt(token);
        result.skipped_frames = 5U;
        result.ticks = {100U, 2U, 1234U, false};
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    }
    CHECK(owner.summary().skipped_frames == 5U);
    CHECK(owner.summary().ticks.ticks == 100U);
    CHECK(owner.summary().ticks.overruns == 2U);
    CHECK(owner.summary().ticks.max_us == 1234U);
    CHECK(owner.summary().source_regressions == 0U);
    CHECK(owner.summary().observed_results == 5U);
}

TEST_CASE("B15 D070 each tick regression retains its prior snapshot but valid skip and payload advance") {
    recorder::AttemptRecorder owner;
    auto start = startAt(1U);
    start.ticks = {100U, 5U, 1500U, false};
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    const logframe::TickStatistics bad[] = {
        {99U, 5U, 1500U, false}, {101U, 4U, 1500U, false},
        {101U, 5U, 1499U, false}, {101U, 102U, 1600U, false}};
    for (std::size_t index = 0U; index < 4U; ++index) {
        auto result = resultAt(index + 2U);
        result.ticks = bad[index];
        result.skipped_frames = static_cast<std::uint32_t>(index + 1U);
        giveFrame(result, index + 1U);
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
        CHECK(owner.summary().ticks.ticks == 100U);
        CHECK(owner.summary().ticks.overruns == 5U);
        CHECK(owner.summary().ticks.max_us == 1500U);
        CHECK(owner.summary().skipped_frames == index + 1U);
        CHECK(owner.summary().source_regressions == index + 1U);
    }
    CHECK(owner.frames().size() == 4U);
}

TEST_CASE("B15 D070 skip and tick regressions are independent and counted once per envelope") {
    recorder::AttemptRecorder owner;
    auto start = startAt(1U);
    start.skipped_frames = 10U;
    start.ticks = {100U, 5U, 1500U, false};
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    auto result = resultAt(2U);
    result.skipped_frames = 9U;
    result.ticks = {101U, 6U, 1501U, false};
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().skipped_frames == 10U);
    CHECK(owner.summary().ticks.ticks == 101U);
    CHECK(owner.summary().ticks.overruns == 6U);
    CHECK(owner.summary().ticks.max_us == 1501U);
    CHECK(owner.summary().source_regressions == 1U);
    result.token = 3U;
    result.ticks = {1U, 0U, 1U, true};
    result.recording_incomplete = true;
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().source_regressions == 2U);
    CHECK(owner.summary().skipped_frames == 10U);
    CHECK(owner.summary().ticks.ticks == 101U);
    CHECK(owner.summary().ticks.saturated);
    CHECK(owner.summary().timing_incomplete);
    CHECK(owner.summary().recording_incomplete);
}

TEST_CASE("B15 D070 timing saturation and source incomplete flags cannot be cleared by later results") {
    recorder::AttemptRecorder owner;
    auto start = startAt(1U);
    start.ticks = {MAX_TOKEN, MAX_TOKEN, MAX_COUNT, true};
    start.recording_incomplete = true;
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    auto result = resultAt(2U);
    result.ticks = {MAX_TOKEN, MAX_TOKEN, MAX_COUNT, false};
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().ticks.saturated);
    CHECK(owner.summary().timing_incomplete);
    CHECK(owner.summary().recording_incomplete);
    CHECK(owner.summary().source_regressions == 0U);
    CHECK(owner.incomplete());
}

TEST_CASE("B15 D070 every known initial state and running mode permits validated START") {
    recorder::AttemptRecorder owner;
    std::uint64_t token = 0U;
    for (unsigned state = 0U; state <= 11U; ++state) {
        for (unsigned mode = 1U; mode <= 6U; ++mode) {
            auto start = startAt(++token, state, static_cast<core::Mode>(mode));
            start.outputs.ui_state = static_cast<core::State>(state);
            CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
            const auto expected_phase = state == 1U || state == 10U ?
                AttemptPhase::DRAINING : AttemptPhase::RECORDING;
            CHECK(owner.phase() == expected_phase);
            CHECK(owner.summary().epoch_token == token);
            CHECK(owner.summary().mode == static_cast<core::Mode>(mode));
            CHECK(owner.summary().observed_results == 1U);
            CHECK(owner.events().size() == 1U);
            CHECK(owner.frames().size() == 0U);
            CHECK_FALSE(owner.incomplete());
        }
    }
}

TEST_CASE("B15 D070 STOPPED drains once then accepts only the stopping receipt and seals") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto stop = resultAt(2U, core::State::STOPPED);
    giveFrame(stop, 1U);
    CHECK(owner.consume(stop) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::DRAINING);
    CHECK_FALSE(owner.incomplete());
    auto tail = resultAt(3U, core::State::IDLE);
    giveFrame(tail, 2U, PackStatus::OK, 0xFFFFFFFFU);
    tail.events.count = 1U;
    tail.events.entries[0] = goEvent(0U);
    tail.ticks = {2U, 0U, 800U, false};
    CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::SEALED);
    CHECK(owner.frames().size() == 2U);
    CHECK(owner.events().size() == 2U);
    CHECK(owner.summary().last_frame_token == 2U);
    CHECK(owner.summary().observed_results == 3U);
    CHECK(owner.summary().ticks.ticks == 2U);
    CHECK_FALSE(owner.summary().final_frame_missing);
    CHECK_FALSE(owner.incomplete());
    checkFrame(owner, 1U, markedFrame(0xFFFFFFFFU));
}

TEST_CASE("B15 D070 every escape fault drains only in EDGE_ESCAPE and none keeps recording") {
    recorder::AttemptRecorder owner;
    std::uint64_t token = 0U;
    for (auto fault : {edge::EscapeFault::WHITE_PATTERN, edge::EscapeFault::REPLAN_LIMIT,
                       edge::EscapeFault::PERMISSION_LOST, edge::EscapeFault::INVALID_CONTEXT}) {
        startOwner(owner, ++token);
        auto ordinary = resultAt(++token);
        ordinary.escape_fault = fault;
        CHECK(owner.consume(ordinary) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::RECORDING);
        auto edge = resultAt(++token, core::State::EDGE_ESCAPE);
        CHECK(owner.consume(edge) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::RECORDING);
        edge.token = ++token;
        edge.escape_fault = fault;
        CHECK(owner.consume(edge) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::DRAINING);
    }
}

TEST_CASE("B15 D070 countdown cancellation and same START IDLE drain but ordinary IDLE does not") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    CHECK(owner.consume(resultAt(2U, core::State::IDLE)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::DRAINING);
    auto start = startAt(3U);
    start.outputs.ui_state = core::State::IDLE;
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::DRAINING);
    startOwner(owner, 4U);
    CHECK(owner.consume(resultAt(5U, core::State::SEARCH)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.consume(resultAt(6U, core::State::IDLE)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::RECORDING);
    CHECK(owner.summary().observed_results == 3U);
}

TEST_CASE("B15 D070 missing wrong or unknown-status final receipt seals with explicit missing evidence") {
    recorder::AttemptRecorder owner;
    std::uint64_t token = 0U;
    for (unsigned fault = 0U; fault < 3U; ++fault) {
        startOwner(owner, ++token);
        const auto stopping = ++token;
        CHECK(owner.consume(resultAt(stopping, core::State::STOPPED)) == ConsumeStatus::ACCEPTED);
        auto tail = resultAt(++token);
        if (fault == 1U) giveFrame(tail, stopping - 1U);
        if (fault == 2U) giveFrame(tail, stopping, static_cast<PackStatus>(255U));
        tail.events.count = 1U;
        tail.events.entries[0] = goEvent(999U);
        CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::SEALED);
        CHECK(owner.summary().final_frame_missing);
        CHECK(owner.summary().identity_rejected == (fault == 1U ? 1U : 0U));
        CHECK(owner.frames().rejectedStatusCount() == (fault == 2U ? 1U : 0U));
        CHECK(owner.frames().size() == 0U);
        CHECK(owner.events().size() == 2U);
        CHECK(owner.incomplete());
    }
}

TEST_CASE("B15 D070 known CLAMPED and INVALID final receipts are retained and are not missing") {
    recorder::AttemptRecorder owner;
    std::uint64_t token = 0U;
    for (auto status : {PackStatus::CLAMPED, PackStatus::INVALID}) {
        startOwner(owner, ++token);
        const auto stopping = ++token;
        CHECK(owner.consume(resultAt(stopping, core::State::STOPPED)) == ConsumeStatus::ACCEPTED);
        auto tail = resultAt(++token);
        giveFrame(tail, stopping, status);
        CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::SEALED);
        CHECK_FALSE(owner.summary().final_frame_missing);
        CHECK(owner.summary().last_frame_token == stopping);
        CHECK(owner.frames().size() == 1U);
        checkFrame(owner, 0U, markedFrame(0x12345678U), status);
        CHECK(owner.incomplete());
    }
}

TEST_CASE("B15 D070 malformed state does not seal draining and its consumed identity prevents false tail") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    CHECK(owner.consume(resultAt(2U, core::State::STOPPED)) == ConsumeStatus::ACCEPTED);
    auto bad = resultAt(3U, static_cast<core::State>(255U));
    giveFrame(bad, 2U);
    CHECK(owner.consume(bad) == ConsumeStatus::REJECTED);
    CHECK(owner.phase() == AttemptPhase::DRAINING);
    CHECK(owner.summary().rejected_results == 1U);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.frames().size() == 0U);
    bad.outputs.ui_state = core::State::IDLE;
    CHECK(owner.consume(bad) == ConsumeStatus::IGNORED_DUPLICATE);
    auto late = resultAt(4U);
    giveFrame(late, 3U);
    CHECK(owner.consume(late) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::SEALED);
    CHECK(owner.summary().identity_rejected == 1U);
    CHECK(owner.summary().final_frame_missing);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.summary().observed_results == 3U);
}

TEST_CASE("B15 D070 skipped tail token cannot accept an old stopping receipt as current") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    CHECK(owner.consume(resultAt(2U, core::State::STOPPED)) == ConsumeStatus::ACCEPTED);
    auto tail = resultAt(4U);
    giveFrame(tail, 2U);
    CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::SEALED);
    CHECK(owner.summary().missing_results == 1U);
    CHECK(owner.summary().identity_rejected == 1U);
    CHECK(owner.summary().final_frame_missing);
    CHECK(owner.frames().size() == 0U);
}

TEST_CASE("B15 D070 malformed tail event count still seals after accepting the final frame") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    CHECK(owner.consume(resultAt(2U, core::State::STOPPED)) == ConsumeStatus::ACCEPTED);
    auto tail = resultAt(3U);
    giveFrame(tail, 2U);
    tail.events.count = 255U;
    CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::SEALED);
    CHECK_FALSE(owner.summary().final_frame_missing);
    CHECK(owner.summary().malformed_batches == 1U);
    CHECK(owner.frames().size() == 1U);
}

TEST_CASE("B15 D070 sealed data survives services reset rejected identities and ignored future payload") {
    recorder::AttemptRecorder owner;
    sealOwner(owner);
    const auto saved = saveAttempt(owner);
    owner.onRobotReset();
    checkSaved(owner, saved);
    auto result = resultAt(1000U, core::State::STOPPED);
    giveFrame(result, 999U, PackStatus::INVALID);
    result.events.count = 255U;
    result.events.rejected = MAX_COUNT;
    result.menu.request = countdown::Service::QTR_CAL;
    CHECK(owner.consume(result) == ConsumeStatus::OUTSIDE_ATTEMPT);
    checkSaved(owner, saved);
    CHECK(owner.consume(startAt(1000U)) == ConsumeStatus::IGNORED_DUPLICATE);
    CHECK(owner.consume(startAt(500U)) == ConsumeStatus::REJECTED);
    checkSaved(owner, saved);
    CHECK(owner.consume(startAt(1001U)) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().observed_results == 1U);
    CHECK(owner.summary().epoch_token == 1001U);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.events().size() == 1U);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 reset interrupts active phases without deleting bytes or inventing timing evidence") {
    recorder::AttemptRecorder owner;
    std::uint64_t token = 0U;
    for (unsigned scenario = 0U; scenario < 4U; ++scenario) {
        auto start = startAt(++token);
        start.lifecycle.gate.go = (scenario & 1U) != 0U;
        CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
        auto result = resultAt(++token, scenario < 2U ? core::State::SEARCH : core::State::STOPPED);
        giveFrame(result, token - 1U);
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
        auto expected = saveAttempt(owner);
        expected.phase = AttemptPhase::INTERRUPTED;
        expected.incomplete = true;
        expected.summary.interrupted = true;
        expected.summary.timing_incomplete = expected.summary.go_seen;
        owner.onRobotReset();
        checkSaved(owner, expected);
        owner.onRobotReset();
        checkSaved(owner, expected);
        CHECK(owner.consume(result) == ConsumeStatus::IGNORED_DUPLICATE);
        checkSaved(owner, expected);
        CHECK(owner.consume(resultAt(++token)) == ConsumeStatus::OUTSIDE_ATTEMPT);
        checkSaved(owner, expected);
    }
}

TEST_CASE("B15 D070 valid replacement START clears draining interruption and all prior loss domains") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    auto result = resultAt(5U, core::State::STOPPED);
    result.events.count = 255U;
    result.events.rejected = 2U;
    result.events.invalid_metadata = 3U;
    result.events.overflowed = true;
    result.recording_incomplete = true;
    result.timing_incomplete = true;
    giveFrame(result, 4U, PackStatus::INVALID);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::DRAINING);
    owner.onRobotReset();
    CHECK(owner.phase() == AttemptPhase::INTERRUPTED);
    CHECK(owner.consume(startAt(8U, 17U, core::Mode::SIDESTEP_L)) == ConsumeStatus::ACCEPTED);
    recorder::AttemptSummary expected;
    expected.epoch_token = 8U;
    expected.release_us = 17U;
    expected.mode = core::Mode::SIDESTEP_L;
    expected.observed_results = 1U;
    checkSummary(owner.summary(), expected);
    CHECK(owner.frames().size() == 0U);
    CHECK(owner.frames().invalidCount() == 0U);
    CHECK(owner.events().size() == 1U);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 terminal exhaustion at UINT64_MAX retains one final actual receipt then interrupts") {
    recorder::AttemptRecorder owner;
    auto start = startAt(MAX_TOKEN);
    start.lifecycle.gate.go = true;
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    auto terminal = terminalResult();
    giveFrame(terminal, MAX_TOKEN);
    terminal.events.count = 1U;
    terminal.events.entries[0] = {0xFFFFFFFFU, core::Event::FAULT, 7U, 128U};
    terminal.ticks = {1U, 0U, 789U, false};
    CHECK(owner.consume(terminal) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::INTERRUPTED);
    CHECK(owner.summary().terminal_exhausted);
    CHECK(owner.summary().interrupted);
    CHECK(owner.summary().timing_incomplete);
    CHECK(owner.summary().observed_results == 2U);
    CHECK(owner.summary().last_frame_token == MAX_TOKEN);
    CHECK(owner.summary().missing_results == 0U);
    CHECK(owner.frames().size() == 1U);
    checkFrame(owner, 0U, markedFrame(0x12345678U));
    checkEvent(owner, 1U, {{0xFF, 0xFF, 0xFF, 0xFF, 9, 7, 128, 0}});
    const auto saved = saveAttempt(owner);
    terminal.events.count = 255U;
    terminal.frame_status = PackStatus::INVALID;
    CHECK(owner.consume(terminal) == ConsumeStatus::IGNORED_DUPLICATE);
    CHECK(owner.consume(startAt(MAX_TOKEN)) == ConsumeStatus::IGNORED_DUPLICATE);
    checkSaved(owner, saved);
}

TEST_CASE("B15 D070 terminal zero requires exhausted highest identity stale STOPPED fault and no START") {
    recorder::AttemptRecorder owner;
    startOwner(owner, MAX_TOKEN - 1U);
    CHECK(owner.consume(terminalResult()) == ConsumeStatus::REJECTED);
    CHECK(owner.consume(resultAt(MAX_TOKEN)) == ConsumeStatus::ACCEPTED);
    for (unsigned fault = 0U; fault < 4U; ++fault) {
        auto terminal = terminalResult();
        if (fault == 0U) terminal.fresh = true;
        if (fault == 1U) terminal.outputs.ui_state = core::State::SEARCH;
        if (fault == 2U) terminal.contract_faults = fsm::APPLICATION_CONTRACT;
        if (fault == 3U) terminal.lifecycle.gate.start_release = true;
        CHECK(owner.consume(terminal) == ConsumeStatus::REJECTED);
        CHECK(owner.phase() == AttemptPhase::RECORDING);
    }
    CHECK(owner.summary().rejected_results == 5U);
    CHECK(owner.consume(terminalResult()) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().terminal_exhausted);
    CHECK_FALSE(owner.summary().timing_incomplete);
    CHECK(owner.summary().observed_results == 3U);
}

TEST_CASE("B15 D070 terminal draining receipt at maximum accepts known status or marks missing") {
    recorder::AttemptRecorder owner;
    startOwner(owner, MAX_TOKEN - 1U);
    CHECK(owner.consume(resultAt(MAX_TOKEN, core::State::STOPPED)) == ConsumeStatus::ACCEPTED);
    auto terminal = terminalResult();
    giveFrame(terminal, MAX_TOKEN, PackStatus::INVALID);
    CHECK(owner.consume(terminal) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::INTERRUPTED);
    CHECK_FALSE(owner.summary().final_frame_missing);
    CHECK(owner.summary().last_frame_token == MAX_TOKEN);
    CHECK(owner.frames().invalidCount() == 1U);
    CHECK(owner.summary().terminal_exhausted);
}

TEST_CASE("B15 D070 terminal draining without final frame or with wrong stopping identity reports loss") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        recorder::AttemptRecorder owner;
        startOwner(owner, MAX_TOKEN - 2U);
        auto stop = resultAt(MAX_TOKEN - 1U, core::State::STOPPED);
        CHECK(owner.consume(stop) == ConsumeStatus::ACCEPTED);
        auto malformed = resultAt(MAX_TOKEN, static_cast<core::State>(255U));
        CHECK(owner.consume(malformed) == ConsumeStatus::REJECTED);
        auto terminal = terminalResult();
        if (scenario == 1U) giveFrame(terminal, MAX_TOKEN);
        if (scenario == 2U) giveFrame(terminal, MAX_TOKEN - 1U);
        CHECK(owner.consume(terminal) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::INTERRUPTED);
        CHECK(owner.summary().final_frame_missing);
        CHECK(owner.summary().identity_rejected == (scenario == 0U ? 0U : 1U));
        CHECK(owner.summary().rejected_results == 1U);
        CHECK(owner.frames().size() == 0U);
    }
}

TEST_CASE("B15 D070 terminal outside EMPTY SEALED and INTERRUPTED preserves stored summaries") {
    for (unsigned phase = 0U; phase < 3U; ++phase) {
        recorder::AttemptRecorder owner;
        if (phase == 1U) sealOwner(owner);
        if (phase == 2U) {
            startOwner(owner);
            owner.onRobotReset();
        }
        CHECK(owner.consume(resultAt(MAX_TOKEN)) == ConsumeStatus::OUTSIDE_ATTEMPT);
        const auto saved = saveAttempt(owner);
        auto terminal = terminalResult();
        giveFrame(terminal, MAX_TOKEN);
        terminal.events.count = 255U;
        terminal.events.rejected = MAX_COUNT;
        CHECK(owner.consume(terminal) == ConsumeStatus::OUTSIDE_ATTEMPT);
        checkSaved(owner, saved);
        CHECK(owner.consume(terminal) == ConsumeStatus::IGNORED_DUPLICATE);
        checkSaved(owner, saved);
    }
}

TEST_CASE("B15 D070 D028 event 4097 overflows while frame receipts continue independently") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    for (std::uint64_t token = 2U; token <= 4096U; ++token) {
        auto result = resultAt(token);
        result.events.count = 1U;
        result.events.entries[0] = goEvent(static_cast<std::uint32_t>(token));
        giveFrame(result, token - 1U, PackStatus::OK, static_cast<std::uint32_t>(token));
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    }
    CHECK(owner.events().size() == 4096U);
    CHECK_FALSE(owner.events().overflowed());
    CHECK(owner.frames().size() == 4095U);
    auto result = resultAt(4097U);
    result.events.count = 1U;
    result.events.entries[0] = goEvent(4097U);
    giveFrame(result, 4096U, PackStatus::OK, 4097U);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 4096U);
    CHECK(owner.events().overflowed());
    CHECK(owner.events().rejectedCount() == 1U);
    CHECK(owner.frames().size() == 4096U);
    CHECK_FALSE(owner.frames().incomplete());
    checkEvent(owner, 0U, {{0x78, 0x56, 0x34, 0x12, 0, 3, 0, 0}});
    checkEvent(owner, 4095U, {{0, 16, 0, 0, 1, 3, 0, 0}});
    checkFrame(owner, 4095U, markedFrame(4097U));
    CHECK(owner.summary().upstream_event_rejected == 0U);
    CHECK(owner.summary().event_semantic_rejected == 0U);
    CHECK(owner.incomplete());
}

TEST_CASE("B15 D070 D069 frame overwrite does not consume event capacity or suppress new events") {
    recorder::AttemptRecorder owner;
    startOwner(owner);
    for (std::uint64_t token = 2U; token <= 10003U; ++token) {
        auto result = resultAt(token);
        giveFrame(result, token - 1U, PackStatus::OK, static_cast<std::uint32_t>(token));
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
        if (token == 10002U) {
            CHECK(owner.frames().size() == 10001U);
            CHECK(owner.frames().overwrittenCount() == 0U);
        }
    }
    CHECK(owner.frames().size() == 10001U);
    CHECK(owner.frames().overwrittenCount() == 1U);
    checkFrame(owner, 0U, markedFrame(3U));
    checkFrame(owner, 10000U, markedFrame(10003U));
    auto result = resultAt(10004U);
    result.events.count = 1U;
    result.events.entries[0] = goEvent(0U);
    CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 2U);
    CHECK_FALSE(owner.events().overflowed());
    CHECK(owner.events().rejectedCount() == 0U);
    CHECK(owner.summary().identity_rejected == 0U);
    CHECK(owner.incomplete());
}

TEST_CASE("B15 D070 each upstream loss flag independently makes otherwise clean evidence incomplete") {
    recorder::AttemptRecorder owner;
    std::uint64_t token = 0U;
    for (unsigned loss = 0U; loss < 7U; ++loss) {
        auto start = startAt(++token);
        if (loss == 0U) start.events.rejected = 1U;
        if (loss == 1U) start.events.invalid_metadata = 1U;
        if (loss == 2U) start.events.overflowed = true;
        if (loss == 3U) start.skipped_frames = 1U;
        if (loss == 4U) start.timing_incomplete = true;
        if (loss == 5U) start.recording_incomplete = true;
        if (loss == 6U) start.ticks.saturated = true;
        CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
        CHECK(owner.phase() == AttemptPhase::RECORDING);
        CHECK(owner.incomplete());
        CHECK_FALSE(owner.frames().incomplete());
        CHECK_FALSE(owner.events().overflowed());
        CHECK(owner.summary().observed_results == 1U);
    }
}

namespace {
struct ExpectedAttempt {
    recorder::AttemptSummary summary;
    std::vector<recorder::StoredFrame> frames;
    std::vector<logframe::EventBytes> events;
    std::uint32_t rejected_status = 0U;
    std::uint32_t clamped = 0U;
    std::uint32_t invalid = 0U;
};

void rememberOracleResult(ExpectedAttempt& expected, const fsm::RobotResult& result) {
    ++expected.summary.observed_results;
    expected.summary.skipped_frames = result.skipped_frames;
    expected.summary.ticks = result.ticks;
    expected.summary.go_seen = expected.summary.go_seen || result.lifecycle.gate.go;
    for (std::size_t index = 0U; index < result.events.count; ++index) {
        expected.events.push_back(eventWire(result.events.entries[index]));
    }
    if (!result.frame_ready) return;
    if (result.frame_token != result.token - 1U) {
        ++expected.summary.identity_rejected;
        return;
    }
    if (result.frame_status == static_cast<PackStatus>(3U)) {
        ++expected.rejected_status;
        return;
    }
    expected.frames.push_back({result.frame, result.frame_status});
    expected.summary.last_frame_token = result.frame_token;
    if (result.frame_status == PackStatus::CLAMPED) ++expected.clamped;
    if (result.frame_status == PackStatus::INVALID) ++expected.invalid;
}

void checkOracleAttempt(const recorder::AttemptRecorder& owner, const ExpectedAttempt& expected) {
    checkSummary(owner.summary(), expected.summary);
    CHECK(owner.frames().size() == expected.frames.size());
    CHECK(owner.events().size() == expected.events.size());
    CHECK(owner.frames().rejectedStatusCount() == expected.rejected_status);
    CHECK(owner.frames().clampedCount() == expected.clamped);
    CHECK(owner.frames().invalidCount() == expected.invalid);
    CHECK(owner.frames().overwrittenCount() == 0U);
    CHECK(owner.events().rejectedCount() == 0U);
    CHECK_FALSE(owner.events().overflowed());
    const bool incomplete = expected.summary.skipped_frames != 0U ||
        expected.summary.identity_rejected != 0U || expected.rejected_status != 0U ||
        expected.clamped != 0U || expected.invalid != 0U;
    CHECK(owner.incomplete() == incomplete);
    for (std::size_t index = 0U; index < expected.frames.size(); ++index) {
        checkFrame(owner, index, expected.frames[index].bytes, expected.frames[index].status);
    }
    for (std::size_t index = 0U; index < expected.events.size(); ++index) {
        checkEvent(owner, index, expected.events[index]);
    }
}

fsm::RobotResult oracleResult(std::uint64_t token, unsigned step, std::uint32_t& seed) {
    const auto choice = randomNext(seed);
    auto result = resultAt(token, step == 127U ? core::State::STOPPED : core::State::SEARCH);
    result.lifecycle.gate.go = step == 5U;
    result.skipped_frames = step / 16U;
    result.ticks = {step + 1U, step / 10U, step + 200U, false};
    result.events.count = static_cast<std::uint8_t>(choice % 3U);
    for (std::size_t index = 0U; index < result.events.count; ++index) {
        result.events.entries[index] = goEvent(randomNext(seed),
            static_cast<std::uint8_t>((choice >> 16U) % 6U + 1U));
    }
    if ((choice & 1U) != 0U) {
        const auto frame_token = choice % 13U == 0U ? token : token - 1U;
        giveFrame(result, frame_token, static_cast<PackStatus>((choice >> 8U) % 4U),
                   randomNext(seed));
    }
    return result;
}

void runOracleAttempt(recorder::AttemptRecorder& owner, std::uint32_t& seed,
                       std::uint64_t& token) {
    const auto release = randomNext(seed);
    const auto mode = static_cast<core::Mode>(randomNext(seed) % 6U + 1U);
    const auto start = startAt(++token, release, mode);
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    ExpectedAttempt expected;
    expected.summary.epoch_token = token;
    expected.summary.release_us = release;
    expected.summary.mode = mode;
    rememberOracleResult(expected, start);
    for (unsigned step = 0U; step < 128U; ++step) {
        CAPTURE(step);
        auto result = oracleResult(++token, step, seed);
        CHECK(owner.consume(result) == ConsumeStatus::ACCEPTED);
        rememberOracleResult(expected, result);
        checkSummary(owner.summary(), expected.summary);
        if (step % 17U == 0U) {
            const auto saved = saveAttempt(owner);
            result.lifecycle.gate.start_release = true;
            result.events.count = 255U;
            CHECK(owner.consume(result) == ConsumeStatus::IGNORED_DUPLICATE);
            checkSaved(owner, saved);
        }
    }
    CHECK(owner.phase() == AttemptPhase::DRAINING);
    auto tail = resultAt(++token, core::State::IDLE);
    tail.skipped_frames = expected.summary.skipped_frames;
    tail.ticks = expected.summary.ticks;
    giveFrame(tail, token - 1U);
    CHECK(owner.consume(tail) == ConsumeStatus::ACCEPTED);
    rememberOracleResult(expected, tail);
    CHECK(owner.phase() == AttemptPhase::SEALED);
    checkOracleAttempt(owner, expected);
    const auto saved = saveAttempt(owner);
    owner.onRobotReset();
    CHECK(owner.consume(resultAt(++token)) == ConsumeStatus::OUTSIDE_ATTEMPT);
    checkSaved(owner, saved);
}
} // namespace

TEST_CASE("B15 D070 fixed seed vector oracle checks 32 complete attempts with mixed receipts and replay") {
    recorder::AttemptRecorder owner;
    std::uint32_t seed = 0xD070B15U;
    std::uint64_t token = 0U;
    for (unsigned attempt = 0U; attempt < 32U; ++attempt) {
        CAPTURE(attempt);
        runOracleAttempt(owner, seed, token);
    }
}

TEST_CASE("B15 D070 START marker at final bounded event slot excludes every preceding event") {
    recorder::AttemptRecorder owner;
    auto start = startAt(1U);
    const auto marker = start.events.entries[0];
    for (std::size_t index = 0U; index < 20U; ++index) {
        start.events.entries[index] = {static_cast<std::uint32_t>(index),
                                       static_cast<core::Event>(255U), 255U, 65535U};
    }
    start.events.entries[20] = marker;
    start.events.count = 21U;
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    CHECK(owner.events().size() == 1U);
    checkEvent(owner, 0U, {{0x78, 0x56, 0x34, 0x12, 0, 3, 0, 0}});
    CHECK(owner.summary().event_semantic_rejected == 0U);
    CHECK_FALSE(owner.incomplete());
}

TEST_CASE("B15 D070 START event alone cannot create or replace an epoch without its gate pulse") {
    recorder::AttemptRecorder owner;
    auto marker_only = startAt(1U);
    marker_only.lifecycle.gate.start_release = false;
    CHECK(owner.consume(marker_only) == ConsumeStatus::OUTSIDE_ATTEMPT);
    CHECK(owner.phase() == AttemptPhase::EMPTY);
    startOwner(owner, 2U);
    marker_only = startAt(3U, 999U, core::Mode::WAIT);
    marker_only.lifecycle.gate.start_release = false;
    CHECK(owner.consume(marker_only) == ConsumeStatus::ACCEPTED);
    CHECK(owner.summary().epoch_token == 2U);
    CHECK(owner.summary().release_us == 0x12345678U);
    CHECK(owner.summary().mode == core::Mode::DIRECT);
    CHECK(owner.events().size() == 2U);
    checkEvent(owner, 1U, {{0xE7, 3, 0, 0, 0, 6, 0, 0}});
}

TEST_CASE("B15 D070 terminal malformed count and unknown final status retain separate bounded losses") {
    recorder::AttemptRecorder owner;
    auto start = startAt(MAX_TOKEN);
    start.outputs.ui_state = core::State::STOPPED;
    CHECK(owner.consume(start) == ConsumeStatus::ACCEPTED);
    auto terminal = terminalResult();
    terminal.events.count = 255U;
    terminal.events.rejected = 7U;
    terminal.events.invalid_metadata = 8U;
    terminal.ticks = {10U, 2U, 1200U, false};
    giveFrame(terminal, MAX_TOKEN, static_cast<PackStatus>(255U));
    CHECK(owner.consume(terminal) == ConsumeStatus::ACCEPTED);
    CHECK(owner.phase() == AttemptPhase::INTERRUPTED);
    CHECK(owner.summary().malformed_batches == 1U);
    CHECK(owner.summary().upstream_event_rejected == 7U);
    CHECK(owner.summary().upstream_event_invalid == 8U);
    CHECK(owner.summary().ticks.ticks == 10U);
    CHECK(owner.summary().identity_rejected == 0U);
    CHECK(owner.frames().rejectedStatusCount() == 1U);
    CHECK(owner.summary().final_frame_missing);
    CHECK(owner.events().size() == 1U);
    CHECK(owner.frames().size() == 0U);
}

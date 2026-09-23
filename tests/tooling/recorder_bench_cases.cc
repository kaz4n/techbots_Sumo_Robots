// Exercises the frozen D091 bench API with independent synthetic host clocks.
// Checks real Robot/Gate/Recorder integration without inspecting Runner bodies.
// Built only by test_recorder_bench_runner.py, outside the normal .cpp test glob.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "recorder_bench.h"
#include "config.h"
#include <cstring>
#include <cstdint>

namespace {
using recorder_bench::Failure;
using recorder_bench::Phase;
using recorder_bench::Report;
using recorder_bench::Runner;
struct Clock {
    std::uint32_t now = 0U;
    std::uint32_t cost = 0U;
    std::uint32_t reads = 0U;
    static std::uint32_t read(void* context) {
        auto& clock = *static_cast<Clock*>(context);
        return clock.now + (clock.reads++ == 0U ? 0U : clock.cost);
    }
    void poll(Runner& runner, std::uint32_t delta = config::TICK_US) {
        now += delta;
        reads = 0U;
        runner.poll();
    }
};
std::uint32_t phase(const Runner& runner) { return runner.report().phase; }
bool terminal(const Runner& runner) {
    return phase(runner) == static_cast<std::uint32_t>(Phase::FROZEN) ||
        phase(runner) == static_cast<std::uint32_t>(Phase::FAILED);
}
std::uint64_t join(std::uint32_t low, std::uint32_t high) {
    return static_cast<std::uint64_t>(low) | (static_cast<std::uint64_t>(high) << 32U);
}
std::uint32_t little32(const std::uint8_t* bytes) {
    return static_cast<std::uint32_t>(bytes[0]) |
        (static_cast<std::uint32_t>(bytes[1]) << 8U) |
        (static_cast<std::uint32_t>(bytes[2]) << 16U) |
        (static_cast<std::uint32_t>(bytes[3]) << 24U);
}
void byteCrc(std::uint32_t& crc, std::uint8_t byte) {
    crc ^= byte;
    for (unsigned bit = 0U; bit < 8U; ++bit) {
        crc = (crc & 1U) != 0U ? (crc >> 1U) ^ 0xEDB88320U : crc >> 1U;
    }
}
std::uint32_t sourceCrc(const recorder::AttemptRecorder& source) {
    std::uint32_t crc = 0xFFFFFFFFU;
    for (std::size_t index = 0U; index < source.frames().size(); ++index) {
        recorder::StoredFrame row;
        REQUIRE(source.frames().read(index, row));
        for (auto value : row.bytes.data) byteCrc(crc, value);
        byteCrc(crc, static_cast<std::uint8_t>(row.status));
    }
    for (std::size_t index = 0U; index < source.events().size(); ++index) {
        for (auto value : source.events().at(index)->data) byteCrc(crc, value);
    }
    return crc ^ 0xFFFFFFFFU;
}
void acceptedStart(Clock& clock, Runner& runner) {
    for (unsigned count = 0U; count < 2000U &&
         runner.source().phase() == recorder::AttemptPhase::EMPTY && !terminal(runner); ++count) {
        clock.poll(runner);
    }
    INFO("phase=" << phase(runner) << " failure=" << runner.report().failure);
    REQUIRE(runner.source().phase() == recorder::AttemptPhase::RECORDING);
    REQUIRE(runner.report().failure == static_cast<std::uint32_t>(Failure::NONE));
}
void finish(Clock& clock, Runner& runner) {
    for (std::uint32_t count = 0U; count < 210000U && !terminal(runner); ++count) {
        const auto before = runner.report();
        clock.poll(runner);
        CHECK(runner.report().ticks - before.ticks <= 1U);
        CHECK(runner.report().checksum_rows - before.checksum_rows <= 1U);
        if (before.phase == static_cast<std::uint32_t>(Phase::CHECKSUM)) {
            CHECK(runner.report().ticks == before.ticks);
        }
    }
    INFO("phase=" << phase(runner) << " failure=" << runner.report().failure);
    REQUIRE(phase(runner) == static_cast<std::uint32_t>(Phase::FROZEN));
    REQUIRE(runner.report().failure == static_cast<std::uint32_t>(Failure::NONE));
}
void summaryMatches(const Runner& runner) {
    const auto& report = runner.report();
    const auto& source = runner.source();
    const auto& summary = source.summary();
    CHECK(report.source_phase == static_cast<std::uint32_t>(source.phase()));
    CHECK(report.frame_count == source.frames().size());
    CHECK(report.event_count == source.events().size());
    CHECK(join(report.epoch_lo, report.epoch_hi) == summary.epoch_token);
    CHECK(join(report.last_frame_lo, report.last_frame_hi) == summary.last_frame_token);
    CHECK(report.release_us == summary.release_us);
    CHECK(report.mode == static_cast<std::uint32_t>(summary.mode));
#define MATCH_SUMMARY(field) CHECK(report.field == static_cast<std::uint32_t>(summary.field))
    MATCH_SUMMARY(observed_results); MATCH_SUMMARY(missing_results);
    MATCH_SUMMARY(rejected_results); MATCH_SUMMARY(identity_rejected);
    MATCH_SUMMARY(malformed_batches); MATCH_SUMMARY(event_semantic_rejected);
    MATCH_SUMMARY(upstream_event_rejected); MATCH_SUMMARY(upstream_event_invalid);
    MATCH_SUMMARY(source_regressions); MATCH_SUMMARY(skipped_frames);
    MATCH_SUMMARY(upstream_event_overflow); MATCH_SUMMARY(timing_incomplete);
    MATCH_SUMMARY(recording_incomplete); MATCH_SUMMARY(go_seen);
    MATCH_SUMMARY(final_frame_missing); MATCH_SUMMARY(interrupted);
    MATCH_SUMMARY(terminal_exhausted);
#undef MATCH_SUMMARY
    CHECK(join(report.timing_ticks_lo, report.timing_ticks_hi) == summary.ticks.ticks);
    CHECK(join(report.timing_overruns_lo, report.timing_overruns_hi) == summary.ticks.overruns);
    CHECK(report.timing_max_us == summary.ticks.max_us);
    CHECK(report.timing_saturated == static_cast<std::uint32_t>(summary.ticks.saturated));
    CHECK(report.frame_overwritten == source.frames().overwrittenCount());
    CHECK(report.frame_rejected_status == source.frames().rejectedStatusCount());
    CHECK(report.frame_clamped == source.frames().clampedCount());
    CHECK(report.frame_invalid == source.frames().invalidCount());
    CHECK(report.event_overflow == static_cast<std::uint32_t>(source.events().overflowed()));
    CHECK(report.event_rejected == source.events().rejectedCount());
    CHECK(report.incomplete == static_cast<std::uint32_t>(source.incomplete()));
}
void staysFrozen(Clock& clock, Runner& runner) {
    const auto saved = runner.report();
    for (auto delta : {0U, 1U, 1000U, 0x80000000U, 0xFFFFFFFFU}) clock.poll(runner, delta);
    CHECK(std::memcmp(&saved, &runner.report(), sizeof(saved)) == 0);
}
} // namespace

TEST_CASE("D091 B15 missing clock and repeated begin fail permanently") {
    Runner absent({});
    CHECK_FALSE(absent.begin());
    CHECK(absent.report().phase == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(absent.report().failure == static_cast<std::uint32_t>(Failure::CLOCK));
    absent.poll();
    CHECK(absent.report().failure == static_cast<std::uint32_t>(Failure::CLOCK));
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    CHECK_FALSE(runner.begin());
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::REENTRY));
    staysFrozen(clock, runner);
}

TEST_CASE("D091 B15 early and duplicate polls do not invent ticks") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    CHECK(runner.report().schema_version == 1U);
    CHECK(runner.report().byte_size == 256U);
    const auto initial = runner.report().ticks;
    clock.poll(runner, 0U);
    clock.poll(runner, config::TICK_US - 1U);
    CHECK(runner.report().ticks == initial);
    clock.poll(runner, 0U);
    CHECK(runner.report().ticks == initial);
    clock.poll(runner, 1U);
    CHECK(runner.report().ticks == initial + 1U);
    clock.poll(runner, 0U);
    CHECK(runner.report().ticks == initial + 1U);
    CHECK(runner.report().configure_calls >= 5U);
    CHECK(runner.report().nonzero_pwm == 0U);
    CHECK(runner.report().enabled_en == 0U);
}

TEST_CASE("D091 B15 backward and half-range chronology reject before a tick") {
    for (auto delta : {0xFFFFFFFFU, 0x80000000U, 0x80000001U}) {
        Clock clock;
        Runner runner({&clock, Clock::read});
        REQUIRE(runner.begin());
        clock.poll(runner);
        const auto ticks = runner.report().ticks;
        clock.poll(runner, delta);
        CHECK(runner.report().ticks == ticks);
        CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::CLOCK));
        CHECK(phase(runner) == static_cast<std::uint32_t>(Phase::FAILED));
        staysFrozen(clock, runner);
    }
}

TEST_CASE("D091 B15 sub-tick backwards movement is still a chronology failure") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    clock.poll(runner, 700U);
    clock.poll(runner, 0xFFFFFFFFU);
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::CLOCK));
    CHECK(runner.report().ticks == 0U);
}

TEST_CASE("D091 B15 lateness skips slots with at most one real step") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    clock.poll(runner);
    const auto ticks = runner.report().ticks;
    clock.poll(runner, 5500U);
    CHECK(runner.report().ticks == ticks + 1U);
    CHECK(runner.report().missed_slots == 4U);
    CHECK(runner.report().max_lateness_us == 4500U);
    clock.poll(runner, 0U);
    CHECK(runner.report().ticks == ticks + 1U);
}

TEST_CASE("D091 B15 unqualified START samples fail with explicit release-phase timeout") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    clock.poll(runner);
    const auto stage = config::BTN_DEBOUNCE_MS * 1000U + 4U * config::TICK_US;
    // Enter START, then release without a second stable START observation. Stage
    // durations are anchored to actual first samples, never synthesized catch-up.
    clock.poll(runner, stage);
    clock.poll(runner, stage);
    clock.poll(runner, config::BTN_LONG_MS * 1000U + config::TICK_US);
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::START_TIMEOUT));
    CHECK(phase(runner) == static_cast<std::uint32_t>(Phase::FAILED));
    CHECK(runner.source().phase() == recorder::AttemptPhase::EMPTY);
    staysFrozen(clock, runner);
}

TEST_CASE("D091 B15 real pipeline retains exact 200-second host fixture then bounded CRC") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    acceptedStart(clock, runner);
    const auto release = runner.source().summary().release_us;
    const auto phase_duration = config::BTN_DEBOUNCE_MS * 1000U + 4U * config::TICK_US;
    CHECK(release >= 2U * phase_duration);
    CHECK(release <= 2U * phase_duration + config::BTN_LONG_MS * 1000U);
    while (clock.now - release < config::LOG_FRAME_WINDOW_MS * 1000U - config::TICK_US) {
        clock.poll(runner);
        REQUIRE_FALSE(terminal(runner));
    }
    CHECK(runner.report().stop_us == 0U);
    CHECK(runner.source().phase() == recorder::AttemptPhase::RECORDING);
    clock.poll(runner);
    CHECK(runner.report().stop_us - release == 200000000U);
    CHECK(runner.source().phase() == recorder::AttemptPhase::DRAINING);
    CHECK(runner.report().checksum_rows == 0U);
    clock.poll(runner);
    CHECK(runner.source().phase() == recorder::AttemptPhase::SEALED);
    CHECK(runner.source().summary().final_frame_missing == false);
    CHECK(runner.report().checksum_rows == 0U);
    const auto checksum_entry = runner.report();
    clock.poll(runner, 0U);
    CHECK(std::memcmp(&checksum_entry, &runner.report(), sizeof(checksum_entry)) == 0);
    const auto tick_count = runner.report().ticks;
    finish(clock, runner);
    CHECK(runner.report().ticks == tick_count);
    CHECK(runner.report().frame_count == 5001U);
    CHECK(runner.report().checksum_rows == runner.report().frame_count + runner.report().event_count);
    CHECK(runner.report().crc32 == sourceCrc(runner.source()));
    CHECK(runner.report().go_seen == 1U);
    CHECK(runner.report().nonzero_pwm == 0U);
    CHECK(runner.report().enabled_en == 0U);
    CHECK(runner.report().robot_faults == 0U);
    CHECK(runner.report().gate_fault == static_cast<std::uint32_t>(motors::Fault::STOPPED));
    CHECK(runner.report().missed_slots == 0U);
    CHECK(runner.report().skipped_frames == 0U);
    CHECK(runner.report().frame_overwritten == 0U);
    CHECK(runner.report().incomplete == 0U);
    for (std::size_t index = 0; index < runner.source().frames().size(); ++index) {
        recorder::StoredFrame storage;
        const auto* frame = runner.source().frames().read(index, storage) ? &storage : nullptr;
        REQUIRE(frame != nullptr);
        CHECK(frame->status == logframe::PackStatus::OK);
        CHECK(frame->bytes.data[18] == 0U);
        CHECK(frame->bytes.data[19] == 0U);
        CHECK(frame->bytes.data[6] == 0U);
    }
    bool saw_start = false, saw_go = false;
    for (std::size_t index = 0; index < runner.source().events().size(); ++index) {
        const auto* event = runner.source().events().at(index);
        if (event->data[4] == static_cast<std::uint8_t>(core::Event::START_RELEASE)) {
            CHECK(little32(event->data) == release); saw_start = true;
        }
        if (event->data[4] == static_cast<std::uint8_t>(core::Event::GO)) {
            CHECK(little32(event->data) - release >=
                  (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U);
            saw_go = true;
        }
    }
    CHECK(saw_start); CHECK(saw_go);
    summaryMatches(runner);
    staysFrozen(clock, runner);
}

TEST_CASE("D091 B15 natural micros wrap preserves accepted duration and all summary fields") {
    Clock clock;
    clock.now = 0xFFFF0000U;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    acceptedStart(clock, runner);
    finish(clock, runner);
    CHECK(runner.report().boot_us == 0xFFFF0000U);
    CHECK(runner.report().stop_us - runner.report().release_us == 200000000U);
    CHECK(runner.report().frame_count == 5001U);
    CHECK(runner.report().crc32 == sourceCrc(runner.source()));
    CHECK(runner.report().incomplete == 0U);
    summaryMatches(runner);
}

TEST_CASE("D091 B15 scheduler gaps are retained as incomplete evidence without catch-up") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    acceptedStart(clock, runner);
    for (unsigned count = 0; count < 10000U; ++count) clock.poll(runner);
    const auto before = runner.report();
    clock.poll(runner, 501000U);
    CHECK(runner.report().ticks == before.ticks + 1U);
    CHECK(runner.report().missed_slots == 500U);
    CHECK(runner.report().max_lateness_us == 500000U);
    finish(clock, runner);
    CHECK(runner.report().skipped_frames > 0U);
    CHECK(runner.report().incomplete == 1U);
    CHECK(runner.report().frame_count < 5001U);
    CHECK(runner.report().crc32 == sourceCrc(runner.source()));
    summaryMatches(runner);
}

TEST_CASE("D091 B15 deferred sealing beyond BTN_LONG fails instead of claiming a completed attempt") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    acceptedStart(clock, runner);
    clock.poll(runner, config::LOG_FRAME_WINDOW_MS * 1000U);
    REQUIRE(runner.source().phase() == recorder::AttemptPhase::DRAINING);
    clock.poll(runner, config::BTN_LONG_MS * 1000U + config::TICK_US);
    CHECK(runner.report().failure == static_cast<std::uint32_t>(Failure::SEAL_TIMEOUT));
    CHECK(phase(runner) == static_cast<std::uint32_t>(Phase::FAILED));
    staysFrozen(clock, runner);
}

TEST_CASE("D091 B15 actual clock-port execution durations reach recorder timing") {
    Clock clock;
    Runner runner({&clock, Clock::read});
    REQUIRE(runner.begin());
    clock.cost = 37U;
    acceptedStart(clock, runner);
    finish(clock, runner);
    CHECK(runner.report().max_step_us == 37U);
    CHECK(runner.report().timing_max_us == 37U);
    CHECK(runner.report().timing_ticks_lo > 0U);
    CHECK(runner.report().timing_overruns_lo == 0U);
    CHECK(runner.report().timing_incomplete == 0U);
    summaryMatches(runner);
}

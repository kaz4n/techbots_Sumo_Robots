// Checks offline B15 CSV against D-073 and the frozen public wire layouts.
// Keeps literal evidence, loss metadata and caller buffer ownership independently tested.
// Host tests use exact strings, guarded buffers and fixed-seed scalar round trips.
#include "doctest.h"
#include "hal/recorder_csv.h"
#include <algorithm>
#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <initializer_list>
#include <limits>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {
namespace csv = recorder::csv;
using csv::FormatStatus;
using csv::SummarySnapshot;
using logframe::PackStatus;
constexpr std::uint64_t U64_MAX = std::numeric_limits<std::uint64_t>::max();
constexpr std::uint32_t U32_MAX = std::numeric_limits<std::uint32_t>::max();
constexpr const char* FRAME_HEADER =
    "schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,heading_cdeg,"
    "gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex\n";
constexpr const char* EVENT_HEADER =
    "schema_version,ordinal,t_us,type,detail,value,raw_hex\n";
constexpr const char* SUMMARY_HEADER =
    "schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,"
    "missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,"
    "upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,"
    "overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,"
    "recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,"
    "frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,"
    "event_overflow,event_rejected,incomplete\n";
constexpr const char* FRAME_ROW =
    "1,7,1,305419896,6,3,9,69,-45025,-125,1250,-500,64,-64,1250,15,4660,"
    "78563412060309451f50ffff83ffe2040cfe40c0e2040f3412\n";
constexpr const char* EVENT_ROW = "1,9,305419896,255,171,61389,78563412ffabcdef\n";
constexpr const char* SUMMARY_ROW =
    "1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,1,0,1,0,1,0,1,0,"
    "27,28,29,30,31,32,1,34,0\n";

recorder::StoredFrame literalFrame() {
    return {{{0x78, 0x56, 0x34, 0x12, 6, 3, 9, 0x45, 0x1f, 0x50, 0xff, 0xff,
              0x83, 0xff, 0xe2, 4, 0x0c, 0xfe, 0x40, 0xc0, 0xe2, 4, 15, 0x34, 0x12}},
            PackStatus::CLAMPED};
}

logframe::EventBytes literalEvent() {
    return {{0x78, 0x56, 0x34, 0x12, 0xff, 0xab, 0xcd, 0xef}};
}

SummarySnapshot distinctSummary() {
    SummarySnapshot value;
    auto& a = value.attempt;
    a.epoch_token = 1U; a.last_frame_token = 2U; a.release_us = 3U;
    a.mode = static_cast<core::Mode>(4U); value.phase = static_cast<recorder::AttemptPhase>(5U);
    a.observed_results = 6U; a.missing_results = 7U; a.rejected_results = 8U;
    a.identity_rejected = 9U; a.malformed_batches = 10U; a.event_semantic_rejected = 11U;
    a.upstream_event_rejected = 12U; a.upstream_event_invalid = 13U;
    a.source_regressions = 14U; a.skipped_frames = 15U; a.ticks = {16U, 17U, 18U, true};
    a.upstream_event_overflow = false; a.timing_incomplete = true;
    a.recording_incomplete = false; a.go_seen = true; a.final_frame_missing = false;
    a.interrupted = true; a.terminal_exhausted = false;
    value.frame_count = 27U; value.frame_overwritten = 28U; value.frame_rejected_status = 29U;
    value.frame_clamped = 30U; value.frame_invalid = 31U; value.event_count = 32U;
    value.event_overflow = true; value.event_rejected = 34U; value.incomplete = false;
    return value;
}

std::array<std::uint64_t, 36> summaryValues(const SummarySnapshot& s) {
    const auto& a = s.attempt;
    return {{1U, a.epoch_token, a.last_frame_token, a.release_us,
        static_cast<std::uint8_t>(a.mode), static_cast<std::uint8_t>(s.phase),
        a.observed_results, a.missing_results, a.rejected_results, a.identity_rejected,
        a.malformed_batches, a.event_semantic_rejected, a.upstream_event_rejected,
        a.upstream_event_invalid, a.source_regressions, a.skipped_frames,
        a.ticks.ticks, a.ticks.overruns, a.ticks.max_us, a.ticks.saturated,
        a.upstream_event_overflow, a.timing_incomplete, a.recording_incomplete,
        a.go_seen, a.final_frame_missing, a.interrupted, a.terminal_exhausted,
        s.frame_count, s.frame_overwritten, s.frame_rejected_status, s.frame_clamped,
        s.frame_invalid, s.event_count, s.event_overflow, s.event_rejected, s.incomplete}};
}

void checkLine(const char* buffer, const csv::FormatResult& result, const char* expected) {
    CHECK(result.status == FormatStatus::OK);
    const auto length = std::strlen(expected);
    CHECK(result.size == length);
    CHECK(length + 1U <= csv::MAX_LINE_BYTES);
    CHECK(std::memcmp(buffer, expected, length + 1U) == 0);
    CHECK(buffer[length - 1U] == '\n');
    CHECK(buffer[length] == '\0');
}

std::vector<std::string_view> columns(const char* buffer, const csv::FormatResult& result) {
    CHECK(result.status == FormatStatus::OK);
    CHECK(result.size > 0U);
    if (result.status != FormatStatus::OK || result.size == 0U) return {};
    CHECK(buffer[result.size - 1U] == '\n');
    CHECK(buffer[result.size] == '\0');
    const std::string_view row(buffer, result.size - 1U);
    std::vector<std::string_view> values;
    std::size_t begin = 0U;
    for (std::size_t i = 0U; i <= row.size(); ++i) {
        if (i == row.size() || row[i] == ',') {
            values.push_back(row.substr(begin, i - begin));
            begin = i + 1U;
        }
    }
    return values;
}

std::uint64_t unsignedNumber(std::string_view text) {
    std::uint64_t value = 0U;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    CHECK(parsed.ec == std::errc{});
    CHECK(parsed.ptr == text.data() + text.size());
    CHECK_FALSE(text.empty());
    CHECK((text.size() == 1U || text[0] != '0'));
    return value;
}

std::int64_t signedNumber(std::string_view text) {
    std::int64_t value = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    CHECK(parsed.ec == std::errc{});
    CHECK(parsed.ptr == text.data() + text.size());
    CHECK_FALSE(text.empty());
    CHECK(text != "-0");
    CHECK((text.size() == 1U || text[0] != '0'));
    return value;
}

std::uint64_t boundedUnsigned(std::string_view text, std::uint64_t maximum) {
    const auto value = unsignedNumber(text);
    CHECK(value <= maximum);
    return value;
}

std::int64_t boundedSigned(std::string_view text, std::int64_t minimum, std::int64_t maximum) {
    const auto value = signedNumber(text);
    CHECK(value >= minimum);
    CHECK(value <= maximum);
    return value;
}

void checkRaw(std::string_view text, const std::uint8_t* bytes, std::size_t count) {
    CHECK(text.size() == count * 2U);
    if (text.size() != count * 2U) return;
    for (char c : text) CHECK(((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')));
    for (std::size_t i = 0U; i < count; ++i) {
        unsigned value = 0U;
        const auto parsed = std::from_chars(text.data() + 2U * i,
            text.data() + 2U * i + 2U, value, 16);
        CHECK(parsed.ec == std::errc{});
        CHECK(parsed.ptr == text.data() + 2U * i + 2U);
        CHECK(value == bytes[i]);
    }
}

enum class Line { FRAME_HEADER, FRAME, EVENT_HEADER, EVENT, SUMMARY_HEADER, SUMMARY };
constexpr std::array<Line, 6> LINES{{Line::FRAME_HEADER, Line::FRAME, Line::EVENT_HEADER,
                                  Line::EVENT, Line::SUMMARY_HEADER, Line::SUMMARY}};
csv::FormatResult format(Line line, char* buffer, std::size_t capacity) {
    switch (line) {
    case Line::FRAME_HEADER: return csv::frameHeader(buffer, capacity);
    case Line::FRAME: return csv::frameRow(literalFrame(), 7U, buffer, capacity);
    case Line::EVENT_HEADER: return csv::eventHeader(buffer, capacity);
    case Line::EVENT: return csv::eventRow(literalEvent(), 9U, buffer, capacity);
    case Line::SUMMARY_HEADER: return csv::summaryHeader(buffer, capacity);
    case Line::SUMMARY: return csv::summaryRow(distinctSummary(), buffer, capacity);
    }
    return {};
}

const char* expectedLine(Line line) {
    switch (line) {
    case Line::FRAME_HEADER: return FRAME_HEADER;
    case Line::FRAME: return FRAME_ROW;
    case Line::EVENT_HEADER: return EVENT_HEADER;
    case Line::EVENT: return EVENT_ROW;
    case Line::SUMMARY_HEADER: return SUMMARY_HEADER;
    case Line::SUMMARY: return SUMMARY_ROW;
    }
    return "";
}

void putLittleEndian(std::uint8_t* destination, std::uint64_t value, unsigned count) {
    for (unsigned i = 0U; i < count; ++i) destination[i] = static_cast<std::uint8_t>(value >> (8U * i));
}

std::uint32_t nextRandom(std::uint32_t& state) {
    state = 1664525U * state + 1013904223U;
    return state;
}

void checkFrameRoundTrip(const recorder::StoredFrame& frame, std::uint64_t ordinal) {
    char buffer[csv::MAX_LINE_BYTES] = {};
    const auto fields = columns(buffer, csv::frameRow(frame, ordinal, buffer, sizeof(buffer)));
    CHECK(fields.size() == 18U);
    if (fields.size() != 18U) return;
    CHECK(unsignedNumber(fields[0]) == 1U);
    CHECK(unsignedNumber(fields[1]) == ordinal);
    CHECK(unsignedNumber(fields[2]) == static_cast<unsigned>(frame.status));
    std::array<std::uint8_t, 25> decoded{};
    putLittleEndian(decoded.data(), boundedUnsigned(fields[3], U32_MAX), 4U);
    for (unsigned i = 4U; i <= 7U; ++i)
        decoded[i] = static_cast<std::uint8_t>(boundedUnsigned(fields[i], 255U));
    putLittleEndian(decoded.data() + 8U,
        static_cast<std::uint64_t>(boundedSigned(fields[8], -2147483648LL, 2147483647LL)), 4U);
    for (unsigned i = 9U; i <= 11U; ++i)
        putLittleEndian(decoded.data() + 12U + (i - 9U) * 2U,
                        static_cast<std::uint64_t>(boundedSigned(fields[i], -32768, 32767)), 2U);
    decoded[18] = static_cast<std::uint8_t>(boundedSigned(fields[12], -128, 127));
    decoded[19] = static_cast<std::uint8_t>(boundedSigned(fields[13], -128, 127));
    putLittleEndian(decoded.data() + 20U, boundedUnsigned(fields[14], 65535U), 2U);
    decoded[22] = static_cast<std::uint8_t>(boundedUnsigned(fields[15], 255U));
    putLittleEndian(decoded.data() + 23U, boundedUnsigned(fields[16], 65535U), 2U);
    CHECK(std::memcmp(decoded.data(), frame.bytes.data, 25U) == 0);
    checkRaw(fields[17], frame.bytes.data, 25U);
}

void checkEventRoundTrip(const logframe::EventBytes& event, std::uint64_t ordinal) {
    char buffer[csv::MAX_LINE_BYTES] = {};
    const auto fields = columns(buffer, csv::eventRow(event, ordinal, buffer, sizeof(buffer)));
    CHECK(fields.size() == 7U);
    if (fields.size() != 7U) return;
    CHECK(unsignedNumber(fields[0]) == 1U);
    CHECK(unsignedNumber(fields[1]) == ordinal);
    std::array<std::uint8_t, 8> decoded{};
    putLittleEndian(decoded.data(), boundedUnsigned(fields[2], U32_MAX), 4U);
    decoded[4] = static_cast<std::uint8_t>(boundedUnsigned(fields[3], 255U));
    decoded[5] = static_cast<std::uint8_t>(boundedUnsigned(fields[4], 255U));
    putLittleEndian(decoded.data() + 6U, boundedUnsigned(fields[5], 65535U), 2U);
    CHECK(std::memcmp(decoded.data(), event.data, 8U) == 0);
    checkRaw(fields[6], event.data, 8U);
}

fsm::RobotResult ownerResult(std::uint64_t token, core::State state = core::State::COUNTDOWN) {
    fsm::RobotResult result;
    result.token = token; result.fresh = true; result.outputs.ui_state = state;
    result.running_mode = core::Mode::DIRECT;
    return result;
}

void startOwner(recorder::AttemptRecorder& owner, std::uint64_t token = 10U) {
    auto start = ownerResult(token);
    start.lifecycle.gate.start_release = true;
    start.lifecycle.gate.release_us = 0xfffffff0U;
    start.events.count = 1U;
    start.events.entries[0] = {0xfffffff0U, core::Event::START_RELEASE, 3U, 0U};
    CHECK(owner.consume(start) == recorder::ConsumeStatus::ACCEPTED);
}

SummarySnapshot expectedOwner(const recorder::AttemptRecorder& owner) {
    SummarySnapshot result;
    result.attempt = owner.summary(); result.phase = owner.phase();
    result.frame_count = static_cast<std::uint32_t>(owner.frames().size());
    result.frame_overwritten = owner.frames().overwrittenCount();
    result.frame_rejected_status = owner.frames().rejectedStatusCount();
    result.frame_clamped = owner.frames().clampedCount();
    result.frame_invalid = owner.frames().invalidCount();
    result.event_count = static_cast<std::uint32_t>(owner.events().size());
    result.event_overflow = owner.events().overflowed();
    result.event_rejected = owner.events().rejectedCount(); result.incomplete = owner.incomplete();
    return result;
}

void checkCapture(const recorder::AttemptRecorder& owner) {
    const auto expected = summaryValues(expectedOwner(owner));
    const auto captured = csv::captureSummary(owner);
    CHECK(summaryValues(captured) == expected);
    CHECK(summaryValues(expectedOwner(owner)) == expected);
    char buffer[csv::MAX_LINE_BYTES] = {};
    const auto fields = columns(buffer, csv::summaryRow(captured, buffer, sizeof(buffer)));
    CHECK(fields.size() == 36U);
    if (fields.size() != 36U) return;
    for (std::size_t i = 0U; i < 36U; ++i) CHECK(unsignedNumber(fields[i]) == expected[i]);
}
} // namespace

TEST_CASE("B15 D073 literal headers fix every column and schema representation") {
    CHECK(csv::SCHEMA_VERSION == 1U);
    CHECK(csv::MAX_LINE_BYTES == 1024U);
    const std::array<std::size_t, 3> counts{{18U, 7U, 36U}};
    unsigned index = 0U;
    for (Line kind : {Line::FRAME_HEADER, Line::EVENT_HEADER, Line::SUMMARY_HEADER}) {
        char buffer[csv::MAX_LINE_BYTES] = {};
        const auto result = format(kind, buffer, sizeof(buffer));
        checkLine(buffer, result, expectedLine(kind));
        CHECK(columns(buffer, result).size() == counts[index++]);
    }
}

TEST_CASE("B15 D073 literal mixed signed frame retains exact integer units and bytes") {
    const auto frame = literalFrame();
    char buffer[csv::MAX_LINE_BYTES] = {};
    checkLine(buffer, csv::frameRow(frame, 7U, buffer, sizeof(buffer)), FRAME_ROW);
}

TEST_CASE("B15 D073 frame signed minima unknown raw codes and maximum ordinal remain evidence") {
    const recorder::StoredFrame frame{{{255, 255, 255, 255, 255, 254, 253, 252,
        0, 0, 0, 128, 0, 128, 255, 127, 255, 255, 128, 127, 255, 255, 255, 255, 255}},
        PackStatus::INVALID};
    const char* expected = "1,18446744073709551615,2,4294967295,255,254,253,252,"
        "-2147483648,-32768,32767,-1,-128,127,65535,255,65535,"
        "fffffffffffefdfc000000800080ff7fffff807fffffffffff\n";
    char buffer[csv::MAX_LINE_BYTES] = {};
    checkLine(buffer, csv::frameRow(frame, U64_MAX, buffer, sizeof(buffer)), expected);
}

TEST_CASE("B15 D073 frame signed maxima alternate minima and negative one are not clamped") {
    const recorder::StoredFrame frame{{{0, 0, 0, 0, 0, 0, 0, 0,
        255, 255, 255, 127, 255, 127, 0, 128, 0, 128, 255, 128, 0, 0, 0, 0, 0}},
        PackStatus::OK};
    const char* expected = "1,0,0,0,0,0,0,0,2147483647,32767,-32768,-32768,-1,-128,0,0,0,"
        "0000000000000000ffffff7fff7f00800080ff800000000000\n";
    char buffer[csv::MAX_LINE_BYTES] = {};
    checkLine(buffer, csv::frameRow(frame, 0U, buffer, sizeof(buffer)), expected);
}

TEST_CASE("B15 D073 all known pack statuses preserve identical arbitrary bytes") {
    for (unsigned status = 0U; status <= 2U; ++status) {
        auto frame = literalFrame(); frame.status = static_cast<PackStatus>(status);
        const auto original = frame;
        char buffer[csv::MAX_LINE_BYTES] = {};
        const std::string expected = "1,7," + std::to_string(status) +
            ",305419896,6,3,9,69,-45025,-125,1250,-500,64,-64,1250,15,4660,"
            "78563412060309451f50ffff83ffe2040cfe40c0e2040f3412\n";
        checkLine(buffer, csv::frameRow(frame, 7U, buffer, sizeof(buffer)), expected.c_str());
        CHECK(frame.status == original.status);
        CHECK(std::memcmp(frame.bytes.data, original.bytes.data, 25U) == 0);
    }
}

TEST_CASE("B15 D073 every unknown pack status rejects before capacity and clears only first byte") {
    for (unsigned status = 3U; status <= 255U; ++status) {
        auto frame = literalFrame(); frame.status = static_cast<PackStatus>(status);
        for (std::size_t capacity : {0U, 1U, 1024U}) {
            std::array<char, 1026> buffer; buffer.fill('!');
            auto expected = buffer;
            if (capacity > 0U) expected[1] = '\0';
            const auto result = csv::frameRow(frame, 0U, buffer.data() + 1U, capacity);
            CHECK(result.status == FormatStatus::INVALID_ARGUMENT);
            CHECK(result.size == 0U);
            CHECK(buffer == expected);
            const auto null = csv::frameRow(frame, 0U, nullptr, capacity);
            CHECK(null.status == FormatStatus::INVALID_ARGUMENT);
            CHECK(null.size == 0U);
        }
    }
}

TEST_CASE("B15 D073 event literal unknown type and unsigned maxima are retained") {
    char buffer[csv::MAX_LINE_BYTES] = {};
    checkLine(buffer, csv::eventRow(literalEvent(), 9U, buffer, sizeof(buffer)), EVENT_ROW);
    const logframe::EventBytes maximum{{255, 255, 255, 255, 255, 255, 255, 255}};
    checkLine(buffer, csv::eventRow(maximum, U64_MAX, buffer, sizeof(buffer)),
        "1,18446744073709551615,4294967295,255,255,65535,ffffffffffffffff\n");
    const logframe::EventBytes zero;
    checkLine(buffer, csv::eventRow(zero, 0U, buffer, sizeof(buffer)),
        "1,0,0,0,0,0,0000000000000000\n");
}

TEST_CASE("B15 D073 event wrapped and equal timestamps follow caller order and ordinal") {
    const std::array<std::uint32_t, 4> times{{U32_MAX, 0U, 0U, 1U}};
    const std::array<std::uint64_t, 4> ordinals{{19U, 7U, 0U, U64_MAX}};
    for (std::size_t i = 0U; i < times.size(); ++i) {
        auto event = literalEvent(); putLittleEndian(event.data, times[i], 4U);
        char buffer[csv::MAX_LINE_BYTES] = {};
        const auto fields = columns(buffer, csv::eventRow(event, ordinals[i], buffer, sizeof(buffer)));
        CHECK(fields.size() == 7U);
        if (fields.size() != 7U) continue;
        CHECK(unsignedNumber(fields[1]) == ordinals[i]);
        CHECK(unsignedNumber(fields[2]) == times[i]);
        checkRaw(fields[6], event.data, 8U);
    }
}

TEST_CASE("B15 D073 summary literal distinguishes all scalar columns without recomputing loss") {
    const auto snapshot = distinctSummary();
    char buffer[csv::MAX_LINE_BYTES] = {};
    checkLine(buffer, csv::summaryRow(snapshot, buffer, sizeof(buffer)), SUMMARY_ROW);
}

TEST_CASE("B15 D073 summary preserves uint64 uint32 enum extrema and all true flags") {
    auto s = distinctSummary();
    auto& a = s.attempt;
    a.epoch_token = U64_MAX; a.last_frame_token = U64_MAX; a.release_us = U32_MAX;
    a.mode = static_cast<core::Mode>(255U); s.phase = static_cast<recorder::AttemptPhase>(255U);
    a.observed_results = U32_MAX; a.missing_results = U32_MAX; a.rejected_results = U32_MAX;
    a.identity_rejected = U32_MAX; a.malformed_batches = U32_MAX; a.event_semantic_rejected = U32_MAX;
    a.upstream_event_rejected = U32_MAX; a.upstream_event_invalid = U32_MAX;
    a.source_regressions = U32_MAX; a.skipped_frames = U32_MAX;
    a.ticks = {U64_MAX, U64_MAX, U32_MAX, true};
    a.upstream_event_overflow = true; a.timing_incomplete = true; a.recording_incomplete = true;
    a.go_seen = true; a.final_frame_missing = true; a.interrupted = true; a.terminal_exhausted = true;
    s.frame_count = U32_MAX; s.frame_overwritten = U32_MAX; s.frame_rejected_status = U32_MAX;
    s.frame_clamped = U32_MAX; s.frame_invalid = U32_MAX; s.event_count = U32_MAX;
    s.event_overflow = true; s.event_rejected = U32_MAX; s.incomplete = true;
    const char* expected = "1,18446744073709551615,18446744073709551615,4294967295,255,255,"
        "4294967295,4294967295,4294967295,4294967295,4294967295,4294967295,4294967295,"
        "4294967295,4294967295,4294967295,18446744073709551615,18446744073709551615,4294967295,"
        "1,1,1,1,1,1,1,1,4294967295,4294967295,4294967295,4294967295,4294967295,4294967295,"
        "1,4294967295,1\n";
    char buffer[csv::MAX_LINE_BYTES] = {};
    checkLine(buffer, csv::summaryRow(s, buffer, sizeof(buffer)), expected);
}

TEST_CASE("B15 D073 each summary boolean occupies its own column and preserves inconsistent input") {
    const std::array<std::size_t, 10> positions{{19U, 20U, 21U, 22U, 23U, 24U, 25U, 26U, 33U, 35U}};
    for (std::size_t flag = 0U; flag < positions.size(); ++flag) {
        SummarySnapshot s; s.attempt.mode = static_cast<core::Mode>(0U);
        auto& a = s.attempt;
        const std::array<bool*, 10> flags{{&a.ticks.saturated, &a.upstream_event_overflow,
            &a.timing_incomplete, &a.recording_incomplete, &a.go_seen, &a.final_frame_missing,
            &a.interrupted, &a.terminal_exhausted, &s.event_overflow, &s.incomplete}};
        *flags[flag] = true;
        char buffer[csv::MAX_LINE_BYTES] = {};
        const auto fields = columns(buffer, csv::summaryRow(s, buffer, sizeof(buffer)));
        CHECK(fields.size() == 36U);
        if (fields.size() != 36U) continue;
        for (std::size_t column = 0U; column < fields.size(); ++column)
            CHECK(unsignedNumber(fields[column]) == (column == 0U || column == positions[flag] ? 1U : 0U));
    }
}

TEST_CASE("B15 D073 every formatter succeeds at exact capacity and leaves outside guards intact") {
    for (Line line : LINES) {
        const auto* expected = expectedLine(line);
        const auto capacity = std::strlen(expected) + 1U;
        std::array<char, csv::MAX_LINE_BYTES + 8U> buffer; buffer.fill('^');
        const auto result = format(line, buffer.data() + 4U, capacity);
        checkLine(buffer.data() + 4U, result, expected);
        CHECK(std::all_of(buffer.begin(), buffer.begin() + 4U, [](char c) { return c == '^'; }));
        CHECK(std::all_of(buffer.begin() + 4U + capacity, buffer.end(), [](char c) { return c == '^'; }));
    }
}

TEST_CASE("B15 D073 every insufficient capacity produces no prefix and only writes first NUL") {
    for (Line line : LINES) {
        const auto needed = std::strlen(expectedLine(line)) + 1U;
        for (std::size_t capacity = 0U; capacity < needed; ++capacity) {
            CAPTURE(static_cast<unsigned>(line)); CAPTURE(capacity);
            std::array<char, csv::MAX_LINE_BYTES + 8U> buffer; buffer.fill('~');
            auto expected = buffer;
            if (capacity > 0U) expected[4] = '\0';
            const auto result = format(line, buffer.data() + 4U, capacity);
            CHECK(result.status == FormatStatus::INSUFFICIENT_CAPACITY);
            CHECK(result.size == 0U);
            CHECK(buffer == expected);
        }
    }
}

TEST_CASE("B15 D073 null is invalid even at zero or maximum capacity for every formatter") {
    for (Line line : LINES) {
        for (std::size_t capacity : {std::size_t{0U}, std::size_t{1U}, csv::MAX_LINE_BYTES,
                                     std::numeric_limits<std::size_t>::max()}) {
            const auto result = format(line, nullptr, capacity);
            CHECK(result.status == FormatStatus::INVALID_ARGUMENT);
            CHECK(result.size == 0U);
        }
    }
}

TEST_CASE("B15 D073 repeated formatting is deterministic and does not mutate any source") {
    const auto frame = literalFrame(); const auto event = literalEvent();
    const auto summary = distinctSummary(); const auto original = summaryValues(summary);
    for (unsigned iteration = 0U; iteration < 1000U; ++iteration) {
        char buffer[csv::MAX_LINE_BYTES] = {};
        checkLine(buffer, csv::frameRow(frame, 7U, buffer, sizeof(buffer)), FRAME_ROW);
        checkLine(buffer, csv::eventRow(event, 9U, buffer, sizeof(buffer)), EVENT_ROW);
        checkLine(buffer, csv::summaryRow(summary, buffer, sizeof(buffer)), SUMMARY_ROW);
        const auto expected_frame = literalFrame(); const auto expected_event = literalEvent();
        CHECK(frame.status == expected_frame.status);
        CHECK(std::memcmp(frame.bytes.data, expected_frame.bytes.data, 25U) == 0);
        CHECK(std::memcmp(event.data, expected_event.data, 8U) == 0);
        CHECK(summaryValues(summary) == original);
    }
}

TEST_CASE("B15 D073 capture retains distinguishable empty recording draining sealed interrupted phases") {
    recorder::AttemptRecorder owner;
    checkCapture(owner);
    CHECK(csv::captureSummary(owner).phase == recorder::AttemptPhase::EMPTY);
    startOwner(owner); checkCapture(owner);
    const auto recording = csv::captureSummary(owner);
    CHECK(recording.phase == recorder::AttemptPhase::RECORDING);
    CHECK(recording.attempt.epoch_token == 10U);
    CHECK(recording.attempt.release_us == 0xfffffff0U);
    CHECK(recording.attempt.observed_results == 1U);
    CHECK(recording.event_count == 1U); CHECK_FALSE(recording.incomplete);
    auto stopped = ownerResult(11U, core::State::STOPPED);
    CHECK(owner.consume(stopped) == recorder::ConsumeStatus::ACCEPTED);
    checkCapture(owner); CHECK(csv::captureSummary(owner).phase == recorder::AttemptPhase::DRAINING);
    auto tail = ownerResult(12U, core::State::STOPPED);
    tail.frame_ready = true; tail.frame_token = 11U; tail.frame = literalFrame().bytes;
    tail.frame_status = PackStatus::CLAMPED;
    CHECK(owner.consume(tail) == recorder::ConsumeStatus::ACCEPTED);
    checkCapture(owner);
    const auto sealed = csv::captureSummary(owner);
    CHECK(sealed.phase == recorder::AttemptPhase::SEALED);
    CHECK(sealed.frame_count == 1U); CHECK(sealed.frame_clamped == 1U);
    CHECK(sealed.attempt.last_frame_token == 11U); CHECK(sealed.incomplete);
    const auto* stored = owner.frames().at(0U);
    CHECK(stored != nullptr);
    if (stored) CHECK(std::memcmp(stored->bytes.data, tail.frame.data, 25U) == 0);
    startOwner(owner, 20U); owner.onRobotReset(); checkCapture(owner);
    const auto interrupted = csv::captureSummary(owner);
    CHECK(interrupted.phase == recorder::AttemptPhase::INTERRUPTED);
    CHECK(interrupted.attempt.interrupted); CHECK(interrupted.incomplete);
    CHECK(interrupted.event_count == 1U); CHECK(interrupted.frame_count == 0U);
}

TEST_CASE("B15 D073 capture copies real frame and event loss counters without clearing payloads") {
    recorder::AttemptRecorder owner; startOwner(owner, 1U);
    for (std::uint64_t token = 2U; token <= 5004U; ++token) {
        auto result = ownerResult(token);
        result.frame_ready = true; result.frame_token = token - 1U;
        result.frame = literalFrame().bytes;
        result.frame_status = static_cast<PackStatus>(token % 3U);
        result.events.count = 1U; result.events.entries[0] = {0U, core::Event::GO, 3U, 0U};
        CHECK(owner.consume(result) == recorder::ConsumeStatus::ACCEPTED);
    }
    const auto summary = csv::captureSummary(owner);
    CHECK(summary.frame_count == 5001U); CHECK(summary.frame_overwritten == 2U);
    CHECK(summary.frame_clamped == 1667U); CHECK(summary.frame_invalid == 1668U);
    CHECK(summary.event_count == 4096U); CHECK(summary.event_overflow);
    CHECK(summary.event_rejected == 908U); CHECK(summary.incomplete);
    const auto* first_frame = owner.frames().at(0U); const auto* first_event = owner.events().at(0U);
    CHECK(first_frame != nullptr); CHECK(first_event != nullptr);
    if (!first_frame || !first_event) return;
    const auto saved_frame = *first_frame; const auto saved_event = *first_event;
    for (unsigned iteration = 0U; iteration < 100U; ++iteration) checkCapture(owner);
    CHECK(std::memcmp(first_frame->bytes.data, saved_frame.bytes.data, 25U) == 0);
    CHECK(first_frame->status == saved_frame.status);
    CHECK(std::memcmp(first_event->data, saved_event.data, 8U) == 0);
}

TEST_CASE("B15 D073 fixed seed arbitrary frame and event bytes round trip through scalar CSV parsing") {
    std::uint32_t seed = 0xD073B15U;
    for (unsigned trial = 0U; trial < 4096U; ++trial) {
        CAPTURE(trial);
        recorder::StoredFrame frame; logframe::EventBytes event;
        for (auto& byte : frame.bytes.data) byte = static_cast<std::uint8_t>(nextRandom(seed) >> 24U);
        for (auto& byte : event.data) byte = static_cast<std::uint8_t>(nextRandom(seed) >> 24U);
        frame.status = static_cast<PackStatus>(trial % 3U);
        const auto ordinal = (static_cast<std::uint64_t>(nextRandom(seed)) << 32U) | nextRandom(seed);
        const auto before_frame = frame; const auto before_event = event;
        checkFrameRoundTrip(frame, ordinal); checkEventRoundTrip(event, ordinal);
        CHECK(frame.status == before_frame.status);
        CHECK(std::memcmp(frame.bytes.data, before_frame.bytes.data, 25U) == 0);
        CHECK(std::memcmp(event.data, before_event.data, 8U) == 0);
    }
}

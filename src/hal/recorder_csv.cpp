// Formats B15 retained bytes and attempt metadata as bounded offline CSV lines.
// Preserves raw evidence without changing the recorder or authorizing a dump.
// Independent D-073 host tests cover exact schemas, raw values and buffer limits.
#include "recorder_csv.h"

namespace recorder::csv {
namespace {
constexpr char FRAME_HEADER[] =
    "schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,"
    "heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,"
    "flags,tick_max_us,raw_hex\n";
constexpr char EVENT_HEADER[] =
    "schema_version,ordinal,t_us,type,detail,value,raw_hex\n";
constexpr char SUMMARY_HEADER[] =
    "schema_version,epoch_token,last_frame_token,release_us,mode,phase,"
    "observed_results,missing_results,rejected_results,identity_rejected,"
    "malformed_batches,event_semantic_rejected,upstream_event_rejected,"
    "upstream_event_invalid,source_regressions,skipped_frames,ticks,overruns,"
    "tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,"
    "recording_incomplete,go_seen,final_frame_missing,interrupted,"
    "terminal_exhausted,frame_count,frame_overwritten,frame_rejected_status,"
    "frame_clamped,frame_invalid,event_count,event_overflow,event_rejected,"
    "incomplete\n";
static_assert(sizeof(FRAME_HEADER) <= MAX_LINE_BYTES);
static_assert(sizeof(EVENT_HEADER) <= MAX_LINE_BYTES);
static_assert(sizeof(SUMMARY_HEADER) <= MAX_LINE_BYTES);
static_assert(config::LOG_FRAME_CAPACITY <= UINT32_MAX);
static_assert(config::LOG_EVENT_CAPACITY <= UINT32_MAX);

FormatResult failure(FormatStatus status, char* destination, std::size_t capacity) {
    if (destination != nullptr && capacity > 0U) destination[0] = '\0';
    return {status, 0U};
}

FormatResult publish(const char* bytes, std::size_t size,
                     char* destination, std::size_t capacity) {
    if (destination == nullptr)
        return failure(FormatStatus::INVALID_ARGUMENT, destination, capacity);
    if (size >= MAX_LINE_BYTES || capacity <= size)
        return failure(FormatStatus::INSUFFICIENT_CAPACITY, destination, capacity);
    // Capacity is known before copying; failure never exposes a partial line.
    for (std::size_t i = 0U; i < size; ++i) destination[i] = bytes[i];
    destination[size] = '\0';
    return {FormatStatus::OK, size};
}

class Line {
public:
    void number(std::uint64_t value) {
        separator();
        digits(value);
    }

    void signedNumber(std::int64_t value) {
        separator();
        if (value < 0) {
            put('-');
            // Negating value+1 also handles the minimum signed integer.
            digits(static_cast<std::uint64_t>(-(value + 1)) + 1U);
        } else {
            digits(static_cast<std::uint64_t>(value));
        }
    }

    void rawHex(const std::uint8_t* bytes, std::size_t count) {
        constexpr char HEX[] = "0123456789abcdef";
        separator();
        for (std::size_t i = 0U; i < count && i < logframe::FRAME_BYTES; ++i) {
            put(HEX[bytes[i] >> 4U]);
            put(HEX[bytes[i] & 0x0FU]);
        }
    }

    FormatResult finish(char* destination, std::size_t capacity) {
        put('\n');
        if (!complete_ && destination != nullptr)
            return failure(FormatStatus::INSUFFICIENT_CAPACITY, destination, capacity);
        return publish(bytes_, size_, destination, capacity);
    }

private:
    void put(char value) {
        if (size_ < MAX_LINE_BYTES - 1U) bytes_[size_++] = value;
        else complete_ = false;
    }

    void separator() {
        if (size_ != 0U) put(',');
    }

    void digits(std::uint64_t value) {
        char reversed[20];
        std::size_t count = 0U;
        for (std::size_t i = 0U; i < sizeof(reversed); ++i) {
            reversed[count++] = static_cast<char>('0' + value % 10U);
            value /= 10U;
            if (value == 0U) break;
        }
        for (std::size_t i = 0U; i < count; ++i) put(reversed[count - i - 1U]);
    }

    char bytes_[MAX_LINE_BYTES];
    std::size_t size_ = 0U;
    bool complete_ = true;
};

std::uint16_t read16(const std::uint8_t* bytes) {
    return static_cast<std::uint16_t>(static_cast<std::uint16_t>(bytes[0]) |
                                    (static_cast<std::uint16_t>(bytes[1]) << 8U));
}

std::uint32_t read32(const std::uint8_t* bytes) {
    return static_cast<std::uint32_t>(bytes[0]) |
           (static_cast<std::uint32_t>(bytes[1]) << 8U) |
           (static_cast<std::uint32_t>(bytes[2]) << 16U) |
           (static_cast<std::uint32_t>(bytes[3]) << 24U);
}

std::int64_t signedWire(std::uint32_t value, unsigned bits) {
    // Subtraction in int64 avoids implementation-defined unsigned-to-signed casts.
    const std::int64_t modulus = std::int64_t{1} << bits;
    const std::int64_t decoded = value;
    return decoded < modulus / 2 ? decoded : decoded - modulus;
}

bool knownStatus(logframe::PackStatus status) {
    return status == logframe::PackStatus::OK ||
           status == logframe::PackStatus::CLAMPED ||
           status == logframe::PackStatus::INVALID;
}
} // namespace

SummarySnapshot captureSummary(const AttemptRecorder& source) {
    SummarySnapshot snapshot;
    snapshot.attempt = source.summary();
    snapshot.phase = source.phase();
    snapshot.frame_count = static_cast<std::uint32_t>(source.frames().size());
    snapshot.frame_overwritten = source.frames().overwrittenCount();
    snapshot.frame_rejected_status = source.frames().rejectedStatusCount();
    snapshot.frame_clamped = source.frames().clampedCount();
    snapshot.frame_invalid = source.frames().invalidCount();
    snapshot.event_count = static_cast<std::uint32_t>(source.events().size());
    snapshot.event_overflow = source.events().overflowed();
    snapshot.event_rejected = source.events().rejectedCount();
    snapshot.incomplete = source.incomplete();
    return snapshot;
}

FormatResult frameHeader(char* destination, std::size_t capacity) {
    return publish(FRAME_HEADER, sizeof(FRAME_HEADER) - 1U, destination, capacity);
}

FormatResult frameRow(const StoredFrame& frame, std::uint64_t ordinal,
                      char* destination, std::size_t capacity) {
    if (!knownStatus(frame.status))
        return failure(FormatStatus::INVALID_ARGUMENT, destination, capacity);
    Line line;
    const std::uint8_t* bytes = frame.bytes.data;
    line.number(SCHEMA_VERSION);
    line.number(ordinal);
    line.number(static_cast<std::uint8_t>(frame.status));
    line.number(read32(bytes));
    line.number(bytes[4]);
    line.number(bytes[5]);
    line.number(bytes[6]);
    line.number(bytes[7]);
    line.signedNumber(signedWire(read32(bytes + 8U), 32U));
    line.signedNumber(signedWire(read16(bytes + 12U), 16U));
    line.signedNumber(signedWire(read16(bytes + 14U), 16U));
    line.signedNumber(signedWire(read16(bytes + 16U), 16U));
    line.signedNumber(signedWire(bytes[18], 8U));
    line.signedNumber(signedWire(bytes[19], 8U));
    line.number(read16(bytes + 20U));
    line.number(bytes[22]);
    line.number(read16(bytes + 23U));
    line.rawHex(bytes, logframe::FRAME_BYTES);
    return line.finish(destination, capacity);
}

FormatResult eventHeader(char* destination, std::size_t capacity) {
    return publish(EVENT_HEADER, sizeof(EVENT_HEADER) - 1U, destination, capacity);
}

FormatResult eventRow(const logframe::EventBytes& event, std::uint64_t ordinal,
                      char* destination, std::size_t capacity) {
    Line line;
    line.number(SCHEMA_VERSION);
    line.number(ordinal);
    line.number(read32(event.data));
    line.number(event.data[4]);
    line.number(event.data[5]);
    line.number(read16(event.data + 6U));
    line.rawHex(event.data, logframe::EVENT_BYTES);
    return line.finish(destination, capacity);
}

FormatResult summaryHeader(char* destination, std::size_t capacity) {
    return publish(SUMMARY_HEADER, sizeof(SUMMARY_HEADER) - 1U, destination, capacity);
}

FormatResult summaryRow(const SummarySnapshot& summary,
                        char* destination, std::size_t capacity) {
    Line line;
    const AttemptSummary& attempt = summary.attempt;
    line.number(SCHEMA_VERSION);
    line.number(attempt.epoch_token);
    line.number(attempt.last_frame_token);
    line.number(attempt.release_us);
    line.number(static_cast<std::uint8_t>(attempt.mode));
    line.number(static_cast<std::uint8_t>(summary.phase));
    line.number(attempt.observed_results);
    line.number(attempt.missing_results);
    line.number(attempt.rejected_results);
    line.number(attempt.identity_rejected);
    line.number(attempt.malformed_batches);
    line.number(attempt.event_semantic_rejected);
    line.number(attempt.upstream_event_rejected);
    line.number(attempt.upstream_event_invalid);
    line.number(attempt.source_regressions);
    line.number(attempt.skipped_frames);
    line.number(attempt.ticks.ticks);
    line.number(attempt.ticks.overruns);
    line.number(attempt.ticks.max_us);
    line.number(attempt.ticks.saturated);
    line.number(attempt.upstream_event_overflow);
    line.number(attempt.timing_incomplete);
    line.number(attempt.recording_incomplete);
    line.number(attempt.go_seen);
    line.number(attempt.final_frame_missing);
    line.number(attempt.interrupted);
    line.number(attempt.terminal_exhausted);
    line.number(summary.frame_count);
    line.number(summary.frame_overwritten);
    line.number(summary.frame_rejected_status);
    line.number(summary.frame_clamped);
    line.number(summary.frame_invalid);
    line.number(summary.event_count);
    line.number(summary.event_overflow);
    line.number(summary.event_rejected);
    line.number(summary.incomplete);
    return line.finish(destination, capacity);
}
} // namespace recorder::csv

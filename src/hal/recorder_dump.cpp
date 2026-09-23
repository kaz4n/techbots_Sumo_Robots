// Streams a frozen B15 attempt under fresh, inhibited IDLE service authority.
// Bounds formatting and acknowledged transport progress without changing evidence.
// Independent D090 host scenarios and receiver round trips exercise this owner.
#include "recorder_dump.h"

namespace recorder::dump {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool validConfig() {
    return config::TICK_US > 0U && config::TICK_US < HALF_RANGE &&
        config::DUMP_PAYLOAD_BYTES > 0U && config::DUMP_PAYLOAD_BYTES <= 64U &&
        config::DUMP_STALL_MS > 0U && config::DUMP_TOTAL_MS > 0U &&
        std::uint64_t{config::DUMP_STALL_MS} * 1000U < HALF_RANGE &&
        std::uint64_t{config::DUMP_TOTAL_MS} * 1000U < HALF_RANGE &&
        config::LOG_HZ > 0U && config::LOG_FRAME_CAPACITY > 0U &&
        config::LOG_FRAME_CAPACITY <= 5001U && config::LOG_EVENT_CAPACITY > 0U &&
        config::LOG_EVENT_CAPACITY <= 4096U;
}

bool sameAttempt(const AttemptSummary& a, const AttemptSummary& b) {
    return a.epoch_token == b.epoch_token && a.last_frame_token == b.last_frame_token &&
        a.release_us == b.release_us && a.mode == b.mode &&
        a.observed_results == b.observed_results && a.missing_results == b.missing_results &&
        a.rejected_results == b.rejected_results && a.identity_rejected == b.identity_rejected &&
        a.malformed_batches == b.malformed_batches &&
        a.event_semantic_rejected == b.event_semantic_rejected &&
        a.upstream_event_rejected == b.upstream_event_rejected &&
        a.upstream_event_invalid == b.upstream_event_invalid &&
        a.source_regressions == b.source_regressions && a.skipped_frames == b.skipped_frames &&
        a.ticks.ticks == b.ticks.ticks && a.ticks.overruns == b.ticks.overruns &&
        a.ticks.max_us == b.ticks.max_us && a.ticks.saturated == b.ticks.saturated &&
        a.upstream_event_overflow == b.upstream_event_overflow &&
        a.timing_incomplete == b.timing_incomplete &&
        a.recording_incomplete == b.recording_incomplete && a.go_seen == b.go_seen &&
        a.final_frame_missing == b.final_frame_missing && a.interrupted == b.interrupted &&
        a.terminal_exhausted == b.terminal_exhausted;
}

bool sameSummary(const csv::SummarySnapshot& a, const csv::SummarySnapshot& b) {
    // Compare fields rather than struct bytes: padding carries no evidence.
    return sameAttempt(a.attempt, b.attempt) && a.phase == b.phase &&
        a.frame_count == b.frame_count && a.frame_overwritten == b.frame_overwritten &&
        a.frame_rejected_status == b.frame_rejected_status &&
        a.frame_clamped == b.frame_clamped && a.frame_invalid == b.frame_invalid &&
        a.event_count == b.event_count && a.event_overflow == b.event_overflow &&
        a.event_rejected == b.event_rejected && a.incomplete == b.incomplete;
}

std::uint32_t updateCrc(std::uint32_t crc, const char* bytes, std::size_t count) {
    for (std::size_t i = 0U; i < count && i < config::DUMP_PAYLOAD_BYTES; ++i) {
        crc ^= static_cast<std::uint8_t>(bytes[i]);
        for (unsigned bit = 0U; bit < 8U; ++bit)
            crc = (crc >> 1U) ^ ((crc & 1U) != 0U ? 0xEDB88320U : 0U);
    }
    return crc;
}
} // namespace

bool Transfer::eligible(const fsm::RobotResult& result) const {
    const auto& gate = result.lifecycle.gate;
    return result.outputs.ui_state == core::State::IDLE &&
        gate.phase == countdown::Phase::IDLE && !gate.start_release && !gate.go &&
        !gate.motion_permitted && !result.outputs.motors_enabled &&
        result.outputs.duty_l == 0.0F && result.outputs.duty_r == 0.0F &&
        result.contract_faults == 0U && result.escape_fault == edge::EscapeFault::NONE &&
        result.menu.selection.service_menu &&
        result.menu.selection.service == countdown::Service::LOG_DUMP;
}

void Transfer::fail(Phase phase, Reason reason) {
    const bool cancelling = report_.phase == Phase::ACTIVE;
    report_.phase = phase;
    report_.reason = reason;
    size_ = offset_ = 0U;
    source_ = nullptr;
    // Cancellation revokes pending native bytes even when further writes are forbidden.
    if (cancelling && port_.cancel != nullptr) port_.cancel(port_.context);
}

void Transfer::reject(Reason reason, bool intent) {
    if (report_.phase == Phase::ACTIVE) fail(Phase::CANCELLED, reason);
    else if (intent) fail(Phase::REFUSED, reason);
}

bool Transfer::admitIdentity(const Context& context, const fsm::RobotResult& result,
                             bool intent) {
    if (result.token < last_token_ ||
        (result.token == last_token_ && context.decision_us != last_decision_us_) ||
        (report_.phase == Phase::ACTIVE && result.token > last_token_ &&
         result.token - last_token_ != 1U)) {
        reject(Reason::RESULT_ORDER, intent);
        return false;
    }
    const auto decision_delta = context.decision_us - last_decision_us_;
    if (last_token_ != 0U && result.token > last_token_ &&
        (decision_delta == 0U || decision_delta >= HALF_RANGE)) {
        reject(Reason::TIME_ORDER, intent);
        return false;
    }
    last_token_ = result.token;
    last_decision_us_ = context.decision_us;
    return true;
}

bool Transfer::admit(const Context& context, const fsm::RobotResult& result, bool intent) {
    const bool repeated = observed_ && context.now_us == last_us_;
    const auto delta = observed_ ? context.now_us - last_us_ : 0U;
    if (!repeated && delta < HALF_RANGE) {
        observed_ = true;
        last_us_ = context.now_us;
    }
    // Inhibition beats duplicate-time suppression; STOP/fault never leaves a packet pending.
    Reason unsafe = Reason::NONE;
    if (!eligible(result)) unsafe = Reason::CONTEXT;
    else if (!result.fresh || result.token == 0U) unsafe = Reason::STALE_CONTEXT;
    else if (!context.linux_ready) unsafe = Reason::LINUX_UNAVAILABLE;
    if (unsafe != Reason::NONE) {
        reject(unsafe, intent);
        // Normal match/boot observations still anchor chronology for later IDLE.
        if (!repeated && delta < HALF_RANGE && result.fresh && result.token != 0U &&
            context.now_us - context.decision_us < config::TICK_US)
            admitIdentity(context, result, false);
        return false;
    }
    if (repeated) return false;
    if (delta >= HALF_RANGE) { reject(Reason::TIME_ORDER, intent); return false; }
    if (context.now_us - context.decision_us >= config::TICK_US) {
        reject(Reason::STALE_CONTEXT, intent);
        return false;
    }
    if (!admitIdentity(context, result, intent)) return false;
    if (report_.phase == Phase::ACTIVE) {
        total_age_us_ = saturatedAdd(total_age_us_, delta);
        stall_age_us_ = saturatedAdd(stall_age_us_, delta);
        if (std::uint64_t{total_age_us_} >= std::uint64_t{config::DUMP_TOTAL_MS} * 1000U) {
            fail(Phase::FAILED, Reason::TOTAL);
            return false;
        }
        if (std::uint64_t{stall_age_us_} >= std::uint64_t{config::DUMP_STALL_MS} * 1000U) {
            fail(Phase::FAILED, Reason::STALL);
            return false;
        }
    }
    return true;
}

void Transfer::start(const Context& context, const fsm::RobotResult& result,
                     const AttemptRecorder& source) {
    if (result.menu.request_unavailable) {
        fail(Phase::REFUSED, Reason::CONTEXT);
        return;
    }
    if (!validConfig() || static_cast<unsigned>(context.origin) >
        static_cast<unsigned>(Origin::HARDWARE_REPORTED)) {
        fail(Phase::REFUSED, Reason::INVALID_CONFIG);
        return;
    }
    if (port_.write == nullptr || port_.cancel == nullptr) {
        fail(Phase::REFUSED, Reason::PORT);
        return;
    }
    const auto snapshot = csv::captureSummary(source);
    if ((snapshot.phase != AttemptPhase::SEALED && snapshot.phase != AttemptPhase::INTERRUPTED) ||
        snapshot.attempt.epoch_token == 0U || snapshot.attempt.terminal_exhausted ||
        snapshot.frame_count > config::LOG_FRAME_CAPACITY ||
        snapshot.event_count > config::LOG_EVENT_CAPACITY) {
        fail(Phase::REFUSED, Reason::NO_EVIDENCE);
        return;
    }
    summary_ = snapshot;
    source_ = &source;
    origin_ = context.origin;
    report_ = Report{};
    report_.phase = Phase::ACTIVE;
    report_.session = result.token;
    report_.epoch = snapshot.attempt.epoch_token;
    size_ = offset_ = ordinal_ = total_age_us_ = stall_age_us_ = 0U;
    crc_ = 0xFFFFFFFFU;
    record_ = Record::BEGIN;
}

bool Transfer::unchanged(const AttemptRecorder& source) const {
    return source_ == &source && sameSummary(summary_, csv::captureSummary(source));
}

bool Transfer::append(const char* value) {
    for (std::size_t i = 0U; i < MAX_WIRE_LINE_BYTES; ++i) {
        if (value[i] == '\0') { line_[size_] = '\0'; return true; }
        if (size_ >= MAX_WIRE_LINE_BYTES - 1U) return false;
        line_[size_++] = value[i];
    }
    return false;
}

bool Transfer::number(std::uint64_t value, char delimiter) {
    char reversed[20];
    std::size_t count = 0U;
    for (std::size_t i = 0U; i < sizeof(reversed); ++i) {
        reversed[count++] = static_cast<char>('0' + value % 10U);
        value /= 10U;
        if (value == 0U) break;
    }
    if (MAX_WIRE_LINE_BYTES - size_ <= count + 1U) return false;
    for (std::size_t i = 0U; i < count; ++i) line_[size_++] = reversed[count - 1U - i];
    line_[size_++] = delimiter;
    line_[size_] = '\0';
    return true;
}

bool Transfer::prefix(const char* tag) {
    return append(tag) && number(report_.session, ',');
}

bool Transfer::prepareEnvelope() {
    if (record_ == Record::END)
        return prefix("END,") && number(summary_.frame_count, ',') &&
            number(summary_.event_count, ',') && number(crc_ ^ 0xFFFFFFFFU, '\n');
    return append("SUMOX26_DUMP,1,") && number(report_.session, ',') &&
        number(report_.epoch, ',') && number(static_cast<std::uint8_t>(origin_), ',') &&
        number(config::LOG_HZ, ',') && number(config::LOG_FRAME_CAPACITY, ',') &&
        number(config::LOG_EVENT_CAPACITY, ',') && number(summary_.frame_count, ',') &&
        number(summary_.event_count, '\n');
}

csv::FormatResult Transfer::preparePayload(char* destination, std::size_t capacity) {
    switch (record_) {
    case Record::SUMMARY_HEADER: return csv::summaryHeader(destination, capacity);
    case Record::SUMMARY_ROW: return csv::summaryRow(summary_, destination, capacity);
    case Record::FRAME_HEADER: return csv::frameHeader(destination, capacity);
    case Record::EVENT_HEADER: return csv::eventHeader(destination, capacity);
    case Record::FRAME_ROW: {
        const auto* frame = source_->frames().at(ordinal_);
        return frame == nullptr ? csv::FormatResult{} :
            csv::frameRow(*frame, ordinal_, destination, capacity);
    }
    case Record::EVENT_ROW: {
        const auto* event = source_->events().at(ordinal_);
        return event == nullptr ? csv::FormatResult{} :
            csv::eventRow(*event, ordinal_, destination, capacity);
    }
    default: return {};
    }
}

bool Transfer::prepare() {
    size_ = offset_ = 0U;
    if (record_ == Record::BEGIN || record_ == Record::END) return prepareEnvelope();
    const char* tag = nullptr;
    switch (record_) {
    case Record::SUMMARY_HEADER: tag = "SH,"; break;
    case Record::SUMMARY_ROW: tag = "SR,"; break;
    case Record::FRAME_HEADER: tag = "FH,"; break;
    case Record::FRAME_ROW: tag = "FR,"; break;
    case Record::EVENT_HEADER: tag = "EH,"; break;
    case Record::EVENT_ROW: tag = "ER,"; break;
    default: return false;
    }
    if (!prefix(tag)) return false;
    const auto payload = preparePayload(line_ + size_, MAX_WIRE_LINE_BYTES - size_);
    if (payload.status != csv::FormatStatus::OK || payload.size == 0U ||
        payload.size >= MAX_WIRE_LINE_BYTES - size_) return false;
    size_ += payload.size;
    return true;
}

void Transfer::advance() {
    size_ = offset_ = 0U;
    switch (record_) {
    case Record::BEGIN: record_ = Record::SUMMARY_HEADER; break;
    case Record::SUMMARY_HEADER: record_ = Record::SUMMARY_ROW; break;
    case Record::SUMMARY_ROW: record_ = Record::FRAME_HEADER; break;
    case Record::FRAME_HEADER:
        ordinal_ = 0U;
        record_ = summary_.frame_count == 0U ? Record::EVENT_HEADER : Record::FRAME_ROW;
        break;
    case Record::FRAME_ROW:
        ++report_.frames;
        if (++ordinal_ == summary_.frame_count) record_ = Record::EVENT_HEADER;
        break;
    case Record::EVENT_HEADER:
        ordinal_ = 0U;
        record_ = summary_.event_count == 0U ? Record::END : Record::EVENT_ROW;
        break;
    case Record::EVENT_ROW:
        ++report_.events;
        if (++ordinal_ == summary_.event_count) record_ = Record::END;
        break;
    case Record::END:
        record_ = Record::FINISHED;
        report_.phase = Phase::SENT_UNCONFIRMED;
        source_ = nullptr;
        break;
    case Record::FINISHED: break;
    }
}

void Transfer::writePending(const AttemptRecorder& source) {
    if (!unchanged(source)) { fail(Phase::CANCELLED, Reason::SOURCE_CHANGED); return; }
    const auto remaining = size_ - offset_;
    const auto offered = remaining < config::DUMP_PAYLOAD_BYTES ?
        remaining : static_cast<std::size_t>(config::DUMP_PAYLOAD_BYTES);
    const auto result = port_.write(port_.context, line_ + offset_, offered);
    if (result.status == WriteStatus::PENDING && result.count == 0U) return;
    if (result.status != WriteStatus::PROGRESS || result.count == 0U || result.count > offered) {
        fail(Phase::FAILED, Reason::PORT);
        return;
    }
    if (record_ != Record::END) crc_ = updateCrc(crc_, line_ + offset_, result.count);
    report_.crc = crc_ ^ 0xFFFFFFFFU;
    report_.bytes += static_cast<std::uint32_t>(result.count);
    offset_ += result.count;
    stall_age_us_ = 0U;
    if (offset_ == size_) advance();
}

Report Transfer::step(const Context& context, const fsm::RobotResult& result,
                      const AttemptRecorder& source) {
    const bool request = result.menu.request == countdown::Service::LOG_DUMP;
    const bool intent = request && result.token > last_request_;
    // Even an ignored intent is consumed; completing a session cannot replay it.
    if (request && result.token > last_request_) last_request_ = result.token;
    if (!admit(context, result, intent)) return report_;
    if (report_.phase != Phase::ACTIVE) {
        if (!intent) return report_;
        start(context, result, source);
        if (report_.phase != Phase::ACTIVE) return report_;
    }
    if (!unchanged(source)) { fail(Phase::CANCELLED, Reason::SOURCE_CHANGED); return report_; }
    if (size_ == 0U && !prepare()) { fail(Phase::FAILED, Reason::FORMAT); return report_; }
    writePending(source);
    return report_;
}

void Transfer::onRobotReset() {
    if (last_token_ > last_request_) last_request_ = last_token_;
    if (report_.phase == Phase::ACTIVE) fail(Phase::CANCELLED, Reason::RESET);
}
} // namespace recorder::dump

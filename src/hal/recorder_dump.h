// Streams one retained B15 attempt only under current inhibited IDLE authority.
// Owns bounded progress and cancellation without resetting Robot or the recorder.
// Independent actual-pipeline and receive-side round trips test D090.
#pragma once
#include "recorder_csv.h"
namespace recorder::dump {
inline constexpr std::size_t MAX_WIRE_LINE_BYTES = 1152U;
enum class Origin : std::uint8_t { UNKNOWN, SYNTHETIC, HARDWARE_REPORTED };
enum class Phase : std::uint8_t { IDLE, ACTIVE, SENT_UNCONFIRMED, CANCELLED, FAILED, REFUSED };
enum class Reason : std::uint8_t {
 NONE, CONTEXT, STALE_CONTEXT, RESULT_ORDER, TIME_ORDER, LINUX_UNAVAILABLE,
 NO_EVIDENCE, SOURCE_CHANGED, FORMAT, PORT, STALL, TOTAL, RESET, INVALID_CONFIG,
 SESSION_CHANGED
};
enum class WriteStatus : std::uint8_t { PENDING, PROGRESS, ERROR };
struct WriteResult { WriteStatus status = WriteStatus::ERROR; std::size_t count = 0U; };
struct Port {
 void* context = nullptr;
 WriteResult (*write)(void*, const char*, std::size_t) = nullptr;
 void (*cancel)(void*) = nullptr;
};
struct Context {
 std::uint32_t now_us = 0U, decision_us = 0U;
 bool linux_ready = false;
 Origin origin = Origin::UNKNOWN;
 // Zero preserves the legacy result-token identity; nonzero is caller supplied.
 std::uint64_t session = 0U;
};
struct Report {
 Phase phase = Phase::IDLE;
 Reason reason = Reason::NONE;
 std::uint64_t session = 0U, epoch = 0U;
 std::uint32_t bytes = 0U, frames = 0U, events = 0U, crc = 0U;
};
class Transfer {
public:
 explicit Transfer(const Port& port) : port_(port) {}
 Report step(const Context&, const fsm::RobotResult&, const AttemptRecorder&);
 void onRobotReset();
 // Owner failure cancels an active transfer once without resetting its history.
 void abort();
 const Report& report() const { return report_; }
private:
 // Private implementation state may be extended by the assigned owner only.
 enum class Record : std::uint8_t { BEGIN, SUMMARY_HEADER, SUMMARY_ROW,
     FRAME_HEADER, FRAME_ROW, EVENT_HEADER, EVENT_ROW, END, FINISHED };
 bool eligible(const fsm::RobotResult&) const;
 bool admit(const Context&, const fsm::RobotResult&, bool intent);
 bool admitIdentity(const Context&, const fsm::RobotResult&, bool intent);
 void reject(Reason, bool intent);
 bool unchanged(const AttemptRecorder&) const;
 bool prepare();
 bool prepareEnvelope();
 csv::FormatResult preparePayload(char*, std::size_t);
 bool prefix(const char*);
 bool append(const char*);
 bool number(std::uint64_t, char);
 void writePending(const AttemptRecorder&);
 void start(const Context&, const fsm::RobotResult&, const AttemptRecorder&);
 void fail(Phase, Reason);
 void advance();
 Port port_;
 Report report_;
 csv::SummarySnapshot summary_;
 const AttemptRecorder* source_ = nullptr;
 char line_[MAX_WIRE_LINE_BYTES] = {};
 std::size_t size_ = 0U, offset_ = 0U;
 Record record_ = Record::BEGIN;
 Origin origin_ = Origin::UNKNOWN;
 std::uint64_t last_token_ = 0U, last_request_ = 0U;
 std::uint64_t supplied_session_ = 0U;
 std::uint32_t last_us_ = 0U, last_decision_us_ = 0U;
 std::uint32_t total_age_us_ = 0U, stall_age_us_ = 0U;
 std::uint32_t ordinal_ = 0U, crc_ = 0xFFFFFFFFU;
 bool observed_ = false;
};
} // namespace recorder::dump

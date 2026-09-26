// Provides bounded transmit-only mon/write notifications on the internal UART.
// Excludes stock blocking Bridge calls and latches framing uncertainty on cancellation.
// Native substitute tests and target hook/register inspection qualify D090 software.
#pragma once
#include "recorder_dump.h"
namespace recorder::dump {
enum class NativeStatus : std::uint8_t {
 NOT_INITIALIZED, OK, CONTEXT, OWNERSHIP, DEVICE, READY_LOW, READY_ERROR,
 REGISTER, POISONED, TIMEOUT, INVALID_ARGUMENT
};
enum class FailureSite : std::uint8_t {
 NONE, SETUP, SETUP_OWNERSHIP, SETUP_READY, FIFO_OWNERSHIP, FIFO_READBACK,
 WRITE_POISONED, WRITE_CONTEXT, WRITE_OWNERSHIP, WRITE_ARGUMENT,
 TRANSMIT_OWNERSHIP, TRANSMIT_READY, TRANSMIT_DEADLINE, STORE_DEADLINE,
 COMPLETE_OWNERSHIP, COMPLETE_READY, COMPLETE_DEADLINE, TC_DEADLINE,
 CANCEL, REPEATED_BEGIN
};
enum class CleanupDisposition : std::uint8_t {
 NOT_ATTEMPTED, SKIPPED_POISONED, SKIPPED_CONTEXT, SKIPPED_OWNERSHIP,
 VERIFIED, READBACK_FAILED
};
struct FailureRecord {
 NativeStatus reason = NativeStatus::NOT_INITIALIZED;
 FailureSite site = FailureSite::NONE;
 CleanupDisposition cleanup = CleanupDisposition::NOT_ATTEMPTED;
 NativeStatus cleanup_ownership = NativeStatus::NOT_INITIALIZED;
 std::uint8_t packet_offset = 0U, packet_size = 0U, payload_size = 0U;
 bool ownership_evaluated = false;
};
static_assert(sizeof(FailureRecord) == 8U, "First failure is a bounded diagnostic record");
enum class Buffering : std::uint8_t { LEGACY_SINGLE = 0U, FIFO8 = 1U };
enum class ReceiveStream : std::uint8_t {
 TRUSTED_FRAMING = 0U, UNTRUSTED_RECEIVE_STREAM = 1U
};
struct SetupGrant {
 bool setup_phase = false;
 bool exclusive_uart = false;
 bool ready_pin_owned = false;
 bool framing_clean = false;
 ReceiveStream receive_stream = ReceiveStream::TRUSTED_FRAMING;
 std::uint64_t session = 0U;
};
// Identified reception tolerates unknown upstream framing only. It creates no
// ownership grant and the receiver must reject every wrong-session envelope.
inline bool setupGrantAccepted(const SetupGrant& grant) {
 if (!grant.setup_phase || !grant.exclusive_uart || !grant.ready_pin_owned) return false;
 if (grant.receive_stream == ReceiveStream::TRUSTED_FRAMING) return grant.framing_clean;
 return grant.receive_stream == ReceiveStream::UNTRUSTED_RECEIVE_STREAM && grant.session != 0U;
}
class UnoQDumpPort {
public:
 constexpr UnoQDumpPort() = default;
 explicit constexpr UnoQDumpPort(Buffering buffering) : buffering_(buffering) {}
 // Setup-only device_init contains verified unbounded TEACK/REACK waits. Never
 // call it lazily in loop. Grants are actual caller obligations, not observations.
 NativeStatus begin(const SetupGrant&);
 bool ready();
 Port port();
 NativeStatus status() const { return status_; }
 // Immutable first failure/cancellation evidence; not an atomic live snapshot.
 const FailureRecord& firstFailure() const { return first_failure_; }
private:
 const Buffering buffering_ = Buffering::LEGACY_SINGLE;
 static WriteResult write(void*, const char*, std::size_t);
 static void cancel(void*);
 WriteResult advance(const char*, std::size_t);
 NativeStatus ownership() const;
 NativeStatus ownedState(std::uint32_t expected, std::uint32_t alternate, bool live) const;
 NativeStatus beginFifo();
 NativeStatus failFifo(NativeStatus, FailureSite, std::uint32_t verified, std::uint32_t attempted);
 NativeStatus sampleReady() const;
 bool remember(NativeStatus, FailureSite);
 NativeStatus setupFailure(NativeStatus, FailureSite = FailureSite::SETUP);
 WriteResult fail(NativeStatus, FailureSite);
 bool prepare(const char*, std::size_t);
 bool withinDeadline(std::uint32_t) const;
 WriteResult transmit(std::uint32_t);
 void abort(NativeStatus = NativeStatus::OK, FailureSite = FailureSite::CANCEL);
 void poison();
 NativeStatus status_ = NativeStatus::NOT_INITIALIZED;
 char payload_[64] = {};
 std::uint8_t packet_[79] = {};
 std::size_t payload_size_ = 0U, packet_size_ = 0U, offset_ = 0U;
 std::uint32_t started_us_ = 0U;
 std::uint32_t baud_register_ = 0U;
 std::uint32_t clock_registers_[8] = {};
 bool cleanup_verified_ = false;
 bool initialized_ = false, attempted_ = false, active_ = false, poisoned_ = false;
 FailureRecord first_failure_;
};
} // namespace recorder::dump

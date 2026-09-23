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
enum class Buffering : std::uint8_t { LEGACY_SINGLE = 0U, FIFO8 = 1U };
struct SetupGrant {
 bool setup_phase = false;
 bool exclusive_uart = false;
 bool ready_pin_owned = false;
 bool framing_clean = false;
};
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
private:
 const Buffering buffering_ = Buffering::LEGACY_SINGLE;
 static WriteResult write(void*, const char*, std::size_t);
 static void cancel(void*);
 WriteResult advance(const char*, std::size_t);
 NativeStatus ownership() const;
 NativeStatus sampleReady() const;
 WriteResult fail(NativeStatus);
 bool prepare(const char*, std::size_t);
 bool withinDeadline(std::uint32_t) const;
 WriteResult transmit(std::uint32_t);
 void abort();
 NativeStatus status_ = NativeStatus::NOT_INITIALIZED;
 char payload_[64] = {};
 std::uint8_t packet_[79] = {};
 std::size_t payload_size_ = 0U, packet_size_ = 0U, offset_ = 0U;
 std::uint32_t started_us_ = 0U;
 std::uint32_t baud_register_ = 0U;
 std::uint32_t clock_registers_[8] = {};
 bool cleanup_verified_ = false;
 bool initialized_ = false, attempted_ = false, active_ = false, poisoned_ = false;
};
} // namespace recorder::dump

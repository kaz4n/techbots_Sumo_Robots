// Acquires one fresh battery sample through the privately owned native ADC1.
// Reports conversion and shutdown failures instead of reusing stale voltage.
// Independent native-header tests and an inert target probe verify this driver.
#pragma once
#include <cstdint>

namespace power {
enum class Status : std::uint8_t {
    OK, NOT_INITIALIZED, ALREADY_STARTED, INVALID_CONFIG, OWNERSHIP,
    REGULATOR_TIMEOUT, CALIBRATION_TIMEOUT, ENABLE_TIMEOUT, CONVERSION_TIMEOUT,
    POLL_LIMIT, READBACK, OVERRUN, INVALID_DATA, FAULT_LATCHED
};
enum class Shutdown : std::uint8_t { NOT_ATTEMPTED, DISABLED, UNCONFIRMED };
struct InitResult {
    Status status = Status::NOT_INITIALIZED;
    Shutdown shutdown = Shutdown::NOT_ATTEMPTED;
    bool ready = false;
};
struct Sample {
    Status status = Status::NOT_INITIALIZED;
    Shutdown shutdown = Shutdown::NOT_ATTEMPTED;
    std::uint16_t raw = 0U;
    std::uint32_t started_us = 0U;
    std::uint32_t completed_us = 0U;
    float voltage_v = 0.0F;
    bool valid = false;
};
class Reader {
public:
    Reader() = default;
    Reader(const Reader&) = delete;
    Reader& operator=(const Reader&) = delete;
    // Setup only. One attempt per instance/boot; no I/O in construction.
    InitResult begin();
    // Bounded native conversion; no last-value cache or second voltage filter.
    Sample read();
private:
    // Implementation may add private helpers/state without changing this API.
    bool attempted_ = false;
    bool ready_ = false;
    bool owned_ = false;
    bool faulted_ = false;
    Shutdown shutdown_ = Shutdown::NOT_ATTEMPTED;
};
} // namespace power

// Transfers bounded MPU6050 register requests on the installed UNO Q I2C4.
// Separates complete bus bytes from sensor freshness, configuration and heading.
// Independent native-register tests and an inert target probe check this boundary.
#pragma once
#include <cstdint>

namespace imu {
enum class Register : std::uint8_t {
    SAMPLE_DIVIDER = 0x19, FILTER = 0x1A, GYRO_RANGE = 0x1B,
    ACCEL_RANGE = 0x1C, FIFO_ENABLE = 0x23, INTERRUPT_CONFIG = 0x37,
    INTERRUPT_ENABLE = 0x38, INTERRUPT_STATUS = 0x3A,
    USER_CONTROL = 0x6A, POWER_1 = 0x6B, POWER_2 = 0x6C, IDENTITY = 0x75
};
enum class BusStatus : std::uint8_t {
    OK, NOT_INITIALIZED, ALREADY_STARTED, INVALID_CONFIG, INVALID_REQUEST,
    OWNERSHIP, READBACK, BUS_NOT_IDLE, NACK, ARBITRATION_LOST, BUS_ERROR,
    OVERRUN, PROTOCOL, TIMEOUT, POLL_LIMIT, FAULT_LATCHED
};
// DISABLED acknowledges local PE=0, not a STOP or an electrically idle bus.
enum class BusCleanup : std::uint8_t { NOT_ATTEMPTED, DISABLED, UNCONFIRMED };
struct BusInit {
    BusStatus status = BusStatus::NOT_INITIALIZED;
    BusCleanup cleanup = BusCleanup::NOT_ATTEMPTED;
    bool ready = false;
};
struct BusTransfer {
    BusStatus status = BusStatus::NOT_INITIALIZED;
    BusCleanup cleanup = BusCleanup::NOT_ATTEMPTED;
    std::uint8_t bytes[15] = {};
    std::uint8_t count = 0U;
    std::uint32_t started_us = 0U;
    std::uint32_t completed_us = 0U;
    std::uint32_t error_flags = 0U; // Native errors and unexpected protocol status.
    bool complete = false;
};
class Bus {
public:
    Bus() = default;
    Bus(const Bus&) = delete;
    Bus& operator=(const Bus&) = delete;
    // Setup only; one attempt per instance and irreversible claim per boot.
    BusInit begin();
    // Fixed MPU6050 register allowlist; unsupported requests perform no I/O.
    BusTransfer readRegister(Register reg);
    BusTransfer writeRegister(Register reg, std::uint8_t value);
    // Reads INT_STATUS plus the coherent 14-byte motion window, 0x3A..0x48.
    // Completion does not prove a new sample or validate the sensor settings.
    BusTransfer readMotion();
private:
    struct Operation {
        std::uint32_t started_us = 0U;
        std::uint32_t observed_us = 0U;
        std::uint32_t polls = 0U;
        std::uint32_t error_flags = 0U;
    };
    bool controlsOwned(bool changing_pe = false);
    bool ownershipValid(bool changing_pe = false);
    BusStatus setupCheckpoint(Operation& op);
    BusStatus configurePad(std::uint32_t pin, Operation& op);
    BusStatus initialize(Operation& op);
    BusCleanup disableOwned();
    BusTransfer failed(BusStatus status, const Operation& op);
    BusStatus observe(Operation& op, std::uint32_t allowed, std::uint32_t& flags);
    BusStatus waitFor(Operation& op, std::uint32_t wanted, std::uint32_t allowed);
    BusStatus launch(Operation& op, std::uint8_t count, bool reading, bool automatic);
    BusStatus sendByte(Operation& op, std::uint8_t value);
    BusStatus receive(Operation& op, BusTransfer& staging, std::uint8_t count);
    BusStatus finish(Operation& op);
    BusStatus admitRequest(Operation& op);
    BusTransfer request(Register reg, std::uint8_t value, std::uint8_t count, bool writing);
    bool attempted_ = false;
    bool ready_ = false;
    bool owned_ = false;
    bool faulted_ = false;
    bool configured_ = false;
    bool pe_enabled_ = false;
    bool ownership_lost_ = false;
    std::uint32_t pad_mode_ = 0U;
    std::uint32_t pad_pull_ = 0U;
    std::uint32_t pad_type_ = 0U;
    std::uint32_t pad_speed_ = 0U;
    std::uint32_t pad_af_ = 0U;
    std::uint32_t cr2_expected_ = 0U;
    BusCleanup cleanup_ = BusCleanup::NOT_ATTEMPTED;
};
} // namespace imu

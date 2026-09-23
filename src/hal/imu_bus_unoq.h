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
    OVERRUN, PROTOCOL, TIMEOUT, POLL_LIMIT, FAULT_LATCHED, CANCELLED
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
enum class AcquisitionState : std::uint8_t { FAULT, NO_NEW, OBSERVATION };
struct BusAcquisition {
    AcquisitionState state = AcquisitionState::FAULT;
    BusTransfer transfer{}; // One aggregate interval; payload only on OBSERVATION.
    std::uint8_t readiness_status = 0U;
    bool readiness_observed = false;
    std::uint32_t readiness_completed_us = 0U;
    bool motion_attempted = false;
    std::uint32_t motion_started_us = 0U; // Before second admission, not sample time.
    bool motion_status_observed = false;
    std::uint8_t motion_status = 0U; // Diagnostic only, never a second generation.
};
// D094 progress is not an acquisition; pending payload remains default/empty.
enum class AsyncState : std::uint8_t { IDLE, PENDING, COMPLETE, FAULT };
struct BusProgress {
    AsyncState state = AsyncState::IDLE;
    bool started = false; // This invocation accepted a new runtime operation.
    bool completed = false; // This invocation produced one terminal result.
    std::uint32_t started_us = 0U;
    std::uint32_t observed_us = 0U; // Service clock, never a sensor generation.
    std::uint32_t polls = 0U;
    BusAcquisition acquisition{}; // Only terminal reports expose acquisition data.
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
    // D081 profile/exclusive-owner precondition; status, STOP/idle, then15bytes.
    // Shares one deadline/poll budget; freshness relies on documented shadow behavior.
    BusAcquisition acquireMotion();
    // One original deadline/poll budget across all advances and caller work.
    // begin only anchors time; advance performs at most one guarded protocol action.
    // Duplicate begin and passive reports do no I/O. Caller must finish/cancel.
    BusProgress beginMotion();
    BusProgress advanceMotion();
    BusProgress cancelMotion();
    BusProgress motionReport() const;
    // Supported legacy transfers during PENDING cancel terminally, never interleave.
private:
    // Private state/helpers may be extended by the implementation owner only.
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
    BusTransfer failed(BusStatus status, Operation& op);
    BusStatus checkFlags(Operation& op, std::uint32_t allowed, std::uint32_t flags);
    BusStatus observe(Operation& op, std::uint32_t allowed, std::uint32_t& flags);
    BusStatus waitFor(Operation& op, std::uint32_t wanted, std::uint32_t allowed);
    BusStatus launch(Operation& op, std::uint8_t count, bool reading, bool automatic);
    BusStatus sendByte(Operation& op, std::uint8_t value);
    BusStatus receive(Operation& op, BusTransfer& staging, std::uint8_t count);
    BusStatus finish(Operation& op);
    BusStatus admitRequest(Operation& op, bool bounded_advance = false);
    BusTransfer transfer(Operation& op, Register reg, std::uint8_t value,
                         std::uint8_t count, bool writing);
    BusTransfer request(Register reg, std::uint8_t value, std::uint8_t count, bool writing);
    BusProgress cancelActiveMotion();
    BusProgress endMotion(BusStatus status);
    enum class MotionPhase : std::uint8_t { ADMIT, POINTER, RESTART, RECEIVE, STOP, FINISH, MOTION_START };
    BusStatus motionReady(std::uint32_t wanted, std::uint32_t allowed, bool& ready);
    BusStatus startMotionPhase();
    BusStatus restartMotionPhase();
    BusStatus receiveMotionByte();
    BusStatus stopMotionPhase();
    BusStatus finishMotionPhase();
    BusStatus acceptMotionPhase();
    bool async_active_ = false;
    Operation async_operation_{};
    BusProgress async_report_{};
    BusAcquisition async_acquisition_{};
    BusTransfer async_staging_{};
    MotionPhase async_phase_ = MotionPhase::ADMIT;
    std::uint8_t async_count_ = 1U;
    std::uint8_t async_index_ = 0U;
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

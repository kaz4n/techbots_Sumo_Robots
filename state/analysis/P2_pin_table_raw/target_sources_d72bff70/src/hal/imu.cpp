// Checks one fixed MPU6050 setup sequence and decodes coherent sensor bytes.
// Caller time and one Bus operation per advance keep setup finite and observable.
// Independent scripted-bus tests and an inert target probe exercise this source.
#include "imu.h"
#include "../config.h"

namespace imu {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;
enum class Operation : std::uint8_t { BEGIN, READ, WRITE, MOTION };
struct Step {
    Operation operation;
    Register reg;
    std::uint8_t value;
    std::uint32_t wait_us;
    bool starts_wait;
};

// These are register-format bytes for the sole supported profile, not tunables.
constexpr Step STEPS[] = {
    {Operation::BEGIN, Register::IDENTITY, 0x00, config::IMU_POWER_WAIT_US, false},
    {Operation::READ, Register::IDENTITY, 0x68, 0U, false},
    {Operation::WRITE, Register::POWER_1, 0x80, 0U, true},
    {Operation::READ, Register::POWER_1, 0x40, config::IMU_RESET_WAIT_US, false},
    {Operation::READ, Register::IDENTITY, 0x68, 0U, false},
    {Operation::READ, Register::POWER_2, 0x00, 0U, false},
    {Operation::READ, Register::USER_CONTROL, 0x00, 0U, false},
    {Operation::READ, Register::FIFO_ENABLE, 0x00, 0U, false},
    {Operation::READ, Register::FILTER, 0x00, 0U, false},
    {Operation::READ, Register::SAMPLE_DIVIDER, 0x00, 0U, false},
    {Operation::READ, Register::GYRO_RANGE, 0x00, 0U, false},
    {Operation::READ, Register::ACCEL_RANGE, 0x00, 0U, false},
    {Operation::READ, Register::INTERRUPT_CONFIG, 0x00, 0U, false},
    {Operation::READ, Register::INTERRUPT_ENABLE, 0x00, 0U, false},
    {Operation::WRITE, Register::POWER_2, 0x00, 0U, false},
    {Operation::READ, Register::POWER_2, 0x00, 0U, false},
    {Operation::WRITE, Register::POWER_1, 0x00, 0U, true},
    {Operation::READ, Register::POWER_1, 0x00, 0U, false},
    {Operation::WRITE, Register::POWER_1, 0x01, config::IMU_GYRO_WAIT_US, true},
    {Operation::READ, Register::POWER_1, 0x01, 0U, false},
    {Operation::WRITE, Register::USER_CONTROL, 0x00, config::IMU_PLL_WAIT_US, false},
    {Operation::READ, Register::USER_CONTROL, 0x00, 0U, false},
    {Operation::WRITE, Register::FIFO_ENABLE, 0x00, 0U, false},
    {Operation::READ, Register::FIFO_ENABLE, 0x00, 0U, false},
    {Operation::WRITE, Register::INTERRUPT_CONFIG, 0x00, 0U, false},
    {Operation::READ, Register::INTERRUPT_CONFIG, 0x00, 0U, false},
    {Operation::WRITE, Register::FILTER, 0x01, 0U, false},
    {Operation::READ, Register::FILTER, 0x01, 0U, false},
    {Operation::WRITE, Register::SAMPLE_DIVIDER, 0x00, 0U, false},
    {Operation::READ, Register::SAMPLE_DIVIDER, 0x00, 0U, false},
    {Operation::WRITE, Register::GYRO_RANGE, 0x10, 0U, false},
    {Operation::READ, Register::GYRO_RANGE, 0x10, 0U, false},
    {Operation::WRITE, Register::ACCEL_RANGE, 0x10, 0U, false},
    {Operation::READ, Register::ACCEL_RANGE, 0x10, 0U, false},
    {Operation::WRITE, Register::INTERRUPT_ENABLE, 0x01, 0U, true},
    {Operation::READ, Register::INTERRUPT_ENABLE, 0x01, 0U, false},
    {Operation::READ, Register::IDENTITY, 0x68, config::IMU_FILTER_WAIT_US, false},
    {Operation::READ, Register::POWER_1, 0x01, 0U, false},
    {Operation::READ, Register::POWER_2, 0x00, 0U, false},
    {Operation::READ, Register::USER_CONTROL, 0x00, 0U, false},
    {Operation::READ, Register::FIFO_ENABLE, 0x00, 0U, false},
    {Operation::READ, Register::FILTER, 0x01, 0U, false},
    {Operation::READ, Register::SAMPLE_DIVIDER, 0x00, 0U, false},
    {Operation::READ, Register::GYRO_RANGE, 0x10, 0U, false},
    {Operation::READ, Register::ACCEL_RANGE, 0x10, 0U, false},
    {Operation::READ, Register::INTERRUPT_CONFIG, 0x00, 0U, false},
    {Operation::READ, Register::INTERRUPT_ENABLE, 0x01, 0U, false},
    {Operation::MOTION, Register::INTERRUPT_STATUS, 0x00, 0U, false}
};
static_assert(sizeof(STEPS) / sizeof(STEPS[0]) == 48U, "D080 has exactly 48 Bus calls");

bool profileValid() {
    return config::IMU_GYRO_RANGE_DPS == 1000U && config::IMU_ACCEL_RANGE_G == 8U &&
        config::IMU_DLPF_CFG == 1U && config::IMU_SAMPLE_DIVIDER == 0U;
}

bool transferBoundValid() {
    return config::IMU_I2C_TRANSFER_US > 0U && config::IMU_I2C_TRANSFER_US < HALF_RANGE;
}

bool setupConfigValid() {
    if (!profileValid() || !transferBoundValid() || config::IMU_SETUP_DEADLINE_US == 0U ||
        config::IMU_SETUP_DEADLINE_US >= HALF_RANGE ||
        config::IMU_SETUP_MAX_ADVANCES == 0U || config::IMU_SETUP_MAX_ADVANCES > 65535U ||
        config::IMU_SETUP_MAX_REQUESTS == 0U || config::IMU_SETUP_MAX_REQUESTS > 65535U) return false;
    const std::uint32_t waits[] = {config::IMU_POWER_WAIT_US, config::IMU_RESET_WAIT_US,
        config::IMU_GYRO_WAIT_US, config::IMU_PLL_WAIT_US, config::IMU_FILTER_WAIT_US};
    for (const auto wait : waits) {
        if (wait == 0U || wait >= config::IMU_SETUP_DEADLINE_US) return false;
    }
    return true;
}

bool responseShape(const BusTransfer& transfer, std::uint8_t count) {
    return transfer.complete && transfer.count == count && transfer.error_flags == 0U &&
        transfer.cleanup == BusCleanup::NOT_ATTEMPTED;
}

std::int32_t signedWord(const std::uint8_t* bytes) {
    const auto word = (static_cast<std::uint32_t>(bytes[0]) << 8U) | bytes[1];
    return word < 32768U ? static_cast<std::int32_t>(word) :
        -static_cast<std::int32_t>(65536U - word);
}

bool rail(std::int32_t value) { return value == -32768 || value == 32767; }
} // namespace

SetupReport Setup::fail(SetupFault fault) {
    report_.state = SetupState::FAULT;
    report_.fault = fault;
    return report_;
}

SetupReport Setup::start(std::uint32_t now_us, bool power_confirmed) {
    if (report_.state != SetupState::NOT_STARTED) return report_;
    report_.state = SetupState::IN_PROGRESS;
    report_.started_us = now_us;
    report_.observed_us = now_us;
    wait_started_us_ = now_us;
    if (!power_confirmed) return fail(SetupFault::POWER_UNCONFIRMED);
    if (!setupConfigValid()) return fail(SetupFault::INVALID_CONFIG);
    return report_;
}

bool Setup::acceptTime(std::uint32_t now_us) {
    if (now_us - report_.observed_us >= HALF_RANGE) {
        fail(SetupFault::TIME_ORDER);
        return false;
    }
    report_.observed_us = now_us;
    if (now_us - report_.started_us >= config::IMU_SETUP_DEADLINE_US) {
        fail(SetupFault::DEADLINE);
        return false;
    }
    return true;
}

bool Setup::acceptTransfer(const BusTransfer& transfer, std::uint8_t count, std::uint32_t call_us) {
    report_.bus_status = transfer.status;
    report_.cleanup = transfer.cleanup;
    report_.error_flags = transfer.error_flags;
    if (transfer.status != BusStatus::OK) { fail(SetupFault::TRANSPORT); return false; }
    if (!responseShape(transfer, count)) { fail(SetupFault::RESPONSE); return false; }
    if (transfer.started_us - call_us >= HALF_RANGE ||
        transfer.completed_us - transfer.started_us >= HALF_RANGE) {
        fail(SetupFault::TIME_ORDER);
        return false;
    }
    if (transfer.completed_us - transfer.started_us >= config::IMU_I2C_TRANSFER_US) {
        fail(SetupFault::RESPONSE);
        return false;
    }
    return acceptTime(transfer.completed_us);
}

SetupReport Setup::advance(std::uint32_t now_us) {
    if (report_.state != SetupState::IN_PROGRESS) return report_;
    if (report_.advances >= config::IMU_SETUP_MAX_ADVANCES) return fail(SetupFault::ADVANCE_LIMIT);
    ++report_.advances;
    if (!acceptTime(now_us)) return report_;
    const auto& step = STEPS[step_];
    if (now_us - wait_started_us_ < step.wait_us) return report_;
    if (report_.requests >= config::IMU_SETUP_MAX_REQUESTS) return fail(SetupFault::REQUEST_LIMIT);
    ++report_.requests;
    if (step.operation == Operation::BEGIN) {
        const auto init = bus_.begin();
        report_.bus_status = init.status;
        report_.cleanup = init.cleanup;
        if (init.status != BusStatus::OK) return fail(SetupFault::TRANSPORT);
        if (!init.ready || init.cleanup != BusCleanup::NOT_ATTEMPTED) return fail(SetupFault::RESPONSE);
        ++step_;
        return report_;
    }
    const auto transfer = step.operation == Operation::READ ? bus_.readRegister(step.reg) :
        step.operation == Operation::WRITE ? bus_.writeRegister(step.reg, step.value) : bus_.readMotion();
    const std::uint8_t count = step.operation == Operation::WRITE ? 0U :
        step.operation == Operation::READ ? 1U : 15U;
    if (!acceptTransfer(transfer, count, now_us)) return report_;
    if (step.operation == Operation::READ && transfer.bytes[0] != step.value)
        return fail(step.reg == Register::IDENTITY ? SetupFault::IDENTITY : SetupFault::READBACK);
    if (step.operation == Operation::MOTION && (transfer.bytes[0] & 0xFEU) != 0U)
        return fail(SetupFault::STATUS);
    if (step.starts_wait) wait_started_us_ = transfer.completed_us;
    ++step_;
    if (step.operation == Operation::MOTION) report_.state = SetupState::PROFILE_READY;
    return report_;
}

CoherentMotion decodeMotion(const BusTransfer& transfer) {
    CoherentMotion result{};
    if (!profileValid() || !transferBoundValid()) { result.status = DecodeStatus::INVALID_CONFIG; return result; }
    if (transfer.status != BusStatus::OK) { result.status = DecodeStatus::TRANSPORT; return result; }
    if (!responseShape(transfer, 15U) ||
        transfer.completed_us - transfer.started_us >= config::IMU_I2C_TRANSFER_US) return result;
    if ((transfer.bytes[0] & 0xFEU) != 0U) { result.status = DecodeStatus::STATUS; return result; }
    for (std::uint8_t axis = 0U; axis < 3U; ++axis) {
        result.accel_raw[axis] = signedWord(&transfer.bytes[1U + 2U * axis]);
        result.gyro_raw[axis] = signedWord(&transfer.bytes[9U + 2U * axis]);
        result.accel_g[axis] = static_cast<float>(result.accel_raw[axis]) / 4096.0F;
        result.gyro_dps[axis] = static_cast<float>(result.gyro_raw[axis]) / 32.8F;
        if (rail(result.accel_raw[axis])) result.rail_mask |= 1U << axis;
        if (rail(result.gyro_raw[axis])) result.rail_mask |= 1U << (axis + 4U);
    }
    result.temperature_raw = signedWord(&transfer.bytes[7]);
    if (rail(result.temperature_raw)) result.rail_mask |= 1U << 3U;
    result.started_us = transfer.started_us;
    result.completed_us = transfer.completed_us;
    result.interrupt_status = transfer.bytes[0];
    result.status = DecodeStatus::OK;
    result.coherent = true;
    return result;
}
} // namespace imu

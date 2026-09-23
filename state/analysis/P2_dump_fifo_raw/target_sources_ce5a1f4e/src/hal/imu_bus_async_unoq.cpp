// Advances a retained native MPU6050 acquisition by one guarded protocol action.
// Caller gaps share the original deadline and private bytes never escape pending.
// Independent installed-register async fixtures and legacy regressions test it.
#include "imu_bus_unoq.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <Arduino.h>
#include <stm32u5xx_ll_i2c.h>

namespace imu {
BusProgress Bus::motionReport() const {
    auto result = async_report_;
    result.started = false;
    result.completed = false;
    return result;
}

BusProgress Bus::beginMotion() {
    if (async_active_) return motionReport();
    if (attempted_ && (faulted_ || !ready_) && async_report_.state == AsyncState::FAULT)
        return motionReport();
    if (!attempted_ || faulted_ || !ready_) {
        async_report_ = {};
        async_report_.state = AsyncState::FAULT;
        async_report_.acquisition.transfer.status = attempted_ ?
            BusStatus::FAULT_LATCHED : BusStatus::NOT_INITIALIZED;
        async_report_.acquisition.transfer.cleanup = cleanup_;
        auto result = async_report_;
        result.completed = true;
        return result;
    }
    async_operation_ = {};
    async_operation_.started_us = static_cast<std::uint32_t>(micros());
    async_operation_.observed_us = async_operation_.started_us;
    async_acquisition_ = {};
    async_staging_ = {};
    async_phase_ = MotionPhase::ADMIT;
    async_count_ = 1U;
    async_index_ = 0U;
    async_active_ = true;
    async_report_ = {};
    async_report_.state = AsyncState::PENDING;
    async_report_.started_us = async_operation_.started_us;
    async_report_.observed_us = async_operation_.observed_us;
    auto result = async_report_;
    result.started = true;
    return result;
}

BusProgress Bus::cancelMotion() {
    return async_active_ ? cancelActiveMotion() : motionReport();
}

BusStatus Bus::motionReady(std::uint32_t wanted, std::uint32_t allowed, bool& ready) {
    ready = false;
    // A missing event consumes one pass; a mutation needs a second fresh pass.
    for (std::uint8_t pass = 0U; pass < 2U; ++pass) {
        std::uint32_t flags = 0U;
        const auto status = observe(async_operation_, allowed, flags);
        if (status != BusStatus::OK) return status;
        if (wanted == I2C_ISR_RXNE && (flags & I2C_ISR_STOPF) != 0U &&
            (flags & I2C_ISR_RXNE) == 0U) {
            async_operation_.error_flags |= I2C_ISR_STOPF;
            return BusStatus::PROTOCOL;
        }
        if ((flags & wanted) == 0U) return BusStatus::OK;
        if ((I2C4_NS->CR2 & I2C_CR2_START) != 0U) return BusStatus::PROTOCOL;
        if (wanted == I2C_ISR_STOPF && (flags & I2C_ISR_BUSY) != 0U) return BusStatus::OK;
    }
    ready = true;
    return BusStatus::OK;
}

BusStatus Bus::startMotionPhase() {
    if (async_phase_ == MotionPhase::MOTION_START) {
        async_acquisition_.motion_attempted = true;
        async_acquisition_.motion_started_us = static_cast<std::uint32_t>(micros());
        async_count_ = 15U;
        async_index_ = 0U;
        async_staging_ = {};
    }
    auto status = admitRequest(async_operation_, true);
    if (status != BusStatus::OK) return status;
    std::uint32_t flags = 0U;
    status = observe(async_operation_, 0U, flags);
    if (status != BusStatus::OK) return status;
    if ((I2C4_NS->CR2 & I2C_CR2_START) != 0U) return BusStatus::PROTOCOL;
    cr2_expected_ = (config::IMU_I2C_ADDRESS << 1U) | (1U << I2C_CR2_NBYTES_Pos);
    LL_I2C_HandleTransfer(I2C4_NS, config::IMU_I2C_ADDRESS << 1U, LL_I2C_ADDRSLAVE_7BIT,
        1U, LL_I2C_MODE_SOFTEND, LL_I2C_GENERATE_START_WRITE);
    if (!controlsOwned()) return BusStatus::READBACK;
    async_phase_ = MotionPhase::POINTER;
    return BusStatus::OK;
}

BusStatus Bus::restartMotionPhase() {
    bool ready = false;
    auto status = motionReady(I2C_ISR_TC, I2C_ISR_TC, ready);
    if (status != BusStatus::OK || !ready) return status;
    // launch's third guard must also observe TC now, not trust the earlier flag.
    std::uint32_t flags = 0U;
    status = observe(async_operation_, I2C_ISR_TC, flags);
    if (status != BusStatus::OK) return status;
    if ((flags & I2C_ISR_TC) == 0U) return BusStatus::OK;
    if ((I2C4_NS->CR2 & I2C_CR2_START) != 0U) return BusStatus::PROTOCOL;
    cr2_expected_ = (config::IMU_I2C_ADDRESS << 1U) |
        (static_cast<std::uint32_t>(async_count_) << I2C_CR2_NBYTES_Pos) |
        I2C_CR2_RD_WRN | I2C_CR2_AUTOEND;
    LL_I2C_HandleTransfer(I2C4_NS, config::IMU_I2C_ADDRESS << 1U, LL_I2C_ADDRSLAVE_7BIT,
        async_count_, LL_I2C_MODE_AUTOEND, LL_I2C_GENERATE_START_READ);
    if (!controlsOwned()) return BusStatus::READBACK;
    async_phase_ = MotionPhase::RECEIVE;
    return BusStatus::OK;
}

BusStatus Bus::receiveMotionByte() {
    const auto allowed = I2C_ISR_RXNE | (async_index_ + 1U == async_count_ ? I2C_ISR_STOPF : 0U);
    bool ready = false;
    const auto status = motionReady(I2C_ISR_RXNE, allowed, ready);
    if (status != BusStatus::OK || !ready) return status;
    async_staging_.bytes[async_index_] = LL_I2C_ReceiveData8(I2C4_NS);
    ++async_index_;
    if (async_index_ == async_count_) async_phase_ = MotionPhase::STOP;
    return BusStatus::OK;
}

BusStatus Bus::stopMotionPhase() {
    bool ready = false;
    const auto status = motionReady(I2C_ISR_STOPF, I2C_ISR_STOPF, ready);
    if (status != BusStatus::OK || !ready) return status;
    LL_I2C_ClearFlag_STOP(I2C4_NS);
    async_phase_ = MotionPhase::FINISH;
    return BusStatus::OK;
}

BusStatus Bus::acceptMotionPhase() {
    // These are D079's final checks, separated from its STOPCF action.
    std::uint32_t flags = 0U;
    auto status = observe(async_operation_, 0U, flags);
    if (status != BusStatus::OK) return status;
    if ((flags & I2C_ISR_BUSY) != 0U) return BusStatus::PROTOCOL;
    async_operation_.observed_us = static_cast<std::uint32_t>(micros());
    if (!ownershipValid()) return BusStatus::OWNERSHIP;
    flags = I2C4_NS->ISR;
    status = checkFlags(async_operation_, 0U, flags);
    if (status != BusStatus::OK) return status;
    if ((flags & I2C_ISR_BUSY) != 0U) return BusStatus::PROTOCOL;
    async_operation_.observed_us = static_cast<std::uint32_t>(micros());
    return async_operation_.observed_us - async_operation_.started_us >= config::IMU_I2C_TRANSFER_US ?
        BusStatus::TIMEOUT : BusStatus::OK;
}

BusStatus Bus::finishMotionPhase() {
    const auto status = acceptMotionPhase();
    if (status != BusStatus::OK) return status;
    if (async_count_ == 1U) {
        async_acquisition_.readiness_observed = true;
        async_acquisition_.readiness_status = async_staging_.bytes[0];
        async_acquisition_.readiness_completed_us = async_operation_.observed_us;
        if ((async_acquisition_.readiness_status & 0xFEU) != 0U) return BusStatus::PROTOCOL;
        if (async_acquisition_.readiness_status != 0U) {
            async_phase_ = MotionPhase::MOTION_START;
            return BusStatus::OK;
        }
        async_acquisition_.state = AcquisitionState::NO_NEW;
        async_staging_ = {};
    } else {
        async_acquisition_.motion_status_observed = true;
        async_acquisition_.motion_status = async_staging_.bytes[0];
        if ((async_acquisition_.motion_status & 0xFEU) != 0U) return BusStatus::PROTOCOL;
        async_acquisition_.state = AcquisitionState::OBSERVATION;
        async_staging_.count = 15U;
    }
    async_staging_.status = BusStatus::OK;
    async_staging_.started_us = async_operation_.started_us;
    async_staging_.completed_us = async_operation_.observed_us;
    async_staging_.complete = true;
    async_acquisition_.transfer = async_staging_;
    async_active_ = false;
    return BusStatus::OK;
}

BusProgress Bus::advanceMotion() {
    if (!async_active_) return motionReport();
    auto status = BusStatus::OK;
    switch (async_phase_) {
    case MotionPhase::ADMIT: case MotionPhase::MOTION_START:
        status = startMotionPhase(); break;
    case MotionPhase::POINTER: {
        bool ready = false;
        status = motionReady(I2C_ISR_TXIS, I2C_ISR_TXIS, ready);
        if (status == BusStatus::OK && ready) {
            LL_I2C_TransmitData8(I2C4_NS, static_cast<std::uint8_t>(Register::INTERRUPT_STATUS));
            async_phase_ = MotionPhase::RESTART;
        }
        break;
    }
    case MotionPhase::RESTART: status = restartMotionPhase(); break;
    case MotionPhase::RECEIVE: status = receiveMotionByte(); break;
    case MotionPhase::STOP: status = stopMotionPhase(); break;
    case MotionPhase::FINISH: status = finishMotionPhase(); break;
    }
    if (status != BusStatus::OK || !async_active_) return endMotion(status);
    async_report_.observed_us = async_operation_.observed_us;
    async_report_.polls = async_operation_.polls;
    return motionReport();
}
} // namespace imu
#endif

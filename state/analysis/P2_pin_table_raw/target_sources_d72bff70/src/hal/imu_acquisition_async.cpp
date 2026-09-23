// Advances the owned MPU6050 acquisition without turning pending work into samples.
// Preserves the original deadline, caller chronology and observed-silence lifetime.
// Independent scripted-Bus tests exercise progress, cancellation and legacy collisions.
#include "imu_acquisition.h"
#include "../config.h"

namespace imu {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool emptyAcquisition(const BusAcquisition& acquisition) {
    const auto& transfer = acquisition.transfer;
    if (acquisition.state != AcquisitionState::FAULT ||
        transfer.status != BusStatus::NOT_INITIALIZED ||
        transfer.cleanup != BusCleanup::NOT_ATTEMPTED || transfer.count != 0U ||
        transfer.started_us != 0U || transfer.completed_us != 0U ||
        transfer.error_flags != 0U || transfer.complete) return false;
    for (const auto byte : transfer.bytes) if (byte != 0U) return false;
    return acquisition.readiness_status == 0U && !acquisition.readiness_observed &&
        acquisition.readiness_completed_us == 0U && !acquisition.motion_attempted &&
        acquisition.motion_started_us == 0U && !acquisition.motion_status_observed &&
        acquisition.motion_status == 0U;
}
} // namespace

SampleProgress Acquirer::readProgress() const {
    auto report = async_report_;
    report.started = false;
    report.completed = false;
    return report;
}

SampleProgress Acquirer::finishRead() {
    async_active_ = false;
    async_report_ = SampleProgress{};
    async_report_.state = faulted_ ? AsyncState::FAULT : AsyncState::COMPLETE;
    async_report_.sample = result_;
    auto report = async_report_;
    report.completed = true;
    return report;
}

SampleProgress Acquirer::abortRead(SampleFault fault) {
    const auto cancelled = bus_.cancelMotion();
    // A native terminal success needs no cleanup; keep that reply's diagnostics.
    if (cancelled.completed) {
        result_.bus_status = cancelled.acquisition.transfer.status;
        result_.cleanup = cancelled.acquisition.transfer.cleanup;
        result_.error_flags = cancelled.acquisition.transfer.error_flags;
    }
    fail(fault, latest_us_);
    return finishRead();
}

bool Acquirer::acceptProgress(const BusProgress& progress, std::uint32_t call_us) {
    if (progress.started_us != async_started_us_ || progress.polls <= async_polls_ ||
        progress.polls > config::IMU_I2C_MAX_POLLS) {
        fail(SampleFault::RESPONSE, latest_us_);
        return false;
    }
    if (progress.observed_us - call_us >= HALF_RANGE ||
        progress.observed_us - async_observed_us_ >= HALF_RANGE) {
        fail(SampleFault::TIME_ORDER, latest_us_);
        return false;
    }
    if (progress.observed_us - async_started_us_ >= config::IMU_I2C_TRANSFER_US) {
        fail(SampleFault::RESPONSE, latest_us_);
        return false;
    }
    return true;
}

SampleProgress Acquirer::beginRead(std::uint32_t now_us) {
    if (async_active_) return readProgress();
    if (faulted_) {
        async_report_.state = AsyncState::FAULT;
        async_report_.sample = result_;
        return readProgress();
    }
    if (!armed_) return SampleProgress{};
    result_ = Sample{};
    result_.sequence = sequence_;
    result_.checked_us = latest_us_;
    if (config::IMU_SILENCE_US == 0U || config::IMU_SILENCE_US >= HALF_RANGE) {
        fail(SampleFault::INVALID_CONFIG, latest_us_);
        return finishRead();
    }
    if (!acceptTime(now_us)) return finishRead();
    async_call_us_ = now_us;
    const auto progress = bus_.beginMotion();
    async_active_ = true;
    if (progress.state != AsyncState::PENDING) {
        if (progress.state != AsyncState::COMPLETE && progress.state != AsyncState::FAULT)
            return abortRead(SampleFault::RESPONSE);
        result_.bus_status = progress.acquisition.transfer.status;
        result_.cleanup = progress.acquisition.transfer.cleanup;
        result_.error_flags = progress.acquisition.transfer.error_flags;
        if (result_.bus_status != BusStatus::OK) {
            fail(SampleFault::TRANSPORT, latest_us_);
            return finishRead();
        }
    }
    if (progress.state != AsyncState::PENDING || !progress.started || progress.completed ||
        progress.polls != 0U || progress.started_us != progress.observed_us ||
        !emptyAcquisition(progress.acquisition)) return abortRead(SampleFault::RESPONSE);
    if (progress.observed_us - now_us >= HALF_RANGE) return abortRead(SampleFault::TIME_ORDER);
    if (!acceptTime(progress.observed_us)) return abortRead(result_.fault);
    async_started_us_ = progress.started_us;
    async_observed_us_ = progress.observed_us;
    async_polls_ = 0U;
    async_report_ = SampleProgress{};
    async_report_.state = AsyncState::PENDING;
    auto report = async_report_;
    report.started = true;
    return report;
}

SampleProgress Acquirer::advanceRead(std::uint32_t now_us) {
    if (!async_active_) return readProgress();
    if (!acceptTime(now_us)) return abortRead(result_.fault);
    const auto progress = bus_.advanceMotion();
    if (progress.state == AsyncState::PENDING) {
        if (progress.started || progress.completed || !emptyAcquisition(progress.acquisition))
            return abortRead(SampleFault::RESPONSE);
        if (!acceptProgress(progress, now_us)) return abortRead(result_.fault);
        if (!acceptTime(progress.observed_us)) return abortRead(result_.fault);
        async_observed_us_ = progress.observed_us;
        async_polls_ = progress.polls;
        return readProgress();
    }
    if (progress.state != AsyncState::COMPLETE && progress.state != AsyncState::FAULT)
        return abortRead(SampleFault::RESPONSE);
    const auto& transfer = progress.acquisition.transfer;
    result_.bus_status = transfer.status;
    result_.cleanup = transfer.cleanup;
    result_.error_flags = transfer.error_flags;
    if (transfer.status != BusStatus::OK) {
        fail(SampleFault::TRANSPORT, latest_us_);
        return finishRead();
    }
    if (progress.state != AsyncState::COMPLETE || progress.started || !progress.completed ||
        progress.started_us != async_started_us_ || progress.polls <= async_polls_ ||
        progress.polls > config::IMU_I2C_MAX_POLLS ||
        progress.observed_us != transfer.completed_us ||
        transfer.started_us != async_started_us_) return abortRead(SampleFault::RESPONSE);
    // D081 shape/phase precedence stays ahead of final caller-time acceptance.
    if (!acceptAcquisition(progress.acquisition, async_call_us_)) return abortRead(result_.fault);
    publishAcquisition(progress.acquisition);
    if (faulted_) return abortRead(result_.fault);
    return finishRead();
}

SampleProgress Acquirer::cancelRead(std::uint32_t now_us) {
    if (!async_active_) return readProgress();
    if (!acceptTime(now_us)) return abortRead(result_.fault);
    return abortRead(SampleFault::TRANSPORT);
}
} // namespace imu

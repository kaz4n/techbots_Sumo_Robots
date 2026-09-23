// Owns checked sensor setup and qualifies finite status/STOP/motion observations.
// No-new results carry no old motion, and observed silence terminally faults.
// Independent scripted-Bus and native tests plus an inert target probe check it.
#include "imu_acquisition.h"
#include "../config.h"

namespace imu {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool shapeValid(const BusAcquisition& acquisition) {
    const auto& transfer = acquisition.transfer;
    const bool no_new = acquisition.state == AcquisitionState::NO_NEW;
    if (!no_new && acquisition.state != AcquisitionState::OBSERVATION) return false;
    if (!transfer.complete || transfer.error_flags != 0U ||
        transfer.cleanup != BusCleanup::NOT_ATTEMPTED ||
        transfer.count != (no_new ? 0U : 15U)) return false;
    if (no_new) {
        for (const auto byte : transfer.bytes) if (byte != 0U) return false;
    }
    return true;
}

bool phasesValid(const BusAcquisition& acquisition) {
    const auto& transfer = acquisition.transfer;
    const auto duration = transfer.completed_us - transfer.started_us;
    const auto readiness = acquisition.readiness_completed_us - transfer.started_us;
    if (!acquisition.readiness_observed || readiness > duration) return false;
    if (acquisition.state == AcquisitionState::NO_NEW) {
        return acquisition.readiness_status == 0U && readiness == duration &&
            !acquisition.motion_attempted && acquisition.motion_started_us == 0U &&
            !acquisition.motion_status_observed && acquisition.motion_status == 0U;
    }
    const auto motion = acquisition.motion_started_us - transfer.started_us;
    return acquisition.readiness_status == 1U && acquisition.motion_attempted &&
        readiness <= motion && motion <= duration && acquisition.motion_status_observed &&
        acquisition.motion_status == transfer.bytes[0];
}
} // namespace

Sample Acquirer::fail(SampleFault fault, std::uint32_t observed_us) {
    Sample failed{};
    failed.state = SampleState::FAULT;
    failed.fault = fault;
    failed.bus_status = result_.bus_status;
    failed.cleanup = result_.cleanup;
    failed.error_flags = result_.error_flags;
    failed.sequence = sequence_;
    failed.checked_us = observed_us;
    result_ = failed;
    faulted_ = true;
    return result_;
}

SetupReport Acquirer::start(std::uint32_t now_us, bool power_confirmed) {
    const auto report = setup_.start(now_us, power_confirmed);
    if (faulted_) return report;
    if (report.state == SetupState::FAULT) {
        result_.bus_status = report.bus_status;
        result_.cleanup = report.cleanup;
        result_.error_flags = report.error_flags;
        fail(SampleFault::SETUP, report.observed_us);
    } else if (!armed_ && report.state == SetupState::PROFILE_READY) {
        armed_ = true;
        latest_us_ = report.observed_us;
        last_observation_us_ = report.observed_us;
    }
    return report;
}

SetupReport Acquirer::advanceSetup(std::uint32_t now_us) {
    const auto report = setup_.advance(now_us);
    if (faulted_) return report;
    if (report.state == SetupState::FAULT) {
        result_.bus_status = report.bus_status;
        result_.cleanup = report.cleanup;
        result_.error_flags = report.error_flags;
        fail(SampleFault::SETUP, report.observed_us);
    } else if (!armed_ && report.state == SetupState::PROFILE_READY) {
        armed_ = true;
        latest_us_ = report.observed_us;
        last_observation_us_ = report.observed_us;
    }
    return report;
}

bool Acquirer::acceptTime(std::uint32_t now_us) {
    if (now_us - latest_us_ >= HALF_RANGE) {
        fail(SampleFault::TIME_ORDER, latest_us_);
        return false;
    }
    latest_us_ = now_us;
    result_.checked_us = now_us;
    if (now_us - last_observation_us_ >= config::IMU_SILENCE_US) {
        fail(SampleFault::SILENCE, now_us);
        return false;
    }
    return true;
}

bool Acquirer::acceptAcquisition(const BusAcquisition& acquisition, std::uint32_t call_us) {
    const auto& transfer = acquisition.transfer;
    result_.bus_status = transfer.status;
    result_.cleanup = transfer.cleanup;
    result_.error_flags = transfer.error_flags;
    if (transfer.status != BusStatus::OK) { fail(SampleFault::TRANSPORT, latest_us_); return false; }
    if (!shapeValid(acquisition)) { fail(SampleFault::RESPONSE, latest_us_); return false; }
    if (transfer.started_us - call_us >= HALF_RANGE ||
        transfer.completed_us - transfer.started_us >= HALF_RANGE) {
        fail(SampleFault::TIME_ORDER, latest_us_);
        return false;
    }
    if (transfer.completed_us - transfer.started_us >= config::IMU_I2C_TRANSFER_US ||
        !phasesValid(acquisition)) {
        fail(SampleFault::RESPONSE, latest_us_);
        return false;
    }
    return acceptTime(transfer.completed_us);
}

Sample Acquirer::read(std::uint32_t now_us) {
    if (async_active_) {
        // The existing Bus path owns collision cleanup, including legacy-only builds.
        const auto acquisition = bus_.acquireMotion();
        result_.bus_status = acquisition.transfer.status;
        result_.cleanup = acquisition.transfer.cleanup;
        result_.error_flags = acquisition.transfer.error_flags;
        fail(SampleFault::TRANSPORT, latest_us_);
        async_active_ = false;
        async_report_ = SampleProgress{};
        async_report_.state = AsyncState::FAULT;
        async_report_.sample = result_;
        return result_;
    }
    if (faulted_) return result_;
    if (!armed_) return Sample{};
    result_ = Sample{};
    result_.sequence = sequence_;
    result_.checked_us = latest_us_;
    if (config::IMU_SILENCE_US == 0U || config::IMU_SILENCE_US >= HALF_RANGE)
        return fail(SampleFault::INVALID_CONFIG, latest_us_);
    if (!acceptTime(now_us)) return result_;
    const auto acquisition = bus_.acquireMotion();
    if (!acceptAcquisition(acquisition, now_us)) return result_;
    return publishAcquisition(acquisition);
}

Sample Acquirer::publishAcquisition(const BusAcquisition& acquisition) {
    if (acquisition.state == AcquisitionState::NO_NEW) {
        result_.state = SampleState::NO_NEW;
        result_.readiness_completed_us = acquisition.readiness_completed_us;
        return result_;
    }
    const auto motion = decodeMotion(acquisition.transfer);
    if (motion.status != DecodeStatus::OK || !motion.coherent)
        return fail(SampleFault::RESPONSE, latest_us_);
    result_.state = SampleState::OBSERVATION;
    result_.motion = motion;
    result_.sequence = ++sequence_;
    result_.readiness_completed_us = acquisition.readiness_completed_us;
    result_.motion_started_us = acquisition.motion_started_us;
    result_.had_previous_observation = have_observation_;
    result_.observation_gap_us = have_observation_ ? latest_us_ - last_observation_us_ : 0U;
    last_observation_us_ = latest_us_;
    have_observation_ = true;
    return result_;
}
} // namespace imu

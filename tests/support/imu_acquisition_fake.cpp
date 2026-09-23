// Defines the runtime-only concrete Bus method for independent D081 tests.
// Keeps all responses and the literal setup recipe outside production source.
// Linked only by host tests and guarded configuration-variant executables.
#include "imu_acquisition_fake.h"
#include "config.h"

namespace imu_acq_fake {
Script script{};
void reset() { script = Script{}; imu_fake::reset(); }

void seedSetup() {
    // Literal D080 48-operation response sequence, including discarded motion.
    const std::uint8_t pairs[][2] = {
        {0,0},{1,0x68},{0,0x80},{1,0x40},{1,0x68},
        {1,0},{1,0},{1,0},{1,0},{1,0},{1,0},{1,0},{1,0},{1,0},
        {0,0},{1,0},{0,0},{1,0},{0,1},{1,1},
        {0,0},{1,0},{0,0},{1,0},{0,0},{1,0},{0,1},{1,1},
        {0,0},{1,0},{0,0x10},{1,0x10},{0,0x10},{1,0x10},{0,1},{1,1},
        {1,0x68},{1,1},{1,0},{1,0},{1,0},{1,1},{1,0},{1,0x10},
        {1,0x10},{1,0},{1,1},{15,1}
    };
    static_assert(sizeof(pairs) / sizeof(pairs[0]) == 48U);
    for (unsigned index = 0U; index < 48U; ++index) {
        auto& reply = imu_fake::script.replies[index];
        reply.start_offset_us = 0U;
        reply.duration_us = 0U;
        reply.transfer.status = imu::BusStatus::OK;
        reply.transfer.complete = true;
        reply.transfer.count = pairs[index][0];
        reply.transfer.bytes[0] = pairs[index][1];
    }
}

std::uint32_t setupTime(unsigned index, std::uint32_t start, std::uint32_t last) {
    switch (index) {
    case 0U: return start + config::IMU_POWER_WAIT_US;
    case 3U: return last + config::IMU_RESET_WAIT_US;
    case 18U: return last + config::IMU_GYRO_WAIT_US;
    case 20U: return last + config::IMU_PLL_WAIT_US;
    case 36U: return last + config::IMU_FILTER_WAIT_US;
    default: return last;
    }
}

imu::BusAcquisition observation(std::uint32_t start, std::uint32_t duration) {
    imu::BusAcquisition result{};
    result.state = imu::AcquisitionState::OBSERVATION;
    result.transfer.status = imu::BusStatus::OK;
    result.transfer.complete = true;
    result.transfer.count = 15U;
    result.transfer.started_us = start;
    result.transfer.completed_us = start + duration;
    result.readiness_observed = true;
    result.readiness_status = 1U;
    result.readiness_completed_us = start + duration / 3U;
    result.motion_attempted = true;
    result.motion_started_us = start + duration / 2U;
    result.motion_status_observed = true;
    result.motion_status = 0U;
    for (unsigned i = 1U; i < 15U; ++i)
        result.transfer.bytes[i] = static_cast<std::uint8_t>(i * 13U);
    return result;
}

imu::BusAcquisition noNew(std::uint32_t start, std::uint32_t duration) {
    imu::BusAcquisition result{};
    result.state = imu::AcquisitionState::NO_NEW;
    result.transfer.status = imu::BusStatus::OK;
    result.transfer.complete = true;
    result.transfer.started_us = start;
    result.transfer.completed_us = start + duration;
    result.readiness_observed = true;
    result.readiness_completed_us = result.transfer.completed_us;
    return result;
}
} // namespace imu_acq_fake

namespace imu {
BusAcquisition Bus::acquireMotion() {
    ++imu_acq_fake::script.calls;
    return imu_acq_fake::script.reply;
}
} // namespace imu

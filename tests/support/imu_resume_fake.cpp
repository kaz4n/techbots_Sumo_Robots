// Defines only resumable Bus entries for independent D094 host tests.
// Existing D080/D081 Bus definitions and their test scripts remain unchanged.
// Actual Acquirer and Setup receive explicitly authored progress and fault data.
#include "imu_resume_fake.h"

namespace imu_resume_fake {
Script script{};
void reset() { script = Script{}; imu_acq_fake::reset(); }
imu::BusProgress pending(std::uint32_t start, std::uint32_t now,
                         std::uint32_t polls, bool beginning) {
    imu::BusProgress p{};
    p.state = imu::AsyncState::PENDING; p.started = beginning;
    p.started_us = start; p.observed_us = now; p.polls = polls;
    return p;
}
imu::BusProgress complete(std::uint32_t start, std::uint32_t duration,
                          bool observation, std::uint32_t polls) {
    imu::BusProgress p{};
    p.state = imu::AsyncState::COMPLETE; p.completed = true;
    p.started_us = start; p.observed_us = start + duration; p.polls = polls;
    p.acquisition = observation ? imu_acq_fake::observation(start, duration) :
                                 imu_acq_fake::noNew(start, duration);
    return p;
}
imu::BusProgress cancelled(std::uint32_t start, std::uint32_t now, bool newly) {
    imu::BusProgress p{};
    p.state = imu::AsyncState::FAULT; p.completed = newly;
    p.started_us = start; p.observed_us = now; p.polls = 9U;
    p.acquisition.transfer.status = imu::BusStatus::CANCELLED;
    p.acquisition.transfer.cleanup = imu::BusCleanup::DISABLED;
    p.acquisition.transfer.started_us = start;
    p.acquisition.transfer.completed_us = now;
    p.acquisition.transfer.error_flags = 0x100U;
    return p;
}
} // namespace imu_resume_fake
namespace imu {
BusProgress Bus::beginMotion() { ++imu_resume_fake::script.begins; return imu_resume_fake::script.begin; }
BusProgress Bus::advanceMotion() { ++imu_resume_fake::script.advances; return imu_resume_fake::script.advance; }
BusProgress Bus::cancelMotion() { ++imu_resume_fake::script.cancels; return imu_resume_fake::script.cancel; }
BusProgress Bus::motionReport() const { ++imu_resume_fake::script.reports; return imu_resume_fake::script.report; }
} // namespace imu

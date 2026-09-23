// Scripts only D094's additive Bus methods without replacing established fakes.
// Separates each caller-controlled progress reply and cancellation observation.
// Independent Acquirer tests derive replies from the frozen public contract.
#pragma once
#include "imu_acquisition_fake.h"

namespace imu_resume_fake {
struct Script {
    imu::BusProgress begin{}, advance{}, cancel{}, report{};
    unsigned begins = 0U, advances = 0U, cancels = 0U, reports = 0U;
};
extern Script script;
void reset();
imu::BusProgress pending(std::uint32_t start, std::uint32_t now,
                         std::uint32_t polls, bool beginning = false);
imu::BusProgress complete(std::uint32_t start, std::uint32_t duration,
                          bool observation = true, std::uint32_t polls = 40U);
imu::BusProgress cancelled(std::uint32_t start, std::uint32_t now,
                           bool newly = true);
} // namespace imu_resume_fake

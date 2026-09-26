// Declares fixed diagnostic observations of the native settle return branches.
// Keeps the first failure across later cleanup without adding hardware reads.
// Independent native-fixture tests verify reasons, layout and call preservation.
#pragma once
#include "../config.h"

#if SUMOX_MOTOR_FAULT_PROBE == 1
#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace motors {
enum class SettleProbeReason : std::uint8_t {
    NONE = 0, SUCCESS = 1, NULL_CONTEXT = 2, PRECONDITION = 3,
    INITIAL_BANK = 4, POLL_DEADLINE = 5, POLL_BANK = 6,
    FINAL_DEADLINE = 7, POLL_LIMIT = 8
};
inline constexpr std::uint8_t SETTLE_ELAPSED_VALID = 1U;
inline constexpr std::uint8_t SETTLE_POLL_VALID = 2U;
inline constexpr std::uint8_t SETTLE_FRESH_VALID = 4U;
struct SettleProbeSample {
    std::uint32_t elapsed_us = 0U;
    std::uint32_t poll_index = 0U;
    SettleProbeReason reason = SettleProbeReason::NONE;
    std::uint8_t fresh_mask = 0U;
    std::uint8_t valid = 0U;
    std::uint8_t reserved = 0U;
};
struct SettleProbeReport {
    SettleProbeSample current{};
    SettleProbeSample first_failure{};
    std::uint8_t has_current = 0U;
    std::uint8_t has_failure = 0U;
    std::uint8_t reserved[2] = {};
};
static_assert(std::is_standard_layout<SettleProbeSample>::value &&
              sizeof(SettleProbeSample) == 12U && alignof(SettleProbeSample) == 4U);
static_assert(offsetof(SettleProbeSample, elapsed_us) == 0U &&
              offsetof(SettleProbeSample, poll_index) == 4U &&
              offsetof(SettleProbeSample, reason) == 8U &&
              offsetof(SettleProbeSample, fresh_mask) == 9U &&
              offsetof(SettleProbeSample, valid) == 10U &&
              offsetof(SettleProbeSample, reserved) == 11U);
static_assert(std::is_standard_layout<SettleProbeReport>::value &&
              sizeof(SettleProbeReport) == 28U && alignof(SettleProbeReport) == 4U);
static_assert(offsetof(SettleProbeReport, current) == 0U &&
              offsetof(SettleProbeReport, first_failure) == 12U &&
              offsetof(SettleProbeReport, has_current) == 24U &&
              offsetof(SettleProbeReport, has_failure) == 25U &&
              offsetof(SettleProbeReport, reserved) == 26U);

// Reports completed calls; reading never clears the lifetime first failure.
const SettleProbeReport& settleProbeReport();
} // namespace motors
#endif

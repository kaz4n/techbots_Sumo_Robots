// Counts each admitted S..C duration in a fixed exact-microsecond histogram.
// Exposes lifetime-prefix p99 without confusing it with full-loop WCET.
// D229 focused distribution and actual Runtime tests verify boundary semantics.
#pragma once
#include "../config.h"
#include <cstdint>
#include <limits>

namespace app::epoch_timing {
static_assert(config::TICK_DISTRIBUTION_LIMIT_US > 0U &&
              config::TICK_DISTRIBUTION_LIMIT_US <= 800U,
              "Diagnostic histogram must remain within its bounded RAM budget");
enum class Status : std::uint8_t { EMPTY, EXACT, RANGE_OVERFLOW, SATURATED, INCONSISTENT };
struct Data {
    std::uint32_t bins[config::TICK_DISTRIBUTION_LIMIT_US]{};
    std::uint32_t samples = 0U;
    std::uint32_t overflow = 0U;
    std::uint32_t rejected = 0U; // UINT32_MAX is a lower bound.
    std::uint32_t retained_maximum_us = 0U;
    std::uint32_t maximum_us = 0U; // Includes observations rejected after saturation.
    std::uint32_t first_started_us = 0U;
    std::uint32_t retained_completed_us = 0U;
    std::uint32_t last_completed_us = 0U;
    bool saturated = false;
};
struct Summary {
    Status status = Status::EMPTY;
    Status retained_status = Status::EMPTY;
    std::uint32_t samples = 0U;
    std::uint32_t overflow = 0U;
    std::uint32_t rejected = 0U;
    std::uint32_t rank = 0U;
    std::uint32_t p99_us = 0U; // Valid only when retained_status == EXACT.
    std::uint32_t retained_maximum_us = 0U;
    std::uint32_t maximum_us = 0U;
    std::uint32_t first_started_us = 0U;
    std::uint32_t retained_completed_us = 0U;
    std::uint32_t last_completed_us = 0U;
};
class Distribution {
public:
    void observe(std::uint32_t execution_us, std::uint32_t started_us,
                 std::uint32_t completed_us) {
        if (execution_us > data_.maximum_us) data_.maximum_us = execution_us;
        data_.last_completed_us = completed_us;
        if (data_.samples == std::numeric_limits<std::uint32_t>::max()) {
            data_.saturated = true;
            if (data_.rejected != std::numeric_limits<std::uint32_t>::max()) ++data_.rejected;
            return;
        }
        if (data_.samples == 0U) data_.first_started_us = started_us;
        ++data_.samples;
        if (execution_us < config::TICK_DISTRIBUTION_LIMIT_US) ++data_.bins[execution_us];
        else ++data_.overflow;
        if (execution_us > data_.retained_maximum_us) data_.retained_maximum_us = execution_us;
        data_.retained_completed_us = completed_us;
    }
    const Data& data() const { return data_; }
    // Call outside the measured epoch. A live concurrent read is not an atomic snapshot.
    Summary summary() const {
        Summary result;
        result.samples = data_.samples;
        result.overflow = data_.overflow;
        result.rejected = data_.rejected;
        result.rank = data_.samples - data_.samples / 100U;
        result.retained_maximum_us = data_.retained_maximum_us;
        result.maximum_us = data_.maximum_us;
        result.first_started_us = data_.first_started_us;
        result.retained_completed_us = data_.retained_completed_us;
        result.last_completed_us = data_.last_completed_us;
        result.retained_status = data_.samples == 0U ? Status::EMPTY : Status::RANGE_OVERFLOW;
        std::uint64_t cumulative = 0U;
        for (std::uint32_t us = 0U; us < config::TICK_DISTRIBUTION_LIMIT_US; ++us) {
            cumulative += data_.bins[us];
            if (result.retained_status == Status::RANGE_OVERFLOW && cumulative >= result.rank) {
                result.retained_status = Status::EXACT;
                result.p99_us = us;
            }
        }
        if (cumulative + data_.overflow != data_.samples) {
            result.retained_status = Status::INCONSISTENT;
            result.status = Status::INCONSISTENT;
        } else result.status = data_.saturated ? Status::SATURATED : result.retained_status;
        return result;
    }
private:
    Data data_;
};
} // namespace app::epoch_timing

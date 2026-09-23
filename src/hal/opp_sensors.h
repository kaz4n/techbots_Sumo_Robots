// Captures seven electrical opponent inputs with explicit native API failures.
// Prevents an unreadable active-low input from becoming a fabricated detection.
// Independent native-API substitutes test all masks; target probe never executes I/O.
#pragma once
#include <cstdint>

namespace opp_sensors {
struct InitResult {
    bool ready = false;
    std::uint8_t configured_mask = 0;
    std::int32_t status[7] = {};
};
struct Snapshot {
    bool valid = false;
    std::uint8_t raw_mask = 0;
    std::uint8_t valid_mask = 0;
    std::int32_t status[7] = {};
    std::uint32_t started_us = 0;
    std::uint32_t completed_us = 0;
};
class Sensors {
public:
    // Setup-only; caller retains exclusive pad ownership until reinitialization.
    InitResult begin();
    // Partial/failed snapshots must never be forwarded as fresh Robot inputs.
    Snapshot read() const;
private:
    bool ready_ = false;
};
} // namespace opp_sensors

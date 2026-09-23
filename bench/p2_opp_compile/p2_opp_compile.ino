// Publishes a never-called native opponent-driver probe for MCU compile checks.
// Keeps proposed input pins unconfigured while physical acceptance is pending.
// Host callback counters and target ELF inspection verify inert setup and loop.
#include "src/config.h"
#include "src/opponent_probe.h"
static_assert(MOTORS_ALLOWED == 0, "Opponent compatibility probe is bench-only");

namespace opponent_probe {
opp_sensors::Sensors sensors;
Probe volatile address = nullptr;
} // namespace opponent_probe

void setup() {
    opponent_probe::address = &opponent_probe::exercise;
}

void loop() {}

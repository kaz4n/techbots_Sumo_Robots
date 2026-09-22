// Links the production decision layer for the P1 app target-compilation check.
// Keeps this pre-HAL entry inert until P2 supplies verified acquisition and MotorGate.
// Host Robot scenarios and tools/flash.sh app --compile-only validate this stage.
#include "src/config.h"
#include "src/core/fsm.h"

static_assert(MOTORS_ALLOWED == 0, "P1 app has no verified HAL: inert compilation only");

namespace {
fsm::Robot robot;
volatile bool p1_boot_inhibited = true;
}

void setup() {
    // No completed setup, sensor claims or actuator writes: exercise real BOOT entry.
    const auto result = robot.step(fsm::RobotInput{});
    p1_boot_inhibited = !result.outputs.motors_enabled &&
                       result.outputs.duty_l == 0.0F && result.outputs.duty_r == 0.0F;
}

void loop() {
    // The 1kHz acquisition/decision/application scheduler belongs to the P2 HAL work.
}

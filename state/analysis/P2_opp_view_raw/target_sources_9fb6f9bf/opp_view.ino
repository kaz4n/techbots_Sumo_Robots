// Runs the opponent-view controller with every native grant absent by default.
// Prepares P2 B1 software without configuring sensors, matrix or motor pins.
// Default-startup callback tests and exact compile-only artifacts verify D107.
#include "src/config.h"
#include "src/opp_view_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Opponent view is motor-free bench software");

namespace {
opp_view::Native native;
opp_view::Runner runner{native.port()};
}

void setup() { runner.begin(opp_view::Grants{}); }
void loop() { runner.poll(); }

// Checks that the host C++17 and doctest scaffold can execute.
// Provides a P0 build smoke test, not evidence of robot behavior.
// Run through tools/test_host.sh.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "config.h"

TEST_CASE("P0 0.3 host scaffold and B16 defaults are accessible") {
    CHECK(config::COUNTDOWN_MS == 5000U);
    CHECK(config::COUNTDOWN_MARGIN_MS == 100U);
    CHECK(config::TICK_US == 1000U);
    CHECK(MOTORS_ALLOWED == 0);
}

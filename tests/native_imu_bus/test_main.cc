// Provides one reusable doctest entry point for the isolated native test binaries.
// Keeps repeated metadata variants from recompiling the test framework itself.
// Linked only by test_imu_bus_unoq.py, outside the ordinary CMake cpp glob.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"

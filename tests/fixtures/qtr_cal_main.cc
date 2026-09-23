// Supplies the independently built D089 doctest entry point.
// Keeps profile variants separate from the repository-wide test executable.
// The tooling runner compiles actual opaque production units with this main.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"

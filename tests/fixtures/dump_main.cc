// Supplies a standalone strict dump test executable without existing test edits.
// Keeps test-author checks independent from production source inspection.
// Built by scoped tooling; the normal suite also discovers the same test cases.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"

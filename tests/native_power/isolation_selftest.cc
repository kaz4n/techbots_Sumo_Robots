// Deliberately fails child checks and child process termination.
// The runner expects a failing native exit, proving isolation cannot hide failure.
// These sentinel cases never call the production driver or a hardware operation.
#include "doctest.h"
#include "isolation.h"
#include <csignal>
TEST_CASE("B5 isolation child assertion failure sentinel") {
 fixture::isolated([]{CHECK(false);});
}
TEST_CASE("B5 isolation child signal failure sentinel") {
 fixture::isolated([]{raise(SIGKILL);});
}

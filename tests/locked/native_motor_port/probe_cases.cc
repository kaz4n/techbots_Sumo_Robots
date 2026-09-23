// Executes only the inert native probe constructor/setup/loop surface.
// A never-called retained exercise function cannot authorize peripheral activity.
// Both default-disabled and host-only MATCH configurations use identical checks.
#include "doctest.h"
#include "native_fixture.h"
#define EMPTY 197
#include "native_motor_probe.h"
static_assert(EMPTY==197,"Platform macro must survive the public probe include");
void setup();void loop();
TEST_CASE("B3 D077 native probe startup and ten thousand loops are inert") {
    CHECK(fixture::hw.trace_size==0);
    CHECK(native_motor_probe::gate.fault()==motors::Fault::NONE);
    CHECK(native_motor_probe::address==nullptr);
    setup();CHECK(native_motor_probe::address==&native_motor_probe::exercise);
    for(unsigned i=0;i<10000;++i)loop();
    CHECK(fixture::hw.trace_size==0);
    CHECK(native_motor_probe::gate.fault()==motors::Fault::NONE);
}

// Exercises only the inert battery probe static object setup and empty loop.
// Retaining a function pointer must never call begin or read during startup.
// The same expectations apply to default and host-only MATCH compiler defines.
#include "doctest.h"
#include "native_fixture.h"
#include "power_probe.h"
void setup();void loop();
TEST_CASE("B5 inert compile probe startup and ten thousand loops perform zero native I/O") {
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);
    CHECK(power_probe::entry==nullptr);setup();CHECK(power_probe::entry==&power_probe::exercise);
    for(unsigned i=0;i<10000;++i)loop();
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);
}

// Checks the real D086 compile-only probe without native register mappings.
// Retained method addresses must never execute during construction setup or loop.
// Both macro modes use the same zero-I/O expectations for ten thousand loops.
#include "doctest.h"
#include "native_fixture.h"
#include "adc_pair_probe.h"
void setup();void loop();
TEST_CASE("B6 D086 actual pair probe is inert during startup and ten thousand loops") {
 CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);
 CHECK(fixture::hw.clock_on==0);CHECK(fixture::hw.clock_rate==0);CHECK(adc_pair_probe::entry==nullptr);
 fixture::hw.count_allocations=true;setup();for(unsigned i=0;i<10000;++i)loop();fixture::hw.count_allocations=false;
 CHECK(adc_pair_probe::entry==&adc_pair_probe::exercise);CHECK(fixture::hw.allocations==0);
 CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);CHECK(fixture::hw.clock_on==0);CHECK(fixture::hw.clock_rate==0);
}

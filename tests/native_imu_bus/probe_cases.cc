// Checks the inert compile-only probe startup and repeated empty loop behavior.
// Merely retaining a function pointer must not claim, configure or read the bus.
// Native MMIO is deliberately unmapped until fixture reset, catching constructor I/O.
#include "doctest.h"
#include "native_fixture.h"
#include "imu_bus_probe.h"
void setup();void loop();
TEST_CASE("B3 inert compile probe setup and ten thousand loops perform zero I/O") {
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);
    CHECK(fixture::hw.irq_reads==0);CHECK(fixture::hw.clock_on==0);
    CHECK(imu_bus_probe::entry==nullptr);setup();CHECK(imu_bus_probe::entry==&imu_bus_probe::exercise);
    for(unsigned i=0;i<10000;++i)loop();
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);
    CHECK(fixture::hw.irq_reads==0);CHECK(fixture::hw.clock_on==0);
}

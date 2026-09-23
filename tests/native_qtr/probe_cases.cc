// Checks the real compile probe without mapping any native register address.
// Startup must retain callable code without granting ownership or executing it.
// Both macro modes exercise constructors, setup and ten thousand empty loops.
#include "doctest.h"
#include "native_fixture.h"
#include "qtr_native_probe.h"
void setup();void loop();
TEST_CASE("B2 D085 actual compile probe remains inert in constructors setup and loops") {
 CHECK(fixture::hw.reg_reads==0);CHECK(fixture::hw.reg_writes==0);CHECK(fixture::hw.clocks==0);
 CHECK(fixture::hw.ready_reads==0);CHECK(fixture::hw.irq_reads==0);CHECK(fixture::hw.config_calls==0);
 CHECK(qtr_native_probe::entry==nullptr);CHECK_FALSE(qtr_native_probe::exclusive_pads);
 CHECK(qtr_native_probe::exercise_calls==0);fixture::hw.count_allocations=true;setup();
 for(unsigned i=0;i<10000;++i)loop();
 fixture::hw.count_allocations=false;
 CHECK(qtr_native_probe::entry==&qtr_native_probe::exercise);CHECK(qtr_native_probe::exercise_calls==0);
 CHECK(fixture::hw.reg_reads==0);CHECK(fixture::hw.reg_writes==0);CHECK(fixture::hw.clocks==0);
 CHECK(fixture::hw.ready_reads==0);CHECK(fixture::hw.irq_reads==0);CHECK(fixture::hw.config_calls==0);
 CHECK(fixture::hw.allocations==0);CHECK(qtr_native_probe::reader.report().phase==line_qtr::Phase::NOT_STARTED);
}

// Supplies deliberately incompatible installed device-tree metadata variants.
// A profile mismatch cannot authorize mutation of a different route or controller.
// The Python runner changes each metadata field independently before compilation.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
TEST_CASE("B3 malformed installed route clock IRQ or pinctrl metadata refuses admission") {
 fixture::isolated([]{
    fixture::reset();imu::Bus b;const auto r=b.begin();CHECK_FALSE(r.ready);CHECK(r.status!=imu::BusStatus::OK);
    CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==0);CHECK(fixture::hw.start_count==0);
 });
}

// Checks invalid public transport settings independently of native metadata.
// Unsupported timing routes addresses or unbounded budgets cannot change hardware.
// The runner stages one changed config value and keeps exact source hashes.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
TEST_CASE("B3 unsupported config returns invalid config before native mutation") {
 fixture::isolated([]{
    fixture::reset();imu::Bus b;const auto r=b.begin();CHECK_FALSE(r.ready);CHECK(r.status==imu::BusStatus::INVALID_CONFIG);
    CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==0);CHECK(fixture::hw.start_count==0);
 });
}

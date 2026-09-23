// Rejects unsupported staged configuration without mutating workspace defaults.
// Test variants preserve actual production bytes and change one public tunable.
// Invalid configuration must fail before any native operation or allocation.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
TEST_CASE("B5 invalid scaling timing and pin config fails before hardware I/O") {fixture::isolated([&] {
    fixture::reset();power::Reader r;auto b=r.begin();CHECK(b.status==power::Status::INVALID_CONFIG);
    CHECK_FALSE(b.ready);CHECK(b.shutdown==power::Shutdown::NOT_ATTEMPTED);
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.ready_reads==0);CHECK(fixture::hw.clock_on==0);
    CHECK_FALSE(r.read().valid);

});}

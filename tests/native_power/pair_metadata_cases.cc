// Rejects malformed A1 metadata and any collision in the fixed pair profile.
// Compiler variants alter only immutable fixture bindings or copied configuration.
// The actual production owner must reject before claim, clock enabling or writes.
#include "doctest.h"
#include "native_fixture.h"
#include "hal/power.h"
TEST_CASE("B6 D086 malformed A1 or excluded proposal metadata rejects before I/O writes") {
 fixture::reset();power::Reader r;const auto init=r.beginWithButtons();CHECK_FALSE(init.ready);
 CHECK((init.status==power::Status::INVALID_CONFIG||init.status==power::Status::OWNERSHIP));
 CHECK(init.shutdown==power::Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==0);
 CHECK_FALSE(r.readButtons().valid);
}

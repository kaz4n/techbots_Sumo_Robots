// Rejects malformed immutable pad metadata before ADC configuration.
// GPIO aliases must not allow the battery reader to seize an existing proposal.
// Each executable compiles the same opaque production source with one bad mapping.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
TEST_CASE("B5 malformed native map fails closed without ADC or pad writes") {fixture::isolated([&] {
    fixture::reset();power::Reader r;auto b=r.begin();CHECK_FALSE(b.ready);
    CHECK((b.status==power::Status::INVALID_CONFIG||b.status==power::Status::OWNERSHIP));
    CHECK(b.shutdown==power::Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);
    CHECK(fixture::hw.clock_on==0);CHECK_FALSE(r.read().valid);

});}

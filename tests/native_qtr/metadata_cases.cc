// Rejects malformed metadata or unsupported configuration before pad writes.
// Each compilation has an independently changed header/config, not source body.
// Runtime observations prove the native driver does not silently substitute pins.
#include "doctest.h"
#include "native_fixture.h"
#include "hal/line_qtr.h"
TEST_CASE("B2 D085 malformed native configuration fails before writes") {
 fixture::reset();line_qtr::Reader r;
 CHECK(r.begin(true)==line_qtr::Status::INVALID_CONFIG);
 CHECK(fixture::hw.config_calls==0);CHECK(fixture::hw.reg_writes==0);
 CHECK_FALSE(r.report().valid);
}

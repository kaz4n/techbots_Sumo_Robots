// Tests copied invalid configuration through the public D116 admission API.
// No clock or native callback may run before CONFIG rejection.
// Each isolated profile changes one literal config value, never live source.
#include "fixture.h"
TEST_CASE("D116 CONFIG rejects before callbacks and disabled ignores invalid settings") {
    d116::Rig f;
    CHECK_FALSE(f.runner.begin(true,d116::grants()));
    CHECK(f.runner.report().phase==d116::Phase::FAILED);
    CHECK(f.runner.report().failure==d116::Failure::CONFIG);
    CHECK(f.io.clocks==0U);CHECK(f.io.begins==0U);
    CHECK(f.runner.report().configure_enable_calls==0U);d116::passive(f);
    d116::Runner absent({});CHECK_FALSE(absent.begin());
    CHECK(absent.report().phase==d116::Phase::DISABLED);absent.poll();
    CHECK(absent.report().phase==d116::Phase::DISABLED);
    d116::Rig missing;
    CHECK_FALSE(missing.runner.begin(true,{}));
    CHECK(missing.runner.report().failure==d116::Failure::GRANT);
    d116::Runner ports({});CHECK_FALSE(ports.begin(true,{}));
    CHECK(ports.report().failure==d116::Failure::PORT);
}

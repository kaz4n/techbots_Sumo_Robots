// Checks D093 seeded representational boundaries without billions of operations.
// Only this dedicated test translation unit exposes owner state after real setup.
// Public dependencies are included first so the seam changes no other class.
#include "doctest.h"
#include "hal/power.h"
#include "hal/ui.h"
#define private public
#include "hal/power_inputs.h"
#undef private
#include "../fixtures/power_inputs_fixture.h"
#include <limits>
using namespace power_inputs_test;
#if defined(INPUT_CONFIG_BAD) || defined(INPUT_CONFIG_GOOD)
TEST_CASE("B6 D093 owner configuration validation runs before all callbacks") {
    Rig rig;
#ifdef INPUT_CONFIG_BAD
    CHECK_FALSE(rig.owner.begin()); CHECK(rig.owner.report().fault == power::InputFault::CONFIG);
    CHECK(rig.fake.callbacks() == 0U); CHECK_FALSE(rig.owner.begin()); CHECK(rig.fake.callbacks() == 0U);
#else
    CHECK(rig.owner.begin()); CHECK(rig.fake.setups == 1U);
#endif
}
#else
TEST_CASE("B6 D093 seeded attempt refusal generation saturation never prevents new callbacks") {
    Rig rig; rig.prime(); const auto maximum = std::numeric_limits<std::uint32_t>::max();
    rig.owner.report_.battery_attempts = maximum-1U; rig.owner.report_.button_attempts = maximum-1U;
    rig.owner.report_.battery_refused = maximum-1U; rig.owner.report_.button_refused = maximum-1U;
    rig.owner.report_.battery_generation = std::numeric_limits<std::uint64_t>::max()-1U;
    for (unsigned index = 0; index < 3U; ++index) {
        rig.fake.now += 10000U; CHECK_FALSE(rig.owner.readBatteryIfDue(false).attempted);
        CHECK_FALSE(rig.owner.readButtons(false).attempted);
        CHECK(rig.owner.readBatteryIfDue(true).accepted); CHECK(rig.owner.readButtons(true).accepted);
    }
    CHECK(rig.owner.report().battery_attempts == maximum); CHECK(rig.owner.report().button_attempts == maximum);
    CHECK(rig.owner.report().battery_refused == maximum); CHECK(rig.owner.report().button_refused == maximum);
    CHECK(rig.owner.report().battery_generation == std::numeric_limits<std::uint64_t>::max());
    CHECK(rig.fake.batteries == 4U); CHECK(rig.fake.buttons == 3U);
}
TEST_CASE("B6 D093 seeded accepted A1 sequence progresses maximum then zero then one") {
    Rig rig; rig.begin(); CHECK(rig.owner.readButtons(true).accepted);
    rig.owner.button_sequence_ = 0xFFFFFFFEU; rig.fake.sequence = 0xFFFFFFFEU;
    for (auto expected : {0xFFFFFFFFU, 0U, 1U}) {
        const auto result = rig.owner.readButtons(true); CHECK(result.accepted);
        CHECK(result.sample.sequence == expected);
    }
    CHECK(rig.owner.report().button_attempts == 4U);
}
#endif

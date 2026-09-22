// Checks the seven front-only bearing rows in B5.2 without adding fusion policy.
// Preserves the specified left/right symmetry and ignores unrelated sensor groups.
// Run with tools/test_host.sh; independent table expectations use the public header.
#include "doctest.h"
#include "core/opp_fusion.h"
#include <cstdint>

namespace {
void checkFront(std::uint8_t mask, float bearing, bool centered, bool close) {
    const auto view = opp_fusion::frontView(mask);
    CHECK(view.detected);
    CHECK(view.bearing_deg == bearing);
    CHECK(view.centered == centered);
    CHECK(view.close == close);
}
} // namespace

TEST_CASE("B5.2 FC alone has zero bearing and is centered without a close cue") {
    checkFront(0b010U, 0.0F, true, false);
}

TEST_CASE("B5.2 FL15 plus FC has minus six degree bearing and is centered") {
    checkFront(0b011U, -6.0F, true, false);
}

TEST_CASE("B5.2 FC plus FR15 has plus six degree bearing and is centered") {
    checkFront(0b110U, 6.0F, true, false);
}

TEST_CASE("B5.2 all three front sensors have zero bearing centered and close cues") {
    checkFront(0b111U, 0.0F, true, true);
}

TEST_CASE("B5.2 FL15 plus FR15 straddling without FC is centered and close") {
    checkFront(0b101U, 0.0F, true, true);
}

TEST_CASE("B5.2 FL15 alone has minus fifteen degree bearing and is not centered") {
    checkFront(0b001U, -15.0F, false, false);
}

TEST_CASE("B5.2 FR15 alone has plus fifteen degree bearing and is not centered") {
    checkFront(0b100U, 15.0F, false, false);
}

TEST_CASE("B5.2 no front bit has no front detection regardless of side or rear bits") {
    for (unsigned groups = 0; groups < 32; ++groups)
        CHECK_FALSE(opp_fusion::frontView(static_cast<std::uint8_t>(groups << 3U)).detected);
}

TEST_CASE("B5.2 side rear and unused bits do not alter any front-only table row") {
    for (unsigned front = 1; front < 8; ++front) {
        const auto expected = opp_fusion::frontView(static_cast<std::uint8_t>(front));
        for (unsigned groups = 0; groups < 32; ++groups) {
            const auto mask = static_cast<std::uint8_t>(front | (groups << 3U));
            const auto view = opp_fusion::frontView(mask);
            CHECK(view.detected == expected.detected);
            CHECK(view.centered == expected.centered);
            CHECK(view.close == expected.close);
            CHECK(view.bearing_deg == expected.bearing_deg);
        }
    }
}

TEST_CASE("B0/B5.2 mirroring FL15 and FR15 negates bearing and preserves front cues") {
    for (unsigned mask = 1; mask < 8; ++mask) {
        const auto mirrored = (mask & 2U) | ((mask & 1U) << 2U) | ((mask & 4U) >> 2U);
        const auto left = opp_fusion::frontView(static_cast<std::uint8_t>(mask));
        const auto right = opp_fusion::frontView(static_cast<std::uint8_t>(mirrored));
        CHECK(left.bearing_deg == -right.bearing_deg);
        CHECK(left.detected == right.detected);
        CHECK(left.centered == right.centered);
        CHECK(left.close == right.close);
    }
}

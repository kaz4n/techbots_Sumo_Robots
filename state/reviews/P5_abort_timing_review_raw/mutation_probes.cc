// Checks adopted D135 negative dispositions under isolated producer fault injection.
// Reuses the frozen public Rig; copied implementation faults expose no production setter.
// Root may execute this one filtered case against one replaced production object.
#include "private_spec_probes.cc"

#ifndef D135_FAULT_CASE
#error "Select one isolated D135 producer fault"
#endif

TEST_CASE("D135 isolated producer fault") {
    using namespace private_d135;
    static_assert(D135_FAULT_CASE >= 1 && D135_FAULT_CASE <= 8);
    Rig rig;
    const auto d = rig.beforeGo(Mode::DIRECT, D135_FAULT_CASE == 8 ? 0U : 2U);
    const auto candidate = rig.step(d);
    APP_REQUIRE(candidate.lifecycle.gate.go);
    if constexpr (D135_FAULT_CASE <= 3) {
        const unsigned state = D135_FAULT_CASE == 1 ? 3U : D135_FAULT_CASE == 2 ? 4U : 5U;
        suffix(candidate, {16U, 17U, 18U, 25U});
        CHECK(event(candidate, 18U).value == cue(3U, 0U, 1U, 2U, true));
        CHECK(event(candidate, 25U).value == state);
        CHECK(event(candidate, 25U).t_us == d); CHECK(count(candidate, 19U) == 0U);
        for (unsigned i = 1U; i <= 3U; ++i) CHECK(traceCount(rig.step(d + i * 1000U)) == 0U);
    } else if constexpr (D135_FAULT_CASE <= 6) {
        suffix(candidate, {16U, 17U, 18U, 19U});
        const auto closed = rig.step(d + 1000U);
        CHECK(traceCount(closed) == 1U); CHECK(event(closed, 24U).value == 1U);
        CHECK(event(closed, 24U).t_us == d + 1000U); CHECK(count(closed, 20U) == 0U);
        for (unsigned i = 2U; i <= 4U; ++i) CHECK(traceCount(rig.step(d + i * 1000U)) == 0U);
    } else {
        if constexpr (D135_FAULT_CASE == 7) suffix(candidate, {16U, 17U, 18U, 19U});
        else { CHECK(traceCount(candidate) == 0U); CHECK(candidate.outputs.ui_state == State::OPENER); }
        const auto exhausted = rig.robot.step(rig.at(d + 1000U));
        CHECK(exhausted.token == 0U); CHECK_FALSE(exhausted.fresh);
        CHECK(exhausted.outputs.ui_state == State::STOPPED); CHECK_FALSE(exhausted.outputs.motors_enabled);
        CHECK(exhausted.outputs.duty_l == 0.0F); CHECK(exhausted.outputs.duty_r == 0.0F);
        CHECK(traceCount(exhausted) == 1U);
        if constexpr (D135_FAULT_CASE == 7) {
            CHECK(event(exhausted, 20U).t_us == d); CHECK(event(exhausted, 20U).value == 1U);
            CHECK(count(exhausted, 22U) == 0U);
        } else {
            CHECK(event(exhausted, 22U).t_us == d + 1000U); CHECK(event(exhausted, 22U).value == 2U);
            CHECK(count(exhausted, 20U) == 0U);
        }
        CHECK(traceCount(rig.robot.step(rig.at(d + 2000U))) == 0U);
    }
}

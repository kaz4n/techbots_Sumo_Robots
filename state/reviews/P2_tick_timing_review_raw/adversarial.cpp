// Exhaustive independent D092 chronology and attempt-mode review checks.
// Covers neighboring boundaries and wrap without accessing Robot private state.
// Built separately from production and established test suites.
#include "fixtures/tick_timing_fixture.h"
#include <initializer_list>
using namespace timing_test;
TEST_CASE("B14 D092 reviewer neighboring chronology exhaustive and wrapped") {
    for (const auto base : {0U, 0U - 5163002U}) {
        for (std::uint32_t acquisition = 0; acquisition <= 2; ++acquisition) {
            for (std::uint32_t a = acquisition; a <= 4; ++a) {
                for (std::uint32_t e = acquisition + 1; e <= 5; ++e) {
                    if (a > e) continue;
                    for (std::uint32_t c = 0; c <= 5; ++c) {
                        for (std::uint32_t n = 0; n <= e; ++n) {
                            Rig rig;
                            const auto d = rig.go(acquisition, base);
                            const auto s = d - acquisition;
                            const auto result = rig.submit(rig.receipt(s+n,s+e,s+a,s+c,c));
                            const bool ordered = a <= c && c <= n;
                            CHECK(result.contract_faults == 0U);
                            CHECK(result.ticks.ticks == (ordered ? 1U : 0U));
                            CHECK(result.timing_incomplete == !ordered);
                            CHECK(result.ticks.max_us == (ordered ? c : 0U));
                            CHECK(result.ticks.overruns == 0U);
                        }
                    }
                }
            }
        }
    }
}
TEST_CASE("B14 D092 reviewer accepted START after cancellation preserves timing mode") {
    Rig rig;
    const auto release = rig.release();
    rig.step(release+1000U,core::ButtonLevel::MODE);
    CHECK(rig.step(release+21000U,core::ButtonLevel::MODE).outputs.ui_state == core::State::IDLE);
    rig.step(release+22000U);
    rig.input.timing.explicit_start=false;
    const auto d=rig.go(0U,release+100000U);
    badTiming(rig.step(d+1000U),d+1000U);
}

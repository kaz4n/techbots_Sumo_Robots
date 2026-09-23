// Verifies D094's retained actual integration probe never runs its exercise.
// Counts actual Bus fixture access and every exposed motor callback at startup.
// Both macro modes execute setup plus10000loops with no hardware or heap action.
#include "doctest.h"
#include "native_fixture.h"
#define EMPTY 197
#include "imu_resume_probe.h"
static_assert(EMPTY == 197, "Probe preserves framework EMPTY macro");
void setup(); void loop();
namespace {
unsigned callbacks = 0U;
bool enSetup(void*) { ++callbacks; return true; }
bool pwmSetup(void*, motors::Channel) { ++callbacks; return true; }
bool enable(void*, bool) { ++callbacks; return true; }
bool pwm(void*, motors::Channel, std::uint32_t, std::uint32_t) { ++callbacks; return true; }
std::uint32_t clock(void*) { ++callbacks; return 0U; }
}
motors::Port motors::UnoQPort::port() {
    return {this, enSetup, pwmSetup, enable, pwm, enSetup, clock, {1000U,1000U,1000U,1000U}};
}
TEST_CASE("B3 D094 actual probe startup and10000loops are inert") {
    CHECK(imu_resume_probe::entry == nullptr); CHECK(callbacks == 0U);
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.clock_on == 0U); CHECK(fixture::hw.ready_reads == 0U);
    {
        fixture::AllocationGuard guard; setup();
        for (unsigned i = 0U; i < 10000U; ++i) loop();
    }
    CHECK(imu_resume_probe::entry == &imu_resume_probe::exercise); CHECK(callbacks == 0U);
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.clock_on == 0U); CHECK(fixture::hw.ready_reads == 0U);
    CHECK(fixture::hw.allocations == 0U);
}

// Verifies D093 probe startup retains actual integration without calling it.
// Native ADC is real fixture-linked code; the motor port exposes counted callbacks.
// Both macro variants execute setup and ten thousand loops with zero device I/O.
#include "doctest.h"
#include "native_fixture.h"
#define EMPTY 197
#include "power_inputs_probe.h"
static_assert(EMPTY == 197, "Probe public header preserves platform macro");
void setup(); void loop();
namespace {
unsigned motor_callbacks = 0U;
bool setupEnable(void*) { ++motor_callbacks; return true; }
bool setupPwm(void*, motors::Channel) { ++motor_callbacks; return true; }
bool enable(void*, bool) { ++motor_callbacks; return true; }
bool pwm(void*, motors::Channel, std::uint32_t, std::uint32_t) { ++motor_callbacks; return true; }
std::uint32_t motorClock(void*) { ++motor_callbacks; return 0U; }
}
motors::Port motors::UnoQPort::port() {
    return {this, setupEnable, setupPwm, enable, pwm, setupEnable, motorClock, {1000U,1000U,1000U,1000U}};
}
TEST_CASE("B6 D093 actual integration probe setup and10000loops never invoke native or motor IO") {
    CHECK(power_inputs_probe::entry == nullptr);
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.clock_on == 0U); CHECK(fixture::hw.ready_reads == 0U); CHECK(motor_callbacks == 0U);
    fixture::hw.count_allocations = true;
    setup(); for (unsigned index = 0U; index < 10000U; ++index) loop();
    fixture::hw.count_allocations = false;
    CHECK(power_inputs_probe::entry == &power_inputs_probe::exercise);
    CHECK(fixture::hw.allocations == 0U); CHECK(motor_callbacks == 0U);
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.clock_on == 0U); CHECK(fixture::hw.clock_rate == 0U); CHECK(fixture::hw.ready_reads == 0U);
}

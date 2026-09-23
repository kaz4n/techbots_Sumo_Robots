// Exercises separately compiled malformed DT and clock metadata.
// A bank rejection must precede the first GPIO configuration or native PWM call.
// The Python runner enumerates every selected pin and invalid source property.
#include "doctest.h"
#include "native_fixture.h"
#include "hal/motor_port_unoq.h"
TEST_CASE("B3 D077 malformed native metadata rejects before configuration") {
    fixture::reset();motors::UnoQPort native;auto p=native.port();
#ifdef NATIVE_INVALID_CLOCK
    for(auto period:p.period_cycles)CHECK(period==0);
#endif
    motors::MotorGate gate(p);CHECK_FALSE(gate.begin());
    CHECK(fixture::hw.calls[fixture::CONFIGURE]==0);
    CHECK(fixture::hw.calls[fixture::ROUTE]==0);
    CHECK(fixture::hw.calls[fixture::PWM]==0);
#ifdef NATIVE_INVALID_CLOCK
    CHECK(fixture::hw.trace_size==0);
#endif
}

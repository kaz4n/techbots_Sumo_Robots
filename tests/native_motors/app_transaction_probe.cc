// Exercises the real D095 retained probe startup with native motor substitutions.
// Separately checks heap silence of the actual owner through counted callbacks.
// Neither test invokes MCU hardware, upload, transport or physical motor motion.
#include "doctest.h"
#include "native_fixture.h"
#define EMPTY 197
#include "app_transaction_probe.h"
static_assert(EMPTY == 197, "Probe public header preserves platform macros");
#include "fixtures/app_transaction_fixture.h"
void setup(); void loop();
TEST_CASE("B3 D095 actual native app probe startup and ten thousand loops are inert") {
    CHECK(fixture::hw.trace_size == 0U);
    CHECK(app_transaction_probe::entry == nullptr);
    fixture::hw.count_allocations = true;
    setup(); for (unsigned i = 0; i < 10000U; ++i) loop();
    fixture::hw.count_allocations = false;
    CHECK(app_transaction_probe::entry == &app_transaction_probe::exercise);
    CHECK(fixture::hw.trace_size == 0U); CHECK(fixture::hw.allocations == 0U);
}
TEST_CASE("B0 B14 D095 actual transaction operations and terminal halt allocate nothing") {
    app_test::Port port;
    app::Transaction owner(port.port()); auto input = app_test::input();
    fixture::hw.allocations = fixture::hw.deallocations = 0U;
    fixture::hw.count_allocations = true;
    bool good = owner.initialize();
    for (unsigned i = 0; i < 1000U; ++i) {
        port.now = i * 1000U; good = owner.open() && good;
        port.now += 100U; good = owner.decide(input) && good;
        port.now += 50U; good = owner.finish() && good;
    }
    owner.abort(); owner.abort();
    fixture::hw.count_allocations = false;
    CHECK(good); CHECK(fixture::hw.allocations == 0U);
    CHECK(fixture::hw.deallocations == 0U); CHECK(owner.report().fault == app::Fault::ABORTED);
}

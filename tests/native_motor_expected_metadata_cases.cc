// Queries real anonymous-namespace candidate helpers in their own translation unit.
// Prints observations for the Python oracle's independently fixed numeric matrix.
// Uses unchanged native fixtures; only Port construction and metadata queries run.
#include D202_SUBJECT
#include "native_fixture.h"
#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <type_traits>

namespace {
void need(bool value) {
    if (!value) { std::fputs("D202 metadata fixture invariant failed\n", stderr); std::exit(1); }
}
}

int main() {
    static_assert(std::is_same<decltype(motors::candidateRate(0U)), std::uint64_t>::value);
    static_assert(std::is_same<decltype(motors::candidatePeriod(0U)), std::uint32_t>::value);
    fixture::reset();
    std::uint64_t rates[5]{};
    std::uint32_t periods[5]{};
    constexpr std::uint32_t indices[5] = {0U, 1U, 2U, 3U, UINT32_MAX};
    motors::UnoQPort native;
    motors::Port port;
    {
        fixture::NoAllocation guard;
        for (unsigned i = 0U; i < 5U; ++i) {
            volatile std::uint32_t index = indices[i];
            rates[i] = motors::candidateRate(index);
            periods[i] = motors::candidatePeriod(index);
        }
        port = native.port();
    }
    need(fixture::hw.trace_size == 0U);
    for (const auto count : fixture::hw.calls) need(count == 0U);
    need(fixture::hw.allocations == 0U && fixture::hw.deallocations == 0U);
    need(port.context == &native && port.configureEnableLow && port.configurePwm &&
         port.writeEnable && port.writePwm && port.settle && port.clockUs);
#if SUMOX_MOTOR_FAULT_PROBE == 1
    const motors::SettleProbeReport zero{};
    need(std::memcmp(&motors::settleProbeReport(), &zero, sizeof(zero)) == 0);
    static_assert(sizeof(motors::SettleProbeReport) == 28U);
#endif
    std::printf("{\"rates\":[");
    for (unsigned i = 0U; i < 5U; ++i) std::printf("%s%" PRIu64, i ? "," : "", rates[i]);
    std::printf("],\"periods\":[");
    for (unsigned i = 0U; i < 5U; ++i) std::printf("%s%" PRIu32, i ? "," : "", periods[i]);
    std::printf("],\"port\":[");
    for (unsigned i = 0U; i < 4U; ++i) std::printf("%s%" PRIu32, i ? "," : "", port.period_cycles[i]);
    std::printf("],\"native_bytes\":%zu,\"port_bytes\":%zu,\"calls\":0,\"allocations\":0}\n",
                sizeof(native), sizeof(port));
}

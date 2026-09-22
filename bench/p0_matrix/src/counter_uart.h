// Declares the inert P0 internal-UART counter diagnostic boundary.
// Exposes truthful admission/completion/fault state without receiving commands.
// Verified by isolated adapter tests, installed-driver audit and target evidence.
#pragma once
#include <cstdint>

namespace p0 {
struct CounterDiagnostics {
    std::uint32_t submitted = 0;
    std::uint32_t completed = 0;
    std::uint32_t refused = 0;
    bool ready = false;
    bool faulted = false;
};
bool beginCounterTransport();
bool submitCounter(std::uint32_t counter, std::uint32_t now_us);
void serviceCounter(std::uint32_t now_us);
CounterDiagnostics counterDiagnostics();
} // namespace p0

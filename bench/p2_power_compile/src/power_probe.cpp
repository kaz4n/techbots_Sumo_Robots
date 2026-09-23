// Retains actual ADC admission, setup, acquisition and fault cleanup methods.
// The sketch never calls this function, including during global startup.
// Host startup tests and MCU ELF inspection verify the retained-only boundary.
#include "power_probe.h"

namespace power_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result;
    result.init = reader.begin();
    result.sample = reader.read();
    return result;
}
} // namespace power_probe

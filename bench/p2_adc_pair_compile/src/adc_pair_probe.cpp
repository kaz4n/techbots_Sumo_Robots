// Retains actual pair admission and alternating native conversion methods.
// The sketch never calls this function, including during global startup.
// Host startup tests and target ELF inspection check this retained-only path.
#include "adc_pair_probe.h"

namespace adc_pair_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result;
    result.init = reader.beginWithButtons();
    result.battery_first = reader.read();
    result.buttons_first = reader.readButtons();
    result.battery_second = reader.read();
    result.buttons_second = reader.readButtons();
    return result;
}
} // namespace adc_pair_probe

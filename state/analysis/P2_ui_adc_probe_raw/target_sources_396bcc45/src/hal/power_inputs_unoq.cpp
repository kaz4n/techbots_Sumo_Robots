// Binds the fixed input owner to one real native ADC Reader and its clock.
// Thin forwarding preserves exclusive fresh conversions without factory I/O.
// Independent installed-shaped native tests and an inert target probe check it.
#include "power_inputs.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include <Arduino.h>

namespace power {
namespace {
InitResult beginPair(void* context) { return static_cast<Reader*>(context)->beginWithButtons(); }
Sample readBattery(void* context) { return static_cast<Reader*>(context)->read(); }
ButtonSample readButtons(void* context) { return static_cast<Reader*>(context)->readButtons(); }
std::uint32_t clockUs(void*) { return static_cast<std::uint32_t>(micros()); }
} // namespace

InputPort readerInputPort(Reader& reader) {
    return {&reader, beginPair, readBattery, readButtons, clockUs};
}
} // namespace power
#endif

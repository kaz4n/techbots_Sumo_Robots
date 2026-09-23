// Forwards A1 capture callbacks to one existing fixed-profile power Reader.
// Leaves ADC ownership and fault cleanup with that owner and construction passive.
// Independent counted native substitutions and target inspection verify this binding.
#include "ui_bench_native.h"
#include <Arduino.h>

namespace ui_bench {
Port Native::port() { return {this, &clockUs, &beginButtons, &readButtons}; }
std::uint32_t Native::clockUs(void*) { return static_cast<std::uint32_t>(micros()); }
power::InitResult Native::beginButtons(void* context) {
    return static_cast<Native*>(context)->reader_.beginWithButtons();
}
power::ButtonSample Native::readButtons(void* context) {
    return static_cast<Native*>(context)->reader_.readButtons();
}
} // namespace ui_bench

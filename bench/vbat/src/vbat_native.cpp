// Forwards battery capture callbacks to one existing battery-only native Reader.
// Keeps construction passive and leaves native ownership and failure cleanup with the Reader.
// Independent counted Reader substitutes and target startup inspection test this binding.
#include "vbat_native.h"
#include <Arduino.h>

namespace vbat {
Port Native::port() { return {this, &clockUs, &beginBattery, &readBattery}; }
std::uint32_t Native::clockUs(void*) { return static_cast<std::uint32_t>(micros()); }
power::InitResult Native::beginBattery(void* context) {
    return static_cast<Native*>(context)->reader_.begin();
}
power::Sample Native::readBattery(void* context) {
    return static_cast<Native*>(context)->reader_.read();
}
} // namespace vbat

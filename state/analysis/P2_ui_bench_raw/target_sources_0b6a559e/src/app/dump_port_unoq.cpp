// Binds the application's optional dump callbacks to one fixed native UART owner.
// Keeps construction free of I/O and setup authority in the explicit grants.
// D101 native binding tests and target compilation verify direct forwarding.
#include "dump_port.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
namespace app {
namespace {
recorder::dump::NativeStatus begin(void* context, const recorder::dump::SetupGrant& grant) {
    return static_cast<recorder::dump::UnoQDumpPort*>(context)->begin(grant);
}

bool ready(void* context) {
    return static_cast<recorder::dump::UnoQDumpPort*>(context)->ready();
}
} // namespace

DumpPort unoQDumpPort(recorder::dump::UnoQDumpPort& owner) {
    return {&owner, begin, ready, owner.port()};
}
} // namespace app
#endif

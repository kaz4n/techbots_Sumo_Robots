// Binds the existing bounded dump transport into actual application transactions.
// Keeps setup ownership, Linux readiness and byte output explicit and optional.
// Independent Runtime tests and target factory inspection verify D101.
#pragma once
#include "../hal/dump_uart_unoq.h"

namespace app {
struct DumpPort {
    void* context = nullptr;
    recorder::dump::NativeStatus (*begin)(void*, const recorder::dump::SetupGrant&) = nullptr;
    bool (*ready)(void*) = nullptr;
    recorder::dump::Port output;
};
// Factory binds the existing native owner; it performs no initialization or I/O.
DumpPort unoQDumpPort(recorder::dump::UnoQDumpPort& owner);
} // namespace app

// Reviews actual D101 factory bindings with instrumented public native methods.
// Separates binding identity and zero construction I/O from hardware qualification.
// run_review.py compiles production dump_port_unoq.cpp and this independent probe.
#include "app/dump_port.h"
#include <cstdio>
#include <cstdlib>

namespace {
unsigned checks = 0U, begins = 0U, readies = 0U, ports = 0U, writes = 0U, cancels = 0U;
recorder::dump::UnoQDumpPort* expected = nullptr;
const recorder::dump::SetupGrant* passed_grant = nullptr;
recorder::dump::SetupGrant seen;
recorder::dump::NativeStatus return_status = recorder::dump::NativeStatus::CONTEXT;
bool return_ready = false;
void require(bool ok, int line) {
    ++checks;
    if (!ok) { std::fprintf(stderr, "factory check failed at %d\n", line); std::exit(1); }
}
#define CHECK(x) require((x), __LINE__)
recorder::dump::WriteResult writeProbe(void* p, const char* bytes, std::size_t size) {
    CHECK(p == expected); CHECK(bytes != nullptr); CHECK(size == 3U); ++writes;
    return {recorder::dump::WriteStatus::PROGRESS, size};
}
void cancelProbe(void* p) { CHECK(p == expected); ++cancels; }
}

namespace recorder::dump {
NativeStatus UnoQDumpPort::begin(const SetupGrant& grant) {
    CHECK(this == expected); CHECK(&grant == passed_grant); seen = grant; ++begins;
    return return_status;
}
bool UnoQDumpPort::ready() { CHECK(this == expected); ++readies; return return_ready; }
Port UnoQDumpPort::port() { CHECK(this == expected); ++ports; return {this, writeProbe, cancelProbe}; }
}

int main() {
    recorder::dump::UnoQDumpPort owners[2];
    for (auto& owner : owners) {
        expected = &owner;
        const auto old_begins = begins, old_readies = readies;
        const auto old_writes = writes, old_cancels = cancels, old_ports = ports;
        const auto binding = app::unoQDumpPort(owner);
        CHECK(begins == old_begins && readies == old_readies);
        CHECK(writes == old_writes && cancels == old_cancels);
        CHECK(ports == old_ports + 1U);
        CHECK(binding.context == &owner && binding.output.context == &owner);
        CHECK(binding.begin != nullptr && binding.ready != nullptr);
        CHECK(binding.output.write == writeProbe && binding.output.cancel == cancelProbe);
        for (unsigned mask = 0U; mask < 16U; ++mask) {
            const recorder::dump::SetupGrant grant{
                (mask & 1U) != 0U, (mask & 2U) != 0U,
                (mask & 4U) != 0U, (mask & 8U) != 0U};
            passed_grant = &grant;
            return_status = static_cast<recorder::dump::NativeStatus>(mask % 11U);
            CHECK(binding.begin(binding.context, grant) == return_status);
            CHECK(seen.setup_phase == grant.setup_phase && seen.exclusive_uart == grant.exclusive_uart);
            CHECK(seen.ready_pin_owned == grant.ready_pin_owned && seen.framing_clean == grant.framing_clean);
        }
        return_ready = false; CHECK(!binding.ready(binding.context));
        return_ready = true; CHECK(binding.ready(binding.context));
        const auto result = binding.output.write(binding.output.context, "abc", 3U);
        CHECK(result.status == recorder::dump::WriteStatus::PROGRESS && result.count == 3U);
        binding.output.cancel(binding.output.context);
    }
    CHECK(begins == 32U && readies == 4U && writes == 2U && cancels == 2U && ports == 2U);
    std::printf("actual factory: %u checks passed; 2 owners, all 16 grant combinations each\n", checks);
}

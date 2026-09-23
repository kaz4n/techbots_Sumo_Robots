// Publishes actual inert Runtime evidence and sampled current-thread stack space.
// Uses only micros and reviewed thread metadata; initializes no peripheral I/O.
// Exact D091 ABI checks, D104 target review and immutable RAM capture verify it.
#include "runtime_bench.h"
#include "runtime_native.h"
#include <Arduino.h>
#include <zephyr/kernel.h>
#include <limits>

static_assert(MOTORS_ALLOWED == 0 && MATCH == 0, "Runtime probe must remain inert");
static_assert(sizeof(void*) == 4U, "Pinned target ABI required");
static_assert(sizeof(k_thread) == 256U, "Pinned loader thread layout required");
static_assert(offsetof(k_thread, stack_info) == 160U, "Pinned stack metadata ABI");
static_assert(sizeof(runtime_bench::StackSample) == 32U, "Pinned stack diagnostic ABI");
static_assert(offsetof(runtime_bench::Diagnostics, report) == 4U, "Pinned report offset");
static_assert(offsetof(runtime_bench::Diagnostics, stack) == 196U, "Pinned stack offset");

extern "C" {
volatile runtime_bench::Diagnostics runtimeDiagnostics;
}
namespace runtime_native {
namespace {
runtime_bench::StackSample stack;
std::uint32_t sequence = 0U;
bool started = false;
bool terminal = false;

bool sram(std::uint32_t start, std::uint32_t size) {
    // The fixed STM32U585 SRAM extent is source-audited in F113/D091.
    return start >= 0x20000000U && start < 0x200C0000U &&
        size > 0U && size <= 0x200C0000U - start;
}

void stackFault(std::uint32_t reason) {
    stack.valid = 0U;
    if (stack.fault == 0U) stack.fault = reason;
}

std::uint32_t currentSp() {
    std::uint32_t control = 0U, ipsr = 0U, sp = 0U;
    asm volatile("mrs %0, control" : "=r"(control));
    asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr != 0U || (control & 3U) != 2U) {
        stackFault(1U); // Require privileged Thread mode with PSP, as in D091.
        return 0U;
    }
    asm volatile("mrs %0, psp" : "=r"(sp));
    return sp;
}

void beginStack() {
    if (currentSp() == 0U) return;
    const auto* thread = k_sched_current_thread_query();
    const auto address = reinterpret_cast<std::uintptr_t>(thread);
    if (address % 4U != 0U || !sram(address, sizeof(k_thread))) {
        stackFault(3U);
        return;
    }
    stack.region_start = thread->stack_info.start;
    stack.region_size = thread->stack_info.size;
    stack.region_delta = thread->stack_info.delta;
    if (stack.region_start % 4U != 0U || !sram(stack.region_start, stack.region_size) ||
        stack.region_delta > stack.region_size) {
        stackFault(4U);
        return;
    }
    stack.valid = 1U;
}

void sampleStack() {
    if (stack.valid == 0U) return;
    const auto sp = currentSp();
    const auto ceiling = stack.region_start + stack.region_size - stack.region_delta;
    if (stack.valid == 0U) return;
    if (sp % 4U != 0U || sp < stack.region_start || sp > ceiling) {
        stackFault(2U);
        return;
    }
    if (stack.samples == 0U || sp < stack.minimum_sp) stack.minimum_sp = sp;
    if (stack.samples < std::numeric_limits<std::uint32_t>::max()) ++stack.samples;
    if (stack.samples == std::numeric_limits<std::uint32_t>::max()) stackFault(5U);
    stack.sampled_headroom_bytes = stack.minimum_sp - stack.region_start;
}

std::uint32_t clockUs(void*) {
    // Samples only these real clock call sites, never a historical watermark.
    sampleStack();
    return micros();
}
runtime_bench::Runner runner({nullptr, clockUs});

void barrier() { asm volatile("dmb" ::: "memory"); }

void publish() {
    runtimeDiagnostics.sequence_front = sequence + 1U;
    barrier();
    const auto* source = reinterpret_cast<const unsigned char*>(&runner.report());
    auto* destination = reinterpret_cast<volatile unsigned char*>(&runtimeDiagnostics.report);
    for (std::size_t i = 0U; i < sizeof(runtime_bench::Report); ++i) destination[i] = source[i];
    source = reinterpret_cast<const unsigned char*>(&stack);
    destination = reinterpret_cast<volatile unsigned char*>(&runtimeDiagnostics.stack);
    for (std::size_t i = 0U; i < sizeof(stack); ++i) destination[i] = source[i];
    barrier();
    sequence += 2U;
    runtimeDiagnostics.sequence_tail = sequence;
    barrier();
    runtimeDiagnostics.sequence_front = sequence;
}

bool done() {
    const auto phase = static_cast<runtime_bench::Phase>(runner.report().phase);
    return phase == runtime_bench::Phase::FROZEN || phase == runtime_bench::Phase::FAILED;
}
} // namespace

void begin() {
    if (started) return;
    started = true;
    beginStack();
    runner.begin();
    terminal = done();
    publish();
}

void poll() {
    if (!started || terminal) return;
    runner.poll();
    terminal = done();
    // RAM publication happens only initially and once terminal, outside timing.
    if (terminal) publish();
}
} // namespace runtime_native

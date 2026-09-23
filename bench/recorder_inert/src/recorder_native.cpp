// Publishes synthetic recorder results and sampled current-thread stack headroom.
// Uses only the MCU clock and metadata; never initializes peripheral I/O.
// Independent review, target imports and frozen RAM capture verify D091 evidence.
#include "recorder_bench.h"
#include "recorder_native.h"
#include <Arduino.h>
#include <zephyr/kernel.h>
#include <limits>

static_assert(MOTORS_ALLOWED == 0, "Recorder experiment must remain inert");
static_assert(MATCH == 0, "Synthetic recorder experiment is not match firmware");
static_assert(sizeof(void*) == 4U, "Pinned target ABI required");
static_assert(sizeof(k_thread) == 256U, "Pinned loader thread layout required");
static_assert(offsetof(k_thread, stack_info) == 160U, "Pinned stack metadata ABI");

extern "C" {
volatile recorder_bench::Diagnostics recorderDiagnostics;
}
namespace recorder_native {
namespace {
recorder_bench::StackSample stack;
std::uint32_t sequence = 0U;
bool terminal = false;

bool sram(std::uint32_t start, std::uint32_t size) {
    // Fixed STM32U585 SRAM extent, audited in F113; not a pin or tunable.
    return start >= 0x20000000U && start < 0x200C0000U &&
        size > 0U && size <= 0x200C0000U - start;
}

void stackFault(std::uint32_t reason) {
    stack.valid = 0U;
    stack.fault = reason;
}

std::uint32_t currentSp() {
    std::uint32_t control = 0U, ipsr = 0U, sp = 0U;
    asm volatile("mrs %0, control" : "=r"(control));
    asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr != 0U || (control & 3U) != 2U) {
        stackFault(1U); // Require privileged Thread mode using PSP.
        return 0U;
    }
    asm volatile("mrs %0, psp" : "=r"(sp));
    return sp;
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
    stack.sampled_headroom_bytes = stack.minimum_sp - stack.region_start;
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
    sampleStack();
}

std::uint32_t clockUs(void*) {
    // Samples at these call sites only: this cannot measure a historical watermark.
    sampleStack();
    return micros();
}
recorder_bench::Runner runner({nullptr, clockUs});

void barrier() { asm volatile("dmb" ::: "memory"); }

void publish() {
    recorderDiagnostics.sequence_front = sequence + 1U;
    barrier();
    const auto* source = reinterpret_cast<const unsigned char*>(&runner.report());
    auto* destination = reinterpret_cast<volatile unsigned char*>(&recorderDiagnostics.report);
    for (std::size_t i = 0U; i < sizeof(recorder_bench::Report); ++i) destination[i] = source[i];
    source = reinterpret_cast<const unsigned char*>(&stack);
    destination = reinterpret_cast<volatile unsigned char*>(&recorderDiagnostics.stack);
    for (std::size_t i = 0U; i < sizeof(stack); ++i) destination[i] = source[i];
    barrier();
    sequence += 2U;
    recorderDiagnostics.sequence_tail = sequence;
    barrier();
    recorderDiagnostics.sequence_front = sequence;
}
} // namespace

void begin() {
    beginStack();
    runner.begin();
    publish();
}

void poll() {
    if (terminal) return;
    const auto before_ticks = runner.report().ticks;
    const auto before_rows = runner.report().checksum_rows;
    const auto before_phase = runner.report().phase;
    runner.poll();
    const auto phase = static_cast<recorder_bench::Phase>(runner.report().phase);
    terminal = phase == recorder_bench::Phase::FROZEN || phase == recorder_bench::Phase::FAILED;
    if (terminal || before_ticks != runner.report().ticks ||
        before_rows != runner.report().checksum_rows || before_phase != runner.report().phase) publish();
}
} // namespace recorder_native

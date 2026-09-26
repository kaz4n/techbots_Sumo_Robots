// Exercises actual D090 native code with independently controlled register words.
// Exact MessagePack bytes and finite progress come from the frozen public contract.
// Each subprocess owns fresh metadata, registers and native-owner lifetime.
#include "hal/dump_uart_unoq.h"
#include "uart_stm32.h"
#include "stm32u5xx_ll_rcc.h"
#include <zephyr/drivers/gpio.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <sys/mman.h>

namespace {
using namespace recorder::dump;
struct Hardware {
    std::uint32_t now = 10000U, clock_step = 0U, control = 0U, ipsr = 0U, primask = 0U;
    std::uint32_t last_clock = 0U, call_started = 0U;
    bool enforce_step_age = false;
    unsigned clock_calls = 0U, init_calls = 0U, configure_calls = 0U, ready_calls = 0U;
    unsigned register_reads = 0U, register_writes = 0U, rdr_reads = 0U, irq_errors = 0U;
    unsigned irq_enabled = 0U, irq_pending = 0U, irq_active = 0U, disable_calls = 0U;
    int ready = 1, init_status = 0, configure_status = 0;
    bool auto_tc = true;
    std::size_t txe_stop_after = 10000U;
    std::vector<unsigned char> tx;
} hw;
device_state states[4] = {{0U, false}, {0U, true}, {0U, true}, {0U, true}};
int api = 1;
gpio_driver_config gpio_metadata{0xFFFFU};
int gpioConfigure(const device*, gpio_pin_t, gpio_flags_t) { return 0; }
int gpioRead(const device*, gpio_port_value_t*) { return 0; }
gpio_driver_api gpio_api{gpioConfigure, gpioRead};
stm32_pclken clocks{168U, 0U, 64U};
pinctrl_dev_config pins{1U};
void irqConfig(const device*) {}
uart_config uart_settings{115200U, 0U, 1U, 3U, 0U};
uart_stm32_data uart_data{&uart_settings, nullptr, nullptr};
uart_stm32_config uart_metadata{LPUART1, &dump_devices[2], {&dump_devices[3], 4102U},
    &clocks, 1U, false, false, false, false, false, 0U, 0U, false, false, &pins, irqConfig};
unsigned checks = 0U;
int failed = 0;
#define VERIFY(c) do { ++checks; if (!(c)) { std::fprintf(stderr,"line %d: %s\n",__LINE__,#c); ++failed; } } while(false)

void mapPage(std::uintptr_t address) {
    const auto page = address & ~std::uintptr_t(4095U);
    void* result = mmap(reinterpret_cast<void*>(page), 4096U, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
    if (result == MAP_FAILED) std::abort();
}
void initialize() {
    mapPage(0x46002400U); mapPage(0x42021800U); mapPage(0x46020C00U);
    RCC->APB3ENR.value = RCC_APB3ENR_LPUART1EN;
    RCC->AHB2ENR1.value = RCC_AHB2ENR1_GPIOGEN;
    GPIOG->MODER.value = 2U << 14U;
    GPIOG->AFR[0].value = 8U << 28U;
    LPUART1->CR1.value = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
    LPUART1->BRR.value = 355556U;
    LPUART1->ISR.value = USART_ISR_TXE | USART_ISR_TC | USART_ISR_TEACK;
}
SetupGrant grant() { return {true, true, true, true}; }
bool start(UnoQDumpPort& native) {
    const auto result = native.begin(grant());
    if (result != NativeStatus::OK) std::fprintf(stderr, "begin_status=%u init=%u configure=%u writes=%u\n",
        static_cast<unsigned>(result), hw.init_calls, hw.configure_calls, hw.register_writes);
    VERIFY(result == NativeStatus::OK);
    VERIFY(native.ready());
    return result == NativeStatus::OK;
}
std::vector<unsigned char> packet(const std::string& text) {
    std::vector<unsigned char> expected{0x93U, 0x02U, 0xA9U, 'm', 'o', 'n', '/', 'w', 'r', 'i', 't', 'e', 0x91U, 0xD9U};
    expected.push_back(static_cast<unsigned char>(text.size()));
    expected.insert(expected.end(), text.begin(), text.end());
    return expected;
}
WriteResult send(UnoQDumpPort& native, const std::string& text) {
    const auto port = native.port();
    const auto before = hw.tx.size();
    const auto clocks_before = hw.clock_calls;
    const auto result = port.write(port.context, text.data(), text.size());
    VERIFY(hw.tx.size() - before <= config::DUMP_UART_STEP_BYTES);
    VERIFY(hw.clock_calls - clocks_before <= 64U);
    VERIFY(hw.rdr_reads == 0U);
    VERIFY(hw.irq_errors == 0U);
    return result;
}
void happy(unsigned length, unsigned mask) {
    hw.primask = mask;
    UnoQDumpPort native; if (!start(native)) return;
    VERIFY(hw.primask == mask);
    std::string text(length, 'A'); text.back() = '\n';
    WriteResult result;
    for (unsigned call = 0U; call < 40U; ++call) {
        result = send(native, text);
        VERIFY(hw.primask == mask);
        if (result.status != WriteStatus::PENDING) break;
        VERIFY(result.count == 0U);
    }
    VERIFY(result.status == WriteStatus::PROGRESS);
    VERIFY(result.count == length);
    VERIFY(hw.tx == packet(text));
    VERIFY(hw.tx.size() == length + 15U);
    VERIFY(hw.init_calls == 1U);
    const auto calls = hw.init_calls;
    VERIFY(native.begin(grant()) != NativeStatus::OK);
    VERIFY(hw.init_calls == calls);
}
void invalidGrant(unsigned kind) {
    UnoQDumpPort native; auto permissions = grant();
    if (kind == 0U) permissions.setup_phase = false;
    if (kind == 1U) permissions.exclusive_uart = false;
    if (kind == 2U) permissions.ready_pin_owned = false;
    if (kind == 3U) permissions.framing_clean = false;
    if (kind == 4U) hw.control = 1U;
    if (kind == 5U) hw.ipsr = 16U;
    VERIFY(native.begin(permissions) != NativeStatus::OK);
    VERIFY(hw.init_calls == 0U);
    VERIFY(hw.register_writes == 0U);
    VERIFY(hw.tx.empty());
}
void readiness(unsigned kind) {
    UnoQDumpPort native;
    if (kind == 0U) hw.ready = 0;
    if (kind == 1U) hw.configure_status = -5;
    if (kind == 2U) hw.init_status = -5;
    if (kind == 3U) hw.ready = -5;
    const auto status = native.begin(grant());
    if (kind == 1U || kind == 2U || kind == 3U) { VERIFY(status != NativeStatus::OK); return; }
    VERIFY(status == NativeStatus::OK);
    VERIFY(!native.ready());
    const auto result = send(native, "X\n");
    VERIFY(result.status == WriteStatus::ERROR);
    VERIFY(result.count == 0U);
    VERIFY(hw.tx.empty());
}
void pending(unsigned kind) {
    UnoQDumpPort native; if (!start(native)) return;
    if (kind == 0U) LPUART1->ISR.value &= ~USART_ISR_TXE;
    if (kind == 1U) hw.txe_stop_after = 3U;
    const auto result = send(native, "abc\n");
    VERIFY(result.status == WriteStatus::PENDING);
    VERIFY(result.count == 0U);
    VERIFY(hw.tx.size() == (kind == 0U ? 0U : 3U));
    const auto before = hw.tx.size();
    VERIFY(send(native, "abc\n").status == WriteStatus::PENDING);
    VERIFY(hw.tx.size() == before);
    LPUART1->ISR.value |= USART_ISR_TXE;
    hw.txe_stop_after = 10000U;
    WriteResult final;
    for (unsigned n = 0U; n < 20U; ++n) {
        final = send(native, "abc\n");
        if (final.status != WriteStatus::PENDING) break;
    }
    VERIFY(final.status == WriteStatus::PROGRESS);
    VERIFY(hw.tx == packet("abc\n"));
}
void tcPending() {
    UnoQDumpPort native; if (!start(native)) return;
    hw.auto_tc = false;
    WriteResult result;
    for (unsigned n = 0U; n < 8U; ++n) result = send(native, "hello\n");
    VERIFY(result.status == WriteStatus::PENDING);
    VERIFY(hw.tx == packet("hello\n"));
    LPUART1->ISR.value |= USART_ISR_TC;
    result = send(native, "hello\n");
    VERIFY(result.status == WriteStatus::PROGRESS);
    VERIFY(result.count == 6U);
    VERIFY(hw.tx == packet("hello\n"));
}
void timeout(unsigned delta, bool wrap) {
    UnoQDumpPort native; if (!start(native)) return;
    if (wrap) hw.now = 0xFFFFFFF0U;
    LPUART1->ISR.value &= ~USART_ISR_TXE;
    VERIFY(send(native, "x").status == WriteStatus::PENDING);
    hw.now += delta;
    const auto result = send(native, "x");
    if (delta < config::DUMP_UART_PACKET_MS * 1000U) VERIFY(result.status == WriteStatus::PENDING);
    else { VERIFY(result.status == WriteStatus::ERROR); VERIFY(native.status() == NativeStatus::TIMEOUT); }
    VERIFY(hw.tx.empty());
}
void invalidPayload(unsigned kind) {
    UnoQDumpPort native; if (!start(native)) return;
    const auto port = native.port();
    std::string text = "abc\n";
    if (kind >= 4U) VERIFY(send(native, text).status == WriteStatus::PENDING);
    const auto before = hw.tx.size();
    WriteResult result;
    if (kind == 0U) result = port.write(port.context, nullptr, 1U);
    if (kind == 1U) result = port.write(port.context, text.data(), 0U);
    if (kind == 2U) { text.assign(65U, 'x'); result = send(native, text); }
    if (kind == 3U) { text = std::string("A\0B", 3U); result = send(native, text); }
    if (kind == 4U) result = send(native, "abd\n");
    if (kind == 5U) result = send(native, "abc");
    if (kind == 6U) { text.assign(1U, static_cast<char>(0xFF)); result = send(native, text); }
    VERIFY(result.status == WriteStatus::ERROR);
    VERIFY(result.count == 0U);
    VERIFY(hw.tx.size() == before);
}
void corruption(unsigned kind) {
    UnoQDumpPort native; if (!start(native)) return;
    switch (kind) {
    case 0: hw.control = 1U; break;
    case 1: hw.ipsr = 16U; break;
    case 2: hw.irq_enabled = 1U; break;
    case 3: hw.irq_pending = 1U; break;
    case 4: hw.irq_active = 1U; break;
    case 5: LPUART1->CR3.value |= USART_CR3_DMAT; break;
    case 6: LPUART1->CR1.value |= USART_CR1_TXEIE; break;
    case 7: LPUART1->CR2.value = 1U; break;
    case 8: RCC->APB3ENR.value = 0U; break;
    case 9: RCC->AHB2ENR1.value = 0U; break;
    case 10: RCC->APB3RSTR.value = RCC_APB3RSTR_LPUART1RST; break;
    case 11: GPIOG->AFR[0].value = 0U; break;
    case 12: GPIOG->PUPDR.value = 0U; break;
    case 13: uart_data.user_data = &api; break;
    case 14: uart_settings.baudrate = 9600U; break;
    case 15: clocks.bus = 0U; break;
    case 16: hw.ready = 0; break;
    case 17: hw.ready = -5; break;
    case 18: RCC->PLL1DIVR.value ^= 1U; break;
    case 19: LPUART1->BRR.value ^= 1U; break;
    default: dump_devices[0].config = nullptr; break;
    }
    const auto before = hw.register_writes;
    VERIFY(send(native, "abc").status == WriteStatus::ERROR);
    VERIFY(hw.tx.empty());
    if (kind < 5U || kind == 8U || kind == 9U || kind == 20U)
        VERIFY(hw.register_writes == before);
}
void cancel(bool lost_context) {
    UnoQDumpPort native; if (!start(native)) return;
    VERIFY(send(native, "abc\n").status == WriteStatus::PENDING);
    const auto before = hw.tx;
    const auto writes = hw.register_writes;
    if (lost_context) hw.control = 1U;
    const auto port = native.port(); port.cancel(port.context);
    VERIFY(native.status() == NativeStatus::POISONED);
    if (lost_context) VERIFY(hw.register_writes == writes);
    else VERIFY((LPUART1->CR1.value & (USART_CR1_UE | USART_CR1_TE)) == 0U);
    hw.control = 0U;
    VERIFY(send(native, "abc\n").status == WriteStatus::ERROR);
    VERIFY(hw.tx == before);
    VERIFY(native.begin(grant()) != NativeStatus::OK);
}
void stepBudget(unsigned increment) {
    UnoQDumpPort native; if (!start(native)) return;
    hw.clock_step = increment;
    hw.call_started = hw.now;
    hw.enforce_step_age = true;
    const auto result = send(native, std::string(64U, 'x'));
    VERIFY(result.count == 0U);
    VERIFY(hw.tx.size() <= 8U);
    if (increment >= config::DUMP_UART_STEP_US) VERIFY(hw.tx.empty());
}
void initialMetadata(unsigned kind) {
    switch (kind) {
    case 0: dump_clock_good = false; break;
    case 1: uart_metadata.usart = nullptr; break;
    case 2: uart_metadata.clock = nullptr; break;
    case 3: uart_metadata.pclken = nullptr; break;
    case 4: uart_metadata.pclk_len = 0U; break;
    case 5: uart_metadata.fifo_enable = true; break;
    case 6: uart_data.uart_cfg = nullptr; break;
    case 7: uart_settings.flow_ctrl = 1U; break;
    case 8: gpio_metadata.port_pin_mask = 0U; break;
    case 9: gpio_api.pin_configure = nullptr; break;
    case 10: gpio_api.port_get_raw = nullptr; break;
    case 11: LPUART1->BRR.value = 355555U; break;
    case 12: LPUART1->PRESC.value = 1U; break;
    case 13: RCC->PLL1CFGR.value |= RCC_PLL1CFGR_PLL1MBOOST; break;
    case 14: RCC->CCIPR3.value |= RCC_CCIPR3_LPUART1SEL; break;
    default: states[1].initialized = false; break;
    }
    UnoQDumpPort native;
    VERIFY(native.begin(grant()) != NativeStatus::OK);
    VERIFY(hw.tx.empty());
    VERIFY(!native.ready());
}
bool sameFailure(const FailureRecord& a, const FailureRecord& b) {
    return a.reason == b.reason && a.site == b.site && a.cleanup == b.cleanup &&
        a.cleanup_ownership == b.cleanup_ownership && a.ownership_evaluated == b.ownership_evaluated &&
        a.packet_offset == b.packet_offset && a.packet_size == b.packet_size && a.payload_size == b.payload_size;
}
void firstFailure(unsigned kind) {
    UnoQDumpPort native; VERIFY(native.firstFailure().site == FailureSite::NONE);
    if (!start(native)) return;
    hw.txe_stop_after = 3U;
    VERIFY(send(native, "abc\n").status == WriteStatus::PENDING);
    const auto port = native.port();
    if (kind == 0U) hw.ready = 0;
    if (kind == 1U) hw.now += 100000U;
    if (kind == 2U) hw.control = 1U;
    if (kind == 3U) hw.irq_enabled = 1U;
    if (kind == 4U) LPUART1->CR3.value = USART_CR3_DMAT;
    if (kind == 5U) port.cancel(port.context);
    else VERIFY(send(native, "abc\n").status == WriteStatus::ERROR);
    const auto reads = hw.register_reads, clocks = hw.clock_calls;
    const auto saved = native.firstFailure();
    VERIFY(hw.register_reads == reads && hw.clock_calls == clocks);
    const NativeStatus reasons[] = {NativeStatus::READY_LOW, NativeStatus::TIMEOUT, NativeStatus::CONTEXT,
        NativeStatus::OWNERSHIP, NativeStatus::REGISTER, NativeStatus::OK};
    const FailureSite sites[] = {FailureSite::TRANSMIT_READY, FailureSite::TRANSMIT_DEADLINE,
        FailureSite::WRITE_CONTEXT, FailureSite::WRITE_OWNERSHIP, FailureSite::WRITE_OWNERSHIP, FailureSite::CANCEL};
    VERIFY(saved.reason == reasons[kind] && saved.site == sites[kind]);
    VERIFY(saved.packet_offset == 3U && saved.packet_size == 19U && saved.payload_size == 4U);
    VERIFY(saved.cleanup == (kind == 2U ? CleanupDisposition::SKIPPED_CONTEXT :
        kind == 3U || kind == 4U ? CleanupDisposition::SKIPPED_OWNERSHIP : CleanupDisposition::VERIFIED));
    VERIFY(saved.ownership_evaluated == (kind != 2U));
    VERIFY(saved.cleanup_ownership == (kind == 2U ? NativeStatus::NOT_INITIALIZED :
        kind == 3U ? NativeStatus::OWNERSHIP : kind == 4U ? NativeStatus::REGISTER : NativeStatus::OK));
    port.cancel(port.context); VERIFY(native.status() == NativeStatus::POISONED);
    const auto writes = hw.register_writes;
    VERIFY(!native.ready()); VERIFY(send(native, "abc\n").status == WriteStatus::ERROR);
    VERIFY(native.begin(grant()) == NativeStatus::POISONED); port.cancel(port.context);
    VERIFY(sameFailure(saved, native.firstFailure())); VERIFY(hw.register_writes == writes);
    VERIFY(hw.tx.size() == 3U);
}
} // namespace

device dump_devices[4] = {{&uart_metadata, &uart_data, &api, &states[0]},
    {&gpio_metadata, &api, &gpio_api, &states[1]}, {&api, &api, &api, &states[2]}, {&api, &api, &api, &states[3]}};
bool dump_clock_good = true;
Reg::operator std::uint32_t() const volatile {
    ++hw.register_reads;
    if (this == &LPUART1->RDR) ++hw.rdr_reads;
    return value;
}
void Reg::operator=(std::uint32_t v) volatile {
    ++hw.register_writes; value = v;
    if (this == &LPUART1->TDR) {
        if (hw.enforce_step_age) VERIFY(hw.last_clock - hw.call_started < config::DUMP_UART_STEP_US);
        hw.tx.push_back(static_cast<unsigned char>(v));
        if (!hw.auto_tc) LPUART1->ISR.value &= ~USART_ISR_TC;
        if (hw.tx.size() >= hw.txe_stop_after) LPUART1->ISR.value &= ~USART_ISR_TXE;
    }
}
unsigned long micros() { ++hw.clock_calls; const auto result = hw.now; hw.last_clock = result; hw.now += hw.clock_step; return result; }
std::uint32_t __get_CONTROL() { return hw.control; }
std::uint32_t __get_IPSR() { return hw.ipsr; }
std::uint32_t __get_PRIMASK() { return hw.primask; }
void __disable_irq() { ++hw.disable_calls; hw.primask = 1U; }
void __set_PRIMASK(std::uint32_t value) { hw.primask = value; }
void __DMB() {}
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type irq) { if (irq != LPUART1_IRQn) ++hw.irq_errors; return hw.irq_enabled; }
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type irq) { if (irq != LPUART1_IRQn) ++hw.irq_errors; return hw.irq_pending; }
std::uint32_t NVIC_GetActive(IRQn_Type irq) { if (irq != LPUART1_IRQn) ++hw.irq_errors; return hw.irq_active; }
void NVIC_DisableIRQ(IRQn_Type irq) { if (irq != LPUART1_IRQn) ++hw.irq_errors; hw.irq_enabled = 0U; }
void NVIC_ClearPendingIRQ(IRQn_Type irq) { if (irq != LPUART1_IRQn) ++hw.irq_errors; hw.irq_pending = 0U; }
bool device_is_ready(const device* dev) { return dev && dev->state && dev->state->initialized && dev->state->init_res == 0U; }
int device_init(const device* dev) { ++hw.init_calls; if (hw.init_status == 0) dev->state->initialized = true; return hw.init_status; }
int gpio_pin_configure_dt(const gpio_dt_spec* spec, gpio_flags_t flags) {
    ++hw.configure_calls;
    VERIFY(spec->port == &dump_devices[1]); VERIFY(spec->pin == 13U);
    VERIFY(flags == (GPIO_INPUT | GPIO_PULL_DOWN));
    if (hw.configure_status == 0) GPIOG->PUPDR.value |= 2U << 26U;
    return hw.configure_status;
}
int gpio_pin_get_dt(const gpio_dt_spec* spec) {
    ++hw.ready_calls; VERIFY(spec->port == &dump_devices[1]); VERIFY(spec->pin == 13U);
    return hw.ready;
}
int main(int argc, char** argv) {
    initialize();
    const std::string name = argc > 1 ? argv[1] : "happy";
    const unsigned value = argc > 2 ? static_cast<unsigned>(std::strtoul(argv[2], nullptr, 10)) : 0U;
    if (name == "happy") happy(value == 0U ? 64U : value, argc > 3 ? 1U : 0U);
    else if (name == "grant") invalidGrant(value);
    else if (name == "ready") readiness(value);
    else if (name == "pending") pending(value);
    else if (name == "tc") tcPending();
    else if (name == "timeout") timeout(value, argc > 3);
    else if (name == "payload") invalidPayload(value);
    else if (name == "corruption") corruption(value);
    else if (name == "cancel") cancel(value != 0U);
    else if (name == "budget") stepBudget(value);
    else if (name == "metadata") initialMetadata(value);
    else if (name == "first_failure") firstFailure(value);
    else return 2;
    std::printf("checks=%u failures=%d tx=%zu clock_calls=%u\n", checks, failed, hw.tx.size(), hw.clock_calls);
    return failed == 0 ? 0 : 1;
}

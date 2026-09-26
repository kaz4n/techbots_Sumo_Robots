// Emits bounded transmit-only MessagePack notifications through the internal UART.
// A lifetime owner and permanent poison prevent reuse of an uncertain byte stream.
// Independent legacy/FIFO substitutes and actual target inspection test D090/D117.
#include "dump_uart_unoq.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <Arduino.h>
#include <cmsis_core.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/clock_control/stm32_clock_control.h>
#include <serial/uart_stm32.h>
#include <stm32u5xx_ll_rcc.h>
#include <cstddef>

namespace recorder::dump {
namespace {
// Installed core 1.0.0 / Zephyr 1743741760ee; see P2_dump_native_audit.md,
// pinned uart_stm32.h, offline_gdb.txt and generated DT in P2_dump_raw/native.
UnoQDumpPort* uart_owner = nullptr;
constexpr std::uint32_t TX_MODE = USART_CR1_UE | USART_CR1_TE;
constexpr std::uint32_t READY_SHIFT = 26U; // Loader's PG13 input/pulldown.
constexpr std::uint32_t TX_SHIFT = 14U; // Installed LPUART1 TX is PG7/AF8.
constexpr std::uint8_t PREFIX[] = {
    0x93U, 0x02U, 0xA9U, 'm', 'o', 'n', '/', 'w', 'r', 'i', 't', 'e', 0x91U
};
static_assert(sizeof(PREFIX) == 13U, "D9 length adds two bytes: 79 with 64 payload");
static_assert(config::DUMP_PAYLOAD_BYTES > 0U && config::DUMP_PAYLOAD_BYTES <= 64U);
static_assert(config::DUMP_UART_STEP_BYTES > 0U && config::DUMP_UART_STEP_BYTES <= 8U);
static_assert(config::DUMP_UART_STEP_US > 0U && config::DUMP_UART_STEP_US <= 80U);
static_assert(config::DUMP_UART_PACKET_MS > 0U && config::DUMP_UART_PACKET_MS <= 100U);

const device* uartDevice() { return DEVICE_DT_GET(DT_NODELABEL(lpuart1)); }
const gpio_dt_spec ready_pad = GPIO_DT_SPEC_GET_BY_IDX(
    DT_PATH(zephyr_user), control_gpios, 0);
bool threadContext() { return (__get_CONTROL() & 1U) == 0U && __get_IPSR() == 0U; }
std::uint32_t clockUs() { return static_cast<std::uint32_t>(micros()); }

class InterruptMask {
public:
    InterruptMask() : saved_(__get_PRIMASK()) { __disable_irq(); }
    ~InterruptMask() { __DMB(); __set_PRIMASK(saved_); }
private:
    std::uint32_t saved_;
};

bool deviceMetadata() {
    const auto* dev = uartDevice();
    if (dev == nullptr || dev->config == nullptr || dev->data == nullptr ||
        dev->api == nullptr || dev->state == nullptr) return false;
    const auto* cfg = static_cast<const uart_stm32_config*>(dev->config);
    const auto* data = static_cast<const uart_stm32_data*>(dev->data);
    return cfg->usart == LPUART1_NS && cfg->clock == DEVICE_DT_GET(DT_NODELABEL(rcc)) &&
        cfg->pclken != nullptr && cfg->pclk_len == 1U && cfg->pclken[0].bus == 0xA8U &&
        cfg->pclken[0].enr == RCC_APB3ENR_LPUART1EN && cfg->pclken[0].div == 0U &&
        !cfg->single_wire && !cfg->tx_rx_swap && !cfg->rx_invert && !cfg->tx_invert &&
        !cfg->de_enable && !cfg->fifo_enable && cfg->pcfg != nullptr &&
        cfg->irq_config_func != nullptr && data->uart_cfg != nullptr &&
        data->user_cb == nullptr && data->user_data == nullptr &&
        data->uart_cfg->baudrate == 115200U &&
        data->uart_cfg->parity == UART_CFG_PARITY_NONE &&
        data->uart_cfg->stop_bits == UART_CFG_STOP_BITS_1 &&
        data->uart_cfg->data_bits == UART_CFG_DATA_BITS_8 &&
        data->uart_cfg->flow_ctrl == UART_CFG_FLOW_CTRL_NONE;
}

bool metadata() {
    const auto* gpio = ready_pad.port;
    if (!deviceMetadata() || gpio == nullptr || gpio->config == nullptr ||
        gpio->data == nullptr || gpio->api == nullptr || gpio->state == nullptr)
        return false;
    const auto* cfg = static_cast<const gpio_driver_config*>(gpio->config);
    const auto* api = static_cast<const gpio_driver_api*>(gpio->api);
    return DT_REG_ADDR(DT_NODELABEL(lpuart1)) == reinterpret_cast<std::uintptr_t>(LPUART1_NS) &&
        DT_IRQN(DT_NODELABEL(lpuart1)) == 66 && LPUART1_IRQn == 66 &&
        DT_PROP(DT_NODELABEL(lpuart1), zephyr_deferred_init) == 1 &&
        DT_PROP(DT_NODELABEL(lpuart1), current_speed) == 115200U &&
        offsetof(USART_TypeDef, ISR) == 0x1CU && offsetof(USART_TypeDef, TDR) == 0x28U &&
        gpio == DEVICE_DT_GET(DT_NODELABEL(gpiog)) && ready_pad.pin == 13U &&
        ready_pad.dt_flags == 0U && (cfg->port_pin_mask & (1U << 13U)) != 0U &&
        api->pin_configure != nullptr && api->port_get_raw != nullptr;
}

bool clocksAvailable() {
    return device_is_ready(DEVICE_DT_GET(DT_NODELABEL(rcc))) &&
        device_is_ready(ready_pad.port) &&
        (RCC_NS->APB3ENR & RCC_APB3ENR_LPUART1EN) != 0U &&
        (RCC_NS->APB3RSTR & RCC_APB3RSTR_LPUART1RST) == 0U &&
        (RCC_NS->AHB2ENR1 & RCC_AHB2ENR1_GPIOGEN) != 0U &&
        (RCC_NS->AHB2RSTR1 & RCC_AHB2RSTR1_GPIOGRST) == 0U;
}

bool nominalClock() {
    // Same installed nominal MSI/PLL configuration checked by the ADC owner.
    // This is not independent oscillator accuracy or whole-tick qualification.
    return LL_RCC_GetSysClkSource() == LL_RCC_SYS_CLKSOURCE_STATUS_PLL1 &&
        LL_RCC_GetAHBPrescaler() == LL_RCC_SYSCLK_DIV_1 &&
        LL_RCC_GetAPB3Prescaler() == LL_RCC_APB3_DIV_1 &&
        LL_RCC_PLL1_GetMainSource() == LL_RCC_PLL1SOURCE_MSIS &&
        LL_RCC_PLL1_GetDivider() == 1U && LL_RCC_PLL1_GetN() == 80U &&
        LL_RCC_PLL1_GetR() == 2U && LL_RCC_PLL1_IsReady() == 1U &&
        LL_RCC_PLL1_IsEnabledDomain_SYS() == 1U && LL_RCC_PLL1FRACN_IsEnabled() == 0U &&
        LL_RCC_MSI_IsEnabledRangeSelect() == 1U &&
        LL_RCC_MSIS_GetRange() == LL_RCC_MSISRANGE_4 && LL_RCC_MSIS_IsReady() == 1U &&
        LL_RCC_IsEnabledPLLMode() == 1U && LL_RCC_GetMSIPLLMode() == LL_RCC_PLLMODE_MSIS &&
        (RCC_NS->PLL1CFGR & RCC_PLL1CFGR_PLL1MBOOST) == 0U &&
        (RCC_NS->CCIPR3 & RCC_CCIPR3_LPUART1SEL) == 0U;
}

std::uint32_t clockRegister(unsigned index) {
    switch (index) {
    case 0U: return RCC_NS->CFGR1;
    case 1U: return RCC_NS->CFGR2;
    case 2U: return RCC_NS->CFGR3;
    case 3U: return RCC_NS->PLL1CFGR;
    case 4U: return RCC_NS->PLL1DIVR;
    case 5U: return RCC_NS->PLL1FRACR;
    case 6U: return RCC_NS->ICSCR1;
    default: return RCC_NS->CCIPR3 & RCC_CCIPR3_LPUART1SEL;
    }
}

bool padsOwned() {
    return (GPIOG_NS->LCKR & ((1U << 7U) | (1U << 13U))) == 0U &&
        ((GPIOG_NS->MODER >> READY_SHIFT) & 3U) == 0U &&
        ((GPIOG_NS->PUPDR >> READY_SHIFT) & 3U) == 2U &&
        ((GPIOG_NS->MODER >> TX_SHIFT) & 3U) == 2U &&
        ((GPIOG_NS->OTYPER >> 7U) & 1U) == 0U &&
        ((GPIOG_NS->AFR[0] >> 28U) & 15U) == 8U;
}

bool irqIdle() {
    return NVIC_GetEnableIRQ(LPUART1_IRQn) == 0U &&
        NVIC_GetPendingIRQ(LPUART1_IRQn) == 0U && NVIC_GetActive(LPUART1_IRQn) == 0U;
}
} // namespace

NativeStatus UnoQDumpPort::begin(const SetupGrant& grant) {
    if (attempted_ || poisoned_) { abort(NativeStatus::OK, FailureSite::REPEATED_BEGIN); return status_; }
    attempted_ = true;
    if (buffering_ != Buffering::LEGACY_SINGLE && buffering_ != Buffering::FIFO8)
        return setupFailure(NativeStatus::INVALID_ARGUMENT);
    if (!setupGrantAccepted(grant)) return setupFailure(NativeStatus::OWNERSHIP);
    if (!threadContext()) return setupFailure(NativeStatus::CONTEXT);
    if (uart_owner != nullptr) return setupFailure(NativeStatus::OWNERSHIP);
    if (!metadata() || !device_is_ready(ready_pad.port) ||
        !device_is_ready(DEVICE_DT_GET(DT_NODELABEL(rcc))))
        return setupFailure(NativeStatus::DEVICE);
    if (uartDevice()->state->initialized || uartDevice()->state->init_res != 0U ||
        !irqIdle()) return setupFailure(NativeStatus::OWNERSHIP);
    uart_owner = this; // Never released, including failed initialization.
    if (gpio_pin_configure_dt(&ready_pad, GPIO_INPUT | GPIO_PULL_DOWN) != 0)
        return setupFailure(NativeStatus::READY_ERROR);
    // Verified unbounded TEACK/REACK waits live ONLY here, in explicit setup.
    if (device_init(uartDevice()) != 0 || !device_is_ready(uartDevice()))
        return setupFailure(NativeStatus::DEVICE);
    const InterruptMask mask;
    if (!threadContext() || !metadata() || !clocksAvailable() || !nominalClock() ||
        NVIC_GetActive(LPUART1_IRQn) != 0U || NVIC_GetPendingIRQ(LPUART1_IRQn) != 0U)
        return setupFailure(NativeStatus::OWNERSHIP);
    if (LPUART1_NS->CR1 != (TX_MODE | USART_CR1_RE) || LPUART1_NS->CR2 != 0U ||
        LPUART1_NS->CR3 != 0U || LPUART1_NS->PRESC != 0U ||
        LPUART1_NS->BRR != 355556U ||
        (buffering_ == Buffering::FIFO8 && LPUART1_NS->AUTOCR != 0U))
        return setupFailure(NativeStatus::REGISTER);
    NVIC_DisableIRQ(LPUART1_IRQn);
    NVIC_ClearPendingIRQ(LPUART1_IRQn);
    if (buffering_ == Buffering::FIFO8) return status_ = beginFifo();
    LPUART1_NS->CR1 = TX_MODE; // No RX, interrupt, FIFO or DMA service.
    __DMB();
    baud_register_ = LPUART1_NS->BRR;
    for (unsigned i = 0U; i < 8U; ++i) clock_registers_[i] = clockRegister(i);
    initialized_ = true;
    status_ = ownership();
    if (status_ != NativeStatus::OK) {
        const auto reason = status_;
        abort(reason, FailureSite::SETUP_OWNERSHIP);
        return status_ = reason;
    }
    // LOW is legitimate at setup, particularly with Immediate startup.
    const auto ready_status = sampleReady();
    if (ready_status == NativeStatus::READY_ERROR) {
        abort(ready_status, FailureSite::SETUP_READY);
        return status_ = ready_status;
    }
    return status_ = NativeStatus::OK;
}

NativeStatus UnoQDumpPort::ownership() const {
    const auto mode = TX_MODE | (buffering_ == Buffering::FIFO8 ? USART_CR1_FIFOEN : 0U);
    return ownedState(mode, mode, true);
}

NativeStatus UnoQDumpPort::ownedState(std::uint32_t expected, std::uint32_t alternate,
                                    bool live) const {
    if (!threadContext()) return NativeStatus::CONTEXT;
    if (live && !initialized_) return NativeStatus::NOT_INITIALIZED;
    if (uart_owner != this) return NativeStatus::OWNERSHIP;
    if (!metadata() || !device_is_ready(uartDevice())) return NativeStatus::DEVICE;
    if (!clocksAvailable() || !nominalClock() || !padsOwned() || !irqIdle())
        return NativeStatus::OWNERSHIP;
    for (unsigned i = 0U; i < 8U; ++i)
        if (clock_registers_[i] != clockRegister(i)) return NativeStatus::OWNERSHIP;
    const auto mode = static_cast<std::uint32_t>(LPUART1_NS->CR1);
    if ((mode != expected && mode != alternate) || LPUART1_NS->CR2 != 0U || LPUART1_NS->CR3 != 0U ||
        LPUART1_NS->PRESC != 0U || LPUART1_NS->BRR != baud_register_ ||
        (live && (LPUART1_NS->ISR & USART_ISR_TEACK) == 0U) ||
        (buffering_ == Buffering::FIFO8 && LPUART1_NS->AUTOCR != 0U))
        return NativeStatus::REGISTER;
    return NativeStatus::OK;
}

NativeStatus UnoQDumpPort::beginFifo() {
    // No polling: immediate readbacks may conservatively refuse physical setup.
    baud_register_ = 355556U;
    for (unsigned i = 0U; i < 8U; ++i) clock_registers_[i] = clockRegister(i);
    std::uint32_t verified = TX_MODE | USART_CR1_RE;
    for (unsigned i = 0U; i < 3U; ++i) {
        const auto reason = ownedState(verified, verified, false);
        if (reason != NativeStatus::OK)
            return i == 0U ? setupFailure(reason, FailureSite::FIFO_OWNERSHIP) :
                failFifo(reason, FailureSite::FIFO_OWNERSHIP, verified, verified);
        const std::uint32_t attempted = i == 0U ? 0U :
            USART_CR1_TE | USART_CR1_FIFOEN | (i == 2U ? USART_CR1_UE : 0U);
        LPUART1_NS->CR1 = attempted;
        __DMB();
        if (LPUART1_NS->CR1 != attempted)
            return failFifo(NativeStatus::REGISTER, FailureSite::FIFO_READBACK, verified, attempted);
        verified = attempted;
    }
    initialized_ = true;
    const auto reason = ownership();
    if (reason != NativeStatus::OK) return failFifo(reason, FailureSite::FIFO_OWNERSHIP, verified, verified);
    const auto ready_status = sampleReady();
    if (ready_status == NativeStatus::READY_ERROR)
        return failFifo(ready_status, FailureSite::SETUP_READY, verified, verified);
    return NativeStatus::OK;
}

NativeStatus UnoQDumpPort::failFifo(NativeStatus reason, FailureSite site, std::uint32_t verified,
                                  std::uint32_t attempted) {
    // Setup owns the interrupt mask. Missing TEACK alone cannot bypass inhibit.
    const bool first = remember(reason, site);
    const auto owner_status = ownedState(verified, attempted, false);
    if (owner_status == NativeStatus::OK) {
        LPUART1_NS->CR1 = 0U;
        __DMB();
        cleanup_verified_ = LPUART1_NS->CR1 == 0U;
    }
    if (first) {
        first_failure_.ownership_evaluated = true;
        first_failure_.cleanup_ownership = owner_status;
        first_failure_.cleanup = owner_status != NativeStatus::OK ? CleanupDisposition::SKIPPED_OWNERSHIP :
            cleanup_verified_ ? CleanupDisposition::VERIFIED : CleanupDisposition::READBACK_FAILED;
    }
    poison();
    return status_ = reason;
}

NativeStatus UnoQDumpPort::sampleReady() const {
    const int value = gpio_pin_get_dt(&ready_pad);
    if (value != 0 && value != 1) return NativeStatus::READY_ERROR;
    return value == 1 ? NativeStatus::OK : NativeStatus::READY_LOW;
}

bool UnoQDumpPort::ready() {
    if (poisoned_) { status_ = NativeStatus::POISONED; return false; }
    if (!threadContext()) { status_ = NativeStatus::CONTEXT; return false; }
    const InterruptMask mask;
    status_ = ownership();
    if (status_ == NativeStatus::OK) status_ = sampleReady();
    return status_ == NativeStatus::OK;
}

Port UnoQDumpPort::port() { return {this, write, cancel}; }
WriteResult UnoQDumpPort::write(void* context, const char* data, std::size_t count) {
    return context == nullptr ? WriteResult{} :
        static_cast<UnoQDumpPort*>(context)->advance(data, count);
}
void UnoQDumpPort::cancel(void* context) {
    if (context != nullptr) static_cast<UnoQDumpPort*>(context)->abort();
}

bool UnoQDumpPort::prepare(const char* data, std::size_t count) {
    if (data == nullptr || count == 0U || count > config::DUMP_PAYLOAD_BYTES) return false;
    if (active_ && count != payload_size_) return false;
    for (std::size_t i = 0U; i < count; ++i) {
        const auto byte = static_cast<unsigned char>(data[i]);
        if ((byte != '\n' && (byte < 32U || byte > 126U)) ||
            (active_ && data[i] != payload_[i])) return false;
    }
    if (active_) return true;
    // mon/write has NINE bytes: a fixstr A9 and a one-element argument array.
    for (std::size_t i = 0U; i < sizeof(PREFIX); ++i) packet_[i] = PREFIX[i];
    packet_[sizeof(PREFIX)] = 0xD9U;
    packet_[sizeof(PREFIX) + 1U] = static_cast<std::uint8_t>(count);
    for (std::size_t i = 0U; i < count; ++i) {
        payload_[i] = data[i];
        packet_[sizeof(PREFIX) + 2U + i] = static_cast<std::uint8_t>(data[i]);
    }
    payload_size_ = count;
    packet_size_ = sizeof(PREFIX) + 2U + count;
    offset_ = 0U;
    started_us_ = clockUs();
    active_ = true;
    return true;
}

bool UnoQDumpPort::withinDeadline(std::uint32_t step_started) const {
    const auto now = clockUs();
    return static_cast<std::uint32_t>(now - step_started) < config::DUMP_UART_STEP_US &&
        static_cast<std::uint32_t>(now - started_us_) < config::DUMP_UART_PACKET_MS * 1000U;
}

WriteResult UnoQDumpPort::advance(const char* data, std::size_t count) {
    if (poisoned_) return fail(NativeStatus::POISONED, FailureSite::WRITE_POISONED);
    if (!threadContext()) return fail(NativeStatus::CONTEXT, FailureSite::WRITE_CONTEXT);
    const auto step_started = clockUs();
    const InterruptMask mask;
    const auto owner_status = ownership();
    if (owner_status != NativeStatus::OK) return fail(owner_status, FailureSite::WRITE_OWNERSHIP);
    if (!prepare(data, count)) return fail(NativeStatus::INVALID_ARGUMENT, FailureSite::WRITE_ARGUMENT);
    return transmit(step_started);
}

WriteResult UnoQDumpPort::transmit(std::uint32_t step_started) {
    for (std::uint32_t i = 0U; i < config::DUMP_UART_STEP_BYTES && offset_ < packet_size_; ++i) {
        const auto owner_status = ownership();
        if (owner_status != NativeStatus::OK) return fail(owner_status, FailureSite::TRANSMIT_OWNERSHIP);
        const auto ready_status = sampleReady();
        if (ready_status != NativeStatus::OK) return fail(ready_status, FailureSite::TRANSMIT_READY);
        if (!withinDeadline(step_started)) return fail(NativeStatus::TIMEOUT, FailureSite::TRANSMIT_DEADLINE);
        // Bit7 means TXE in legacy mode and TXFNF in the selected FIFO mode.
        // Unlike the public ISR-only API, this is one nonwaiting Thread store.
        if ((LPUART1_NS->ISR & USART_ISR_TXE) == 0U) break;
        if (!withinDeadline(step_started)) return fail(NativeStatus::TIMEOUT, FailureSite::STORE_DEADLINE);
        LPUART1_NS->TDR = packet_[offset_++];
    }
    const auto owner_status = ownership();
    if (owner_status != NativeStatus::OK) return fail(owner_status, FailureSite::COMPLETE_OWNERSHIP);
    const auto ready_status = sampleReady();
    if (ready_status != NativeStatus::OK) return fail(ready_status, FailureSite::COMPLETE_READY);
    if (!withinDeadline(step_started)) return fail(NativeStatus::TIMEOUT, FailureSite::COMPLETE_DEADLINE);
    const bool complete = offset_ == packet_size_ && (LPUART1_NS->ISR & USART_ISR_TC) != 0U;
    if (!withinDeadline(step_started)) return fail(NativeStatus::TIMEOUT, FailureSite::TC_DEADLINE);
    status_ = NativeStatus::OK;
    if (!complete) return {WriteStatus::PENDING, 0U};
    active_ = false;
    const auto submitted = payload_size_;
    payload_size_ = packet_size_ = offset_ = 0U;
    return {WriteStatus::PROGRESS, submitted};
}

bool UnoQDumpPort::remember(NativeStatus reason, FailureSite site) {
    if (first_failure_.site != FailureSite::NONE) return false;
    first_failure_.reason = reason;
    first_failure_.site = site;
    first_failure_.packet_offset = static_cast<std::uint8_t>(offset_);
    first_failure_.packet_size = static_cast<std::uint8_t>(packet_size_);
    first_failure_.payload_size = static_cast<std::uint8_t>(payload_size_);
    return true;
}

NativeStatus UnoQDumpPort::setupFailure(NativeStatus reason, FailureSite site) {
    remember(reason, site);
    return status_ = reason;
}

WriteResult UnoQDumpPort::fail(NativeStatus reason, FailureSite site) {
    abort(reason, site);
    status_ = reason;
    return {WriteStatus::ERROR, 0U};
}

void UnoQDumpPort::abort(NativeStatus reason, FailureSite site) {
    const bool first = remember(reason, site);
    auto cleanup = poisoned_ ? CleanupDisposition::SKIPPED_POISONED : CleanupDisposition::SKIPPED_CONTEXT;
    auto owner_status = NativeStatus::NOT_INITIALIZED;
    bool evaluated = false;
    // No ownership means no write to potentially foreign peripheral registers.
    if (!poisoned_ && threadContext()) {
        const InterruptMask mask;
        owner_status = ownership();
        evaluated = true;
        cleanup = CleanupDisposition::SKIPPED_OWNERSHIP;
        if (owner_status == NativeStatus::OK) {
            LPUART1_NS->CR1 = 0U;
            __DMB();
            // Installed LL LPUART header:520-537 and RM0456 Rev6:p2882
            // document immediate discard on UE=0. Neither mode treats room or
            // a FIFO flush as proof of complete framing at the remote decoder.
            cleanup_verified_ = LPUART1_NS->CR1 == 0U;
            cleanup = cleanup_verified_ ? CleanupDisposition::VERIFIED : CleanupDisposition::READBACK_FAILED;
        }
    }
    if (first) {
        first_failure_.cleanup = cleanup;
        first_failure_.ownership_evaluated = evaluated;
        first_failure_.cleanup_ownership = owner_status;
    }
    poison();
}

void UnoQDumpPort::poison() {
    // Already shifted bytes cannot be recalled. No framing recovery is implied.
    active_ = false;
    payload_size_ = packet_size_ = offset_ = 0U;
    poisoned_ = true;
    status_ = NativeStatus::POISONED;
}
} // namespace recorder::dump
#endif

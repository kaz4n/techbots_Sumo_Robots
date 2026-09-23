// Transfers only the bounded MPU6050 requests on privately owned native I2C4.
// Exclusive ownership, one deadline and terminal local disable reject partial bytes.
// Independent installed-register fixtures and an inert target probe test this source.
#include "imu_bus_unoq.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <Arduino.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/clock_control/stm32_clock_control.h>
#include <stm32u5xx_ll_i2c.h>
#include <stm32u5xx_ll_gpio.h>
#include <stm32u5xx_ll_rcc.h>
#include <cstddef>

#define IMU_BUS_NODE DT_NODELABEL(i2c4)
#define IMU_SCL_NODE DT_PHANDLE_BY_IDX(IMU_BUS_NODE, pinctrl_0, 0)
#define IMU_SDA_NODE DT_PHANDLE_BY_IDX(IMU_BUS_NODE, pinctrl_0, 1)

namespace imu {
namespace {
constexpr std::uint32_t PINS = (1U << 12U) | (1U << 13U);
constexpr std::uint32_t MODE_MASK = (3U << 24U) | (3U << 26U);
constexpr std::uint32_t AF_MASK = (15U << 16U) | (15U << 20U);
constexpr std::uint32_t ERRORS = I2C_ISR_ARLO | I2C_ISR_BERR | I2C_ISR_NACKF |
    I2C_ISR_OVR | I2C_ISR_PECERR | I2C_ISR_TIMEOUT | I2C_ISR_ALERT;
constexpr std::uint32_t EVENTS = I2C_ISR_TXIS | I2C_ISR_RXNE | I2C_ISR_ADDR |
    I2C_ISR_STOPF | I2C_ISR_TC | I2C_ISR_TCR;
// Serialized whole-application ownership makes this an irreversible boot claim.
bool bus_claimed = false;
std::uint32_t clockUs() { return static_cast<std::uint32_t>(micros()); }
bool bounded(std::uint32_t n) { return n > 0U && n < 0x80000000U; }

bool configValid() {
    return (config::IMU_I2C_ADDRESS == 0x68U || config::IMU_I2C_ADDRESS == 0x69U) &&
        config::IMU_I2C_GPIO_PORT == 3U && config::IMU_I2C_SCL_PIN == 12U &&
        config::IMU_I2C_SDA_PIN == 13U && config::IMU_I2C_AF == 4U &&
        config::IMU_I2C_TIMINGR == 0x40EB202CU && bounded(config::IMU_I2C_SETUP_US) &&
        bounded(config::IMU_I2C_TRANSFER_US) && bounded(config::IMU_I2C_CLEANUP_US) &&
        bounded(config::IMU_I2C_MAX_POLLS);
}

bool registerAllowed(Register reg, bool writing) {
    switch (reg) {
    case Register::SAMPLE_DIVIDER: case Register::FILTER: case Register::GYRO_RANGE:
    case Register::ACCEL_RANGE: case Register::FIFO_ENABLE: case Register::INTERRUPT_CONFIG:
    case Register::INTERRUPT_ENABLE: case Register::USER_CONTROL: case Register::POWER_1:
    case Register::POWER_2: return true;
    case Register::INTERRUPT_STATUS: case Register::IDENTITY: return !writing;
    }
    return false;
}

bool padMetadataValid() {
    return DT_PROP_LEN(IMU_BUS_NODE, pinctrl_0) == 2U &&
        DT_PROP(IMU_SCL_NODE, pinmux) == 1924U && DT_PROP(IMU_SDA_NODE, pinmux) == 1956U &&
        DT_PROP(IMU_SCL_NODE, bias_pull_up) == 1 && DT_PROP(IMU_SDA_NODE, bias_pull_up) == 1 &&
        DT_PROP(IMU_SCL_NODE, bias_pull_down) == 0 && DT_PROP(IMU_SDA_NODE, bias_pull_down) == 0 &&
        DT_PROP(IMU_SCL_NODE, bias_disable) == 0 && DT_PROP(IMU_SDA_NODE, bias_disable) == 0 &&
        DT_PROP(IMU_SCL_NODE, drive_open_drain) == 1 && DT_PROP(IMU_SDA_NODE, drive_open_drain) == 1 &&
        DT_PROP(IMU_SCL_NODE, drive_push_pull) == 0 && DT_PROP(IMU_SDA_NODE, drive_push_pull) == 0 &&
        DT_ENUM_IDX(IMU_SCL_NODE, slew_rate) == 0 && DT_ENUM_IDX(IMU_SDA_NODE, slew_rate) == 0;
}

bool metadataValid() {
    return DT_REG_ADDR(IMU_BUS_NODE) == 0x40008400U &&
        DT_REG_ADDR(IMU_BUS_NODE) == reinterpret_cast<std::uintptr_t>(I2C4_NS) &&
        DT_REG_ADDR(DT_NODELABEL(gpiod)) == reinterpret_cast<std::uintptr_t>(GPIOD_NS) &&
        offsetof(I2C_TypeDef, ISR) == 0x18U && offsetof(I2C_TypeDef, AUTOCR) == 0x2CU &&
        DT_PROP(IMU_BUS_NODE, zephyr_deferred_init) == 1 &&
        DT_PROP(IMU_BUS_NODE, clock_frequency) == 400000U &&
        DT_IRQ_BY_IDX(IMU_BUS_NODE, 0, irq) == 101 && I2C4_EV_IRQn == 101 &&
        DT_IRQ_BY_IDX(IMU_BUS_NODE, 1, irq) == 100 && I2C4_ER_IRQn == 100 &&
        DT_PROP_LEN(IMU_BUS_NODE, clocks) == 1U &&
        DT_CLOCKS_CELL_BY_IDX(IMU_BUS_NODE, 0, bus) == 160U &&
        DT_CLOCKS_CELL_BY_IDX(IMU_BUS_NODE, 0, bits) == RCC_APB1ENR2_I2C4EN &&
        DT_PROP(DT_NODELABEL(rcc), clock_frequency) == 160000000U &&
        DT_PROP(DT_NODELABEL(rcc), ahb_prescaler) == 1U &&
        DT_PROP(DT_NODELABEL(rcc), apb1_prescaler) == 1U && padMetadataValid();
}

bool devicesAvailable() {
    const auto* bus = DEVICE_DT_GET(IMU_BUS_NODE);
    const auto* rcc = DEVICE_DT_GET(DT_NODELABEL(rcc));
    const auto* gpio = DEVICE_DT_GET(DT_NODELABEL(gpiod));
    return bus != nullptr && bus->state != nullptr && !bus->state->initialized &&
        bus->state->init_res == 0U && rcc != nullptr && rcc->api != nullptr &&
        device_is_ready(rcc) && gpio != nullptr && device_is_ready(gpio);
}

bool irqsUnused() {
    const IRQn_Type irqs[] = {I2C4_ER_IRQn, I2C4_EV_IRQn};
    for (const auto irq : irqs) {
        if (NVIC_GetEnableIRQ(irq) != 0U || NVIC_GetPendingIRQ(irq) != 0U ||
            NVIC_GetActive(irq) != 0U) return false;
    }
    return true;
}

bool clocksValid() {
    // Configuration and readiness do not prove MSI auto-calibration lock.
    return LL_RCC_GetSysClkSource() == LL_RCC_SYS_CLKSOURCE_STATUS_PLL1 &&
        LL_RCC_GetAHBPrescaler() == LL_RCC_SYSCLK_DIV_1 &&
        LL_RCC_GetAPB1Prescaler() == LL_RCC_APB1_DIV_1 &&
        LL_RCC_PLL1_GetMainSource() == LL_RCC_PLL1SOURCE_MSIS &&
        LL_RCC_PLL1_GetDivider() == 1U && LL_RCC_PLL1_GetN() == 80U &&
        LL_RCC_PLL1_GetR() == 2U && LL_RCC_PLL1_IsReady() == 1U &&
        LL_RCC_PLL1_IsEnabledDomain_SYS() == 1U && LL_RCC_PLL1FRACN_IsEnabled() == 0U &&
        LL_RCC_MSI_IsEnabledRangeSelect() == 1U &&
        LL_RCC_MSIS_GetRange() == LL_RCC_MSISRANGE_4 && LL_RCC_MSIS_IsReady() == 1U &&
        LL_RCC_IsEnabledPLLMode() == 1U && LL_RCC_GetMSIPLLMode() == LL_RCC_PLLMODE_MSIS &&
        (RCC_NS->PLL1CFGR & RCC_PLL1CFGR_PLL1MBOOST) == 0U &&
        (RCC_NS->CCIPR1 & RCC_CCIPR1_I2C4SEL) == 0U;
}

bool suppliesValid() {
    if ((RCC_NS->AHB3ENR & RCC_AHB3ENR_PWREN) == 0U) return false;
    const auto requested = PWR_VOSR_VOS | PWR_VOSR_VOSRDY | PWR_VOSR_BOOSTEN | PWR_VOSR_BOOSTRDY;
    const auto applied = PWR_SVMSR_ACTVOS | PWR_SVMSR_ACTVOSRDY;
    return (PWR_NS->SVMCR & PWR_SVMCR_ASV) != 0U &&
        (PWR_NS->VOSR & requested) == requested && (PWR_NS->SVMSR & applied) == applied;
}

bool environmentValid() {
    return devicesAvailable() && irqsUnused() && suppliesValid() && clocksValid() &&
        (RCC_NS->AHB2ENR1 & RCC_AHB2ENR1_GPIODEN) != 0U &&
        LL_GPIO_IsPinLocked(GPIOD_NS, 1U << 12U) == 0U &&
        LL_GPIO_IsPinLocked(GPIOD_NS, 1U << 13U) == 0U;
}

bool padsPristine() {
    return (GPIOD_NS->MODER & MODE_MASK) == MODE_MASK &&
           (GPIOD_NS->PUPDR & MODE_MASK) == 0U;
}

bool pristineBus() {
    return I2C4_NS->CR1 == 0U && I2C4_NS->CR2 == 0U && I2C4_NS->OAR1 == 0U &&
        I2C4_NS->OAR2 == 0U && I2C4_NS->TIMINGR == 0U && I2C4_NS->TIMEOUTR == 0U &&
        I2C4_NS->AUTOCR == 0U && I2C4_NS->ISR == I2C_ISR_TXE;
}

bool enableClock() {
    const auto* rcc = DEVICE_DT_GET(DT_NODELABEL(rcc));
    const auto* api = static_cast<const clock_control_driver_api*>(rcc->api);
    if (api->on == nullptr) return false;
    stm32_pclken clock{};
    clock.bus = DT_CLOCKS_CELL_BY_IDX(IMU_BUS_NODE, 0, bus);
    clock.enr = DT_CLOCKS_CELL_BY_IDX(IMU_BUS_NODE, 0, bits);
    return api->on(rcc, &clock) == 0 && (RCC_NS->APB1ENR2 & RCC_APB1ENR2_I2C4EN) != 0U;
}

BusStatus errorStatus(std::uint32_t flags) {
    if ((flags & I2C_ISR_ARLO) != 0U) return BusStatus::ARBITRATION_LOST;
    if ((flags & I2C_ISR_BERR) != 0U) return BusStatus::BUS_ERROR;
    if ((flags & I2C_ISR_NACKF) != 0U) return BusStatus::NACK;
    if ((flags & I2C_ISR_OVR) != 0U) return BusStatus::OVERRUN;
    return (flags & (I2C_ISR_PECERR | I2C_ISR_TIMEOUT | I2C_ISR_ALERT)) != 0U ?
        BusStatus::PROTOCOL : BusStatus::OK;
}
} // namespace

bool Bus::controlsOwned(bool changing_pe) {
    if (ownership_lost_) return false;
    const auto cr1 = static_cast<std::uint32_t>(I2C4_NS->CR1);
    const bool match = (GPIOD_NS->MODER & MODE_MASK) == pad_mode_ &&
        (GPIOD_NS->PUPDR & MODE_MASK) == pad_pull_ &&
        (GPIOD_NS->OTYPER & PINS) == pad_type_ &&
        (GPIOD_NS->OSPEEDR & MODE_MASK) == pad_speed_ &&
        (GPIOD_NS->AFR[1] & AF_MASK) == pad_af_ &&
        (cr1 & ~I2C_CR1_PE) == 0U && (changing_pe || cr1 == (pe_enabled_ ? I2C_CR1_PE : 0U)) &&
        I2C4_NS->OAR1 == 0U && I2C4_NS->OAR2 == 0U && I2C4_NS->TIMEOUTR == 0U &&
        I2C4_NS->AUTOCR == 0U && I2C4_NS->TIMINGR == (configured_ ? config::IMU_I2C_TIMINGR : 0U) &&
        (I2C4_NS->CR2 & ~I2C_CR2_START) == cr2_expected_;
    if (!match) ownership_lost_ = true;
    return match;
}

bool Bus::ownershipValid(bool changing_pe) {
    if (ownership_lost_) return false;
    if (!environmentValid() || (RCC_NS->APB1ENR2 & RCC_APB1ENR2_I2C4EN) == 0U) {
        ownership_lost_ = true;
        return false;
    }
    return controlsOwned(changing_pe);
}

BusStatus Bus::setupCheckpoint(Operation& op) {
    if (op.polls >= config::IMU_I2C_MAX_POLLS) return BusStatus::POLL_LIMIT;
    ++op.polls;
    op.observed_us = clockUs();
    if (!ownershipValid()) return BusStatus::OWNERSHIP;
    op.observed_us = clockUs();
    return op.observed_us - op.started_us >= config::IMU_I2C_SETUP_US ?
        BusStatus::TIMEOUT : BusStatus::OK;
}

BusStatus Bus::configurePad(std::uint32_t pin, Operation& op) {
    const auto mask = 1U << pin;
    const auto pair = 3U << (2U * pin);
    const auto af = 15U << ((pin - 8U) * 4U);
    auto status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    LL_GPIO_SetAFPin_8_15(GPIOD_NS, mask, LL_GPIO_AF_4);
    pad_af_ = (pad_af_ & ~af) | (4U << ((pin - 8U) * 4U));
    if (!controlsOwned()) return BusStatus::READBACK;
    status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    LL_GPIO_SetPinOutputType(GPIOD_NS, mask, LL_GPIO_OUTPUT_OPENDRAIN);
    pad_type_ |= mask;
    if (!controlsOwned()) return BusStatus::READBACK;
    status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    LL_GPIO_SetPinSpeed(GPIOD_NS, mask, LL_GPIO_SPEED_FREQ_LOW);
    pad_speed_ &= ~pair;
    if (!controlsOwned()) return BusStatus::READBACK;
    status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    LL_GPIO_SetPinPull(GPIOD_NS, mask, LL_GPIO_PULL_UP);
    pad_pull_ = (pad_pull_ & ~pair) | (1U << (2U * pin));
    if (!controlsOwned()) return BusStatus::READBACK;
    status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    LL_GPIO_SetPinMode(GPIOD_NS, mask, LL_GPIO_MODE_ALTERNATE);
    pad_mode_ = (pad_mode_ & ~pair) | (2U << (2U * pin));
    return controlsOwned() ? setupCheckpoint(op) : BusStatus::READBACK;
}

BusStatus Bus::initialize(Operation& op) {
    pad_mode_ = GPIOD_NS->MODER & MODE_MASK;
    pad_pull_ = GPIOD_NS->PUPDR & MODE_MASK;
    pad_type_ = GPIOD_NS->OTYPER & PINS;
    pad_speed_ = GPIOD_NS->OSPEEDR & MODE_MASK;
    pad_af_ = GPIOD_NS->AFR[1] & AF_MASK;
    const std::uint32_t pins[] = {12U, 13U};
    for (const auto pin : pins) {
        const auto status = configurePad(pin, op);
        if (status != BusStatus::OK) return status;
    }
    auto status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    WRITE_REG(I2C4_NS->TIMINGR, config::IMU_I2C_TIMINGR);
    configured_ = true;
    if (!controlsOwned()) return BusStatus::READBACK;
    status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    LL_I2C_Enable(I2C4_NS);
    pe_enabled_ = true;
    if (!controlsOwned()) return BusStatus::READBACK;
    status = setupCheckpoint(op);
    if (status != BusStatus::OK) return status;
    if (I2C4_NS->ISR != I2C_ISR_TXE) return BusStatus::BUS_NOT_IDLE;
    return setupCheckpoint(op);
}

BusInit Bus::begin() {
    if (attempted_) return {BusStatus::ALREADY_STARTED, cleanup_, false};
    attempted_ = true;
    if (!configValid()) { faulted_ = true; return {BusStatus::INVALID_CONFIG, cleanup_, false}; }
    if (bus_claimed) { faulted_ = true; return {BusStatus::OWNERSHIP, cleanup_, false}; }
    Operation op{};
    op.started_us = clockUs();
    if (!metadataValid() || !environmentValid() || !padsPristine()) {
        faulted_ = true;
        return {BusStatus::OWNERSHIP, cleanup_, false};
    }
    if (!enableClock()) { faulted_ = true; return {BusStatus::READBACK, cleanup_, false}; }
    if (!environmentValid() || !padsPristine() || !pristineBus() ||
        !environmentValid() || !padsPristine()) {
        faulted_ = true;
        return {BusStatus::OWNERSHIP, cleanup_, false};
    }
    bus_claimed = true;
    owned_ = true;
    const auto status = initialize(op);
    if (status != BusStatus::OK) {
        faulted_ = true;
        cleanup_ = disableOwned();
        return {status, cleanup_, false};
    }
    ready_ = true;
    return {BusStatus::OK, cleanup_, true};
}

BusCleanup Bus::disableOwned() {
    if (!owned_ || ownership_lost_) return BusCleanup::NOT_ATTEMPTED;
    const auto started = clockUs();
    if (!ownershipValid()) return BusCleanup::NOT_ATTEMPTED;
    if ((I2C4_NS->CR1 & I2C_CR1_PE) != 0U) LL_I2C_Disable(I2C4_NS);
    for (std::uint32_t poll = 0U; poll < config::IMU_I2C_MAX_POLLS; ++poll) {
        const auto now = clockUs();
        if (!ownershipValid(true)) return BusCleanup::NOT_ATTEMPTED;
        if (now - started >= config::IMU_I2C_CLEANUP_US) return BusCleanup::UNCONFIRMED;
        if ((I2C4_NS->CR1 & I2C_CR1_PE) == 0U) {
            if (!ownershipValid(true)) return BusCleanup::NOT_ATTEMPTED;
            const auto checked = clockUs();
            if (checked - started >= config::IMU_I2C_CLEANUP_US) return BusCleanup::UNCONFIRMED;
            if (!ownershipValid(true)) return BusCleanup::NOT_ATTEMPTED;
            if ((I2C4_NS->CR1 & I2C_CR1_PE) == 0U) {
                const auto completed = clockUs();
                if (completed - started >= config::IMU_I2C_CLEANUP_US) return BusCleanup::UNCONFIRMED;
                pe_enabled_ = false;
                return BusCleanup::DISABLED;
            }
        }
    }
    return BusCleanup::UNCONFIRMED;
}

BusTransfer Bus::failed(BusStatus status, Operation& op) {
    ready_ = false;
    faulted_ = true;
    if (owned_ && ownershipValid()) op.error_flags |= I2C4_NS->ISR & ERRORS;
    cleanup_ = disableOwned();
    BusTransfer result{};
    result.status = status;
    result.cleanup = cleanup_;
    result.started_us = op.started_us;
    result.completed_us = op.observed_us;
    result.error_flags = op.error_flags;
    return result;
}

BusStatus Bus::checkFlags(Operation& op, std::uint32_t allowed, std::uint32_t flags) {
    const auto unexpected = flags & ((EVENTS & ~allowed) | I2C_ISR_DIR | I2C_ISR_ADDCODE);
    op.error_flags |= (flags & ERRORS) | unexpected;
    const auto status = errorStatus(flags);
    if (status != BusStatus::OK) return status;
    return unexpected != 0U ? BusStatus::PROTOCOL : BusStatus::OK;
}

BusStatus Bus::observe(Operation& op, std::uint32_t allowed, std::uint32_t& flags) {
    if (op.polls >= config::IMU_I2C_MAX_POLLS) return BusStatus::POLL_LIMIT;
    ++op.polls;
    op.observed_us = clockUs();
    if (!ownershipValid()) return BusStatus::OWNERSHIP;
    flags = I2C4_NS->ISR;
    auto status = checkFlags(op, allowed, flags);
    if (status != BusStatus::OK) return status;
    if (op.observed_us - op.started_us >= config::IMU_I2C_TRANSFER_US) return BusStatus::TIMEOUT;
    op.observed_us = clockUs();
    if (!ownershipValid()) return BusStatus::OWNERSHIP;
    flags = I2C4_NS->ISR;
    status = checkFlags(op, allowed, flags);
    if (status != BusStatus::OK) return status;
    op.observed_us = clockUs();
    return op.observed_us - op.started_us >= config::IMU_I2C_TRANSFER_US ?
        BusStatus::TIMEOUT : BusStatus::OK;
}

BusStatus Bus::waitFor(Operation& op, std::uint32_t wanted, std::uint32_t allowed) {
    for (std::uint32_t poll = 0U; poll < config::IMU_I2C_MAX_POLLS; ++poll) {
        std::uint32_t flags = 0U;
        auto status = observe(op, allowed, flags);
        if (status != BusStatus::OK) return status;
        if ((flags & I2C_ISR_STOPF) != 0U && wanted == I2C_ISR_RXNE && (flags & wanted) == 0U) {
            op.error_flags |= I2C_ISR_STOPF;
            return BusStatus::PROTOCOL;
        }
        if ((flags & wanted) == 0U) continue;
        if ((I2C4_NS->CR2 & I2C_CR2_START) != 0U) return BusStatus::PROTOCOL;
        if (wanted == I2C_ISR_STOPF && (flags & I2C_ISR_BUSY) != 0U) continue;
        status = observe(op, allowed, flags);
        if (status != BusStatus::OK) return status;
        if ((flags & wanted) == 0U) continue;
        if ((I2C4_NS->CR2 & I2C_CR2_START) != 0U) return BusStatus::PROTOCOL;
        if (wanted != I2C_ISR_STOPF || (flags & I2C_ISR_BUSY) == 0U) return BusStatus::OK;
    }
    return BusStatus::POLL_LIMIT;
}

BusStatus Bus::launch(Operation& op, std::uint8_t count, bool reading, bool automatic) {
    std::uint32_t flags = 0U;
    auto status = observe(op, reading ? I2C_ISR_TC : 0U, flags);
    if (status != BusStatus::OK) return status;
    if ((I2C4_NS->CR2 & I2C_CR2_START) != 0U) return BusStatus::PROTOCOL;
    cr2_expected_ = (config::IMU_I2C_ADDRESS << 1U) |
        (static_cast<std::uint32_t>(count) << I2C_CR2_NBYTES_Pos) |
        (reading ? I2C_CR2_RD_WRN : 0U) | (automatic ? I2C_CR2_AUTOEND : 0U);
    LL_I2C_HandleTransfer(I2C4_NS, config::IMU_I2C_ADDRESS << 1U, LL_I2C_ADDRSLAVE_7BIT,
        count, automatic ? LL_I2C_MODE_AUTOEND : LL_I2C_MODE_SOFTEND,
        reading ? LL_I2C_GENERATE_START_READ : LL_I2C_GENERATE_START_WRITE);
    return controlsOwned() ? BusStatus::OK : BusStatus::READBACK;
}

BusStatus Bus::sendByte(Operation& op, std::uint8_t value) {
    const auto status = waitFor(op, I2C_ISR_TXIS, I2C_ISR_TXIS);
    if (status != BusStatus::OK) return status;
    LL_I2C_TransmitData8(I2C4_NS, value);
    return BusStatus::OK;
}

BusStatus Bus::receive(Operation& op, BusTransfer& staging, std::uint8_t count) {
    for (std::uint8_t i = 0U; i < count; ++i) {
        const auto allowed = I2C_ISR_RXNE | (i + 1U == count ? I2C_ISR_STOPF : 0U);
        const auto status = waitFor(op, I2C_ISR_RXNE, allowed);
        if (status != BusStatus::OK) return status;
        staging.bytes[i] = LL_I2C_ReceiveData8(I2C4_NS);
    }
    return BusStatus::OK;
}

BusStatus Bus::finish(Operation& op) {
    auto status = waitFor(op, I2C_ISR_STOPF, I2C_ISR_STOPF);
    if (status != BusStatus::OK) return status;
    LL_I2C_ClearFlag_STOP(I2C4_NS);
    std::uint32_t flags = 0U;
    status = observe(op, 0U, flags);
    if (status != BusStatus::OK) return status;
    if ((flags & I2C_ISR_BUSY) != 0U) return BusStatus::PROTOCOL;
    op.observed_us = clockUs();
    if (!ownershipValid()) return BusStatus::OWNERSHIP;
    flags = I2C4_NS->ISR;
    status = checkFlags(op, 0U, flags);
    if (status != BusStatus::OK) return status;
    if ((flags & I2C_ISR_BUSY) != 0U) return BusStatus::PROTOCOL;
    op.observed_us = clockUs();
    return op.observed_us - op.started_us >= config::IMU_I2C_TRANSFER_US ?
        BusStatus::TIMEOUT : BusStatus::OK;
}

BusStatus Bus::admitRequest(Operation& op) {
    if (!ownershipValid()) return BusStatus::OWNERSHIP;
    const auto flags = static_cast<std::uint32_t>(I2C4_NS->ISR);
    op.error_flags |= flags & (ERRORS | EVENTS | I2C_ISR_DIR | I2C_ISR_ADDCODE);
    const auto error = errorStatus(flags);
    if (error != BusStatus::OK) return error;
    if ((flags & (EVENTS | I2C_ISR_BUSY | I2C_ISR_DIR | I2C_ISR_ADDCODE)) != 0U ||
        (I2C4_NS->CR2 & I2C_CR2_START) != 0U || LL_GPIO_IsInputPinSet(GPIOD_NS, PINS) != 1U)
        return BusStatus::BUS_NOT_IDLE;
    std::uint32_t observed = 0U;
    return observe(op, 0U, observed);
}

BusTransfer Bus::request(Register reg, std::uint8_t value, std::uint8_t count, bool writing) {
    BusTransfer staging{};
    if (!attempted_) return staging;
    if (faulted_ || !ready_) { staging.status = BusStatus::FAULT_LATCHED; staging.cleanup = cleanup_; return staging; }
    Operation op{};
    op.started_us = clockUs();
    auto status = admitRequest(op);
    if (status == BusStatus::OK) status = launch(op, writing ? 2U : 1U, false, writing);
    if (status == BusStatus::OK) status = sendByte(op, static_cast<std::uint8_t>(reg));
    if (status == BusStatus::OK && writing) status = sendByte(op, value);
    if (status == BusStatus::OK && !writing) status = waitFor(op, I2C_ISR_TC, I2C_ISR_TC);
    if (status == BusStatus::OK && !writing) status = launch(op, count, true, true);
    if (status == BusStatus::OK && !writing) status = receive(op, staging, count);
    if (status == BusStatus::OK) status = finish(op);
    if (status != BusStatus::OK) return failed(status, op);
    staging.status = BusStatus::OK;
    staging.started_us = op.started_us;
    staging.completed_us = op.observed_us;
    staging.count = writing ? 0U : count;
    staging.complete = true;
    return staging;
}

BusTransfer Bus::readRegister(Register reg) {
    if (!registerAllowed(reg, false)) { BusTransfer result{}; result.status = BusStatus::INVALID_REQUEST; return result; }
    return request(reg, 0U, 1U, false);
}

BusTransfer Bus::writeRegister(Register reg, std::uint8_t value) {
    if (!registerAllowed(reg, true)) { BusTransfer result{}; result.status = BusStatus::INVALID_REQUEST; return result; }
    return request(reg, value, 0U, true);
}

BusTransfer Bus::readMotion() { return request(Register::INTERRUPT_STATUS, 0U, 15U, false); }
} // namespace imu
#endif

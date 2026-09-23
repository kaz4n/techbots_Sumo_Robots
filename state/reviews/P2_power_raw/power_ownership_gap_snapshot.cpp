// Acquires fresh, bounded ADC1 battery samples on the installed UNO Q core.
// Exclusive native ownership and reset-only faults prevent stale valid voltages.
// Independent native-header tests and an inert compile probe check this source.
#include "power.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <Arduino.h>
#include <wiring_private.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/clock_control/stm32_clock_control.h>
#include <stm32u5xx_ll_adc.h>
#include <stm32u5xx_ll_gpio.h>
#include <stm32u5xx_ll_rcc.h>
#include <cmath>
#include <cstddef>

namespace power {
namespace {
constexpr std::size_t PIN_COUNT = sizeof(zephyr::arduino::arduino_pins) /
                                  sizeof(zephyr::arduino::arduino_pins[0]);
constexpr std::uint32_t CFGR1_RESET = 0x80000000U;
constexpr std::uint32_t SAMPLE_FLAGS = ADC_ISR_EOC | ADC_ISR_EOS |
                                       ADC_ISR_OVR | ADC_ISR_EOSMP;
constexpr std::uint32_t BUSY_COMMANDS = ADC_CR_ADCAL | ADC_CR_ADDIS |
    ADC_CR_ADSTART | ADC_CR_ADSTP | ADC_CR_JADSTART | ADC_CR_JADSTP;
constexpr std::uint32_t RAW_MAX = 16383U;
constexpr std::uint32_t PAD_MASK = 1U << 4U;

std::uint32_t clockUs() { return static_cast<std::uint32_t>(micros()); }

bool bounded(std::uint32_t value) { return value > 0U && value < 0x80000000U; }

bool configValid() {
    const std::uint32_t limits[] = {config::VBAT_ADC_REGULATOR_US,
        config::VBAT_ADC_CALIBRATION_US, config::VBAT_ADC_POST_CAL_US,
        config::VBAT_ADC_ENABLE_US, config::VBAT_ADC_CONVERSION_US,
        config::VBAT_ADC_SHUTDOWN_US, config::VBAT_ADC_SETUP_MAX_POLLS,
        config::VBAT_ADC_READ_MAX_POLLS};
    for (const auto limit : limits) if (!bounded(limit)) return false;
    return config::VBAT_ADC_POST_CAL_US >= 2U &&
           std::isfinite(config::VBAT_ADC_REFERENCE_V) &&
           config::VBAT_ADC_REFERENCE_V > 2.4F && config::VBAT_ADC_REFERENCE_V <= 3.6F &&
           std::isfinite(config::VBAT_DIVIDER_RATIO) && config::VBAT_DIVIDER_RATIO >= 1.0F;
}

bool validPad(const gpio_dt_spec& pad) {
    if (pad.port == nullptr || pad.port->config == nullptr ||
        pad.dt_flags != 0U || pad.pin >= 16U) return false;
    const auto* driver = static_cast<const gpio_driver_config*>(pad.port->config);
    return (driver->port_pin_mask & (1U << pad.pin)) != 0U;
}

bool separatePin(std::uint32_t index, const gpio_dt_spec& battery) {
    if (index >= PIN_COUNT) return false;
    const auto& pad = zephyr::arduino::arduino_pins[index];
    return validPad(pad) && (pad.port != battery.port || pad.pin != battery.pin);
}

bool padMetadataValid() {
    if (config::VBAT_INPUT_PIN != 14U || config::VBAT_INPUT_PIN >= PIN_COUNT) return false;
    const auto& pad = zephyr::arduino::arduino_pins[config::VBAT_INPUT_PIN];
    if (!validPad(pad) || pad.pin != 4U ||
        pad.port != DEVICE_DT_GET(DT_NODELABEL(gpioa))) return false;
    for (const auto pin : config::MOTOR_PWM_PINS) if (!separatePin(pin, pad)) return false;
    for (const auto pin : config::OPP_INPUT_PINS) if (!separatePin(pin, pad)) return false;
    for (const auto pin : config::P0_QTR_PINS) if (!separatePin(pin, pad)) return false;
    return separatePin(config::MOTOR_ENABLE_PIN, pad);
}

bool nativeMetadataValid() {
    return DT_REG_ADDR(DT_NODELABEL(adc1)) == reinterpret_cast<std::uintptr_t>(ADC1_NS) &&
        DT_REG_ADDR(DT_NODELABEL(gpioa)) == reinterpret_cast<std::uintptr_t>(GPIOA_NS) &&
        reinterpret_cast<std::uintptr_t>(ADC12_COMMON_NS) ==
            DT_REG_ADDR(DT_NODELABEL(adc1)) + 0x308U &&
        offsetof(ADC_Common_TypeDef, CCR) == 0U &&
        DT_IRQN(DT_NODELABEL(adc1)) == 37 && ADC1_IRQn == 37 && ADC4_IRQn == 113 &&
        DT_PROP(DT_NODELABEL(adc1), zephyr_deferred_init) == 1 &&
        DT_PROP(DT_NODELABEL(adc1), st_adc_prescaler) == 4 &&
        DT_REG_ADDR(DT_CHILD(DT_NODELABEL(adc1), channel_9)) == 9U &&
        DT_CLOCKS_CELL_BY_IDX(DT_NODELABEL(adc1), 0, bus) == 0x8CU &&
        DT_CLOCKS_CELL_BY_IDX(DT_NODELABEL(adc1), 0, bits) == RCC_AHB2ENR1_ADC12EN &&
        DT_CLOCKS_CELL_BY_IDX(DT_NODELABEL(adc1), 1, bus) == STM32_SRC_HCLK &&
        DT_CLOCKS_CELL_BY_IDX(DT_NODELABEL(adc1), 1, bits) == 0x4C00E8U &&
        DT_PROP(DT_NODELABEL(rcc), clock_frequency) == 160000000U &&
        DT_PROP(DT_NODELABEL(rcc), ahb_prescaler) == 1U;
}

bool devicesAvailable() {
    const auto* adc = DEVICE_DT_GET(DT_NODELABEL(adc1));
    const auto* rcc = DEVICE_DT_GET(DT_NODELABEL(rcc));
    const auto* gpio = DEVICE_DT_GET(DT_NODELABEL(gpioa));
    return adc != nullptr && adc->state != nullptr && !adc->state->initialized &&
        adc->state->init_res == 0U && rcc != nullptr && rcc->api != nullptr &&
        device_is_ready(rcc) && gpio != nullptr && device_is_ready(gpio) &&
        device_is_ready(DEVICE_DT_GET(DT_NODELABEL(adc4))) &&
        device_is_ready(DEVICE_DT_GET(DT_NODELABEL(dac1)));
}

bool peersIdle() {
    const auto adc4_busy = ADC_CR_ADEN | ADC_CR_ADDIS | ADC_CR_ADSTART |
                           ADC_CR_ADSTP | ADC_CR_ADCAL;
    const auto adc4_mode = ADC_CFGR1_EXTEN | ADC_CFGR1_CONT |
                           ADC4_CFGR1_DMAEN | ADC4_CFGR1_DMACFG;
    const auto dac1_mode = DAC_CR_EN1 | DAC_CR_CEN1 | DAC_CR_TEN1 |
                           DAC_CR_DMAEN1 | DAC_CR_WAVE1;
    return NVIC_GetEnableIRQ(ADC1_IRQn) == 0U && NVIC_GetPendingIRQ(ADC1_IRQn) == 0U &&
        NVIC_GetActive(ADC1_IRQn) == 0U && NVIC_GetPendingIRQ(ADC4_IRQn) == 0U &&
        NVIC_GetActive(ADC4_IRQn) == 0U && (ADC4_NS->CR & adc4_busy) == 0U &&
        ADC4_NS->IER == 0U && (ADC4_NS->CFGR1 & adc4_mode) == 0U &&
        (DAC1_NS->CR & dac1_mode) == 0U;
}

bool padOwned() {
    return (RCC_NS->AHB2ENR1 & RCC_AHB2ENR1_GPIOAEN) != 0U &&
        LL_GPIO_IsPinLocked(GPIOA_NS, PAD_MASK) == 0U &&
        LL_GPIO_GetPinMode(GPIOA_NS, PAD_MASK) == LL_GPIO_MODE_ANALOG &&
        LL_GPIO_GetPinPull(GPIOA_NS, PAD_MASK) == LL_GPIO_PULL_NO;
}

bool fixedModes(bool configured) {
    const auto* adc = ADC1_NS;
    return adc->IER == 0U && adc->CFGR1 == CFGR1_RESET &&
        adc->CFGR2 == (configured ? ADC_CFGR2_LFTRIG : 0U) &&
        adc->SMPR1 == (configured ? ADC_SMPR1_SMP9 : 0U) && adc->SMPR2 == 0U &&
        adc->PCSEL == (configured ? (1U << 9U) : 0U) &&
        adc->SQR1 == (configured ? (9U << ADC_SQR1_SQ1_Pos) : 0U) &&
        adc->SQR2 == 0U && adc->SQR3 == 0U && adc->SQR4 == 0U && adc->JSQR == 0U &&
        adc->OFR1 == 0U && adc->OFR2 == 0U && adc->OFR3 == 0U && adc->OFR4 == 0U &&
        adc->GCOMP == 0U && adc->AWD2CR == 0U && adc->AWD3CR == 0U && adc->DIFSEL == 0U &&
        (adc->CALFACT & (ADC_CALFACT_CAPTURE_COEF | ADC_CALFACT_LATCH_COEF)) == 0U;
}

bool pristineAdc() {
    return fixedModes(false) && ADC1_NS->CR == ADC_CR_DEEPPWD &&
        ADC12_COMMON_NS->CCR == 0U;
}

bool clocksValid() {
    // These predicates prove nominal mode only; MSI lock remains unqualified.
    return LL_RCC_GetSysClkSource() == LL_RCC_SYS_CLKSOURCE_STATUS_PLL1 &&
        LL_RCC_GetAHBPrescaler() == LL_RCC_SYSCLK_DIV_1 &&
        LL_RCC_PLL1_GetMainSource() == LL_RCC_PLL1SOURCE_MSIS &&
        LL_RCC_PLL1_GetDivider() == 1U && LL_RCC_PLL1_GetN() == 80U &&
        LL_RCC_PLL1_GetR() == 2U && LL_RCC_PLL1_IsReady() == 1U &&
        LL_RCC_PLL1_IsEnabledDomain_SYS() == 1U && LL_RCC_PLL1FRACN_IsEnabled() == 0U &&
        LL_RCC_MSI_IsEnabledRangeSelect() == 1U &&
        LL_RCC_MSIS_GetRange() == LL_RCC_MSISRANGE_4 && LL_RCC_MSIS_IsReady() == 1U &&
        LL_RCC_IsEnabledPLLMode() == 1U && LL_RCC_GetMSIPLLMode() == LL_RCC_PLLMODE_MSIS &&
        (RCC_NS->CCIPR3 & RCC_CCIPR3_ADCDACSEL) == 0U;
}

bool suppliesValid() {
    const auto peripherals = RCC_AHB3ENR_PWREN | RCC_AHB3ENR_ADC4EN | RCC_AHB3ENR_DAC1EN;
    if ((RCC_NS->AHB3ENR & peripherals) != peripherals ||
        (RCC_NS->APB3ENR & RCC_APB3ENR_SYSCFGEN) == 0U) return false;
    const auto requested = PWR_VOSR_VOS | PWR_VOSR_VOSRDY;
    const auto applied = PWR_SVMSR_ACTVOS | PWR_SVMSR_ACTVOSRDY;
    return (PWR_NS->SVMCR & PWR_SVMCR_ASV) != 0U &&
        (PWR_NS->VOSR & requested) == requested &&
        (PWR_NS->SVMSR & applied) == applied &&
        (SYSCFG_NS->CFGR1 & (SYSCFG_CFGR1_BOOSTEN | SYSCFG_CFGR1_ANASWVDD)) == 0U;
}

bool environmentOwned() {
    return devicesAvailable() && suppliesValid() && clocksValid() && padOwned() && peersIdle();
}

bool enableClock() {
    const auto* rcc = DEVICE_DT_GET(DT_NODELABEL(rcc));
    const auto* api = static_cast<const clock_control_driver_api*>(rcc->api);
    if (api->on == nullptr) return false;
    stm32_pclken clock{};
    clock.bus = DT_CLOCKS_CELL_BY_IDX(DT_NODELABEL(adc1), 0, bus);
    clock.enr = DT_CLOCKS_CELL_BY_IDX(DT_NODELABEL(adc1), 0, bits);
    // Installed STM32 on() only enables this bus bit and reads it back; no wait.
    return api->on(rcc, &clock) == 0 &&
           (RCC_NS->AHB2ENR1 & RCC_AHB2ENR1_ADC12EN) != 0U;
}
} // namespace

bool Reader::controlsOwned() const {
    if (!owned_ || !environmentOwned() ||
        (RCC_NS->AHB2ENR1 & RCC_AHB2ENR1_ADC12EN) == 0U) return false;
    return (!regulator_ready_ || (ADC1_NS->ISR & ADC_ISR_LDORDY) != 0U) &&
        fixedModes(configured_) &&
        ADC12_COMMON_NS->CCR == (divider_set_ ? LL_ADC_CLOCK_ASYNC_DIV4 : 0U) &&
        (ADC1_NS->CR & ~cr_allowed_) == cr_base_;
}

Status Reader::waitFlag(bool control, std::uint32_t mask, bool set,
                        std::uint32_t started, std::uint32_t budget, Status timeout) {
    for (std::uint32_t poll = 0U; poll < config::VBAT_ADC_SETUP_MAX_POLLS; ++poll) {
        if (!controlsOwned()) return Status::OWNERSHIP;
        const auto value = control ? ADC1_NS->CR : ADC1_NS->ISR;
        if (clockUs() - started >= budget) return timeout;
        if (((value & mask) != 0U) == set) return Status::OK;
    }
    return Status::POLL_LIMIT;
}

Status Reader::waitCalibrationGap() {
    // Anchor after ADCAL was observed clear, so clock quantization cannot erase the gap.
    const auto started = clockUs();
    for (std::uint32_t poll = 0U; poll < config::VBAT_ADC_SETUP_MAX_POLLS; ++poll) {
        if (!controlsOwned()) return Status::OWNERSHIP;
        if (clockUs() - started >= config::VBAT_ADC_POST_CAL_US) return Status::OK;
    }
    return Status::POLL_LIMIT;
}

Status Reader::initialize() {
    LL_ADC_SetCommonClock(ADC12_COMMON_NS, LL_ADC_CLOCK_ASYNC_DIV4);
    divider_set_ = true;
    LL_GPIO_SetPinMode(GPIOA_NS, PAD_MASK, LL_GPIO_MODE_ANALOG);
    LL_GPIO_SetPinPull(GPIOA_NS, PAD_MASK, LL_GPIO_PULL_NO);
    if (!controlsOwned()) return Status::READBACK;
    LL_ADC_DisableDeepPowerDown(ADC1_NS);
    cr_base_ = 0U;
    if (!controlsOwned()) return Status::READBACK;
    auto started = clockUs();
    LL_ADC_EnableInternalRegulator(ADC1_NS);
    cr_base_ = ADC_CR_ADVREGEN;
    auto status = waitFlag(false, ADC_ISR_LDORDY, true, started,
        config::VBAT_ADC_REGULATOR_US, Status::REGULATOR_TIMEOUT);
    if (status != Status::OK) return status;
    regulator_ready_ = true;
    started = clockUs();
    cr_base_ |= ADC_CR_ADCALLIN;
    cr_allowed_ = ADC_CR_ADCAL;
    LL_ADC_StartCalibration(ADC1_NS, LL_ADC_CALIB_OFFSET_LINEARITY);
    __DMB();
    status = waitFlag(true, ADC_CR_ADCAL, false, started,
        config::VBAT_ADC_CALIBRATION_US, Status::CALIBRATION_TIMEOUT);
    if (status != Status::OK) return status;
    cr_allowed_ = 0U;
    status = waitCalibrationGap();
    if (status != Status::OK) return status;
    MODIFY_REG(ADC1_NS->CR, ADC_CR_ADCALLIN | ADC_CR_BITS_PROPERTY_RS, 0U);
    cr_base_ = ADC_CR_ADVREGEN;
    __DMB();
    if (!controlsOwned()) return Status::OWNERSHIP;
    WRITE_REG(ADC1_NS->ISR, ADC_ISR_ADRDY);
    if ((ADC1_NS->ISR & ADC_ISR_ADRDY) != 0U) return Status::READBACK;
    started = clockUs();
    cr_allowed_ = ADC_CR_ADEN;
    LL_ADC_Enable(ADC1_NS);
    status = waitFlag(false, ADC_ISR_ADRDY, true, started,
        config::VBAT_ADC_ENABLE_US, Status::ENABLE_TIMEOUT);
    if (status != Status::OK) return status;
    cr_base_ |= ADC_CR_ADEN;
    cr_allowed_ = 0U;
    if (!controlsOwned()) return Status::OWNERSHIP;
    SET_BIT(ADC1_NS->CFGR2, ADC_CFGR2_LFTRIG);
    MODIFY_REG(ADC1_NS->SMPR1, ADC_SMPR1_SMP9, ADC_SMPR1_SMP9);
    SET_BIT(ADC1_NS->PCSEL, 1U << 9U);
    MODIFY_REG(ADC1_NS->SQR1, ADC_SQR1_SQ1, 9U << ADC_SQR1_SQ1_Pos);
    configured_ = true;
    return controlsOwned() ? Status::OK : Status::READBACK;
}

InitResult Reader::begin() {
    if (attempted_) return {Status::ALREADY_STARTED, shutdown_, ready_};
    attempted_ = true;
    Status status = Status::INVALID_CONFIG;
    if (configValid() && padMetadataValid() && nativeMetadataValid()) {
        status = Status::OWNERSHIP;
        if (environmentOwned()) {
            status = Status::READBACK;
            // The gated ADC registers are inspected only after their clock is available.
            if (enableClock()) {
                status = Status::OWNERSHIP;
                if (environmentOwned() && pristineAdc()) {
                    owned_ = true;
                    cr_base_ = ADC_CR_DEEPPWD;
                    status = initialize();
                }
            }
        }
    }
    if (status == Status::OK) ready_ = true;
    else fail(status);
    return {status, shutdown_, ready_};
}

Shutdown Reader::stopOwned() {
    const auto started = clockUs();
    bool stop_sent = false;
    bool disable_sent = false;
    for (std::uint32_t poll = 0U; poll < config::VBAT_ADC_READ_MAX_POLLS; ++poll) {
        if (!controlsOwned()) return Shutdown::UNCONFIRMED;
        const auto cr = ADC1_NS->CR;
        if (clockUs() - started >= config::VBAT_ADC_SHUTDOWN_US) return Shutdown::UNCONFIRMED;
        if ((cr & (ADC_CR_ADCAL | ADC_CR_JADSTART | ADC_CR_JADSTP)) != 0U)
            return Shutdown::UNCONFIRMED;
        if ((cr & BUSY_COMMANDS) == 0U && (cr & ADC_CR_ADEN) == 0U) {
            if (!controlsOwned() || (ADC1_NS->CR & (BUSY_COMMANDS | ADC_CR_ADEN)) != 0U ||
                clockUs() - started >= config::VBAT_ADC_SHUTDOWN_US) return Shutdown::UNCONFIRMED;
            return Shutdown::DISABLED;
        }
        if ((cr & ADC_CR_ADEN) != 0U && (ADC1_NS->ISR & ADC_ISR_ADRDY) == 0U)
            return Shutdown::UNCONFIRMED;
        if ((cr & ADC_CR_ADSTART) != 0U) {
            if (!stop_sent && (cr & (ADC_CR_ADDIS | ADC_CR_ADSTP)) == 0U) {
                cr_allowed_ |= ADC_CR_ADSTP;
                LL_ADC_REG_StopConversion(ADC1_NS);
                stop_sent = true;
            }
        } else if ((cr & BUSY_COMMANDS) == 0U && !disable_sent) {
            cr_base_ &= ~ADC_CR_ADEN;
            cr_allowed_ = ADC_CR_ADEN | ADC_CR_ADDIS;
            LL_ADC_Disable(ADC1_NS);
            disable_sent = true;
        }
    }
    return Shutdown::UNCONFIRMED;
}

void Reader::fail(Status status) {
    ready_ = false;
    faulted_ = true;
    if (!owned_) shutdown_ = Shutdown::NOT_ATTEMPTED;
    else shutdown_ = status == Status::OWNERSHIP ? Shutdown::UNCONFIRMED : stopOwned();
}

Status Reader::sampleStatus(std::uint32_t started) const {
    if (!controlsOwned() || (ADC1_NS->ISR & ADC_ISR_ADRDY) == 0U) return Status::OWNERSHIP;
    if ((ADC1_NS->ISR & ADC_ISR_OVR) != 0U) return Status::OVERRUN;
    return clockUs() - started >= config::VBAT_ADC_CONVERSION_US
               ? Status::CONVERSION_TIMEOUT : Status::OK;
}

Status Reader::finishSample(Sample& sample) {
    const std::uint32_t raw = LL_ADC_REG_ReadConversionData32(ADC1_NS);
    if (raw > RAW_MAX) return Status::INVALID_DATA;
    auto status = sampleStatus(sample.started_us);
    if (status != Status::OK) return status;
    if ((ADC1_NS->CR & BUSY_COMMANDS) != 0U ||
        (ADC1_NS->ISR & (ADC_ISR_EOC | ADC_ISR_EOS)) != ADC_ISR_EOS) return Status::READBACK;
    WRITE_REG(ADC1_NS->ISR, ADC_ISR_EOS);
    const auto voltage = static_cast<float>(raw) / static_cast<float>(RAW_MAX) *
                         config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
    if (!std::isfinite(voltage)) return Status::INVALID_DATA;
    status = sampleStatus(sample.started_us);
    if (status != Status::OK) return status;
    if ((ADC1_NS->ISR & (ADC_ISR_EOC | ADC_ISR_EOS)) != 0U ||
        (ADC1_NS->CR & BUSY_COMMANDS) != 0U) return Status::READBACK;
    const auto completed = clockUs();
    if (completed - sample.started_us >= config::VBAT_ADC_CONVERSION_US)
        return Status::CONVERSION_TIMEOUT;
    sample.raw = static_cast<std::uint16_t>(raw);
    sample.voltage_v = voltage;
    sample.completed_us = completed;
    sample.valid = true;
    return Status::OK;
}

Sample Reader::read() {
    Sample sample{};
    sample.shutdown = shutdown_;
    if (!attempted_) return sample;
    if (faulted_) { sample.status = Status::FAULT_LATCHED; return sample; }
    sample.started_us = clockUs();
    auto status = controlsOwned() && ready_ ? Status::OK : Status::OWNERSHIP;
    if (status == Status::OK) {
        // Exactly one W1C clear identifies the next conversion, including raw zero.
        WRITE_REG(ADC1_NS->ISR, SAMPLE_FLAGS);
        if ((ADC1_NS->ISR & SAMPLE_FLAGS) != 0U) status = Status::READBACK;
        else status = sampleStatus(sample.started_us);
    }
    if (status == Status::OK) {
        cr_allowed_ = ADC_CR_ADSTART;
        LL_ADC_REG_StartConversion(ADC1_NS);
        status = Status::POLL_LIMIT;
        for (std::uint32_t poll = 0U; poll < config::VBAT_ADC_READ_MAX_POLLS; ++poll) {
            const auto observed = sampleStatus(sample.started_us);
            if (observed != Status::OK) { status = observed; break; }
            const auto flags = ADC1_NS->ISR;
            if ((flags & (ADC_ISR_EOC | ADC_ISR_EOS)) == (ADC_ISR_EOC | ADC_ISR_EOS) &&
                (ADC1_NS->CR & ADC_CR_ADSTART) == 0U) {
                status = finishSample(sample);
                break;
            }
        }
    }
    if (status == Status::OK) cr_allowed_ = 0U;
    else { fail(status); sample.completed_us = clockUs(); }
    sample.status = status;
    sample.shutdown = shutdown_;
    return sample;
}

} // namespace power
#endif

// Reads the seven proposed opponent inputs through checked native GPIO calls.
// Keeps electrical levels distinct from failures and from core sensor polarity.
// Independent native-API tests exercise this source; target probe retains it inert.
#include "opp_sensors.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <Arduino.h>
#include <wiring_private.h>
#include <zephyr/drivers/gpio.h>
#include <cerrno>
#include <climits>
#include <cstddef>

namespace opp_sensors {
namespace {
constexpr std::size_t CHANNEL_COUNT = 7U;
constexpr std::uint8_t ALL_CHANNELS_MASK = 0x7FU;
constexpr std::size_t PIN_COUNT = sizeof(zephyr::arduino::arduino_pins) /
                                  sizeof(zephyr::arduino::arduino_pins[0]);

bool validSpec(const gpio_dt_spec& spec) {
    if (spec.port == nullptr || spec.port->config == nullptr ||
        spec.dt_flags != 0U || spec.pin >= sizeof(gpio_port_pins_t) * CHAR_BIT) {
        return false;
    }
    const auto* driver = static_cast<const gpio_driver_config*>(spec.port->config);
    const auto pin_mask = static_cast<gpio_port_pins_t>(gpio_port_pins_t{1} << spec.pin);
    return (driver->port_pin_mask & pin_mask) != 0U;
}

bool validBank() {
    for (std::size_t i = 0; i < CHANNEL_COUNT; ++i) {
        const auto index = config::OPP_INPUT_PINS[i];
        if (index >= PIN_COUNT) return false;
        const auto& spec = zephyr::arduino::arduino_pins[index];
        if (!validSpec(spec)) return false;
        for (std::size_t previous = 0; previous < i; ++previous) {
            const auto& other = zephyr::arduino::arduino_pins[config::OPP_INPUT_PINS[previous]];
            if (spec.port == other.port && spec.pin == other.pin) return false;
        }
    }
    return true;
}
} // namespace

InitResult Sensors::begin() {
    ready_ = false;
    InitResult result{};
    // Reject the entire malformed bank before configuring even its valid prefix.
    if (!validBank()) {
        for (auto& status : result.status) status = -EINVAL;
        return result;
    }
    for (std::size_t i = 0; i < CHANNEL_COUNT; ++i) {
        const auto& spec = zephyr::arduino::arduino_pins[config::OPP_INPUT_PINS[i]];
        result.status[i] = device_is_ready(spec.port)
                               ? gpio_pin_configure_dt(&spec, GPIO_INPUT) : -ENODEV;
        if (result.status[i] == 0) {
            result.configured_mask |= static_cast<std::uint8_t>(1U << i);
        }
    }
    ready_ = result.configured_mask == ALL_CHANNELS_MASK;
    result.ready = ready_;
    return result;
}

Snapshot Sensors::read() const {
    Snapshot result{};
    if (!ready_) {
        for (auto& status : result.status) status = -EACCES;
        return result;
    }
    result.started_us = static_cast<std::uint32_t>(micros());
    for (std::size_t i = 0; i < CHANNEL_COUNT; ++i) {
        const auto& spec = zephyr::arduino::arduino_pins[config::OPP_INPUT_PINS[i]];
        result.status[i] = device_is_ready(spec.port)
                               ? gpio_pin_get_raw(spec.port, spec.pin) : -ENODEV;
        if (result.status[i] == 0 || result.status[i] == 1) {
            const auto bit = static_cast<std::uint8_t>(1U << i);
            result.valid_mask |= bit;
            if (result.status[i] == 1) result.raw_mask |= bit;
        }
    }
    result.completed_us = static_cast<std::uint32_t>(micros());
    result.valid = result.valid_mask == ALL_CHANNELS_MASK;
    return result;
}
} // namespace opp_sensors
#endif

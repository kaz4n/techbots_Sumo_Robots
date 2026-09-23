// Models the audited native GPIO argument and result types.
// Keeps every readiness, configure and raw read observable without real I/O.
// Contract cases provide these functions and reject unexpected flags or calls.
#pragma once
#include <cstdint>

using gpio_pin_t = std::uint8_t;
using gpio_dt_flags_t = std::uint16_t;
using gpio_flags_t = std::uint32_t;
using gpio_port_pins_t = std::uint32_t;
struct gpio_driver_config { gpio_port_pins_t port_pin_mask; };
struct device { const void* config; };
struct gpio_dt_spec {
    const device* port;
    gpio_pin_t pin;
    gpio_dt_flags_t dt_flags;
};
constexpr gpio_flags_t GPIO_INPUT = 1U << 16;
bool device_is_ready(const device* port);
int gpio_pin_configure_dt(const gpio_dt_spec* spec, gpio_flags_t flags);
int gpio_pin_get_raw(const device* port, gpio_pin_t pin);

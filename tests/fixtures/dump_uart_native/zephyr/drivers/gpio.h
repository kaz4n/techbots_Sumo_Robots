// Declares the exact PG13 ready-pin wrapper operations used by the native port.
// Configuration and read status are independent from register side effects.
// Tests reject low/error readiness and verify input-pulldown setup arguments.
#pragma once
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
using gpio_flags_t = std::uint32_t;
using gpio_pin_t = std::uint8_t;
using gpio_port_value_t = std::uint32_t;
struct gpio_driver_config { std::uint32_t port_pin_mask; };
struct gpio_driver_api {
    int (*pin_configure)(const device*, gpio_pin_t, gpio_flags_t);
    int (*port_get_raw)(const device*, gpio_port_value_t*);
};
struct gpio_dt_spec { const device* port; unsigned pin; unsigned dt_flags; };
#define GPIO_DT_SPEC_GET_BY_IDX(n,p,i) {&dump_devices[1],13U,0U}
inline constexpr gpio_flags_t GPIO_INPUT = 1U << 16U;
inline constexpr gpio_flags_t GPIO_PULL_DOWN = 1U << 5U;
int gpio_pin_configure_dt(const gpio_dt_spec*, gpio_flags_t);
int gpio_pin_get_dt(const gpio_dt_spec*);
inline bool gpio_is_ready_dt(const gpio_dt_spec* spec) { return device_is_ready(spec->port); }

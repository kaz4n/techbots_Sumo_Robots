// Preserves installed GPIO flags, callback names and checked wrapper signatures.
// Dispatch side effects are independent from return status and physical levels.
// Native cases require HIGH preload before output and neutral INPUT cleanup.
#pragma once
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
using gpio_pin_t=std::uint8_t;
using gpio_dt_flags_t=std::uint16_t;
using gpio_flags_t=std::uint32_t;
using gpio_port_pins_t=std::uint32_t;
using gpio_port_value_t=std::uint32_t;
struct gpio_driver_config { gpio_port_pins_t port_pin_mask; };
struct gpio_driver_data { gpio_port_pins_t invert; };
struct gpio_dt_spec { const device* port; gpio_pin_t pin; gpio_dt_flags_t dt_flags; };
struct gpio_driver_api {
 int (*pin_configure)(const device*,gpio_pin_t,gpio_flags_t);
 int (*port_get_raw)(const device*,gpio_port_value_t*);
 int (*port_set_bits_raw)(const device*,gpio_port_pins_t);
 int (*port_clear_bits_raw)(const device*,gpio_port_pins_t);
};
constexpr gpio_flags_t GPIO_INPUT=1U<<16;
constexpr gpio_flags_t GPIO_OUTPUT=1U<<17;
constexpr gpio_flags_t GPIO_OUTPUT_INIT_LOW=1U<<18;
constexpr gpio_flags_t GPIO_OUTPUT_INIT_HIGH=1U<<19;
constexpr gpio_flags_t GPIO_OUTPUT_HIGH=GPIO_OUTPUT|GPIO_OUTPUT_INIT_HIGH;
int gpio_pin_configure_dt(const gpio_dt_spec*,gpio_flags_t);
int gpio_pin_get_raw(const device*,gpio_pin_t);
int gpio_pin_set_raw(const device*,gpio_pin_t,int);
inline bool gpio_is_ready_dt(const gpio_dt_spec* s){return device_is_ready(s->port);}

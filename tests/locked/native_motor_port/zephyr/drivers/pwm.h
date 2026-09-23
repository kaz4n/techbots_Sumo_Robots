// Supplies exact cycle-based native PWM argument types.
// Set success changes preloads only; independent timer events transfer active state.
// Cases check native status, route and rate instead of accepting synthetic success.
#pragma once
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
using pwm_flags_t = std::uint16_t;
struct pwm_dt_spec { const device* dev; std::uint32_t channel; std::uint32_t period; pwm_flags_t flags; };
constexpr pwm_flags_t PWM_POLARITY_NORMAL = 0;
constexpr pwm_flags_t PWM_POLARITY_INVERTED = 1;
int pwm_get_cycles_per_sec(const device*, std::uint32_t, std::uint64_t*);
int pwm_set_cycles(const device*, std::uint32_t, std::uint32_t, std::uint32_t, pwm_flags_t);
inline bool pwm_is_ready_dt(const pwm_dt_spec* s) { return device_is_ready(s->dev); }

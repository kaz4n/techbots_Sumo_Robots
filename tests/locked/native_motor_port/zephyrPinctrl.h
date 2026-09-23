// Reproduces the installed per-device Arduino pinctrl ordinal helper.
// Whole-state routing is deliberately absent because it can steal QTR or EN pins.
// The counted channel helper validates native device and channel index arguments.
#pragma once
#include <cstddef>
#include <zephyr/device.h>
namespace zephyr { namespace arduino {
int init_dev_apply_channel_pinctrl(const device*, std::size_t);
template <typename Spec, std::size_t N>
constexpr std::size_t state_pin_index_from_spec_index(const Spec (&specs)[N], std::size_t selected) {
    std::size_t ordinal = 0;
    for (std::size_t i = 0; i < selected; ++i) if (specs[i].dev == specs[selected].dev) ++ordinal;
    return ordinal;
}
}}

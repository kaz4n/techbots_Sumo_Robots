// Defines independent immutable pin fixtures from the installed GPIO audit.
// Malformed compile variants exercise validation before any native operation.
// The Python runner emits the constexpr Arduino table using fixtureSpec below.
#pragma once
#include "zephyr/drivers/gpio.h"

#ifndef OPP_TABLE_SIZE
#define OPP_TABLE_SIZE 70
#endif
#ifndef OPP_BAD_SLOT
#define OPP_BAD_SLOT 0
#endif
#ifndef OPP_MAP_KIND
#define OPP_MAP_KIND 0
#endif

extern gpio_driver_config fixture_configs[3];
extern const device fixture_ports[3];
constexpr unsigned fixture_indices[7] = {11, 12, 13, 16, 17, 18, 19};
constexpr gpio_dt_spec expected_specs[7] = {
    {&fixture_ports[1], 15, 0}, {&fixture_ports[1], 14, 0},
    {&fixture_ports[1], 13, 0}, {&fixture_ports[0], 6, 0},
    {&fixture_ports[0], 7, 0}, {&fixture_ports[2], 1, 0},
    {&fixture_ports[2], 0, 0},
};

constexpr gpio_dt_spec fixtureSpec(unsigned index) {
    for (unsigned slot = 0; slot < 7; ++slot) {
        if (index != fixture_indices[slot]) continue;
        gpio_dt_spec spec = expected_specs[slot];
        if (slot != OPP_BAD_SLOT) return spec;
        if (OPP_MAP_KIND == 1) spec.port = nullptr;
        if (OPP_MAP_KIND == 2) spec.pin = 32;
        if (OPP_MAP_KIND == 3) spec.pin = 255;
        if (OPP_MAP_KIND == 4) spec.dt_flags = 1;
        if (OPP_MAP_KIND == 5) spec.dt_flags = 65535;
        if (OPP_MAP_KIND == 6) spec = expected_specs[(slot + 1) % 7];
        if (OPP_MAP_KIND == 7) spec.pin = 31;
        if (OPP_MAP_KIND == 8) {
            constexpr gpio_pin_t same_number_other_port[7] = {6, 7, 0, 15, 14, 6, 7};
            spec.pin = same_number_other_port[slot];
        }
        return spec;
    }
    return {nullptr, 0, 0};
}

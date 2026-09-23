// Provides installed-shaped native clock dispatch declarations.
// The fixture records finite dispatch and emulates enable readback failures.
// No stock I2C initialization or clock-selector reconfiguration API is supplied.
#pragma once
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
using clock_control_subsys_t = void*;
using clock_control_cb_t = void (*)(const device*,clock_control_subsys_t,void*);
using clock_control_on_t = int (*)(const device*,clock_control_subsys_t);
using clock_control_off_t = int (*)(const device*,clock_control_subsys_t);
using clock_control_get_rate_t = int (*)(const device*,clock_control_subsys_t,std::uint32_t*);
struct clock_control_driver_api { clock_control_on_t on; clock_control_off_t off; void* async_on; clock_control_get_rate_t get_rate; void* get_status; void* configure; };
struct stm32_pclken { std::uint32_t enr; std::uint32_t bus; };
#define STM32_SRC_HCLK 9
#define STM32_CLOCK_BUS_AHB2 140
#define STM32_CLOCK_CONTROL_NODE DT_NODELABEL(rcc)
int clock_control_on(const device*,clock_control_subsys_t);
int clock_control_get_rate(const device*,clock_control_subsys_t,std::uint32_t*);

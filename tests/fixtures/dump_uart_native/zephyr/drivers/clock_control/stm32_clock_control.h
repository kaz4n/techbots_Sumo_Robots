// Declares pinned clock metadata for the internal LPUART1 APB3 gate.
// Host fields are observable metadata; target layout is separately compiled.
// Tests mutate gate, bus and reset identity independently from UART readiness.
#pragma once
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
struct stm32_pclken { std::uint32_t bus; std::uint32_t div; std::uint32_t enr; };
#define STM32_CLOCK_BUS_APB3 168U

// Defines installed clock metadata constants, with controlled build variants.
// No live clock-control API is supplied or silently emulated.
// Immutable candidate-rate tests compile the real adapter against this metadata.
#pragma once
#include <zephyr/devicetree.h>
#define STM32_SRC_TIMPCLK1 13
#define STM32_SRC_TIMPCLK2 14
#define STM32_CLOCK_CONTROL_NODE DT_NODELABEL(rcc)

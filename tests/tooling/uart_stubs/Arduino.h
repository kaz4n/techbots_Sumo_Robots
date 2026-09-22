// Supplies only the installed setup helper needed by the P0 adapter tests.
// Omits Serial, Bridge, clocks and allocation APIs to reject accidental usage.
// Compiled by test_counter_uart.py with the real opaque adapter source.
#pragma once
#include <zephyr/drivers/uart.h>
namespace zephyr { namespace arduino {
int init_dev_apply_pinctrl(const device* dev);
} }

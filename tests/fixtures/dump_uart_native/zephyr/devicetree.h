// Maps the pinned internal LPUART1, GPIOG and clock identities to host devices.
// These compile-time bindings model the installed device tree, not physical I/O.
// Tests independently mutate runtime metadata behind each declared device.
#pragma once
#define DT_NODELABEL(n) n
#define DT_PATH(n) n
#define DT_PROP(n,p) DUMP_PROP_EXPAND(p)
#define DUMP_PROP_EXPAND(p) DUMP_PROP_##p
#define DUMP_PROP_current_speed 115200U
#define DUMP_PROP_zephyr_deferred_init 1
#define DEVICE_DT_GET(n) DUMP_DEVICE_EXPAND(n)
#define DUMP_DEVICE_EXPAND(n) DUMP_DEVICE_##n
#define DUMP_DEVICE_lpuart1 (&dump_devices[0])
#define DUMP_DEVICE_gpiog (&dump_devices[1])
#define DUMP_DEVICE_rcc (&dump_devices[2])
#define DT_REG_ADDR(n) DUMP_ADDRESS_EXPAND(n)
#define DUMP_ADDRESS_EXPAND(n) DUMP_ADDRESS_##n
#define DUMP_ADDRESS_lpuart1 0x46002400UL
#define DUMP_ADDRESS_gpiog 0x42021800UL
#define DT_IRQN(n) 66
#define DT_NODE_HAS_STATUS(n,s) 1
#define STM32_CLOCK_CONTROL_NODE DT_NODELABEL(rcc)

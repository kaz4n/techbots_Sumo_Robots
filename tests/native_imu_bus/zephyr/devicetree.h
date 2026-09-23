// Provides source-verified I2C4 DT metadata with independent malformed variants.
// Default PD12/13 pinctrl is separate from the unused PF14/15 sleep state.
// Contract tests demand rejection before changing the peripheral or pad modes.
#pragma once
#ifndef NATIVE_BAD_METADATA
#define NATIVE_BAD_METADATA 0
#endif
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define DT_NODELABEL(n) n
#define DT_PROP(n,p) DT_PROP_IMPL(n,p)
#define DT_PROP_IMPL(n,p) FIX_PROP_##n##_##p
#define DT_REG_ADDR(n) DT_REG_IMPL(n)
#define DT_REG_IMPL(n) FIX_REG_##n
#define DT_PROP_LEN(n,p) DT_LEN_IMPL(n,p)
#define DT_LEN_IMPL(n,p) FIX_LEN_##n##_##p
#define DT_PHANDLE_BY_IDX(n,p,i) DT_PH_IMPL(n,p,i)
#define DT_PH_IMPL(n,p,i) FIX_PH_##n##_##p##_##i
#define DT_ENUM_IDX(n,p) DT_ENUM_IMPL(n,p)
#define DT_ENUM_IMPL(n,p) FIX_ENUM_##n##_##p
#define DT_IRQ_BY_IDX(n,i,c) DT_IRQ_IMPL(n,i,c)
#define DT_IRQ_IMPL(n,i,c) FIX_IRQ_##n##_##i##_##c
#define DT_CLOCKS_CELL_BY_IDX(n,i,c) DT_CLOCK_IMPL(n,i,c)
#define DT_CLOCK_IMPL(n,i,c) FIX_CLOCK_##n##_##i##_##c
#define DEVICE_DT_GET(n) DEVICE_DT_IMPL(n)
#define DEVICE_DT_IMPL(n) FIX_DEVICE_##n
#define FIX_DEVICE_i2c4 (&fixture_devices[0])
#define FIX_DEVICE_gpiod (&fixture_devices[1])
#define FIX_DEVICE_rcc (&fixture_devices[2])
#define FIX_REG_i2c4 (NATIVE_BAD_METADATA==1?0x40005800UL:0x40008400UL)
#define FIX_REG_gpiod (NATIVE_BAD_METADATA==2?0x42020800UL:0x42020C00UL)
#define FIX_REG_rcc 0x46020C00UL
#define FIX_PROP_rcc_clock_frequency (NATIVE_BAD_METADATA==3?80000000UL:160000000UL)
#define FIX_PROP_rcc_ahb_prescaler (NATIVE_BAD_METADATA==4?2:1)
#define FIX_PROP_rcc_apb1_prescaler (NATIVE_BAD_METADATA==5?2:1)
#define FIX_PROP_i2c4_zephyr_deferred_init (NATIVE_BAD_METADATA==6?0:1)
#define FIX_PROP_i2c4_clock_frequency (NATIVE_BAD_METADATA==7?100000:400000)
#define FIX_LEN_i2c4_pinctrl_0 (NATIVE_BAD_METADATA==8?1:2)
#define FIX_LEN_i2c4_clocks (NATIVE_BAD_METADATA==9?2:1)
#define FIX_PH_i2c4_pinctrl_0_0 scl
#define FIX_PH_i2c4_pinctrl_0_1 sda
#define FIX_PROP_scl_pinmux (NATIVE_BAD_METADATA==10?1925:1924)
#define FIX_PROP_sda_pinmux (NATIVE_BAD_METADATA==11?1957:1956)
#define FIX_PROP_scl_bias_pull_up (NATIVE_BAD_METADATA==12?0:1)
#define FIX_PROP_sda_bias_pull_up (NATIVE_BAD_METADATA==13?0:1)
#define FIX_PROP_scl_bias_pull_down (NATIVE_BAD_METADATA==14?1:0)
#define FIX_PROP_sda_bias_pull_down (NATIVE_BAD_METADATA==15?1:0)
#define FIX_PROP_scl_drive_open_drain (NATIVE_BAD_METADATA==16?0:1)
#define FIX_PROP_sda_drive_open_drain (NATIVE_BAD_METADATA==17?0:1)
#define FIX_PROP_scl_drive_push_pull (NATIVE_BAD_METADATA==18?1:0)
#define FIX_PROP_sda_drive_push_pull (NATIVE_BAD_METADATA==19?1:0)
#define FIX_PROP_scl_slew_rate "low-speed"
#define FIX_PROP_sda_slew_rate "low-speed"
#define FIX_ENUM_scl_slew_rate (NATIVE_BAD_METADATA==20?1:0)
#define FIX_ENUM_sda_slew_rate (NATIVE_BAD_METADATA==21?1:0)
#define FIX_PROP_scl_bias_disable (NATIVE_BAD_METADATA==22?1:0)
#define FIX_PROP_sda_bias_disable (NATIVE_BAD_METADATA==23?1:0)
#define FIX_IRQ_i2c4_0_irq (NATIVE_BAD_METADATA==24?100:101)
#define FIX_IRQ_i2c4_1_irq (NATIVE_BAD_METADATA==25?101:100)
#define FIX_CLOCK_i2c4_0_bus (NATIVE_BAD_METADATA==26?156U:160U)
#define FIX_CLOCK_i2c4_0_bits (NATIVE_BAD_METADATA==27?4U:2U)

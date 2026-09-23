// Reproduces only source-verified device-tree metadata for the ADC fixture.
// Malformed variants are rejected before ADC or pad configuration.
// Native runtime cases mutate device state separately from immutable metadata.
#pragma once
#include <cstdint>
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define DT_NODELABEL(n) n
#define DT_PATH(n) n
#define DT_PARENT(n) n
#define DT_PROP(n,p) DT_PROP_IMPL(n,p)
#define DT_PROP_IMPL(n,p) FIX_PROP_##n##_##p
#define FIX_PROP_rcc_clock_frequency 160000000UL
#define FIX_PROP_rcc_ahb_prescaler 1
#define FIX_PROP_adc1_st_adc_clock_source 2
#define FIX_PROP_adc1_st_adc_prescaler 4
#define DT_REG_ADDR(n) DT_REG_IMPL(n)
#define DT_REG_IMPL(n) FIX_REG_##n
#define FIX_REG_adc1 0x42028000UL
#define FIX_REG_adc4 0x46021000UL
#define FIX_REG_gpioa 0x42020000UL
#define FIX_REG_rcc 0x46020C00UL
#define FIX_REG_dac1 0x46021800UL
#define DT_IRQN(n) 37
#define DT_CLOCKS_CELL_BY_IDX(n,i,c) DT_CLOCK_IMPL(n,i,c)
#define DT_CLOCK_IMPL(n,i,c) FIX_CLOCK_##n##_##i##_##c
#define FIX_CLOCK_adc1_0_bus 140U
#define FIX_CLOCK_adc1_0_bits 1024U
#define FIX_CLOCK_adc1_0_div 0U
#define FIX_CLOCK_adc1_1_bus 9U
#define FIX_CLOCK_adc1_1_bits 4980968U
#define FIX_CLOCK_adc1_1_div 0U
#define DEVICE_DT_GET(n) DEVICE_DT_IMPL(n)
#define DEVICE_DT_IMPL(n) FIX_DEVICE_##n
#define FIX_DEVICE_adc1 (&fixture_devices[0])
#define FIX_DEVICE_gpioa (&fixture_devices[1])
#define FIX_DEVICE_rcc (&fixture_devices[2])
#define FIX_DEVICE_adc4 (&fixture_devices[3])
#define FIX_DEVICE_dac1 (&fixture_devices[4])

#define DT_CHILD(n,c) DT_CHILD_IMPL(n,c)
#define DT_CHILD_IMPL(n,c) n##_##c
#define FIX_REG_adc1_channel_9 9U
#define FIX_PROP_adc1_deferred_init 1

#define FIX_PROP_adc1_zephyr_deferred_init 1

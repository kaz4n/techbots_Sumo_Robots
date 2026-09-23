// Recreates only source-verified DT extraction macros used by the native backend.
// Configurable clock and mapping metadata make unsupported candidates explicit.
// Macros expand to installed-shaped constant specs and literal register addresses.
#pragma once
#include <cstdint>
#ifndef NATIVE_HCLK
#define NATIVE_HCLK 160000000UL
#endif
#ifndef NATIVE_APB1
#define NATIVE_APB1 1
#endif
#ifndef NATIVE_APB2
#define NATIVE_APB2 1
#endif
#ifndef NATIVE_DOMAIN1
#define NATIVE_DOMAIN1 14
#endif
#ifndef NATIVE_DOMAIN3
#define NATIVE_DOMAIN3 13
#endif
#ifndef NATIVE_CLOCK_DIV
#define NATIVE_CLOCK_DIV 0
#endif
#define DT_NODELABEL(n) n
#define DT_PATH(n) n
#define DT_PARENT(n) n
#define DT_PROP(n,p) DT_PROP_IMPL(n,p)
#define DT_PROP_IMPL(n,p) FIXTURE_PROP_##n##_##p
#define FIXTURE_PROP_rcc_clock_frequency NATIVE_HCLK
#define FIXTURE_PROP_rcc_ahb_prescaler 1
#define FIXTURE_PROP_rcc_apb1_prescaler NATIVE_APB1
#define FIXTURE_PROP_rcc_apb2_prescaler NATIVE_APB2
#define FIXTURE_PROP_pwm1_st_prescaler 63UL
#define FIXTURE_PROP_pwm3_st_prescaler 4UL
#define FIXTURE_PROP_pwm4_st_prescaler 4UL
#define DT_CLOCKS_CELL_BY_IDX(n,i,c) DT_CLOCK_IMPL(n,c)
#define DT_CLOCK_IMPL(n,c) FIXTURE_CLOCK_##n##_##c
#define FIXTURE_CLOCK_pwm1_bus (NATIVE_DOMAIN1 | (NATIVE_CLOCK_DIV << 12))
#define FIXTURE_CLOCK_pwm3_bus (NATIVE_DOMAIN3 | (NATIVE_CLOCK_DIV << 12))
#define FIXTURE_CLOCK_pwm4_bus (13 | (NATIVE_CLOCK_DIV << 12))
#define FIXTURE_CLOCK_pwm1_div NATIVE_CLOCK_DIV
#define FIXTURE_CLOCK_pwm3_div NATIVE_CLOCK_DIV
#define FIXTURE_CLOCK_pwm4_div NATIVE_CLOCK_DIV
#define FIXTURE_CLOCK_pwm1_bits 255
#define FIXTURE_CLOCK_pwm3_bits 255
#define FIXTURE_CLOCK_pwm4_bits 255
#define DT_REG_ADDR(n) DT_REG_IMPL(n)
#define DT_REG_IMPL(n) FIXTURE_REG_##n
#define FIXTURE_REG_pwm1 0x40012c00UL
#define FIXTURE_REG_pwm3 0x40000400UL
#define FIXTURE_REG_pwm4 0x40000800UL
#define FIXTURE_REG_gpiob 0x42020400UL
#define DEVICE_DT_GET(n) DEVICE_DT_IMPL(n)
#define DEVICE_DT_IMPL(n) FIXTURE_DEVICE_##n
#define FIXTURE_DEVICE_pwm1 (&fixture_pwm_devices[0])
#define FIXTURE_DEVICE_pwm3 (&fixture_pwm_devices[1])
#define FIXTURE_DEVICE_pwm4 (&fixture_pwm_devices[2])
#define FIXTURE_DEVICE_gpiob (&fixture_gpio_ports[1])
#define PWM_DT_SPEC_GET_BY_IDX(n,i) pwmSpec(i)
#define GPIO_DT_SPEC_GET_BY_IDX(n,p,i) pwmPad(i)
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#ifdef NATIVE_SHORT_PWM
#define DT_FOREACH_PROP_ELEM(n,p,f) f(n,p,0) f(n,p,1) f(n,p,2) f(n,p,3) f(n,p,4) f(n,p,5) f(n,p,6) f(n,p,7) f(n,p,8) f(n,p,9) f(n,p,10) f(n,p,11) f(n,p,12) f(n,p,13) f(n,p,14)
#else
#define DT_FOREACH_PROP_ELEM(n,p,f) f(n,p,0) f(n,p,1) f(n,p,2) f(n,p,3) f(n,p,4) f(n,p,5) f(n,p,6) f(n,p,7) f(n,p,8) f(n,p,9) f(n,p,10) f(n,p,11) f(n,p,12) f(n,p,13) f(n,p,14) f(n,p,15)
#endif
#ifdef NATIVE_SHORT_PAD
#define DT_FOREACH_PROP_ELEM_SEP(n,p,f,s) f(n,p,0), f(n,p,1), f(n,p,2), f(n,p,3), f(n,p,4), f(n,p,5), f(n,p,6), f(n,p,7), f(n,p,8), f(n,p,9), f(n,p,10), f(n,p,11), f(n,p,12), f(n,p,13), f(n,p,14)
#else
#define DT_FOREACH_PROP_ELEM_SEP(n,p,f,s) f(n,p,0), f(n,p,1), f(n,p,2), f(n,p,3), f(n,p,4), f(n,p,5), f(n,p,6), f(n,p,7), f(n,p,8), f(n,p,9), f(n,p,10), f(n,p,11), f(n,p,12), f(n,p,13), f(n,p,14), f(n,p,15)
#endif

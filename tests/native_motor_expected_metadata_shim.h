// Supplies isolated D202 clock metadata after the unchanged fake DT header.
// Keeps alternate values out of production config and locked fixtures.
// The independent matrix supplies every scalar explicitly for each build.
#pragma once
#include <zephyr/devicetree.h>
#undef FIXTURE_PROP_rcc_clock_frequency
#undef FIXTURE_PROP_rcc_ahb_prescaler
#undef FIXTURE_PROP_rcc_apb1_prescaler
#undef FIXTURE_PROP_rcc_apb2_prescaler
#undef FIXTURE_PROP_pwm1_st_prescaler
#undef FIXTURE_PROP_pwm3_st_prescaler
#undef FIXTURE_PROP_pwm4_st_prescaler
#undef FIXTURE_CLOCK_pwm1_bus
#undef FIXTURE_CLOCK_pwm3_bus
#undef FIXTURE_CLOCK_pwm4_bus
#undef FIXTURE_CLOCK_pwm1_bits
#undef FIXTURE_CLOCK_pwm3_bits
#undef FIXTURE_CLOCK_pwm4_bits
#define FIXTURE_PROP_rcc_clock_frequency D202_HCLK
#define FIXTURE_PROP_rcc_ahb_prescaler D202_AHB
#define FIXTURE_PROP_rcc_apb1_prescaler D202_APB1
#define FIXTURE_PROP_rcc_apb2_prescaler D202_APB2
#define FIXTURE_PROP_pwm1_st_prescaler D202_PSC0
#define FIXTURE_PROP_pwm3_st_prescaler D202_PSC1
#define FIXTURE_PROP_pwm4_st_prescaler D202_PSC2
#define FIXTURE_CLOCK_pwm1_bus (D202_DOMAIN0 | (D202_DIV0 << 12))
#define FIXTURE_CLOCK_pwm3_bus (D202_DOMAIN1 | (D202_DIV1 << 12))
#define FIXTURE_CLOCK_pwm4_bus (D202_DOMAIN2 | (D202_DIV2 << 12))
#define FIXTURE_CLOCK_pwm1_bits D202_SELECTOR0
#define FIXTURE_CLOCK_pwm3_bits D202_SELECTOR1
#define FIXTURE_CLOCK_pwm4_bits D202_SELECTOR2

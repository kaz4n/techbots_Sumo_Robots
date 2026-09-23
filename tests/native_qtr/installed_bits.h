// Copies source-verified installed STM32U585 declarations.
// Four-byte observable storage preserves native offsets and command encodings.
// Independent B2 tests supply hardware side effects and fault injection.
#pragma once
/* Copyright (c) 2021 STMicroelectronics. All rights reserved.
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 * Extracted from the exact installed headers retained with hashes in
 * state/analysis/P2_adc_ownership_raw/headers/manifest.json.
 */
#define DBGMCU_IDCODE_DEV_ID_Pos            (0UL)
#define DBGMCU_IDCODE_DEV_ID_Msk            (0xFFFUL << DBGMCU_IDCODE_DEV_ID_Pos)
#define DBGMCU_IDCODE_DEV_ID                DBGMCU_IDCODE_DEV_ID_Msk
#define DBGMCU_IDCODE_REV_ID_Pos            (16UL)
#define DBGMCU_IDCODE_REV_ID_Msk            (0xFFFFUL << DBGMCU_IDCODE_REV_ID_Pos)
#define DBGMCU_IDCODE_REV_ID                DBGMCU_IDCODE_REV_ID_Msk
#define DBGMCU_CR_DBG_STOP_Pos              (1UL)
#define DBGMCU_CR_DBG_STOP_Msk              (0x1UL << DBGMCU_CR_DBG_STOP_Pos)
#define DBGMCU_CR_DBG_STOP                  DBGMCU_CR_DBG_STOP_Msk
#define DBGMCU_CR_DBG_STANDBY_Pos           (2UL)
#define DBGMCU_CR_DBG_STANDBY_Msk           (0x1UL << DBGMCU_CR_DBG_STANDBY_Pos)
#define DBGMCU_CR_DBG_STANDBY               DBGMCU_CR_DBG_STANDBY_Msk
#define DBGMCU_CR_TRACE_IOEN_Pos            (4UL)
#define DBGMCU_CR_TRACE_IOEN_Msk            (0x1UL << DBGMCU_CR_TRACE_IOEN_Pos)
#define DBGMCU_CR_TRACE_IOEN                DBGMCU_CR_TRACE_IOEN_Msk
#define DBGMCU_CR_TRACE_CLKEN_Pos           (5UL)
#define DBGMCU_CR_TRACE_CLKEN_Msk           (0x1UL << DBGMCU_CR_TRACE_CLKEN_Pos)
#define DBGMCU_CR_TRACE_CLKEN               DBGMCU_CR_TRACE_CLKEN_Msk
#define DBGMCU_CR_TRACE_MODE_Pos            (6UL)
#define DBGMCU_CR_TRACE_MODE_Msk            (0x3UL << DBGMCU_CR_TRACE_MODE_Pos)
#define DBGMCU_CR_TRACE_MODE                DBGMCU_CR_TRACE_MODE_Msk
#define DBGMCU_CR_TRACE_MODE_0              (0x1UL << DBGMCU_CR_TRACE_MODE_Pos)
#define DBGMCU_CR_TRACE_MODE_1              (0x2UL << DBGMCU_CR_TRACE_MODE_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM2_STOP_Pos   (0UL)
#define DBGMCU_APB1FZR1_DBG_TIM2_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_TIM2_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM2_STOP       DBGMCU_APB1FZR1_DBG_TIM2_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_TIM3_STOP_Pos   (1UL)
#define DBGMCU_APB1FZR1_DBG_TIM3_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_TIM3_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM3_STOP       DBGMCU_APB1FZR1_DBG_TIM3_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_TIM4_STOP_Pos   (2UL)
#define DBGMCU_APB1FZR1_DBG_TIM4_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_TIM4_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM4_STOP       DBGMCU_APB1FZR1_DBG_TIM4_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_TIM5_STOP_Pos   (3UL)
#define DBGMCU_APB1FZR1_DBG_TIM5_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_TIM5_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM5_STOP       DBGMCU_APB1FZR1_DBG_TIM5_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_TIM6_STOP_Pos   (4UL)
#define DBGMCU_APB1FZR1_DBG_TIM6_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_TIM6_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM6_STOP       DBGMCU_APB1FZR1_DBG_TIM6_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_TIM7_STOP_Pos   (5UL)
#define DBGMCU_APB1FZR1_DBG_TIM7_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_TIM7_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_TIM7_STOP       DBGMCU_APB1FZR1_DBG_TIM7_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_WWDG_STOP_Pos   (11UL)
#define DBGMCU_APB1FZR1_DBG_WWDG_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_WWDG_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_WWDG_STOP       DBGMCU_APB1FZR1_DBG_WWDG_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_IWDG_STOP_Pos   (12UL)
#define DBGMCU_APB1FZR1_DBG_IWDG_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_IWDG_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_IWDG_STOP       DBGMCU_APB1FZR1_DBG_IWDG_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_I2C1_STOP_Pos   (21UL)
#define DBGMCU_APB1FZR1_DBG_I2C1_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_I2C1_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_I2C1_STOP       DBGMCU_APB1FZR1_DBG_I2C1_STOP_Msk
#define DBGMCU_APB1FZR1_DBG_I2C2_STOP_Pos   (22UL)
#define DBGMCU_APB1FZR1_DBG_I2C2_STOP_Msk   (0x1UL << DBGMCU_APB1FZR1_DBG_I2C2_STOP_Pos)
#define DBGMCU_APB1FZR1_DBG_I2C2_STOP       DBGMCU_APB1FZR1_DBG_I2C2_STOP_Msk
#define DBGMCU_APB1FZR2_DBG_I2C4_STOP_Pos   (1UL)
#define DBGMCU_APB1FZR2_DBG_I2C4_STOP_Msk   (0x1UL << DBGMCU_APB1FZR2_DBG_I2C4_STOP_Pos)
#define DBGMCU_APB1FZR2_DBG_I2C4_STOP       DBGMCU_APB1FZR2_DBG_I2C4_STOP_Msk
#define DBGMCU_APB1FZR2_DBG_LPTIM2_STOP_Pos (5UL)
#define DBGMCU_APB1FZR2_DBG_LPTIM2_STOP_Msk (0x1UL << DBGMCU_APB1FZR2_DBG_LPTIM2_STOP_Pos)
#define DBGMCU_APB1FZR2_DBG_LPTIM2_STOP     DBGMCU_APB1FZR2_DBG_LPTIM2_STOP_Msk
#define DBGMCU_APB2FZR_DBG_TIM1_STOP_Pos    (11UL)
#define DBGMCU_APB2FZR_DBG_TIM1_STOP_Msk    (0x1UL << DBGMCU_APB2FZR_DBG_TIM1_STOP_Pos)
#define DBGMCU_APB2FZR_DBG_TIM1_STOP        DBGMCU_APB2FZR_DBG_TIM1_STOP_Msk
#define DBGMCU_APB2FZR_DBG_TIM8_STOP_Pos    (13UL)
#define DBGMCU_APB2FZR_DBG_TIM8_STOP_Msk    (0x1UL << DBGMCU_APB2FZR_DBG_TIM8_STOP_Pos)
#define DBGMCU_APB2FZR_DBG_TIM8_STOP        DBGMCU_APB2FZR_DBG_TIM8_STOP_Msk
#define DBGMCU_APB2FZR_DBG_TIM15_STOP_Pos   (16UL)
#define DBGMCU_APB2FZR_DBG_TIM15_STOP_Msk   (0x1UL << DBGMCU_APB2FZR_DBG_TIM15_STOP_Pos)
#define DBGMCU_APB2FZR_DBG_TIM15_STOP       DBGMCU_APB2FZR_DBG_TIM15_STOP_Msk
#define DBGMCU_APB2FZR_DBG_TIM16_STOP_Pos   (17UL)
#define DBGMCU_APB2FZR_DBG_TIM16_STOP_Msk   (0x1UL << DBGMCU_APB2FZR_DBG_TIM16_STOP_Pos)
#define DBGMCU_APB2FZR_DBG_TIM16_STOP       DBGMCU_APB2FZR_DBG_TIM16_STOP_Msk
#define DBGMCU_APB2FZR_DBG_TIM17_STOP_Pos   (18UL)
#define DBGMCU_APB2FZR_DBG_TIM17_STOP_Msk   (0x1UL << DBGMCU_APB2FZR_DBG_TIM17_STOP_Pos)
#define DBGMCU_APB2FZR_DBG_TIM17_STOP       DBGMCU_APB2FZR_DBG_TIM17_STOP_Msk
#define DBGMCU_APB3FZR_DBG_I2C3_STOP_Pos    (10UL)
#define DBGMCU_APB3FZR_DBG_I2C3_STOP_Msk    (0x1UL << DBGMCU_APB3FZR_DBG_I2C3_STOP_Pos)
#define DBGMCU_APB3FZR_DBG_I2C3_STOP        DBGMCU_APB3FZR_DBG_I2C3_STOP_Msk
#define DBGMCU_APB3FZR_DBG_LPTIM1_STOP_Pos  (17UL)
#define DBGMCU_APB3FZR_DBG_LPTIM1_STOP_Msk  (0x1UL << DBGMCU_APB3FZR_DBG_LPTIM1_STOP_Pos)
#define DBGMCU_APB3FZR_DBG_LPTIM1_STOP      DBGMCU_APB3FZR_DBG_LPTIM1_STOP_Msk
#define DBGMCU_APB3FZR_DBG_LPTIM3_STOP_Pos  (18UL)
#define DBGMCU_APB3FZR_DBG_LPTIM3_STOP_Msk  (0x1UL << DBGMCU_APB3FZR_DBG_LPTIM3_STOP_Pos)
#define DBGMCU_APB3FZR_DBG_LPTIM3_STOP      DBGMCU_APB3FZR_DBG_LPTIM3_STOP_Msk
#define DBGMCU_APB3FZR_DBG_LPTIM4_STOP_Pos  (19UL)
#define DBGMCU_APB3FZR_DBG_LPTIM4_STOP_Msk  (0x1UL << DBGMCU_APB3FZR_DBG_LPTIM4_STOP_Pos)
#define DBGMCU_APB3FZR_DBG_LPTIM4_STOP      DBGMCU_APB3FZR_DBG_LPTIM4_STOP_Msk
#define DBGMCU_APB3FZR_DBG_RTC_STOP_Pos     (30UL)
#define DBGMCU_APB3FZR_DBG_RTC_STOP_Msk     (0x1UL << DBGMCU_APB3FZR_DBG_RTC_STOP_Pos)
#define DBGMCU_APB3FZR_DBG_RTC_STOP         DBGMCU_APB3FZR_DBG_RTC_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA0_STOP_Pos  (0UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA0_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA0_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA0_STOP      DBGMCU_AHB1FZR_DBG_GPDMA0_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA1_STOP_Pos  (1UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA1_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA1_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA1_STOP      DBGMCU_AHB1FZR_DBG_GPDMA1_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA2_STOP_Pos  (2UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA2_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA2_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA2_STOP      DBGMCU_AHB1FZR_DBG_GPDMA2_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA3_STOP_Pos  (3UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA3_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA3_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA3_STOP      DBGMCU_AHB1FZR_DBG_GPDMA3_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA4_STOP_Pos  (4UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA4_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA4_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA4_STOP      DBGMCU_AHB1FZR_DBG_GPDMA4_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA5_STOP_Pos  (5UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA5_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA5_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA5_STOP      DBGMCU_AHB1FZR_DBG_GPDMA5_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA6_STOP_Pos  (6UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA6_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA6_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA6_STOP      DBGMCU_AHB1FZR_DBG_GPDMA6_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA7_STOP_Pos  (7UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA7_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA7_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA7_STOP      DBGMCU_AHB1FZR_DBG_GPDMA7_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA8_STOP_Pos  (8UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA8_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA8_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA8_STOP      DBGMCU_AHB1FZR_DBG_GPDMA8_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA9_STOP_Pos  (9UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA9_STOP_Msk  (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA9_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA9_STOP      DBGMCU_AHB1FZR_DBG_GPDMA9_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA10_STOP_Pos (10UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA10_STOP_Msk (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA10_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA10_STOP     DBGMCU_AHB1FZR_DBG_GPDMA10_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA11_STOP_Pos (11UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA11_STOP_Msk (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA11_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA11_STOP     DBGMCU_AHB1FZR_DBG_GPDMA11_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA12_STOP_Pos (12UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA12_STOP_Msk (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA12_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA12_STOP     DBGMCU_AHB1FZR_DBG_GPDMA12_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA13_STOP_Pos (13UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA13_STOP_Msk (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA13_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA13_STOP     DBGMCU_AHB1FZR_DBG_GPDMA13_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA14_STOP_Pos (14UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA14_STOP_Msk (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA14_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA14_STOP     DBGMCU_AHB1FZR_DBG_GPDMA14_STOP_Msk
#define DBGMCU_AHB1FZR_DBG_GPDMA15_STOP_Pos (15UL)
#define DBGMCU_AHB1FZR_DBG_GPDMA15_STOP_Msk (0x1UL << DBGMCU_AHB1FZR_DBG_GPDMA15_STOP_Pos)
#define DBGMCU_AHB1FZR_DBG_GPDMA15_STOP     DBGMCU_AHB1FZR_DBG_GPDMA15_STOP_Msk
#define DBGMCU_AHB3FZR_DBG_LPDMA0_STOP_Pos  (0UL)
#define DBGMCU_AHB3FZR_DBG_LPDMA0_STOP_Msk  (0x1UL << DBGMCU_AHB3FZR_DBG_LPDMA0_STOP_Pos)
#define DBGMCU_AHB3FZR_DBG_LPDMA0_STOP      DBGMCU_AHB3FZR_DBG_LPDMA0_STOP_Msk
#define DBGMCU_AHB3FZR_DBG_LPDMA1_STOP_Pos  (1UL)
#define DBGMCU_AHB3FZR_DBG_LPDMA1_STOP_Msk  (0x1UL << DBGMCU_AHB3FZR_DBG_LPDMA1_STOP_Pos)
#define DBGMCU_AHB3FZR_DBG_LPDMA1_STOP      DBGMCU_AHB3FZR_DBG_LPDMA1_STOP_Msk
#define DBGMCU_AHB3FZR_DBG_LPDMA2_STOP_Pos  (2UL)
#define DBGMCU_AHB3FZR_DBG_LPDMA2_STOP_Msk  (0x1UL << DBGMCU_AHB3FZR_DBG_LPDMA2_STOP_Pos)
#define DBGMCU_AHB3FZR_DBG_LPDMA2_STOP      DBGMCU_AHB3FZR_DBG_LPDMA2_STOP_Msk
#define DBGMCU_AHB3FZR_DBG_LPDMA3_STOP_Pos  (3UL)
#define DBGMCU_AHB3FZR_DBG_LPDMA3_STOP_Msk  (0x1UL << DBGMCU_AHB3FZR_DBG_LPDMA3_STOP_Pos)
#define DBGMCU_AHB3FZR_DBG_LPDMA3_STOP      DBGMCU_AHB3FZR_DBG_LPDMA3_STOP_Msk
#define EXTI_RTSR1_RT0_Pos                  (0UL)
#define EXTI_RTSR1_RT0_Msk                  (0x1UL << EXTI_RTSR1_RT0_Pos)
#define EXTI_RTSR1_RT0                      EXTI_RTSR1_RT0_Msk
#define EXTI_RTSR1_RT1_Pos                  (1UL)
#define EXTI_RTSR1_RT1_Msk                  (0x1UL << EXTI_RTSR1_RT1_Pos)
#define EXTI_RTSR1_RT1                      EXTI_RTSR1_RT1_Msk
#define EXTI_RTSR1_RT2_Pos                  (2UL)
#define EXTI_RTSR1_RT2_Msk                  (0x1UL << EXTI_RTSR1_RT2_Pos)
#define EXTI_RTSR1_RT2                      EXTI_RTSR1_RT2_Msk
#define EXTI_RTSR1_RT3_Pos                  (3UL)
#define EXTI_RTSR1_RT3_Msk                  (0x1UL << EXTI_RTSR1_RT3_Pos)
#define EXTI_RTSR1_RT3                      EXTI_RTSR1_RT3_Msk
#define EXTI_RTSR1_RT4_Pos                  (4UL)
#define EXTI_RTSR1_RT4_Msk                  (0x1UL << EXTI_RTSR1_RT4_Pos)
#define EXTI_RTSR1_RT4                      EXTI_RTSR1_RT4_Msk
#define EXTI_RTSR1_RT5_Pos                  (5UL)
#define EXTI_RTSR1_RT5_Msk                  (0x1UL << EXTI_RTSR1_RT5_Pos)
#define EXTI_RTSR1_RT5                      EXTI_RTSR1_RT5_Msk
#define EXTI_RTSR1_RT6_Pos                  (6UL)
#define EXTI_RTSR1_RT6_Msk                  (0x1UL << EXTI_RTSR1_RT6_Pos)
#define EXTI_RTSR1_RT6                      EXTI_RTSR1_RT6_Msk
#define EXTI_RTSR1_RT7_Pos                  (7UL)
#define EXTI_RTSR1_RT7_Msk                  (0x1UL << EXTI_RTSR1_RT7_Pos)
#define EXTI_RTSR1_RT7                      EXTI_RTSR1_RT7_Msk
#define EXTI_RTSR1_RT8_Pos                  (8UL)
#define EXTI_RTSR1_RT8_Msk                  (0x1UL << EXTI_RTSR1_RT8_Pos)
#define EXTI_RTSR1_RT8                      EXTI_RTSR1_RT8_Msk
#define EXTI_RTSR1_RT9_Pos                  (9UL)
#define EXTI_RTSR1_RT9_Msk                  (0x1UL << EXTI_RTSR1_RT9_Pos)
#define EXTI_RTSR1_RT9                      EXTI_RTSR1_RT9_Msk
#define EXTI_RTSR1_RT10_Pos                 (10UL)
#define EXTI_RTSR1_RT10_Msk                 (0x1UL << EXTI_RTSR1_RT10_Pos)
#define EXTI_RTSR1_RT10                     EXTI_RTSR1_RT10_Msk
#define EXTI_RTSR1_RT11_Pos                 (11UL)
#define EXTI_RTSR1_RT11_Msk                 (0x1UL << EXTI_RTSR1_RT11_Pos)
#define EXTI_RTSR1_RT11                     EXTI_RTSR1_RT11_Msk
#define EXTI_RTSR1_RT12_Pos                 (12UL)
#define EXTI_RTSR1_RT12_Msk                 (0x1UL << EXTI_RTSR1_RT12_Pos)
#define EXTI_RTSR1_RT12                     EXTI_RTSR1_RT12_Msk
#define EXTI_RTSR1_RT13_Pos                 (13UL)
#define EXTI_RTSR1_RT13_Msk                 (0x1UL << EXTI_RTSR1_RT13_Pos)
#define EXTI_RTSR1_RT13                     EXTI_RTSR1_RT13_Msk
#define EXTI_RTSR1_RT14_Pos                 (14UL)
#define EXTI_RTSR1_RT14_Msk                 (0x1UL << EXTI_RTSR1_RT14_Pos)
#define EXTI_RTSR1_RT14                     EXTI_RTSR1_RT14_Msk
#define EXTI_RTSR1_RT15_Pos                 (15UL)
#define EXTI_RTSR1_RT15_Msk                 (0x1UL << EXTI_RTSR1_RT15_Pos)
#define EXTI_RTSR1_RT15                     EXTI_RTSR1_RT15_Msk
#define EXTI_RTSR1_RT16_Pos                 (16UL)
#define EXTI_RTSR1_RT16_Msk                 (0x1UL << EXTI_RTSR1_RT16_Pos)
#define EXTI_RTSR1_RT16                     EXTI_RTSR1_RT16_Msk
#define EXTI_RTSR1_RT17_Pos                 (17UL)
#define EXTI_RTSR1_RT17_Msk                 (0x1UL << EXTI_RTSR1_RT17_Pos)
#define EXTI_RTSR1_RT17                     EXTI_RTSR1_RT17_Msk
#define EXTI_RTSR1_RT18_Pos                 (18UL)
#define EXTI_RTSR1_RT18_Msk                 (0x1UL << EXTI_RTSR1_RT18_Pos)
#define EXTI_RTSR1_RT18                     EXTI_RTSR1_RT18_Msk
#define EXTI_RTSR1_RT19_Pos                 (19UL)
#define EXTI_RTSR1_RT19_Msk                 (0x1UL << EXTI_RTSR1_RT19_Pos)
#define EXTI_RTSR1_RT19                     EXTI_RTSR1_RT19_Msk
#define EXTI_RTSR1_RT20_Pos                 (20UL)
#define EXTI_RTSR1_RT20_Msk                 (0x1UL << EXTI_RTSR1_RT20_Pos)
#define EXTI_RTSR1_RT20                     EXTI_RTSR1_RT20_Msk
#define EXTI_RTSR1_RT21_Pos                 (21UL)
#define EXTI_RTSR1_RT21_Msk                 (0x1UL << EXTI_RTSR1_RT21_Pos)
#define EXTI_RTSR1_RT21                     EXTI_RTSR1_RT21_Msk
#define EXTI_RTSR1_RT22_Pos                 (22UL)
#define EXTI_RTSR1_RT22_Msk                 (0x1UL << EXTI_RTSR1_RT22_Pos)
#define EXTI_RTSR1_RT22                     EXTI_RTSR1_RT22_Msk
#define EXTI_RTSR1_RT23_Pos                 (23UL)
#define EXTI_RTSR1_RT23_Msk                 (0x1UL << EXTI_RTSR1_RT23_Pos)
#define EXTI_RTSR1_RT23                     EXTI_RTSR1_RT23_Msk
#define EXTI_FTSR1_FT0_Pos                  (0UL)
#define EXTI_FTSR1_FT0_Msk                  (0x1UL << EXTI_FTSR1_FT0_Pos)
#define EXTI_FTSR1_FT0                      EXTI_FTSR1_FT0_Msk
#define EXTI_FTSR1_FT1_Pos                  (1UL)
#define EXTI_FTSR1_FT1_Msk                  (0x1UL << EXTI_FTSR1_FT1_Pos)
#define EXTI_FTSR1_FT1                      EXTI_FTSR1_FT1_Msk
#define EXTI_FTSR1_FT2_Pos                  (2UL)
#define EXTI_FTSR1_FT2_Msk                  (0x1UL << EXTI_FTSR1_FT2_Pos)
#define EXTI_FTSR1_FT2                      EXTI_FTSR1_FT2_Msk
#define EXTI_FTSR1_FT3_Pos                  (3UL)
#define EXTI_FTSR1_FT3_Msk                  (0x1UL << EXTI_FTSR1_FT3_Pos)
#define EXTI_FTSR1_FT3                      EXTI_FTSR1_FT3_Msk
#define EXTI_FTSR1_FT4_Pos                  (4UL)
#define EXTI_FTSR1_FT4_Msk                  (0x1UL << EXTI_FTSR1_FT4_Pos)
#define EXTI_FTSR1_FT4                      EXTI_FTSR1_FT4_Msk
#define EXTI_FTSR1_FT5_Pos                  (5UL)
#define EXTI_FTSR1_FT5_Msk                  (0x1UL << EXTI_FTSR1_FT5_Pos)
#define EXTI_FTSR1_FT5                      EXTI_FTSR1_FT5_Msk
#define EXTI_FTSR1_FT6_Pos                  (6UL)
#define EXTI_FTSR1_FT6_Msk                  (0x1UL << EXTI_FTSR1_FT6_Pos)
#define EXTI_FTSR1_FT6                      EXTI_FTSR1_FT6_Msk
#define EXTI_FTSR1_FT7_Pos                  (7UL)
#define EXTI_FTSR1_FT7_Msk                  (0x1UL << EXTI_FTSR1_FT7_Pos)
#define EXTI_FTSR1_FT7                      EXTI_FTSR1_FT7_Msk
#define EXTI_FTSR1_FT8_Pos                  (8UL)
#define EXTI_FTSR1_FT8_Msk                  (0x1UL << EXTI_FTSR1_FT8_Pos)
#define EXTI_FTSR1_FT8                      EXTI_FTSR1_FT8_Msk
#define EXTI_FTSR1_FT9_Pos                  (9UL)
#define EXTI_FTSR1_FT9_Msk                  (0x1UL << EXTI_FTSR1_FT9_Pos)
#define EXTI_FTSR1_FT9                      EXTI_FTSR1_FT9_Msk
#define EXTI_FTSR1_FT10_Pos                 (10UL)
#define EXTI_FTSR1_FT10_Msk                 (0x1UL << EXTI_FTSR1_FT10_Pos)
#define EXTI_FTSR1_FT10                     EXTI_FTSR1_FT10_Msk
#define EXTI_FTSR1_FT11_Pos                 (11UL)
#define EXTI_FTSR1_FT11_Msk                 (0x1UL << EXTI_FTSR1_FT11_Pos)
#define EXTI_FTSR1_FT11                     EXTI_FTSR1_FT11_Msk
#define EXTI_FTSR1_FT12_Pos                 (12UL)
#define EXTI_FTSR1_FT12_Msk                 (0x1UL << EXTI_FTSR1_FT12_Pos)
#define EXTI_FTSR1_FT12                     EXTI_FTSR1_FT12_Msk
#define EXTI_FTSR1_FT13_Pos                 (13UL)
#define EXTI_FTSR1_FT13_Msk                 (0x1UL << EXTI_FTSR1_FT13_Pos)
#define EXTI_FTSR1_FT13                     EXTI_FTSR1_FT13_Msk
#define EXTI_FTSR1_FT14_Pos                 (14UL)
#define EXTI_FTSR1_FT14_Msk                 (0x1UL << EXTI_FTSR1_FT14_Pos)
#define EXTI_FTSR1_FT14                     EXTI_FTSR1_FT14_Msk
#define EXTI_FTSR1_FT15_Pos                 (15UL)
#define EXTI_FTSR1_FT15_Msk                 (0x1UL << EXTI_FTSR1_FT15_Pos)
#define EXTI_FTSR1_FT15                     EXTI_FTSR1_FT15_Msk
#define EXTI_FTSR1_FT16_Pos                 (16UL)
#define EXTI_FTSR1_FT16_Msk                 (0x1UL << EXTI_FTSR1_FT16_Pos)
#define EXTI_FTSR1_FT16                     EXTI_FTSR1_FT16_Msk
#define EXTI_FTSR1_FT17_Pos                 (17UL)
#define EXTI_FTSR1_FT17_Msk                 (0x1UL << EXTI_FTSR1_FT17_Pos)
#define EXTI_FTSR1_FT17                     EXTI_FTSR1_FT17_Msk
#define EXTI_FTSR1_FT18_Pos                 (18UL)
#define EXTI_FTSR1_FT18_Msk                 (0x1UL << EXTI_FTSR1_FT18_Pos)
#define EXTI_FTSR1_FT18                     EXTI_FTSR1_FT18_Msk
#define EXTI_FTSR1_FT19_Pos                 (19UL)
#define EXTI_FTSR1_FT19_Msk                 (0x1UL << EXTI_FTSR1_FT19_Pos)
#define EXTI_FTSR1_FT19                     EXTI_FTSR1_FT19_Msk
#define EXTI_FTSR1_FT20_Pos                 (20UL)
#define EXTI_FTSR1_FT20_Msk                 (0x1UL << EXTI_FTSR1_FT20_Pos)
#define EXTI_FTSR1_FT20                     EXTI_FTSR1_FT20_Msk
#define EXTI_FTSR1_FT21_Pos                 (21UL)
#define EXTI_FTSR1_FT21_Msk                 (0x1UL << EXTI_FTSR1_FT21_Pos)
#define EXTI_FTSR1_FT21                     EXTI_FTSR1_FT21_Msk
#define EXTI_FTSR1_FT22_Pos                 (22UL)
#define EXTI_FTSR1_FT22_Msk                 (0x1UL << EXTI_FTSR1_FT22_Pos)
#define EXTI_FTSR1_FT22                     EXTI_FTSR1_FT22_Msk
#define EXTI_FTSR1_FT23_Pos                 (23UL)
#define EXTI_FTSR1_FT23_Msk                 (0x1UL << EXTI_FTSR1_FT23_Pos)
#define EXTI_FTSR1_FT23                     EXTI_FTSR1_FT23_Msk
#define EXTI_SWIER1_SWI0_Pos                (0UL)
#define EXTI_SWIER1_SWI0_Msk                (0x1UL << EXTI_SWIER1_SWI0_Pos)
#define EXTI_SWIER1_SWI0                    EXTI_SWIER1_SWI0_Msk
#define EXTI_SWIER1_SWI1_Pos                (1UL)
#define EXTI_SWIER1_SWI1_Msk                (0x1UL << EXTI_SWIER1_SWI1_Pos)
#define EXTI_SWIER1_SWI1                    EXTI_SWIER1_SWI1_Msk
#define EXTI_SWIER1_SWI2_Pos                (2UL)
#define EXTI_SWIER1_SWI2_Msk                (0x1UL << EXTI_SWIER1_SWI2_Pos)
#define EXTI_SWIER1_SWI2                    EXTI_SWIER1_SWI2_Msk
#define EXTI_SWIER1_SWI3_Pos                (3UL)
#define EXTI_SWIER1_SWI3_Msk                (0x1UL << EXTI_SWIER1_SWI3_Pos)
#define EXTI_SWIER1_SWI3                    EXTI_SWIER1_SWI3_Msk
#define EXTI_SWIER1_SWI4_Pos                (4UL)
#define EXTI_SWIER1_SWI4_Msk                (0x1UL << EXTI_SWIER1_SWI4_Pos)
#define EXTI_SWIER1_SWI4                    EXTI_SWIER1_SWI4_Msk
#define EXTI_SWIER1_SWI5_Pos                (5UL)
#define EXTI_SWIER1_SWI5_Msk                (0x1UL << EXTI_SWIER1_SWI5_Pos)
#define EXTI_SWIER1_SWI5                    EXTI_SWIER1_SWI5_Msk
#define EXTI_SWIER1_SWI6_Pos                (6UL)
#define EXTI_SWIER1_SWI6_Msk                (0x1UL << EXTI_SWIER1_SWI6_Pos)
#define EXTI_SWIER1_SWI6                    EXTI_SWIER1_SWI6_Msk
#define EXTI_SWIER1_SWI7_Pos                (7UL)
#define EXTI_SWIER1_SWI7_Msk                (0x1UL << EXTI_SWIER1_SWI7_Pos)
#define EXTI_SWIER1_SWI7                    EXTI_SWIER1_SWI7_Msk
#define EXTI_SWIER1_SWI8_Pos                (8UL)
#define EXTI_SWIER1_SWI8_Msk                (0x1UL << EXTI_SWIER1_SWI8_Pos)
#define EXTI_SWIER1_SWI8                    EXTI_SWIER1_SWI8_Msk
#define EXTI_SWIER1_SWI9_Pos                (9UL)
#define EXTI_SWIER1_SWI9_Msk                (0x1UL << EXTI_SWIER1_SWI9_Pos)
#define EXTI_SWIER1_SWI9                    EXTI_SWIER1_SWI9_Msk
#define EXTI_SWIER1_SWI10_Pos               (10UL)
#define EXTI_SWIER1_SWI10_Msk               (0x1UL << EXTI_SWIER1_SWI10_Pos)
#define EXTI_SWIER1_SWI10                   EXTI_SWIER1_SWI10_Msk
#define EXTI_SWIER1_SWI11_Pos               (11UL)
#define EXTI_SWIER1_SWI11_Msk               (0x1UL << EXTI_SWIER1_SWI11_Pos)
#define EXTI_SWIER1_SWI11                   EXTI_SWIER1_SWI11_Msk
#define EXTI_SWIER1_SWI12_Pos               (12UL)
#define EXTI_SWIER1_SWI12_Msk               (0x1UL << EXTI_SWIER1_SWI12_Pos)
#define EXTI_SWIER1_SWI12                   EXTI_SWIER1_SWI12_Msk
#define EXTI_SWIER1_SWI13_Pos               (13UL)
#define EXTI_SWIER1_SWI13_Msk               (0x1UL << EXTI_SWIER1_SWI13_Pos)
#define EXTI_SWIER1_SWI13                   EXTI_SWIER1_SWI13_Msk
#define EXTI_SWIER1_SWI14_Pos               (14UL)
#define EXTI_SWIER1_SWI14_Msk               (0x1UL << EXTI_SWIER1_SWI14_Pos)
#define EXTI_SWIER1_SWI14                   EXTI_SWIER1_SWI14_Msk
#define EXTI_SWIER1_SWI15_Pos               (15UL)
#define EXTI_SWIER1_SWI15_Msk               (0x1UL << EXTI_SWIER1_SWI15_Pos)
#define EXTI_SWIER1_SWI15                   EXTI_SWIER1_SWI15_Msk
#define EXTI_SWIER1_SWI16_Pos               (16UL)
#define EXTI_SWIER1_SWI16_Msk               (0x1UL << EXTI_SWIER1_SWI16_Pos)
#define EXTI_SWIER1_SWI16                   EXTI_SWIER1_SWI16_Msk
#define EXTI_SWIER1_SWI17_Pos               (17UL)
#define EXTI_SWIER1_SWI17_Msk               (0x1UL << EXTI_SWIER1_SWI17_Pos)
#define EXTI_SWIER1_SWI17                   EXTI_SWIER1_SWI17_Msk
#define EXTI_SWIER1_SWI18_Pos               (18UL)
#define EXTI_SWIER1_SWI18_Msk               (0x1UL << EXTI_SWIER1_SWI18_Pos)
#define EXTI_SWIER1_SWI18                   EXTI_SWIER1_SWI18_Msk
#define EXTI_SWIER1_SWI19_Pos               (19UL)
#define EXTI_SWIER1_SWI19_Msk               (0x1UL << EXTI_SWIER1_SWI19_Pos)
#define EXTI_SWIER1_SWI19                   EXTI_SWIER1_SWI19_Msk
#define EXTI_SWIER1_SWI20_Pos               (20UL)
#define EXTI_SWIER1_SWI20_Msk               (0x1UL << EXTI_SWIER1_SWI20_Pos)
#define EXTI_SWIER1_SWI20                   EXTI_SWIER1_SWI20_Msk
#define EXTI_SWIER1_SWI21_Pos               (21UL)
#define EXTI_SWIER1_SWI21_Msk               (0x1UL << EXTI_SWIER1_SWI21_Pos)
#define EXTI_SWIER1_SWI21                   EXTI_SWIER1_SWI21_Msk
#define EXTI_SWIER1_SWI22_Pos               (22UL)
#define EXTI_SWIER1_SWI22_Msk               (0x1UL << EXTI_SWIER1_SWI22_Pos)
#define EXTI_SWIER1_SWI22                   EXTI_SWIER1_SWI22_Msk
#define EXTI_SWIER1_SWI23_Pos               (23UL)
#define EXTI_SWIER1_SWI23_Msk               (0x1UL << EXTI_SWIER1_SWI23_Pos)
#define EXTI_SWIER1_SWI23                   EXTI_SWIER1_SWI23_Msk
#define EXTI_RPR1_RPIF0_Pos                 (0UL)
#define EXTI_RPR1_RPIF0_Msk                 (0x1UL << EXTI_RPR1_RPIF0_Pos)
#define EXTI_RPR1_RPIF0                     EXTI_RPR1_RPIF0_Msk
#define EXTI_RPR1_RPIF1_Pos                 (1UL)
#define EXTI_RPR1_RPIF1_Msk                 (0x1UL << EXTI_RPR1_RPIF1_Pos)
#define EXTI_RPR1_RPIF1                     EXTI_RPR1_RPIF1_Msk
#define EXTI_RPR1_RPIF2_Pos                 (2UL)
#define EXTI_RPR1_RPIF2_Msk                 (0x1UL << EXTI_RPR1_RPIF2_Pos)
#define EXTI_RPR1_RPIF2                     EXTI_RPR1_RPIF2_Msk
#define EXTI_RPR1_RPIF3_Pos                 (3UL)
#define EXTI_RPR1_RPIF3_Msk                 (0x1UL << EXTI_RPR1_RPIF3_Pos)
#define EXTI_RPR1_RPIF3                     EXTI_RPR1_RPIF3_Msk
#define EXTI_RPR1_RPIF4_Pos                 (4UL)
#define EXTI_RPR1_RPIF4_Msk                 (0x1UL << EXTI_RPR1_RPIF4_Pos)
#define EXTI_RPR1_RPIF4                     EXTI_RPR1_RPIF4_Msk
#define EXTI_RPR1_RPIF5_Pos                 (5UL)
#define EXTI_RPR1_RPIF5_Msk                 (0x1UL << EXTI_RPR1_RPIF5_Pos)
#define EXTI_RPR1_RPIF5                     EXTI_RPR1_RPIF5_Msk
#define EXTI_RPR1_RPIF6_Pos                 (6UL)
#define EXTI_RPR1_RPIF6_Msk                 (0x1UL << EXTI_RPR1_RPIF6_Pos)
#define EXTI_RPR1_RPIF6                     EXTI_RPR1_RPIF6_Msk
#define EXTI_RPR1_RPIF7_Pos                 (7UL)
#define EXTI_RPR1_RPIF7_Msk                 (0x1UL << EXTI_RPR1_RPIF7_Pos)
#define EXTI_RPR1_RPIF7                     EXTI_RPR1_RPIF7_Msk
#define EXTI_RPR1_RPIF8_Pos                 (8UL)
#define EXTI_RPR1_RPIF8_Msk                 (0x1UL << EXTI_RPR1_RPIF8_Pos)
#define EXTI_RPR1_RPIF8                     EXTI_RPR1_RPIF8_Msk
#define EXTI_RPR1_RPIF9_Pos                 (9UL)
#define EXTI_RPR1_RPIF9_Msk                 (0x1UL << EXTI_RPR1_RPIF9_Pos)
#define EXTI_RPR1_RPIF9                     EXTI_RPR1_RPIF9_Msk
#define EXTI_RPR1_RPIF10_Pos                (10UL)
#define EXTI_RPR1_RPIF10_Msk                (0x1UL << EXTI_RPR1_RPIF10_Pos)
#define EXTI_RPR1_RPIF10                    EXTI_RPR1_RPIF10_Msk
#define EXTI_RPR1_RPIF11_Pos                (11UL)
#define EXTI_RPR1_RPIF11_Msk                (0x1UL << EXTI_RPR1_RPIF11_Pos)
#define EXTI_RPR1_RPIF11                    EXTI_RPR1_RPIF11_Msk
#define EXTI_RPR1_RPIF12_Pos                (12UL)
#define EXTI_RPR1_RPIF12_Msk                (0x1UL << EXTI_RPR1_RPIF12_Pos)
#define EXTI_RPR1_RPIF12                    EXTI_RPR1_RPIF12_Msk
#define EXTI_RPR1_RPIF13_Pos                (13UL)
#define EXTI_RPR1_RPIF13_Msk                (0x1UL << EXTI_RPR1_RPIF13_Pos)
#define EXTI_RPR1_RPIF13                    EXTI_RPR1_RPIF13_Msk
#define EXTI_RPR1_RPIF14_Pos                (14UL)
#define EXTI_RPR1_RPIF14_Msk                (0x1UL << EXTI_RPR1_RPIF14_Pos)
#define EXTI_RPR1_RPIF14                    EXTI_RPR1_RPIF14_Msk
#define EXTI_RPR1_RPIF15_Pos                (15UL)
#define EXTI_RPR1_RPIF15_Msk                (0x1UL << EXTI_RPR1_RPIF15_Pos)
#define EXTI_RPR1_RPIF15                    EXTI_RPR1_RPIF15_Msk
#define EXTI_RPR1_RPIF16_Pos                (16UL)
#define EXTI_RPR1_RPIF16_Msk                (0x1UL << EXTI_RPR1_RPIF16_Pos)
#define EXTI_RPR1_RPIF16                    EXTI_RPR1_RPIF16_Msk
#define EXTI_RPR1_RPIF17_Pos                (17UL)
#define EXTI_RPR1_RPIF17_Msk                (0x1UL << EXTI_RPR1_RPIF17_Pos)
#define EXTI_RPR1_RPIF17                    EXTI_RPR1_RPIF17_Msk
#define EXTI_RPR1_RPIF18_Pos                (18UL)
#define EXTI_RPR1_RPIF18_Msk                (0x1UL << EXTI_RPR1_RPIF18_Pos)
#define EXTI_RPR1_RPIF18                    EXTI_RPR1_RPIF18_Msk
#define EXTI_RPR1_RPIF19_Pos                (19UL)
#define EXTI_RPR1_RPIF19_Msk                (0x1UL << EXTI_RPR1_RPIF19_Pos)
#define EXTI_RPR1_RPIF19                    EXTI_RPR1_RPIF19_Msk
#define EXTI_RPR1_RPIF20_Pos                (20UL)
#define EXTI_RPR1_RPIF20_Msk                (0x1UL << EXTI_RPR1_RPIF20_Pos)
#define EXTI_RPR1_RPIF20                    EXTI_RPR1_RPIF20_Msk
#define EXTI_RPR1_RPIF21_Pos                (21UL)
#define EXTI_RPR1_RPIF21_Msk                (0x1UL << EXTI_RPR1_RPIF21_Pos)
#define EXTI_RPR1_RPIF21                    EXTI_RPR1_RPIF21_Msk
#define EXTI_RPR1_RPIF22_Pos                (22UL)
#define EXTI_RPR1_RPIF22_Msk                (0x1UL << EXTI_RPR1_RPIF22_Pos)
#define EXTI_RPR1_RPIF22                    EXTI_RPR1_RPIF22_Msk
#define EXTI_RPR1_RPIF23_Pos                (23UL)
#define EXTI_RPR1_RPIF23_Msk                (0x1UL << EXTI_RPR1_RPIF23_Pos)
#define EXTI_RPR1_RPIF23                    EXTI_RPR1_RPIF23_Msk
#define EXTI_FPR1_FPIF0_Pos                 (0UL)
#define EXTI_FPR1_FPIF0_Msk                 (0x1UL << EXTI_FPR1_FPIF0_Pos)
#define EXTI_FPR1_FPIF0                     EXTI_FPR1_FPIF0_Msk
#define EXTI_FPR1_FPIF1_Pos                 (1UL)
#define EXTI_FPR1_FPIF1_Msk                 (0x1UL << EXTI_FPR1_FPIF1_Pos)
#define EXTI_FPR1_FPIF1                     EXTI_FPR1_FPIF1_Msk
#define EXTI_FPR1_FPIF2_Pos                 (2UL)
#define EXTI_FPR1_FPIF2_Msk                 (0x1UL << EXTI_FPR1_FPIF2_Pos)
#define EXTI_FPR1_FPIF2                     EXTI_FPR1_FPIF2_Msk
#define EXTI_FPR1_FPIF3_Pos                 (3UL)
#define EXTI_FPR1_FPIF3_Msk                 (0x1UL << EXTI_FPR1_FPIF3_Pos)
#define EXTI_FPR1_FPIF3                     EXTI_FPR1_FPIF3_Msk
#define EXTI_FPR1_FPIF4_Pos                 (4UL)
#define EXTI_FPR1_FPIF4_Msk                 (0x1UL << EXTI_FPR1_FPIF4_Pos)
#define EXTI_FPR1_FPIF4                     EXTI_FPR1_FPIF4_Msk
#define EXTI_FPR1_FPIF5_Pos                 (5UL)
#define EXTI_FPR1_FPIF5_Msk                 (0x1UL << EXTI_FPR1_FPIF5_Pos)
#define EXTI_FPR1_FPIF5                     EXTI_FPR1_FPIF5_Msk
#define EXTI_FPR1_FPIF6_Pos                 (6UL)
#define EXTI_FPR1_FPIF6_Msk                 (0x1UL << EXTI_FPR1_FPIF6_Pos)
#define EXTI_FPR1_FPIF6                     EXTI_FPR1_FPIF6_Msk
#define EXTI_FPR1_FPIF7_Pos                 (7UL)
#define EXTI_FPR1_FPIF7_Msk                 (0x1UL << EXTI_FPR1_FPIF7_Pos)
#define EXTI_FPR1_FPIF7                     EXTI_FPR1_FPIF7_Msk
#define EXTI_FPR1_FPIF8_Pos                 (8UL)
#define EXTI_FPR1_FPIF8_Msk                 (0x1UL << EXTI_FPR1_FPIF8_Pos)
#define EXTI_FPR1_FPIF8                     EXTI_FPR1_FPIF8_Msk
#define EXTI_FPR1_FPIF9_Pos                 (9UL)
#define EXTI_FPR1_FPIF9_Msk                 (0x1UL << EXTI_FPR1_FPIF9_Pos)
#define EXTI_FPR1_FPIF9                     EXTI_FPR1_FPIF9_Msk
#define EXTI_FPR1_FPIF10_Pos                (10UL)
#define EXTI_FPR1_FPIF10_Msk                (0x1UL << EXTI_FPR1_FPIF10_Pos)
#define EXTI_FPR1_FPIF10                    EXTI_FPR1_FPIF10_Msk
#define EXTI_FPR1_FPIF11_Pos                (11UL)
#define EXTI_FPR1_FPIF11_Msk                (0x1UL << EXTI_FPR1_FPIF11_Pos)
#define EXTI_FPR1_FPIF11                    EXTI_FPR1_FPIF11_Msk
#define EXTI_FPR1_FPIF12_Pos                (12UL)
#define EXTI_FPR1_FPIF12_Msk                (0x1UL << EXTI_FPR1_FPIF12_Pos)
#define EXTI_FPR1_FPIF12                    EXTI_FPR1_FPIF12_Msk
#define EXTI_FPR1_FPIF13_Pos                (13UL)
#define EXTI_FPR1_FPIF13_Msk                (0x1UL << EXTI_FPR1_FPIF13_Pos)
#define EXTI_FPR1_FPIF13                    EXTI_FPR1_FPIF13_Msk
#define EXTI_FPR1_FPIF14_Pos                (14UL)
#define EXTI_FPR1_FPIF14_Msk                (0x1UL << EXTI_FPR1_FPIF14_Pos)
#define EXTI_FPR1_FPIF14                    EXTI_FPR1_FPIF14_Msk
#define EXTI_FPR1_FPIF15_Pos                (15UL)
#define EXTI_FPR1_FPIF15_Msk                (0x1UL << EXTI_FPR1_FPIF15_Pos)
#define EXTI_FPR1_FPIF15                    EXTI_FPR1_FPIF15_Msk
#define EXTI_FPR1_FPIF16_Pos                (16UL)
#define EXTI_FPR1_FPIF16_Msk                (0x1UL << EXTI_FPR1_FPIF16_Pos)
#define EXTI_FPR1_FPIF16                    EXTI_FPR1_FPIF16_Msk
#define EXTI_FPR1_FPIF17_Pos                (17UL)
#define EXTI_FPR1_FPIF17_Msk                (0x1UL << EXTI_FPR1_FPIF17_Pos)
#define EXTI_FPR1_FPIF17                    EXTI_FPR1_FPIF17_Msk
#define EXTI_FPR1_FPIF18_Pos                (18UL)
#define EXTI_FPR1_FPIF18_Msk                (0x1UL << EXTI_FPR1_FPIF18_Pos)
#define EXTI_FPR1_FPIF18                    EXTI_FPR1_FPIF18_Msk
#define EXTI_FPR1_FPIF19_Pos                (19UL)
#define EXTI_FPR1_FPIF19_Msk                (0x1UL << EXTI_FPR1_FPIF19_Pos)
#define EXTI_FPR1_FPIF19                    EXTI_FPR1_FPIF19_Msk
#define EXTI_FPR1_FPIF20_Pos                (20UL)
#define EXTI_FPR1_FPIF20_Msk                (0x1UL << EXTI_FPR1_FPIF20_Pos)
#define EXTI_FPR1_FPIF20                    EXTI_FPR1_FPIF20_Msk
#define EXTI_FPR1_FPIF21_Pos                (21UL)
#define EXTI_FPR1_FPIF21_Msk                (0x1UL << EXTI_FPR1_FPIF21_Pos)
#define EXTI_FPR1_FPIF21                    EXTI_FPR1_FPIF21_Msk
#define EXTI_FPR1_FPIF22_Pos                (22UL)
#define EXTI_FPR1_FPIF22_Msk                (0x1UL << EXTI_FPR1_FPIF22_Pos)
#define EXTI_FPR1_FPIF22                    EXTI_FPR1_FPIF22_Msk
#define EXTI_FPR1_FPIF23_Pos                (23UL)
#define EXTI_FPR1_FPIF23_Msk                (0x1UL << EXTI_FPR1_FPIF23_Pos)
#define EXTI_FPR1_FPIF23                    EXTI_FPR1_FPIF23_Msk
#define EXTI_SECCFGR1_SEC0_Pos              (0UL)
#define EXTI_SECCFGR1_SEC0_Msk              (0x1UL << EXTI_SECCFGR1_SEC0_Pos)
#define EXTI_SECCFGR1_SEC0                  EXTI_SECCFGR1_SEC0_Msk
#define EXTI_SECCFGR1_SEC1_Pos              (1UL)
#define EXTI_SECCFGR1_SEC1_Msk              (0x1UL << EXTI_SECCFGR1_SEC1_Pos)
#define EXTI_SECCFGR1_SEC1                  EXTI_SECCFGR1_SEC1_Msk
#define EXTI_SECCFGR1_SEC2_Pos              (2UL)
#define EXTI_SECCFGR1_SEC2_Msk              (0x1UL << EXTI_SECCFGR1_SEC2_Pos)
#define EXTI_SECCFGR1_SEC2                  EXTI_SECCFGR1_SEC2_Msk
#define EXTI_SECCFGR1_SEC3_Pos              (3UL)
#define EXTI_SECCFGR1_SEC3_Msk              (0x1UL << EXTI_SECCFGR1_SEC3_Pos)
#define EXTI_SECCFGR1_SEC3                  EXTI_SECCFGR1_SEC3_Msk
#define EXTI_SECCFGR1_SEC4_Pos              (4UL)
#define EXTI_SECCFGR1_SEC4_Msk              (0x1UL << EXTI_SECCFGR1_SEC4_Pos)
#define EXTI_SECCFGR1_SEC4                  EXTI_SECCFGR1_SEC4_Msk
#define EXTI_SECCFGR1_SEC5_Pos              (5UL)
#define EXTI_SECCFGR1_SEC5_Msk              (0x1UL << EXTI_SECCFGR1_SEC5_Pos)
#define EXTI_SECCFGR1_SEC5                  EXTI_SECCFGR1_SEC5_Msk
#define EXTI_SECCFGR1_SEC6_Pos              (6UL)
#define EXTI_SECCFGR1_SEC6_Msk              (0x1UL << EXTI_SECCFGR1_SEC6_Pos)
#define EXTI_SECCFGR1_SEC6                  EXTI_SECCFGR1_SEC6_Msk
#define EXTI_SECCFGR1_SEC7_Pos              (7UL)
#define EXTI_SECCFGR1_SEC7_Msk              (0x1UL << EXTI_SECCFGR1_SEC7_Pos)
#define EXTI_SECCFGR1_SEC7                  EXTI_SECCFGR1_SEC7_Msk
#define EXTI_SECCFGR1_SEC8_Pos              (8UL)
#define EXTI_SECCFGR1_SEC8_Msk              (0x1UL << EXTI_SECCFGR1_SEC8_Pos)
#define EXTI_SECCFGR1_SEC8                  EXTI_SECCFGR1_SEC8_Msk
#define EXTI_SECCFGR1_SEC9_Pos              (9UL)
#define EXTI_SECCFGR1_SEC9_Msk              (0x1UL << EXTI_SECCFGR1_SEC9_Pos)
#define EXTI_SECCFGR1_SEC9                  EXTI_SECCFGR1_SEC9_Msk
#define EXTI_SECCFGR1_SEC10_Pos             (10UL)
#define EXTI_SECCFGR1_SEC10_Msk             (0x1UL << EXTI_SECCFGR1_SEC10_Pos)
#define EXTI_SECCFGR1_SEC10                 EXTI_SECCFGR1_SEC10_Msk
#define EXTI_SECCFGR1_SEC11_Pos             (11UL)
#define EXTI_SECCFGR1_SEC11_Msk             (0x1UL << EXTI_SECCFGR1_SEC11_Pos)
#define EXTI_SECCFGR1_SEC11                 EXTI_SECCFGR1_SEC11_Msk
#define EXTI_SECCFGR1_SEC12_Pos             (12UL)
#define EXTI_SECCFGR1_SEC12_Msk             (0x1UL << EXTI_SECCFGR1_SEC12_Pos)
#define EXTI_SECCFGR1_SEC12                 EXTI_SECCFGR1_SEC12_Msk
#define EXTI_SECCFGR1_SEC13_Pos             (13UL)
#define EXTI_SECCFGR1_SEC13_Msk             (0x1UL << EXTI_SECCFGR1_SEC13_Pos)
#define EXTI_SECCFGR1_SEC13                 EXTI_SECCFGR1_SEC13_Msk
#define EXTI_SECCFGR1_SEC14_Pos             (14UL)
#define EXTI_SECCFGR1_SEC14_Msk             (0x1UL << EXTI_SECCFGR1_SEC14_Pos)
#define EXTI_SECCFGR1_SEC14                 EXTI_SECCFGR1_SEC14_Msk
#define EXTI_SECCFGR1_SEC15_Pos             (15UL)
#define EXTI_SECCFGR1_SEC15_Msk             (0x1UL << EXTI_SECCFGR1_SEC15_Pos)
#define EXTI_SECCFGR1_SEC15                 EXTI_SECCFGR1_SEC15_Msk
#define EXTI_SECCFGR1_SEC16_Pos             (16UL)
#define EXTI_SECCFGR1_SEC16_Msk             (0x1UL << EXTI_SECCFGR1_SEC16_Pos)
#define EXTI_SECCFGR1_SEC16                 EXTI_SECCFGR1_SEC16_Msk
#define EXTI_SECCFGR1_SEC17_Pos             (17UL)
#define EXTI_SECCFGR1_SEC17_Msk             (0x1UL << EXTI_SECCFGR1_SEC17_Pos)
#define EXTI_SECCFGR1_SEC17                 EXTI_SECCFGR1_SEC17_Msk
#define EXTI_SECCFGR1_SEC18_Pos             (18UL)
#define EXTI_SECCFGR1_SEC18_Msk             (0x1UL << EXTI_SECCFGR1_SEC18_Pos)
#define EXTI_SECCFGR1_SEC18                 EXTI_SECCFGR1_SEC18_Msk
#define EXTI_SECCFGR1_SEC19_Pos             (19UL)
#define EXTI_SECCFGR1_SEC19_Msk             (0x1UL << EXTI_SECCFGR1_SEC19_Pos)
#define EXTI_SECCFGR1_SEC19                 EXTI_SECCFGR1_SEC19_Msk
#define EXTI_SECCFGR1_SEC20_Pos             (20UL)
#define EXTI_SECCFGR1_SEC20_Msk             (0x1UL << EXTI_SECCFGR1_SEC20_Pos)
#define EXTI_SECCFGR1_SEC20                 EXTI_SECCFGR1_SEC20_Msk
#define EXTI_SECCFGR1_SEC21_Pos             (21UL)
#define EXTI_SECCFGR1_SEC21_Msk             (0x1UL << EXTI_SECCFGR1_SEC21_Pos)
#define EXTI_SECCFGR1_SEC21                 EXTI_SECCFGR1_SEC21_Msk
#define EXTI_SECCFGR1_SEC22_Pos             (22UL)
#define EXTI_SECCFGR1_SEC22_Msk             (0x1UL << EXTI_SECCFGR1_SEC22_Pos)
#define EXTI_SECCFGR1_SEC22                 EXTI_SECCFGR1_SEC22_Msk
#define EXTI_SECCFGR1_SEC23_Pos             (23UL)
#define EXTI_SECCFGR1_SEC23_Msk             (0x1UL << EXTI_SECCFGR1_SEC23_Pos)
#define EXTI_SECCFGR1_SEC23                 EXTI_SECCFGR1_SEC23_Msk
#define EXTI_PRIVCFGR1_PRIV0_Pos             (0UL)
#define EXTI_PRIVCFGR1_PRIV0_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV0_Pos)
#define EXTI_PRIVCFGR1_PRIV0                 EXTI_PRIVCFGR1_PRIV0_Msk
#define EXTI_PRIVCFGR1_PRIV1_Pos             (1UL)
#define EXTI_PRIVCFGR1_PRIV1_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV1_Pos)
#define EXTI_PRIVCFGR1_PRIV1                 EXTI_PRIVCFGR1_PRIV1_Msk
#define EXTI_PRIVCFGR1_PRIV2_Pos             (2UL)
#define EXTI_PRIVCFGR1_PRIV2_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV2_Pos)
#define EXTI_PRIVCFGR1_PRIV2                 EXTI_PRIVCFGR1_PRIV2_Msk
#define EXTI_PRIVCFGR1_PRIV3_Pos             (3UL)
#define EXTI_PRIVCFGR1_PRIV3_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV3_Pos)
#define EXTI_PRIVCFGR1_PRIV3                 EXTI_PRIVCFGR1_PRIV3_Msk
#define EXTI_PRIVCFGR1_PRIV4_Pos             (4UL)
#define EXTI_PRIVCFGR1_PRIV4_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV4_Pos)
#define EXTI_PRIVCFGR1_PRIV4                 EXTI_PRIVCFGR1_PRIV4_Msk
#define EXTI_PRIVCFGR1_PRIV5_Pos             (5UL)
#define EXTI_PRIVCFGR1_PRIV5_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV5_Pos)
#define EXTI_PRIVCFGR1_PRIV5                 EXTI_PRIVCFGR1_PRIV5_Msk
#define EXTI_PRIVCFGR1_PRIV6_Pos             (6UL)
#define EXTI_PRIVCFGR1_PRIV6_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV6_Pos)
#define EXTI_PRIVCFGR1_PRIV6                 EXTI_PRIVCFGR1_PRIV6_Msk
#define EXTI_PRIVCFGR1_PRIV7_Pos             (7UL)
#define EXTI_PRIVCFGR1_PRIV7_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV7_Pos)
#define EXTI_PRIVCFGR1_PRIV7                 EXTI_PRIVCFGR1_PRIV7_Msk
#define EXTI_PRIVCFGR1_PRIV8_Pos             (8UL)
#define EXTI_PRIVCFGR1_PRIV8_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV8_Pos)
#define EXTI_PRIVCFGR1_PRIV8                 EXTI_PRIVCFGR1_PRIV8_Msk
#define EXTI_PRIVCFGR1_PRIV9_Pos             (9UL)
#define EXTI_PRIVCFGR1_PRIV9_Msk             (0x1UL << EXTI_PRIVCFGR1_PRIV9_Pos)
#define EXTI_PRIVCFGR1_PRIV9                 EXTI_PRIVCFGR1_PRIV9_Msk
#define EXTI_PRIVCFGR1_PRIV10_Pos            (10UL)
#define EXTI_PRIVCFGR1_PRIV10_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV10_Pos)
#define EXTI_PRIVCFGR1_PRIV10                EXTI_PRIVCFGR1_PRIV10_Msk
#define EXTI_PRIVCFGR1_PRIV11_Pos            (11UL)
#define EXTI_PRIVCFGR1_PRIV11_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV11_Pos)
#define EXTI_PRIVCFGR1_PRIV11                EXTI_PRIVCFGR1_PRIV11_Msk
#define EXTI_PRIVCFGR1_PRIV12_Pos            (12UL)
#define EXTI_PRIVCFGR1_PRIV12_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV12_Pos)
#define EXTI_PRIVCFGR1_PRIV12                EXTI_PRIVCFGR1_PRIV12_Msk
#define EXTI_PRIVCFGR1_PRIV13_Pos            (13UL)
#define EXTI_PRIVCFGR1_PRIV13_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV13_Pos)
#define EXTI_PRIVCFGR1_PRIV13                EXTI_PRIVCFGR1_PRIV13_Msk
#define EXTI_PRIVCFGR1_PRIV14_Pos            (14UL)
#define EXTI_PRIVCFGR1_PRIV14_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV14_Pos)
#define EXTI_PRIVCFGR1_PRIV14                EXTI_PRIVCFGR1_PRIV14_Msk
#define EXTI_PRIVCFGR1_PRIV15_Pos            (15UL)
#define EXTI_PRIVCFGR1_PRIV15_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV15_Pos)
#define EXTI_PRIVCFGR1_PRIV15                EXTI_PRIVCFGR1_PRIV15_Msk
#define EXTI_PRIVCFGR1_PRIV16_Pos            (16UL)
#define EXTI_PRIVCFGR1_PRIV16_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV16_Pos)
#define EXTI_PRIVCFGR1_PRIV16                EXTI_PRIVCFGR1_PRIV16_Msk
#define EXTI_PRIVCFGR1_PRIV17_Pos            (17UL)
#define EXTI_PRIVCFGR1_PRIV17_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV17_Pos)
#define EXTI_PRIVCFGR1_PRIV17                EXTI_PRIVCFGR1_PRIV17_Msk
#define EXTI_PRIVCFGR1_PRIV18_Pos            (18UL)
#define EXTI_PRIVCFGR1_PRIV18_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV18_Pos)
#define EXTI_PRIVCFGR1_PRIV18                EXTI_PRIVCFGR1_PRIV18_Msk
#define EXTI_PRIVCFGR1_PRIV19_Pos            (19UL)
#define EXTI_PRIVCFGR1_PRIV19_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV19_Pos)
#define EXTI_PRIVCFGR1_PRIV19                EXTI_PRIVCFGR1_PRIV19_Msk
#define EXTI_PRIVCFGR1_PRIV20_Pos            (20UL)
#define EXTI_PRIVCFGR1_PRIV20_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV20_Pos)
#define EXTI_PRIVCFGR1_PRIV20                EXTI_PRIVCFGR1_PRIV20_Msk
#define EXTI_PRIVCFGR1_PRIV21_Pos            (21UL)
#define EXTI_PRIVCFGR1_PRIV21_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV21_Pos)
#define EXTI_PRIVCFGR1_PRIV21                EXTI_PRIVCFGR1_PRIV21_Msk
#define EXTI_PRIVCFGR1_PRIV22_Pos            (22UL)
#define EXTI_PRIVCFGR1_PRIV22_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV22_Pos)
#define EXTI_PRIVCFGR1_PRIV22                EXTI_PRIVCFGR1_PRIV22_Msk
#define EXTI_PRIVCFGR1_PRIV23_Pos            (23UL)
#define EXTI_PRIVCFGR1_PRIV23_Msk            (0x1UL << EXTI_PRIVCFGR1_PRIV23_Pos)
#define EXTI_PRIVCFGR1_PRIV23                EXTI_PRIVCFGR1_PRIV23_Msk
#define EXTI_EXTICR1_EXTI0_Pos              (0UL)
#define EXTI_EXTICR1_EXTI0_Msk              (0xFUL << EXTI_EXTICR1_EXTI0_Pos)
#define EXTI_EXTICR1_EXTI0                  EXTI_EXTICR1_EXTI0_Msk
#define EXTI_EXTICR1_EXTI0_0                (0x1UL << EXTI_EXTICR1_EXTI0_Pos)
#define EXTI_EXTICR1_EXTI0_1                (0x2UL << EXTI_EXTICR1_EXTI0_Pos)
#define EXTI_EXTICR1_EXTI0_2                (0x4UL << EXTI_EXTICR1_EXTI0_Pos)
#define EXTI_EXTICR1_EXTI0_3                (0x8UL << EXTI_EXTICR1_EXTI0_Pos)
#define EXTI_EXTICR1_EXTI1_Pos              (8UL)
#define EXTI_EXTICR1_EXTI1_Msk              (0xFUL << EXTI_EXTICR1_EXTI1_Pos)
#define EXTI_EXTICR1_EXTI1                  EXTI_EXTICR1_EXTI1_Msk
#define EXTI_EXTICR1_EXTI1_0                (0x1UL << EXTI_EXTICR1_EXTI1_Pos)
#define EXTI_EXTICR1_EXTI1_1                (0x2UL << EXTI_EXTICR1_EXTI1_Pos)
#define EXTI_EXTICR1_EXTI1_2                (0x4UL << EXTI_EXTICR1_EXTI1_Pos)
#define EXTI_EXTICR1_EXTI1_3                (0x8UL << EXTI_EXTICR1_EXTI1_Pos)
#define EXTI_EXTICR1_EXTI2_Pos              (16UL)
#define EXTI_EXTICR1_EXTI2_Msk              (0xFUL << EXTI_EXTICR1_EXTI2_Pos)
#define EXTI_EXTICR1_EXTI2                  EXTI_EXTICR1_EXTI2_Msk
#define EXTI_EXTICR1_EXTI2_0                (0x1UL << EXTI_EXTICR1_EXTI2_Pos)
#define EXTI_EXTICR1_EXTI2_1                (0x2UL << EXTI_EXTICR1_EXTI2_Pos)
#define EXTI_EXTICR1_EXTI2_2                (0x4UL << EXTI_EXTICR1_EXTI2_Pos)
#define EXTI_EXTICR1_EXTI2_3                (0x8UL << EXTI_EXTICR1_EXTI2_Pos)
#define EXTI_EXTICR1_EXTI3_Pos              (24UL)
#define EXTI_EXTICR1_EXTI3_Msk              (0xFUL << EXTI_EXTICR1_EXTI3_Pos)
#define EXTI_EXTICR1_EXTI3                  EXTI_EXTICR1_EXTI3_Msk
#define EXTI_EXTICR1_EXTI3_0                (0x1UL << EXTI_EXTICR1_EXTI3_Pos)
#define EXTI_EXTICR1_EXTI3_1                (0x2UL << EXTI_EXTICR1_EXTI3_Pos)
#define EXTI_EXTICR1_EXTI3_2                (0x4UL << EXTI_EXTICR1_EXTI3_Pos)
#define EXTI_EXTICR1_EXTI3_3                (0x8UL << EXTI_EXTICR1_EXTI3_Pos)
#define EXTI_EXTICR2_EXTI4_Pos              (0UL)
#define EXTI_EXTICR2_EXTI4_Msk              (0xFUL << EXTI_EXTICR2_EXTI4_Pos)
#define EXTI_EXTICR2_EXTI4                  EXTI_EXTICR2_EXTI4_Msk
#define EXTI_EXTICR2_EXTI4_0                (0x1UL << EXTI_EXTICR2_EXTI4_Pos)
#define EXTI_EXTICR2_EXTI4_1                (0x2UL << EXTI_EXTICR2_EXTI4_Pos)
#define EXTI_EXTICR2_EXTI4_2                (0x4UL << EXTI_EXTICR2_EXTI4_Pos)
#define EXTI_EXTICR2_EXTI4_3                (0x8UL << EXTI_EXTICR2_EXTI4_Pos)
#define EXTI_EXTICR2_EXTI5_Pos              (8UL)
#define EXTI_EXTICR2_EXTI5_Msk              (0xFUL << EXTI_EXTICR2_EXTI5_Pos)
#define EXTI_EXTICR2_EXTI5                  EXTI_EXTICR2_EXTI5_Msk
#define EXTI_EXTICR2_EXTI5_0                (0x1UL << EXTI_EXTICR2_EXTI5_Pos)
#define EXTI_EXTICR2_EXTI5_1                (0x2UL << EXTI_EXTICR2_EXTI5_Pos)
#define EXTI_EXTICR2_EXTI5_2                (0x4UL << EXTI_EXTICR2_EXTI5_Pos)
#define EXTI_EXTICR2_EXTI5_3                (0x8UL << EXTI_EXTICR2_EXTI5_Pos)
#define EXTI_EXTICR2_EXTI6_Pos              (16UL)
#define EXTI_EXTICR2_EXTI6_Msk              (0xFUL << EXTI_EXTICR2_EXTI6_Pos)
#define EXTI_EXTICR2_EXTI6                  EXTI_EXTICR2_EXTI6_Msk
#define EXTI_EXTICR2_EXTI6_0                (0x1UL << EXTI_EXTICR2_EXTI6_Pos)
#define EXTI_EXTICR2_EXTI6_1                (0x2UL << EXTI_EXTICR2_EXTI6_Pos)
#define EXTI_EXTICR2_EXTI6_2                (0x4UL << EXTI_EXTICR2_EXTI6_Pos)
#define EXTI_EXTICR2_EXTI6_3                (0x8UL << EXTI_EXTICR2_EXTI6_Pos)
#define EXTI_EXTICR2_EXTI7_Pos              (24UL)
#define EXTI_EXTICR2_EXTI7_Msk              (0xFUL << EXTI_EXTICR2_EXTI7_Pos)
#define EXTI_EXTICR2_EXTI7                  EXTI_EXTICR2_EXTI7_Msk
#define EXTI_EXTICR2_EXTI7_0                (0x1UL << EXTI_EXTICR2_EXTI7_Pos)
#define EXTI_EXTICR2_EXTI7_1                (0x2UL << EXTI_EXTICR2_EXTI7_Pos)
#define EXTI_EXTICR2_EXTI7_2                (0x4UL << EXTI_EXTICR2_EXTI7_Pos)
#define EXTI_EXTICR2_EXTI7_3                (0x8UL << EXTI_EXTICR2_EXTI7_Pos)
#define EXTI_EXTICR3_EXTI8_Pos              (0UL)
#define EXTI_EXTICR3_EXTI8_Msk              (0xFUL << EXTI_EXTICR3_EXTI8_Pos)
#define EXTI_EXTICR3_EXTI8                  EXTI_EXTICR3_EXTI8_Msk
#define EXTI_EXTICR3_EXTI8_0                (0x1UL << EXTI_EXTICR3_EXTI8_Pos)
#define EXTI_EXTICR3_EXTI8_1                (0x2UL << EXTI_EXTICR3_EXTI8_Pos)
#define EXTI_EXTICR3_EXTI8_2                (0x4UL << EXTI_EXTICR3_EXTI8_Pos)
#define EXTI_EXTICR3_EXTI8_3                (0x8UL << EXTI_EXTICR3_EXTI8_Pos)
#define EXTI_EXTICR3_EXTI9_Pos              (8UL)
#define EXTI_EXTICR3_EXTI9_Msk              (0xFUL << EXTI_EXTICR3_EXTI9_Pos)
#define EXTI_EXTICR3_EXTI9                  EXTI_EXTICR3_EXTI9_Msk
#define EXTI_EXTICR3_EXTI9_0                (0x1UL << EXTI_EXTICR3_EXTI9_Pos)
#define EXTI_EXTICR3_EXTI9_1                (0x2UL << EXTI_EXTICR3_EXTI9_Pos)
#define EXTI_EXTICR3_EXTI9_2                (0x4UL << EXTI_EXTICR3_EXTI9_Pos)
#define EXTI_EXTICR3_EXTI9_3                (0x8UL << EXTI_EXTICR3_EXTI9_Pos)
#define EXTI_EXTICR3_EXTI10_Pos             (16UL)
#define EXTI_EXTICR3_EXTI10_Msk             (0xFUL << EXTI_EXTICR3_EXTI10_Pos)
#define EXTI_EXTICR3_EXTI10                 EXTI_EXTICR3_EXTI10_Msk
#define EXTI_EXTICR3_EXTI10_0               (0x1UL << EXTI_EXTICR3_EXTI10_Pos)
#define EXTI_EXTICR3_EXTI10_1               (0x2UL << EXTI_EXTICR3_EXTI10_Pos)
#define EXTI_EXTICR3_EXTI10_2               (0x4UL << EXTI_EXTICR3_EXTI10_Pos)
#define EXTI_EXTICR3_EXTI10_3               (0x8UL << EXTI_EXTICR3_EXTI10_Pos)
#define EXTI_EXTICR3_EXTI11_Pos             (24UL)
#define EXTI_EXTICR3_EXTI11_Msk             (0xFUL << EXTI_EXTICR3_EXTI11_Pos)
#define EXTI_EXTICR3_EXTI11                 EXTI_EXTICR3_EXTI11_Msk
#define EXTI_EXTICR3_EXTI11_0               (0x1UL << EXTI_EXTICR3_EXTI11_Pos)
#define EXTI_EXTICR3_EXTI11_1               (0x2UL << EXTI_EXTICR3_EXTI11_Pos)
#define EXTI_EXTICR3_EXTI11_2               (0x4UL << EXTI_EXTICR3_EXTI11_Pos)
#define EXTI_EXTICR3_EXTI11_3               (0x8UL << EXTI_EXTICR3_EXTI11_Pos)
#define EXTI_EXTICR4_EXTI12_Pos             (0UL)
#define EXTI_EXTICR4_EXTI12_Msk             (0xFUL << EXTI_EXTICR4_EXTI12_Pos)
#define EXTI_EXTICR4_EXTI12                 EXTI_EXTICR4_EXTI12_Msk
#define EXTI_EXTICR4_EXTI12_0               (0x1UL << EXTI_EXTICR4_EXTI12_Pos)
#define EXTI_EXTICR4_EXTI12_1               (0x2UL << EXTI_EXTICR4_EXTI12_Pos)
#define EXTI_EXTICR4_EXTI12_2               (0x4UL << EXTI_EXTICR4_EXTI12_Pos)
#define EXTI_EXTICR4_EXTI12_3               (0x8UL << EXTI_EXTICR4_EXTI12_Pos)
#define EXTI_EXTICR4_EXTI13_Pos             (8UL)
#define EXTI_EXTICR4_EXTI13_Msk             (0xFUL << EXTI_EXTICR4_EXTI13_Pos)
#define EXTI_EXTICR4_EXTI13                 EXTI_EXTICR4_EXTI13_Msk
#define EXTI_EXTICR4_EXTI13_0               (0x1UL << EXTI_EXTICR4_EXTI13_Pos)
#define EXTI_EXTICR4_EXTI13_1               (0x2UL << EXTI_EXTICR4_EXTI13_Pos)
#define EXTI_EXTICR4_EXTI13_2               (0x4UL << EXTI_EXTICR4_EXTI13_Pos)
#define EXTI_EXTICR4_EXTI13_3               (0x8UL << EXTI_EXTICR4_EXTI13_Pos)
#define EXTI_EXTICR4_EXTI14_Pos             (16UL)
#define EXTI_EXTICR4_EXTI14_Msk             (0xFUL << EXTI_EXTICR4_EXTI14_Pos)
#define EXTI_EXTICR4_EXTI14                 EXTI_EXTICR4_EXTI14_Msk
#define EXTI_EXTICR4_EXTI14_0               (0x1UL << EXTI_EXTICR4_EXTI14_Pos)
#define EXTI_EXTICR4_EXTI14_1               (0x2UL << EXTI_EXTICR4_EXTI14_Pos)
#define EXTI_EXTICR4_EXTI14_2               (0x4UL << EXTI_EXTICR4_EXTI14_Pos)
#define EXTI_EXTICR4_EXTI14_3               (0x8UL << EXTI_EXTICR4_EXTI14_Pos)
#define EXTI_EXTICR4_EXTI15_Pos             (24UL)
#define EXTI_EXTICR4_EXTI15_Msk             (0xFUL << EXTI_EXTICR4_EXTI15_Pos)
#define EXTI_EXTICR4_EXTI15                 EXTI_EXTICR4_EXTI15_Msk
#define EXTI_EXTICR4_EXTI15_0               (0x1UL << EXTI_EXTICR4_EXTI15_Pos)
#define EXTI_EXTICR4_EXTI15_1               (0x2UL << EXTI_EXTICR4_EXTI15_Pos)
#define EXTI_EXTICR4_EXTI15_2               (0x4UL << EXTI_EXTICR4_EXTI15_Pos)
#define EXTI_EXTICR4_EXTI15_3               (0x8UL << EXTI_EXTICR4_EXTI15_Pos)
#define EXTI_LOCKR_LOCK_Pos                 (0UL)
#define EXTI_LOCKR_LOCK_Msk                 (0x1UL << EXTI_LOCKR_LOCK_Pos)
#define EXTI_LOCKR_LOCK                     EXTI_LOCKR_LOCK_Msk
#define EXTI_IMR1_IM0_Pos                   (0UL)
#define EXTI_IMR1_IM0_Msk                   (0x1UL << EXTI_IMR1_IM0_Pos)
#define EXTI_IMR1_IM0                       EXTI_IMR1_IM0_Msk
#define EXTI_IMR1_IM1_Pos                   (1UL)
#define EXTI_IMR1_IM1_Msk                   (0x1UL << EXTI_IMR1_IM1_Pos)
#define EXTI_IMR1_IM1                       EXTI_IMR1_IM1_Msk
#define EXTI_IMR1_IM2_Pos                   (2UL)
#define EXTI_IMR1_IM2_Msk                   (0x1UL << EXTI_IMR1_IM2_Pos)
#define EXTI_IMR1_IM2                       EXTI_IMR1_IM2_Msk
#define EXTI_IMR1_IM3_Pos                   (3UL)
#define EXTI_IMR1_IM3_Msk                   (0x1UL << EXTI_IMR1_IM3_Pos)
#define EXTI_IMR1_IM3                       EXTI_IMR1_IM3_Msk
#define EXTI_IMR1_IM4_Pos                   (4UL)
#define EXTI_IMR1_IM4_Msk                   (0x1UL << EXTI_IMR1_IM4_Pos)
#define EXTI_IMR1_IM4                       EXTI_IMR1_IM4_Msk
#define EXTI_IMR1_IM5_Pos                   (5UL)
#define EXTI_IMR1_IM5_Msk                   (0x1UL << EXTI_IMR1_IM5_Pos)
#define EXTI_IMR1_IM5                       EXTI_IMR1_IM5_Msk
#define EXTI_IMR1_IM6_Pos                   (6UL)
#define EXTI_IMR1_IM6_Msk                   (0x1UL << EXTI_IMR1_IM6_Pos)
#define EXTI_IMR1_IM6                       EXTI_IMR1_IM6_Msk
#define EXTI_IMR1_IM7_Pos                   (7UL)
#define EXTI_IMR1_IM7_Msk                   (0x1UL << EXTI_IMR1_IM7_Pos)
#define EXTI_IMR1_IM7                       EXTI_IMR1_IM7_Msk
#define EXTI_IMR1_IM8_Pos                   (8UL)
#define EXTI_IMR1_IM8_Msk                   (0x1UL << EXTI_IMR1_IM8_Pos)
#define EXTI_IMR1_IM8                       EXTI_IMR1_IM8_Msk
#define EXTI_IMR1_IM9_Pos                   (9UL)
#define EXTI_IMR1_IM9_Msk                   (0x1UL << EXTI_IMR1_IM9_Pos)
#define EXTI_IMR1_IM9                       EXTI_IMR1_IM9_Msk
#define EXTI_IMR1_IM10_Pos                  (10UL)
#define EXTI_IMR1_IM10_Msk                  (0x1UL << EXTI_IMR1_IM10_Pos)
#define EXTI_IMR1_IM10                      EXTI_IMR1_IM10_Msk
#define EXTI_IMR1_IM11_Pos                  (11UL)
#define EXTI_IMR1_IM11_Msk                  (0x1UL << EXTI_IMR1_IM11_Pos)
#define EXTI_IMR1_IM11                      EXTI_IMR1_IM11_Msk
#define EXTI_IMR1_IM12_Pos                  (12UL)
#define EXTI_IMR1_IM12_Msk                  (0x1UL << EXTI_IMR1_IM12_Pos)
#define EXTI_IMR1_IM12                      EXTI_IMR1_IM12_Msk
#define EXTI_IMR1_IM13_Pos                  (13UL)
#define EXTI_IMR1_IM13_Msk                  (0x1UL << EXTI_IMR1_IM13_Pos)
#define EXTI_IMR1_IM13                      EXTI_IMR1_IM13_Msk
#define EXTI_IMR1_IM14_Pos                  (14UL)
#define EXTI_IMR1_IM14_Msk                  (0x1UL << EXTI_IMR1_IM14_Pos)
#define EXTI_IMR1_IM14                      EXTI_IMR1_IM14_Msk
#define EXTI_IMR1_IM15_Pos                  (15UL)
#define EXTI_IMR1_IM15_Msk                  (0x1UL << EXTI_IMR1_IM15_Pos)
#define EXTI_IMR1_IM15                      EXTI_IMR1_IM15_Msk
#define EXTI_IMR1_IM16_Pos                  (16UL)
#define EXTI_IMR1_IM16_Msk                  (0x1UL << EXTI_IMR1_IM16_Pos)
#define EXTI_IMR1_IM16                      EXTI_IMR1_IM16_Msk
#define EXTI_IMR1_IM17_Pos                  (17UL)
#define EXTI_IMR1_IM17_Msk                  (0x1UL << EXTI_IMR1_IM17_Pos)
#define EXTI_IMR1_IM17                      EXTI_IMR1_IM17_Msk
#define EXTI_IMR1_IM18_Pos                  (18UL)
#define EXTI_IMR1_IM18_Msk                  (0x1UL << EXTI_IMR1_IM18_Pos)
#define EXTI_IMR1_IM18                      EXTI_IMR1_IM18_Msk
#define EXTI_IMR1_IM19_Pos                  (19UL)
#define EXTI_IMR1_IM19_Msk                  (0x1UL << EXTI_IMR1_IM19_Pos)
#define EXTI_IMR1_IM19                      EXTI_IMR1_IM19_Msk
#define EXTI_IMR1_IM20_Pos                  (20UL)
#define EXTI_IMR1_IM20_Msk                  (0x1UL << EXTI_IMR1_IM20_Pos)
#define EXTI_IMR1_IM20                      EXTI_IMR1_IM20_Msk
#define EXTI_IMR1_IM21_Pos                  (21UL)
#define EXTI_IMR1_IM21_Msk                  (0x1UL << EXTI_IMR1_IM21_Pos)
#define EXTI_IMR1_IM21                      EXTI_IMR1_IM21_Msk
#define EXTI_IMR1_IM22_Pos                  (22UL)
#define EXTI_IMR1_IM22_Msk                  (0x1UL << EXTI_IMR1_IM22_Pos)
#define EXTI_IMR1_IM22                      EXTI_IMR1_IM22_Msk
#define EXTI_IMR1_IM23_Pos                  (23UL)
#define EXTI_IMR1_IM23_Msk                  (0x1UL << EXTI_IMR1_IM23_Pos)
#define EXTI_IMR1_IM23                      EXTI_IMR1_IM23_Msk
#define EXTI_EMR1_EM0_Pos                   (0UL)
#define EXTI_EMR1_EM0_Msk                   (0x1UL << EXTI_EMR1_EM0_Pos)
#define EXTI_EMR1_EM0                       EXTI_EMR1_EM0_Msk
#define EXTI_EMR1_EM1_Pos                   (1UL)
#define EXTI_EMR1_EM1_Msk                   (0x1UL << EXTI_EMR1_EM1_Pos)
#define EXTI_EMR1_EM1                       EXTI_EMR1_EM1_Msk
#define EXTI_EMR1_EM2_Pos                   (2UL)
#define EXTI_EMR1_EM2_Msk                   (0x1UL << EXTI_EMR1_EM2_Pos)
#define EXTI_EMR1_EM2                       EXTI_EMR1_EM2_Msk
#define EXTI_EMR1_EM3_Pos                   (3UL)
#define EXTI_EMR1_EM3_Msk                   (0x1UL << EXTI_EMR1_EM3_Pos)
#define EXTI_EMR1_EM3                       EXTI_EMR1_EM3_Msk
#define EXTI_EMR1_EM4_Pos                   (4UL)
#define EXTI_EMR1_EM4_Msk                   (0x1UL << EXTI_EMR1_EM4_Pos)
#define EXTI_EMR1_EM4                       EXTI_EMR1_EM4_Msk
#define EXTI_EMR1_EM5_Pos                   (5UL)
#define EXTI_EMR1_EM5_Msk                   (0x1UL << EXTI_EMR1_EM5_Pos)
#define EXTI_EMR1_EM5                       EXTI_EMR1_EM5_Msk
#define EXTI_EMR1_EM6_Pos                   (6UL)
#define EXTI_EMR1_EM6_Msk                   (0x1UL << EXTI_EMR1_EM6_Pos)
#define EXTI_EMR1_EM6                       EXTI_EMR1_EM6_Msk
#define EXTI_EMR1_EM7_Pos                   (7UL)
#define EXTI_EMR1_EM7_Msk                   (0x1UL << EXTI_EMR1_EM7_Pos)
#define EXTI_EMR1_EM7                       EXTI_EMR1_EM7_Msk
#define EXTI_EMR1_EM8_Pos                   (8UL)
#define EXTI_EMR1_EM8_Msk                   (0x1UL << EXTI_EMR1_EM8_Pos)
#define EXTI_EMR1_EM8                       EXTI_EMR1_EM8_Msk
#define EXTI_EMR1_EM9_Pos                   (9UL)
#define EXTI_EMR1_EM9_Msk                   (0x1UL << EXTI_EMR1_EM9_Pos)
#define EXTI_EMR1_EM9                       EXTI_EMR1_EM9_Msk
#define EXTI_EMR1_EM10_Pos                  (10UL)
#define EXTI_EMR1_EM10_Msk                  (0x1UL << EXTI_EMR1_EM10_Pos)
#define EXTI_EMR1_EM10                      EXTI_EMR1_EM10_Msk
#define EXTI_EMR1_EM11_Pos                  (11UL)
#define EXTI_EMR1_EM11_Msk                  (0x1UL << EXTI_EMR1_EM11_Pos)
#define EXTI_EMR1_EM11                      EXTI_EMR1_EM11_Msk
#define EXTI_EMR1_EM12_Pos                  (12UL)
#define EXTI_EMR1_EM12_Msk                  (0x1UL << EXTI_EMR1_EM12_Pos)
#define EXTI_EMR1_EM12                      EXTI_EMR1_EM12_Msk
#define EXTI_EMR1_EM13_Pos                  (13UL)
#define EXTI_EMR1_EM13_Msk                  (0x1UL << EXTI_EMR1_EM13_Pos)
#define EXTI_EMR1_EM13                      EXTI_EMR1_EM13_Msk
#define EXTI_EMR1_EM14_Pos                  (14UL)
#define EXTI_EMR1_EM14_Msk                  (0x1UL << EXTI_EMR1_EM14_Pos)
#define EXTI_EMR1_EM14                      EXTI_EMR1_EM14_Msk
#define EXTI_EMR1_EM15_Pos                  (15UL)
#define EXTI_EMR1_EM15_Msk                  (0x1UL << EXTI_EMR1_EM15_Pos)
#define EXTI_EMR1_EM15                      EXTI_EMR1_EM15_Msk
#define EXTI_EMR1_EM16_Pos                  (16UL)
#define EXTI_EMR1_EM16_Msk                  (0x1UL << EXTI_EMR1_EM16_Pos)
#define EXTI_EMR1_EM16                      EXTI_EMR1_EM16_Msk
#define EXTI_EMR1_EM17_Pos                  (17UL)
#define EXTI_EMR1_EM17_Msk                  (0x1UL << EXTI_EMR1_EM17_Pos)
#define EXTI_EMR1_EM17                      EXTI_EMR1_EM17_Msk
#define EXTI_EMR1_EM18_Pos                  (18UL)
#define EXTI_EMR1_EM18_Msk                  (0x1UL << EXTI_EMR1_EM18_Pos)
#define EXTI_EMR1_EM18                      EXTI_EMR1_EM18_Msk
#define EXTI_EMR1_EM19_Pos                  (19UL)
#define EXTI_EMR1_EM19_Msk                  (0x1UL << EXTI_EMR1_EM19_Pos)
#define EXTI_EMR1_EM19                      EXTI_EMR1_EM19_Msk
#define EXTI_EMR1_EM20_Pos                  (20UL)
#define EXTI_EMR1_EM20_Msk                  (0x1UL << EXTI_EMR1_EM20_Pos)
#define EXTI_EMR1_EM20                      EXTI_EMR1_EM20_Msk
#define EXTI_EMR1_EM21_Pos                  (21UL)
#define EXTI_EMR1_EM21_Msk                  (0x1UL << EXTI_EMR1_EM21_Pos)
#define EXTI_EMR1_EM21                      EXTI_EMR1_EM21_Msk
#define EXTI_EMR1_EM22_Pos                  (22UL)
#define EXTI_EMR1_EM22_Msk                  (0x1UL << EXTI_EMR1_EM22_Pos)
#define EXTI_EMR1_EM22                      EXTI_EMR1_EM22_Msk
#define EXTI_EMR1_EM23_Pos                  (23UL)
#define EXTI_EMR1_EM23_Msk                  (0x1UL << EXTI_EMR1_EM23_Pos)
#define EXTI_EMR1_EM23                      EXTI_EMR1_EM23_Msk
#define GPIO_MODER_MODE0_Pos                (0UL)
#define GPIO_MODER_MODE0_Msk                (0x3UL << GPIO_MODER_MODE0_Pos)
#define GPIO_MODER_MODE0                    GPIO_MODER_MODE0_Msk
#define GPIO_MODER_MODE0_0                  (0x1UL << GPIO_MODER_MODE0_Pos)
#define GPIO_MODER_MODE0_1                  (0x2UL << GPIO_MODER_MODE0_Pos)
#define GPIO_MODER_MODE1_Pos                (2UL)
#define GPIO_MODER_MODE1_Msk                (0x3UL << GPIO_MODER_MODE1_Pos)
#define GPIO_MODER_MODE1                    GPIO_MODER_MODE1_Msk
#define GPIO_MODER_MODE1_0                  (0x1UL << GPIO_MODER_MODE1_Pos)
#define GPIO_MODER_MODE1_1                  (0x2UL << GPIO_MODER_MODE1_Pos)
#define GPIO_MODER_MODE2_Pos                (4UL)
#define GPIO_MODER_MODE2_Msk                (0x3UL << GPIO_MODER_MODE2_Pos)
#define GPIO_MODER_MODE2                    GPIO_MODER_MODE2_Msk
#define GPIO_MODER_MODE2_0                  (0x1UL << GPIO_MODER_MODE2_Pos)
#define GPIO_MODER_MODE2_1                  (0x2UL << GPIO_MODER_MODE2_Pos)
#define GPIO_MODER_MODE3_Pos                (6UL)
#define GPIO_MODER_MODE3_Msk                (0x3UL << GPIO_MODER_MODE3_Pos)
#define GPIO_MODER_MODE3                    GPIO_MODER_MODE3_Msk
#define GPIO_MODER_MODE3_0                  (0x1UL << GPIO_MODER_MODE3_Pos)
#define GPIO_MODER_MODE3_1                  (0x2UL << GPIO_MODER_MODE3_Pos)
#define GPIO_MODER_MODE4_Pos                (8UL)
#define GPIO_MODER_MODE4_Msk                (0x3UL << GPIO_MODER_MODE4_Pos)
#define GPIO_MODER_MODE4                    GPIO_MODER_MODE4_Msk
#define GPIO_MODER_MODE4_0                  (0x1UL << GPIO_MODER_MODE4_Pos)
#define GPIO_MODER_MODE4_1                  (0x2UL << GPIO_MODER_MODE4_Pos)
#define GPIO_MODER_MODE5_Pos                (10UL)
#define GPIO_MODER_MODE5_Msk                (0x3UL << GPIO_MODER_MODE5_Pos)
#define GPIO_MODER_MODE5                    GPIO_MODER_MODE5_Msk
#define GPIO_MODER_MODE5_0                  (0x1UL << GPIO_MODER_MODE5_Pos)
#define GPIO_MODER_MODE5_1                  (0x2UL << GPIO_MODER_MODE5_Pos)
#define GPIO_MODER_MODE6_Pos                (12UL)
#define GPIO_MODER_MODE6_Msk                (0x3UL << GPIO_MODER_MODE6_Pos)
#define GPIO_MODER_MODE6                    GPIO_MODER_MODE6_Msk
#define GPIO_MODER_MODE6_0                  (0x1UL << GPIO_MODER_MODE6_Pos)
#define GPIO_MODER_MODE6_1                  (0x2UL << GPIO_MODER_MODE6_Pos)
#define GPIO_MODER_MODE7_Pos                (14UL)
#define GPIO_MODER_MODE7_Msk                (0x3UL << GPIO_MODER_MODE7_Pos)
#define GPIO_MODER_MODE7                    GPIO_MODER_MODE7_Msk
#define GPIO_MODER_MODE7_0                  (0x1UL << GPIO_MODER_MODE7_Pos)
#define GPIO_MODER_MODE7_1                  (0x2UL << GPIO_MODER_MODE7_Pos)
#define GPIO_MODER_MODE8_Pos                (16UL)
#define GPIO_MODER_MODE8_Msk                (0x3UL << GPIO_MODER_MODE8_Pos)
#define GPIO_MODER_MODE8                    GPIO_MODER_MODE8_Msk
#define GPIO_MODER_MODE8_0                  (0x1UL << GPIO_MODER_MODE8_Pos)
#define GPIO_MODER_MODE8_1                  (0x2UL << GPIO_MODER_MODE8_Pos)
#define GPIO_MODER_MODE9_Pos                (18UL)
#define GPIO_MODER_MODE9_Msk                (0x3UL << GPIO_MODER_MODE9_Pos)
#define GPIO_MODER_MODE9                    GPIO_MODER_MODE9_Msk
#define GPIO_MODER_MODE9_0                  (0x1UL << GPIO_MODER_MODE9_Pos)
#define GPIO_MODER_MODE9_1                  (0x2UL << GPIO_MODER_MODE9_Pos)
#define GPIO_MODER_MODE10_Pos               (20UL)
#define GPIO_MODER_MODE10_Msk               (0x3UL << GPIO_MODER_MODE10_Pos)
#define GPIO_MODER_MODE10                   GPIO_MODER_MODE10_Msk
#define GPIO_MODER_MODE10_0                 (0x1UL << GPIO_MODER_MODE10_Pos)
#define GPIO_MODER_MODE10_1                 (0x2UL << GPIO_MODER_MODE10_Pos)
#define GPIO_MODER_MODE11_Pos               (22UL)
#define GPIO_MODER_MODE11_Msk               (0x3UL << GPIO_MODER_MODE11_Pos)
#define GPIO_MODER_MODE11                   GPIO_MODER_MODE11_Msk
#define GPIO_MODER_MODE11_0                 (0x1UL << GPIO_MODER_MODE11_Pos)
#define GPIO_MODER_MODE11_1                 (0x2UL << GPIO_MODER_MODE11_Pos)
#define GPIO_MODER_MODE12_Pos               (24UL)
#define GPIO_MODER_MODE12_Msk               (0x3UL << GPIO_MODER_MODE12_Pos)
#define GPIO_MODER_MODE12                   GPIO_MODER_MODE12_Msk
#define GPIO_MODER_MODE12_0                 (0x1UL << GPIO_MODER_MODE12_Pos)
#define GPIO_MODER_MODE12_1                 (0x2UL << GPIO_MODER_MODE12_Pos)
#define GPIO_MODER_MODE13_Pos               (26UL)
#define GPIO_MODER_MODE13_Msk               (0x3UL << GPIO_MODER_MODE13_Pos)
#define GPIO_MODER_MODE13                   GPIO_MODER_MODE13_Msk
#define GPIO_MODER_MODE13_0                 (0x1UL << GPIO_MODER_MODE13_Pos)
#define GPIO_MODER_MODE13_1                 (0x2UL << GPIO_MODER_MODE13_Pos)
#define GPIO_MODER_MODE14_Pos               (28UL)
#define GPIO_MODER_MODE14_Msk               (0x3UL << GPIO_MODER_MODE14_Pos)
#define GPIO_MODER_MODE14                   GPIO_MODER_MODE14_Msk
#define GPIO_MODER_MODE14_0                 (0x1UL << GPIO_MODER_MODE14_Pos)
#define GPIO_MODER_MODE14_1                 (0x2UL << GPIO_MODER_MODE14_Pos)
#define GPIO_MODER_MODE15_Pos               (30UL)
#define GPIO_MODER_MODE15_Msk               (0x3UL << GPIO_MODER_MODE15_Pos)
#define GPIO_MODER_MODE15                   GPIO_MODER_MODE15_Msk
#define GPIO_MODER_MODE15_0                 (0x1UL << GPIO_MODER_MODE15_Pos)
#define GPIO_MODER_MODE15_1                 (0x2UL << GPIO_MODER_MODE15_Pos)
#define GPIO_OTYPER_OT0_Pos                 (0UL)
#define GPIO_OTYPER_OT0_Msk                 (0x1UL << GPIO_OTYPER_OT0_Pos)
#define GPIO_OTYPER_OT0                     GPIO_OTYPER_OT0_Msk
#define GPIO_OTYPER_OT1_Pos                 (1UL)
#define GPIO_OTYPER_OT1_Msk                 (0x1UL << GPIO_OTYPER_OT1_Pos)
#define GPIO_OTYPER_OT1                     GPIO_OTYPER_OT1_Msk
#define GPIO_OTYPER_OT2_Pos                 (2UL)
#define GPIO_OTYPER_OT2_Msk                 (0x1UL << GPIO_OTYPER_OT2_Pos)
#define GPIO_OTYPER_OT2                     GPIO_OTYPER_OT2_Msk
#define GPIO_OTYPER_OT3_Pos                 (3UL)
#define GPIO_OTYPER_OT3_Msk                 (0x1UL << GPIO_OTYPER_OT3_Pos)
#define GPIO_OTYPER_OT3                     GPIO_OTYPER_OT3_Msk
#define GPIO_OTYPER_OT4_Pos                 (4UL)
#define GPIO_OTYPER_OT4_Msk                 (0x1UL << GPIO_OTYPER_OT4_Pos)
#define GPIO_OTYPER_OT4                     GPIO_OTYPER_OT4_Msk
#define GPIO_OTYPER_OT5_Pos                 (5UL)
#define GPIO_OTYPER_OT5_Msk                 (0x1UL << GPIO_OTYPER_OT5_Pos)
#define GPIO_OTYPER_OT5                     GPIO_OTYPER_OT5_Msk
#define GPIO_OTYPER_OT6_Pos                 (6UL)
#define GPIO_OTYPER_OT6_Msk                 (0x1UL << GPIO_OTYPER_OT6_Pos)
#define GPIO_OTYPER_OT6                     GPIO_OTYPER_OT6_Msk
#define GPIO_OTYPER_OT7_Pos                 (7UL)
#define GPIO_OTYPER_OT7_Msk                 (0x1UL << GPIO_OTYPER_OT7_Pos)
#define GPIO_OTYPER_OT7                     GPIO_OTYPER_OT7_Msk
#define GPIO_OTYPER_OT8_Pos                 (8UL)
#define GPIO_OTYPER_OT8_Msk                 (0x1UL << GPIO_OTYPER_OT8_Pos)
#define GPIO_OTYPER_OT8                     GPIO_OTYPER_OT8_Msk
#define GPIO_OTYPER_OT9_Pos                 (9UL)
#define GPIO_OTYPER_OT9_Msk                 (0x1UL << GPIO_OTYPER_OT9_Pos)
#define GPIO_OTYPER_OT9                     GPIO_OTYPER_OT9_Msk
#define GPIO_OTYPER_OT10_Pos                (10UL)
#define GPIO_OTYPER_OT10_Msk                (0x1UL << GPIO_OTYPER_OT10_Pos)
#define GPIO_OTYPER_OT10                    GPIO_OTYPER_OT10_Msk
#define GPIO_OTYPER_OT11_Pos                (11UL)
#define GPIO_OTYPER_OT11_Msk                (0x1UL << GPIO_OTYPER_OT11_Pos)
#define GPIO_OTYPER_OT11                    GPIO_OTYPER_OT11_Msk
#define GPIO_OTYPER_OT12_Pos                (12UL)
#define GPIO_OTYPER_OT12_Msk                (0x1UL << GPIO_OTYPER_OT12_Pos)
#define GPIO_OTYPER_OT12                    GPIO_OTYPER_OT12_Msk
#define GPIO_OTYPER_OT13_Pos                (13UL)
#define GPIO_OTYPER_OT13_Msk                (0x1UL << GPIO_OTYPER_OT13_Pos)
#define GPIO_OTYPER_OT13                    GPIO_OTYPER_OT13_Msk
#define GPIO_OTYPER_OT14_Pos                (14UL)
#define GPIO_OTYPER_OT14_Msk                (0x1UL << GPIO_OTYPER_OT14_Pos)
#define GPIO_OTYPER_OT14                    GPIO_OTYPER_OT14_Msk
#define GPIO_OTYPER_OT15_Pos                (15UL)
#define GPIO_OTYPER_OT15_Msk                (0x1UL << GPIO_OTYPER_OT15_Pos)
#define GPIO_OTYPER_OT15                    GPIO_OTYPER_OT15_Msk
#define GPIO_OSPEEDR_OSPEED0_Pos            (0UL)
#define GPIO_OSPEEDR_OSPEED0_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED0_Pos)
#define GPIO_OSPEEDR_OSPEED0                GPIO_OSPEEDR_OSPEED0_Msk
#define GPIO_OSPEEDR_OSPEED0_0              (0x1UL << GPIO_OSPEEDR_OSPEED0_Pos)
#define GPIO_OSPEEDR_OSPEED0_1              (0x2UL << GPIO_OSPEEDR_OSPEED0_Pos)
#define GPIO_OSPEEDR_OSPEED1_Pos            (2UL)
#define GPIO_OSPEEDR_OSPEED1_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED1_Pos)
#define GPIO_OSPEEDR_OSPEED1                GPIO_OSPEEDR_OSPEED1_Msk
#define GPIO_OSPEEDR_OSPEED1_0              (0x1UL << GPIO_OSPEEDR_OSPEED1_Pos)
#define GPIO_OSPEEDR_OSPEED1_1              (0x2UL << GPIO_OSPEEDR_OSPEED1_Pos)
#define GPIO_OSPEEDR_OSPEED2_Pos            (4UL)
#define GPIO_OSPEEDR_OSPEED2_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED2_Pos)
#define GPIO_OSPEEDR_OSPEED2                GPIO_OSPEEDR_OSPEED2_Msk
#define GPIO_OSPEEDR_OSPEED2_0              (0x1UL << GPIO_OSPEEDR_OSPEED2_Pos)
#define GPIO_OSPEEDR_OSPEED2_1              (0x2UL << GPIO_OSPEEDR_OSPEED2_Pos)
#define GPIO_OSPEEDR_OSPEED3_Pos            (6UL)
#define GPIO_OSPEEDR_OSPEED3_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED3_Pos)
#define GPIO_OSPEEDR_OSPEED3                GPIO_OSPEEDR_OSPEED3_Msk
#define GPIO_OSPEEDR_OSPEED3_0              (0x1UL << GPIO_OSPEEDR_OSPEED3_Pos)
#define GPIO_OSPEEDR_OSPEED3_1              (0x2UL << GPIO_OSPEEDR_OSPEED3_Pos)
#define GPIO_OSPEEDR_OSPEED4_Pos            (8UL)
#define GPIO_OSPEEDR_OSPEED4_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED4_Pos)
#define GPIO_OSPEEDR_OSPEED4                GPIO_OSPEEDR_OSPEED4_Msk
#define GPIO_OSPEEDR_OSPEED4_0              (0x1UL << GPIO_OSPEEDR_OSPEED4_Pos)
#define GPIO_OSPEEDR_OSPEED4_1              (0x2UL << GPIO_OSPEEDR_OSPEED4_Pos)
#define GPIO_OSPEEDR_OSPEED5_Pos            (10UL)
#define GPIO_OSPEEDR_OSPEED5_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED5_Pos)
#define GPIO_OSPEEDR_OSPEED5                GPIO_OSPEEDR_OSPEED5_Msk
#define GPIO_OSPEEDR_OSPEED5_0              (0x1UL << GPIO_OSPEEDR_OSPEED5_Pos)
#define GPIO_OSPEEDR_OSPEED5_1              (0x2UL << GPIO_OSPEEDR_OSPEED5_Pos)
#define GPIO_OSPEEDR_OSPEED6_Pos            (12UL)
#define GPIO_OSPEEDR_OSPEED6_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED6_Pos)
#define GPIO_OSPEEDR_OSPEED6                GPIO_OSPEEDR_OSPEED6_Msk
#define GPIO_OSPEEDR_OSPEED6_0              (0x1UL << GPIO_OSPEEDR_OSPEED6_Pos)
#define GPIO_OSPEEDR_OSPEED6_1              (0x2UL << GPIO_OSPEEDR_OSPEED6_Pos)
#define GPIO_OSPEEDR_OSPEED7_Pos            (14UL)
#define GPIO_OSPEEDR_OSPEED7_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED7_Pos)
#define GPIO_OSPEEDR_OSPEED7                GPIO_OSPEEDR_OSPEED7_Msk
#define GPIO_OSPEEDR_OSPEED7_0              (0x1UL << GPIO_OSPEEDR_OSPEED7_Pos)
#define GPIO_OSPEEDR_OSPEED7_1              (0x2UL << GPIO_OSPEEDR_OSPEED7_Pos)
#define GPIO_OSPEEDR_OSPEED8_Pos            (16UL)
#define GPIO_OSPEEDR_OSPEED8_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED8_Pos)
#define GPIO_OSPEEDR_OSPEED8                GPIO_OSPEEDR_OSPEED8_Msk
#define GPIO_OSPEEDR_OSPEED8_0              (0x1UL << GPIO_OSPEEDR_OSPEED8_Pos)
#define GPIO_OSPEEDR_OSPEED8_1              (0x2UL << GPIO_OSPEEDR_OSPEED8_Pos)
#define GPIO_OSPEEDR_OSPEED9_Pos            (18UL)
#define GPIO_OSPEEDR_OSPEED9_Msk            (0x3UL << GPIO_OSPEEDR_OSPEED9_Pos)
#define GPIO_OSPEEDR_OSPEED9                GPIO_OSPEEDR_OSPEED9_Msk
#define GPIO_OSPEEDR_OSPEED9_0              (0x1UL << GPIO_OSPEEDR_OSPEED9_Pos)
#define GPIO_OSPEEDR_OSPEED9_1              (0x2UL << GPIO_OSPEEDR_OSPEED9_Pos)
#define GPIO_OSPEEDR_OSPEED10_Pos           (20UL)
#define GPIO_OSPEEDR_OSPEED10_Msk           (0x3UL << GPIO_OSPEEDR_OSPEED10_Pos)
#define GPIO_OSPEEDR_OSPEED10               GPIO_OSPEEDR_OSPEED10_Msk
#define GPIO_OSPEEDR_OSPEED10_0             (0x1UL << GPIO_OSPEEDR_OSPEED10_Pos)
#define GPIO_OSPEEDR_OSPEED10_1             (0x2UL << GPIO_OSPEEDR_OSPEED10_Pos)
#define GPIO_OSPEEDR_OSPEED11_Pos           (22UL)
#define GPIO_OSPEEDR_OSPEED11_Msk           (0x3UL << GPIO_OSPEEDR_OSPEED11_Pos)
#define GPIO_OSPEEDR_OSPEED11               GPIO_OSPEEDR_OSPEED11_Msk
#define GPIO_OSPEEDR_OSPEED11_0             (0x1UL << GPIO_OSPEEDR_OSPEED11_Pos)
#define GPIO_OSPEEDR_OSPEED11_1             (0x2UL << GPIO_OSPEEDR_OSPEED11_Pos)
#define GPIO_OSPEEDR_OSPEED12_Pos           (24UL)
#define GPIO_OSPEEDR_OSPEED12_Msk           (0x3UL << GPIO_OSPEEDR_OSPEED12_Pos)
#define GPIO_OSPEEDR_OSPEED12               GPIO_OSPEEDR_OSPEED12_Msk
#define GPIO_OSPEEDR_OSPEED12_0             (0x1UL << GPIO_OSPEEDR_OSPEED12_Pos)
#define GPIO_OSPEEDR_OSPEED12_1             (0x2UL << GPIO_OSPEEDR_OSPEED12_Pos)
#define GPIO_OSPEEDR_OSPEED13_Pos           (26UL)
#define GPIO_OSPEEDR_OSPEED13_Msk           (0x3UL << GPIO_OSPEEDR_OSPEED13_Pos)
#define GPIO_OSPEEDR_OSPEED13               GPIO_OSPEEDR_OSPEED13_Msk
#define GPIO_OSPEEDR_OSPEED13_0             (0x1UL << GPIO_OSPEEDR_OSPEED13_Pos)
#define GPIO_OSPEEDR_OSPEED13_1             (0x2UL << GPIO_OSPEEDR_OSPEED13_Pos)
#define GPIO_OSPEEDR_OSPEED14_Pos           (28UL)
#define GPIO_OSPEEDR_OSPEED14_Msk           (0x3UL << GPIO_OSPEEDR_OSPEED14_Pos)
#define GPIO_OSPEEDR_OSPEED14               GPIO_OSPEEDR_OSPEED14_Msk
#define GPIO_OSPEEDR_OSPEED14_0             (0x1UL << GPIO_OSPEEDR_OSPEED14_Pos)
#define GPIO_OSPEEDR_OSPEED14_1             (0x2UL << GPIO_OSPEEDR_OSPEED14_Pos)
#define GPIO_OSPEEDR_OSPEED15_Pos           (30UL)
#define GPIO_OSPEEDR_OSPEED15_Msk           (0x3UL << GPIO_OSPEEDR_OSPEED15_Pos)
#define GPIO_OSPEEDR_OSPEED15               GPIO_OSPEEDR_OSPEED15_Msk
#define GPIO_OSPEEDR_OSPEED15_0             (0x1UL << GPIO_OSPEEDR_OSPEED15_Pos)
#define GPIO_OSPEEDR_OSPEED15_1             (0x2UL << GPIO_OSPEEDR_OSPEED15_Pos)
#define GPIO_PUPDR_PUPD0_Pos                (0UL)
#define GPIO_PUPDR_PUPD0_Msk                (0x3UL << GPIO_PUPDR_PUPD0_Pos)
#define GPIO_PUPDR_PUPD0                    GPIO_PUPDR_PUPD0_Msk
#define GPIO_PUPDR_PUPD0_0                  (0x1UL << GPIO_PUPDR_PUPD0_Pos)
#define GPIO_PUPDR_PUPD0_1                  (0x2UL << GPIO_PUPDR_PUPD0_Pos)
#define GPIO_PUPDR_PUPD1_Pos                (2UL)
#define GPIO_PUPDR_PUPD1_Msk                (0x3UL << GPIO_PUPDR_PUPD1_Pos)
#define GPIO_PUPDR_PUPD1                    GPIO_PUPDR_PUPD1_Msk
#define GPIO_PUPDR_PUPD1_0                  (0x1UL << GPIO_PUPDR_PUPD1_Pos)
#define GPIO_PUPDR_PUPD1_1                  (0x2UL << GPIO_PUPDR_PUPD1_Pos)
#define GPIO_PUPDR_PUPD2_Pos                (4UL)
#define GPIO_PUPDR_PUPD2_Msk                (0x3UL << GPIO_PUPDR_PUPD2_Pos)
#define GPIO_PUPDR_PUPD2                    GPIO_PUPDR_PUPD2_Msk
#define GPIO_PUPDR_PUPD2_0                  (0x1UL << GPIO_PUPDR_PUPD2_Pos)
#define GPIO_PUPDR_PUPD2_1                  (0x2UL << GPIO_PUPDR_PUPD2_Pos)
#define GPIO_PUPDR_PUPD3_Pos                (6UL)
#define GPIO_PUPDR_PUPD3_Msk                (0x3UL << GPIO_PUPDR_PUPD3_Pos)
#define GPIO_PUPDR_PUPD3                    GPIO_PUPDR_PUPD3_Msk
#define GPIO_PUPDR_PUPD3_0                  (0x1UL << GPIO_PUPDR_PUPD3_Pos)
#define GPIO_PUPDR_PUPD3_1                  (0x2UL << GPIO_PUPDR_PUPD3_Pos)
#define GPIO_PUPDR_PUPD4_Pos                (8UL)
#define GPIO_PUPDR_PUPD4_Msk                (0x3UL << GPIO_PUPDR_PUPD4_Pos)
#define GPIO_PUPDR_PUPD4                    GPIO_PUPDR_PUPD4_Msk
#define GPIO_PUPDR_PUPD4_0                  (0x1UL << GPIO_PUPDR_PUPD4_Pos)
#define GPIO_PUPDR_PUPD4_1                  (0x2UL << GPIO_PUPDR_PUPD4_Pos)
#define GPIO_PUPDR_PUPD5_Pos                (10UL)
#define GPIO_PUPDR_PUPD5_Msk                (0x3UL << GPIO_PUPDR_PUPD5_Pos)
#define GPIO_PUPDR_PUPD5                    GPIO_PUPDR_PUPD5_Msk
#define GPIO_PUPDR_PUPD5_0                  (0x1UL << GPIO_PUPDR_PUPD5_Pos)
#define GPIO_PUPDR_PUPD5_1                  (0x2UL << GPIO_PUPDR_PUPD5_Pos)
#define GPIO_PUPDR_PUPD6_Pos                (12UL)
#define GPIO_PUPDR_PUPD6_Msk                (0x3UL << GPIO_PUPDR_PUPD6_Pos)
#define GPIO_PUPDR_PUPD6                    GPIO_PUPDR_PUPD6_Msk
#define GPIO_PUPDR_PUPD6_0                  (0x1UL << GPIO_PUPDR_PUPD6_Pos)
#define GPIO_PUPDR_PUPD6_1                  (0x2UL << GPIO_PUPDR_PUPD6_Pos)
#define GPIO_PUPDR_PUPD7_Pos                (14UL)
#define GPIO_PUPDR_PUPD7_Msk                (0x3UL << GPIO_PUPDR_PUPD7_Pos)
#define GPIO_PUPDR_PUPD7                    GPIO_PUPDR_PUPD7_Msk
#define GPIO_PUPDR_PUPD7_0                  (0x1UL << GPIO_PUPDR_PUPD7_Pos)
#define GPIO_PUPDR_PUPD7_1                  (0x2UL << GPIO_PUPDR_PUPD7_Pos)
#define GPIO_PUPDR_PUPD8_Pos                (16UL)
#define GPIO_PUPDR_PUPD8_Msk                (0x3UL << GPIO_PUPDR_PUPD8_Pos)
#define GPIO_PUPDR_PUPD8                    GPIO_PUPDR_PUPD8_Msk
#define GPIO_PUPDR_PUPD8_0                  (0x1UL << GPIO_PUPDR_PUPD8_Pos)
#define GPIO_PUPDR_PUPD8_1                  (0x2UL << GPIO_PUPDR_PUPD8_Pos)
#define GPIO_PUPDR_PUPD9_Pos                (18UL)
#define GPIO_PUPDR_PUPD9_Msk                (0x3UL << GPIO_PUPDR_PUPD9_Pos)
#define GPIO_PUPDR_PUPD9                    GPIO_PUPDR_PUPD9_Msk
#define GPIO_PUPDR_PUPD9_0                  (0x1UL << GPIO_PUPDR_PUPD9_Pos)
#define GPIO_PUPDR_PUPD9_1                  (0x2UL << GPIO_PUPDR_PUPD9_Pos)
#define GPIO_PUPDR_PUPD10_Pos               (20UL)
#define GPIO_PUPDR_PUPD10_Msk               (0x3UL << GPIO_PUPDR_PUPD10_Pos)
#define GPIO_PUPDR_PUPD10                   GPIO_PUPDR_PUPD10_Msk
#define GPIO_PUPDR_PUPD10_0                 (0x1UL << GPIO_PUPDR_PUPD10_Pos)
#define GPIO_PUPDR_PUPD10_1                 (0x2UL << GPIO_PUPDR_PUPD10_Pos)
#define GPIO_PUPDR_PUPD11_Pos               (22UL)
#define GPIO_PUPDR_PUPD11_Msk               (0x3UL << GPIO_PUPDR_PUPD11_Pos)
#define GPIO_PUPDR_PUPD11                   GPIO_PUPDR_PUPD11_Msk
#define GPIO_PUPDR_PUPD11_0                 (0x1UL << GPIO_PUPDR_PUPD11_Pos)
#define GPIO_PUPDR_PUPD11_1                 (0x2UL << GPIO_PUPDR_PUPD11_Pos)
#define GPIO_PUPDR_PUPD12_Pos               (24UL)
#define GPIO_PUPDR_PUPD12_Msk               (0x3UL << GPIO_PUPDR_PUPD12_Pos)
#define GPIO_PUPDR_PUPD12                   GPIO_PUPDR_PUPD12_Msk
#define GPIO_PUPDR_PUPD12_0                 (0x1UL << GPIO_PUPDR_PUPD12_Pos)
#define GPIO_PUPDR_PUPD12_1                 (0x2UL << GPIO_PUPDR_PUPD12_Pos)
#define GPIO_PUPDR_PUPD13_Pos               (26UL)
#define GPIO_PUPDR_PUPD13_Msk               (0x3UL << GPIO_PUPDR_PUPD13_Pos)
#define GPIO_PUPDR_PUPD13                   GPIO_PUPDR_PUPD13_Msk
#define GPIO_PUPDR_PUPD13_0                 (0x1UL << GPIO_PUPDR_PUPD13_Pos)
#define GPIO_PUPDR_PUPD13_1                 (0x2UL << GPIO_PUPDR_PUPD13_Pos)
#define GPIO_PUPDR_PUPD14_Pos               (28UL)
#define GPIO_PUPDR_PUPD14_Msk               (0x3UL << GPIO_PUPDR_PUPD14_Pos)
#define GPIO_PUPDR_PUPD14                   GPIO_PUPDR_PUPD14_Msk
#define GPIO_PUPDR_PUPD14_0                 (0x1UL << GPIO_PUPDR_PUPD14_Pos)
#define GPIO_PUPDR_PUPD14_1                 (0x2UL << GPIO_PUPDR_PUPD14_Pos)
#define GPIO_PUPDR_PUPD15_Pos               (30UL)
#define GPIO_PUPDR_PUPD15_Msk               (0x3UL << GPIO_PUPDR_PUPD15_Pos)
#define GPIO_PUPDR_PUPD15                   GPIO_PUPDR_PUPD15_Msk
#define GPIO_PUPDR_PUPD15_0                 (0x1UL << GPIO_PUPDR_PUPD15_Pos)
#define GPIO_PUPDR_PUPD15_1                 (0x2UL << GPIO_PUPDR_PUPD15_Pos)
#define GPIO_IDR_ID0_Pos                    (0UL)
#define GPIO_IDR_ID0_Msk                    (0x1UL << GPIO_IDR_ID0_Pos)
#define GPIO_IDR_ID0                        GPIO_IDR_ID0_Msk
#define GPIO_IDR_ID1_Pos                    (1UL)
#define GPIO_IDR_ID1_Msk                    (0x1UL << GPIO_IDR_ID1_Pos)
#define GPIO_IDR_ID1                        GPIO_IDR_ID1_Msk
#define GPIO_IDR_ID2_Pos                    (2UL)
#define GPIO_IDR_ID2_Msk                    (0x1UL << GPIO_IDR_ID2_Pos)
#define GPIO_IDR_ID2                        GPIO_IDR_ID2_Msk
#define GPIO_IDR_ID3_Pos                    (3UL)
#define GPIO_IDR_ID3_Msk                    (0x1UL << GPIO_IDR_ID3_Pos)
#define GPIO_IDR_ID3                        GPIO_IDR_ID3_Msk
#define GPIO_IDR_ID4_Pos                    (4UL)
#define GPIO_IDR_ID4_Msk                    (0x1UL << GPIO_IDR_ID4_Pos)
#define GPIO_IDR_ID4                        GPIO_IDR_ID4_Msk
#define GPIO_IDR_ID5_Pos                    (5UL)
#define GPIO_IDR_ID5_Msk                    (0x1UL << GPIO_IDR_ID5_Pos)
#define GPIO_IDR_ID5                        GPIO_IDR_ID5_Msk
#define GPIO_IDR_ID6_Pos                    (6UL)
#define GPIO_IDR_ID6_Msk                    (0x1UL << GPIO_IDR_ID6_Pos)
#define GPIO_IDR_ID6                        GPIO_IDR_ID6_Msk
#define GPIO_IDR_ID7_Pos                    (7UL)
#define GPIO_IDR_ID7_Msk                    (0x1UL << GPIO_IDR_ID7_Pos)
#define GPIO_IDR_ID7                        GPIO_IDR_ID7_Msk
#define GPIO_IDR_ID8_Pos                    (8UL)
#define GPIO_IDR_ID8_Msk                    (0x1UL << GPIO_IDR_ID8_Pos)
#define GPIO_IDR_ID8                        GPIO_IDR_ID8_Msk
#define GPIO_IDR_ID9_Pos                    (9UL)
#define GPIO_IDR_ID9_Msk                    (0x1UL << GPIO_IDR_ID9_Pos)
#define GPIO_IDR_ID9                        GPIO_IDR_ID9_Msk
#define GPIO_IDR_ID10_Pos                   (10UL)
#define GPIO_IDR_ID10_Msk                   (0x1UL << GPIO_IDR_ID10_Pos)
#define GPIO_IDR_ID10                       GPIO_IDR_ID10_Msk
#define GPIO_IDR_ID11_Pos                   (11UL)
#define GPIO_IDR_ID11_Msk                   (0x1UL << GPIO_IDR_ID11_Pos)
#define GPIO_IDR_ID11                       GPIO_IDR_ID11_Msk
#define GPIO_IDR_ID12_Pos                   (12UL)
#define GPIO_IDR_ID12_Msk                   (0x1UL << GPIO_IDR_ID12_Pos)
#define GPIO_IDR_ID12                       GPIO_IDR_ID12_Msk
#define GPIO_IDR_ID13_Pos                   (13UL)
#define GPIO_IDR_ID13_Msk                   (0x1UL << GPIO_IDR_ID13_Pos)
#define GPIO_IDR_ID13                       GPIO_IDR_ID13_Msk
#define GPIO_IDR_ID14_Pos                   (14UL)
#define GPIO_IDR_ID14_Msk                   (0x1UL << GPIO_IDR_ID14_Pos)
#define GPIO_IDR_ID14                       GPIO_IDR_ID14_Msk
#define GPIO_IDR_ID15_Pos                   (15UL)
#define GPIO_IDR_ID15_Msk                   (0x1UL << GPIO_IDR_ID15_Pos)
#define GPIO_IDR_ID15                       GPIO_IDR_ID15_Msk
#define GPIO_ODR_OD0_Pos                    (0UL)
#define GPIO_ODR_OD0_Msk                    (0x1UL << GPIO_ODR_OD0_Pos)
#define GPIO_ODR_OD0                        GPIO_ODR_OD0_Msk
#define GPIO_ODR_OD1_Pos                    (1UL)
#define GPIO_ODR_OD1_Msk                    (0x1UL << GPIO_ODR_OD1_Pos)
#define GPIO_ODR_OD1                        GPIO_ODR_OD1_Msk
#define GPIO_ODR_OD2_Pos                    (2UL)
#define GPIO_ODR_OD2_Msk                    (0x1UL << GPIO_ODR_OD2_Pos)
#define GPIO_ODR_OD2                        GPIO_ODR_OD2_Msk
#define GPIO_ODR_OD3_Pos                    (3UL)
#define GPIO_ODR_OD3_Msk                    (0x1UL << GPIO_ODR_OD3_Pos)
#define GPIO_ODR_OD3                        GPIO_ODR_OD3_Msk
#define GPIO_ODR_OD4_Pos                    (4UL)
#define GPIO_ODR_OD4_Msk                    (0x1UL << GPIO_ODR_OD4_Pos)
#define GPIO_ODR_OD4                        GPIO_ODR_OD4_Msk
#define GPIO_ODR_OD5_Pos                    (5UL)
#define GPIO_ODR_OD5_Msk                    (0x1UL << GPIO_ODR_OD5_Pos)
#define GPIO_ODR_OD5                        GPIO_ODR_OD5_Msk
#define GPIO_ODR_OD6_Pos                    (6UL)
#define GPIO_ODR_OD6_Msk                    (0x1UL << GPIO_ODR_OD6_Pos)
#define GPIO_ODR_OD6                        GPIO_ODR_OD6_Msk
#define GPIO_ODR_OD7_Pos                    (7UL)
#define GPIO_ODR_OD7_Msk                    (0x1UL << GPIO_ODR_OD7_Pos)
#define GPIO_ODR_OD7                        GPIO_ODR_OD7_Msk
#define GPIO_ODR_OD8_Pos                    (8UL)
#define GPIO_ODR_OD8_Msk                    (0x1UL << GPIO_ODR_OD8_Pos)
#define GPIO_ODR_OD8                        GPIO_ODR_OD8_Msk
#define GPIO_ODR_OD9_Pos                    (9UL)
#define GPIO_ODR_OD9_Msk                    (0x1UL << GPIO_ODR_OD9_Pos)
#define GPIO_ODR_OD9                        GPIO_ODR_OD9_Msk
#define GPIO_ODR_OD10_Pos                   (10UL)
#define GPIO_ODR_OD10_Msk                   (0x1UL << GPIO_ODR_OD10_Pos)
#define GPIO_ODR_OD10                       GPIO_ODR_OD10_Msk
#define GPIO_ODR_OD11_Pos                   (11UL)
#define GPIO_ODR_OD11_Msk                   (0x1UL << GPIO_ODR_OD11_Pos)
#define GPIO_ODR_OD11                       GPIO_ODR_OD11_Msk
#define GPIO_ODR_OD12_Pos                   (12UL)
#define GPIO_ODR_OD12_Msk                   (0x1UL << GPIO_ODR_OD12_Pos)
#define GPIO_ODR_OD12                       GPIO_ODR_OD12_Msk
#define GPIO_ODR_OD13_Pos                   (13UL)
#define GPIO_ODR_OD13_Msk                   (0x1UL << GPIO_ODR_OD13_Pos)
#define GPIO_ODR_OD13                       GPIO_ODR_OD13_Msk
#define GPIO_ODR_OD14_Pos                   (14UL)
#define GPIO_ODR_OD14_Msk                   (0x1UL << GPIO_ODR_OD14_Pos)
#define GPIO_ODR_OD14                       GPIO_ODR_OD14_Msk
#define GPIO_ODR_OD15_Pos                   (15UL)
#define GPIO_ODR_OD15_Msk                   (0x1UL << GPIO_ODR_OD15_Pos)
#define GPIO_ODR_OD15                       GPIO_ODR_OD15_Msk
#define GPIO_BSRR_BS0_Pos                   (0UL)
#define GPIO_BSRR_BS0_Msk                   (0x1UL << GPIO_BSRR_BS0_Pos)
#define GPIO_BSRR_BS0                       GPIO_BSRR_BS0_Msk
#define GPIO_BSRR_BS1_Pos                   (1UL)
#define GPIO_BSRR_BS1_Msk                   (0x1UL << GPIO_BSRR_BS1_Pos)
#define GPIO_BSRR_BS1                       GPIO_BSRR_BS1_Msk
#define GPIO_BSRR_BS2_Pos                   (2UL)
#define GPIO_BSRR_BS2_Msk                   (0x1UL << GPIO_BSRR_BS2_Pos)
#define GPIO_BSRR_BS2                       GPIO_BSRR_BS2_Msk
#define GPIO_BSRR_BS3_Pos                   (3UL)
#define GPIO_BSRR_BS3_Msk                   (0x1UL << GPIO_BSRR_BS3_Pos)
#define GPIO_BSRR_BS3                       GPIO_BSRR_BS3_Msk
#define GPIO_BSRR_BS4_Pos                   (4UL)
#define GPIO_BSRR_BS4_Msk                   (0x1UL << GPIO_BSRR_BS4_Pos)
#define GPIO_BSRR_BS4                       GPIO_BSRR_BS4_Msk
#define GPIO_BSRR_BS5_Pos                   (5UL)
#define GPIO_BSRR_BS5_Msk                   (0x1UL << GPIO_BSRR_BS5_Pos)
#define GPIO_BSRR_BS5                       GPIO_BSRR_BS5_Msk
#define GPIO_BSRR_BS6_Pos                   (6UL)
#define GPIO_BSRR_BS6_Msk                   (0x1UL << GPIO_BSRR_BS6_Pos)
#define GPIO_BSRR_BS6                       GPIO_BSRR_BS6_Msk
#define GPIO_BSRR_BS7_Pos                   (7UL)
#define GPIO_BSRR_BS7_Msk                   (0x1UL << GPIO_BSRR_BS7_Pos)
#define GPIO_BSRR_BS7                       GPIO_BSRR_BS7_Msk
#define GPIO_BSRR_BS8_Pos                   (8UL)
#define GPIO_BSRR_BS8_Msk                   (0x1UL << GPIO_BSRR_BS8_Pos)
#define GPIO_BSRR_BS8                       GPIO_BSRR_BS8_Msk
#define GPIO_BSRR_BS9_Pos                   (9UL)
#define GPIO_BSRR_BS9_Msk                   (0x1UL << GPIO_BSRR_BS9_Pos)
#define GPIO_BSRR_BS9                       GPIO_BSRR_BS9_Msk
#define GPIO_BSRR_BS10_Pos                  (10UL)
#define GPIO_BSRR_BS10_Msk                  (0x1UL << GPIO_BSRR_BS10_Pos)
#define GPIO_BSRR_BS10                      GPIO_BSRR_BS10_Msk
#define GPIO_BSRR_BS11_Pos                  (11UL)
#define GPIO_BSRR_BS11_Msk                  (0x1UL << GPIO_BSRR_BS11_Pos)
#define GPIO_BSRR_BS11                      GPIO_BSRR_BS11_Msk
#define GPIO_BSRR_BS12_Pos                  (12UL)
#define GPIO_BSRR_BS12_Msk                  (0x1UL << GPIO_BSRR_BS12_Pos)
#define GPIO_BSRR_BS12                      GPIO_BSRR_BS12_Msk
#define GPIO_BSRR_BS13_Pos                  (13UL)
#define GPIO_BSRR_BS13_Msk                  (0x1UL << GPIO_BSRR_BS13_Pos)
#define GPIO_BSRR_BS13                      GPIO_BSRR_BS13_Msk
#define GPIO_BSRR_BS14_Pos                  (14UL)
#define GPIO_BSRR_BS14_Msk                  (0x1UL << GPIO_BSRR_BS14_Pos)
#define GPIO_BSRR_BS14                      GPIO_BSRR_BS14_Msk
#define GPIO_BSRR_BS15_Pos                  (15UL)
#define GPIO_BSRR_BS15_Msk                  (0x1UL << GPIO_BSRR_BS15_Pos)
#define GPIO_BSRR_BS15                      GPIO_BSRR_BS15_Msk
#define GPIO_BSRR_BR0_Pos                   (16UL)
#define GPIO_BSRR_BR0_Msk                   (0x1UL << GPIO_BSRR_BR0_Pos)
#define GPIO_BSRR_BR0                       GPIO_BSRR_BR0_Msk
#define GPIO_BSRR_BR1_Pos                   (17UL)
#define GPIO_BSRR_BR1_Msk                   (0x1UL << GPIO_BSRR_BR1_Pos)
#define GPIO_BSRR_BR1                       GPIO_BSRR_BR1_Msk
#define GPIO_BSRR_BR2_Pos                   (18UL)
#define GPIO_BSRR_BR2_Msk                   (0x1UL << GPIO_BSRR_BR2_Pos)
#define GPIO_BSRR_BR2                       GPIO_BSRR_BR2_Msk
#define GPIO_BSRR_BR3_Pos                   (19UL)
#define GPIO_BSRR_BR3_Msk                   (0x1UL << GPIO_BSRR_BR3_Pos)
#define GPIO_BSRR_BR3                       GPIO_BSRR_BR3_Msk
#define GPIO_BSRR_BR4_Pos                   (20UL)
#define GPIO_BSRR_BR4_Msk                   (0x1UL << GPIO_BSRR_BR4_Pos)
#define GPIO_BSRR_BR4                       GPIO_BSRR_BR4_Msk
#define GPIO_BSRR_BR5_Pos                   (21UL)
#define GPIO_BSRR_BR5_Msk                   (0x1UL << GPIO_BSRR_BR5_Pos)
#define GPIO_BSRR_BR5                       GPIO_BSRR_BR5_Msk
#define GPIO_BSRR_BR6_Pos                   (22UL)
#define GPIO_BSRR_BR6_Msk                   (0x1UL << GPIO_BSRR_BR6_Pos)
#define GPIO_BSRR_BR6                       GPIO_BSRR_BR6_Msk
#define GPIO_BSRR_BR7_Pos                   (23UL)
#define GPIO_BSRR_BR7_Msk                   (0x1UL << GPIO_BSRR_BR7_Pos)
#define GPIO_BSRR_BR7                       GPIO_BSRR_BR7_Msk
#define GPIO_BSRR_BR8_Pos                   (24UL)
#define GPIO_BSRR_BR8_Msk                   (0x1UL << GPIO_BSRR_BR8_Pos)
#define GPIO_BSRR_BR8                       GPIO_BSRR_BR8_Msk
#define GPIO_BSRR_BR9_Pos                   (25UL)
#define GPIO_BSRR_BR9_Msk                   (0x1UL << GPIO_BSRR_BR9_Pos)
#define GPIO_BSRR_BR9                       GPIO_BSRR_BR9_Msk
#define GPIO_BSRR_BR10_Pos                  (26UL)
#define GPIO_BSRR_BR10_Msk                  (0x1UL << GPIO_BSRR_BR10_Pos)
#define GPIO_BSRR_BR10                      GPIO_BSRR_BR10_Msk
#define GPIO_BSRR_BR11_Pos                  (27UL)
#define GPIO_BSRR_BR11_Msk                  (0x1UL << GPIO_BSRR_BR11_Pos)
#define GPIO_BSRR_BR11                      GPIO_BSRR_BR11_Msk
#define GPIO_BSRR_BR12_Pos                  (28UL)
#define GPIO_BSRR_BR12_Msk                  (0x1UL << GPIO_BSRR_BR12_Pos)
#define GPIO_BSRR_BR12                      GPIO_BSRR_BR12_Msk
#define GPIO_BSRR_BR13_Pos                  (29UL)
#define GPIO_BSRR_BR13_Msk                  (0x1UL << GPIO_BSRR_BR13_Pos)
#define GPIO_BSRR_BR13                      GPIO_BSRR_BR13_Msk
#define GPIO_BSRR_BR14_Pos                  (30UL)
#define GPIO_BSRR_BR14_Msk                  (0x1UL << GPIO_BSRR_BR14_Pos)
#define GPIO_BSRR_BR14                      GPIO_BSRR_BR14_Msk
#define GPIO_BSRR_BR15_Pos                  (31UL)
#define GPIO_BSRR_BR15_Msk                  (0x1UL << GPIO_BSRR_BR15_Pos)
#define GPIO_BSRR_BR15                      GPIO_BSRR_BR15_Msk
#define GPIO_LCKR_LCK0_Pos                  (0UL)
#define GPIO_LCKR_LCK0_Msk                  (0x1UL << GPIO_LCKR_LCK0_Pos)
#define GPIO_LCKR_LCK0                      GPIO_LCKR_LCK0_Msk
#define GPIO_LCKR_LCK1_Pos                  (1UL)
#define GPIO_LCKR_LCK1_Msk                  (0x1UL << GPIO_LCKR_LCK1_Pos)
#define GPIO_LCKR_LCK1                      GPIO_LCKR_LCK1_Msk
#define GPIO_LCKR_LCK2_Pos                  (2UL)
#define GPIO_LCKR_LCK2_Msk                  (0x1UL << GPIO_LCKR_LCK2_Pos)
#define GPIO_LCKR_LCK2                      GPIO_LCKR_LCK2_Msk
#define GPIO_LCKR_LCK3_Pos                  (3UL)
#define GPIO_LCKR_LCK3_Msk                  (0x1UL << GPIO_LCKR_LCK3_Pos)
#define GPIO_LCKR_LCK3                      GPIO_LCKR_LCK3_Msk
#define GPIO_LCKR_LCK4_Pos                  (4UL)
#define GPIO_LCKR_LCK4_Msk                  (0x1UL << GPIO_LCKR_LCK4_Pos)
#define GPIO_LCKR_LCK4                      GPIO_LCKR_LCK4_Msk
#define GPIO_LCKR_LCK5_Pos                  (5UL)
#define GPIO_LCKR_LCK5_Msk                  (0x1UL << GPIO_LCKR_LCK5_Pos)
#define GPIO_LCKR_LCK5                      GPIO_LCKR_LCK5_Msk
#define GPIO_LCKR_LCK6_Pos                  (6UL)
#define GPIO_LCKR_LCK6_Msk                  (0x1UL << GPIO_LCKR_LCK6_Pos)
#define GPIO_LCKR_LCK6                      GPIO_LCKR_LCK6_Msk
#define GPIO_LCKR_LCK7_Pos                  (7UL)
#define GPIO_LCKR_LCK7_Msk                  (0x1UL << GPIO_LCKR_LCK7_Pos)
#define GPIO_LCKR_LCK7                      GPIO_LCKR_LCK7_Msk
#define GPIO_LCKR_LCK8_Pos                  (8UL)
#define GPIO_LCKR_LCK8_Msk                  (0x1UL << GPIO_LCKR_LCK8_Pos)
#define GPIO_LCKR_LCK8                      GPIO_LCKR_LCK8_Msk
#define GPIO_LCKR_LCK9_Pos                  (9UL)
#define GPIO_LCKR_LCK9_Msk                  (0x1UL << GPIO_LCKR_LCK9_Pos)
#define GPIO_LCKR_LCK9                      GPIO_LCKR_LCK9_Msk
#define GPIO_LCKR_LCK10_Pos                 (10UL)
#define GPIO_LCKR_LCK10_Msk                 (0x1UL << GPIO_LCKR_LCK10_Pos)
#define GPIO_LCKR_LCK10                     GPIO_LCKR_LCK10_Msk
#define GPIO_LCKR_LCK11_Pos                 (11UL)
#define GPIO_LCKR_LCK11_Msk                 (0x1UL << GPIO_LCKR_LCK11_Pos)
#define GPIO_LCKR_LCK11                     GPIO_LCKR_LCK11_Msk
#define GPIO_LCKR_LCK12_Pos                 (12UL)
#define GPIO_LCKR_LCK12_Msk                 (0x1UL << GPIO_LCKR_LCK12_Pos)
#define GPIO_LCKR_LCK12                     GPIO_LCKR_LCK12_Msk
#define GPIO_LCKR_LCK13_Pos                 (13UL)
#define GPIO_LCKR_LCK13_Msk                 (0x1UL << GPIO_LCKR_LCK13_Pos)
#define GPIO_LCKR_LCK13                     GPIO_LCKR_LCK13_Msk
#define GPIO_LCKR_LCK14_Pos                 (14UL)
#define GPIO_LCKR_LCK14_Msk                 (0x1UL << GPIO_LCKR_LCK14_Pos)
#define GPIO_LCKR_LCK14                     GPIO_LCKR_LCK14_Msk
#define GPIO_LCKR_LCK15_Pos                 (15UL)
#define GPIO_LCKR_LCK15_Msk                 (0x1UL << GPIO_LCKR_LCK15_Pos)
#define GPIO_LCKR_LCK15                     GPIO_LCKR_LCK15_Msk
#define GPIO_LCKR_LCKK_Pos                  (16UL)
#define GPIO_LCKR_LCKK_Msk                  (0x1UL << GPIO_LCKR_LCKK_Pos)
#define GPIO_LCKR_LCKK                      GPIO_LCKR_LCKK_Msk
#define GPIO_AFRL_AFSEL0_Pos                (0UL)
#define GPIO_AFRL_AFSEL0_Msk                (0xFUL << GPIO_AFRL_AFSEL0_Pos)
#define GPIO_AFRL_AFSEL0                    GPIO_AFRL_AFSEL0_Msk
#define GPIO_AFRL_AFSEL0_0                  (0x1UL << GPIO_AFRL_AFSEL0_Pos)
#define GPIO_AFRL_AFSEL0_1                  (0x2UL << GPIO_AFRL_AFSEL0_Pos)
#define GPIO_AFRL_AFSEL0_2                  (0x4UL << GPIO_AFRL_AFSEL0_Pos)
#define GPIO_AFRL_AFSEL0_3                  (0x8UL << GPIO_AFRL_AFSEL0_Pos)
#define GPIO_AFRL_AFSEL1_Pos                (4UL)
#define GPIO_AFRL_AFSEL1_Msk                (0xFUL << GPIO_AFRL_AFSEL1_Pos)
#define GPIO_AFRL_AFSEL1                    GPIO_AFRL_AFSEL1_Msk
#define GPIO_AFRL_AFSEL1_0                  (0x1UL << GPIO_AFRL_AFSEL1_Pos)
#define GPIO_AFRL_AFSEL1_1                  (0x2UL << GPIO_AFRL_AFSEL1_Pos)
#define GPIO_AFRL_AFSEL1_2                  (0x4UL << GPIO_AFRL_AFSEL1_Pos)
#define GPIO_AFRL_AFSEL1_3                  (0x8UL << GPIO_AFRL_AFSEL1_Pos)
#define GPIO_AFRL_AFSEL2_Pos                (8UL)
#define GPIO_AFRL_AFSEL2_Msk                (0xFUL << GPIO_AFRL_AFSEL2_Pos)
#define GPIO_AFRL_AFSEL2                    GPIO_AFRL_AFSEL2_Msk
#define GPIO_AFRL_AFSEL2_0                  (0x1UL << GPIO_AFRL_AFSEL2_Pos)
#define GPIO_AFRL_AFSEL2_1                  (0x2UL << GPIO_AFRL_AFSEL2_Pos)
#define GPIO_AFRL_AFSEL2_2                  (0x4UL << GPIO_AFRL_AFSEL2_Pos)
#define GPIO_AFRL_AFSEL2_3                  (0x8UL << GPIO_AFRL_AFSEL2_Pos)
#define GPIO_AFRL_AFSEL3_Pos                (12UL)
#define GPIO_AFRL_AFSEL3_Msk                (0xFUL << GPIO_AFRL_AFSEL3_Pos)
#define GPIO_AFRL_AFSEL3                    GPIO_AFRL_AFSEL3_Msk
#define GPIO_AFRL_AFSEL3_0                  (0x1UL << GPIO_AFRL_AFSEL3_Pos)
#define GPIO_AFRL_AFSEL3_1                  (0x2UL << GPIO_AFRL_AFSEL3_Pos)
#define GPIO_AFRL_AFSEL3_2                  (0x4UL << GPIO_AFRL_AFSEL3_Pos)
#define GPIO_AFRL_AFSEL3_3                  (0x8UL << GPIO_AFRL_AFSEL3_Pos)
#define GPIO_AFRL_AFSEL4_Pos                (16UL)
#define GPIO_AFRL_AFSEL4_Msk                (0xFUL << GPIO_AFRL_AFSEL4_Pos)
#define GPIO_AFRL_AFSEL4                    GPIO_AFRL_AFSEL4_Msk
#define GPIO_AFRL_AFSEL4_0                  (0x1UL << GPIO_AFRL_AFSEL4_Pos)
#define GPIO_AFRL_AFSEL4_1                  (0x2UL << GPIO_AFRL_AFSEL4_Pos)
#define GPIO_AFRL_AFSEL4_2                  (0x4UL << GPIO_AFRL_AFSEL4_Pos)
#define GPIO_AFRL_AFSEL4_3                  (0x8UL << GPIO_AFRL_AFSEL4_Pos)
#define GPIO_AFRL_AFSEL5_Pos                (20UL)
#define GPIO_AFRL_AFSEL5_Msk                (0xFUL << GPIO_AFRL_AFSEL5_Pos)
#define GPIO_AFRL_AFSEL5                    GPIO_AFRL_AFSEL5_Msk
#define GPIO_AFRL_AFSEL5_0                  (0x1UL << GPIO_AFRL_AFSEL5_Pos)
#define GPIO_AFRL_AFSEL5_1                  (0x2UL << GPIO_AFRL_AFSEL5_Pos)
#define GPIO_AFRL_AFSEL5_2                  (0x4UL << GPIO_AFRL_AFSEL5_Pos)
#define GPIO_AFRL_AFSEL5_3                  (0x8UL << GPIO_AFRL_AFSEL5_Pos)
#define GPIO_AFRL_AFSEL6_Pos                (24UL)
#define GPIO_AFRL_AFSEL6_Msk                (0xFUL << GPIO_AFRL_AFSEL6_Pos)
#define GPIO_AFRL_AFSEL6                    GPIO_AFRL_AFSEL6_Msk
#define GPIO_AFRL_AFSEL6_0                  (0x1UL << GPIO_AFRL_AFSEL6_Pos)
#define GPIO_AFRL_AFSEL6_1                  (0x2UL << GPIO_AFRL_AFSEL6_Pos)
#define GPIO_AFRL_AFSEL6_2                  (0x4UL << GPIO_AFRL_AFSEL6_Pos)
#define GPIO_AFRL_AFSEL6_3                  (0x8UL << GPIO_AFRL_AFSEL6_Pos)
#define GPIO_AFRL_AFSEL7_Pos                (28UL)
#define GPIO_AFRL_AFSEL7_Msk                (0xFUL << GPIO_AFRL_AFSEL7_Pos)
#define GPIO_AFRL_AFSEL7                    GPIO_AFRL_AFSEL7_Msk
#define GPIO_AFRL_AFSEL7_0                  (0x1UL << GPIO_AFRL_AFSEL7_Pos)
#define GPIO_AFRL_AFSEL7_1                  (0x2UL << GPIO_AFRL_AFSEL7_Pos)
#define GPIO_AFRL_AFSEL7_2                  (0x4UL << GPIO_AFRL_AFSEL7_Pos)
#define GPIO_AFRL_AFSEL7_3                  (0x8UL << GPIO_AFRL_AFSEL7_Pos)
#define GPIO_AFRH_AFSEL8_Pos                (0UL)
#define GPIO_AFRH_AFSEL8_Msk                (0xFUL << GPIO_AFRH_AFSEL8_Pos)
#define GPIO_AFRH_AFSEL8                    GPIO_AFRH_AFSEL8_Msk
#define GPIO_AFRH_AFSEL8_0                  (0x1UL << GPIO_AFRH_AFSEL8_Pos)
#define GPIO_AFRH_AFSEL8_1                  (0x2UL << GPIO_AFRH_AFSEL8_Pos)
#define GPIO_AFRH_AFSEL8_2                  (0x4UL << GPIO_AFRH_AFSEL8_Pos)
#define GPIO_AFRH_AFSEL8_3                  (0x8UL << GPIO_AFRH_AFSEL8_Pos)
#define GPIO_AFRH_AFSEL9_Pos                (4UL)
#define GPIO_AFRH_AFSEL9_Msk                (0xFUL << GPIO_AFRH_AFSEL9_Pos)
#define GPIO_AFRH_AFSEL9                    GPIO_AFRH_AFSEL9_Msk
#define GPIO_AFRH_AFSEL9_0                  (0x1UL << GPIO_AFRH_AFSEL9_Pos)
#define GPIO_AFRH_AFSEL9_1                  (0x2UL << GPIO_AFRH_AFSEL9_Pos)
#define GPIO_AFRH_AFSEL9_2                  (0x4UL << GPIO_AFRH_AFSEL9_Pos)
#define GPIO_AFRH_AFSEL9_3                  (0x8UL << GPIO_AFRH_AFSEL9_Pos)
#define GPIO_AFRH_AFSEL10_Pos               (8UL)
#define GPIO_AFRH_AFSEL10_Msk               (0xFUL << GPIO_AFRH_AFSEL10_Pos)
#define GPIO_AFRH_AFSEL10                   GPIO_AFRH_AFSEL10_Msk
#define GPIO_AFRH_AFSEL10_0                 (0x1UL << GPIO_AFRH_AFSEL10_Pos)
#define GPIO_AFRH_AFSEL10_1                 (0x2UL << GPIO_AFRH_AFSEL10_Pos)
#define GPIO_AFRH_AFSEL10_2                 (0x4UL << GPIO_AFRH_AFSEL10_Pos)
#define GPIO_AFRH_AFSEL10_3                 (0x8UL << GPIO_AFRH_AFSEL10_Pos)
#define GPIO_AFRH_AFSEL11_Pos               (12UL)
#define GPIO_AFRH_AFSEL11_Msk               (0xFUL << GPIO_AFRH_AFSEL11_Pos)
#define GPIO_AFRH_AFSEL11                   GPIO_AFRH_AFSEL11_Msk
#define GPIO_AFRH_AFSEL11_0                 (0x1UL << GPIO_AFRH_AFSEL11_Pos)
#define GPIO_AFRH_AFSEL11_1                 (0x2UL << GPIO_AFRH_AFSEL11_Pos)
#define GPIO_AFRH_AFSEL11_2                 (0x4UL << GPIO_AFRH_AFSEL11_Pos)
#define GPIO_AFRH_AFSEL11_3                 (0x8UL << GPIO_AFRH_AFSEL11_Pos)
#define GPIO_AFRH_AFSEL12_Pos               (16UL)
#define GPIO_AFRH_AFSEL12_Msk               (0xFUL << GPIO_AFRH_AFSEL12_Pos)
#define GPIO_AFRH_AFSEL12                   GPIO_AFRH_AFSEL12_Msk
#define GPIO_AFRH_AFSEL12_0                 (0x1UL << GPIO_AFRH_AFSEL12_Pos)
#define GPIO_AFRH_AFSEL12_1                 (0x2UL << GPIO_AFRH_AFSEL12_Pos)
#define GPIO_AFRH_AFSEL12_2                 (0x4UL << GPIO_AFRH_AFSEL12_Pos)
#define GPIO_AFRH_AFSEL12_3                 (0x8UL << GPIO_AFRH_AFSEL12_Pos)
#define GPIO_AFRH_AFSEL13_Pos               (20UL)
#define GPIO_AFRH_AFSEL13_Msk               (0xFUL << GPIO_AFRH_AFSEL13_Pos)
#define GPIO_AFRH_AFSEL13                   GPIO_AFRH_AFSEL13_Msk
#define GPIO_AFRH_AFSEL13_0                 (0x1UL << GPIO_AFRH_AFSEL13_Pos)
#define GPIO_AFRH_AFSEL13_1                 (0x2UL << GPIO_AFRH_AFSEL13_Pos)
#define GPIO_AFRH_AFSEL13_2                 (0x4UL << GPIO_AFRH_AFSEL13_Pos)
#define GPIO_AFRH_AFSEL13_3                 (0x8UL << GPIO_AFRH_AFSEL13_Pos)
#define GPIO_AFRH_AFSEL14_Pos               (24UL)
#define GPIO_AFRH_AFSEL14_Msk               (0xFUL << GPIO_AFRH_AFSEL14_Pos)
#define GPIO_AFRH_AFSEL14                   GPIO_AFRH_AFSEL14_Msk
#define GPIO_AFRH_AFSEL14_0                 (0x1UL << GPIO_AFRH_AFSEL14_Pos)
#define GPIO_AFRH_AFSEL14_1                 (0x2UL << GPIO_AFRH_AFSEL14_Pos)
#define GPIO_AFRH_AFSEL14_2                 (0x4UL << GPIO_AFRH_AFSEL14_Pos)
#define GPIO_AFRH_AFSEL14_3                 (0x8UL << GPIO_AFRH_AFSEL14_Pos)
#define GPIO_AFRH_AFSEL15_Pos               (28UL)
#define GPIO_AFRH_AFSEL15_Msk               (0xFUL << GPIO_AFRH_AFSEL15_Pos)
#define GPIO_AFRH_AFSEL15                   GPIO_AFRH_AFSEL15_Msk
#define GPIO_AFRH_AFSEL15_0                 (0x1UL << GPIO_AFRH_AFSEL15_Pos)
#define GPIO_AFRH_AFSEL15_1                 (0x2UL << GPIO_AFRH_AFSEL15_Pos)
#define GPIO_AFRH_AFSEL15_2                 (0x4UL << GPIO_AFRH_AFSEL15_Pos)
#define GPIO_AFRH_AFSEL15_3                 (0x8UL << GPIO_AFRH_AFSEL15_Pos)
#define GPIO_BRR_BR0_Pos                    (0UL)
#define GPIO_BRR_BR0_Msk                    (0x1UL << GPIO_BRR_BR0_Pos)
#define GPIO_BRR_BR0                        GPIO_BRR_BR0_Msk
#define GPIO_BRR_BR1_Pos                    (1UL)
#define GPIO_BRR_BR1_Msk                    (0x1UL << GPIO_BRR_BR1_Pos)
#define GPIO_BRR_BR1                        GPIO_BRR_BR1_Msk
#define GPIO_BRR_BR2_Pos                    (2UL)
#define GPIO_BRR_BR2_Msk                    (0x1UL << GPIO_BRR_BR2_Pos)
#define GPIO_BRR_BR2                        GPIO_BRR_BR2_Msk
#define GPIO_BRR_BR3_Pos                    (3UL)
#define GPIO_BRR_BR3_Msk                    (0x1UL << GPIO_BRR_BR3_Pos)
#define GPIO_BRR_BR3                        GPIO_BRR_BR3_Msk
#define GPIO_BRR_BR4_Pos                    (4UL)
#define GPIO_BRR_BR4_Msk                    (0x1UL << GPIO_BRR_BR4_Pos)
#define GPIO_BRR_BR4                        GPIO_BRR_BR4_Msk
#define GPIO_BRR_BR5_Pos                    (5UL)
#define GPIO_BRR_BR5_Msk                    (0x1UL << GPIO_BRR_BR5_Pos)
#define GPIO_BRR_BR5                        GPIO_BRR_BR5_Msk
#define GPIO_BRR_BR6_Pos                    (6UL)
#define GPIO_BRR_BR6_Msk                    (0x1UL << GPIO_BRR_BR6_Pos)
#define GPIO_BRR_BR6                        GPIO_BRR_BR6_Msk
#define GPIO_BRR_BR7_Pos                    (7UL)
#define GPIO_BRR_BR7_Msk                    (0x1UL << GPIO_BRR_BR7_Pos)
#define GPIO_BRR_BR7                        GPIO_BRR_BR7_Msk
#define GPIO_BRR_BR8_Pos                    (8UL)
#define GPIO_BRR_BR8_Msk                    (0x1UL << GPIO_BRR_BR8_Pos)
#define GPIO_BRR_BR8                        GPIO_BRR_BR8_Msk
#define GPIO_BRR_BR9_Pos                    (9UL)
#define GPIO_BRR_BR9_Msk                    (0x1UL << GPIO_BRR_BR9_Pos)
#define GPIO_BRR_BR9                        GPIO_BRR_BR9_Msk
#define GPIO_BRR_BR10_Pos                   (10UL)
#define GPIO_BRR_BR10_Msk                   (0x1UL << GPIO_BRR_BR10_Pos)
#define GPIO_BRR_BR10                       GPIO_BRR_BR10_Msk
#define GPIO_BRR_BR11_Pos                   (11UL)
#define GPIO_BRR_BR11_Msk                   (0x1UL << GPIO_BRR_BR11_Pos)
#define GPIO_BRR_BR11                       GPIO_BRR_BR11_Msk
#define GPIO_BRR_BR12_Pos                   (12UL)
#define GPIO_BRR_BR12_Msk                   (0x1UL << GPIO_BRR_BR12_Pos)
#define GPIO_BRR_BR12                       GPIO_BRR_BR12_Msk
#define GPIO_BRR_BR13_Pos                   (13UL)
#define GPIO_BRR_BR13_Msk                   (0x1UL << GPIO_BRR_BR13_Pos)
#define GPIO_BRR_BR13                       GPIO_BRR_BR13_Msk
#define GPIO_BRR_BR14_Pos                   (14UL)
#define GPIO_BRR_BR14_Msk                   (0x1UL << GPIO_BRR_BR14_Pos)
#define GPIO_BRR_BR14                       GPIO_BRR_BR14_Msk
#define GPIO_BRR_BR15_Pos                   (15UL)
#define GPIO_BRR_BR15_Msk                   (0x1UL << GPIO_BRR_BR15_Pos)
#define GPIO_BRR_BR15                       GPIO_BRR_BR15_Msk
#define GPIO_HSLVR_HSLV0_Pos                (0UL)
#define GPIO_HSLVR_HSLV0_Msk                (0x1UL << GPIO_HSLVR_HSLV0_Pos)
#define GPIO_HSLVR_HSLV0                    GPIO_HSLVR_HSLV0_Msk
#define GPIO_HSLVR_HSLV1_Pos                (1UL)
#define GPIO_HSLVR_HSLV1_Msk                (0x1UL << GPIO_HSLVR_HSLV1_Pos)
#define GPIO_HSLVR_HSLV1                    GPIO_HSLVR_HSLV1_Msk
#define GPIO_HSLVR_HSLV2_Pos                (2UL)
#define GPIO_HSLVR_HSLV2_Msk                (0x1UL << GPIO_HSLVR_HSLV2_Pos)
#define GPIO_HSLVR_HSLV2                    GPIO_HSLVR_HSLV2_Msk
#define GPIO_HSLVR_HSLV3_Pos                (3UL)
#define GPIO_HSLVR_HSLV3_Msk                (0x1UL << GPIO_HSLVR_HSLV3_Pos)
#define GPIO_HSLVR_HSLV3                    GPIO_HSLVR_HSLV3_Msk
#define GPIO_HSLVR_HSLV4_Pos                (4UL)
#define GPIO_HSLVR_HSLV4_Msk                (0x1UL << GPIO_HSLVR_HSLV4_Pos)
#define GPIO_HSLVR_HSLV4                    GPIO_HSLVR_HSLV4_Msk
#define GPIO_HSLVR_HSLV5_Pos                (5UL)
#define GPIO_HSLVR_HSLV5_Msk                (0x1UL << GPIO_HSLVR_HSLV5_Pos)
#define GPIO_HSLVR_HSLV5                    GPIO_HSLVR_HSLV5_Msk
#define GPIO_HSLVR_HSLV6_Pos                (6UL)
#define GPIO_HSLVR_HSLV6_Msk                (0x1UL << GPIO_HSLVR_HSLV6_Pos)
#define GPIO_HSLVR_HSLV6                    GPIO_HSLVR_HSLV6_Msk
#define GPIO_HSLVR_HSLV7_Pos                (7UL)
#define GPIO_HSLVR_HSLV7_Msk                (0x1UL << GPIO_HSLVR_HSLV7_Pos)
#define GPIO_HSLVR_HSLV7                    GPIO_HSLVR_HSLV7_Msk
#define GPIO_HSLVR_HSLV8_Pos                (8UL)
#define GPIO_HSLVR_HSLV8_Msk                (0x1UL << GPIO_HSLVR_HSLV8_Pos)
#define GPIO_HSLVR_HSLV8                    GPIO_HSLVR_HSLV8_Msk
#define GPIO_HSLVR_HSLV9_Pos                (9UL)
#define GPIO_HSLVR_HSLV9_Msk                (0x1UL << GPIO_HSLVR_HSLV9_Pos)
#define GPIO_HSLVR_HSLV9                    GPIO_HSLVR_HSLV9_Msk
#define GPIO_HSLVR_HSLV10_Pos               (10UL)
#define GPIO_HSLVR_HSLV10_Msk               (0x1UL << GPIO_HSLVR_HSLV10_Pos)
#define GPIO_HSLVR_HSLV10                   GPIO_HSLVR_HSLV10_Msk
#define GPIO_HSLVR_HSLV11_Pos               (11UL)
#define GPIO_HSLVR_HSLV11_Msk               (x1UL << GPIO_HSLVR_HSLV11_Pos)
#define GPIO_HSLVR_HSLV11                   GPIO_HSLVR_HSLV11_Msk
#define GPIO_HSLVR_HSLV12_Pos               (12UL)
#define GPIO_HSLVR_HSLV12_Msk               (0x1UL << GPIO_HSLVR_HSLV12_Pos)
#define GPIO_HSLVR_HSLV12                   GPIO_HSLVR_HSLV12_Msk
#define GPIO_HSLVR_HSLV13_Pos               (13UL)
#define GPIO_HSLVR_HSLV13_Msk               (0x1UL << GPIO_HSLVR_HSLV13_Pos)
#define GPIO_HSLVR_HSLV13                   GPIO_HSLVR_HSLV13_Msk
#define GPIO_HSLVR_HSLV14_Pos               (14UL)
#define GPIO_HSLVR_HSLV14_Msk               (0x1UL << GPIO_HSLVR_HSLV14_Pos)
#define GPIO_HSLVR_HSLV14                   GPIO_HSLVR_HSLV14_Msk
#define GPIO_HSLVR_HSLV15_Pos               (15UL)
#define GPIO_HSLVR_HSLV15_Msk               (0x1UL << GPIO_HSLVR_HSLV15_Pos)
#define GPIO_HSLVR_HSLV15                   GPIO_HSLVR_HSLV15_Msk
#define GPIO_SECCFGR_SEC0_Pos               (0UL)
#define GPIO_SECCFGR_SEC0_Msk               (0x1UL << GPIO_SECCFGR_SEC0_Pos)
#define GPIO_SECCFGR_SEC0                   GPIO_SECCFGR_SEC0_Msk
#define GPIO_SECCFGR_SEC1_Pos               (1UL)
#define GPIO_SECCFGR_SEC1_Msk               (0x1UL << GPIO_SECCFGR_SEC1_Pos)
#define GPIO_SECCFGR_SEC1                   GPIO_SECCFGR_SEC1_Msk
#define GPIO_SECCFGR_SEC2_Pos               (2UL)
#define GPIO_SECCFGR_SEC2_Msk               (0x1UL << GPIO_SECCFGR_SEC2_Pos)
#define GPIO_SECCFGR_SEC2                   GPIO_SECCFGR_SEC2_Msk
#define GPIO_SECCFGR_SEC3_Pos               (3UL)
#define GPIO_SECCFGR_SEC3_Msk               (0x1UL << GPIO_SECCFGR_SEC3_Pos)
#define GPIO_SECCFGR_SEC3                   GPIO_SECCFGR_SEC3_Msk
#define GPIO_SECCFGR_SEC4_Pos               (4UL)
#define GPIO_SECCFGR_SEC4_Msk               (0x1UL << GPIO_SECCFGR_SEC4_Pos)
#define GPIO_SECCFGR_SEC4                   GPIO_SECCFGR_SEC4_Msk
#define GPIO_SECCFGR_SEC5_Pos               (5UL)
#define GPIO_SECCFGR_SEC5_Msk               (0x1UL << GPIO_SECCFGR_SEC5_Pos)
#define GPIO_SECCFGR_SEC5                   GPIO_SECCFGR_SEC5_Msk
#define GPIO_SECCFGR_SEC6_Pos               (6UL)
#define GPIO_SECCFGR_SEC6_Msk               (0x1UL << GPIO_SECCFGR_SEC6_Pos)
#define GPIO_SECCFGR_SEC6                   GPIO_SECCFGR_SEC6_Msk
#define GPIO_SECCFGR_SEC7_Pos               (7UL)
#define GPIO_SECCFGR_SEC7_Msk               (0x1UL << GPIO_SECCFGR_SEC7_Pos)
#define GPIO_SECCFGR_SEC7                   GPIO_SECCFGR_SEC7_Msk
#define GPIO_SECCFGR_SEC8_Pos               (8UL)
#define GPIO_SECCFGR_SEC8_Msk               (0x1UL << GPIO_SECCFGR_SEC8_Pos)
#define GPIO_SECCFGR_SEC8                   GPIO_SECCFGR_SEC8_Msk
#define GPIO_SECCFGR_SEC9_Pos               (9UL)
#define GPIO_SECCFGR_SEC9_Msk               (0x1UL << GPIO_SECCFGR_SEC9_Pos)
#define GPIO_SECCFGR_SEC9                   GPIO_SECCFGR_SEC9_Msk
#define GPIO_SECCFGR_SEC10_Pos              (10UL)
#define GPIO_SECCFGR_SEC10_Msk              (0x1UL << GPIO_SECCFGR_SEC10_Pos)
#define GPIO_SECCFGR_SEC10                  GPIO_SECCFGR_SEC10_Msk
#define GPIO_SECCFGR_SEC11_Pos              (11UL)
#define GPIO_SECCFGR_SEC11_Msk              (x1UL << GPIO_SECCFGR_SEC11_Pos)
#define GPIO_SECCFGR_SEC11                  GPIO_SECCFGR_SEC11_Msk
#define GPIO_SECCFGR_SEC12_Pos              (12UL)
#define GPIO_SECCFGR_SEC12_Msk              (0x1UL << GPIO_SECCFGR_SEC12_Pos)
#define GPIO_SECCFGR_SEC12                  GPIO_SECCFGR_SEC12_Msk
#define GPIO_SECCFGR_SEC13_Pos              (13UL)
#define GPIO_SECCFGR_SEC13_Msk              (0x1UL << GPIO_SECCFGR_SEC13_Pos)
#define GPIO_SECCFGR_SEC13                  GPIO_SECCFGR_SEC13_Msk
#define GPIO_SECCFGR_SEC14_Pos              (14UL)
#define GPIO_SECCFGR_SEC14_Msk              (0x1UL << GPIO_SECCFGR_SEC14_Pos)
#define GPIO_SECCFGR_SEC14                  GPIO_SECCFGR_SEC14_Msk
#define GPIO_SECCFGR_SEC15_Pos              (15UL)
#define GPIO_SECCFGR_SEC15_Msk              (0x1UL << GPIO_SECCFGR_SEC15_Pos)
#define GPIO_SECCFGR_SEC15                  GPIO_SECCFGR_SEC15_Msk
#define RCC_CR_MSISON_Pos                   (0UL)
#define RCC_CR_MSISON_Msk                   (0x1UL << RCC_CR_MSISON_Pos)
#define RCC_CR_MSISON                       RCC_CR_MSISON_Msk
#define RCC_CR_MSIKERON_Pos                 (1UL)
#define RCC_CR_MSIKERON_Msk                 (0x1UL << RCC_CR_MSIKERON_Pos)
#define RCC_CR_MSIKERON                     RCC_CR_MSIKERON_Msk
#define RCC_CR_MSISRDY_Pos                  (2UL)
#define RCC_CR_MSISRDY_Msk                  (0x1UL << RCC_CR_MSISRDY_Pos)
#define RCC_CR_MSISRDY                      RCC_CR_MSISRDY_Msk
#define RCC_CR_MSIPLLEN_Pos                 (3UL)
#define RCC_CR_MSIPLLEN_Msk                 (0x1UL << RCC_CR_MSIPLLEN_Pos)
#define RCC_CR_MSIPLLEN                     RCC_CR_MSIPLLEN_Msk
#define RCC_CR_MSIKON_Pos                   (4UL)
#define RCC_CR_MSIKON_Msk                   (0x1UL << RCC_CR_MSIKON_Pos)
#define RCC_CR_MSIKON                       RCC_CR_MSIKON_Msk
#define RCC_CR_MSIKRDY_Pos                  (5UL)
#define RCC_CR_MSIKRDY_Msk                  (0x1UL << RCC_CR_MSIKRDY_Pos)
#define RCC_CR_MSIKRDY                      RCC_CR_MSIKRDY_Msk
#define RCC_CR_MSIPLLSEL_Pos                (6UL)
#define RCC_CR_MSIPLLSEL_Msk                (0x1UL << RCC_CR_MSIPLLSEL_Pos)
#define RCC_CR_MSIPLLSEL                    RCC_CR_MSIPLLSEL_Msk
#define RCC_CR_MSIPLLFAST_Pos               (7UL)
#define RCC_CR_MSIPLLFAST_Msk               (0x1UL << RCC_CR_MSIPLLFAST_Pos)
#define RCC_CR_MSIPLLFAST                   RCC_CR_MSIPLLFAST_Msk
#define RCC_CR_HSION_Pos                    (8UL)
#define RCC_CR_HSION_Msk                    (0x1UL << RCC_CR_HSION_Pos)
#define RCC_CR_HSION                        RCC_CR_HSION_Msk
#define RCC_CR_HSIKERON_Pos                 (9UL)
#define RCC_CR_HSIKERON_Msk                 (0x1UL << RCC_CR_HSIKERON_Pos)
#define RCC_CR_HSIKERON                     RCC_CR_HSIKERON_Msk
#define RCC_CR_HSIRDY_Pos                   (10UL)
#define RCC_CR_HSIRDY_Msk                   (0x1UL << RCC_CR_HSIRDY_Pos)
#define RCC_CR_HSIRDY                       RCC_CR_HSIRDY_Msk
#define RCC_CR_HSI48ON_Pos                  (12UL)
#define RCC_CR_HSI48ON_Msk                  (0x1UL << RCC_CR_HSI48ON_Pos)
#define RCC_CR_HSI48ON                      RCC_CR_HSI48ON_Msk
#define RCC_CR_HSI48RDY_Pos                 (13UL)
#define RCC_CR_HSI48RDY_Msk                 (0x1UL << RCC_CR_HSI48RDY_Pos)
#define RCC_CR_HSI48RDY                     RCC_CR_HSI48RDY_Msk
#define RCC_CR_SHSION_Pos                   (14UL)
#define RCC_CR_SHSION_Msk                   (0x1UL << RCC_CR_SHSION_Pos)
#define RCC_CR_SHSION                       RCC_CR_SHSION_Msk
#define RCC_CR_SHSIRDY_Pos                  (15UL)
#define RCC_CR_SHSIRDY_Msk                  (0x1UL << RCC_CR_SHSIRDY_Pos)
#define RCC_CR_SHSIRDY                      RCC_CR_SHSIRDY_Msk
#define RCC_CR_HSEON_Pos                    (16UL)
#define RCC_CR_HSEON_Msk                    (0x1UL << RCC_CR_HSEON_Pos)
#define RCC_CR_HSEON                        RCC_CR_HSEON_Msk
#define RCC_CR_HSERDY_Pos                   (17UL)
#define RCC_CR_HSERDY_Msk                   (0x1UL << RCC_CR_HSERDY_Pos)
#define RCC_CR_HSERDY                       RCC_CR_HSERDY_Msk
#define RCC_CR_HSEBYP_Pos                   (18UL)
#define RCC_CR_HSEBYP_Msk                   (0x1UL << RCC_CR_HSEBYP_Pos)
#define RCC_CR_HSEBYP                       RCC_CR_HSEBYP_Msk
#define RCC_CR_CSSON_Pos                    (19UL)
#define RCC_CR_CSSON_Msk                    (0x1UL << RCC_CR_CSSON_Pos)
#define RCC_CR_CSSON                        RCC_CR_CSSON_Msk
#define RCC_CR_HSEEXT_Pos                   (20UL)
#define RCC_CR_HSEEXT_Msk                   (0x1UL << RCC_CR_HSEEXT_Pos)
#define RCC_CR_HSEEXT                       RCC_CR_HSEEXT_Msk
#define RCC_CR_PLL1ON_Pos                   (24UL)
#define RCC_CR_PLL1ON_Msk                   (0x1UL << RCC_CR_PLL1ON_Pos)
#define RCC_CR_PLL1ON                       RCC_CR_PLL1ON_Msk
#define RCC_CR_PLL1RDY_Pos                  (25UL)
#define RCC_CR_PLL1RDY_Msk                  (0x1UL << RCC_CR_PLL1RDY_Pos)
#define RCC_CR_PLL1RDY                      RCC_CR_PLL1RDY_Msk
#define RCC_CR_PLL2ON_Pos                   (26UL)
#define RCC_CR_PLL2ON_Msk                   (0x1UL << RCC_CR_PLL2ON_Pos)
#define RCC_CR_PLL2ON                       RCC_CR_PLL2ON_Msk
#define RCC_CR_PLL2RDY_Pos                  (27UL)
#define RCC_CR_PLL2RDY_Msk                  (0x1UL << RCC_CR_PLL2RDY_Pos)
#define RCC_CR_PLL2RDY                      RCC_CR_PLL2RDY_Msk
#define RCC_CR_PLL3ON_Pos                   (28UL)
#define RCC_CR_PLL3ON_Msk                   (0x1UL << RCC_CR_PLL3ON_Pos)
#define RCC_CR_PLL3ON                       RCC_CR_PLL3ON_Msk
#define RCC_CR_PLL3RDY_Pos                  (29UL)
#define RCC_CR_PLL3RDY_Msk                  (0x1UL << RCC_CR_PLL3RDY_Pos)
#define RCC_CR_PLL3RDY                      RCC_CR_PLL3RDY_Msk
#define RCC_ICSCR1_MSICAL3_Pos              (0UL)
#define RCC_ICSCR1_MSICAL3_Msk              (0x1FUL << RCC_ICSCR1_MSICAL3_Pos)
#define RCC_ICSCR1_MSICAL3                  RCC_ICSCR1_MSICAL3_Msk
#define RCC_ICSCR1_MSICAL3_0                (0x01UL << RCC_ICSCR1_MSICAL3_Pos)
#define RCC_ICSCR1_MSICAL3_1                (0x02UL << RCC_ICSCR1_MSICAL3_Pos)
#define RCC_ICSCR1_MSICAL3_2                (0x04UL << RCC_ICSCR1_MSICAL3_Pos)
#define RCC_ICSCR1_MSICAL3_3                (0x08UL << RCC_ICSCR1_MSICAL3_Pos)
#define RCC_ICSCR1_MSICAL3_4                (0x10UL << RCC_ICSCR1_MSICAL3_Pos)
#define RCC_ICSCR1_MSICAL2_Pos              (5UL)
#define RCC_ICSCR1_MSICAL2_Msk              (0x1FUL << RCC_ICSCR1_MSICAL2_Pos)
#define RCC_ICSCR1_MSICAL2                  RCC_ICSCR1_MSICAL2_Msk
#define RCC_ICSCR1_MSICAL2_0                (0x01UL << RCC_ICSCR1_MSICAL2_Pos)
#define RCC_ICSCR1_MSICAL2_1                (0x02UL << RCC_ICSCR1_MSICAL2_Pos)
#define RCC_ICSCR1_MSICAL2_2                (0x04UL << RCC_ICSCR1_MSICAL2_Pos)
#define RCC_ICSCR1_MSICAL2_3                (0x08UL << RCC_ICSCR1_MSICAL2_Pos)
#define RCC_ICSCR1_MSICAL2_4                (0x10UL << RCC_ICSCR1_MSICAL2_Pos)
#define RCC_ICSCR1_MSICAL1_Pos              (10UL)
#define RCC_ICSCR1_MSICAL1_Msk              (0x1FUL << RCC_ICSCR1_MSICAL1_Pos)
#define RCC_ICSCR1_MSICAL1                  RCC_ICSCR1_MSICAL1_Msk
#define RCC_ICSCR1_MSICAL1_0                (0x01UL << RCC_ICSCR1_MSICAL1_Pos)
#define RCC_ICSCR1_MSICAL1_1                (0x02UL << RCC_ICSCR1_MSICAL1_Pos)
#define RCC_ICSCR1_MSICAL1_2                (0x04UL << RCC_ICSCR1_MSICAL1_Pos)
#define RCC_ICSCR1_MSICAL1_3                (0x08UL << RCC_ICSCR1_MSICAL1_Pos)
#define RCC_ICSCR1_MSICAL1_4                (0x10UL << RCC_ICSCR1_MSICAL1_Pos)
#define RCC_ICSCR1_MSICAL0_Pos              (15UL)
#define RCC_ICSCR1_MSICAL0_Msk              (0x1FUL << RCC_ICSCR1_MSICAL0_Pos)
#define RCC_ICSCR1_MSICAL0                  RCC_ICSCR1_MSICAL0_Msk
#define RCC_ICSCR1_MSICAL0_0                (0x01UL << RCC_ICSCR1_MSICAL0_Pos)
#define RCC_ICSCR1_MSICAL0_1                (0x02UL << RCC_ICSCR1_MSICAL0_Pos)
#define RCC_ICSCR1_MSICAL0_2                (0x04UL << RCC_ICSCR1_MSICAL0_Pos)
#define RCC_ICSCR1_MSICAL0_3                (0x08UL << RCC_ICSCR1_MSICAL0_Pos)
#define RCC_ICSCR1_MSICAL0_4                (0x10UL << RCC_ICSCR1_MSICAL0_Pos)
#define RCC_ICSCR1_MSIBIAS_Pos              (22UL)
#define RCC_ICSCR1_MSIBIAS_Msk              (0x1UL << RCC_ICSCR1_MSIBIAS_Pos)
#define RCC_ICSCR1_MSIBIAS                  RCC_ICSCR1_MSIBIAS_Msk
#define RCC_ICSCR1_MSIRGSEL_Pos             (23UL)
#define RCC_ICSCR1_MSIRGSEL_Msk             (0x1UL << RCC_ICSCR1_MSIRGSEL_Pos)
#define RCC_ICSCR1_MSIRGSEL                 RCC_ICSCR1_MSIRGSEL_Msk
#define RCC_ICSCR1_MSIKRANGE_Pos            (24UL)
#define RCC_ICSCR1_MSIKRANGE_Msk            (0xFUL << RCC_ICSCR1_MSIKRANGE_Pos)
#define RCC_ICSCR1_MSIKRANGE                RCC_ICSCR1_MSIKRANGE_Msk
#define RCC_ICSCR1_MSIKRANGE_0              (0x1UL << RCC_ICSCR1_MSIKRANGE_Pos)
#define RCC_ICSCR1_MSIKRANGE_1              (0x2UL << RCC_ICSCR1_MSIKRANGE_Pos)
#define RCC_ICSCR1_MSIKRANGE_2              (0x4UL << RCC_ICSCR1_MSIKRANGE_Pos)
#define RCC_ICSCR1_MSIKRANGE_3              (0x8UL << RCC_ICSCR1_MSIKRANGE_Pos)
#define RCC_ICSCR1_MSISRANGE_Pos            (28UL)
#define RCC_ICSCR1_MSISRANGE_Msk            (0xFUL << RCC_ICSCR1_MSISRANGE_Pos)
#define RCC_ICSCR1_MSISRANGE                RCC_ICSCR1_MSISRANGE_Msk
#define RCC_ICSCR1_MSISRANGE_0              (0x1UL << RCC_ICSCR1_MSISRANGE_Pos)
#define RCC_ICSCR1_MSISRANGE_1              (0x2UL << RCC_ICSCR1_MSISRANGE_Pos)
#define RCC_ICSCR1_MSISRANGE_2              (0x4UL << RCC_ICSCR1_MSISRANGE_Pos)
#define RCC_ICSCR1_MSISRANGE_3              (0x8UL << RCC_ICSCR1_MSISRANGE_Pos)
#define RCC_ICSCR2_MSITRIM3_Pos             (0UL)
#define RCC_ICSCR2_MSITRIM3_Msk             (0x1FUL << RCC_ICSCR2_MSITRIM3_Pos)
#define RCC_ICSCR2_MSITRIM3                 RCC_ICSCR2_MSITRIM3_Msk
#define RCC_ICSCR2_MSITRIM3_0               (0x01UL << RCC_ICSCR2_MSITRIM3_Pos)
#define RCC_ICSCR2_MSITRIM3_1               (0x02UL << RCC_ICSCR2_MSITRIM3_Pos)
#define RCC_ICSCR2_MSITRIM3_2               (0x04UL << RCC_ICSCR2_MSITRIM3_Pos)
#define RCC_ICSCR2_MSITRIM3_3               (0x08UL << RCC_ICSCR2_MSITRIM3_Pos)
#define RCC_ICSCR2_MSITRIM3_4               (0x10UL << RCC_ICSCR2_MSITRIM3_Pos)
#define RCC_ICSCR2_MSITRIM2_Pos             (5UL)
#define RCC_ICSCR2_MSITRIM2_Msk             (0x1FUL << RCC_ICSCR2_MSITRIM2_Pos)
#define RCC_ICSCR2_MSITRIM2                 RCC_ICSCR2_MSITRIM2_Msk
#define RCC_ICSCR2_MSITRIM2_0               (0x01UL << RCC_ICSCR2_MSITRIM2_Pos)
#define RCC_ICSCR2_MSITRIM2_1               (0x02UL << RCC_ICSCR2_MSITRIM2_Pos)
#define RCC_ICSCR2_MSITRIM2_2               (0x04UL << RCC_ICSCR2_MSITRIM2_Pos)
#define RCC_ICSCR2_MSITRIM2_3               (0x08UL << RCC_ICSCR2_MSITRIM2_Pos)
#define RCC_ICSCR2_MSITRIM2_4               (0x10UL << RCC_ICSCR2_MSITRIM2_Pos)
#define RCC_ICSCR2_MSITRIM1_Pos             (10UL)
#define RCC_ICSCR2_MSITRIM1_Msk             (0x1FUL << RCC_ICSCR2_MSITRIM1_Pos)
#define RCC_ICSCR2_MSITRIM1                 RCC_ICSCR2_MSITRIM1_Msk
#define RCC_ICSCR2_MSITRIM1_0               (0x01UL << RCC_ICSCR2_MSITRIM1_Pos)
#define RCC_ICSCR2_MSITRIM1_1               (0x02UL << RCC_ICSCR2_MSITRIM1_Pos)
#define RCC_ICSCR2_MSITRIM1_2               (0x04UL << RCC_ICSCR2_MSITRIM1_Pos)
#define RCC_ICSCR2_MSITRIM1_3               (0x08UL << RCC_ICSCR2_MSITRIM1_Pos)
#define RCC_ICSCR2_MSITRIM1_4               (0x10UL << RCC_ICSCR2_MSITRIM1_Pos)
#define RCC_ICSCR2_MSITRIM0_Pos             (15UL)
#define RCC_ICSCR2_MSITRIM0_Msk             (0x1FUL << RCC_ICSCR2_MSITRIM0_Pos)
#define RCC_ICSCR2_MSITRIM0                 RCC_ICSCR2_MSITRIM0_Msk
#define RCC_ICSCR2_MSITRIM0_0               (0x01UL << RCC_ICSCR2_MSITRIM0_Pos)
#define RCC_ICSCR2_MSITRIM0_1               (0x02UL << RCC_ICSCR2_MSITRIM0_Pos)
#define RCC_ICSCR2_MSITRIM0_2               (0x04UL << RCC_ICSCR2_MSITRIM0_Pos)
#define RCC_ICSCR2_MSITRIM0_3               (0x08UL << RCC_ICSCR2_MSITRIM0_Pos)
#define RCC_ICSCR2_MSITRIM0_4               (0x10UL << RCC_ICSCR2_MSITRIM0_Pos)
#define RCC_ICSCR3_HSICAL_Pos               (0UL)
#define RCC_ICSCR3_HSICAL_Msk               (0xFFFUL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL                   RCC_ICSCR3_HSICAL_Msk
#define RCC_ICSCR3_HSICAL_0                 (0x001UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_1                 (0x002UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_2                 (0x004UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_3                 (0x008UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_4                 (0x010UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_5                 (0x020UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_6                 (0x040UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_7                 (0x080UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_8                 (0x100UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_9                 (0x200UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_10                (0x400UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSICAL_11                (0x800UL << RCC_ICSCR3_HSICAL_Pos)
#define RCC_ICSCR3_HSITRIM_Pos              (16UL)
#define RCC_ICSCR3_HSITRIM_Msk              (0x1FUL << RCC_ICSCR3_HSITRIM_Pos)
#define RCC_ICSCR3_HSITRIM                  RCC_ICSCR3_HSITRIM_Msk
#define RCC_ICSCR3_HSITRIM_0                (0x01UL << RCC_ICSCR3_HSITRIM_Pos)
#define RCC_ICSCR3_HSITRIM_1                (0x02UL << RCC_ICSCR3_HSITRIM_Pos)
#define RCC_ICSCR3_HSITRIM_2                (0x04UL << RCC_ICSCR3_HSITRIM_Pos)
#define RCC_ICSCR3_HSITRIM_3                (0x08UL << RCC_ICSCR3_HSITRIM_Pos)
#define RCC_ICSCR3_HSITRIM_4                (0x10UL << RCC_ICSCR3_HSITRIM_Pos)
#define RCC_CRRCR_HSI48CAL_Pos              (0UL)
#define RCC_CRRCR_HSI48CAL_Msk              (0x1FFUL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL                  RCC_CRRCR_HSI48CAL_Msk
#define RCC_CRRCR_HSI48CAL_0                (0x001UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_1                (0x002UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_2                (0x004UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_3                (0x008UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_4                (0x010UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_5                (0x020UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_6                (0x040UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_7                (0x080UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CRRCR_HSI48CAL_8                (0x100UL << RCC_CRRCR_HSI48CAL_Pos)
#define RCC_CFGR1_SW_Pos                    (0UL)
#define RCC_CFGR1_SW_Msk                    (0x3UL << RCC_CFGR1_SW_Pos)
#define RCC_CFGR1_SW                        RCC_CFGR1_SW_Msk
#define RCC_CFGR1_SW_0                      (0x1UL << RCC_CFGR1_SW_Pos)
#define RCC_CFGR1_SW_1                      (0x2UL << RCC_CFGR1_SW_Pos)
#define RCC_CFGR1_SWS_Pos                   (2UL)
#define RCC_CFGR1_SWS_Msk                   (0x3UL << RCC_CFGR1_SWS_Pos)
#define RCC_CFGR1_SWS                       RCC_CFGR1_SWS_Msk
#define RCC_CFGR1_SWS_0                     (0x1UL << RCC_CFGR1_SWS_Pos)
#define RCC_CFGR1_SWS_1                     (0x2UL << RCC_CFGR1_SWS_Pos)
#define RCC_CFGR1_STOPWUCK_Pos              (4UL)
#define RCC_CFGR1_STOPWUCK_Msk              (0x1UL << RCC_CFGR1_STOPWUCK_Pos)
#define RCC_CFGR1_STOPWUCK                  RCC_CFGR1_STOPWUCK_Msk
#define RCC_CFGR1_STOPKERWUCK_Pos           (5UL)
#define RCC_CFGR1_STOPKERWUCK_Msk           (0x1UL << RCC_CFGR1_STOPKERWUCK_Pos)
#define RCC_CFGR1_STOPKERWUCK               RCC_CFGR1_STOPKERWUCK_Msk
#define RCC_CFGR1_MCOSEL_Pos                (24UL)
#define RCC_CFGR1_MCOSEL_Msk                (0xFUL << RCC_CFGR1_MCOSEL_Pos)
#define RCC_CFGR1_MCOSEL                    RCC_CFGR1_MCOSEL_Msk
#define RCC_CFGR1_MCOSEL_0                  (0x1UL << RCC_CFGR1_MCOSEL_Pos)
#define RCC_CFGR1_MCOSEL_1                  (0x2UL << RCC_CFGR1_MCOSEL_Pos)
#define RCC_CFGR1_MCOSEL_2                  (0x4UL << RCC_CFGR1_MCOSEL_Pos)
#define RCC_CFGR1_MCOSEL_3                  (0x8UL << RCC_CFGR1_MCOSEL_Pos)
#define RCC_CFGR1_MCOPRE_Pos                (28UL)
#define RCC_CFGR1_MCOPRE_Msk                (0x7UL << RCC_CFGR1_MCOPRE_Pos)
#define RCC_CFGR1_MCOPRE                    RCC_CFGR1_MCOPRE_Msk
#define RCC_CFGR1_MCOPRE_0                  (0x1UL << RCC_CFGR1_MCOPRE_Pos)
#define RCC_CFGR1_MCOPRE_1                  (0x2UL << RCC_CFGR1_MCOPRE_Pos)
#define RCC_CFGR1_MCOPRE_2                  (0x4UL << RCC_CFGR1_MCOPRE_Pos)
#define RCC_CFGR2_HPRE_Pos                  (0UL)
#define RCC_CFGR2_HPRE_Msk                  (0xFUL << RCC_CFGR2_HPRE_Pos)
#define RCC_CFGR2_HPRE                      RCC_CFGR2_HPRE_Msk
#define RCC_CFGR2_HPRE_0                    (0x1UL << RCC_CFGR2_HPRE_Pos)
#define RCC_CFGR2_HPRE_1                    (0x2UL << RCC_CFGR2_HPRE_Pos)
#define RCC_CFGR2_HPRE_2                    (0x4UL << RCC_CFGR2_HPRE_Pos)
#define RCC_CFGR2_HPRE_3                    (0x8UL << RCC_CFGR2_HPRE_Pos)
#define RCC_CFGR2_PPRE1_Pos                 (4UL)
#define RCC_CFGR2_PPRE1_Msk                 (0x7UL << RCC_CFGR2_PPRE1_Pos)
#define RCC_CFGR2_PPRE1                     RCC_CFGR2_PPRE1_Msk
#define RCC_CFGR2_PPRE1_0                   (0x1UL << RCC_CFGR2_PPRE1_Pos)
#define RCC_CFGR2_PPRE1_1                   (0x2UL << RCC_CFGR2_PPRE1_Pos)
#define RCC_CFGR2_PPRE1_2                   (0x4UL << RCC_CFGR2_PPRE1_Pos)
#define RCC_CFGR2_PPRE2_Pos                 (8UL)
#define RCC_CFGR2_PPRE2_Msk                 (0x7UL << RCC_CFGR2_PPRE2_Pos)
#define RCC_CFGR2_PPRE2                     RCC_CFGR2_PPRE2_Msk
#define RCC_CFGR2_PPRE2_0                   (0x1UL << RCC_CFGR2_PPRE2_Pos)
#define RCC_CFGR2_PPRE2_1                   (0x2UL << RCC_CFGR2_PPRE2_Pos)
#define RCC_CFGR2_PPRE2_2                   (0x4UL << RCC_CFGR2_PPRE2_Pos)
#define RCC_CFGR2_AHB1DIS_Pos               (16UL)
#define RCC_CFGR2_AHB1DIS_Msk               (0x1UL << RCC_CFGR2_AHB1DIS_Pos)
#define RCC_CFGR2_AHB1DIS                   RCC_CFGR2_AHB1DIS_Msk
#define RCC_CFGR2_AHB2DIS1_Pos              (17UL)
#define RCC_CFGR2_AHB2DIS1_Msk              (0x1UL << RCC_CFGR2_AHB2DIS1_Pos)
#define RCC_CFGR2_AHB2DIS1                  RCC_CFGR2_AHB2DIS1_Msk
#define RCC_CFGR2_AHB2DIS2_Pos              (18UL)
#define RCC_CFGR2_AHB2DIS2_Msk              (0x1UL << RCC_CFGR2_AHB2DIS2_Pos)
#define RCC_CFGR2_AHB2DIS2                  RCC_CFGR2_AHB2DIS2_Msk
#define RCC_CFGR2_APB1DIS_Pos               (19UL)
#define RCC_CFGR2_APB1DIS_Msk               (0x1UL << RCC_CFGR2_APB1DIS_Pos)
#define RCC_CFGR2_APB1DIS                   RCC_CFGR2_APB1DIS_Msk
#define RCC_CFGR2_APB2DIS_Pos               (20UL)
#define RCC_CFGR2_APB2DIS_Msk               (0x1UL << RCC_CFGR2_APB2DIS_Pos)
#define RCC_CFGR2_APB2DIS                   RCC_CFGR2_APB2DIS_Msk
#define RCC_CFGR3_PPRE3_Pos                 (4UL)
#define RCC_CFGR3_PPRE3_Msk                 (0x7UL << RCC_CFGR3_PPRE3_Pos)
#define RCC_CFGR3_PPRE3                     RCC_CFGR3_PPRE3_Msk
#define RCC_CFGR3_PPRE3_0                   (0x1UL << RCC_CFGR3_PPRE3_Pos)
#define RCC_CFGR3_PPRE3_1                   (0x2UL << RCC_CFGR3_PPRE3_Pos)
#define RCC_CFGR3_PPRE3_2                   (0x4UL << RCC_CFGR3_PPRE3_Pos)
#define RCC_CFGR3_AHB3DIS_Pos               (16UL)
#define RCC_CFGR3_AHB3DIS_Msk               (0x1UL << RCC_CFGR3_AHB3DIS_Pos)
#define RCC_CFGR3_AHB3DIS                   RCC_CFGR3_AHB3DIS_Msk
#define RCC_CFGR3_APB3DIS_Pos               (17UL)
#define RCC_CFGR3_APB3DIS_Msk               (0x1UL << RCC_CFGR3_APB3DIS_Pos)
#define RCC_CFGR3_APB3DIS                   RCC_CFGR3_APB3DIS_Msk
#define RCC_PLL1CFGR_PLL1SRC_Pos            (0UL)
#define RCC_PLL1CFGR_PLL1SRC_Msk            (0x3UL << RCC_PLL1CFGR_PLL1SRC_Pos)
#define RCC_PLL1CFGR_PLL1SRC                RCC_PLL1CFGR_PLL1SRC_Msk
#define RCC_PLL1CFGR_PLL1SRC_0              (0x1UL << RCC_PLL1CFGR_PLL1SRC_Pos)
#define RCC_PLL1CFGR_PLL1SRC_1              (0x2UL << RCC_PLL1CFGR_PLL1SRC_Pos)
#define RCC_PLL1CFGR_PLL1RGE_Pos            (2UL)
#define RCC_PLL1CFGR_PLL1RGE_Msk            (0x3UL << RCC_PLL1CFGR_PLL1RGE_Pos)
#define RCC_PLL1CFGR_PLL1RGE                RCC_PLL1CFGR_PLL1RGE_Msk
#define RCC_PLL1CFGR_PLL1RGE_0              (0x1UL << RCC_PLL1CFGR_PLL1RGE_Pos)
#define RCC_PLL1CFGR_PLL1RGE_1              (0x2UL << RCC_PLL1CFGR_PLL1RGE_Pos)
#define RCC_PLL1CFGR_PLL1FRACEN_Pos         (4UL)
#define RCC_PLL1CFGR_PLL1FRACEN_Msk         (0x1UL << RCC_PLL1CFGR_PLL1FRACEN_Pos)
#define RCC_PLL1CFGR_PLL1FRACEN             RCC_PLL1CFGR_PLL1FRACEN_Msk
#define RCC_PLL1CFGR_PLL1M_Pos              (8UL)
#define RCC_PLL1CFGR_PLL1M_Msk              (0xFUL << RCC_PLL1CFGR_PLL1M_Pos)
#define RCC_PLL1CFGR_PLL1M                  RCC_PLL1CFGR_PLL1M_Msk
#define RCC_PLL1CFGR_PLL1M_0                (0x01UL << RCC_PLL1CFGR_PLL1M_Pos)
#define RCC_PLL1CFGR_PLL1M_1                (0x02UL << RCC_PLL1CFGR_PLL1M_Pos)
#define RCC_PLL1CFGR_PLL1M_2                (0x04UL << RCC_PLL1CFGR_PLL1M_Pos)
#define RCC_PLL1CFGR_PLL1M_3                (0x08UL << RCC_PLL1CFGR_PLL1M_Pos)
#define RCC_PLL1CFGR_PLL1MBOOST_Pos         (12UL)
#define RCC_PLL1CFGR_PLL1MBOOST_Msk         (0xFUL << RCC_PLL1CFGR_PLL1MBOOST_Pos)
#define RCC_PLL1CFGR_PLL1MBOOST             RCC_PLL1CFGR_PLL1MBOOST_Msk
#define RCC_PLL1CFGR_PLL1MBOOST_0           (0x01UL << RCC_PLL1CFGR_PLL1MBOOST_Pos)
#define RCC_PLL1CFGR_PLL1MBOOST_1           (0x02UL << RCC_PLL1CFGR_PLL1MBOOST_Pos)
#define RCC_PLL1CFGR_PLL1MBOOST_2           (0x04UL << RCC_PLL1CFGR_PLL1MBOOST_Pos)
#define RCC_PLL1CFGR_PLL1MBOOST_3           (0x08UL << RCC_PLL1CFGR_PLL1MBOOST_Pos)
#define RCC_PLL1CFGR_PLL1PEN_Pos            (16UL)
#define RCC_PLL1CFGR_PLL1PEN_Msk            (0x1UL << RCC_PLL1CFGR_PLL1PEN_Pos)
#define RCC_PLL1CFGR_PLL1PEN                RCC_PLL1CFGR_PLL1PEN_Msk
#define RCC_PLL1CFGR_PLL1QEN_Pos            (17UL)
#define RCC_PLL1CFGR_PLL1QEN_Msk            (0x1UL << RCC_PLL1CFGR_PLL1QEN_Pos)
#define RCC_PLL1CFGR_PLL1QEN                RCC_PLL1CFGR_PLL1QEN_Msk
#define RCC_PLL1CFGR_PLL1REN_Pos            (18UL)
#define RCC_PLL1CFGR_PLL1REN_Msk            (0x1UL << RCC_PLL1CFGR_PLL1REN_Pos)
#define RCC_PLL1CFGR_PLL1REN                RCC_PLL1CFGR_PLL1REN_Msk
#define RCC_PLL2CFGR_PLL2SRC_Pos            (0UL)
#define RCC_PLL2CFGR_PLL2SRC_Msk            (0x3UL << RCC_PLL2CFGR_PLL2SRC_Pos)
#define RCC_PLL2CFGR_PLL2SRC                RCC_PLL2CFGR_PLL2SRC_Msk
#define RCC_PLL2CFGR_PLL2SRC_0              (0x1UL << RCC_PLL2CFGR_PLL2SRC_Pos)
#define RCC_PLL2CFGR_PLL2SRC_1              (0x2UL << RCC_PLL2CFGR_PLL2SRC_Pos)
#define RCC_PLL2CFGR_PLL2RGE_Pos            (2UL)
#define RCC_PLL2CFGR_PLL2RGE_Msk            (0x3UL << RCC_PLL2CFGR_PLL2RGE_Pos)
#define RCC_PLL2CFGR_PLL2RGE                RCC_PLL2CFGR_PLL2RGE_Msk
#define RCC_PLL2CFGR_PLL2RGE_0              (0x1UL << RCC_PLL2CFGR_PLL2RGE_Pos)
#define RCC_PLL2CFGR_PLL2RGE_1              (0x2UL << RCC_PLL2CFGR_PLL2RGE_Pos)
#define RCC_PLL2CFGR_PLL2FRACEN_Pos         (4UL)
#define RCC_PLL2CFGR_PLL2FRACEN_Msk         (0x1UL << RCC_PLL2CFGR_PLL2FRACEN_Pos)
#define RCC_PLL2CFGR_PLL2FRACEN             RCC_PLL2CFGR_PLL2FRACEN_Msk
#define RCC_PLL2CFGR_PLL2M_Pos              (8UL)
#define RCC_PLL2CFGR_PLL2M_Msk              (0xFUL << RCC_PLL2CFGR_PLL2M_Pos)
#define RCC_PLL2CFGR_PLL2M                  RCC_PLL2CFGR_PLL2M_Msk
#define RCC_PLL2CFGR_PLL2M_0                (0x01UL << RCC_PLL2CFGR_PLL2M_Pos)
#define RCC_PLL2CFGR_PLL2M_1                (0x02UL << RCC_PLL2CFGR_PLL2M_Pos)
#define RCC_PLL2CFGR_PLL2M_2                (0x04UL << RCC_PLL2CFGR_PLL2M_Pos)
#define RCC_PLL2CFGR_PLL2M_3                (0x08UL << RCC_PLL2CFGR_PLL2M_Pos)
#define RCC_PLL2CFGR_PLL2PEN_Pos            (16UL)
#define RCC_PLL2CFGR_PLL2PEN_Msk            (0x1UL << RCC_PLL2CFGR_PLL2PEN_Pos)
#define RCC_PLL2CFGR_PLL2PEN                RCC_PLL2CFGR_PLL2PEN_Msk
#define RCC_PLL2CFGR_PLL2QEN_Pos            (17UL)
#define RCC_PLL2CFGR_PLL2QEN_Msk            (0x1UL << RCC_PLL2CFGR_PLL2QEN_Pos)
#define RCC_PLL2CFGR_PLL2QEN                RCC_PLL2CFGR_PLL2QEN_Msk
#define RCC_PLL2CFGR_PLL2REN_Pos            (18UL)
#define RCC_PLL2CFGR_PLL2REN_Msk            (0x1UL << RCC_PLL2CFGR_PLL2REN_Pos)
#define RCC_PLL2CFGR_PLL2REN                RCC_PLL2CFGR_PLL2REN_Msk
#define RCC_PLL3CFGR_PLL3SRC_Pos            (0UL)
#define RCC_PLL3CFGR_PLL3SRC_Msk            (0x3UL << RCC_PLL3CFGR_PLL3SRC_Pos)
#define RCC_PLL3CFGR_PLL3SRC                RCC_PLL3CFGR_PLL3SRC_Msk
#define RCC_PLL3CFGR_PLL3SRC_0              (0x1UL << RCC_PLL3CFGR_PLL3SRC_Pos)
#define RCC_PLL3CFGR_PLL3SRC_1              (0x2UL << RCC_PLL3CFGR_PLL3SRC_Pos)
#define RCC_PLL3CFGR_PLL3RGE_Pos            (2UL)
#define RCC_PLL3CFGR_PLL3RGE_Msk            (0x3UL << RCC_PLL3CFGR_PLL3RGE_Pos)
#define RCC_PLL3CFGR_PLL3RGE                RCC_PLL3CFGR_PLL3RGE_Msk
#define RCC_PLL3CFGR_PLL3RGE_0              (0x1UL << RCC_PLL3CFGR_PLL3RGE_Pos)
#define RCC_PLL3CFGR_PLL3RGE_1              (0x2UL << RCC_PLL3CFGR_PLL3RGE_Pos)
#define RCC_PLL3CFGR_PLL3FRACEN_Pos         (4UL)
#define RCC_PLL3CFGR_PLL3FRACEN_Msk         (0x1UL << RCC_PLL3CFGR_PLL3FRACEN_Pos)
#define RCC_PLL3CFGR_PLL3FRACEN             RCC_PLL3CFGR_PLL3FRACEN_Msk
#define RCC_PLL3CFGR_PLL3M_Pos              (8UL)
#define RCC_PLL3CFGR_PLL3M_Msk              (0xFUL << RCC_PLL3CFGR_PLL3M_Pos)
#define RCC_PLL3CFGR_PLL3M                  RCC_PLL3CFGR_PLL3M_Msk
#define RCC_PLL3CFGR_PLL3M_0                (0x01UL << RCC_PLL3CFGR_PLL3M_Pos)
#define RCC_PLL3CFGR_PLL3M_1                (0x02UL << RCC_PLL3CFGR_PLL3M_Pos)
#define RCC_PLL3CFGR_PLL3M_2                (0x04UL << RCC_PLL3CFGR_PLL3M_Pos)
#define RCC_PLL3CFGR_PLL3M_3                (0x08UL << RCC_PLL3CFGR_PLL3M_Pos)
#define RCC_PLL3CFGR_PLL3PEN_Pos            (16UL)
#define RCC_PLL3CFGR_PLL3PEN_Msk            (0x1UL << RCC_PLL3CFGR_PLL3PEN_Pos)
#define RCC_PLL3CFGR_PLL3PEN                RCC_PLL3CFGR_PLL3PEN_Msk
#define RCC_PLL3CFGR_PLL3QEN_Pos            (17UL)
#define RCC_PLL3CFGR_PLL3QEN_Msk            (0x1UL << RCC_PLL3CFGR_PLL3QEN_Pos)
#define RCC_PLL3CFGR_PLL3QEN                RCC_PLL3CFGR_PLL3QEN_Msk
#define RCC_PLL3CFGR_PLL3REN_Pos            (18UL)
#define RCC_PLL3CFGR_PLL3REN_Msk            (0x1UL << RCC_PLL3CFGR_PLL3REN_Pos)
#define RCC_PLL3CFGR_PLL3REN                RCC_PLL3CFGR_PLL3REN_Msk
#define RCC_PLL1DIVR_PLL1N_Pos              (0UL)
#define RCC_PLL1DIVR_PLL1N_Msk              (0x1FFUL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N                  RCC_PLL1DIVR_PLL1N_Msk
#define RCC_PLL1DIVR_PLL1N_0                (0x001UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_1                (0x002UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_2                (0x004UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_3                (0x008UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_4                (0x010UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_5                (0x020UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_6                (0x040UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_7                (0x080UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1N_8                (0x100UL << RCC_PLL1DIVR_PLL1N_Pos)
#define RCC_PLL1DIVR_PLL1P_Pos              (9UL)
#define RCC_PLL1DIVR_PLL1P_Msk              (0x7FUL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P                  RCC_PLL1DIVR_PLL1P_Msk
#define RCC_PLL1DIVR_PLL1P_0                (0x001UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P_1                (0x002UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P_2                (0x004UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P_3                (0x008UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P_4                (0x010UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P_5                (0x020UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1P_6                (0x040UL << RCC_PLL1DIVR_PLL1P_Pos)
#define RCC_PLL1DIVR_PLL1Q_Pos              (16UL)
#define RCC_PLL1DIVR_PLL1Q_Msk              (0x7FUL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q                  RCC_PLL1DIVR_PLL1Q_Msk
#define RCC_PLL1DIVR_PLL1Q_0                (0x001UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q_1                (0x002UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q_2                (0x004UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q_3                (0x008UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q_4                (0x010UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q_5                (0x020UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1Q_6                (0x040UL << RCC_PLL1DIVR_PLL1Q_Pos)
#define RCC_PLL1DIVR_PLL1R_Pos              (24UL)
#define RCC_PLL1DIVR_PLL1R_Msk              (0x7FUL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R                  RCC_PLL1DIVR_PLL1R_Msk
#define RCC_PLL1DIVR_PLL1R_0                (0x001UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R_1                (0x002UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R_2                (0x004UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R_3                (0x008UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R_4                (0x010UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R_5                (0x020UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1DIVR_PLL1R_6                (0x040UL << RCC_PLL1DIVR_PLL1R_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_Pos         (3UL)
#define RCC_PLL1FRACR_PLL1FRACN_Msk         (0x1FFFUL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN             RCC_PLL1FRACR_PLL1FRACN_Msk
#define RCC_PLL1FRACR_PLL1FRACN_0           (0x0001UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_1           (0x0002UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_2           (0x0004UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_3           (0x0008UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_4           (0x0010UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_5           (0x0020UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_6           (0x0040UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_7           (0x0080UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_8           (0x0100UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_9           (0x0200UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_10          (0x0400UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_11          (0x0800UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL1FRACR_PLL1FRACN_12          (0x1000UL << RCC_PLL1FRACR_PLL1FRACN_Pos)
#define RCC_PLL2DIVR_PLL2N_Pos              (0UL)
#define RCC_PLL2DIVR_PLL2N_Msk              (0x1FFUL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N                  RCC_PLL2DIVR_PLL2N_Msk
#define RCC_PLL2DIVR_PLL2N_0                (0x001UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_1                (0x002UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_2                (0x004UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_3                (0x008UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_4                (0x010UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_5                (0x020UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_6                (0x040UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_7                (0x080UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2N_8                (0x100UL << RCC_PLL2DIVR_PLL2N_Pos)
#define RCC_PLL2DIVR_PLL2P_Pos              (9UL)
#define RCC_PLL2DIVR_PLL2P_Msk              (0x7FUL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P                  RCC_PLL2DIVR_PLL2P_Msk
#define RCC_PLL2DIVR_PLL2P_0                (0x001UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P_1                (0x002UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P_2                (0x004UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P_3                (0x008UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P_4                (0x010UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P_5                (0x020UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2P_6                (0x040UL << RCC_PLL2DIVR_PLL2P_Pos)
#define RCC_PLL2DIVR_PLL2Q_Pos              (16UL)
#define RCC_PLL2DIVR_PLL2Q_Msk              (0x7FUL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q                  RCC_PLL2DIVR_PLL2Q_Msk
#define RCC_PLL2DIVR_PLL2Q_0                (0x001UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q_1                (0x002UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q_2                (0x004UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q_3                (0x008UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q_4                (0x010UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q_5                (0x020UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2Q_6                (0x040UL << RCC_PLL2DIVR_PLL2Q_Pos)
#define RCC_PLL2DIVR_PLL2R_Pos              (24UL)
#define RCC_PLL2DIVR_PLL2R_Msk              (0x7FUL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R                  RCC_PLL2DIVR_PLL2R_Msk
#define RCC_PLL2DIVR_PLL2R_0                (0x001UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R_1                (0x002UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R_2                (0x004UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R_3                (0x008UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R_4                (0x010UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R_5                (0x020UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2DIVR_PLL2R_6                (0x040UL << RCC_PLL2DIVR_PLL2R_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_Pos         (3UL)
#define RCC_PLL2FRACR_PLL2FRACN_Msk         (0x1FFFUL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN             RCC_PLL2FRACR_PLL2FRACN_Msk
#define RCC_PLL2FRACR_PLL2FRACN_0           (0x0001UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_1           (0x0002UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_2           (0x0004UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_3           (0x0008UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_4           (0x0010UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_5           (0x0020UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_6           (0x0040UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_7           (0x0080UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_8           (0x0100UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_9           (0x0200UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_10          (0x0400UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_11          (0x0800UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL2FRACR_PLL2FRACN_12          (0x1000UL << RCC_PLL2FRACR_PLL2FRACN_Pos)
#define RCC_PLL3DIVR_PLL3N_Pos              (0UL)
#define RCC_PLL3DIVR_PLL3N_Msk              (0x1FFUL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N                  RCC_PLL3DIVR_PLL3N_Msk
#define RCC_PLL3DIVR_PLL3N_0                (0x001UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_1                (0x002UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_2                (0x004UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_3                (0x008UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_4                (0x010UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_5                (0x020UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_6                (0x040UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_7                (0x080UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3N_8                (0x100UL << RCC_PLL3DIVR_PLL3N_Pos)
#define RCC_PLL3DIVR_PLL3P_Pos              (9UL)
#define RCC_PLL3DIVR_PLL3P_Msk              (0x7FUL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P                  RCC_PLL3DIVR_PLL3P_Msk
#define RCC_PLL3DIVR_PLL3P_0                (0x001UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P_1                (0x002UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P_2                (0x004UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P_3                (0x008UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P_4                (0x010UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P_5                (0x020UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3P_6                (0x040UL << RCC_PLL3DIVR_PLL3P_Pos)
#define RCC_PLL3DIVR_PLL3Q_Pos              (16UL)
#define RCC_PLL3DIVR_PLL3Q_Msk              (0x7FUL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q                  RCC_PLL3DIVR_PLL3Q_Msk
#define RCC_PLL3DIVR_PLL3Q_0                (0x001UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q_1                (0x002UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q_2                (0x004UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q_3                (0x008UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q_4                (0x010UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q_5                (0x020UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3Q_6                (0x040UL << RCC_PLL3DIVR_PLL3Q_Pos)
#define RCC_PLL3DIVR_PLL3R_Pos              (24UL)
#define RCC_PLL3DIVR_PLL3R_Msk              (0x7FUL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R                  RCC_PLL3DIVR_PLL3R_Msk
#define RCC_PLL3DIVR_PLL3R_0                (0x001UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R_1                (0x002UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R_2                (0x004UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R_3                (0x008UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R_4                (0x010UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R_5                (0x020UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3DIVR_PLL3R_6                (0x040UL << RCC_PLL3DIVR_PLL3R_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_Pos         (3UL)
#define RCC_PLL3FRACR_PLL3FRACN_Msk         (0x1FFFUL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN             RCC_PLL3FRACR_PLL3FRACN_Msk
#define RCC_PLL3FRACR_PLL3FRACN_0           (0x0001UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_1           (0x0002UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_2           (0x0004UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_3           (0x0008UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_4           (0x0010UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_5           (0x0020UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_6           (0x0040UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_7           (0x0080UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_8           (0x0100UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_9           (0x0200UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_10          (0x0400UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_11          (0x0800UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_PLL3FRACR_PLL3FRACN_12          (0x1000UL << RCC_PLL3FRACR_PLL3FRACN_Pos)
#define RCC_CIER_LSIRDYIE_Pos               (0UL)
#define RCC_CIER_LSIRDYIE_Msk               (0x1UL << RCC_CIER_LSIRDYIE_Pos)
#define RCC_CIER_LSIRDYIE                   RCC_CIER_LSIRDYIE_Msk
#define RCC_CIER_LSERDYIE_Pos               (1UL)
#define RCC_CIER_LSERDYIE_Msk               (0x1UL << RCC_CIER_LSERDYIE_Pos)
#define RCC_CIER_LSERDYIE                   RCC_CIER_LSERDYIE_Msk
#define RCC_CIER_MSISRDYIE_Pos              (2UL)
#define RCC_CIER_MSISRDYIE_Msk              (0x1UL << RCC_CIER_MSISRDYIE_Pos)
#define RCC_CIER_MSISRDYIE                  RCC_CIER_MSISRDYIE_Msk
#define RCC_CIER_HSIRDYIE_Pos               (3UL)
#define RCC_CIER_HSIRDYIE_Msk               (0x1UL << RCC_CIER_HSIRDYIE_Pos)
#define RCC_CIER_HSIRDYIE                   RCC_CIER_HSIRDYIE_Msk
#define RCC_CIER_HSERDYIE_Pos               (4UL)
#define RCC_CIER_HSERDYIE_Msk               (0x1UL << RCC_CIER_HSERDYIE_Pos)
#define RCC_CIER_HSERDYIE                   RCC_CIER_HSERDYIE_Msk
#define RCC_CIER_HSI48RDYIE_Pos             (5UL)
#define RCC_CIER_HSI48RDYIE_Msk             (0x1UL << RCC_CIER_HSI48RDYIE_Pos)
#define RCC_CIER_HSI48RDYIE                 RCC_CIER_HSI48RDYIE_Msk
#define RCC_CIER_PLL1RDYIE_Pos              (6UL)
#define RCC_CIER_PLL1RDYIE_Msk              (0x1UL << RCC_CIER_PLL1RDYIE_Pos)
#define RCC_CIER_PLL1RDYIE                  RCC_CIER_PLL1RDYIE_Msk
#define RCC_CIER_PLL2RDYIE_Pos              (7UL)
#define RCC_CIER_PLL2RDYIE_Msk              (0x1UL << RCC_CIER_PLL2RDYIE_Pos)
#define RCC_CIER_PLL2RDYIE                  RCC_CIER_PLL2RDYIE_Msk
#define RCC_CIER_PLL3RDYIE_Pos              (8UL)
#define RCC_CIER_PLL3RDYIE_Msk              (0x1UL << RCC_CIER_PLL3RDYIE_Pos)
#define RCC_CIER_PLL3RDYIE                  RCC_CIER_PLL3RDYIE_Msk
#define RCC_CIER_MSIKRDYIE_Pos              (11UL)
#define RCC_CIER_MSIKRDYIE_Msk              (0x1UL << RCC_CIER_MSIKRDYIE_Pos)
#define RCC_CIER_MSIKRDYIE                  RCC_CIER_MSIKRDYIE_Msk
#define RCC_CIER_SHSIRDYIE_Pos              (12UL)
#define RCC_CIER_SHSIRDYIE_Msk              (0x1UL << RCC_CIER_SHSIRDYIE_Pos)
#define RCC_CIER_SHSIRDYIE                  RCC_CIER_SHSIRDYIE_Msk
#define RCC_CIFR_LSIRDYF_Pos                (0UL)
#define RCC_CIFR_LSIRDYF_Msk                (0x1UL << RCC_CIFR_LSIRDYF_Pos)
#define RCC_CIFR_LSIRDYF                    RCC_CIFR_LSIRDYF_Msk
#define RCC_CIFR_LSERDYF_Pos                (1UL)
#define RCC_CIFR_LSERDYF_Msk                (0x1UL << RCC_CIFR_LSERDYF_Pos)
#define RCC_CIFR_LSERDYF                    RCC_CIFR_LSERDYF_Msk
#define RCC_CIFR_MSISRDYF_Pos               (2UL)
#define RCC_CIFR_MSISRDYF_Msk               (0x1UL << RCC_CIFR_MSISRDYF_Pos)
#define RCC_CIFR_MSISRDYF                   RCC_CIFR_MSISRDYF_Msk
#define RCC_CIFR_HSIRDYF_Pos                (3UL)
#define RCC_CIFR_HSIRDYF_Msk                (0x1UL << RCC_CIFR_HSIRDYF_Pos)
#define RCC_CIFR_HSIRDYF                    RCC_CIFR_HSIRDYF_Msk
#define RCC_CIFR_HSERDYF_Pos                (4UL)
#define RCC_CIFR_HSERDYF_Msk                (0x1UL << RCC_CIFR_HSERDYF_Pos)
#define RCC_CIFR_HSERDYF                    RCC_CIFR_HSERDYF_Msk
#define RCC_CIFR_HSI48RDYF_Pos              (5UL)
#define RCC_CIFR_HSI48RDYF_Msk              (0x1UL << RCC_CIFR_HSI48RDYF_Pos)
#define RCC_CIFR_HSI48RDYF                  RCC_CIFR_HSI48RDYF_Msk
#define RCC_CIFR_PLL1RDYF_Pos               (6UL)
#define RCC_CIFR_PLL1RDYF_Msk               (0x1UL << RCC_CIFR_PLL1RDYF_Pos)
#define RCC_CIFR_PLL1RDYF                   RCC_CIFR_PLL1RDYF_Msk
#define RCC_CIFR_PLL2RDYF_Pos               (7UL)
#define RCC_CIFR_PLL2RDYF_Msk               (0x1UL << RCC_CIFR_PLL2RDYF_Pos)
#define RCC_CIFR_PLL2RDYF                   RCC_CIFR_PLL2RDYF_Msk
#define RCC_CIFR_PLL3RDYF_Pos               (8UL)
#define RCC_CIFR_PLL3RDYF_Msk               (0x1UL << RCC_CIFR_PLL3RDYF_Pos)
#define RCC_CIFR_PLL3RDYF                   RCC_CIFR_PLL3RDYF_Msk
#define RCC_CIFR_CSSF_Pos                   (10UL)
#define RCC_CIFR_CSSF_Msk                   (0x1UL << RCC_CIFR_CSSF_Pos)
#define RCC_CIFR_CSSF                       RCC_CIFR_CSSF_Msk
#define RCC_CIFR_MSIKRDYF_Pos               (11UL)
#define RCC_CIFR_MSIKRDYF_Msk               (0x1UL << RCC_CIFR_MSIKRDYF_Pos)
#define RCC_CIFR_MSIKRDYF                   RCC_CIFR_MSIKRDYF_Msk
#define RCC_CIFR_SHSIRDYF_Pos               (12UL)
#define RCC_CIFR_SHSIRDYF_Msk               (0x1UL << RCC_CIFR_SHSIRDYF_Pos)
#define RCC_CIFR_SHSIRDYF                   RCC_CIFR_SHSIRDYF_Msk
#define RCC_CICR_LSIRDYC_Pos                (0UL)
#define RCC_CICR_LSIRDYC_Msk                (0x1UL << RCC_CICR_LSIRDYC_Pos)
#define RCC_CICR_LSIRDYC                    RCC_CICR_LSIRDYC_Msk
#define RCC_CICR_LSERDYC_Pos                (1UL)
#define RCC_CICR_LSERDYC_Msk                (0x1UL << RCC_CICR_LSERDYC_Pos)
#define RCC_CICR_LSERDYC                    RCC_CICR_LSERDYC_Msk
#define RCC_CICR_MSISRDYC_Pos               (2UL)
#define RCC_CICR_MSISRDYC_Msk               (0x1UL << RCC_CICR_MSISRDYC_Pos)
#define RCC_CICR_MSISRDYC                   RCC_CICR_MSISRDYC_Msk
#define RCC_CICR_HSIRDYC_Pos                (3UL)
#define RCC_CICR_HSIRDYC_Msk                (0x1UL << RCC_CICR_HSIRDYC_Pos)
#define RCC_CICR_HSIRDYC                    RCC_CICR_HSIRDYC_Msk
#define RCC_CICR_HSERDYC_Pos                (4UL)
#define RCC_CICR_HSERDYC_Msk                (0x1UL << RCC_CICR_HSERDYC_Pos)
#define RCC_CICR_HSERDYC                    RCC_CICR_HSERDYC_Msk
#define RCC_CICR_HSI48RDYC_Pos              (5UL)
#define RCC_CICR_HSI48RDYC_Msk              (0x1UL << RCC_CICR_HSI48RDYC_Pos)
#define RCC_CICR_HSI48RDYC                  RCC_CICR_HSI48RDYC_Msk
#define RCC_CICR_PLL1RDYC_Pos               (6UL)
#define RCC_CICR_PLL1RDYC_Msk               (0x1UL << RCC_CICR_PLL1RDYC_Pos)
#define RCC_CICR_PLL1RDYC                   RCC_CICR_PLL1RDYC_Msk
#define RCC_CICR_PLL2RDYC_Pos               (7UL)
#define RCC_CICR_PLL2RDYC_Msk               (0x1UL << RCC_CICR_PLL2RDYC_Pos)
#define RCC_CICR_PLL2RDYC                   RCC_CICR_PLL2RDYC_Msk
#define RCC_CICR_PLL3RDYC_Pos               (8UL)
#define RCC_CICR_PLL3RDYC_Msk               (0x1UL << RCC_CICR_PLL3RDYC_Pos)
#define RCC_CICR_PLL3RDYC                   RCC_CICR_PLL3RDYC_Msk
#define RCC_CICR_CSSC_Pos                   (10UL)
#define RCC_CICR_CSSC_Msk                   (0x1UL << RCC_CICR_CSSC_Pos)
#define RCC_CICR_CSSC                       RCC_CICR_CSSC_Msk
#define RCC_CICR_MSIKRDYC_Pos               (11UL)
#define RCC_CICR_MSIKRDYC_Msk               (0x1UL << RCC_CICR_MSIKRDYC_Pos)
#define RCC_CICR_MSIKRDYC                   RCC_CICR_MSIKRDYC_Msk
#define RCC_CICR_SHSIRDYC_Pos               (12UL)
#define RCC_CICR_SHSIRDYC_Msk               (0x1UL << RCC_CICR_SHSIRDYC_Pos)
#define RCC_CICR_SHSIRDYC                   RCC_CICR_SHSIRDYC_Msk
#define RCC_AHB1RSTR_GPDMA1RST_Pos          (0UL)
#define RCC_AHB1RSTR_GPDMA1RST_Msk          (0x1UL << RCC_AHB1RSTR_GPDMA1RST_Pos)
#define RCC_AHB1RSTR_GPDMA1RST              RCC_AHB1RSTR_GPDMA1RST_Msk
#define RCC_AHB1RSTR_CORDICRST_Pos          (1UL)
#define RCC_AHB1RSTR_CORDICRST_Msk          (0x1UL << RCC_AHB1RSTR_CORDICRST_Pos)
#define RCC_AHB1RSTR_CORDICRST              RCC_AHB1RSTR_CORDICRST_Msk
#define RCC_AHB1RSTR_FMACRST_Pos            (2UL)
#define RCC_AHB1RSTR_FMACRST_Msk            (0x1UL << RCC_AHB1RSTR_FMACRST_Pos)
#define RCC_AHB1RSTR_FMACRST                RCC_AHB1RSTR_FMACRST_Msk
#define RCC_AHB1RSTR_MDF1RST_Pos            (3UL)
#define RCC_AHB1RSTR_MDF1RST_Msk            (0x1UL << RCC_AHB1RSTR_MDF1RST_Pos)
#define RCC_AHB1RSTR_MDF1RST                RCC_AHB1RSTR_MDF1RST_Msk
#define RCC_AHB1RSTR_CRCRST_Pos             (12UL)
#define RCC_AHB1RSTR_CRCRST_Msk             (0x1UL << RCC_AHB1RSTR_CRCRST_Pos)
#define RCC_AHB1RSTR_CRCRST                 RCC_AHB1RSTR_CRCRST_Msk
#define RCC_AHB1RSTR_TSCRST_Pos             (16UL)
#define RCC_AHB1RSTR_TSCRST_Msk             (0x1UL << RCC_AHB1RSTR_TSCRST_Pos)
#define RCC_AHB1RSTR_TSCRST                 RCC_AHB1RSTR_TSCRST_Msk
#define RCC_AHB1RSTR_RAMCFGRST_Pos          (17UL)
#define RCC_AHB1RSTR_RAMCFGRST_Msk          (0x1UL << RCC_AHB1RSTR_RAMCFGRST_Pos)
#define RCC_AHB1RSTR_RAMCFGRST              RCC_AHB1RSTR_RAMCFGRST_Msk
#define RCC_AHB1RSTR_DMA2DRST_Pos           (18UL)
#define RCC_AHB1RSTR_DMA2DRST_Msk           (0x1UL << RCC_AHB1RSTR_DMA2DRST_Pos)
#define RCC_AHB1RSTR_DMA2DRST               RCC_AHB1RSTR_DMA2DRST_Msk
#define RCC_AHB2RSTR1_GPIOARST_Pos          (0UL)
#define RCC_AHB2RSTR1_GPIOARST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOARST_Pos)
#define RCC_AHB2RSTR1_GPIOARST              RCC_AHB2RSTR1_GPIOARST_Msk
#define RCC_AHB2RSTR1_GPIOBRST_Pos          (1UL)
#define RCC_AHB2RSTR1_GPIOBRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOBRST_Pos)
#define RCC_AHB2RSTR1_GPIOBRST              RCC_AHB2RSTR1_GPIOBRST_Msk
#define RCC_AHB2RSTR1_GPIOCRST_Pos          (2UL)
#define RCC_AHB2RSTR1_GPIOCRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOCRST_Pos)
#define RCC_AHB2RSTR1_GPIOCRST              RCC_AHB2RSTR1_GPIOCRST_Msk
#define RCC_AHB2RSTR1_GPIODRST_Pos          (3UL)
#define RCC_AHB2RSTR1_GPIODRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIODRST_Pos)
#define RCC_AHB2RSTR1_GPIODRST              RCC_AHB2RSTR1_GPIODRST_Msk
#define RCC_AHB2RSTR1_GPIOERST_Pos          (4UL)
#define RCC_AHB2RSTR1_GPIOERST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOERST_Pos)
#define RCC_AHB2RSTR1_GPIOERST              RCC_AHB2RSTR1_GPIOERST_Msk
#define RCC_AHB2RSTR1_GPIOFRST_Pos          (5UL)
#define RCC_AHB2RSTR1_GPIOFRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOFRST_Pos)
#define RCC_AHB2RSTR1_GPIOFRST              RCC_AHB2RSTR1_GPIOFRST_Msk
#define RCC_AHB2RSTR1_GPIOGRST_Pos          (6UL)
#define RCC_AHB2RSTR1_GPIOGRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOGRST_Pos)
#define RCC_AHB2RSTR1_GPIOGRST              RCC_AHB2RSTR1_GPIOGRST_Msk
#define RCC_AHB2RSTR1_GPIOHRST_Pos          (7UL)
#define RCC_AHB2RSTR1_GPIOHRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOHRST_Pos)
#define RCC_AHB2RSTR1_GPIOHRST              RCC_AHB2RSTR1_GPIOHRST_Msk
#define RCC_AHB2RSTR1_GPIOIRST_Pos          (8UL)
#define RCC_AHB2RSTR1_GPIOIRST_Msk          (0x1UL << RCC_AHB2RSTR1_GPIOIRST_Pos)
#define RCC_AHB2RSTR1_GPIOIRST              RCC_AHB2RSTR1_GPIOIRST_Msk
#define RCC_AHB2RSTR1_ADC12RST_Pos           (10UL)
#define RCC_AHB2RSTR1_ADC12RST_Msk           (0x1UL << RCC_AHB2RSTR1_ADC12RST_Pos)
#define RCC_AHB2RSTR1_ADC12RST               RCC_AHB2RSTR1_ADC12RST_Msk
#define RCC_AHB2RSTR1_DCMI_PSSIRST_Pos      (12UL)
#define RCC_AHB2RSTR1_DCMI_PSSIRST_Msk      (0x1UL << RCC_AHB2RSTR1_DCMI_PSSIRST_Pos)
#define RCC_AHB2RSTR1_DCMI_PSSIRST          RCC_AHB2RSTR1_DCMI_PSSIRST_Msk
#define RCC_AHB2RSTR1_OTGRST_Pos            (14UL)
#define RCC_AHB2RSTR1_OTGRST_Msk            (0x1UL << RCC_AHB2RSTR1_OTGRST_Pos)
#define RCC_AHB2RSTR1_OTGRST                RCC_AHB2RSTR1_OTGRST_Msk
#define RCC_AHB2RSTR1_AESRST_Pos            (16UL)
#define RCC_AHB2RSTR1_AESRST_Msk            (0x1UL << RCC_AHB2RSTR1_AESRST_Pos)
#define RCC_AHB2RSTR1_AESRST                RCC_AHB2RSTR1_AESRST_Msk
#define RCC_AHB2RSTR1_HASHRST_Pos           (17UL)
#define RCC_AHB2RSTR1_HASHRST_Msk           (0x1UL << RCC_AHB2RSTR1_HASHRST_Pos)
#define RCC_AHB2RSTR1_HASHRST               RCC_AHB2RSTR1_HASHRST_Msk
#define RCC_AHB2RSTR1_RNGRST_Pos            (18UL)
#define RCC_AHB2RSTR1_RNGRST_Msk            (0x1UL << RCC_AHB2RSTR1_RNGRST_Pos)
#define RCC_AHB2RSTR1_RNGRST                RCC_AHB2RSTR1_RNGRST_Msk
#define RCC_AHB2RSTR1_PKARST_Pos            (19UL)
#define RCC_AHB2RSTR1_PKARST_Msk            (0x1UL << RCC_AHB2RSTR1_PKARST_Pos)
#define RCC_AHB2RSTR1_PKARST                RCC_AHB2RSTR1_PKARST_Msk
#define RCC_AHB2RSTR1_SAESRST_Pos           (20UL)
#define RCC_AHB2RSTR1_SAESRST_Msk           (0x1UL << RCC_AHB2RSTR1_SAESRST_Pos)
#define RCC_AHB2RSTR1_SAESRST               RCC_AHB2RSTR1_SAESRST_Msk
#define RCC_AHB2RSTR1_OCTOSPIMRST_Pos       (21UL)
#define RCC_AHB2RSTR1_OCTOSPIMRST_Msk       (0x1UL << RCC_AHB2RSTR1_OCTOSPIMRST_Pos)
#define RCC_AHB2RSTR1_OCTOSPIMRST           RCC_AHB2RSTR1_OCTOSPIMRST_Msk
#define RCC_AHB2RSTR1_OTFDEC1RST_Pos        (23UL)
#define RCC_AHB2RSTR1_OTFDEC1RST_Msk        (0x1UL << RCC_AHB2RSTR1_OTFDEC1RST_Pos)
#define RCC_AHB2RSTR1_OTFDEC1RST            RCC_AHB2RSTR1_OTFDEC1RST_Msk
#define RCC_AHB2RSTR1_OTFDEC2RST_Pos        (24UL)
#define RCC_AHB2RSTR1_OTFDEC2RST_Msk        (0x1UL << RCC_AHB2RSTR1_OTFDEC2RST_Pos)
#define RCC_AHB2RSTR1_OTFDEC2RST            RCC_AHB2RSTR1_OTFDEC2RST_Msk
#define RCC_AHB2RSTR1_SDMMC1RST_Pos         (27UL)
#define RCC_AHB2RSTR1_SDMMC1RST_Msk         (0x1UL << RCC_AHB2RSTR1_SDMMC1RST_Pos)
#define RCC_AHB2RSTR1_SDMMC1RST             RCC_AHB2RSTR1_SDMMC1RST_Msk
#define RCC_AHB2RSTR1_SDMMC2RST_Pos         (28UL)
#define RCC_AHB2RSTR1_SDMMC2RST_Msk         (0x1UL << RCC_AHB2RSTR1_SDMMC2RST_Pos)
#define RCC_AHB2RSTR1_SDMMC2RST             RCC_AHB2RSTR1_SDMMC2RST_Msk
#define RCC_AHB2RSTR2_FSMCRST_Pos           (0UL)
#define RCC_AHB2RSTR2_FSMCRST_Msk           (0x1UL << RCC_AHB2RSTR2_FSMCRST_Pos)
#define RCC_AHB2RSTR2_FSMCRST               RCC_AHB2RSTR2_FSMCRST_Msk
#define RCC_AHB2RSTR2_OCTOSPI1RST_Pos       (4UL)
#define RCC_AHB2RSTR2_OCTOSPI1RST_Msk       (0x1UL << RCC_AHB2RSTR2_OCTOSPI1RST_Pos)
#define RCC_AHB2RSTR2_OCTOSPI1RST           RCC_AHB2RSTR2_OCTOSPI1RST_Msk
#define RCC_AHB2RSTR2_OCTOSPI2RST_Pos       (8UL)
#define RCC_AHB2RSTR2_OCTOSPI2RST_Msk       (0x1UL << RCC_AHB2RSTR2_OCTOSPI2RST_Pos)
#define RCC_AHB2RSTR2_OCTOSPI2RST           RCC_AHB2RSTR2_OCTOSPI2RST_Msk
#define RCC_AHB3RSTR_LPGPIO1RST_Pos         (0UL)
#define RCC_AHB3RSTR_LPGPIO1RST_Msk         (0x1UL << RCC_AHB3RSTR_LPGPIO1RST_Pos)
#define RCC_AHB3RSTR_LPGPIO1RST             RCC_AHB3RSTR_LPGPIO1RST_Msk
#define RCC_AHB3RSTR_ADC4RST_Pos            (5UL)
#define RCC_AHB3RSTR_ADC4RST_Msk            (0x1UL << RCC_AHB3RSTR_ADC4RST_Pos)
#define RCC_AHB3RSTR_ADC4RST                RCC_AHB3RSTR_ADC4RST_Msk
#define RCC_AHB3RSTR_DAC1RST_Pos            (6UL)
#define RCC_AHB3RSTR_DAC1RST_Msk            (0x1UL << RCC_AHB3RSTR_DAC1RST_Pos)
#define RCC_AHB3RSTR_DAC1RST                RCC_AHB3RSTR_DAC1RST_Msk
#define RCC_AHB3RSTR_LPDMA1RST_Pos          (9UL)
#define RCC_AHB3RSTR_LPDMA1RST_Msk          (0x1UL << RCC_AHB3RSTR_LPDMA1RST_Pos)
#define RCC_AHB3RSTR_LPDMA1RST              RCC_AHB3RSTR_LPDMA1RST_Msk
#define RCC_AHB3RSTR_ADF1RST_Pos            (10UL)
#define RCC_AHB3RSTR_ADF1RST_Msk            (0x1UL << RCC_AHB3RSTR_ADF1RST_Pos)
#define RCC_AHB3RSTR_ADF1RST                RCC_AHB3RSTR_ADF1RST_Msk
#define RCC_APB1RSTR1_TIM2RST_Pos           (0UL)
#define RCC_APB1RSTR1_TIM2RST_Msk           (0x1UL << RCC_APB1RSTR1_TIM2RST_Pos)
#define RCC_APB1RSTR1_TIM2RST               RCC_APB1RSTR1_TIM2RST_Msk
#define RCC_APB1RSTR1_TIM3RST_Pos           (1UL)
#define RCC_APB1RSTR1_TIM3RST_Msk           (0x1UL << RCC_APB1RSTR1_TIM3RST_Pos)
#define RCC_APB1RSTR1_TIM3RST               RCC_APB1RSTR1_TIM3RST_Msk
#define RCC_APB1RSTR1_TIM4RST_Pos           (2UL)
#define RCC_APB1RSTR1_TIM4RST_Msk           (0x1UL << RCC_APB1RSTR1_TIM4RST_Pos)
#define RCC_APB1RSTR1_TIM4RST               RCC_APB1RSTR1_TIM4RST_Msk
#define RCC_APB1RSTR1_TIM5RST_Pos           (3UL)
#define RCC_APB1RSTR1_TIM5RST_Msk           (0x1UL << RCC_APB1RSTR1_TIM5RST_Pos)
#define RCC_APB1RSTR1_TIM5RST               RCC_APB1RSTR1_TIM5RST_Msk
#define RCC_APB1RSTR1_TIM6RST_Pos           (4UL)
#define RCC_APB1RSTR1_TIM6RST_Msk           (0x1UL << RCC_APB1RSTR1_TIM6RST_Pos)
#define RCC_APB1RSTR1_TIM6RST               RCC_APB1RSTR1_TIM6RST_Msk
#define RCC_APB1RSTR1_TIM7RST_Pos           (5UL)
#define RCC_APB1RSTR1_TIM7RST_Msk           (0x1UL << RCC_APB1RSTR1_TIM7RST_Pos)
#define RCC_APB1RSTR1_TIM7RST               RCC_APB1RSTR1_TIM7RST_Msk
#define RCC_APB1RSTR1_SPI2RST_Pos           (14UL)
#define RCC_APB1RSTR1_SPI2RST_Msk           (0x1UL << RCC_APB1RSTR1_SPI2RST_Pos)
#define RCC_APB1RSTR1_SPI2RST               RCC_APB1RSTR1_SPI2RST_Msk
#define RCC_APB1RSTR1_USART2RST_Pos         (17UL)
#define RCC_APB1RSTR1_USART2RST_Msk         (0x1UL << RCC_APB1RSTR1_USART2RST_Pos)
#define RCC_APB1RSTR1_USART2RST             RCC_APB1RSTR1_USART2RST_Msk
#define RCC_APB1RSTR1_USART3RST_Pos         (18UL)
#define RCC_APB1RSTR1_USART3RST_Msk         (0x1UL << RCC_APB1RSTR1_USART3RST_Pos)
#define RCC_APB1RSTR1_USART3RST             RCC_APB1RSTR1_USART3RST_Msk
#define RCC_APB1RSTR1_UART4RST_Pos          (19UL)
#define RCC_APB1RSTR1_UART4RST_Msk          (0x1UL << RCC_APB1RSTR1_UART4RST_Pos)
#define RCC_APB1RSTR1_UART4RST              RCC_APB1RSTR1_UART4RST_Msk
#define RCC_APB1RSTR1_UART5RST_Pos          (20UL)
#define RCC_APB1RSTR1_UART5RST_Msk          (0x1UL << RCC_APB1RSTR1_UART5RST_Pos)
#define RCC_APB1RSTR1_UART5RST              RCC_APB1RSTR1_UART5RST_Msk
#define RCC_APB1RSTR1_I2C1RST_Pos           (21UL)
#define RCC_APB1RSTR1_I2C1RST_Msk           (0x1UL << RCC_APB1RSTR1_I2C1RST_Pos)
#define RCC_APB1RSTR1_I2C1RST               RCC_APB1RSTR1_I2C1RST_Msk
#define RCC_APB1RSTR1_I2C2RST_Pos           (22UL)
#define RCC_APB1RSTR1_I2C2RST_Msk           (0x1UL << RCC_APB1RSTR1_I2C2RST_Pos)
#define RCC_APB1RSTR1_I2C2RST               RCC_APB1RSTR1_I2C2RST_Msk
#define RCC_APB1RSTR1_CRSRST_Pos            (24UL)
#define RCC_APB1RSTR1_CRSRST_Msk            (0x1UL << RCC_APB1RSTR1_CRSRST_Pos)
#define RCC_APB1RSTR1_CRSRST                RCC_APB1RSTR1_CRSRST_Msk
#define RCC_APB1RSTR2_I2C4RST_Pos           (1UL)
#define RCC_APB1RSTR2_I2C4RST_Msk           (0x1UL << RCC_APB1RSTR2_I2C4RST_Pos)
#define RCC_APB1RSTR2_I2C4RST               RCC_APB1RSTR2_I2C4RST_Msk
#define RCC_APB1RSTR2_LPTIM2RST_Pos         (5UL)
#define RCC_APB1RSTR2_LPTIM2RST_Msk         (0x1UL << RCC_APB1RSTR2_LPTIM2RST_Pos)
#define RCC_APB1RSTR2_LPTIM2RST             RCC_APB1RSTR2_LPTIM2RST_Msk
#define RCC_APB1RSTR2_FDCAN1RST_Pos         (9UL)
#define RCC_APB1RSTR2_FDCAN1RST_Msk         (0x1UL << RCC_APB1RSTR2_FDCAN1RST_Pos)
#define RCC_APB1RSTR2_FDCAN1RST             RCC_APB1RSTR2_FDCAN1RST_Msk
#define RCC_APB1RSTR2_UCPD1RST_Pos          (23UL)
#define RCC_APB1RSTR2_UCPD1RST_Msk          (0x1UL << RCC_APB1RSTR2_UCPD1RST_Pos)
#define RCC_APB1RSTR2_UCPD1RST              RCC_APB1RSTR2_UCPD1RST_Msk
#define RCC_APB2RSTR_TIM1RST_Pos            (11UL)
#define RCC_APB2RSTR_TIM1RST_Msk            (0x1UL << RCC_APB2RSTR_TIM1RST_Pos)
#define RCC_APB2RSTR_TIM1RST                RCC_APB2RSTR_TIM1RST_Msk
#define RCC_APB2RSTR_SPI1RST_Pos            (12UL)
#define RCC_APB2RSTR_SPI1RST_Msk            (0x1UL << RCC_APB2RSTR_SPI1RST_Pos)
#define RCC_APB2RSTR_SPI1RST                RCC_APB2RSTR_SPI1RST_Msk
#define RCC_APB2RSTR_TIM8RST_Pos            (13UL)
#define RCC_APB2RSTR_TIM8RST_Msk            (0x1UL << RCC_APB2RSTR_TIM8RST_Pos)
#define RCC_APB2RSTR_TIM8RST                RCC_APB2RSTR_TIM8RST_Msk
#define RCC_APB2RSTR_USART1RST_Pos          (14UL)
#define RCC_APB2RSTR_USART1RST_Msk          (0x1UL << RCC_APB2RSTR_USART1RST_Pos)
#define RCC_APB2RSTR_USART1RST              RCC_APB2RSTR_USART1RST_Msk
#define RCC_APB2RSTR_TIM15RST_Pos           (16UL)
#define RCC_APB2RSTR_TIM15RST_Msk           (0x1UL << RCC_APB2RSTR_TIM15RST_Pos)
#define RCC_APB2RSTR_TIM15RST               RCC_APB2RSTR_TIM15RST_Msk
#define RCC_APB2RSTR_TIM16RST_Pos           (17UL)
#define RCC_APB2RSTR_TIM16RST_Msk           (0x1UL << RCC_APB2RSTR_TIM16RST_Pos)
#define RCC_APB2RSTR_TIM16RST               RCC_APB2RSTR_TIM16RST_Msk
#define RCC_APB2RSTR_TIM17RST_Pos           (18UL)
#define RCC_APB2RSTR_TIM17RST_Msk           (0x1UL << RCC_APB2RSTR_TIM17RST_Pos)
#define RCC_APB2RSTR_TIM17RST               RCC_APB2RSTR_TIM17RST_Msk
#define RCC_APB2RSTR_SAI1RST_Pos            (21UL)
#define RCC_APB2RSTR_SAI1RST_Msk            (0x1UL << RCC_APB2RSTR_SAI1RST_Pos)
#define RCC_APB2RSTR_SAI1RST                RCC_APB2RSTR_SAI1RST_Msk
#define RCC_APB2RSTR_SAI2RST_Pos            (22UL)
#define RCC_APB2RSTR_SAI2RST_Msk            (0x1UL << RCC_APB2RSTR_SAI2RST_Pos)
#define RCC_APB2RSTR_SAI2RST                RCC_APB2RSTR_SAI2RST_Msk
#define RCC_APB3RSTR_SYSCFGRST_Pos          (1UL)
#define RCC_APB3RSTR_SYSCFGRST_Msk          (0x1UL << RCC_APB3RSTR_SYSCFGRST_Pos)
#define RCC_APB3RSTR_SYSCFGRST              RCC_APB3RSTR_SYSCFGRST_Msk
#define RCC_APB3RSTR_SPI3RST_Pos            (5UL)
#define RCC_APB3RSTR_SPI3RST_Msk            (0x1UL << RCC_APB3RSTR_SPI3RST_Pos)
#define RCC_APB3RSTR_SPI3RST                RCC_APB3RSTR_SPI3RST_Msk
#define RCC_APB3RSTR_LPUART1RST_Pos         (6UL)
#define RCC_APB3RSTR_LPUART1RST_Msk         (0x1UL << RCC_APB3RSTR_LPUART1RST_Pos)
#define RCC_APB3RSTR_LPUART1RST             RCC_APB3RSTR_LPUART1RST_Msk
#define RCC_APB3RSTR_I2C3RST_Pos            (7UL)
#define RCC_APB3RSTR_I2C3RST_Msk            (0x1UL << RCC_APB3RSTR_I2C3RST_Pos)
#define RCC_APB3RSTR_I2C3RST                RCC_APB3RSTR_I2C3RST_Msk
#define RCC_APB3RSTR_LPTIM1RST_Pos          (11UL)
#define RCC_APB3RSTR_LPTIM1RST_Msk          (0x1UL << RCC_APB3RSTR_LPTIM1RST_Pos)
#define RCC_APB3RSTR_LPTIM1RST              RCC_APB3RSTR_LPTIM1RST_Msk
#define RCC_APB3RSTR_LPTIM3RST_Pos          (12UL)
#define RCC_APB3RSTR_LPTIM3RST_Msk          (0x1UL << RCC_APB3RSTR_LPTIM3RST_Pos)
#define RCC_APB3RSTR_LPTIM3RST              RCC_APB3RSTR_LPTIM3RST_Msk
#define RCC_APB3RSTR_LPTIM4RST_Pos          (13UL)
#define RCC_APB3RSTR_LPTIM4RST_Msk          (0x1UL << RCC_APB3RSTR_LPTIM4RST_Pos)
#define RCC_APB3RSTR_LPTIM4RST              RCC_APB3RSTR_LPTIM4RST_Msk
#define RCC_APB3RSTR_OPAMPRST_Pos           (14UL)
#define RCC_APB3RSTR_OPAMPRST_Msk           (0x1UL << RCC_APB3RSTR_OPAMPRST_Pos)
#define RCC_APB3RSTR_OPAMPRST               RCC_APB3RSTR_OPAMPRST_Msk
#define RCC_APB3RSTR_COMPRST_Pos            (15UL)
#define RCC_APB3RSTR_COMPRST_Msk            (0x1UL << RCC_APB3RSTR_COMPRST_Pos)
#define RCC_APB3RSTR_COMPRST                RCC_APB3RSTR_COMPRST_Msk
#define RCC_APB3RSTR_VREFRST_Pos            (20UL)
#define RCC_APB3RSTR_VREFRST_Msk            (0x1UL << RCC_APB3RSTR_VREFRST_Pos)
#define RCC_APB3RSTR_VREFRST                RCC_APB3RSTR_VREFRST_Msk
#define RCC_AHB1ENR_GPDMA1EN_Pos            (0UL)
#define RCC_AHB1ENR_GPDMA1EN_Msk            (0x1UL << RCC_AHB1ENR_GPDMA1EN_Pos)
#define RCC_AHB1ENR_GPDMA1EN                RCC_AHB1ENR_GPDMA1EN_Msk
#define RCC_AHB1ENR_CORDICEN_Pos            (1UL)
#define RCC_AHB1ENR_CORDICEN_Msk            (0x1UL << RCC_AHB1ENR_CORDICEN_Pos)
#define RCC_AHB1ENR_CORDICEN                RCC_AHB1ENR_CORDICEN_Msk
#define RCC_AHB1ENR_FMACEN_Pos              (2UL)
#define RCC_AHB1ENR_FMACEN_Msk              (0x1UL << RCC_AHB1ENR_FMACEN_Pos)
#define RCC_AHB1ENR_FMACEN                  RCC_AHB1ENR_FMACEN_Msk
#define RCC_AHB1ENR_MDF1EN_Pos              (3UL)
#define RCC_AHB1ENR_MDF1EN_Msk              (0x1UL << RCC_AHB1ENR_MDF1EN_Pos)
#define RCC_AHB1ENR_MDF1EN                  RCC_AHB1ENR_MDF1EN_Msk
#define RCC_AHB1ENR_FLASHEN_Pos             (8UL)
#define RCC_AHB1ENR_FLASHEN_Msk             (0x1UL << RCC_AHB1ENR_FLASHEN_Pos)
#define RCC_AHB1ENR_FLASHEN                 RCC_AHB1ENR_FLASHEN_Msk
#define RCC_AHB1ENR_CRCEN_Pos               (12UL)
#define RCC_AHB1ENR_CRCEN_Msk               (0x1UL << RCC_AHB1ENR_CRCEN_Pos)
#define RCC_AHB1ENR_CRCEN                   RCC_AHB1ENR_CRCEN_Msk
#define RCC_AHB1ENR_TSCEN_Pos               (16UL)
#define RCC_AHB1ENR_TSCEN_Msk               (0x1UL << RCC_AHB1ENR_TSCEN_Pos)
#define RCC_AHB1ENR_TSCEN                   RCC_AHB1ENR_TSCEN_Msk
#define RCC_AHB1ENR_RAMCFGEN_Pos            (17UL)
#define RCC_AHB1ENR_RAMCFGEN_Msk            (0x1UL << RCC_AHB1ENR_RAMCFGEN_Pos)
#define RCC_AHB1ENR_RAMCFGEN                RCC_AHB1ENR_RAMCFGEN_Msk
#define RCC_AHB1ENR_DMA2DEN_Pos             (18UL)
#define RCC_AHB1ENR_DMA2DEN_Msk             (0x1UL << RCC_AHB1ENR_DMA2DEN_Pos)
#define RCC_AHB1ENR_DMA2DEN                 RCC_AHB1ENR_DMA2DEN_Msk
#define RCC_AHB1ENR_GTZC1EN_Pos             (24UL)
#define RCC_AHB1ENR_GTZC1EN_Msk             (0x1UL << RCC_AHB1ENR_GTZC1EN_Pos)
#define RCC_AHB1ENR_GTZC1EN                 RCC_AHB1ENR_GTZC1EN_Msk
#define RCC_AHB1ENR_BKPSRAMEN_Pos           (28UL)
#define RCC_AHB1ENR_BKPSRAMEN_Msk           (0x1UL << RCC_AHB1ENR_BKPSRAMEN_Pos)
#define RCC_AHB1ENR_BKPSRAMEN               RCC_AHB1ENR_BKPSRAMEN_Msk
#define RCC_AHB1ENR_DCACHE1EN_Pos           (30UL)
#define RCC_AHB1ENR_DCACHE1EN_Msk           (0x1UL << RCC_AHB1ENR_DCACHE1EN_Pos)
#define RCC_AHB1ENR_DCACHE1EN               RCC_AHB1ENR_DCACHE1EN_Msk
#define RCC_AHB1ENR_SRAM1EN_Pos             (31UL)
#define RCC_AHB1ENR_SRAM1EN_Msk             (0x1UL << RCC_AHB1ENR_SRAM1EN_Pos)
#define RCC_AHB1ENR_SRAM1EN                 RCC_AHB1ENR_SRAM1EN_Msk
#define RCC_AHB2ENR1_GPIOAEN_Pos            (0UL)
#define RCC_AHB2ENR1_GPIOAEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOAEN_Pos)
#define RCC_AHB2ENR1_GPIOAEN                RCC_AHB2ENR1_GPIOAEN_Msk
#define RCC_AHB2ENR1_GPIOBEN_Pos            (1UL)
#define RCC_AHB2ENR1_GPIOBEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOBEN_Pos)
#define RCC_AHB2ENR1_GPIOBEN                RCC_AHB2ENR1_GPIOBEN_Msk
#define RCC_AHB2ENR1_GPIOCEN_Pos            (2UL)
#define RCC_AHB2ENR1_GPIOCEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOCEN_Pos)
#define RCC_AHB2ENR1_GPIOCEN                RCC_AHB2ENR1_GPIOCEN_Msk
#define RCC_AHB2ENR1_GPIODEN_Pos            (3UL)
#define RCC_AHB2ENR1_GPIODEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIODEN_Pos)
#define RCC_AHB2ENR1_GPIODEN                RCC_AHB2ENR1_GPIODEN_Msk
#define RCC_AHB2ENR1_GPIOEEN_Pos            (4UL)
#define RCC_AHB2ENR1_GPIOEEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOEEN_Pos)
#define RCC_AHB2ENR1_GPIOEEN                RCC_AHB2ENR1_GPIOEEN_Msk
#define RCC_AHB2ENR1_GPIOFEN_Pos            (5UL)
#define RCC_AHB2ENR1_GPIOFEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOFEN_Pos)
#define RCC_AHB2ENR1_GPIOFEN                RCC_AHB2ENR1_GPIOFEN_Msk
#define RCC_AHB2ENR1_GPIOGEN_Pos            (6UL)
#define RCC_AHB2ENR1_GPIOGEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOGEN_Pos)
#define RCC_AHB2ENR1_GPIOGEN                RCC_AHB2ENR1_GPIOGEN_Msk
#define RCC_AHB2ENR1_GPIOHEN_Pos            (7UL)
#define RCC_AHB2ENR1_GPIOHEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOHEN_Pos)
#define RCC_AHB2ENR1_GPIOHEN                RCC_AHB2ENR1_GPIOHEN_Msk
#define RCC_AHB2ENR1_GPIOIEN_Pos            (8UL)
#define RCC_AHB2ENR1_GPIOIEN_Msk            (0x1UL << RCC_AHB2ENR1_GPIOIEN_Pos)
#define RCC_AHB2ENR1_GPIOIEN                RCC_AHB2ENR1_GPIOIEN_Msk
#define RCC_AHB2ENR1_ADC12EN_Pos             (10UL)
#define RCC_AHB2ENR1_ADC12EN_Msk             (0x1UL << RCC_AHB2ENR1_ADC12EN_Pos)
#define RCC_AHB2ENR1_ADC12EN                 RCC_AHB2ENR1_ADC12EN_Msk
#define RCC_AHB2ENR1_DCMI_PSSIEN_Pos        (12UL)
#define RCC_AHB2ENR1_DCMI_PSSIEN_Msk        (0x1UL << RCC_AHB2ENR1_DCMI_PSSIEN_Pos)
#define RCC_AHB2ENR1_DCMI_PSSIEN            RCC_AHB2ENR1_DCMI_PSSIEN_Msk
#define RCC_AHB2ENR1_OTGEN_Pos              (14UL)
#define RCC_AHB2ENR1_OTGEN_Msk              (0x1UL << RCC_AHB2ENR1_OTGEN_Pos)
#define RCC_AHB2ENR1_OTGEN                  RCC_AHB2ENR1_OTGEN_Msk
#define RCC_AHB2ENR1_AESEN_Pos              (16UL)
#define RCC_AHB2ENR1_AESEN_Msk              (0x1UL << RCC_AHB2ENR1_AESEN_Pos)
#define RCC_AHB2ENR1_AESEN                  RCC_AHB2ENR1_AESEN_Msk
#define RCC_AHB2ENR1_HASHEN_Pos             (17UL)
#define RCC_AHB2ENR1_HASHEN_Msk             (0x1UL << RCC_AHB2ENR1_HASHEN_Pos)
#define RCC_AHB2ENR1_HASHEN                 RCC_AHB2ENR1_HASHEN_Msk
#define RCC_AHB2ENR1_RNGEN_Pos              (18UL)
#define RCC_AHB2ENR1_RNGEN_Msk              (0x1UL << RCC_AHB2ENR1_RNGEN_Pos)
#define RCC_AHB2ENR1_RNGEN                  RCC_AHB2ENR1_RNGEN_Msk
#define RCC_AHB2ENR1_PKAEN_Pos              (19UL)
#define RCC_AHB2ENR1_PKAEN_Msk              (0x1UL << RCC_AHB2ENR1_PKAEN_Pos)
#define RCC_AHB2ENR1_PKAEN                  RCC_AHB2ENR1_PKAEN_Msk
#define RCC_AHB2ENR1_SAESEN_Pos             (20UL)
#define RCC_AHB2ENR1_SAESEN_Msk             (0x1UL << RCC_AHB2ENR1_SAESEN_Pos)
#define RCC_AHB2ENR1_SAESEN                 RCC_AHB2ENR1_SAESEN_Msk
#define RCC_AHB2ENR1_OCTOSPIMEN_Pos         (21UL)
#define RCC_AHB2ENR1_OCTOSPIMEN_Msk         (0x1UL << RCC_AHB2ENR1_OCTOSPIMEN_Pos)
#define RCC_AHB2ENR1_OCTOSPIMEN             RCC_AHB2ENR1_OCTOSPIMEN_Msk
#define RCC_AHB2ENR1_OTFDEC1EN_Pos          (23UL)
#define RCC_AHB2ENR1_OTFDEC1EN_Msk          (0x1UL << RCC_AHB2ENR1_OTFDEC1EN_Pos)
#define RCC_AHB2ENR1_OTFDEC1EN              RCC_AHB2ENR1_OTFDEC1EN_Msk
#define RCC_AHB2ENR1_OTFDEC2EN_Pos          (24UL)
#define RCC_AHB2ENR1_OTFDEC2EN_Msk          (0x1UL << RCC_AHB2ENR1_OTFDEC2EN_Pos)
#define RCC_AHB2ENR1_OTFDEC2EN              RCC_AHB2ENR1_OTFDEC2EN_Msk
#define RCC_AHB2ENR1_SDMMC1EN_Pos           (27UL)
#define RCC_AHB2ENR1_SDMMC1EN_Msk           (0x1UL << RCC_AHB2ENR1_SDMMC1EN_Pos)
#define RCC_AHB2ENR1_SDMMC1EN               RCC_AHB2ENR1_SDMMC1EN_Msk
#define RCC_AHB2ENR1_SDMMC2EN_Pos           (28UL)
#define RCC_AHB2ENR1_SDMMC2EN_Msk           (0x1UL << RCC_AHB2ENR1_SDMMC2EN_Pos)
#define RCC_AHB2ENR1_SDMMC2EN               RCC_AHB2ENR1_SDMMC2EN_Msk
#define RCC_AHB2ENR1_SRAM2EN_Pos            (30UL)
#define RCC_AHB2ENR1_SRAM2EN_Msk            (0x1UL << RCC_AHB2ENR1_SRAM2EN_Pos)
#define RCC_AHB2ENR1_SRAM2EN                RCC_AHB2ENR1_SRAM2EN_Msk
#define RCC_AHB2ENR1_SRAM3EN_Pos            (31UL)
#define RCC_AHB2ENR1_SRAM3EN_Msk            (0x1UL << RCC_AHB2ENR1_SRAM3EN_Pos)
#define RCC_AHB2ENR1_SRAM3EN                RCC_AHB2ENR1_SRAM3EN_Msk
#define RCC_AHB2ENR2_FSMCEN_Pos             (0UL)
#define RCC_AHB2ENR2_FSMCEN_Msk             (0x1UL << RCC_AHB2ENR2_FSMCEN_Pos)
#define RCC_AHB2ENR2_FSMCEN                 RCC_AHB2ENR2_FSMCEN_Msk
#define RCC_AHB2ENR2_OCTOSPI1EN_Pos         (4UL)
#define RCC_AHB2ENR2_OCTOSPI1EN_Msk         (0x1UL << RCC_AHB2ENR2_OCTOSPI1EN_Pos)
#define RCC_AHB2ENR2_OCTOSPI1EN             RCC_AHB2ENR2_OCTOSPI1EN_Msk
#define RCC_AHB2ENR2_OCTOSPI2EN_Pos         (8UL)
#define RCC_AHB2ENR2_OCTOSPI2EN_Msk         (0x1UL << RCC_AHB2ENR2_OCTOSPI2EN_Pos)
#define RCC_AHB2ENR2_OCTOSPI2EN             RCC_AHB2ENR2_OCTOSPI2EN_Msk
#define RCC_AHB3ENR_LPGPIO1EN_Pos           (0UL)
#define RCC_AHB3ENR_LPGPIO1EN_Msk           (0x1UL << RCC_AHB3ENR_LPGPIO1EN_Pos)
#define RCC_AHB3ENR_LPGPIO1EN               RCC_AHB3ENR_LPGPIO1EN_Msk
#define RCC_AHB3ENR_PWREN_Pos               (2UL)
#define RCC_AHB3ENR_PWREN_Msk               (0x1UL << RCC_AHB3ENR_PWREN_Pos)
#define RCC_AHB3ENR_PWREN                   RCC_AHB3ENR_PWREN_Msk
#define RCC_AHB3ENR_ADC4EN_Pos              (5UL)
#define RCC_AHB3ENR_ADC4EN_Msk              (0x1UL << RCC_AHB3ENR_ADC4EN_Pos)
#define RCC_AHB3ENR_ADC4EN                  RCC_AHB3ENR_ADC4EN_Msk
#define RCC_AHB3ENR_DAC1EN_Pos              (6UL)
#define RCC_AHB3ENR_DAC1EN_Msk              (0x1UL << RCC_AHB3ENR_DAC1EN_Pos)
#define RCC_AHB3ENR_DAC1EN                  RCC_AHB3ENR_DAC1EN_Msk
#define RCC_AHB3ENR_LPDMA1EN_Pos            (9UL)
#define RCC_AHB3ENR_LPDMA1EN_Msk            (0x1UL << RCC_AHB3ENR_LPDMA1EN_Pos)
#define RCC_AHB3ENR_LPDMA1EN                RCC_AHB3ENR_LPDMA1EN_Msk
#define RCC_AHB3ENR_ADF1EN_Pos              (10UL)
#define RCC_AHB3ENR_ADF1EN_Msk              (0x1UL << RCC_AHB3ENR_ADF1EN_Pos)
#define RCC_AHB3ENR_ADF1EN                  RCC_AHB3ENR_ADF1EN_Msk
#define RCC_AHB3ENR_GTZC2EN_Pos             (12UL)
#define RCC_AHB3ENR_GTZC2EN_Msk             (0x1UL << RCC_AHB3ENR_GTZC2EN_Pos)
#define RCC_AHB3ENR_GTZC2EN                 RCC_AHB3ENR_GTZC2EN_Msk
#define RCC_AHB3ENR_SRAM4EN_Pos             (31UL)
#define RCC_AHB3ENR_SRAM4EN_Msk             (0x1UL << RCC_AHB3ENR_SRAM4EN_Pos)
#define RCC_AHB3ENR_SRAM4EN                 RCC_AHB3ENR_SRAM4EN_Msk
#define RCC_APB1ENR1_TIM2EN_Pos             (0UL)
#define RCC_APB1ENR1_TIM2EN_Msk             (0x1UL << RCC_APB1ENR1_TIM2EN_Pos)
#define RCC_APB1ENR1_TIM2EN                 RCC_APB1ENR1_TIM2EN_Msk
#define RCC_APB1ENR1_TIM3EN_Pos             (1UL)
#define RCC_APB1ENR1_TIM3EN_Msk             (0x1UL << RCC_APB1ENR1_TIM3EN_Pos)
#define RCC_APB1ENR1_TIM3EN                 RCC_APB1ENR1_TIM3EN_Msk
#define RCC_APB1ENR1_TIM4EN_Pos             (2UL)
#define RCC_APB1ENR1_TIM4EN_Msk             (0x1UL << RCC_APB1ENR1_TIM4EN_Pos)
#define RCC_APB1ENR1_TIM4EN                 RCC_APB1ENR1_TIM4EN_Msk
#define RCC_APB1ENR1_TIM5EN_Pos             (3UL)
#define RCC_APB1ENR1_TIM5EN_Msk             (0x1UL << RCC_APB1ENR1_TIM5EN_Pos)
#define RCC_APB1ENR1_TIM5EN                 RCC_APB1ENR1_TIM5EN_Msk
#define RCC_APB1ENR1_TIM6EN_Pos             (4UL)
#define RCC_APB1ENR1_TIM6EN_Msk             (0x1UL << RCC_APB1ENR1_TIM6EN_Pos)
#define RCC_APB1ENR1_TIM6EN                 RCC_APB1ENR1_TIM6EN_Msk
#define RCC_APB1ENR1_TIM7EN_Pos             (5UL)
#define RCC_APB1ENR1_TIM7EN_Msk             (0x1UL << RCC_APB1ENR1_TIM7EN_Pos)
#define RCC_APB1ENR1_TIM7EN                 RCC_APB1ENR1_TIM7EN_Msk
#define RCC_APB1ENR1_WWDGEN_Pos             (11UL)
#define RCC_APB1ENR1_WWDGEN_Msk             (0x1UL << RCC_APB1ENR1_WWDGEN_Pos)
#define RCC_APB1ENR1_WWDGEN                 RCC_APB1ENR1_WWDGEN_Msk
#define RCC_APB1ENR1_SPI2EN_Pos             (14UL)
#define RCC_APB1ENR1_SPI2EN_Msk             (0x1UL << RCC_APB1ENR1_SPI2EN_Pos)
#define RCC_APB1ENR1_SPI2EN                 RCC_APB1ENR1_SPI2EN_Msk
#define RCC_APB1ENR1_USART2EN_Pos           (17UL)
#define RCC_APB1ENR1_USART2EN_Msk           (0x1UL << RCC_APB1ENR1_USART2EN_Pos)
#define RCC_APB1ENR1_USART2EN               RCC_APB1ENR1_USART2EN_Msk
#define RCC_APB1ENR1_USART3EN_Pos           (18UL)
#define RCC_APB1ENR1_USART3EN_Msk           (0x1UL << RCC_APB1ENR1_USART3EN_Pos)
#define RCC_APB1ENR1_USART3EN               RCC_APB1ENR1_USART3EN_Msk
#define RCC_APB1ENR1_UART4EN_Pos            (19UL)
#define RCC_APB1ENR1_UART4EN_Msk            (0x1UL << RCC_APB1ENR1_UART4EN_Pos)
#define RCC_APB1ENR1_UART4EN                RCC_APB1ENR1_UART4EN_Msk
#define RCC_APB1ENR1_UART5EN_Pos            (20UL)
#define RCC_APB1ENR1_UART5EN_Msk            (0x1UL << RCC_APB1ENR1_UART5EN_Pos)
#define RCC_APB1ENR1_UART5EN                RCC_APB1ENR1_UART5EN_Msk
#define RCC_APB1ENR1_I2C1EN_Pos             (21UL)
#define RCC_APB1ENR1_I2C1EN_Msk             (0x1UL << RCC_APB1ENR1_I2C1EN_Pos)
#define RCC_APB1ENR1_I2C1EN                 RCC_APB1ENR1_I2C1EN_Msk
#define RCC_APB1ENR1_I2C2EN_Pos             (22UL)
#define RCC_APB1ENR1_I2C2EN_Msk             (0x1UL << RCC_APB1ENR1_I2C2EN_Pos)
#define RCC_APB1ENR1_I2C2EN                 RCC_APB1ENR1_I2C2EN_Msk
#define RCC_APB1ENR1_CRSEN_Pos              (24UL)
#define RCC_APB1ENR1_CRSEN_Msk              (0x1UL << RCC_APB1ENR1_CRSEN_Pos)
#define RCC_APB1ENR1_CRSEN                  RCC_APB1ENR1_CRSEN_Msk
#define RCC_APB1ENR2_I2C4EN_Pos             (1UL)
#define RCC_APB1ENR2_I2C4EN_Msk             (0x1UL << RCC_APB1ENR2_I2C4EN_Pos)
#define RCC_APB1ENR2_I2C4EN                 RCC_APB1ENR2_I2C4EN_Msk
#define RCC_APB1ENR2_LPTIM2EN_Pos           (5UL)
#define RCC_APB1ENR2_LPTIM2EN_Msk           (0x1UL << RCC_APB1ENR2_LPTIM2EN_Pos)
#define RCC_APB1ENR2_LPTIM2EN               RCC_APB1ENR2_LPTIM2EN_Msk
#define RCC_APB1ENR2_FDCAN1EN_Pos           (9UL)
#define RCC_APB1ENR2_FDCAN1EN_Msk           (0x1UL << RCC_APB1ENR2_FDCAN1EN_Pos)
#define RCC_APB1ENR2_FDCAN1EN               RCC_APB1ENR2_FDCAN1EN_Msk
#define RCC_APB1ENR2_UCPD1EN_Pos            (23UL)
#define RCC_APB1ENR2_UCPD1EN_Msk            (0x1UL << RCC_APB1ENR2_UCPD1EN_Pos)
#define RCC_APB1ENR2_UCPD1EN                RCC_APB1ENR2_UCPD1EN_Msk
#define RCC_APB2ENR_TIM1EN_Pos              (11UL)
#define RCC_APB2ENR_TIM1EN_Msk              (0x1UL << RCC_APB2ENR_TIM1EN_Pos)
#define RCC_APB2ENR_TIM1EN                  RCC_APB2ENR_TIM1EN_Msk
#define RCC_APB2ENR_SPI1EN_Pos              (12UL)
#define RCC_APB2ENR_SPI1EN_Msk              (0x1UL << RCC_APB2ENR_SPI1EN_Pos)
#define RCC_APB2ENR_SPI1EN                  RCC_APB2ENR_SPI1EN_Msk
#define RCC_APB2ENR_TIM8EN_Pos              (13UL)
#define RCC_APB2ENR_TIM8EN_Msk              (0x1UL << RCC_APB2ENR_TIM8EN_Pos)
#define RCC_APB2ENR_TIM8EN                  RCC_APB2ENR_TIM8EN_Msk
#define RCC_APB2ENR_USART1EN_Pos            (14UL)
#define RCC_APB2ENR_USART1EN_Msk            (0x1UL << RCC_APB2ENR_USART1EN_Pos)
#define RCC_APB2ENR_USART1EN                RCC_APB2ENR_USART1EN_Msk
#define RCC_APB2ENR_TIM15EN_Pos             (16UL)
#define RCC_APB2ENR_TIM15EN_Msk             (0x1UL << RCC_APB2ENR_TIM15EN_Pos)
#define RCC_APB2ENR_TIM15EN                 RCC_APB2ENR_TIM15EN_Msk
#define RCC_APB2ENR_TIM16EN_Pos             (17UL)
#define RCC_APB2ENR_TIM16EN_Msk             (0x1UL << RCC_APB2ENR_TIM16EN_Pos)
#define RCC_APB2ENR_TIM16EN                 RCC_APB2ENR_TIM16EN_Msk
#define RCC_APB2ENR_TIM17EN_Pos             (18UL)
#define RCC_APB2ENR_TIM17EN_Msk             (0x1UL << RCC_APB2ENR_TIM17EN_Pos)
#define RCC_APB2ENR_TIM17EN                 RCC_APB2ENR_TIM17EN_Msk
#define RCC_APB2ENR_SAI1EN_Pos              (21UL)
#define RCC_APB2ENR_SAI1EN_Msk              (0x1UL << RCC_APB2ENR_SAI1EN_Pos)
#define RCC_APB2ENR_SAI1EN                  RCC_APB2ENR_SAI1EN_Msk
#define RCC_APB2ENR_SAI2EN_Pos              (22UL)
#define RCC_APB2ENR_SAI2EN_Msk              (0x1UL << RCC_APB2ENR_SAI2EN_Pos)
#define RCC_APB2ENR_SAI2EN                  RCC_APB2ENR_SAI2EN_Msk
#define RCC_APB3ENR_SYSCFGEN_Pos            (1UL)
#define RCC_APB3ENR_SYSCFGEN_Msk            (0x1UL << RCC_APB3ENR_SYSCFGEN_Pos)
#define RCC_APB3ENR_SYSCFGEN                RCC_APB3ENR_SYSCFGEN_Msk
#define RCC_APB3ENR_SPI3EN_Pos              (5UL)
#define RCC_APB3ENR_SPI3EN_Msk              (0x1UL << RCC_APB3ENR_SPI3EN_Pos)
#define RCC_APB3ENR_SPI3EN                  RCC_APB3ENR_SPI3EN_Msk
#define RCC_APB3ENR_LPUART1EN_Pos           (6UL)
#define RCC_APB3ENR_LPUART1EN_Msk           (0x1UL << RCC_APB3ENR_LPUART1EN_Pos)
#define RCC_APB3ENR_LPUART1EN               RCC_APB3ENR_LPUART1EN_Msk
#define RCC_APB3ENR_I2C3EN_Pos              (7UL)
#define RCC_APB3ENR_I2C3EN_Msk              (0x1UL << RCC_APB3ENR_I2C3EN_Pos)
#define RCC_APB3ENR_I2C3EN                  RCC_APB3ENR_I2C3EN_Msk
#define RCC_APB3ENR_LPTIM1EN_Pos            (11UL)
#define RCC_APB3ENR_LPTIM1EN_Msk            (0x1UL << RCC_APB3ENR_LPTIM1EN_Pos)
#define RCC_APB3ENR_LPTIM1EN                RCC_APB3ENR_LPTIM1EN_Msk
#define RCC_APB3ENR_LPTIM3EN_Pos            (12UL)
#define RCC_APB3ENR_LPTIM3EN_Msk            (0x1UL << RCC_APB3ENR_LPTIM3EN_Pos)
#define RCC_APB3ENR_LPTIM3EN                RCC_APB3ENR_LPTIM3EN_Msk
#define RCC_APB3ENR_LPTIM4EN_Pos            (13UL)
#define RCC_APB3ENR_LPTIM4EN_Msk            (0x1UL << RCC_APB3ENR_LPTIM4EN_Pos)
#define RCC_APB3ENR_LPTIM4EN                RCC_APB3ENR_LPTIM4EN_Msk
#define RCC_APB3ENR_OPAMPEN_Pos             (14UL)
#define RCC_APB3ENR_OPAMPEN_Msk             (0x1UL << RCC_APB3ENR_OPAMPEN_Pos)
#define RCC_APB3ENR_OPAMPEN                 RCC_APB3ENR_OPAMPEN_Msk
#define RCC_APB3ENR_COMPEN_Pos              (15UL)
#define RCC_APB3ENR_COMPEN_Msk              (0x1UL << RCC_APB3ENR_COMPEN_Pos)
#define RCC_APB3ENR_COMPEN                  RCC_APB3ENR_COMPEN_Msk
#define RCC_APB3ENR_VREFEN_Pos              (20UL)
#define RCC_APB3ENR_VREFEN_Msk              (0x1UL << RCC_APB3ENR_VREFEN_Pos)
#define RCC_APB3ENR_VREFEN                  RCC_APB3ENR_VREFEN_Msk
#define RCC_APB3ENR_RTCAPBEN_Pos            (21UL)
#define RCC_APB3ENR_RTCAPBEN_Msk            (0x1UL << RCC_APB3ENR_RTCAPBEN_Pos)
#define RCC_APB3ENR_RTCAPBEN                RCC_APB3ENR_RTCAPBEN_Msk
#define RCC_AHB1SMENR_GPDMA1SMEN_Pos        (0UL)
#define RCC_AHB1SMENR_GPDMA1SMEN_Msk        (0x1UL << RCC_AHB1SMENR_GPDMA1SMEN_Pos)
#define RCC_AHB1SMENR_GPDMA1SMEN            RCC_AHB1SMENR_GPDMA1SMEN_Msk
#define RCC_AHB1SMENR_CORDICSMEN_Pos        (1UL)
#define RCC_AHB1SMENR_CORDICSMEN_Msk        (0x1UL << RCC_AHB1SMENR_CORDICSMEN_Pos)
#define RCC_AHB1SMENR_CORDICSMEN            RCC_AHB1SMENR_CORDICSMEN_Msk
#define RCC_AHB1SMENR_FMACSMEN_Pos          (2UL)
#define RCC_AHB1SMENR_FMACSMEN_Msk          (0x1UL << RCC_AHB1SMENR_FMACSMEN_Pos)
#define RCC_AHB1SMENR_FMACSMEN              RCC_AHB1SMENR_FMACSMEN_Msk
#define RCC_AHB1SMENR_MDF1SMEN_Pos          (3UL)
#define RCC_AHB1SMENR_MDF1SMEN_Msk          (0x1UL << RCC_AHB1SMENR_MDF1SMEN_Pos)
#define RCC_AHB1SMENR_MDF1SMEN              RCC_AHB1SMENR_MDF1SMEN_Msk
#define RCC_AHB1SMENR_FLASHSMEN_Pos         (8UL)
#define RCC_AHB1SMENR_FLASHSMEN_Msk         (0x1UL << RCC_AHB1SMENR_FLASHSMEN_Pos)
#define RCC_AHB1SMENR_FLASHSMEN             RCC_AHB1SMENR_FLASHSMEN_Msk
#define RCC_AHB1SMENR_CRCSMEN_Pos           (12UL)
#define RCC_AHB1SMENR_CRCSMEN_Msk           (0x1UL << RCC_AHB1SMENR_CRCSMEN_Pos)
#define RCC_AHB1SMENR_CRCSMEN               RCC_AHB1SMENR_CRCSMEN_Msk
#define RCC_AHB1SMENR_TSCSMEN_Pos           (16UL)
#define RCC_AHB1SMENR_TSCSMEN_Msk           (0x1UL << RCC_AHB1SMENR_TSCSMEN_Pos)
#define RCC_AHB1SMENR_TSCSMEN               RCC_AHB1SMENR_TSCSMEN_Msk
#define RCC_AHB1SMENR_RAMCFGSMEN_Pos        (17UL)
#define RCC_AHB1SMENR_RAMCFGSMEN_Msk        (0x1UL << RCC_AHB1SMENR_RAMCFGSMEN_Pos)
#define RCC_AHB1SMENR_RAMCFGSMEN            RCC_AHB1SMENR_RAMCFGSMEN_Msk
#define RCC_AHB1SMENR_DMA2DSMEN_Pos         (18UL)
#define RCC_AHB1SMENR_DMA2DSMEN_Msk         (0x1UL << RCC_AHB1SMENR_DMA2DSMEN_Pos)
#define RCC_AHB1SMENR_DMA2DSMEN             RCC_AHB1SMENR_DMA2DSMEN_Msk
#define RCC_AHB1SMENR_GTZC1SMEN_Pos         (24UL)
#define RCC_AHB1SMENR_GTZC1SMEN_Msk         (0x1UL << RCC_AHB1SMENR_GTZC1SMEN_Pos)
#define RCC_AHB1SMENR_GTZC1SMEN             RCC_AHB1SMENR_GTZC1SMEN_Msk
#define RCC_AHB1SMENR_BKPSRAMSMEN_Pos       (28UL)
#define RCC_AHB1SMENR_BKPSRAMSMEN_Msk       (0x1UL << RCC_AHB1SMENR_BKPSRAMSMEN_Pos)
#define RCC_AHB1SMENR_BKPSRAMSMEN           RCC_AHB1SMENR_BKPSRAMSMEN_Msk
#define RCC_AHB1SMENR_ICACHESMEN_Pos        (29UL)
#define RCC_AHB1SMENR_ICACHESMEN_Msk        (0x1UL << RCC_AHB1SMENR_ICACHESMEN_Pos)
#define RCC_AHB1SMENR_ICACHESMEN            RCC_AHB1SMENR_ICACHESMEN_Msk
#define RCC_AHB1SMENR_DCACHE1SMEN_Pos       (30UL)
#define RCC_AHB1SMENR_DCACHE1SMEN_Msk       (0x1UL << RCC_AHB1SMENR_DCACHE1SMEN_Pos)
#define RCC_AHB1SMENR_DCACHE1SMEN           RCC_AHB1SMENR_DCACHE1SMEN_Msk
#define RCC_AHB1SMENR_SRAM1SMEN_Pos         (31UL)
#define RCC_AHB1SMENR_SRAM1SMEN_Msk         (0x1UL << RCC_AHB1SMENR_SRAM1SMEN_Pos)
#define RCC_AHB1SMENR_SRAM1SMEN             RCC_AHB1SMENR_SRAM1SMEN_Msk
#define RCC_AHB2SMENR1_GPIOASMEN_Pos        (0UL)
#define RCC_AHB2SMENR1_GPIOASMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOASMEN_Pos)
#define RCC_AHB2SMENR1_GPIOASMEN            RCC_AHB2SMENR1_GPIOASMEN_Msk
#define RCC_AHB2SMENR1_GPIOBSMEN_Pos        (1UL)
#define RCC_AHB2SMENR1_GPIOBSMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOBSMEN_Pos)
#define RCC_AHB2SMENR1_GPIOBSMEN            RCC_AHB2SMENR1_GPIOBSMEN_Msk
#define RCC_AHB2SMENR1_GPIOCSMEN_Pos        (2UL)
#define RCC_AHB2SMENR1_GPIOCSMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOCSMEN_Pos)
#define RCC_AHB2SMENR1_GPIOCSMEN            RCC_AHB2SMENR1_GPIOCSMEN_Msk
#define RCC_AHB2SMENR1_GPIODSMEN_Pos        (3UL)
#define RCC_AHB2SMENR1_GPIODSMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIODSMEN_Pos)
#define RCC_AHB2SMENR1_GPIODSMEN            RCC_AHB2SMENR1_GPIODSMEN_Msk
#define RCC_AHB2SMENR1_GPIOESMEN_Pos        (4UL)
#define RCC_AHB2SMENR1_GPIOESMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOESMEN_Pos)
#define RCC_AHB2SMENR1_GPIOESMEN            RCC_AHB2SMENR1_GPIOESMEN_Msk
#define RCC_AHB2SMENR1_GPIOFSMEN_Pos        (5UL)
#define RCC_AHB2SMENR1_GPIOFSMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOFSMEN_Pos)
#define RCC_AHB2SMENR1_GPIOFSMEN            RCC_AHB2SMENR1_GPIOFSMEN_Msk
#define RCC_AHB2SMENR1_GPIOGSMEN_Pos        (6UL)
#define RCC_AHB2SMENR1_GPIOGSMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOGSMEN_Pos)
#define RCC_AHB2SMENR1_GPIOGSMEN            RCC_AHB2SMENR1_GPIOGSMEN_Msk
#define RCC_AHB2SMENR1_GPIOHSMEN_Pos        (7UL)
#define RCC_AHB2SMENR1_GPIOHSMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOHSMEN_Pos)
#define RCC_AHB2SMENR1_GPIOHSMEN            RCC_AHB2SMENR1_GPIOHSMEN_Msk
#define RCC_AHB2SMENR1_GPIOISMEN_Pos        (8UL)
#define RCC_AHB2SMENR1_GPIOISMEN_Msk        (0x1UL << RCC_AHB2SMENR1_GPIOISMEN_Pos)
#define RCC_AHB2SMENR1_GPIOISMEN            RCC_AHB2SMENR1_GPIOISMEN_Msk
#define RCC_AHB2SMENR1_ADC12SMEN_Pos        (10UL)
#define RCC_AHB2SMENR1_ADC12SMEN_Msk        (0x1UL << RCC_AHB2SMENR1_ADC12SMEN_Pos)
#define RCC_AHB2SMENR1_ADC12SMEN            RCC_AHB2SMENR1_ADC12SMEN_Msk
#define RCC_AHB2SMENR1_DCMI_PSSISMEN_Pos    (12UL)
#define RCC_AHB2SMENR1_DCMI_PSSISMEN_Msk    (0x1UL << RCC_AHB2SMENR1_DCMI_PSSISMEN_Pos)
#define RCC_AHB2SMENR1_DCMI_PSSISMEN        RCC_AHB2SMENR1_DCMI_PSSISMEN_Msk
#define RCC_AHB2SMENR1_OTGSMEN_Pos          (14UL)
#define RCC_AHB2SMENR1_OTGSMEN_Msk          (0x1UL << RCC_AHB2SMENR1_OTGSMEN_Pos)
#define RCC_AHB2SMENR1_OTGSMEN              RCC_AHB2SMENR1_OTGSMEN_Msk
#define RCC_AHB2SMENR1_AESSMEN_Pos          (16UL)
#define RCC_AHB2SMENR1_AESSMEN_Msk          (0x1UL << RCC_AHB2SMENR1_AESSMEN_Pos)
#define RCC_AHB2SMENR1_AESSMEN              RCC_AHB2SMENR1_AESSMEN_Msk
#define RCC_AHB2SMENR1_HASHSMEN_Pos         (17UL)
#define RCC_AHB2SMENR1_HASHSMEN_Msk         (0x1UL << RCC_AHB2SMENR1_HASHSMEN_Pos)
#define RCC_AHB2SMENR1_HASHSMEN             RCC_AHB2SMENR1_HASHSMEN_Msk
#define RCC_AHB2SMENR1_RNGSMEN_Pos          (18UL)
#define RCC_AHB2SMENR1_RNGSMEN_Msk          (0x1UL << RCC_AHB2SMENR1_RNGSMEN_Pos)
#define RCC_AHB2SMENR1_RNGSMEN              RCC_AHB2SMENR1_RNGSMEN_Msk
#define RCC_AHB2SMENR1_PKASMEN_Pos          (19UL)
#define RCC_AHB2SMENR1_PKASMEN_Msk          (0x1UL << RCC_AHB2SMENR1_PKASMEN_Pos)
#define RCC_AHB2SMENR1_PKASMEN              RCC_AHB2SMENR1_PKASMEN_Msk
#define RCC_AHB2SMENR1_SAESSMEN_Pos         (20UL)
#define RCC_AHB2SMENR1_SAESSMEN_Msk         (0x1UL << RCC_AHB2SMENR1_SAESSMEN_Pos)
#define RCC_AHB2SMENR1_SAESSMEN              RCC_AHB2SMENR1_SAESSMEN_Msk
#define RCC_AHB2SMENR1_OCTOSPIMSMEN_Pos     (21UL)
#define RCC_AHB2SMENR1_OCTOSPIMSMEN_Msk     (0x1UL << RCC_AHB2SMENR1_OCTOSPIMSMEN_Pos)
#define RCC_AHB2SMENR1_OCTOSPIMSMEN         RCC_AHB2SMENR1_OCTOSPIMSMEN_Msk
#define RCC_AHB2SMENR1_OTFDEC1SMEN_Pos      (23UL)
#define RCC_AHB2SMENR1_OTFDEC1SMEN_Msk      (0x1UL << RCC_AHB2SMENR1_OTFDEC1SMEN_Pos)
#define RCC_AHB2SMENR1_OTFDEC1SMEN          RCC_AHB2SMENR1_OTFDEC1SMEN_Msk
#define RCC_AHB2SMENR1_OTFDEC2SMEN_Pos      (24UL)
#define RCC_AHB2SMENR1_OTFDEC2SMEN_Msk      (0x1UL << RCC_AHB2SMENR1_OTFDEC2SMEN_Pos)
#define RCC_AHB2SMENR1_OTFDEC2SMEN          RCC_AHB2SMENR1_OTFDEC2SMEN_Msk
#define RCC_AHB2SMENR1_SDMMC1SMEN_Pos       (27UL)
#define RCC_AHB2SMENR1_SDMMC1SMEN_Msk       (0x1UL << RCC_AHB2SMENR1_SDMMC1SMEN_Pos)
#define RCC_AHB2SMENR1_SDMMC1SMEN           RCC_AHB2SMENR1_SDMMC1SMEN_Msk
#define RCC_AHB2SMENR1_SDMMC2SMEN_Pos       (28UL)
#define RCC_AHB2SMENR1_SDMMC2SMEN_Msk       (0x1UL << RCC_AHB2SMENR1_SDMMC2SMEN_Pos)
#define RCC_AHB2SMENR1_SDMMC2SMEN           RCC_AHB2SMENR1_SDMMC2SMEN_Msk
#define RCC_AHB2SMENR1_SRAM2SMEN_Pos        (30UL)
#define RCC_AHB2SMENR1_SRAM2SMEN_Msk        (0x1UL << RCC_AHB2SMENR1_SRAM2SMEN_Pos)
#define RCC_AHB2SMENR1_SRAM2SMEN            RCC_AHB2SMENR1_SRAM2SMEN_Msk
#define RCC_AHB2SMENR1_SRAM3SMEN_Pos        (31UL)
#define RCC_AHB2SMENR1_SRAM3SMEN_Msk        (0x1UL << RCC_AHB2SMENR1_SRAM3SMEN_Pos)
#define RCC_AHB2SMENR1_SRAM3SMEN            RCC_AHB2SMENR1_SRAM3SMEN_Msk
#define RCC_AHB2SMENR2_FSMCSMEN_Pos         (0UL)
#define RCC_AHB2SMENR2_FSMCSMEN_Msk         (0x1UL << RCC_AHB2SMENR2_FSMCSMEN_Pos)
#define RCC_AHB2SMENR2_FSMCSMEN             RCC_AHB2SMENR2_FSMCSMEN_Msk
#define RCC_AHB2SMENR2_OCTOSPI1SMEN_Pos     (4UL)
#define RCC_AHB2SMENR2_OCTOSPI1SMEN_Msk     (0x1UL << RCC_AHB2SMENR2_OCTOSPI1SMEN_Pos)
#define RCC_AHB2SMENR2_OCTOSPI1SMEN         RCC_AHB2SMENR2_OCTOSPI1SMEN_Msk
#define RCC_AHB2SMENR2_OCTOSPI2SMEN_Pos     (8UL)
#define RCC_AHB2SMENR2_OCTOSPI2SMEN_Msk     (0x1UL << RCC_AHB2SMENR2_OCTOSPI2SMEN_Pos)
#define RCC_AHB2SMENR2_OCTOSPI2SMEN         RCC_AHB2SMENR2_OCTOSPI2SMEN_Msk
#define RCC_AHB3SMENR_LPGPIO1SMEN_Pos       (0UL)
#define RCC_AHB3SMENR_LPGPIO1SMEN_Msk       (0x1UL << RCC_AHB3SMENR_LPGPIO1SMEN_Pos)
#define RCC_AHB3SMENR_LPGPIO1SMEN           RCC_AHB3SMENR_LPGPIO1SMEN_Msk
#define RCC_AHB3SMENR_PWRSMEN_Pos           (2UL)
#define RCC_AHB3SMENR_PWRSMEN_Msk           (0x1UL << RCC_AHB3SMENR_PWRSMEN_Pos)
#define RCC_AHB3SMENR_PWRSMEN               RCC_AHB3SMENR_PWRSMEN_Msk
#define RCC_AHB3SMENR_ADC4SMEN_Pos          (5UL)
#define RCC_AHB3SMENR_ADC4SMEN_Msk          (0x1UL << RCC_AHB3SMENR_ADC4SMEN_Pos)
#define RCC_AHB3SMENR_ADC4SMEN              RCC_AHB3SMENR_ADC4SMEN_Msk
#define RCC_AHB3SMENR_DAC1SMEN_Pos          (6UL)
#define RCC_AHB3SMENR_DAC1SMEN_Msk          (0x1UL << RCC_AHB3SMENR_DAC1SMEN_Pos)
#define RCC_AHB3SMENR_DAC1SMEN              RCC_AHB3SMENR_DAC1SMEN_Msk
#define RCC_AHB3SMENR_LPDMA1SMEN_Pos        (9UL)
#define RCC_AHB3SMENR_LPDMA1SMEN_Msk        (0x1UL << RCC_AHB3SMENR_LPDMA1SMEN_Pos)
#define RCC_AHB3SMENR_LPDMA1SMEN            RCC_AHB3SMENR_LPDMA1SMEN_Msk
#define RCC_AHB3SMENR_ADF1SMEN_Pos          (10UL)
#define RCC_AHB3SMENR_ADF1SMEN_Msk          (0x1UL << RCC_AHB3SMENR_ADF1SMEN_Pos)
#define RCC_AHB3SMENR_ADF1SMEN              RCC_AHB3SMENR_ADF1SMEN_Msk
#define RCC_AHB3SMENR_GTZC2SMEN_Pos         (12UL)
#define RCC_AHB3SMENR_GTZC2SMEN_Msk         (0x1UL << RCC_AHB3SMENR_GTZC2SMEN_Pos)
#define RCC_AHB3SMENR_GTZC2SMEN             RCC_AHB3SMENR_GTZC2SMEN_Msk
#define RCC_AHB3SMENR_SRAM4SMEN_Pos         (31UL)
#define RCC_AHB3SMENR_SRAM4SMEN_Msk         (0x1UL << RCC_AHB3SMENR_SRAM4SMEN_Pos)
#define RCC_AHB3SMENR_SRAM4SMEN             RCC_AHB3SMENR_SRAM4SMEN_Msk
#define RCC_APB1SMENR1_TIM2SMEN_Pos         (0UL)
#define RCC_APB1SMENR1_TIM2SMEN_Msk         (0x1UL << RCC_APB1SMENR1_TIM2SMEN_Pos)
#define RCC_APB1SMENR1_TIM2SMEN             RCC_APB1SMENR1_TIM2SMEN_Msk
#define RCC_APB1SMENR1_TIM3SMEN_Pos         (1UL)
#define RCC_APB1SMENR1_TIM3SMEN_Msk         (0x1UL << RCC_APB1SMENR1_TIM3SMEN_Pos)
#define RCC_APB1SMENR1_TIM3SMEN             RCC_APB1SMENR1_TIM3SMEN_Msk
#define RCC_APB1SMENR1_TIM4SMEN_Pos         (2UL)
#define RCC_APB1SMENR1_TIM4SMEN_Msk         (0x1UL << RCC_APB1SMENR1_TIM4SMEN_Pos)
#define RCC_APB1SMENR1_TIM4SMEN             RCC_APB1SMENR1_TIM4SMEN_Msk
#define RCC_APB1SMENR1_TIM5SMEN_Pos         (3UL)
#define RCC_APB1SMENR1_TIM5SMEN_Msk         (0x1UL << RCC_APB1SMENR1_TIM5SMEN_Pos)
#define RCC_APB1SMENR1_TIM5SMEN             RCC_APB1SMENR1_TIM5SMEN_Msk
#define RCC_APB1SMENR1_TIM6SMEN_Pos         (4UL)
#define RCC_APB1SMENR1_TIM6SMEN_Msk         (0x1UL << RCC_APB1SMENR1_TIM6SMEN_Pos)
#define RCC_APB1SMENR1_TIM6SMEN             RCC_APB1SMENR1_TIM6SMEN_Msk
#define RCC_APB1SMENR1_TIM7SMEN_Pos         (5UL)
#define RCC_APB1SMENR1_TIM7SMEN_Msk         (0x1UL << RCC_APB1SMENR1_TIM7SMEN_Pos)
#define RCC_APB1SMENR1_TIM7SMEN             RCC_APB1SMENR1_TIM7SMEN_Msk
#define RCC_APB1SMENR1_WWDGSMEN_Pos         (11UL)
#define RCC_APB1SMENR1_WWDGSMEN_Msk         (0x1UL << RCC_APB1SMENR1_WWDGSMEN_Pos)
#define RCC_APB1SMENR1_WWDGSMEN             RCC_APB1SMENR1_WWDGSMEN_Msk
#define RCC_APB1SMENR1_SPI2SMEN_Pos         (14UL)
#define RCC_APB1SMENR1_SPI2SMEN_Msk         (0x1UL << RCC_APB1SMENR1_SPI2SMEN_Pos)
#define RCC_APB1SMENR1_SPI2SMEN             RCC_APB1SMENR1_SPI2SMEN_Msk
#define RCC_APB1SMENR1_USART2SMEN_Pos       (17UL)
#define RCC_APB1SMENR1_USART2SMEN_Msk       (0x1UL << RCC_APB1SMENR1_USART2SMEN_Pos)
#define RCC_APB1SMENR1_USART2SMEN           RCC_APB1SMENR1_USART2SMEN_Msk
#define RCC_APB1SMENR1_USART3SMEN_Pos       (18UL)
#define RCC_APB1SMENR1_USART3SMEN_Msk       (0x1UL << RCC_APB1SMENR1_USART3SMEN_Pos)
#define RCC_APB1SMENR1_USART3SMEN           RCC_APB1SMENR1_USART3SMEN_Msk
#define RCC_APB1SMENR1_UART4SMEN_Pos        (19UL)
#define RCC_APB1SMENR1_UART4SMEN_Msk        (0x1UL << RCC_APB1SMENR1_UART4SMEN_Pos)
#define RCC_APB1SMENR1_UART4SMEN            RCC_APB1SMENR1_UART4SMEN_Msk
#define RCC_APB1SMENR1_UART5SMEN_Pos        (20UL)
#define RCC_APB1SMENR1_UART5SMEN_Msk        (0x1UL << RCC_APB1SMENR1_UART5SMEN_Pos)
#define RCC_APB1SMENR1_UART5SMEN            RCC_APB1SMENR1_UART5SMEN_Msk
#define RCC_APB1SMENR1_I2C1SMEN_Pos         (21UL)
#define RCC_APB1SMENR1_I2C1SMEN_Msk         (0x1UL << RCC_APB1SMENR1_I2C1SMEN_Pos)
#define RCC_APB1SMENR1_I2C1SMEN             RCC_APB1SMENR1_I2C1SMEN_Msk
#define RCC_APB1SMENR1_I2C2SMEN_Pos         (22UL)
#define RCC_APB1SMENR1_I2C2SMEN_Msk         (0x1UL << RCC_APB1SMENR1_I2C2SMEN_Pos)
#define RCC_APB1SMENR1_I2C2SMEN             RCC_APB1SMENR1_I2C2SMEN_Msk
#define RCC_APB1SMENR1_CRSSMEN_Pos          (24UL)
#define RCC_APB1SMENR1_CRSSMEN_Msk          (0x1UL << RCC_APB1SMENR1_CRSSMEN_Pos)
#define RCC_APB1SMENR1_CRSSMEN              RCC_APB1SMENR1_CRSSMEN_Msk
#define RCC_APB1SMENR2_I2C4SMEN_Pos         (1UL)
#define RCC_APB1SMENR2_I2C4SMEN_Msk         (0x1UL << RCC_APB1SMENR2_I2C4SMEN_Pos)
#define RCC_APB1SMENR2_I2C4SMEN             RCC_APB1SMENR2_I2C4SMEN_Msk
#define RCC_APB1SMENR2_LPTIM2SMEN_Pos       (5UL)
#define RCC_APB1SMENR2_LPTIM2SMEN_Msk       (0x1UL << RCC_APB1SMENR2_LPTIM2SMEN_Pos)
#define RCC_APB1SMENR2_LPTIM2SMEN           RCC_APB1SMENR2_LPTIM2SMEN_Msk
#define RCC_APB1SMENR2_FDCAN1SMEN_Pos       (9UL)
#define RCC_APB1SMENR2_FDCAN1SMEN_Msk       (0x1UL << RCC_APB1SMENR2_FDCAN1SMEN_Pos)
#define RCC_APB1SMENR2_FDCAN1SMEN           RCC_APB1SMENR2_FDCAN1SMEN_Msk
#define RCC_APB1SMENR2_UCPD1SMEN_Pos        (23UL)
#define RCC_APB1SMENR2_UCPD1SMEN_Msk        (0x1UL << RCC_APB1SMENR2_UCPD1SMEN_Pos)
#define RCC_APB1SMENR2_UCPD1SMEN            RCC_APB1SMENR2_UCPD1SMEN_Msk
#define RCC_APB2SMENR_TIM1SMEN_Pos          (11UL)
#define RCC_APB2SMENR_TIM1SMEN_Msk          (0x1UL << RCC_APB2SMENR_TIM1SMEN_Pos)
#define RCC_APB2SMENR_TIM1SMEN              RCC_APB2SMENR_TIM1SMEN_Msk
#define RCC_APB2SMENR_SPI1SMEN_Pos          (12UL)
#define RCC_APB2SMENR_SPI1SMEN_Msk          (0x1UL << RCC_APB2SMENR_SPI1SMEN_Pos)
#define RCC_APB2SMENR_SPI1SMEN              RCC_APB2SMENR_SPI1SMEN_Msk
#define RCC_APB2SMENR_TIM8SMEN_Pos          (13UL)
#define RCC_APB2SMENR_TIM8SMEN_Msk          (0x1UL << RCC_APB2SMENR_TIM8SMEN_Pos)
#define RCC_APB2SMENR_TIM8SMEN              RCC_APB2SMENR_TIM8SMEN_Msk
#define RCC_APB2SMENR_USART1SMEN_Pos        (14UL)
#define RCC_APB2SMENR_USART1SMEN_Msk        (0x1UL << RCC_APB2SMENR_USART1SMEN_Pos)
#define RCC_APB2SMENR_USART1SMEN            RCC_APB2SMENR_USART1SMEN_Msk
#define RCC_APB2SMENR_TIM15SMEN_Pos         (16UL)
#define RCC_APB2SMENR_TIM15SMEN_Msk         (0x1UL << RCC_APB2SMENR_TIM15SMEN_Pos)
#define RCC_APB2SMENR_TIM15SMEN             RCC_APB2SMENR_TIM15SMEN_Msk
#define RCC_APB2SMENR_TIM16SMEN_Pos         (17UL)
#define RCC_APB2SMENR_TIM16SMEN_Msk         (0x1UL << RCC_APB2SMENR_TIM16SMEN_Pos)
#define RCC_APB2SMENR_TIM16SMEN             RCC_APB2SMENR_TIM16SMEN_Msk
#define RCC_APB2SMENR_TIM17SMEN_Pos         (18UL)
#define RCC_APB2SMENR_TIM17SMEN_Msk         (0x1UL << RCC_APB2SMENR_TIM17SMEN_Pos)
#define RCC_APB2SMENR_TIM17SMEN             RCC_APB2SMENR_TIM17SMEN_Msk
#define RCC_APB2SMENR_SAI1SMEN_Pos          (21UL)
#define RCC_APB2SMENR_SAI1SMEN_Msk          (0x1UL << RCC_APB2SMENR_SAI1SMEN_Pos)
#define RCC_APB2SMENR_SAI1SMEN              RCC_APB2SMENR_SAI1SMEN_Msk
#define RCC_APB2SMENR_SAI2SMEN_Pos          (22UL)
#define RCC_APB2SMENR_SAI2SMEN_Msk          (0x1UL << RCC_APB2SMENR_SAI2SMEN_Pos)
#define RCC_APB2SMENR_SAI2SMEN              RCC_APB2SMENR_SAI2SMEN_Msk
#define RCC_APB3SMENR_SYSCFGSMEN_Pos        (1UL)
#define RCC_APB3SMENR_SYSCFGSMEN_Msk        (0x1UL << RCC_APB3SMENR_SYSCFGSMEN_Pos)
#define RCC_APB3SMENR_SYSCFGSMEN            RCC_APB3SMENR_SYSCFGSMEN_Msk
#define RCC_APB3SMENR_SPI3SMEN_Pos          (5UL)
#define RCC_APB3SMENR_SPI3SMEN_Msk          (0x1UL << RCC_APB3SMENR_SPI3SMEN_Pos)
#define RCC_APB3SMENR_SPI3SMEN              RCC_APB3SMENR_SPI3SMEN_Msk
#define RCC_APB3SMENR_LPUART1SMEN_Pos       (6UL)
#define RCC_APB3SMENR_LPUART1SMEN_Msk       (0x1UL << RCC_APB3SMENR_LPUART1SMEN_Pos)
#define RCC_APB3SMENR_LPUART1SMEN           RCC_APB3SMENR_LPUART1SMEN_Msk
#define RCC_APB3SMENR_I2C3SMEN_Pos          (7UL)
#define RCC_APB3SMENR_I2C3SMEN_Msk          (0x1UL << RCC_APB3SMENR_I2C3SMEN_Pos)
#define RCC_APB3SMENR_I2C3SMEN              RCC_APB3SMENR_I2C3SMEN_Msk
#define RCC_APB3SMENR_LPTIM1SMEN_Pos        (11UL)
#define RCC_APB3SMENR_LPTIM1SMEN_Msk        (0x1UL << RCC_APB3SMENR_LPTIM1SMEN_Pos)
#define RCC_APB3SMENR_LPTIM1SMEN            RCC_APB3SMENR_LPTIM1SMEN_Msk
#define RCC_APB3SMENR_LPTIM3SMEN_Pos        (12UL)
#define RCC_APB3SMENR_LPTIM3SMEN_Msk        (0x1UL << RCC_APB3SMENR_LPTIM3SMEN_Pos)
#define RCC_APB3SMENR_LPTIM3SMEN            RCC_APB3SMENR_LPTIM3SMEN_Msk
#define RCC_APB3SMENR_LPTIM4SMEN_Pos        (13UL)
#define RCC_APB3SMENR_LPTIM4SMEN_Msk        (0x1UL << RCC_APB3SMENR_LPTIM4SMEN_Pos)
#define RCC_APB3SMENR_LPTIM4SMEN            RCC_APB3SMENR_LPTIM4SMEN_Msk
#define RCC_APB3SMENR_OPAMPSMEN_Pos         (14UL)
#define RCC_APB3SMENR_OPAMPSMEN_Msk         (0x1UL << RCC_APB3SMENR_OPAMPSMEN_Pos)
#define RCC_APB3SMENR_OPAMPSMEN             RCC_APB3SMENR_OPAMPSMEN_Msk
#define RCC_APB3SMENR_COMPSMEN_Pos          (15UL)
#define RCC_APB3SMENR_COMPSMEN_Msk          (0x1UL << RCC_APB3SMENR_COMPSMEN_Pos)
#define RCC_APB3SMENR_COMPSMEN              RCC_APB3SMENR_COMPSMEN_Msk
#define RCC_APB3SMENR_VREFSMEN_Pos          (20UL)
#define RCC_APB3SMENR_VREFSMEN_Msk          (0x1UL << RCC_APB3SMENR_VREFSMEN_Pos)
#define RCC_APB3SMENR_VREFSMEN              RCC_APB3SMENR_VREFSMEN_Msk
#define RCC_APB3SMENR_RTCAPBSMEN_Pos        (21UL)
#define RCC_APB3SMENR_RTCAPBSMEN_Msk        (0x1UL << RCC_APB3SMENR_RTCAPBSMEN_Pos)
#define RCC_APB3SMENR_RTCAPBSMEN            RCC_APB3SMENR_RTCAPBSMEN_Msk
#define RCC_SRDAMR_SPI3AMEN_Pos             (5UL)
#define RCC_SRDAMR_SPI3AMEN_Msk             (0x1UL << RCC_SRDAMR_SPI3AMEN_Pos)
#define RCC_SRDAMR_SPI3AMEN                 RCC_SRDAMR_SPI3AMEN_Msk
#define RCC_SRDAMR_LPUART1AMEN_Pos          (6UL)
#define RCC_SRDAMR_LPUART1AMEN_Msk          (0x1UL << RCC_SRDAMR_LPUART1AMEN_Pos)
#define RCC_SRDAMR_LPUART1AMEN              RCC_SRDAMR_LPUART1AMEN_Msk
#define RCC_SRDAMR_I2C3AMEN_Pos             (7UL)
#define RCC_SRDAMR_I2C3AMEN_Msk             (0x1UL << RCC_SRDAMR_I2C3AMEN_Pos)
#define RCC_SRDAMR_I2C3AMEN                 RCC_SRDAMR_I2C3AMEN_Msk
#define RCC_SRDAMR_LPTIM1AMEN_Pos           (11UL)
#define RCC_SRDAMR_LPTIM1AMEN_Msk           (0x1UL << RCC_SRDAMR_LPTIM1AMEN_Pos)
#define RCC_SRDAMR_LPTIM1AMEN               RCC_SRDAMR_LPTIM1AMEN_Msk
#define RCC_SRDAMR_LPTIM3AMEN_Pos           (12UL)
#define RCC_SRDAMR_LPTIM3AMEN_Msk           (0x1UL << RCC_SRDAMR_LPTIM3AMEN_Pos)
#define RCC_SRDAMR_LPTIM3AMEN               RCC_SRDAMR_LPTIM3AMEN_Msk
#define RCC_SRDAMR_LPTIM4AMEN_Pos           (13UL)
#define RCC_SRDAMR_LPTIM4AMEN_Msk           (0x1UL << RCC_SRDAMR_LPTIM4AMEN_Pos)
#define RCC_SRDAMR_LPTIM4AMEN               RCC_SRDAMR_LPTIM4AMEN_Msk
#define RCC_SRDAMR_OPAMPAMEN_Pos            (14UL)
#define RCC_SRDAMR_OPAMPAMEN_Msk            (0x1UL << RCC_SRDAMR_OPAMPAMEN_Pos)
#define RCC_SRDAMR_OPAMPAMEN                RCC_SRDAMR_OPAMPAMEN_Msk
#define RCC_SRDAMR_COMPAMEN_Pos             (15UL)
#define RCC_SRDAMR_COMPAMEN_Msk             (0x1UL << RCC_SRDAMR_COMPAMEN_Pos)
#define RCC_SRDAMR_COMPAMEN                 RCC_SRDAMR_COMPAMEN_Msk
#define RCC_SRDAMR_VREFAMEN_Pos             (20UL)
#define RCC_SRDAMR_VREFAMEN_Msk             (0x1UL << RCC_SRDAMR_VREFAMEN_Pos)
#define RCC_SRDAMR_VREFAMEN                 RCC_SRDAMR_VREFAMEN_Msk
#define RCC_SRDAMR_RTCAPBAMEN_Pos           (21UL)
#define RCC_SRDAMR_RTCAPBAMEN_Msk           (0x1UL << RCC_SRDAMR_RTCAPBAMEN_Pos)
#define RCC_SRDAMR_RTCAPBAMEN               RCC_SRDAMR_RTCAPBAMEN_Msk
#define RCC_SRDAMR_ADC4AMEN_Pos             (25UL)
#define RCC_SRDAMR_ADC4AMEN_Msk             (0x1UL << RCC_SRDAMR_ADC4AMEN_Pos)
#define RCC_SRDAMR_ADC4AMEN                 RCC_SRDAMR_ADC4AMEN_Msk
#define RCC_SRDAMR_LPGPIO1AMEN_Pos          (26UL)
#define RCC_SRDAMR_LPGPIO1AMEN_Msk          (0x1UL << RCC_SRDAMR_LPGPIO1AMEN_Pos)
#define RCC_SRDAMR_LPGPIO1AMEN              RCC_SRDAMR_LPGPIO1AMEN_Msk
#define RCC_SRDAMR_DAC1AMEN_Pos             (27UL)
#define RCC_SRDAMR_DAC1AMEN_Msk             (0x1UL << RCC_SRDAMR_DAC1AMEN_Pos)
#define RCC_SRDAMR_DAC1AMEN                 RCC_SRDAMR_DAC1AMEN_Msk
#define RCC_SRDAMR_LPDMA1AMEN_Pos           (28UL)
#define RCC_SRDAMR_LPDMA1AMEN_Msk           (0x1UL << RCC_SRDAMR_LPDMA1AMEN_Pos)
#define RCC_SRDAMR_LPDMA1AMEN               RCC_SRDAMR_LPDMA1AMEN_Msk
#define RCC_SRDAMR_ADF1AMEN_Pos             (29UL)
#define RCC_SRDAMR_ADF1AMEN_Msk             (0x1UL << RCC_SRDAMR_ADF1AMEN_Pos)
#define RCC_SRDAMR_ADF1AMEN                 RCC_SRDAMR_ADF1AMEN_Msk
#define RCC_SRDAMR_SRAM4AMEN_Pos            (31UL)
#define RCC_SRDAMR_SRAM4AMEN_Msk            (0x1UL << RCC_SRDAMR_SRAM4AMEN_Pos)
#define RCC_SRDAMR_SRAM4AMEN                RCC_SRDAMR_SRAM4AMEN_Msk
#define RCC_CCIPR1_USART1SEL_Pos            (0UL)
#define RCC_CCIPR1_USART1SEL_Msk            (0x3UL << RCC_CCIPR1_USART1SEL_Pos)
#define RCC_CCIPR1_USART1SEL                RCC_CCIPR1_USART1SEL_Msk
#define RCC_CCIPR1_USART1SEL_0              (0x1UL << RCC_CCIPR1_USART1SEL_Pos)
#define RCC_CCIPR1_USART1SEL_1              (0x2UL << RCC_CCIPR1_USART1SEL_Pos)
#define RCC_CCIPR1_USART2SEL_Pos            (2UL)
#define RCC_CCIPR1_USART2SEL_Msk            (0x3UL << RCC_CCIPR1_USART2SEL_Pos)
#define RCC_CCIPR1_USART2SEL                RCC_CCIPR1_USART2SEL_Msk
#define RCC_CCIPR1_USART2SEL_0              (0x1UL << RCC_CCIPR1_USART2SEL_Pos)
#define RCC_CCIPR1_USART2SEL_1              (0x2UL << RCC_CCIPR1_USART2SEL_Pos)
#define RCC_CCIPR1_USART3SEL_Pos            (4UL)
#define RCC_CCIPR1_USART3SEL_Msk            (0x3UL << RCC_CCIPR1_USART3SEL_Pos)
#define RCC_CCIPR1_USART3SEL                RCC_CCIPR1_USART3SEL_Msk
#define RCC_CCIPR1_USART3SEL_0              (0x1UL << RCC_CCIPR1_USART3SEL_Pos)
#define RCC_CCIPR1_USART3SEL_1              (0x2UL << RCC_CCIPR1_USART3SEL_Pos)
#define RCC_CCIPR1_UART4SEL_Pos             (6UL)
#define RCC_CCIPR1_UART4SEL_Msk             (0x3UL << RCC_CCIPR1_UART4SEL_Pos)
#define RCC_CCIPR1_UART4SEL                 RCC_CCIPR1_UART4SEL_Msk
#define RCC_CCIPR1_UART4SEL_0               (0x1UL << RCC_CCIPR1_UART4SEL_Pos)
#define RCC_CCIPR1_UART4SEL_1               (0x2UL << RCC_CCIPR1_UART4SEL_Pos)
#define RCC_CCIPR1_UART5SEL_Pos             (8UL)
#define RCC_CCIPR1_UART5SEL_Msk             (0x3UL << RCC_CCIPR1_UART5SEL_Pos)
#define RCC_CCIPR1_UART5SEL                 RCC_CCIPR1_UART5SEL_Msk
#define RCC_CCIPR1_UART5SEL_0               (0x1UL << RCC_CCIPR1_UART5SEL_Pos)
#define RCC_CCIPR1_UART5SEL_1               (0x2UL << RCC_CCIPR1_UART5SEL_Pos)
#define RCC_CCIPR1_I2C1SEL_Pos              (10UL)
#define RCC_CCIPR1_I2C1SEL_Msk              (0x3UL << RCC_CCIPR1_I2C1SEL_Pos)
#define RCC_CCIPR1_I2C1SEL                  RCC_CCIPR1_I2C1SEL_Msk
#define RCC_CCIPR1_I2C1SEL_0                (0x1UL << RCC_CCIPR1_I2C1SEL_Pos)
#define RCC_CCIPR1_I2C1SEL_1                (0x2UL << RCC_CCIPR1_I2C1SEL_Pos)
#define RCC_CCIPR1_I2C2SEL_Pos              (12UL)
#define RCC_CCIPR1_I2C2SEL_Msk              (0x3UL << RCC_CCIPR1_I2C2SEL_Pos)
#define RCC_CCIPR1_I2C2SEL                  RCC_CCIPR1_I2C2SEL_Msk
#define RCC_CCIPR1_I2C2SEL_0                (0x1UL << RCC_CCIPR1_I2C2SEL_Pos)
#define RCC_CCIPR1_I2C2SEL_1                (0x2UL << RCC_CCIPR1_I2C2SEL_Pos)
#define RCC_CCIPR1_I2C4SEL_Pos              (14UL)
#define RCC_CCIPR1_I2C4SEL_Msk              (0x3UL << RCC_CCIPR1_I2C4SEL_Pos)
#define RCC_CCIPR1_I2C4SEL                  RCC_CCIPR1_I2C4SEL_Msk
#define RCC_CCIPR1_I2C4SEL_0                (0x1UL << RCC_CCIPR1_I2C4SEL_Pos)
#define RCC_CCIPR1_I2C4SEL_1                (0x2UL << RCC_CCIPR1_I2C4SEL_Pos)
#define RCC_CCIPR1_SPI2SEL_Pos              (16UL)
#define RCC_CCIPR1_SPI2SEL_Msk              (0x3UL << RCC_CCIPR1_SPI2SEL_Pos)
#define RCC_CCIPR1_SPI2SEL                  RCC_CCIPR1_SPI2SEL_Msk
#define RCC_CCIPR1_SPI2SEL_0                (0x1UL << RCC_CCIPR1_SPI2SEL_Pos)
#define RCC_CCIPR1_SPI2SEL_1                (0x2UL << RCC_CCIPR1_SPI2SEL_Pos)
#define RCC_CCIPR1_LPTIM2SEL_Pos            (18UL)
#define RCC_CCIPR1_LPTIM2SEL_Msk            (0x3UL << RCC_CCIPR1_LPTIM2SEL_Pos)
#define RCC_CCIPR1_LPTIM2SEL                RCC_CCIPR1_LPTIM2SEL_Msk
#define RCC_CCIPR1_LPTIM2SEL_0              (0x1UL << RCC_CCIPR1_LPTIM2SEL_Pos)
#define RCC_CCIPR1_LPTIM2SEL_1              (0x2UL << RCC_CCIPR1_LPTIM2SEL_Pos)
#define RCC_CCIPR1_SPI1SEL_Pos              (20UL)
#define RCC_CCIPR1_SPI1SEL_Msk              (0x3UL << RCC_CCIPR1_SPI1SEL_Pos)
#define RCC_CCIPR1_SPI1SEL                  RCC_CCIPR1_SPI1SEL_Msk
#define RCC_CCIPR1_SPI1SEL_0                (0x1UL << RCC_CCIPR1_SPI1SEL_Pos)
#define RCC_CCIPR1_SPI1SEL_1                (0x2UL << RCC_CCIPR1_SPI1SEL_Pos)
#define RCC_CCIPR1_SYSTICKSEL_Pos           (22UL)
#define RCC_CCIPR1_SYSTICKSEL_Msk           (0x3UL << RCC_CCIPR1_SYSTICKSEL_Pos)
#define RCC_CCIPR1_SYSTICKSEL               RCC_CCIPR1_SYSTICKSEL_Msk
#define RCC_CCIPR1_SYSTICKSEL_0             (0x1UL << RCC_CCIPR1_SYSTICKSEL_Pos)
#define RCC_CCIPR1_SYSTICKSEL_1             (0x2UL << RCC_CCIPR1_SYSTICKSEL_Pos)
#define RCC_CCIPR1_FDCANSEL_Pos             (24UL)
#define RCC_CCIPR1_FDCANSEL_Msk             (0x3UL << RCC_CCIPR1_FDCANSEL_Pos)
#define RCC_CCIPR1_FDCANSEL                 RCC_CCIPR1_FDCANSEL_Msk
#define RCC_CCIPR1_FDCANSEL_0               (0x1UL << RCC_CCIPR1_FDCANSEL_Pos)
#define RCC_CCIPR1_FDCANSEL_1               (0x2UL << RCC_CCIPR1_FDCANSEL_Pos)
#define RCC_CCIPR1_ICLKSEL_Pos              (26UL)
#define RCC_CCIPR1_ICLKSEL_Msk              (0x3UL << RCC_CCIPR1_ICLKSEL_Pos)
#define RCC_CCIPR1_ICLKSEL                  RCC_CCIPR1_ICLKSEL_Msk
#define RCC_CCIPR1_ICLKSEL_0                (0x1UL << RCC_CCIPR1_ICLKSEL_Pos)
#define RCC_CCIPR1_ICLKSEL_1                (0x2UL << RCC_CCIPR1_ICLKSEL_Pos)
#define RCC_CCIPR1_TIMICSEL_Pos             (29UL)
#define RCC_CCIPR1_TIMICSEL_Msk             (0x7UL << RCC_CCIPR1_TIMICSEL_Pos)
#define RCC_CCIPR1_TIMICSEL                 RCC_CCIPR1_TIMICSEL_Msk
#define RCC_CCIPR1_TIMICSEL_0               (0x1UL << RCC_CCIPR1_TIMICSEL_Pos)
#define RCC_CCIPR1_TIMICSEL_1               (0x2UL << RCC_CCIPR1_TIMICSEL_Pos)
#define RCC_CCIPR1_TIMICSEL_2               (0x4UL << RCC_CCIPR1_TIMICSEL_Pos)
#define RCC_CCIPR2_MDF1SEL_Pos              (0UL)
#define RCC_CCIPR2_MDF1SEL_Msk              (0x7UL << RCC_CCIPR2_MDF1SEL_Pos)
#define RCC_CCIPR2_MDF1SEL                  RCC_CCIPR2_MDF1SEL_Msk
#define RCC_CCIPR2_MDF1SEL_0                (0x1UL << RCC_CCIPR2_MDF1SEL_Pos)
#define RCC_CCIPR2_MDF1SEL_1                (0x2UL << RCC_CCIPR2_MDF1SEL_Pos)
#define RCC_CCIPR2_MDF1SEL_2                (0x4UL << RCC_CCIPR2_MDF1SEL_Pos)
#define RCC_CCIPR2_SAI1SEL_Pos              (5UL)
#define RCC_CCIPR2_SAI1SEL_Msk              (0x7UL << RCC_CCIPR2_SAI1SEL_Pos)
#define RCC_CCIPR2_SAI1SEL                  RCC_CCIPR2_SAI1SEL_Msk
#define RCC_CCIPR2_SAI1SEL_0                (0x1UL << RCC_CCIPR2_SAI1SEL_Pos)
#define RCC_CCIPR2_SAI1SEL_1                (0x2UL << RCC_CCIPR2_SAI1SEL_Pos)
#define RCC_CCIPR2_SAI1SEL_2                (0x4UL << RCC_CCIPR2_SAI1SEL_Pos)
#define RCC_CCIPR2_SAI2SEL_Pos              (8UL)
#define RCC_CCIPR2_SAI2SEL_Msk              (0x7UL << RCC_CCIPR2_SAI2SEL_Pos)
#define RCC_CCIPR2_SAI2SEL                  RCC_CCIPR2_SAI2SEL_Msk
#define RCC_CCIPR2_SAI2SEL_0                (0x1UL << RCC_CCIPR2_SAI2SEL_Pos)
#define RCC_CCIPR2_SAI2SEL_1                (0x2UL << RCC_CCIPR2_SAI2SEL_Pos)
#define RCC_CCIPR2_SAI2SEL_2                (0x4UL << RCC_CCIPR2_SAI2SEL_Pos)
#define RCC_CCIPR2_SAESSEL_Pos              (11UL)
#define RCC_CCIPR2_SAESSEL_Msk              (0x1UL << RCC_CCIPR2_SAESSEL_Pos)
#define RCC_CCIPR2_SAESSEL                  RCC_CCIPR2_SAESSEL_Msk
#define RCC_CCIPR2_RNGSEL_Pos               (12UL)
#define RCC_CCIPR2_RNGSEL_Msk               (0x3UL << RCC_CCIPR2_RNGSEL_Pos)
#define RCC_CCIPR2_RNGSEL                   RCC_CCIPR2_RNGSEL_Msk
#define RCC_CCIPR2_RNGSEL_0                 (0x1UL << RCC_CCIPR2_RNGSEL_Pos)
#define RCC_CCIPR2_RNGSEL_1                 (0x2UL << RCC_CCIPR2_RNGSEL_Pos)
#define RCC_CCIPR2_SDMMCSEL_Pos             (14UL)
#define RCC_CCIPR2_SDMMCSEL_Msk             (0x1UL << RCC_CCIPR2_SDMMCSEL_Pos)
#define RCC_CCIPR2_SDMMCSEL                 RCC_CCIPR2_SDMMCSEL_Msk
#define RCC_CCIPR2_OCTOSPISEL_Pos           (20UL)
#define RCC_CCIPR2_OCTOSPISEL_Msk           (0x3UL << RCC_CCIPR2_OCTOSPISEL_Pos)
#define RCC_CCIPR2_OCTOSPISEL               RCC_CCIPR2_OCTOSPISEL_Msk
#define RCC_CCIPR2_OCTOSPISEL_0             (0x1UL << RCC_CCIPR2_OCTOSPISEL_Pos)
#define RCC_CCIPR2_OCTOSPISEL_1             (0x2UL << RCC_CCIPR2_OCTOSPISEL_Pos)
#define RCC_CCIPR3_LPUART1SEL_Pos           (0UL)
#define RCC_CCIPR3_LPUART1SEL_Msk           (0x7UL << RCC_CCIPR3_LPUART1SEL_Pos)
#define RCC_CCIPR3_LPUART1SEL               RCC_CCIPR3_LPUART1SEL_Msk
#define RCC_CCIPR3_LPUART1SEL_0             (0x1UL << RCC_CCIPR3_LPUART1SEL_Pos)
#define RCC_CCIPR3_LPUART1SEL_1             (0x2UL << RCC_CCIPR3_LPUART1SEL_Pos)
#define RCC_CCIPR3_LPUART1SEL_2             (0x4UL << RCC_CCIPR3_LPUART1SEL_Pos)
#define RCC_CCIPR3_SPI3SEL_Pos              (3UL)
#define RCC_CCIPR3_SPI3SEL_Msk              (0x3UL << RCC_CCIPR3_SPI3SEL_Pos)
#define RCC_CCIPR3_SPI3SEL                  RCC_CCIPR3_SPI3SEL_Msk
#define RCC_CCIPR3_SPI3SEL_0                (0x1UL << RCC_CCIPR3_SPI3SEL_Pos)
#define RCC_CCIPR3_SPI3SEL_1                (0x2UL << RCC_CCIPR3_SPI3SEL_Pos)
#define RCC_CCIPR3_I2C3SEL_Pos              (6UL)
#define RCC_CCIPR3_I2C3SEL_Msk              (0x3UL << RCC_CCIPR3_I2C3SEL_Pos)
#define RCC_CCIPR3_I2C3SEL                  RCC_CCIPR3_I2C3SEL_Msk
#define RCC_CCIPR3_I2C3SEL_0                (0x1UL << RCC_CCIPR3_I2C3SEL_Pos)
#define RCC_CCIPR3_I2C3SEL_1                (0x2UL << RCC_CCIPR3_I2C3SEL_Pos)
#define RCC_CCIPR3_LPTIM34SEL_Pos           (8UL)
#define RCC_CCIPR3_LPTIM34SEL_Msk           (0x3UL << RCC_CCIPR3_LPTIM34SEL_Pos)
#define RCC_CCIPR3_LPTIM34SEL               RCC_CCIPR3_LPTIM34SEL_Msk
#define RCC_CCIPR3_LPTIM34SEL_0             (0x1UL << RCC_CCIPR3_LPTIM34SEL_Pos)
#define RCC_CCIPR3_LPTIM34SEL_1             (0x2UL << RCC_CCIPR3_LPTIM34SEL_Pos)
#define RCC_CCIPR3_LPTIM1SEL_Pos            (10UL)
#define RCC_CCIPR3_LPTIM1SEL_Msk            (0x3UL << RCC_CCIPR3_LPTIM1SEL_Pos)
#define RCC_CCIPR3_LPTIM1SEL                RCC_CCIPR3_LPTIM1SEL_Msk
#define RCC_CCIPR3_LPTIM1SEL_0              (0x1UL << RCC_CCIPR3_LPTIM1SEL_Pos)
#define RCC_CCIPR3_LPTIM1SEL_1              (0x2UL << RCC_CCIPR3_LPTIM1SEL_Pos)
#define RCC_CCIPR3_ADCDACSEL_Pos            (12UL)
#define RCC_CCIPR3_ADCDACSEL_Msk            (0x7UL << RCC_CCIPR3_ADCDACSEL_Pos)
#define RCC_CCIPR3_ADCDACSEL                RCC_CCIPR3_ADCDACSEL_Msk
#define RCC_CCIPR3_ADCDACSEL_0              (0x1UL << RCC_CCIPR3_ADCDACSEL_Pos)
#define RCC_CCIPR3_ADCDACSEL_1              (0x2UL << RCC_CCIPR3_ADCDACSEL_Pos)
#define RCC_CCIPR3_ADCDACSEL_2              (0x4UL << RCC_CCIPR3_ADCDACSEL_Pos)
#define RCC_CCIPR3_DAC1SEL_Pos              (15UL)
#define RCC_CCIPR3_DAC1SEL_Msk              (0x1UL << RCC_CCIPR3_DAC1SEL_Pos)
#define RCC_CCIPR3_DAC1SEL                  RCC_CCIPR3_DAC1SEL_Msk
#define RCC_CCIPR3_ADF1SEL_Pos              (16UL)
#define RCC_CCIPR3_ADF1SEL_Msk              (0x7UL << RCC_CCIPR3_ADF1SEL_Pos)
#define RCC_CCIPR3_ADF1SEL                  RCC_CCIPR3_ADF1SEL_Msk
#define RCC_CCIPR3_ADF1SEL_0                (0x1UL << RCC_CCIPR3_ADF1SEL_Pos)
#define RCC_CCIPR3_ADF1SEL_1                (0x2UL << RCC_CCIPR3_ADF1SEL_Pos)
#define RCC_CCIPR3_ADF1SEL_2                (0x4UL << RCC_CCIPR3_ADF1SEL_Pos)
#define RCC_BDCR_LSEON_Pos                  (0UL)
#define RCC_BDCR_LSEON_Msk                  (0x1UL << RCC_BDCR_LSEON_Pos)
#define RCC_BDCR_LSEON                      RCC_BDCR_LSEON_Msk
#define RCC_BDCR_LSERDY_Pos                 (1UL)
#define RCC_BDCR_LSERDY_Msk                 (0x1UL << RCC_BDCR_LSERDY_Pos)
#define RCC_BDCR_LSERDY                     RCC_BDCR_LSERDY_Msk
#define RCC_BDCR_LSEBYP_Pos                 (2UL)
#define RCC_BDCR_LSEBYP_Msk                 (0x1UL << RCC_BDCR_LSEBYP_Pos)
#define RCC_BDCR_LSEBYP                     RCC_BDCR_LSEBYP_Msk
#define RCC_BDCR_LSEDRV_Pos                 (3UL)
#define RCC_BDCR_LSEDRV_Msk                 (0x3UL << RCC_BDCR_LSEDRV_Pos)
#define RCC_BDCR_LSEDRV                     RCC_BDCR_LSEDRV_Msk
#define RCC_BDCR_LSEDRV_0                   (0x1UL << RCC_BDCR_LSEDRV_Pos)
#define RCC_BDCR_LSEDRV_1                   (0x2UL << RCC_BDCR_LSEDRV_Pos)
#define RCC_BDCR_LSECSSON_Pos               (5UL)
#define RCC_BDCR_LSECSSON_Msk               (0x1UL << RCC_BDCR_LSECSSON_Pos)
#define RCC_BDCR_LSECSSON                   RCC_BDCR_LSECSSON_Msk
#define RCC_BDCR_LSECSSD_Pos                (6UL)
#define RCC_BDCR_LSECSSD_Msk                (0x1UL << RCC_BDCR_LSECSSD_Pos)
#define RCC_BDCR_LSECSSD                    RCC_BDCR_LSECSSD_Msk
#define RCC_BDCR_LSESYSEN_Pos               (7UL)
#define RCC_BDCR_LSESYSEN_Msk               (0x1UL << RCC_BDCR_LSESYSEN_Pos)
#define RCC_BDCR_LSESYSEN                   RCC_BDCR_LSESYSEN_Msk
#define RCC_BDCR_RTCSEL_Pos                 (8UL)
#define RCC_BDCR_RTCSEL_Msk                 (0x3UL << RCC_BDCR_RTCSEL_Pos)
#define RCC_BDCR_RTCSEL                     RCC_BDCR_RTCSEL_Msk
#define RCC_BDCR_RTCSEL_0                   (0x1UL << RCC_BDCR_RTCSEL_Pos)
#define RCC_BDCR_RTCSEL_1                   (0x2UL << RCC_BDCR_RTCSEL_Pos)
#define RCC_BDCR_LSESYSRDY_Pos              (11UL)
#define RCC_BDCR_LSESYSRDY_Msk              (0x1UL << RCC_BDCR_LSESYSRDY_Pos)
#define RCC_BDCR_LSESYSRDY                  RCC_BDCR_LSESYSRDY_Msk
#define RCC_BDCR_LSEGFON_Pos                (12UL)
#define RCC_BDCR_LSEGFON_Msk                (0x1UL << RCC_BDCR_LSEGFON_Pos)
#define RCC_BDCR_LSEGFON                    RCC_BDCR_LSEGFON_Msk
#define RCC_BDCR_RTCEN_Pos                  (15UL)
#define RCC_BDCR_RTCEN_Msk                  (0x1UL << RCC_BDCR_RTCEN_Pos)
#define RCC_BDCR_RTCEN                      RCC_BDCR_RTCEN_Msk
#define RCC_BDCR_BDRST_Pos                  (16UL)
#define RCC_BDCR_BDRST_Msk                  (0x1UL << RCC_BDCR_BDRST_Pos)
#define RCC_BDCR_BDRST                      RCC_BDCR_BDRST_Msk
#define RCC_BDCR_LSCOEN_Pos                 (24UL)
#define RCC_BDCR_LSCOEN_Msk                 (0x1UL << RCC_BDCR_LSCOEN_Pos)
#define RCC_BDCR_LSCOEN                     RCC_BDCR_LSCOEN_Msk
#define RCC_BDCR_LSCOSEL_Pos                (25UL)
#define RCC_BDCR_LSCOSEL_Msk                (0x1UL << RCC_BDCR_LSCOSEL_Pos)
#define RCC_BDCR_LSCOSEL                    RCC_BDCR_LSCOSEL_Msk
#define RCC_BDCR_LSION_Pos                  (26UL)
#define RCC_BDCR_LSION_Msk                  (0x1UL << RCC_BDCR_LSION_Pos)
#define RCC_BDCR_LSION                      RCC_BDCR_LSION_Msk
#define RCC_BDCR_LSIRDY_Pos                 (27UL)
#define RCC_BDCR_LSIRDY_Msk                 (0x1UL << RCC_BDCR_LSIRDY_Pos)
#define RCC_BDCR_LSIRDY                     RCC_BDCR_LSIRDY_Msk
#define RCC_BDCR_LSIPREDIV_Pos              (28UL)
#define RCC_BDCR_LSIPREDIV_Msk              (0x1UL << RCC_BDCR_LSIPREDIV_Pos)
#define RCC_BDCR_LSIPREDIV                  RCC_BDCR_LSIPREDIV_Msk
#define RCC_CSR_MSIKSRANGE_Pos              (8UL)
#define RCC_CSR_MSIKSRANGE_Msk              (0xFUL << RCC_CSR_MSIKSRANGE_Pos)
#define RCC_CSR_MSIKSRANGE                  RCC_CSR_MSIKSRANGE_Msk
#define RCC_CSR_MSIKSRANGE_0                (0x1UL << RCC_CSR_MSIKSRANGE_Pos)
#define RCC_CSR_MSIKSRANGE_1                (0x2UL << RCC_CSR_MSIKSRANGE_Pos)
#define RCC_CSR_MSIKSRANGE_2                (0x4UL << RCC_CSR_MSIKSRANGE_Pos)
#define RCC_CSR_MSIKSRANGE_3                (0x8UL << RCC_CSR_MSIKSRANGE_Pos)
#define RCC_CSR_MSISSRANGE_Pos              (12UL)
#define RCC_CSR_MSISSRANGE_Msk              (0xFUL << RCC_CSR_MSISSRANGE_Pos)
#define RCC_CSR_MSISSRANGE                  RCC_CSR_MSISSRANGE_Msk
#define RCC_CSR_MSISSRANGE_0                (0x1UL << RCC_CSR_MSISSRANGE_Pos)
#define RCC_CSR_MSISSRANGE_1                (0x2UL << RCC_CSR_MSISSRANGE_Pos)
#define RCC_CSR_MSISSRANGE_2                (0x4UL << RCC_CSR_MSISSRANGE_Pos)
#define RCC_CSR_MSISSRANGE_3                (0x8UL << RCC_CSR_MSISSRANGE_Pos)
#define RCC_CSR_RMVF_Pos                    (23UL)
#define RCC_CSR_RMVF_Msk                    (0x1UL << RCC_CSR_RMVF_Pos)
#define RCC_CSR_RMVF                        RCC_CSR_RMVF_Msk
#define RCC_CSR_OBLRSTF_Pos                 (25UL)
#define RCC_CSR_OBLRSTF_Msk                 (0x1UL << RCC_CSR_OBLRSTF_Pos)
#define RCC_CSR_OBLRSTF                     RCC_CSR_OBLRSTF_Msk
#define RCC_CSR_PINRSTF_Pos                 (26UL)
#define RCC_CSR_PINRSTF_Msk                 (0x1UL << RCC_CSR_PINRSTF_Pos)
#define RCC_CSR_PINRSTF                     RCC_CSR_PINRSTF_Msk
#define RCC_CSR_BORRSTF_Pos                 (27UL)
#define RCC_CSR_BORRSTF_Msk                 (0x1UL << RCC_CSR_BORRSTF_Pos)
#define RCC_CSR_BORRSTF                     RCC_CSR_BORRSTF_Msk
#define RCC_CSR_SFTRSTF_Pos                 (28UL)
#define RCC_CSR_SFTRSTF_Msk                 (0x1UL << RCC_CSR_SFTRSTF_Pos)
#define RCC_CSR_SFTRSTF                     RCC_CSR_SFTRSTF_Msk
#define RCC_CSR_IWDGRSTF_Pos                (29UL)
#define RCC_CSR_IWDGRSTF_Msk                (0x1UL << RCC_CSR_IWDGRSTF_Pos)
#define RCC_CSR_IWDGRSTF                    RCC_CSR_IWDGRSTF_Msk
#define RCC_CSR_WWDGRSTF_Pos                (30UL)
#define RCC_CSR_WWDGRSTF_Msk                (0x1UL << RCC_CSR_WWDGRSTF_Pos)
#define RCC_CSR_WWDGRSTF                    RCC_CSR_WWDGRSTF_Msk
#define RCC_CSR_LPWRRSTF_Pos                (31UL)
#define RCC_CSR_LPWRRSTF_Msk                (0x1UL << RCC_CSR_LPWRRSTF_Pos)
#define RCC_CSR_LPWRRSTF                    RCC_CSR_LPWRRSTF_Msk
#define RCC_SECCFGR_HSISEC_Pos              (0UL)
#define RCC_SECCFGR_HSISEC_Msk              (0x1UL << RCC_SECCFGR_HSISEC_Pos)
#define RCC_SECCFGR_HSISEC                  RCC_SECCFGR_HSISEC_Msk
#define RCC_SECCFGR_HSESEC_Pos              (1UL)
#define RCC_SECCFGR_HSESEC_Msk              (0x1UL << RCC_SECCFGR_HSESEC_Pos)
#define RCC_SECCFGR_HSESEC                  RCC_SECCFGR_HSESEC_Msk
#define RCC_SECCFGR_MSISEC_Pos              (2UL)
#define RCC_SECCFGR_MSISEC_Msk              (0x1UL << RCC_SECCFGR_MSISEC_Pos)
#define RCC_SECCFGR_MSISEC                  RCC_SECCFGR_MSISEC_Msk
#define RCC_SECCFGR_LSISEC_Pos              (3UL)
#define RCC_SECCFGR_LSISEC_Msk              (0x1UL << RCC_SECCFGR_LSISEC_Pos)
#define RCC_SECCFGR_LSISEC                  RCC_SECCFGR_LSISEC_Msk
#define RCC_SECCFGR_LSESEC_Pos              (4UL)
#define RCC_SECCFGR_LSESEC_Msk              (0x1UL << RCC_SECCFGR_LSESEC_Pos)
#define RCC_SECCFGR_LSESEC                  RCC_SECCFGR_LSESEC_Msk
#define RCC_SECCFGR_SYSCLKSEC_Pos           (5UL)
#define RCC_SECCFGR_SYSCLKSEC_Msk           (0x1UL << RCC_SECCFGR_SYSCLKSEC_Pos)
#define RCC_SECCFGR_SYSCLKSEC               RCC_SECCFGR_SYSCLKSEC_Msk
#define RCC_SECCFGR_PRESCSEC_Pos            (6UL)
#define RCC_SECCFGR_PRESCSEC_Msk            (0x1UL << RCC_SECCFGR_PRESCSEC_Pos)
#define RCC_SECCFGR_PRESCSEC                RCC_SECCFGR_PRESCSEC_Msk
#define RCC_SECCFGR_PLL1SEC_Pos             (7UL)
#define RCC_SECCFGR_PLL1SEC_Msk             (0x1UL << RCC_SECCFGR_PLL1SEC_Pos)
#define RCC_SECCFGR_PLL1SEC                 RCC_SECCFGR_PLL1SEC_Msk
#define RCC_SECCFGR_PLL2SEC_Pos             (8UL)
#define RCC_SECCFGR_PLL2SEC_Msk             (0x1UL << RCC_SECCFGR_PLL2SEC_Pos)
#define RCC_SECCFGR_PLL2SEC                 RCC_SECCFGR_PLL2SEC_Msk
#define RCC_SECCFGR_PLL3SEC_Pos             (9UL)
#define RCC_SECCFGR_PLL3SEC_Msk             (0x1UL << RCC_SECCFGR_PLL3SEC_Pos)
#define RCC_SECCFGR_PLL3SEC                 RCC_SECCFGR_PLL3SEC_Msk
#define RCC_SECCFGR_ICLKSEC_Pos             (10UL)
#define RCC_SECCFGR_ICLKSEC_Msk             (0x1UL << RCC_SECCFGR_ICLKSEC_Pos)
#define RCC_SECCFGR_ICLKSEC                 RCC_SECCFGR_ICLKSEC_Msk
#define RCC_SECCFGR_HSI48SEC_Pos            (11UL)
#define RCC_SECCFGR_HSI48SEC_Msk            (0x1UL << RCC_SECCFGR_HSI48SEC_Pos)
#define RCC_SECCFGR_HSI48SEC                RCC_SECCFGR_HSI48SEC_Msk
#define RCC_SECCFGR_RMVFSEC_Pos             (12UL)
#define RCC_SECCFGR_RMVFSEC_Msk             (0x1UL << RCC_SECCFGR_RMVFSEC_Pos)
#define RCC_SECCFGR_RMVFSEC                 RCC_SECCFGR_RMVFSEC_Msk
#define RCC_PRIVCFGR_SPRIV_Pos              (0UL)
#define RCC_PRIVCFGR_SPRIV_Msk              (0x1UL << RCC_PRIVCFGR_SPRIV_Pos)
#define RCC_PRIVCFGR_SPRIV                  RCC_PRIVCFGR_SPRIV_Msk
#define RCC_PRIVCFGR_NSPRIV_Pos             (1UL)
#define RCC_PRIVCFGR_NSPRIV_Msk             (0x1UL << RCC_PRIVCFGR_NSPRIV_Pos)
#define RCC_PRIVCFGR_NSPRIV                 RCC_PRIVCFGR_NSPRIV_Msk

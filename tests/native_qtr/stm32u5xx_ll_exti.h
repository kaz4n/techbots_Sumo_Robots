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
#include "native_cmsis.h"
#define LL_EXTI_REGISTER_PINPOS_SHFT        16U
#define LL_EXTI_LINE_0                 EXTI_IMR1_IM0
#define LL_EXTI_LINE_1                 EXTI_IMR1_IM1
#define LL_EXTI_LINE_2                 EXTI_IMR1_IM2
#define LL_EXTI_LINE_3                 EXTI_IMR1_IM3
#define LL_EXTI_LINE_4                 EXTI_IMR1_IM4
#define LL_EXTI_LINE_5                 EXTI_IMR1_IM5
#define LL_EXTI_LINE_6                 EXTI_IMR1_IM6
#define LL_EXTI_LINE_7                 EXTI_IMR1_IM7
#define LL_EXTI_LINE_8                 EXTI_IMR1_IM8
#define LL_EXTI_LINE_9                 EXTI_IMR1_IM9
#define LL_EXTI_LINE_10               EXTI_IMR1_IM10
#define LL_EXTI_LINE_11               EXTI_IMR1_IM11
#define LL_EXTI_LINE_12               EXTI_IMR1_IM12
#define LL_EXTI_LINE_13               EXTI_IMR1_IM13
#define LL_EXTI_LINE_14               EXTI_IMR1_IM14
#define LL_EXTI_LINE_15               EXTI_IMR1_IM15
#define LL_EXTI_LINE_16               EXTI_IMR1_IM16
#define LL_EXTI_LINE_17               EXTI_IMR1_IM17
#define LL_EXTI_LINE_18               EXTI_IMR1_IM18
#define LL_EXTI_LINE_19               EXTI_IMR1_IM19
#define LL_EXTI_LINE_20               EXTI_IMR1_IM20
#define LL_EXTI_LINE_21               EXTI_IMR1_IM21
#define LL_EXTI_LINE_22               EXTI_IMR1_IM22
#define LL_EXTI_LINE_23               EXTI_IMR1_IM23
#define LL_EXTI_LINE_24               EXTI_IMR1_IM24
#define LL_EXTI_LINE_25               EXTI_IMR1_IM25
#define LL_EXTI_LINE_NONE              0x00000000U
#define LL_EXTI_EXTI_PORTA               0U
#define LL_EXTI_EXTI_PORTB               EXTI_EXTICR1_EXTI0_0
#define LL_EXTI_EXTI_PORTC               EXTI_EXTICR1_EXTI0_1
#define LL_EXTI_EXTI_PORTD               (EXTI_EXTICR1_EXTI0_1|EXTI_EXTICR1_EXTI0_0)
#define LL_EXTI_EXTI_PORTE               EXTI_EXTICR1_EXTI0_2
#define LL_EXTI_EXTI_PORTF               (EXTI_EXTICR1_EXTI0_2|EXTI_EXTICR1_EXTI0_0)
#define LL_EXTI_EXTI_PORTG               (EXTI_EXTICR1_EXTI0_2|EXTI_EXTICR1_EXTI0_1)
#define LL_EXTI_EXTI_PORTH               (EXTI_EXTICR1_EXTI0_2|EXTI_EXTICR1_EXTI0_1|EXTI_EXTICR1_EXTI0_0)
#define LL_EXTI_EXTI_PORTI               EXTI_EXTICR1_EXTI0_3
#define LL_EXTI_EXTI_PORTJ               (EXTI_EXTICR1_EXTI0_3 | EXTI_EXTICR1_EXTI0_0)
#define LL_EXTI_EXTI_LINE0               ((0U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 0U)
#define LL_EXTI_EXTI_LINE1               ((8U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 0U)
#define LL_EXTI_EXTI_LINE2               ((16U << LL_EXTI_REGISTER_PINPOS_SHFT) | 0U)
#define LL_EXTI_EXTI_LINE3               ((24U << LL_EXTI_REGISTER_PINPOS_SHFT) | 0U)
#define LL_EXTI_EXTI_LINE4               ((0U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 1U)
#define LL_EXTI_EXTI_LINE5               ((8U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 1U)
#define LL_EXTI_EXTI_LINE6               ((16U << LL_EXTI_REGISTER_PINPOS_SHFT) | 1U)
#define LL_EXTI_EXTI_LINE7               ((24U << LL_EXTI_REGISTER_PINPOS_SHFT) | 1U)
#define LL_EXTI_EXTI_LINE8               ((0U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 2U)
#define LL_EXTI_EXTI_LINE9               ((8U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 2U)
#define LL_EXTI_EXTI_LINE10              ((16U << LL_EXTI_REGISTER_PINPOS_SHFT) | 2U)
#define LL_EXTI_EXTI_LINE11              ((24U << LL_EXTI_REGISTER_PINPOS_SHFT) | 2U)
#define LL_EXTI_EXTI_LINE12              ((0U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 3U)
#define LL_EXTI_EXTI_LINE13              ((8U  << LL_EXTI_REGISTER_PINPOS_SHFT) | 3U)
#define LL_EXTI_EXTI_LINE14              ((16U << LL_EXTI_REGISTER_PINPOS_SHFT) | 3U)
#define LL_EXTI_EXTI_LINE15              ((24U << LL_EXTI_REGISTER_PINPOS_SHFT) | 3U)
#define LL_EXTI_MODE_IT                 ((uint8_t)0x00U)
#define LL_EXTI_MODE_EVENT              ((uint8_t)0x01U)
#define LL_EXTI_MODE_IT_EVENT           ((uint8_t)0x02U)
#define LL_EXTI_TRIGGER_NONE            ((uint8_t)0x00U)
#define LL_EXTI_TRIGGER_RISING          ((uint8_t)0x01U)
#define LL_EXTI_TRIGGER_FALLING         ((uint8_t)0x02U)
#define LL_EXTI_TRIGGER_RISING_FALLING  ((uint8_t)0x03U)
#define LL_EXTI_WriteReg(__REG__, __VALUE__) WRITE_REG(EXTI->__REG__, (__VALUE__))
#define LL_EXTI_ReadReg(__REG__) READ_REG(EXTI->__REG__)
#if defined(EXTI_IMR1_IM24) && defined(EXTI_IMR1_IM25)
#define LL_EXTI_LINE_ALL_0_31 0x03FFFFFFU
#else
#define LL_EXTI_LINE_ALL_0_31 0x00FFFFFFU
#endif
inline uint32_t LL_EXTI_GetEXTISource(uint32_t Line)
{
  return (uint32_t)(READ_BIT(EXTI->EXTICR[Line & 0x03U],
                             (EXTI_EXTICR1_EXTI0 << (Line >> LL_EXTI_REGISTER_PINPOS_SHFT))) >>
                    (Line >> LL_EXTI_REGISTER_PINPOS_SHFT));
}

// Copies source-verified installed STM32U585 declarations.
// Four-byte observable storage preserves native offsets and command encodings.
// Independent B5 tests supply hardware side effects and fault injection.
#pragma once
/* Copyright (c) 2021 STMicroelectronics. All rights reserved.
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 * Extracted from the exact installed headers retained with hashes in
 * state/analysis/P2_adc_ownership_raw/headers/manifest.json.
 */
#include "native_cmsis.h"
#define LL_GPIO_PIN_0                      GPIO_BSRR_BS0
#define LL_GPIO_PIN_1                      GPIO_BSRR_BS1
#define LL_GPIO_PIN_2                      GPIO_BSRR_BS2
#define LL_GPIO_PIN_3                      GPIO_BSRR_BS3
#define LL_GPIO_PIN_4                      GPIO_BSRR_BS4
#define LL_GPIO_PIN_5                      GPIO_BSRR_BS5
#define LL_GPIO_PIN_6                      GPIO_BSRR_BS6
#define LL_GPIO_PIN_7                      GPIO_BSRR_BS7
#define LL_GPIO_PIN_8                      GPIO_BSRR_BS8
#define LL_GPIO_PIN_9                      GPIO_BSRR_BS9
#define LL_GPIO_PIN_10                     GPIO_BSRR_BS10
#define LL_GPIO_PIN_11                     GPIO_BSRR_BS11
#define LL_GPIO_PIN_12                     GPIO_BSRR_BS12
#define LL_GPIO_PIN_13                     GPIO_BSRR_BS13
#define LL_GPIO_PIN_14                     GPIO_BSRR_BS14
#define LL_GPIO_PIN_15                     GPIO_BSRR_BS15
#define LL_GPIO_PIN_ALL                    (GPIO_BSRR_BS0 | GPIO_BSRR_BS1  | GPIO_BSRR_BS2  | \
                                            GPIO_BSRR_BS3  | GPIO_BSRR_BS4  | GPIO_BSRR_BS5  | \
                                            GPIO_BSRR_BS6  | GPIO_BSRR_BS7  | GPIO_BSRR_BS8  | \
                                            GPIO_BSRR_BS9  | GPIO_BSRR_BS10 | GPIO_BSRR_BS11 | \
                                            GPIO_BSRR_BS12 | GPIO_BSRR_BS13 | GPIO_BSRR_BS14 | \
                                            GPIO_BSRR_BS15)
#define LL_GPIO_MODE_INPUT                 (0x00000000U)
#define LL_GPIO_MODE_OUTPUT                GPIO_MODER_MODE0_0
#define LL_GPIO_MODE_ALTERNATE             GPIO_MODER_MODE0_1
#define LL_GPIO_MODE_ANALOG                GPIO_MODER_MODE0
#define LL_GPIO_OUTPUT_PUSHPULL            (0x00000000U)
#define LL_GPIO_OUTPUT_OPENDRAIN           GPIO_OTYPER_OT0
#define LL_GPIO_SPEED_FREQ_LOW             (0x00000000U)
#define LL_GPIO_SPEED_FREQ_MEDIUM          GPIO_OSPEEDR_OSPEED0_0
#define LL_GPIO_SPEED_FREQ_HIGH            GPIO_OSPEEDR_OSPEED0_1
#define LL_GPIO_SPEED_FREQ_VERY_HIGH       GPIO_OSPEEDR_OSPEED0
#define LL_GPIO_SPEED_LOW                  LL_GPIO_SPEED_FREQ_LOW
#define LL_GPIO_SPEED_MEDIUM               LL_GPIO_SPEED_FREQ_MEDIUM
#define LL_GPIO_SPEED_FAST                 LL_GPIO_SPEED_FREQ_HIGH
#define LL_GPIO_SPEED_HIGH                 LL_GPIO_SPEED_FREQ_VERY_HIGH
#define LL_GPIO_PULL_NO                    (0x00000000U)
#define LL_GPIO_PULL_UP                    GPIO_PUPDR_PUPD0_0
#define LL_GPIO_PULL_DOWN                  GPIO_PUPDR_PUPD0_1
#define LL_GPIO_AF_0                       (0x0000000U)
#define LL_GPIO_AF_1                       (0x0000001U)
#define LL_GPIO_AF_2                       (0x0000002U)
#define LL_GPIO_AF_3                       (0x0000003U)
#define LL_GPIO_AF_4                       (0x0000004U)
#define LL_GPIO_AF_5                       (0x0000005U)
#define LL_GPIO_AF_6                       (0x0000006U)
#define LL_GPIO_AF_7                       (0x0000007U)
#define LL_GPIO_AF_8                       (0x0000008U)
#define LL_GPIO_AF_9                       (0x0000009U)
#define LL_GPIO_AF_10                      (0x000000AU)
#define LL_GPIO_AF_11                      (0x000000BU)
#define LL_GPIO_AF_12                      (0x000000CU)
#define LL_GPIO_AF_13                      (0x000000DU)
#define LL_GPIO_AF_14                      (0x000000EU)
#define LL_GPIO_AF_15                      (0x000000FU)
#define LL_GPIO_WriteReg(__INSTANCE__, __REG__, __VALUE__) WRITE_REG(__INSTANCE__->__REG__, (__VALUE__))
#define LL_GPIO_ReadReg(__INSTANCE__, __REG__) READ_REG(__INSTANCE__->__REG__)
inline void LL_GPIO_SetPinMode(GPIO_TypeDef *GPIOx, uint32_t Pin, uint32_t Mode)
{
  MODIFY_REG(GPIOx->MODER, (GPIO_MODER_MODE0 << (POSITION_VAL(Pin) * GPIO_MODER_MODE1_Pos)),
             (Mode << (POSITION_VAL(Pin) * GPIO_MODER_MODE1_Pos)));
}
inline uint32_t LL_GPIO_GetPinMode(const GPIO_TypeDef *GPIOx, uint32_t Pin)
{
  return (uint32_t)(READ_BIT(GPIOx->MODER, (GPIO_MODER_MODE0 << (POSITION_VAL(Pin) * GPIO_MODER_MODE1_Pos))) >>
                    (POSITION_VAL(Pin) * GPIO_MODER_MODE1_Pos));
}
inline void LL_GPIO_SetPinPull(GPIO_TypeDef *GPIOx, uint32_t Pin, uint32_t Pull)
{
  MODIFY_REG(GPIOx->PUPDR, (GPIO_PUPDR_PUPD0 << (POSITION_VAL(Pin) * GPIO_PUPDR_PUPD1_Pos)),
             (Pull << (POSITION_VAL(Pin) * GPIO_PUPDR_PUPD1_Pos)));
}
inline uint32_t LL_GPIO_GetPinPull(const GPIO_TypeDef *GPIOx, uint32_t Pin)
{
  return (uint32_t)(READ_BIT(GPIOx->PUPDR, (GPIO_PUPDR_PUPD0 << \
                                            (POSITION_VAL(Pin) * GPIO_PUPDR_PUPD1_Pos))) >> \
                    (POSITION_VAL(Pin) * GPIO_PUPDR_PUPD1_Pos));
}
inline uint32_t LL_GPIO_IsPinLocked(const GPIO_TypeDef *GPIOx, uint32_t PinMask)
{
  return ((READ_BIT(GPIOx->LCKR, PinMask) == (PinMask)) ? 1UL : 0UL);
}

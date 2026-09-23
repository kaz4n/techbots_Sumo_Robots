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
#include "register.h"
#include <cstdint>
using std::uint32_t;
typedef struct
{
  volatile Reg MODER;
  volatile Reg OTYPER;
  volatile Reg OSPEEDR;
  volatile Reg PUPDR;
  volatile Reg IDR;
  volatile Reg ODR;
  volatile Reg BSRR;
  volatile Reg LCKR;
  volatile Reg AFR[2];
  volatile Reg BRR;
  volatile Reg HSLVR;
  volatile Reg SECCFGR;
} GPIO_TypeDef;
typedef struct
{
  volatile Reg CR;
  uint32_t      RESERVED0;
  volatile Reg ICSCR1;
  volatile Reg ICSCR2;
  volatile Reg ICSCR3;
  volatile Reg CRRCR;
  uint32_t      RESERVED1;
  volatile Reg CFGR1;
  volatile Reg CFGR2;
  volatile Reg CFGR3;
  volatile Reg PLL1CFGR;
  volatile Reg PLL2CFGR;
  volatile Reg PLL3CFGR;
  volatile Reg PLL1DIVR;
  volatile Reg PLL1FRACR;
  volatile Reg PLL2DIVR;
  volatile Reg PLL2FRACR;
  volatile Reg PLL3DIVR;
  volatile Reg PLL3FRACR;
  uint32_t      RESERVED2;
  volatile Reg CIER;
  volatile Reg CIFR;
  volatile Reg CICR;
  uint32_t      RESERVED3;
  volatile Reg AHB1RSTR;
  volatile Reg AHB2RSTR1;
  volatile Reg AHB2RSTR2;
  volatile Reg AHB3RSTR;
  uint32_t      RESERVED4;
  volatile Reg APB1RSTR1;
  volatile Reg APB1RSTR2;
  volatile Reg APB2RSTR;
  volatile Reg APB3RSTR;
  uint32_t      RESERVED5;
  volatile Reg AHB1ENR;
  volatile Reg AHB2ENR1;
  volatile Reg AHB2ENR2;
  volatile Reg AHB3ENR;
  uint32_t      RESERVED6;
  volatile Reg APB1ENR1;
  volatile Reg APB1ENR2;
  volatile Reg APB2ENR;
  volatile Reg APB3ENR;
  uint32_t      RESERVED7;
  volatile Reg AHB1SMENR;
  volatile Reg AHB2SMENR1;
  volatile Reg AHB2SMENR2;
  volatile Reg AHB3SMENR;
  uint32_t      RESERVED8;
  volatile Reg APB1SMENR1;
  volatile Reg APB1SMENR2;
  volatile Reg APB2SMENR;
  volatile Reg APB3SMENR;
  uint32_t      RESERVED9;
  volatile Reg SRDAMR;
  uint32_t      RESERVED10;
  volatile Reg CCIPR1;
  volatile Reg CCIPR2;
  volatile Reg CCIPR3;
  uint32_t      RESERVED11;
  volatile Reg BDCR;
  volatile Reg CSR;
  uint32_t      RESERVED[6];
  volatile Reg SECCFGR;
  volatile Reg PRIVCFGR;
} RCC_TypeDef;
typedef struct
{
  volatile Reg RTSR1;
  volatile Reg FTSR1;
  volatile Reg SWIER1;
  volatile Reg RPR1;
  volatile Reg FPR1;
  volatile Reg SECCFGR1;
  volatile Reg PRIVCFGR1;
       uint32_t RESERVED1[17];
  volatile Reg EXTICR[4];
  volatile Reg LOCKR;
       uint32_t RESERVED2[3];
  volatile Reg IMR1;
  volatile Reg EMR1;
} EXTI_TypeDef;
typedef struct
{
  volatile Reg IDCODE;
  volatile Reg CR;
  volatile Reg APB1FZR1;
  volatile Reg APB1FZR2;
  volatile Reg APB2FZR;
  volatile Reg APB3FZR;
       uint32_t RESERVED1[2];
  volatile Reg AHB1FZR;
       uint32_t RESERVED2;
  volatile Reg AHB3FZR;
} DBGMCU_TypeDef;

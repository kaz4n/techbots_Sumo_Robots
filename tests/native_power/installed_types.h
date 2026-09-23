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
#include "register.h"
#include <cstdint>
using std::uint32_t;
typedef struct
{
  volatile Reg ISR;
  volatile Reg IER;
  volatile Reg CR;
  volatile Reg CFGR1;
  volatile Reg CFGR2;
  volatile Reg SMPR1;
  volatile Reg SMPR2;
  volatile Reg PCSEL;
  volatile Reg AWD1TR;
  volatile Reg AWD2TR;
  volatile Reg CHSELR;
  volatile Reg AWD3TR;
  volatile Reg SQR1;
  volatile Reg SQR2;
  volatile Reg SQR3;
  volatile Reg SQR4;
  volatile Reg DR;
  volatile Reg PWRR;
  uint32_t      RESERVED1;
  volatile Reg JSQR;
  uint32_t      RESERVED2[4];
  volatile Reg OFR1;
  volatile Reg OFR2;
  volatile Reg OFR3;
  volatile Reg OFR4;
  volatile Reg GCOMP;
  uint32_t      RESERVED3[3];
  volatile Reg JDR1;
  volatile Reg JDR2;
  volatile Reg JDR3;
  volatile Reg JDR4;
  uint32_t      RESERVED4[4];
  volatile Reg AWD2CR;
  volatile Reg AWD3CR;
  volatile Reg LTR1;
  volatile Reg HTR1;
  volatile Reg LTR2;
  volatile Reg HTR2;
  volatile Reg LTR3;
  volatile Reg HTR3;
  volatile Reg DIFSEL;
  volatile Reg CALFACT;
  volatile Reg CALFACT2;
  uint32_t      RESERVED5;
  volatile Reg OR;
} ADC_TypeDef;
typedef struct
{
  volatile Reg CCR;
} ADC_Common_TypeDef;
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
  volatile Reg CR1;
  volatile Reg CR2;
  volatile Reg CR3;
  volatile Reg VOSR;
  volatile Reg SVMCR;
  volatile Reg WUCR1;
  volatile Reg WUCR2;
  volatile Reg WUCR3;
  volatile Reg BDCR1;
  volatile Reg BDCR2;
  volatile Reg DBPR;
  volatile Reg UCPDR;
  volatile Reg SECCFGR;
  volatile Reg PRIVCFGR;
  volatile Reg SR;
  volatile Reg SVMSR;
  volatile Reg BDSR;
  volatile Reg WUSR;
  volatile Reg WUSCR;
  volatile Reg APCR;
  volatile Reg PUCRA;
  volatile Reg PDCRA;
  volatile Reg PUCRB;
  volatile Reg PDCRB;
  volatile Reg PUCRC;
  volatile Reg PDCRC;
  volatile Reg PUCRD;
  volatile Reg PDCRD;
  volatile Reg PUCRE;
  volatile Reg PDCRE;
  volatile Reg PUCRF;
  volatile Reg PDCRF;
  volatile Reg PUCRG;
  volatile Reg PDCRG;
  volatile Reg PUCRH;
  volatile Reg PDCRH;
  volatile Reg PUCRI;
  volatile Reg PDCRI;
} PWR_TypeDef;
typedef struct
{
  volatile Reg SECCFGR;
  volatile Reg CFGR1;
  volatile Reg FPUIMR;
  volatile Reg CNSLCKR;
  volatile Reg CSLCKR;
  volatile Reg CFGR2;
  volatile Reg MESR;
  volatile Reg CCCSR;
  volatile Reg CCVR;
  volatile Reg CCCR;
       uint32_t RESERVED1;
  volatile Reg RSSCMDR;
} SYSCFG_TypeDef;
typedef struct
{
  volatile Reg CR;
  volatile Reg SWTRIGR;
  volatile Reg DHR12R1;
  volatile Reg DHR12L1;
  volatile Reg DHR8R1;
  volatile Reg DHR12R2;
  volatile Reg DHR12L2;
  volatile Reg DHR8R2;
  volatile Reg DHR12RD;
  volatile Reg DHR12LD;
  volatile Reg DHR8RD;
  volatile Reg DOR1;
  volatile Reg DOR2;
  volatile Reg SR;
  volatile Reg CCR;
  volatile Reg MCR;
  volatile Reg SHSR1;
  volatile Reg SHSR2;
  volatile Reg SHHR;
  volatile Reg SHRR;
  volatile Reg RESERVED[1];
  volatile Reg AUTOCR;
} DAC_TypeDef;

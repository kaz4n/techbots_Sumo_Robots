// Copies exact installed STM32U585 definitions and selected LL operations.
// Observable four-byte words preserve offsets while modeling hardware side effects.
// Independent B3 native tests exercise the production transfer contract.
#pragma once
/* Copyright (c) 2021 STMicroelectronics. All rights reserved.
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 * Source identities and selected bodies are recorded in extraction.json.
 */
#include "register.h"
#include <cstdint>
using std::uint32_t;
typedef struct
{
  volatile Reg CR1;
  volatile Reg CR2;
  volatile Reg OAR1;
  volatile Reg OAR2;
  volatile Reg TIMINGR;
  volatile Reg TIMEOUTR;
  volatile Reg ISR;
  volatile Reg ICR;
  volatile Reg PECR;
  volatile Reg RXDR;
  volatile Reg TXDR;
  volatile Reg AUTOCR;
} I2C_TypeDef;
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

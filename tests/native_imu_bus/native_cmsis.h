// Supplies source-verified I2C4/GPIOD/RCC addresses and CMSIS operations.
// Only register storage and NVIC observations are controlled by the host model.
// Exact installed LL operation bodies are compiled against this surface.
#pragma once
#include "installed_bits.h"
#include "installed_types.h"
#define __IO volatile
#define I2C4_BASE 0x40008400UL
#define GPIOD_BASE 0x42020C00UL
#define RCC_BASE 0x46020C00UL
#define I2C4 reinterpret_cast<I2C_TypeDef*>(I2C4_BASE)
#define GPIOD reinterpret_cast<GPIO_TypeDef*>(GPIOD_BASE)
#define RCC reinterpret_cast<RCC_TypeDef*>(RCC_BASE)
#define PWR reinterpret_cast<PWR_TypeDef*>(0x46020800UL)
#define SYSCFG reinterpret_cast<SYSCFG_TypeDef*>(0x46000400UL)
#define READ_REG(r) static_cast<std::uint32_t>(r)
#define WRITE_REG(r,v) ((r)=static_cast<std::uint32_t>(v))
#define READ_BIT(r,m) (READ_REG(r)&(m))
#define SET_BIT(r,m) ((r)|=(m))
#define CLEAR_BIT(r,m) ((r)&=static_cast<std::uint32_t>(~(m)))
#define MODIFY_REG(r,c,s) WRITE_REG((r),(READ_REG(r)&~(c))|(s))
#define POSITION_VAL(v) static_cast<unsigned>(__builtin_ctz(v))
enum IRQn_Type { I2C4_ER_IRQn=100, I2C4_EV_IRQn=101 };
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type);
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type);
std::uint32_t NVIC_GetActive(IRQn_Type);
void __DMB();

#define I2C4_NS I2C4
#define GPIOD_NS GPIOD
#define RCC_NS RCC
#define PWR_NS PWR

// Exposes the saved installed STM32U585 register layout at native addresses.
// Observable storage catches forbidden writes and reads with disabled clocks.
// Independently modeled GPIO dispatch and NVIC state drive the native tests.
#pragma once
#include "installed_bits.h"
#include "installed_types.h"
#define GPIOA_NS reinterpret_cast<GPIO_TypeDef*>(0x42020000UL)
#define GPIOB_NS reinterpret_cast<GPIO_TypeDef*>(0x42020400UL)
#define RCC_NS reinterpret_cast<RCC_TypeDef*>(0x46020C00UL)
#define EXTI_NS reinterpret_cast<EXTI_TypeDef*>(0x46022000UL)
#define DBGMCU reinterpret_cast<DBGMCU_TypeDef*>(0xE0044000UL)
#define GPIOA GPIOA_NS
#define GPIOB GPIOB_NS
#define RCC RCC_NS
#define EXTI EXTI_NS
#define READ_REG(r) static_cast<std::uint32_t>(r)
#define WRITE_REG(r,v) ((r)=static_cast<std::uint32_t>(v))
#define READ_BIT(r,m) (READ_REG(r)&(m))
#define SET_BIT(r,m) ((r)|=(m))
#define CLEAR_BIT(r,m) ((r)&=static_cast<std::uint32_t>(~(m)))
#define MODIFY_REG(r,c,s) WRITE_REG((r),(READ_REG(r)&~(c))|(s))
#define POSITION_VAL(v) static_cast<unsigned>(__builtin_ctz(v))
enum IRQn_Type { EXTI2_IRQn=13, EXTI3_IRQn=14, EXTI4_IRQn=15, EXTI12_IRQn=23 };
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type);
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type);
std::uint32_t NVIC_GetActive(IRQn_Type);

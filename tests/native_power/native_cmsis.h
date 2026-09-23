// Exposes installed addresses, layouts and CMSIS read-modify-write operations.
// Only the side effects of storage and NVIC observations are controlled.
// Native B5 tests exercise the actual production source at these fixed addresses.
#pragma once
#include "installed_bits.h"
#include "installed_types.h"
#define ADC1_NS reinterpret_cast<ADC_TypeDef*>(0x42028000UL)
#define ADC12_COMMON_NS reinterpret_cast<ADC_Common_TypeDef*>(0x42028308UL)
#define ADC4_NS reinterpret_cast<ADC_TypeDef*>(0x46021000UL)
#define GPIOA_NS reinterpret_cast<GPIO_TypeDef*>(0x42020000UL)
#define RCC_NS reinterpret_cast<RCC_TypeDef*>(0x46020C00UL)
#define PWR_NS reinterpret_cast<PWR_TypeDef*>(0x46020800UL)
#define SYSCFG_NS reinterpret_cast<SYSCFG_TypeDef*>(0x46000400UL)
#define DAC1_NS reinterpret_cast<DAC_TypeDef*>(0x46021800UL)
#define ADC1 ADC1_NS
#define ADC4 ADC4_NS
#define ADC12_COMMON ADC12_COMMON_NS
#define GPIOA GPIOA_NS
#define RCC RCC_NS
#define PWR PWR_NS
#define SYSCFG SYSCFG_NS
#define DAC1 DAC1_NS
#define READ_REG(r) static_cast<std::uint32_t>(r)
#define WRITE_REG(r,v) ((r)=static_cast<std::uint32_t>(v))
#define READ_BIT(r,m) (READ_REG(r)&(m))
#define SET_BIT(r,m) ((r)|=(m))
#define CLEAR_BIT(r,m) ((r)&=static_cast<std::uint32_t>(~(m)))
#define MODIFY_REG(r,c,s) WRITE_REG((r),(READ_REG(r)&~(c))|(s))
#define POSITION_VAL(v) static_cast<unsigned>(__builtin_ctz(v))
enum IRQn_Type { ADC1_IRQn=37, ADC4_IRQn=113 };
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type);
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type);
std::uint32_t NVIC_GetActive(IRQn_Type);
void __DMB();

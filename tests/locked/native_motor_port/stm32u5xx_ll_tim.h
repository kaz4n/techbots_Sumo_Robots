// Declares STM32U585 register names and observed LL update operations.
// Numeric masks come from the retained installed-header source receipt.
// Independent cases model rc_w0 and distinct preload versus active state.
#pragma once
#include <cstdint>
#include "installed_tim_bits.h"
struct TIM_TypeDef {
    volatile std::uint32_t CR1, CR2, SMCR, DIER, SR, EGR, CCMR1, CCMR2, CCER;
    volatile std::uint32_t CNT, PSC, ARR, RCR, CCR1, CCR2, CCR3, CCR4, BDTR;
    volatile std::uint32_t DCR, DMAR, OR1, CCMR3, CCR5, CCR6, AF1, AF2, TISEL;
};
#define TIM1 reinterpret_cast<TIM_TypeDef*>(0x40012c00UL)
#define TIM3 reinterpret_cast<TIM_TypeDef*>(0x40000400UL)
#define TIM4 reinterpret_cast<TIM_TypeDef*>(0x40000800UL)
#define TIM_SR_UIF 1UL
#define LL_TIM_UPDATESOURCE_REGULAR 0UL
#define LL_TIM_COUNTERMODE_UP 0UL
void LL_TIM_ClearFlag_UPDATE(TIM_TypeDef*);
std::uint32_t LL_TIM_IsActiveFlag_UPDATE(const TIM_TypeDef*);
inline std::uint32_t LL_TIM_IsEnabledCounter(const TIM_TypeDef* p) { return (p->CR1 & TIM_CR1_CEN) != 0; }
inline std::uint32_t LL_TIM_IsEnabledUpdateEvent(const TIM_TypeDef* p) { return (p->CR1 & TIM_CR1_UDIS) == 0; }
inline std::uint32_t LL_TIM_GetUpdateSource(const TIM_TypeDef* p) { return p->CR1 & TIM_CR1_URS; }
inline std::uint32_t LL_TIM_GetRepetitionCounter(const TIM_TypeDef* p) { return p->RCR; }
inline std::uint32_t LL_TIM_GetPrescaler(const TIM_TypeDef* p) { return p->PSC; }
inline std::uint32_t LL_TIM_GetAutoReload(const TIM_TypeDef* p) { return p->ARR; }

// Models the pinned nominal MSIS4MHz PLL1x80 / R2 160MHz clock admission calls.
// Host values represent source configuration, never a measured physical frequency.
// A separately controlled predicate lets native tests reject initial clock drift.
#pragma once
#include "cmsis_core.h"
extern bool dump_clock_good;
inline constexpr std::uint32_t LL_RCC_SYS_CLKSOURCE_STATUS_PLL1 = RCC_CFGR1_SWS_1 | RCC_CFGR1_SWS_0;
inline constexpr std::uint32_t LL_RCC_SYSCLK_DIV_1 = 0U;
inline constexpr std::uint32_t LL_RCC_APB3_DIV_1 = 0U;
inline constexpr std::uint32_t LL_RCC_PLL1SOURCE_MSIS = RCC_PLL1CFGR_PLL1SRC_0;
inline constexpr std::uint32_t LL_RCC_MSISRANGE_4 = RCC_ICSCR1_MSISRANGE_2;
inline constexpr std::uint32_t LL_RCC_PLLMODE_MSIS = RCC_CR_MSIPLLSEL;
inline std::uint32_t LL_RCC_GetSysClkSource() { return dump_clock_good ? LL_RCC_SYS_CLKSOURCE_STATUS_PLL1 : 0U; }
inline std::uint32_t LL_RCC_GetAHBPrescaler() { return LL_RCC_SYSCLK_DIV_1; }
inline std::uint32_t LL_RCC_GetAPB3Prescaler() { return LL_RCC_APB3_DIV_1; }
inline std::uint32_t LL_RCC_PLL1_GetMainSource() { return LL_RCC_PLL1SOURCE_MSIS; }
inline std::uint32_t LL_RCC_PLL1_GetDivider() { return 1U; }
inline std::uint32_t LL_RCC_PLL1_GetN() { return 80U; }
inline std::uint32_t LL_RCC_PLL1_GetR() { return 2U; }
inline std::uint32_t LL_RCC_PLL1_IsReady() { return 1U; }
inline std::uint32_t LL_RCC_PLL1_IsEnabledDomain_SYS() { return 1U; }
inline std::uint32_t LL_RCC_PLL1FRACN_IsEnabled() { return 0U; }
inline std::uint32_t LL_RCC_MSI_IsEnabledRangeSelect() { return 1U; }
inline std::uint32_t LL_RCC_MSIS_GetRange() { return LL_RCC_MSISRANGE_4; }
inline std::uint32_t LL_RCC_MSIS_IsReady() { return 1U; }
inline std::uint32_t LL_RCC_MSI_IsEnabledPLLMode() { return 1U; }
inline std::uint32_t LL_RCC_MSI_GetMSIPLLMode() { return LL_RCC_PLLMODE_MSIS; }
inline std::uint32_t LL_RCC_IsEnabledPLLMode() { return 1U; }
inline std::uint32_t LL_RCC_GetMSIPLLMode() { return LL_RCC_PLLMODE_MSIS; }

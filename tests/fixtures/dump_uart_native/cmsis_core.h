// Declares observed register and privilege operations for D090 native tests.
// Uses pinned peripheral addresses with exact saved PRIMASK restoration checks.
// The fixture independently models TXE, TC, flush and context loss.
#pragma once
#include "installed_uart.h"
#define LPUART1 reinterpret_cast<USART_TypeDef*>(0x46002400UL)
#define GPIOG reinterpret_cast<GPIO_TypeDef*>(0x42021800UL)
#define RCC reinterpret_cast<RCC_TypeDef*>(0x46020C00UL)
#define LPUART1_NS LPUART1
#define GPIOG_NS GPIOG
#define RCC_NS RCC
#define LPUART1_BASE 0x46002400UL
#define GPIOG_BASE 0x42021800UL
#define READ_REG(r) static_cast<std::uint32_t>(r)
#define WRITE_REG(r,v) ((r)=static_cast<std::uint32_t>(v))
#define READ_BIT(r,m) (READ_REG(r)&(m))
#define SET_BIT(r,m) ((r)|=(m))
#define CLEAR_BIT(r,m) ((r)&=static_cast<std::uint32_t>(~(m)))
#define MODIFY_REG(r,c,s) WRITE_REG((r),(READ_REG(r)&~(c))|(s))
enum IRQn_Type { LPUART1_IRQn = 66 };
std::uint32_t __get_CONTROL();
std::uint32_t __get_IPSR();
std::uint32_t __get_PRIMASK();
void __disable_irq();
void __set_PRIMASK(std::uint32_t);
void __DMB();
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type);
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type);
std::uint32_t NVIC_GetActive(IRQn_Type);
void NVIC_DisableIRQ(IRQn_Type);
void NVIC_ClearPendingIRQ(IRQn_Type);

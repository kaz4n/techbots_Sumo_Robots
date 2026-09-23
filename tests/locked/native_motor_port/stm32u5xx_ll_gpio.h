// Models source-verified STM32U585 GPIO ownership read APIs.
// Pin masks, output latch and physical input readback remain separate observations.
// Cases inject remux, pull and output-type changes at runtime.
#pragma once
#include <cstdint>
struct GPIO_TypeDef { volatile std::uint32_t MODER, OTYPER, OSPEEDR, PUPDR, IDR, ODR, BSRR, LCKR, AFR[2], BRR; };
#define GPIOB reinterpret_cast<GPIO_TypeDef*>(0x42020400UL)
#define LL_GPIO_MODE_OUTPUT 1U
#define LL_GPIO_OUTPUT_PUSHPULL 0U
#define LL_GPIO_PULL_NO 0U
inline unsigned fixturePinShift(std::uint32_t p) { return static_cast<unsigned>(__builtin_ctz(p)); }
inline std::uint32_t LL_GPIO_GetPinMode(const GPIO_TypeDef* g, std::uint32_t p) { return (g->MODER >> (2U * fixturePinShift(p))) & 3U; }
inline std::uint32_t LL_GPIO_GetPinOutputType(const GPIO_TypeDef* g, std::uint32_t p) { return (g->OTYPER & p) ? 1U : 0U; }
inline std::uint32_t LL_GPIO_GetPinPull(const GPIO_TypeDef* g, std::uint32_t p) { return (g->PUPDR >> (2U * fixturePinShift(p))) & 3U; }
inline std::uint32_t LL_GPIO_IsOutputPinSet(const GPIO_TypeDef* g, std::uint32_t p) { return (g->ODR & p) == p; }

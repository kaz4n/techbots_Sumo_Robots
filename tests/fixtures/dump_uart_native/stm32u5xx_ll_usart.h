// Aliases the pinned STM32 UART declaration include used by the installed SDK.
// Exposes no polling or FIFO API with unsuitable execution-context guarantees.
// Independent register traces validate actual native owner calls.
#pragma once
#include "stm32_ll_usart.h"

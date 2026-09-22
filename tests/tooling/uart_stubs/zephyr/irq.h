// Declares modeled IRQ masking for the independent P0 adapter tests.
// Checks that UART mutations are protected and the original key is restored.
// Implemented by counter_uart_cases.cc and used by the real adapter.
#pragma once
unsigned int irq_lock();
void irq_unlock(unsigned int key);

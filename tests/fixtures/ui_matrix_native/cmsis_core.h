// Declares controlled D088 CMSIS calls for the actual native source host test.
// Allows exact ordering and preexisting-mask restoration assertions.
// Definitions in native_cases.cc count every observable operation.
#pragma once
#include <cstdint>
std::uint32_t __get_CONTROL();
std::uint32_t __get_IPSR();
std::uint32_t __get_PRIMASK();
void __disable_irq();
void __DMB();
void __set_PRIMASK(std::uint32_t value);

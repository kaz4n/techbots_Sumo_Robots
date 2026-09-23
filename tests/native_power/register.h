// Intercepts four-byte native register reads and writes for hardware semantics.
// ISR uses W1C and CR commands retain read-as-set state until acknowledgement.
// The production source accesses these words through its ordinary CMSIS surface.
#pragma once
#include <cstdint>
struct Reg {
    std::uint32_t value;
    Reg()=default;
    Reg(const volatile Reg& r):value(static_cast<std::uint32_t>(r)){}
    operator std::uint32_t() const volatile;
    void operator=(std::uint32_t) volatile;
    void operator|=(std::uint32_t v) volatile { *this=std::uint32_t(*this)|v; }
    void operator&=(std::uint32_t v) volatile { *this=std::uint32_t(*this)&v; }
};
static_assert(sizeof(Reg)==4,"Fixture must preserve installed register offsets");

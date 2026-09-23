// Declares direct battery-only callbacks backed by one existing power Reader.
// Keeps native construction passive and excludes the optional A1 profile and other owners.
// D110 contract: counted owner substitutes and exact target startup checks are pending.
#pragma once
#include "vbat.h"

namespace vbat {
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    Port port();
private:
    static std::uint32_t clockUs(void* context);
    static power::InitResult beginBattery(void* context);
    static power::Sample readBattery(void* context);
    power::Reader reader_;
};
} // namespace vbat

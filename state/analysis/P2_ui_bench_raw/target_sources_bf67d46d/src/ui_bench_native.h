// Declares direct A1 callbacks backed by one existing fixed-profile power Reader.
// Keeps construction passive and excludes battery reads, extra owners and cleanup inventions.
// D112 contract: counted Reader substitutions and target checks follow adoption.
#pragma once
#include "ui_bench.h"

namespace ui_bench {
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    Port port();
private:
    static std::uint32_t clockUs(void* context);
    static power::InitResult beginButtons(void* context);
    static power::ButtonSample readButtons(void* context);
    power::Reader reader_;
};
} // namespace ui_bench

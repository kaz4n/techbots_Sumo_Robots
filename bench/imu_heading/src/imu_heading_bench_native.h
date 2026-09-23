// Declares direct heading-bench callbacks backed by one existing native Acquirer.
// Keeps construction passive and excludes unrelated application resource owners.
// D111 contract: counted binding and exact target startup checks follow adoption.
#pragma once
#include "imu_heading_bench.h"

namespace imu_heading_bench {
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    Port port();
private:
    static std::uint32_t clockUs(void*);
    static imu::SetupReport startSetup(void*, std::uint32_t, bool);
    static imu::SetupReport advanceSetup(void*, std::uint32_t);
    static imu::SampleProgress beginRead(void*, std::uint32_t);
    static imu::SampleProgress advanceRead(void*, std::uint32_t);
    static imu::SampleProgress cancelRead(void*, std::uint32_t);
    imu::Acquirer acquirer_;
};
} // namespace imu_heading_bench

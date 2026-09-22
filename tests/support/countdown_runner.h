// Supplies deterministic clocks and random streams for standalone countdown tests.
// Keeps the test oracle on a 64-bit timeline independent of the module's wrap math.
// Used by B3 tests; it does not model motor writes or the complete Robot scheduler.
#pragma once
#include "core/countdown.h"
#include <cstdint>

namespace test_support {
class FixedRandom {
public:
    explicit FixedRandom(std::uint32_t seed) : value_(seed) {}
    std::uint32_t next() {
        value_ ^= value_ << 13;
        value_ ^= value_ >> 17;
        value_ ^= value_ << 5;
        return value_;
    }
private:
    std::uint32_t value_;
};

class CountdownRunner {
public:
    explicit CountdownRunner(std::uint64_t origin) : now_us(origin) {}
    countdown::Result sample(countdown::Commands commands = {}) {
        return gate.step(static_cast<std::uint32_t>(now_us), commands);
    }
    countdown::Result after(std::uint32_t elapsed_us,
                            countdown::Commands commands = {}) {
        now_us += elapsed_us;
        return sample(commands);
    }
    countdown::Gate gate;
    std::uint64_t now_us;
};
} // namespace test_support

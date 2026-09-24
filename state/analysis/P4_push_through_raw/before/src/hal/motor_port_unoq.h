// Supplies checked native UNO Q callbacks exclusively to MotorGate.
// Keeps proposed routing and pending PWM updates from becoming unverified motion.
// Independent native-header tests and inert target builds verify this adapter.
#pragma once
#include "motors.h"
#include <cstdint>

namespace motors {
class UnoQPort {
public:
    UnoQPort() = default;
    UnoQPort(const UnoQPort&) = delete;
    UnoQPort& operator=(const UnoQPort&) = delete;
    // No I/O. This object must outlive its sole MotorGate and retain pin ownership.
    Port port();
private:
    static bool configureEnableLow(void* context);
    static bool configurePwm(void* context, Channel channel);
    static bool writeEnable(void* context, bool high);
    static bool writePwm(void* context, Channel channel, std::uint32_t period,
                         std::uint32_t pulse);
    static bool settle(void* context);
    static std::uint32_t clockUs(void* context);
    bool enableOwned() const;
    bool enableLow() const;
    bool timerValid(std::uint32_t timer) const;
    bool bankValid() const;
    std::uint32_t pwm_indices_[4] = {};
    bool enable_configured_ = false;
    bool enable_low_ = false;
    bool settled_ = false;
    std::uint8_t configured_mask_ = 0U;
    std::uint8_t written_mask_ = 0U;
    std::uint8_t initialized_timers_ = 0U;
    std::uint8_t active_channels_ = 0U;
    std::uint32_t pulses_[4] = {};
};
} // namespace motors

// Supplies independent D095 physical-call traces and actual application owners.
// Keeps expected clock/source values in tests rather than deriving them from code.
// Halt and transaction tests share only this finite callback fixture.
#pragma once
#include "doctest.h"
#include "app/transaction.h"
#include <array>
#include <cstdint>
#include <cstdlib>

#define APP_REQUIRE(...) do { const bool passed = (__VA_ARGS__); \
    CHECK_MESSAGE(passed, #__VA_ARGS__); if (!passed) std::abort(); } while (false)

namespace app_test {
enum class Kind { CONFIG_ENABLE, CONFIG_PWM, ENABLE, PWM, SETTLE, CLOCK };
struct Call { Kind kind; unsigned channel = 0; std::uint32_t pulse = 0; bool high = false; };
struct Port {
    std::array<Call, 128> calls{};
    std::array<std::uint32_t, 12> clock_script{};
    std::array<std::uint32_t, 4> pulses{};
    std::uint32_t now = 0, work_us = 0, settle_us = 0;
    unsigned count = 0, operations = 0, clocks = 0, fail_at = 0;
    unsigned scripted = 0, highs = 0, nonzero = 0, settles = 0;
    bool enabled = false;
    void clear(std::uint32_t time = 0) {
        now = time; count = operations = clocks = fail_at = scripted = 0;
        highs = nonzero = settles = 0; work_us = settle_us = 0;
    }
    bool record(Call call) {
        if (count < calls.size()) calls[count] = call;
        ++count;
        if (call.kind == Kind::CLOCK) return true;
        now += work_us;
        return ++operations != fail_at;
    }
    static Port& self(void* context) { return *static_cast<Port*>(context); }
    static bool configureEnable(void* context) {
        auto& p = self(context); const bool ok = p.record({Kind::CONFIG_ENABLE});
        if (ok) p.enabled = false;
        return ok;
    }
    static bool configurePwm(void* context, motors::Channel channel) {
        return self(context).record({Kind::CONFIG_PWM, static_cast<unsigned>(channel)});
    }
    static bool enable(void* context, bool high) {
        auto& p = self(context); const bool ok = p.record({Kind::ENABLE, 0, 0, high});
        if (high) ++p.highs;
        if (ok) p.enabled = high;
        return ok;
    }
    static bool pwm(void* context, motors::Channel channel, std::uint32_t, std::uint32_t pulse) {
        auto& p = self(context); const auto index = static_cast<unsigned>(channel);
        const bool ok = p.record({Kind::PWM, index, pulse});
        if (pulse != 0U) ++p.nonzero;
        if (ok && index < 4U) p.pulses[index] = pulse;
        return ok;
    }
    static bool settle(void* context) {
        auto& p = self(context); ++p.settles; p.now += p.settle_us;
        return p.record({Kind::SETTLE});
    }
    static std::uint32_t clock(void* context) {
        auto& p = self(context); p.record({Kind::CLOCK});
        const auto index = p.clocks++;
        return index < p.scripted ? p.clock_script[index] : p.now;
    }
    motors::Port port() {
        return {this, configureEnable, configurePwm, enable, pwm, settle, clock,
            {1000U, 997U, 251U, 65535U}};
    }
};
inline void zero(const Port& port) {
    CHECK_FALSE(port.enabled);
    for (auto pulse : port.pulses) CHECK(pulse == 0U);
}
inline fsm::RobotInput input() {
    fsm::RobotInput value;
    value.initialization_complete = true;
    value.observations_fresh = true;
    value.opp_raw_mask = 0x78U;
    value.imu_ok = true;
    value.vbat_v = 11.1F; value.vbat_valid = true;
    for (auto& line : value.line_raw_us) line = 1000U;
    return value;
}
struct Rig {
    Port port;
    app::Transaction owner{port.port()};
    fsm::RobotInput source = input();
    Rig() { APP_REQUIRE(owner.initialize()); port.clear(); }
    const app::TransactionReport& cycle(std::uint32_t start, std::uint32_t decision,
                                       std::uint32_t completion) {
        port.now = start; APP_REQUIRE(owner.open());
        port.now = decision; APP_REQUIRE(owner.decide(source));
        port.now = completion; APP_REQUIRE(owner.finish());
        return owner.report();
    }
    const app::TransactionReport& tick(std::uint32_t decision,
                                      core::ButtonLevel button = core::ButtonLevel::NONE) {
        source.button = button; return cycle(decision, decision, decision);
    }
    std::uint32_t release(std::uint32_t base = 0U) {
        tick(base); tick(base + 1000U); tick(base + 21000U);
        tick(base + 22000U, core::ButtonLevel::START);
        tick(base + 42000U, core::ButtonLevel::START);
        tick(base + 43000U); const auto time = base + 63000U;
        APP_REQUIRE(tick(time).robot.lifecycle.gate.start_release);
        return time;
    }
    std::uint32_t go(std::uint32_t base = 0U) {
        const auto r = release(base);
        tick(r + 1500000U); tick(r + 1501000U); tick(r + 4500000U);
        tick(r + 5099000U);
        APP_REQUIRE(tick(r + 5100000U).robot.lifecycle.gate.go);
        return r + 5100000U;
    }
};
inline std::uint32_t u32(const std::uint8_t* bytes) {
    return static_cast<std::uint32_t>(bytes[0]) |
        (static_cast<std::uint32_t>(bytes[1]) << 8U) |
        (static_cast<std::uint32_t>(bytes[2]) << 16U) |
        (static_cast<std::uint32_t>(bytes[3]) << 24U);
}
} // namespace app_test

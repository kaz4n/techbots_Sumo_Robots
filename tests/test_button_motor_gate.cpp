// Exercises B3/B13 D087 through Robot and the actual MotorGate callback boundary.
// Host-enabled callbacks prove inhibition writes after button expiry or invalid evidence.
// The same source runs inert by default and active only in the host-only target.
#include "doctest.h"
#include "hal/motors.h"
#include "hal/ui.h"
#include <array>

namespace {
struct ButtonPort {
    std::array<std::uint32_t, 4> pwm{};
    std::uint32_t time = 0U;
    unsigned highs = 0U;
    unsigned lows = 0U;
    unsigned zeros = 0U;
    bool enabled = false;
    static ButtonPort& get(void* p) { return *static_cast<ButtonPort*>(p); }
    static bool configure(void* p) { get(p).enabled = false; return true; }
    static bool configurePwm(void*, motors::Channel) { return true; }
    static bool enable(void* p, bool value) {
        auto& port = get(p);
        port.enabled = value;
        value ? ++port.highs : ++port.lows;
        return true;
    }
    static bool duty(void* p, motors::Channel channel, std::uint32_t, std::uint32_t value) {
        auto& port = get(p);
        port.pwm.at(static_cast<unsigned>(channel)) = value;
        if (value == 0U) ++port.zeros;
        return true;
    }
    static bool settle(void*) { return true; }
    static std::uint32_t clock(void* p) { return get(p).time; }
    motors::Port port() {
        return {this, configure, configurePwm, enable, duty, settle, clock,
                {1000U, 1000U, 1000U, 1000U}};
    }
};
struct AppliedButtons {
    ButtonPort io;
    motors::MotorGate gate{io.port()};
    fsm::Robot robot;
    fsm::RobotInput in;
    fsm::RobotResult last;
    std::uint32_t sequence = 0U;
    AppliedButtons() {
        CHECK(gate.begin());
        in.initialization_complete = true;
        in.observations_fresh = true;
        in.opp_raw_mask = 0x78U;
        in.imu_ok = true;
        in.vbat_valid = true;
        in.vbat_v = 11.1F;
        for (auto& line : in.line_raw_us) line = 1000U;
    }
    void step(std::uint32_t now, core::ButtonLevel level = core::ButtonLevel::NONE,
              core::ButtonPresence presence = core::ButtonPresence::VALID,
              bool decode_unconfigured = false) {
        in.t_us = now;
        in.buttons = {};
        in.buttons.explicit_values = true;
        in.buttons.presence = presence;
        if (presence == core::ButtonPresence::VALID) {
            in.buttons.level = level;
            in.buttons.sequence = sequence++;
            in.buttons.started_us = now - 20U;
            in.buttons.completed_us = now;
        }
        if (decode_unconfigured) {
            power::ButtonSample raw;
            raw.status = power::Status::OK;
            raw.valid = true;
            raw.raw = 100U;
            raw.sequence = sequence++;
            raw.started_us = now - 20U;
            raw.completed_us = now;
            CHECK(ui::applyButtons(in, raw) == ui::ButtonQualification::UNCONFIGURED);
        }
        last = robot.step(in);
        io.time = now;
        const auto applied = gate.apply(now, last);
        CHECK(applied.consumed);
        CHECK(applied.fault == (last.outputs.ui_state == core::State::STOPPED ?
                               motors::Fault::STOPPED : motors::Fault::NONE));
        in.previous = applied.feedback;
        in.previous.duration_valid = true;
        in.previous.completed_us = now;
        CHECK(in.previous.applied_valid);
    }
    void run(std::uint32_t begin, std::uint32_t end, core::ButtonLevel level) {
        for (auto now = begin; now <= end; now += 1000U) step(now, level);
    }
};
}

TEST_CASE("B3 B13 D087 actual enabled MotorGate zeros all channels on button contract failure") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        AppliedButtons rig;
        rig.run(0U, 30000U, core::ButtonLevel::NONE);
        rig.run(31000U, 51000U, core::ButtonLevel::START);
        rig.run(52000U, 72000U, core::ButtonLevel::NONE);
        CHECK(rig.last.lifecycle.gate.start_release);
        rig.run(73000U, 5171000U, core::ButtonLevel::NONE);
        CHECK(rig.io.highs == 0U);
        CHECK_FALSE(rig.io.enabled);
        rig.step(5172000U);
        CHECK(rig.last.lifecycle.gate.go);
        rig.step(5173000U);
        if (MOTORS_ALLOWED != 0) {
            CHECK(rig.io.highs > 0U);
            CHECK(rig.io.enabled);
            CHECK((rig.io.pwm[0] | rig.io.pwm[1] | rig.io.pwm[2] | rig.io.pwm[3]) != 0U);
        } else CHECK(rig.io.highs == 0U);
        const auto lows = rig.io.lows;
        const auto zeros = rig.io.zeros;
        rig.step(scenario == 0U ? 5179000U : 5174000U, core::ButtonLevel::NONE,
                 scenario == 0U ? core::ButtonPresence::ABSENT : core::ButtonPresence::INVALID,
                 scenario == 2U);
        CHECK((rig.last.contract_faults & fsm::BUTTON_CONTRACT) != 0U);
        CHECK(rig.last.outputs.ui_state == core::State::STOPPED);
        CHECK_FALSE(rig.io.enabled);
        CHECK(rig.io.lows > lows);
        CHECK(rig.io.zeros >= zeros + 4U);
        for (const auto value : rig.io.pwm) CHECK(value == 0U);
        CHECK_FALSE(rig.in.previous.motors_enabled);
        CHECK(rig.in.previous.duty_l == 0.0F);
        CHECK(rig.in.previous.duty_r == 0.0F);
    }
}

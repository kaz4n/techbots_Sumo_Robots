// Supplies explicit synthetic raw observations and application receipts to the real Robot.
// Keeps scenario wiring distinct from physical acquisition, output application and timing proof.
// Robot tests use literal behavior expectations; this helper contains no strategy arbitration.
#pragma once
#include "doctest.h"
#include "core/fsm.h"
#include <cmath>
#include <cstdint>

namespace robot_test {
using State = core::State;
using Mode = core::Mode;
using Button = core::ButtonLevel;

inline void zero(const fsm::RobotResult& result, bool disabled = true) {
    CHECK(result.outputs.duty_l == 0.0F);
    CHECK(result.outputs.duty_r == 0.0F);
    if (disabled) CHECK_FALSE(result.outputs.motors_enabled);
}

inline void bounded(const fsm::RobotResult& result) {
    CHECK(std::isfinite(result.outputs.duty_l));
    CHECK(std::isfinite(result.outputs.duty_r));
    CHECK(std::fabs(result.outputs.duty_l) <= 1.0F);
    CHECK(std::fabs(result.outputs.duty_r) <= 1.0F);
    CHECK(std::isfinite(result.heading.heading_deg));
    CHECK(std::isfinite(result.accepted_bias_dps));
    CHECK(result.events.count <= 21U);
    CHECK_FALSE(result.events.overflowed);
    CHECK(result.events.rejected == 0U);
    CHECK(result.events.invalid_metadata == 0U);
    for (unsigned i = 0U; i < result.events.count && i < 21U; ++i)
        CHECK(logframe::validEventMetadata(result.events.entries[i]));
    if (!result.outputs.motors_enabled) zero(result);
}

inline unsigned count(const fsm::RobotResult& result, core::Event type, int detail = -1) {
    unsigned total = 0U;
    for (unsigned i = 0U; i < result.events.count && i < 21U; ++i) {
        const auto& event = result.events.entries[i];
        if (event.type == type && (detail < 0 || event.detail == static_cast<unsigned>(detail))) ++total;
    }
    return total;
}

inline logframe::EventInput event(const fsm::RobotResult& result, core::Event type,
                                  int detail = -1) {
    CHECK(count(result, type, detail) == 1U);
    for (unsigned i = 0U; i < result.events.count && i < 21U; ++i) {
        const auto& found = result.events.entries[i];
        if (found.type == type && (detail < 0 || found.detail == static_cast<unsigned>(detail))) return found;
    }
    return {};
}

inline std::uint32_t u32(const logframe::FrameBytes& frame, unsigned offset) {
    return static_cast<std::uint32_t>(frame.data[offset]) |
        (static_cast<std::uint32_t>(frame.data[offset + 1U]) << 8U) |
        (static_cast<std::uint32_t>(frame.data[offset + 2U]) << 16U) |
        (static_cast<std::uint32_t>(frame.data[offset + 3U]) << 24U);
}

class Rig {
public:
    Rig() {
        input.initialization_complete = true;
        input.observations_fresh = true;
        input.opp_raw_mask = 0x78U;
        input.imu_ok = true;
        input.vbat_v = 11.1F;
        input.vbat_valid = true;
        lines(0U);
    }

    void lines(std::uint8_t mask) {
        for (unsigned bit = 0U; bit < 4U; ++bit)
            input.line_raw_us[bit] = (mask & (1U << bit)) != 0U ? 100U : 1000U;
    }
    void opponent(std::uint8_t logical) { input.opp_raw_mask = static_cast<std::uint8_t>(logical ^ 0x78U); }

    fsm::RobotInput at(std::uint32_t time, Button button = Button::NONE) const {
        auto next = input;
        next.t_us = time;
        next.button = button;
        if (has_previous) {
            next.previous.applied_valid = true;
            next.previous.token = last.token;
            next.previous.applied_us = last_time;
            next.previous.motors_enabled = apply_enabled && last.outputs.motors_enabled;
            next.previous.duty_l = next.previous.motors_enabled ? last.outputs.duty_l * applied_scale : 0.0F;
            next.previous.duty_r = next.previous.motors_enabled ? last.outputs.duty_r * applied_scale : 0.0F;
            next.previous.duration_valid = true;
            next.previous.completed_us = last_time;
            next.previous.execution_us = 0U;
        }
        return next;
    }

    fsm::RobotResult submit(const fsm::RobotInput& observation) {
        const auto result = robot.step(observation);
        if (result.fresh) {
            last = result;
            last_time = observation.t_us;
            has_previous = true;
        }
        return result;
    }
    fsm::RobotResult step(std::uint32_t time, Button button = Button::NONE) {
        return submit(at(time, button));
    }
    void reset() { robot.reset(); has_previous = false; }

    fsm::Robot robot;
    fsm::RobotInput input;
    fsm::RobotResult last;
    std::uint32_t last_time = 0;
    bool has_previous = false;
    bool apply_enabled = true;
    float applied_scale = 1.0F;
};

inline std::uint32_t idle(Rig& rig, std::uint32_t base = 0U) {
    const auto boot = rig.step(base);
    CHECK(boot.outputs.ui_state == State::IDLE);
    CHECK(boot.contract_faults == 0U);
    zero(boot);
    rig.step(base + 1000U);
    rig.step(base + 21000U);
    return base + 21000U;
}

inline std::uint32_t shortMode(Rig& rig, std::uint32_t base) {
    rig.step(base, Button::MODE);
    rig.step(base + 20000U, Button::MODE);
    rig.step(base + 20001U);
    CHECK(rig.step(base + 40001U).menu.selection_changed);
    return base + 40001U;
}

inline std::uint32_t longMode(Rig& rig, std::uint32_t base) {
    rig.step(base, Button::MODE);
    rig.step(base + 20000U, Button::MODE);
    CHECK(rig.step(base + 1020000U, Button::MODE).menu.menu_toggled);
    rig.step(base + 1020001U);
    rig.step(base + 1040001U);
    return base + 1040001U;
}

inline std::uint32_t select(Rig& rig, Mode mode, std::uint32_t base = 0U) {
    auto time = idle(rig, base);
    for (unsigned index = 1U; index < static_cast<unsigned>(mode); ++index)
        time = shortMode(rig, time + 1U);
    CHECK(rig.last.menu.selection.mode == mode);
    return time;
}

inline std::uint32_t release(Rig& rig, std::uint32_t base) {
    rig.step(base + 1000U, Button::START);
    rig.step(base + 21000U, Button::START);
    rig.step(base + 22000U);
    CHECK_FALSE(rig.step(base + 41999U).lifecycle.gate.start_release);
    const auto result = rig.step(base + 42000U);
    CHECK(result.lifecycle.gate.start_release);
    CHECK(result.outputs.ui_state == State::COUNTDOWN);
    zero(result);
    return base + 42000U;
}

inline std::uint32_t go(Rig& rig, Mode mode = Mode::SIDESTEP_R, std::uint32_t base = 0U) {
    const auto anchor = release(rig, select(rig, mode, base));
    rig.step(anchor + 1500000U);
    rig.step(anchor + 1501000U);
    rig.step(anchor + 4500000U);
    zero(rig.step(anchor + 5099999U));
    CHECK(rig.step(anchor + 5100000U).lifecycle.gate.go);
    return anchor + 5100000U;
}

inline std::uint32_t attack(Rig& rig) {
    rig.opponent(2U);
    const auto time = go(rig, Mode::DIRECT);
    CHECK(rig.last.outputs.ui_state == State::TRACK);
    CHECK(rig.step(time + 1000U).outputs.ui_state == State::TRACK);
    rig.input.ax_g = 2.0F;
    const auto contact = rig.step(time + 2000U);
    CHECK(contact.outputs.ui_state == State::ATTACK);
    CHECK(contact.contact);
    rig.input.ax_g = 0.0F;
    const auto full = rig.step(time + 52000U);
    CHECK(full.outputs.duty_l == doctest::Approx(1.0F));
    CHECK(full.outputs.duty_r == doctest::Approx(1.0F));
    return time + 52000U;
}

inline std::uint32_t randomWord(std::uint32_t& value) {
    value ^= value << 13U;
    value ^= value >> 17U;
    value ^= value << 5U;
    return value;
}
} // namespace robot_test

// Supplies independent D092 acquisition, decision and completion clocks.
// Keeps synthetic receipts separate from optional actual MotorGate feedback.
// New timing tests use this fixture without changing any established test rig.
#pragma once
#include "doctest.h"
#include "core/fsm.h"
#include "hal/motors.h"
#include "hal/recorder.h"
#include <cstdint>

namespace timing_test {
struct Port {
    std::uint32_t now = 0;
    std::uint32_t nonzero_writes = 0;
    bool enabled = false;
    static bool enableSetup(void*) { return true; }
    static bool pwmSetup(void*, motors::Channel) { return true; }
    static bool enable(void* context, bool value) {
        static_cast<Port*>(context)->enabled = value; return true;
    }
    static bool pwm(void* context, motors::Channel, std::uint32_t, std::uint32_t pulse) {
        if (pulse != 0U) ++static_cast<Port*>(context)->nonzero_writes;
        return true;
    }
    static bool settle(void*) { return true; }
    static std::uint32_t clock(void* context) { return static_cast<Port*>(context)->now; }
    motors::Port port() {
        return {this, enableSetup, pwmSetup, enable, pwm, settle, clock, {1000, 1000, 1000, 1000}};
    }
};
class Rig {
public:
    explicit Rig(bool explicit_start = true, bool actual_gate = false, bool imu = false)
        : gate(port.port()), real_gate(actual_gate), explicit_imu(imu) {
        input.initialization_complete = true;
        input.observations_fresh = true;
        input.opp_raw_mask = 0x78U;
        input.imu_ok = true;
        input.vbat_v = 11.1F;
        input.vbat_valid = true;
        for (auto& line : input.line_raw_us) line = 1000U;
        input.timing.explicit_start = explicit_start;
        input.timing.start_valid = true;
        if (real_gate) CHECK(gate.begin());
    }
    fsm::RobotInput at(std::uint32_t decision, std::uint32_t start) const {
        auto value = input;
        value.t_us = decision;
        value.timing.started_us = start;
        value.previous = previous;
        if (explicit_imu) {
            value.imu.explicit_values = true;
            value.imu.heading_available = true;
            value.imu.heading_updated = true;
            value.imu.gyro = core::ImuPresence::VALID;
            value.imu.accel = core::ImuPresence::VALID;
            value.imu.checked_us = decision;
            value.imu.observation_us = decision;
            value.imu.sequence = static_cast<std::uint32_t>(last.token + 1U);
        }
        return value;
    }
    fsm::RobotResult submit(const fsm::RobotInput& value, std::uint32_t apply_delay = 0,
                            std::uint32_t complete_delay = 0) {
        const auto result = robot.step(value);
        if (!result.fresh) return result;
        last = result;
        decision = value.t_us;
        start = value.timing.started_us;
        if (real_gate) {
            port.now = decision + apply_delay;
            const auto applied = gate.apply(decision, result);
            CHECK(applied.consumed);
            CHECK(applied.feedback.applied_valid);
            previous = applied.feedback;
        } else {
            previous.applied_valid = true;
            previous.token = result.token;
            previous.applied_us = decision + apply_delay;
            previous.motors_enabled = result.outputs.motors_enabled;
            previous.duty_l = result.outputs.duty_l;
            previous.duty_r = result.outputs.duty_r;
        }
        previous.duration_valid = true;
        previous.completed_us = decision + complete_delay;
        previous.execution_us = previous.completed_us -
            (input.timing.explicit_start ? start : decision);
        source.consume(result);
        return result;
    }
    fsm::RobotResult step(std::uint32_t decision, core::ButtonLevel button = core::ButtonLevel::NONE) {
        auto value = at(decision, decision); value.button = button; return submit(value);
    }
    std::uint32_t release(std::uint32_t base = 0) {
        step(base); step(base + 1000U); step(base + 21000U);
        step(base + 22000U, core::ButtonLevel::START);
        step(base + 42000U, core::ButtonLevel::START);
        step(base + 43000U);
        const auto value = step(base + 63000U);
        CHECK(value.lifecycle.gate.start_release);
        return base + 63000U;
    }
    std::uint32_t go(std::uint32_t acquisition = 0, std::uint32_t base = 0) {
        const auto released = release(base);
        step(released + 1500000U); step(released + 1501000U);
        step(released + 4500000U); step(released + 5099000U);
        const auto time = released + 5100000U;
        CHECK(submit(at(time, time - acquisition)).lifecycle.gate.go);
        return time;
    }
    fsm::RobotInput receipt(std::uint32_t next_start, std::uint32_t next_decision,
                            std::uint32_t applied, std::uint32_t completed,
                            std::uint32_t duration) const {
        auto value = at(next_decision, next_start);
        value.previous.applied_us = applied;
        value.previous.completed_us = completed;
        value.previous.execution_us = duration;
        return value;
    }
    fsm::Robot robot;
    Port port;
    motors::MotorGate gate;
    recorder::AttemptRecorder source;
    fsm::RobotInput input;
    fsm::RobotResult last;
    fsm::PreviousTick previous;
    std::uint32_t decision = 0, start = 0;
    bool real_gate = false, explicit_imu = false;
};
inline unsigned count(const fsm::RobotResult& value, core::Event type, int detail = -1) {
    unsigned result = 0;
    for (unsigned index = 0; index < value.events.count; ++index) {
        const auto& item = value.events.entries[index];
        if (item.type == type && (detail < 0 || item.detail == detail)) ++result;
    }
    return result;
}
inline logframe::EventInput event(const fsm::RobotResult& value, core::Event type, int detail = -1) {
    CHECK(count(value, type, detail) == 1U);
    for (unsigned index = 0; index < value.events.count; ++index) {
        const auto& item = value.events.entries[index];
        if (item.type == type && (detail < 0 || item.detail == detail)) return item;
    }
    return {};
}
inline void cleanTiming(const fsm::RobotResult& value, std::uint32_t duration) {
    CHECK(value.contract_faults == 0U);
    CHECK_FALSE(value.timing_incomplete);
    CHECK(value.ticks.ticks == 1U);
    CHECK(value.ticks.max_us == duration);
    CHECK(value.ticks.overruns == (duration > 1000U ? 1U : 0U));
}
inline void badTiming(const fsm::RobotResult& value, std::uint32_t detection) {
    CHECK(value.contract_faults == 0U);
    CHECK(value.timing_incomplete);
    CHECK(value.ticks.ticks == 0U);
    CHECK(value.outputs.ui_state != core::State::STOPPED);
    const auto warning = event(value, core::Event::FAULT, 9);
    CHECK(warning.value == 4U);
    CHECK(warning.t_us == detection);
}
} // namespace timing_test

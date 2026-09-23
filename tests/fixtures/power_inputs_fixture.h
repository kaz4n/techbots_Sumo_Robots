// Supplies contract-controlled setup, A0, A1 and clock callbacks for D093.
// Distinguishes real callback attempts from retained battery projections.
// New owner tests validate chronology independently of implementation bodies.
#pragma once
#include "doctest.h"
#include "hal/power_inputs.h"
#include "config.h"
#include <cstdint>
#include <initializer_list>

namespace power_inputs_test {
inline float voltage(std::uint16_t raw) {
    return float(raw) / 16383.0F * config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
}
struct Fake {
    std::uint32_t now = 100U, setup_elapsed = 0U, duration = 3U, tail = 2U;
    unsigned clocks = 0U, setups = 0U, batteries = 0U, buttons = 0U;
    std::uint16_t raw = 8192U;
    std::uint32_t sequence = 0U;
    bool auto_battery = true, auto_buttons = true;
    power::InitResult setup_result{power::Status::OK, power::Shutdown::NOT_ATTEMPTED, true};
    power::Sample battery;
    power::ButtonSample button;
    static power::InitResult setup(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.setups;
        f.now += f.setup_elapsed; return f.setup_result;
    }
    static power::Sample a0(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.batteries;
        if (f.auto_battery)
            f.battery = {power::Status::OK, power::Shutdown::NOT_ATTEMPTED, f.raw,
                         f.now, f.now + f.duration, voltage(f.raw), true};
        f.now += f.duration + f.tail; return f.battery;
    }
    static power::ButtonSample a1(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.buttons;
        if (f.auto_buttons)
            f.button = {power::Status::OK, power::Shutdown::NOT_ATTEMPTED, f.raw,
                        f.now, f.now + f.duration, ++f.sequence, true};
        f.now += f.duration + f.tail; return f.button;
    }
    static std::uint32_t clock(void* context) {
        auto& f = *static_cast<Fake*>(context); ++f.clocks; return f.now;
    }
    power::InputPort port() { return {this, setup, a0, a1, clock}; }
    unsigned callbacks() const { return clocks + setups + batteries + buttons; }
};
struct Rig {
    Fake fake;
    power::InputOwner owner{fake.port()};
    void begin() { CHECK(owner.begin()); }
    power::BatteryRead prime() { begin(); const auto read = owner.readBatteryIfDue(true); CHECK(read.accepted); return read; }
};
inline void same(const power::Sample& a, const power::Sample& b) {
    CHECK(a.status == b.status); CHECK(a.shutdown == b.shutdown); CHECK(a.raw == b.raw);
    CHECK(a.started_us == b.started_us); CHECK(a.completed_us == b.completed_us);
    CHECK(a.valid == b.valid);
    if (a.voltage_v == a.voltage_v) CHECK(a.voltage_v == b.voltage_v);
    else CHECK(b.voltage_v != b.voltage_v);
}
inline void blocked(Rig& rig, power::InputFault expected, power::InputOperation operation) {
    const auto before = rig.fake.callbacks();
    const auto snapshot = rig.owner.report();
    CHECK(snapshot.fault == expected); CHECK(snapshot.fault_operation == operation);
    CHECK_FALSE(snapshot.ready); CHECK_FALSE(snapshot.battery_available); CHECK_FALSE(snapshot.battery_due);
    CHECK_FALSE(rig.owner.begin());
    CHECK_FALSE(rig.owner.readBatteryIfDue(true).attempted);
    CHECK_FALSE(rig.owner.readButtons(true).attempted);
    rig.owner.observe(rig.fake.now + 1U);
    fsm::RobotInput input; input.t_us = rig.fake.now + 2U;
    CHECK_FALSE(rig.owner.applyBattery(input));
    CHECK(rig.owner.applyButtons(input, {}) == ui::ButtonQualification::INVALID);
    CHECK_FALSE(input.buttons.contract_valid);
    CHECK(input.buttons.presence == core::ButtonPresence::INVALID);
    CHECK(rig.fake.callbacks() == before);
    CHECK(rig.owner.report().fault == snapshot.fault);
    CHECK(rig.owner.report().first_status == snapshot.first_status);
    CHECK(rig.owner.report().first_shutdown == snapshot.first_shutdown);
}
} // namespace power_inputs_test

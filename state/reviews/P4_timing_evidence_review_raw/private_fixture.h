// Independently reproduces invalid intermediate D129 epoch chronology.
// Uses real Robot and Gate receipts; timestamps and source windows are synthetic.
// Frozen before execution and retained even after the production fix.
#include "fixtures/app_transaction_fixture.h"
#include <vector>

namespace {
using Detail = logframe::TimingDetail;
using Button = core::ButtonLevel;
struct Rig {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    fsm::RobotResult last;
    std::vector<logframe::EventInput> events;
    Rig() { APP_REQUIRE(gate.begin()); }
    const fsm::RobotResult& atWindow(std::uint32_t time, std::uint32_t start,
        std::uint32_t read_start, std::uint32_t read_end, Button button = Button::NONE) {
        input.t_us = time; input.button = button;
        input.timing = {true, true, start};
        input.opponent_read = {true, read_start, read_end};
        port.now = time;
        last = robot.step(input);
        if (last.fresh) {
            for (unsigned i = 0U; i < last.events.count; ++i)
                if (last.events.entries[i].type == core::Event::TIMING)
                    events.push_back(last.events.entries[i]);
            input.previous = gate.apply(time, last).feedback;
            APP_REQUIRE(input.previous.applied_valid);
            input.previous.completed_us = port.now;
            input.previous.duration_valid = true;
            input.previous.execution_us = port.now - start;
        }
        return last;
    }
    const fsm::RobotResult& at(std::uint32_t t, Button button = Button::NONE) {
        return atWindow(t, t - 100U, t - 80U, t - 60U, button);
    }
    unsigned count(Detail detail) const {
        unsigned found = 0U;
        for (const auto& event : events)
            found += event.detail == static_cast<unsigned>(detail);
        return found;
    }
    std::uint32_t approach(std::uint32_t base = 0U) {
        input.opp_raw_mask = 2U ^ 0x78U;
        at(base); at(base + 1000U); at(base + 21000U); at(base + 22000U, Button::START);
        at(base + 42000U, Button::START); at(base + 43000U);
        APP_REQUIRE(at(base + 63000U).lifecycle.gate.start_release);
        const std::uint32_t go = base + 5163000U;
        APP_REQUIRE(at(go).lifecycle.gate.go);
        for (unsigned i = 1U; i <= 8U; ++i) at(go + i * 1000U);
        at(go + 50000U);
        APP_REQUIRE(last.outputs.ui_state == core::State::ATTACK);
        APP_REQUIRE(!last.contact);
        APP_REQUIRE(input.previous.motors_enabled == (MOTORS_ALLOWED != 0));
        if (MOTORS_ALLOWED) APP_REQUIRE(input.previous.duty_l > 0.0F && input.previous.duty_r > 0.0F);
        return go;
    }
};
}


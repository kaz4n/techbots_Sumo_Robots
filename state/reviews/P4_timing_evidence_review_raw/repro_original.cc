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
    std::uint32_t approach() {
        input.opp_raw_mask = 2U ^ 0x78U;
        at(0U); at(1000U); at(21000U); at(22000U, Button::START);
        at(42000U, Button::START); at(43000U);
        APP_REQUIRE(at(63000U).lifecycle.gate.start_release);
        constexpr std::uint32_t go = 5163000U;
        APP_REQUIRE(at(go).lifecycle.gate.go);
        for (unsigned i = 1U; i <= 8U; ++i) at(go + i * 1000U);
        at(go + 50000U);
        APP_REQUIRE(last.outputs.ui_state == core::State::ATTACK);
        APP_REQUIRE(!last.contact);
        APP_REQUIRE(input.previous.motors_enabled);
        APP_REQUIRE(input.previous.duty_l > 0.0F && input.previous.duty_r > 0.0F);
        return go;
    }
};
}

TEST_CASE("D129 private invalid intermediate epoch closes candidate before a later genuine zero") {
    static_assert(MOTORS_ALLOWED == 1);
    Rig rig;
    const auto onset = rig.approach() + 60000U;
    rig.input.opp_raw_mask = 0x78U;
    rig.at(onset);
    APP_REQUIRE(rig.count(Detail::LOSS_READ_START) == 1U);
    APP_REQUIRE(rig.count(Detail::LOSS_READ_END) == 1U);
    // All offsets inside this alleged epoch look valid, but its start precedes
    // the preceding actual receipt completion and its window repeats old data.
    rig.atWindow(onset + 1000U, onset - 100U, onset - 80U, onset - 60U);
    CHECK(rig.count(Detail::INVALID_SOURCE_TIME) == 1U);
    CHECK(rig.last.timing_incomplete);
    CHECK(rig.last.contract_faults == 0U);
    CHECK(rig.last.outputs.ui_state == core::State::ATTACK);
    rig.at(onset + 30000U);
    CHECK(rig.last.outputs.duty_l == 0.0F);
    CHECK(rig.last.outputs.duty_r == 0.0F);
    rig.at(onset + 31000U);
    CHECK(rig.count(Detail::LOSS_BRAKE_DECISION) == 0U);
    CHECK(rig.count(Detail::LOSS_ZERO_APPLIED) == 0U);
    CHECK(rig.count(Detail::INVALID_SOURCE_TIME) == 1U);
    CHECK(rig.last.timing_incomplete);
}

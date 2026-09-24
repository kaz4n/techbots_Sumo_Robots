// Supplies independent D126 observations around actual Robot and motor owners.
// Distinguishes the selected final electrical cap from raw Straight requests.
// M0/M1 and five identified duty overlays share these public-contract checks.
#pragma once
#include "drive_test_fixture.h"
#include "app_service_reset/fixture.h"

namespace stop_test {
using Rig = drive_test::Rig;
using Button = drive_test::Button;
using Phase = stop_trial::Phase;
using Reason = stop_trial::Reason;
constexpr float DUTY = config::STOP_TRIAL_DUTY;

inline void bounded(const stop_trial::Report& r) {
    CHECK(std::isfinite(r.duty_l)); CHECK(std::isfinite(r.duty_r));
    CHECK(r.duty_l >= 0.0F); CHECK(r.duty_r >= 0.0F);
    CHECK(r.duty_l <= 1.0F); CHECK(r.duty_r <= 1.0F);
    if (r.phase != Phase::APPROACH) { CHECK(r.duty_l == 0.0F); CHECK(r.duty_r == 0.0F); }
}
inline void same(const stop_trial::Report& a, const stop_trial::Report& b) {
    CHECK(a.phase == b.phase); CHECK(a.reason == b.reason); CHECK(a.approach_status == b.approach_status);
    CHECK(a.duty_l == b.duty_l); CHECK(a.duty_r == b.duty_r); CHECK(a.started_us == b.started_us);
    CHECK(a.approach_finished_us == b.approach_finished_us); CHECK(a.finished_us == b.finished_us);
    CHECK(a.started == b.started); CHECK(a.approach_finished == b.approach_finished);
    CHECK(a.finished == b.finished); CHECK(a.imu_fallback == b.imu_fallback); bounded(a);
}
inline void running(const Rig& rig, const app::TransactionReport& r) {
    drive_test::moving(rig, r); CHECK_FALSE(r.robot.stop_trial_stopping);
    CHECK_FALSE(r.robot.stop_trial_edge_interrupted); bounded(r.robot.stop_trial);
    CHECK(r.robot.stop_trial.started); CHECK(r.robot.outputs.ui_state != core::State::SEARCH);
    CHECK(r.robot.outputs.duty_l >= 0.0F); CHECK(r.robot.outputs.duty_r >= 0.0F);
    CHECK(r.robot.outputs.duty_l <= DUTY); CHECK(r.robot.outputs.duty_r <= DUTY);
}
inline void approach(const Rig& rig, const app::TransactionReport& r, std::uint32_t go) {
    running(rig, r); CHECK(r.robot.stop_trial.phase == Phase::APPROACH);
    CHECK(r.robot.stop_trial.reason == Reason::NONE);
    CHECK(r.robot.stop_trial.approach_status == motion::Status::ACTIVE);
    CHECK(r.robot.stop_trial.started_us == go);
    CHECK_FALSE(r.robot.stop_trial.approach_finished); CHECK_FALSE(r.robot.stop_trial.finished);
}
inline void brake(const Rig& rig, const app::TransactionReport& r, std::uint32_t observed) {
    running(rig, r); const auto& t = r.robot.stop_trial;
    CHECK(t.phase == Phase::BRAKE); CHECK(t.reason == Reason::NO_EDGE_TIMEOUT);
    CHECK(t.approach_status == motion::Status::DONE); CHECK(t.approach_finished);
    CHECK(t.approach_finished_us == observed); CHECK_FALSE(t.finished);
    CHECK(r.robot.outputs.duty_l == 0.0F); CHECK(r.robot.outputs.duty_r == 0.0F);
    CHECK(r.applied.feedback.duty_l == 0.0F); CHECK(r.applied.feedback.duty_r == 0.0F);
    for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
}
inline void complete(Rig& rig, const app::TransactionReport& r, std::uint32_t time) {
    CHECK(r.robot.stop_trial.phase == Phase::COMPLETE); CHECK(r.robot.stop_trial.reason == Reason::NO_EDGE_TIMEOUT);
    CHECK(r.robot.stop_trial.approach_status == motion::Status::DONE); CHECK(r.robot.stop_trial.finished);
    CHECK(r.robot.stop_trial.finished_us == time); CHECK(r.robot.stop_trial_stopping);
    CHECK_FALSE(r.robot.stop_trial_edge_interrupted); drive_test::disabled(r, rig.port);
    CHECK(r.robot.lifecycle.gate.phase == countdown::Phase::READY);
}
struct ActualRobot {
    app_test::Port port;
    motors::MotorGate gate{port.port()};
    fsm::Robot robot;
    fsm::RobotInput input = app_test::input();
    ActualRobot() { APP_REQUIRE(gate.begin()); }
    fsm::RobotResult at(std::uint32_t time, Button button = Button::NONE) {
        port.now = time; input.t_us = time; input.button = button;
        const auto result = robot.step(input);
        if (result.fresh) input.previous = gate.apply(time, result).feedback;
        return result;
    }
    std::uint32_t go() {
        struct Observation { std::uint32_t time; Button button; };
        const Observation sequence[] = {{0U,Button::NONE},{1000U,Button::NONE},{21000U,Button::NONE},
            {22000U,Button::MODE},{42000U,Button::MODE},{1042000U,Button::MODE},
            {1043000U,Button::NONE},{1063000U,Button::NONE},{1064000U,Button::MODE},
            {1084000U,Button::MODE},{1085000U,Button::NONE},{1105000U,Button::NONE},
            {1106000U,Button::MODE},{1126000U,Button::MODE},{1127000U,Button::NONE},
            {1147000U,Button::NONE},{1148000U,Button::START},{1168000U,Button::START},
            {1169000U,Button::NONE},{1189000U,Button::NONE}};
        for (const auto& sample : sequence) at(sample.time, sample.button);
        APP_REQUIRE(at(6289000U).lifecycle.gate.go); return 6289000U;
    }
};
} // namespace stop_test

// Supplies D125 expectations around genuine menu and actual application owners.
// Uses the configured signed angle so isolated identified overlays share the oracle.
// Independent profile M0/M1 cases exercise real Gate callbacks without hardware.
#pragma once
#include "drive_test_fixture.h"
#include "app_service_reset/fixture.h"

namespace turn_integration {
using Rig = drive_test::Rig;
using Button = drive_test::Button;
using Phase = turn_trial::Phase;
using Reason = turn_trial::Reason;
constexpr float ANGLE = config::TURN_TRIAL_DEG;
constexpr float SIGN = ANGLE > 0.0F ? 1.0F : -1.0F;
constexpr std::uint32_t FALLBACK_US = ANGLE == 90.0F || ANGLE == -90.0F ? 180000U : 360000U;

inline void bounded(const turn_trial::Report& r) {
    CHECK(std::isfinite(r.signed_angle_deg)); CHECK(std::isfinite(r.duty_l));
    CHECK(std::isfinite(r.duty_r)); CHECK(std::fabs(r.duty_l) <= .8F);
    CHECK(std::fabs(r.duty_r) <= .8F); CHECK(r.duty_l == -r.duty_r);
}
inline void sameTrial(const turn_trial::Report& a, const turn_trial::Report& b) {
    CHECK(a.phase == b.phase); CHECK(a.reason == b.reason); CHECK(a.turn_status == b.turn_status);
    CHECK(a.signed_angle_deg == b.signed_angle_deg); CHECK(a.duty_l == b.duty_l);
    CHECK(a.duty_r == b.duty_r); CHECK(a.started_us == b.started_us);
    CHECK(a.turn_finished_us == b.turn_finished_us); CHECK(a.finished_us == b.finished_us);
    CHECK(a.turn_finished == b.turn_finished); CHECK(a.finished == b.finished);
    CHECK(a.imu_fallback == b.imu_fallback); bounded(a);
}
inline void running(const Rig& rig, const app::TransactionReport& report) {
    drive_test::moving(rig, report); bounded(report.robot.turn_trial);
    CHECK_FALSE(report.robot.turn_trial_stopping); CHECK_FALSE(report.robot.turn_trial_edge_interrupted);
    CHECK(report.robot.turn_trial.signed_angle_deg == ANGLE);
    CHECK(report.robot.outputs.ui_state != core::State::SEARCH);
    CHECK(std::fabs(report.robot.outputs.duty_l) <= .8F);
    CHECK(std::fabs(report.robot.outputs.duty_r) <= .8F);
}
inline void braking(const Rig& rig, const app::TransactionReport& report,
                    motion::Status status, std::uint32_t observed) {
    running(rig, report); const auto& trial = report.robot.turn_trial;
    CHECK(trial.phase == Phase::BRAKE); CHECK(trial.turn_status == status);
    CHECK(trial.turn_finished); CHECK(trial.turn_finished_us == observed); CHECK_FALSE(trial.finished);
    CHECK(trial.duty_l == 0.0F); CHECK(trial.duty_r == 0.0F);
    CHECK(report.robot.outputs.duty_l == 0.0F); CHECK(report.robot.outputs.duty_r == 0.0F);
    CHECK(report.applied.feedback.duty_l == 0.0F); CHECK(report.applied.feedback.duty_r == 0.0F);
    for (auto pulse : rig.port.pulses) CHECK(pulse == 0U);
}
inline void completed(Rig& rig, const app::TransactionReport& report,
                      motion::Status status, std::uint32_t observed) {
    CHECK(report.robot.turn_trial.phase == Phase::COMPLETE);
    CHECK(report.robot.turn_trial.turn_status == status); CHECK(report.robot.turn_trial.finished);
    CHECK(report.robot.turn_trial.finished_us == observed); CHECK(report.robot.turn_trial_stopping);
    CHECK_FALSE(report.robot.turn_trial_edge_interrupted); drive_test::disabled(report, rig.port);
    CHECK(report.robot.lifecycle.gate.phase == countdown::Phase::READY);
}
inline unsigned timeoutCount(const recorder::AttemptRecorder& recording, std::uint32_t time) {
    unsigned count = 0U;
    for (std::size_t i = 0U; i < recording.events().size(); ++i) {
        const auto* e = recording.events().at(i); APP_REQUIRE(e != nullptr);
        if (e->data[4] != static_cast<unsigned>(core::Event::FAULT) ||
            e->data[5] != static_cast<unsigned>(logframe::FaultCode::TURN_TIMEOUT)) continue;
        ++count; CHECK(e->data[6] == 16U); CHECK(e->data[7] == 0U);
        CHECK(app_test::u32(e->data) == time);
    }
    return count;
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
} // namespace turn_integration

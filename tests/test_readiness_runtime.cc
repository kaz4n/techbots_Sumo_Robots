// Tests D138 B13 readiness at the actual Runtime/Transaction/MotorGate boundary.
// Synthetic sources capture submitted pixels without replacing any production owner.
// Root executes configured M0/M1 builds; no result is physical acceptance.
#include "doctest.h"
#include "fixtures/app_runtime_fixture.h"
#include <cmath>

#define P7_REQUIRE(...) do { const bool ok = (__VA_ARGS__); CHECK(ok); if (!ok) return; } while (false)
#define P7_REQUIRE_FALSE(...) P7_REQUIRE(!(__VA_ARGS__))

namespace readiness_runtime {
constexpr std::uint16_t NONE = 50U, START = 1000U, MODE = 2000U, BOTH = 3000U;
struct Source : runtime_test::Fake {
    ui::Frame displayed;
    std::uint32_t displayed_at = 0U;
    std::uint16_t battery_raw = 11000U;
    unsigned displays = 0U, highs = 0U, nonzero = 0U;
    bool reject_pwm = false;
    static Source& cast(void* c) { return *static_cast<Source*>(c); }
    static power::Sample battery(void* c) {
        auto& f = cast(c); f.note(runtime_test::Call::BATTERY); ++f.batteries;
        const auto started = f.now; f.now += f.adc_work;
        if (f.adc_failure) return {power::Status::OVERRUN,power::Shutdown::DISABLED};
        const auto raw = f.battery_raw;
        const float voltage = float(raw) / 16383.0F * config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
        return {power::Status::OK,power::Shutdown::NOT_ATTEMPTED,raw,started,f.now,voltage,true};
    }
    static bool enable(void* c, bool high) {
        auto& f = cast(c); if (high) ++f.highs; return Fake::enable(c,high);
    }
    static bool pwm(void* c, motors::Channel channel, std::uint32_t period, std::uint32_t pulse) {
        auto& f = cast(c); if (pulse != 0U) ++f.nonzero;
        return Fake::pwm(c,channel,period,pulse) && !f.reject_pwm;
    }
    static ui::MatrixStatus matrix(void* c, std::uint32_t time, const ui::Frame& frame) {
        auto& f = cast(c); f.displayed = frame; f.displayed_at = time; ++f.displays;
        return Fake::matrix(c,time,frame);
    }
    motors::Port motorPort() {
        auto p = Fake::motorPort(); p.writeEnable = enable; p.writePwm = pwm; return p;
    }
    power::InputPort adcPort() { return {this,Fake::adcSetup,battery,Fake::button,Fake::clock}; }
    app::SourcePort sourcePort() {
        auto p = Fake::sourcePort(); p.submitMatrix = matrix; return p;
    }
};
struct Rig {
    Source fake;
    app::Runtime owner{fake.motorPort(),fake.adcPort(),fake.sourcePort()};
    bool begin(bool control = true, bool imu = true, bool service_reset = false) {
        auto g = runtime_test::grants(control,imu);
        g.matrix_enabled = true; g.matrix = {true,true}; g.local_service_reset = service_reset;
#ifndef APP_TEST_CONFIGURED_BUTTONS
        g.adc_pair = false;
#endif
        return owner.begin(g);
    }
    bool next() { fake.now = owner.report().next_release_us; return owner.step(); }
    bool run(unsigned ticks, std::uint16_t raw = NONE) {
        fake.button_raw = raw;
        for (unsigned i = 0U; i < ticks; ++i) if (!next()) return false;
        return true;
    }
    const fsm::RobotResult& robot() const { return owner.transaction().report().robot; }
};
bool hasR(const ui::Frame& f) {
    constexpr unsigned rows[] = {6U,5U,6U,5U,5U};
    for (unsigned y = 0U; y < 5U; ++y) for (unsigned x = 0U; x < 3U; ++x) {
        const auto expected = (rows[y] & (4U >> x)) ? 7U : 0U;
        if (f.pixels[(y+1U)*13U+10U+x] != expected) return false;
    }
    return true;
}
void zero(const Rig& rig) {
    CHECK_FALSE(rig.fake.enabled);
    for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
    const auto& applied = rig.owner.transaction().report().applied.feedback;
    CHECK_FALSE(applied.motors_enabled); CHECK(applied.duty_l == 0.0F); CHECK(applied.duty_r == 0.0F);
}
bool noMotionYet(const Rig& rig) { return rig.fake.highs == 0U && rig.fake.nonzero == 0U; }
} // namespace readiness_runtime
using namespace readiness_runtime;

TEST_CASE("B13 D138 actual default grants cannot manufacture readiness or hardware setup") {
    Rig rig; CHECK(rig.owner.begin({})); CHECK(rig.next());
    CHECK(rig.robot().outputs.ui_state == core::State::BOOT);
    CHECK_FALSE(rig.robot().match_start_eligible); CHECK(rig.fake.displays == 0U);
    CHECK(rig.fake.buttons == 0U); CHECK(rig.fake.opponents == 0U);
    CHECK(rig.fake.line_starts == 0U); CHECK(rig.fake.imu_setups == 0U); zero(rig);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B13 D138 actual qualified Runtime blinks R only in M1 with genuine zero receipts") {
    Rig rig; P7_REQUIRE(rig.begin()); P7_REQUIRE(rig.run(40U));
    CHECK(rig.owner.report().initialization_complete); CHECK(rig.robot().match_start_eligible);
    bool lit = false, dark = false;
    for (unsigned i = 0U; i < 1100U; ++i) {
        P7_REQUIRE(rig.next()); const auto& tx = rig.owner.transaction().report();
        P7_REQUIRE(tx.applied.consumed); P7_REQUIRE(tx.applied.feedback.applied_valid);
        CHECK(tx.applied.feedback.token == tx.robot.token); CHECK(tx.applied.fault == motors::Fault::NONE);
        CHECK(rig.robot().match_start_eligible); CHECK(rig.robot().imu_available);
        CHECK(rig.fake.displayed.pixels[90U] == 7U);
        const bool even = (tx.decision_us / 1000U / config::UI_FAULT_PAGE_MS) % 2U == 0U;
        CHECK(hasR(rig.fake.displayed) == (MOTORS_ALLOWED != 0 && even));
        lit = lit || hasR(rig.fake.displayed); dark = dark || !hasR(rig.fake.displayed);
        zero(rig);
    }
    CHECK(lit == (MOTORS_ALLOWED != 0)); CHECK(dark); CHECK(noMotionYet(rig));
}
TEST_CASE("B13 D138 actual ungranted ADC leaves battery unknown and cannot advertise readiness") {
    Rig rig; auto g = runtime_test::grants(true,true); g.adc_pair = false;
    g.matrix_enabled = true; g.matrix = {true,true};
    P7_REQUIRE(rig.owner.begin(g)); P7_REQUIRE(rig.run(40U));
    CHECK_FALSE(rig.owner.decisionInput().vbat_valid); CHECK(rig.fake.batteries == 0U);
    CHECK_FALSE(rig.robot().match_start_eligible); CHECK_FALSE(hasR(rig.fake.displayed));
    CHECK(rig.fake.displayed.pixels[90U] == 0U); zero(rig); CHECK(noMotionYet(rig));
}
TEST_CASE("B13 D138 actual valid ADC values straddle warning without changing control requests") {
    std::uint16_t above = 0U;
    for (unsigned raw = 0U; raw <= 16383U; ++raw) {
        const float value = float(raw) / 16383.0F * config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
        if (value >= config::VBAT_WARN_V) { above = static_cast<std::uint16_t>(raw); break; }
    }
    P7_REQUIRE(above > 0U);
    for (bool sufficient : {false,true}) {
        Rig rig; rig.fake.battery_raw = sufficient ? above : static_cast<std::uint16_t>(above-1U);
        P7_REQUIRE(rig.begin()); P7_REQUIRE(rig.run(40U));
        const auto& source = rig.owner.decisionInput(); P7_REQUIRE(source.vbat_valid);
        CHECK((source.vbat_v >= config::VBAT_WARN_V) == sufficient);
        CHECK(rig.robot().match_start_eligible);
        CHECK(rig.fake.displayed.pixels[90U] == (sufficient ? 7U : 3U));
        if (!sufficient) CHECK_FALSE(hasR(rig.fake.displayed));
        zero(rig); CHECK(noMotionYet(rig));
    }
}
TEST_CASE("B13 D138 current low marker does not wait for filtered low battery latch") {
    Rig rig; P7_REQUIRE(rig.begin()); P7_REQUIRE(rig.run(40U));
    P7_REQUIRE_FALSE(rig.robot().low_battery); rig.fake.battery_raw = 9000U;
    bool low_seen = false;
    for (unsigned i = 0U; i < 20U; ++i) {
        P7_REQUIRE(rig.next());
        if (rig.owner.decisionInput().vbat_v < config::VBAT_WARN_V) {
            low_seen = true; CHECK(rig.fake.displayed.pixels[90U] == 3U);
            CHECK_FALSE(hasR(rig.fake.displayed)); CHECK_FALSE(rig.robot().low_battery); break;
        }
    }
    CHECK(low_seen); zero(rig); CHECK(noMotionYet(rig));
}
TEST_CASE("B14 D138 absent IMU raw line and white line keep conservative display without start veto") {
    for (unsigned condition = 0U; condition < 3U; ++condition) {
        Rig rig; if (condition == 2U) rig.fake.line_lower = 100U;
        P7_REQUIRE(rig.begin(condition != 1U,condition != 0U)); P7_REQUIRE(rig.run(40U));
        CHECK_FALSE(hasR(rig.fake.displayed)); CHECK(rig.fake.displayed.pixels[90U] == 7U);
        if (condition == 0U) { CHECK_FALSE(rig.robot().imu_available); CHECK(rig.robot().match_start_eligible); }
        if (condition == 1U) { CHECK(rig.robot().line_raw_mode); CHECK_FALSE(rig.robot().match_start_eligible); }
        if (condition == 2U) CHECK(rig.robot().line_mask == 15U);
        zero(rig); CHECK(noMotionYet(rig));
    }
}
TEST_CASE("B3 D138 readiness adds no start shortcut and real hold lasts full5100ms") {
    Rig rig; P7_REQUIRE(rig.begin()); P7_REQUIRE(rig.run(40U)); CHECK(noMotionYet(rig));
    P7_REQUIRE(rig.run(30U,START)); CHECK_FALSE(rig.robot().match_start_eligible);
    CHECK_FALSE(hasR(rig.fake.displayed)); rig.fake.button_raw = NONE;
    std::uint32_t released = 0U;
    for (unsigned i = 0U; i < 35U; ++i) {
        P7_REQUIRE(rig.next()); if (rig.robot().lifecycle.gate.start_release)
            released = rig.robot().lifecycle.gate.release_us;
    }
    P7_REQUIRE(released != 0U); bool go = false;
    for (unsigned i = 0U; i < 5200U; ++i) {
        P7_REQUIRE(rig.next()); const auto& tx = rig.owner.transaction().report();
        CHECK_FALSE(tx.robot.match_start_eligible); CHECK_FALSE(hasR(rig.fake.displayed));
        if (tx.decision_us - released < 5100000U) { zero(rig); CHECK(noMotionYet(rig)); }
        if (tx.robot.lifecycle.gate.go) {
            CHECK(tx.decision_us - released >= 5100000U);
            CHECK(tx.decision_us - released < 5101000U); go = true; break;
        }
    }
    CHECK(go); if (MOTORS_ALLOWED == 0) CHECK(noMotionYet(rig));
}
TEST_CASE("B13 D138 service selection and raw calibration hide readiness and threshold extension") {
    Rig rig; P7_REQUIRE(rig.begin()); P7_REQUIRE(rig.run(40U));
    P7_REQUIRE(rig.run(1030U,MODE)); P7_REQUIRE(rig.run(35U));
    P7_REQUIRE(rig.robot().menu.selection.service_menu);
    CHECK_FALSE(rig.robot().match_start_eligible); CHECK_FALSE(hasR(rig.fake.displayed));
    CHECK(rig.fake.displayed.pixels[90U] == 0U); zero(rig);
    P7_REQUIRE(rig.run(30U,MODE)); P7_REQUIRE(rig.run(35U));
    CHECK(rig.robot().menu.selection.service == countdown::Service::QTR_CAL);
    CHECK_FALSE(hasR(rig.fake.displayed)); CHECK(rig.fake.displayed.pixels[90U] == 0U);
    zero(rig); CHECK(noMotionYet(rig));
}
TEST_CASE("B14 D138 stale buttons opponents ADC failure and invalid receipt do not display new readiness") {
    for (unsigned failure = 0U; failure < 4U; ++failure) {
        Rig rig; P7_REQUIRE(rig.begin()); P7_REQUIRE(rig.run(40U));
        if (failure == 0U) rig.fake.freeze_buttons = true;
        if (failure == 1U) rig.fake.opponent_error = 1U;
        if (failure == 2U) rig.fake.adc_failure = true;
        if (failure == 3U) rig.fake.reject_pwm = true;
        const auto initial = rig.fake.displays;
        for (unsigned i = 0U; i < 25U; ++i) {
            const auto before = rig.fake.displays; if (!rig.next()) break;
            const bool pending_adc = failure == 2U && rig.owner.adcInputs().report().fault == power::InputFault::NONE;
            if (!pending_adc && rig.fake.displays > before) CHECK_FALSE(hasR(rig.fake.displayed));
        }
        CHECK(rig.fake.displays >= initial);
        CHECK(rig.robot().contract_faults != 0U || rig.owner.adcInputs().report().fault != power::InputFault::NONE ||
            rig.owner.transaction().report().applied.fault != motors::Fault::NONE);
        if (rig.robot().outputs.ui_state == core::State::STOPPED) CHECK_FALSE(rig.robot().match_start_eligible);
        CHECK_FALSE(rig.fake.enabled); for (auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
        CHECK(noMotionYet(rig));
    }
}
TEST_CASE("B13 D138 actual local service-reset lifetime cannot advertise match readiness") {
    Rig rig; P7_REQUIRE(rig.begin(true,true,true)); P7_REQUIRE(rig.run(40U));
    rig.fake.button_raw = BOTH; bool stopped = false;
    for (unsigned i = 0U; i < 1100U; ++i) {
        P7_REQUIRE(rig.next()); if (rig.robot().outputs.ui_state == core::State::STOPPED) { stopped = true; break; }
    }
    P7_REQUIRE(stopped); P7_REQUIRE(rig.next()); P7_REQUIRE(rig.run(30U)); P7_REQUIRE(rig.run(1040U,MODE));
    rig.fake.button_raw = NONE; bool pending = false;
    for (unsigned i = 0U; i < 40U; ++i) {
        P7_REQUIRE(rig.next()); if (rig.owner.report().service_reset_pending) { pending = true; break; }
    }
    P7_REQUIRE(pending); P7_REQUIRE(rig.next()); P7_REQUIRE(rig.owner.report().service_only);
    P7_REQUIRE(rig.run(40U));
    CHECK(rig.robot().outputs.ui_state == core::State::IDLE);
    CHECK_FALSE(hasR(rig.fake.displayed)); zero(rig); CHECK(noMotionYet(rig));
}
#endif

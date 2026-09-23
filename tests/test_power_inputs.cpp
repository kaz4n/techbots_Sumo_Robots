// Tests B6 D093 input ownership and bounded battery retention from its contract.
// Preserves source clocks, shared failures and the existing Robot motor boundary.
// Independent fake/native variants and normal/enabled host suites exercise this API.
#include "fixtures/power_inputs_fixture.h"
#include "fixtures/tick_timing_fixture.h"
#include "core/governor.h"
#include <cmath>
#include <limits>
#include <type_traits>
using namespace power_inputs_test;
using power::InputFault;
using power::InputOperation;
using power::Shutdown;
using power::Status;

TEST_CASE("B6 D093 construction destruction prebegin methods and copied port are inert") {
    static_assert(!std::is_copy_constructible<power::InputOwner>::value);
    static_assert(!std::is_copy_assignable<power::InputOwner>::value);
    Fake fake;
    { auto port = fake.port(); power::InputOwner owner(port); port.readA0 = nullptr;
      CHECK_FALSE(owner.readBatteryIfDue(true).attempted);
      CHECK_FALSE(owner.readButtons(true).attempted);
      CHECK_FALSE(owner.observe(0x80000000U).ready);
      fsm::RobotInput input; input.t_us = 0x90000000U; input.vbat_v = 12.0F; input.vbat_valid = true;
      CHECK_FALSE(owner.applyBattery(input)); CHECK(input.vbat_v == 0.0F);
      CHECK_FALSE(input.vbat_valid); CHECK(fake.callbacks() == 0U);
      CHECK(owner.begin()); CHECK(owner.readBatteryIfDue(true).accepted);
      const auto count = fake.callbacks(); CHECK_FALSE(owner.begin()); CHECK(fake.callbacks() == count);
    }
    CHECK(fake.setups == 1U); CHECK(fake.batteries == 1U); CHECK(fake.buttons == 0U);
}

TEST_CASE("B6 D093 healthy setup requires exact result and only setup bracket callbacks") {
    Rig rig; rig.fake.setup_elapsed = 20U; rig.begin();
    const auto report = rig.owner.report();
    CHECK(report.attempted); CHECK(report.ready); CHECK(report.battery_due);
    CHECK_FALSE(report.battery_available); CHECK(report.battery_generation == 0U);
    CHECK(report.setup.status == Status::OK); CHECK(report.setup.ready);
    CHECK(report.observed_us == 120U); CHECK(rig.fake.clocks == 2U);
    CHECK(rig.fake.setups == 1U); CHECK(rig.fake.batteries == 0U); CHECK(rig.fake.buttons == 0U);
}

TEST_CASE("B6 D093 every required null callback fails admission before any callback") {
    for (unsigned field = 0; field < 4U; ++field) {
        Fake fake; auto port = fake.port();
        if (field == 0U) port.beginWithButtons = nullptr;
        if (field == 1U) port.readA0 = nullptr;
        if (field == 2U) port.readA1 = nullptr;
        if (field == 3U) port.clockUs = nullptr;
        power::InputOwner owner(port); CHECK_FALSE(owner.begin());
        CHECK(owner.report().fault == InputFault::PORT); CHECK(owner.report().attempted);
        CHECK_FALSE(owner.begin()); CHECK_FALSE(owner.readButtons(true).attempted);
        CHECK(fake.callbacks() == 0U);
    }
}

TEST_CASE("B6 D093 stateless callbacks may have null context and identical source clocks") {
    power::InputPort port;
    port.beginWithButtons = [](void*) { return power::InitResult{Status::OK, Shutdown::NOT_ATTEMPTED, true}; };
    port.readA0 = [](void*) { return power::Sample{Status::OK, Shutdown::NOT_ATTEMPTED, 0U, 0U, 0U, 0.0F, true}; };
    port.readA1 = [](void*) { return power::ButtonSample{Status::OK, Shutdown::NOT_ATTEMPTED, 0U, 0U, 0U, 1U, true}; };
    port.clockUs = [](void*) -> std::uint32_t { return 0U; };
    power::InputOwner owner(port); CHECK(owner.begin()); CHECK(owner.readBatteryIfDue(true).accepted);
    CHECK(owner.readButtons(true).accepted); CHECK(owner.report().battery_age_us == 0U);
}

TEST_CASE("B6 D093 first setup known errors and malformed results have distinct faults") {
    for (unsigned variant = 0; variant < 7U; ++variant) {
        Rig rig;
        if (variant == 0U) rig.fake.setup_result = {Status::OWNERSHIP, Shutdown::UNCONFIRMED, false};
        if (variant == 1U) rig.fake.setup_result = {Status::ALREADY_STARTED, Shutdown::NOT_ATTEMPTED, true};
        if (variant == 2U) rig.fake.setup_result.ready = false;
        if (variant == 3U) rig.fake.setup_result.shutdown = Shutdown::DISABLED;
        if (variant == 4U) rig.fake.setup_result.status = static_cast<Status>(255U);
        if (variant == 5U) rig.fake.setup_result.shutdown = static_cast<Shutdown>(255U);
        if (variant == 6U) { rig.fake.setup_result = {Status::READBACK, Shutdown::DISABLED, false}; rig.fake.setup_elapsed = 0x80000000U; }
        CHECK_FALSE(rig.owner.begin());
        blocked(rig, variant < 2U || variant == 6U ? InputFault::SETUP : InputFault::SOURCE, InputOperation::SETUP);
        CHECK(rig.owner.report().setup.status == rig.fake.setup_result.status);
        CHECK(rig.owner.report().first_status == rig.fake.setup_result.status);
        CHECK(rig.owner.report().first_shutdown == rig.fake.setup_result.shutdown);
    }
}

TEST_CASE("B6 D093 setup clock equality natural wrap and half range obey common clock") {
    for (auto elapsed : {0U, 1U, 0x7FFFFFFFU, 0x80000000U, 0x80000001U, 0xFFFFFFFFU}) {
        Rig rig; rig.fake.now = 0xFFFFFFF0U; rig.fake.setup_elapsed = elapsed;
        CHECK(rig.owner.begin() == (elapsed < 0x80000000U));
        if (elapsed >= 0x80000000U) blocked(rig, InputFault::CLOCK, InputOperation::SETUP);
        else CHECK(rig.owner.report().observed_us == 0xFFFFFFF0U + elapsed);
    }
}

TEST_CASE("B6 D093 first due grant refusal and period boundary never perform catchup") {
    Rig rig; rig.begin();
    CHECK_FALSE(rig.owner.readBatteryIfDue(false).attempted);
    CHECK(rig.owner.report().battery_refused == 1U); CHECK(rig.fake.batteries == 0U);
    const auto first = rig.owner.readBatteryIfDue(true); CHECK(first.accepted);
    CHECK(rig.owner.report().battery_age_us == 5U);
    for (auto age : {9998U, 9999U, 10000U, 10001U, 50000U}) {
        rig.fake.now = first.sample.started_us + age;
        const auto before = rig.fake.batteries;
        CHECK_FALSE(rig.owner.readBatteryIfDue(false).attempted);
        CHECK(rig.fake.batteries == before);
        CHECK(rig.owner.report().battery_due == (age >= 10000U));
    }
    CHECK(rig.owner.report().battery_refused == 4U);
    CHECK(rig.owner.readBatteryIfDue(true).accepted);
    CHECK(rig.fake.batteries == 2U); CHECK(rig.owner.report().battery_generation == 2U);
    CHECK_FALSE(rig.owner.readBatteryIfDue(true).attempted); CHECK(rig.fake.batteries == 2U);
}

TEST_CASE("B6 D093 start age19999 is available and exact20000 expires without owner fault") {
    Rig rig; const auto first = rig.prime();
    for (auto age : {19999U, 20000U, 20001U}) {
        const auto report = rig.owner.observe(first.sample.started_us + age);
        CHECK(report.battery_age_us == age); CHECK(report.battery_available == (age < 20000U));
        CHECK(report.battery_due); CHECK(report.ready); CHECK(report.fault == InputFault::NONE);
        same(report.battery, first.sample);
    }
    const auto before = rig.fake.callbacks(); rig.fake.now += 100000U;
    CHECK(rig.owner.report().battery_age_us == 20001U); CHECK(rig.fake.callbacks() == before);
}

TEST_CASE("B6 D093 genuine equal value replaces expired cache old interval replay faults") {
    for (bool replay : {false, true}) {
        Rig rig; const auto first = rig.prime();
        rig.fake.now = first.sample.started_us + 30000U;
        CHECK_FALSE(rig.owner.observe(rig.fake.now).battery_available);
        rig.fake.auto_battery = !replay;
        const auto next = rig.owner.readBatteryIfDue(true); CHECK(next.attempted);
        CHECK(next.accepted == !replay); CHECK(next.sample.raw == first.sample.raw);
        CHECK(next.sample.voltage_v == first.sample.voltage_v);
        if (replay) { blocked(rig, InputFault::SOURCE, InputOperation::BATTERY); same(next.sample, first.sample); }
        else { CHECK(rig.owner.report().battery_age_us == 5U); CHECK(rig.owner.report().battery_generation == 2U); }
    }
}

TEST_CASE("B6 D093 quantized equal clocks allow genuine A1 calls and do not refresh A0") {
    Rig rig; rig.fake.duration = 0U; rig.fake.tail = 0U; rig.prime();
    const auto first = rig.owner.readButtons(true), second = rig.owner.readButtons(true);
    CHECK(first.accepted); CHECK(second.accepted); CHECK(first.sample.sequence == 1U);
    CHECK(second.sample.sequence == 2U); CHECK(first.sample.started_us == second.sample.started_us);
    CHECK(rig.owner.report().button_attempts == 2U); CHECK(rig.owner.report().battery_generation == 1U);
    CHECK(rig.owner.report().battery_age_us == 0U); CHECK_FALSE(rig.owner.readBatteryIfDue(true).attempted);
}

TEST_CASE("B6 D093 successful raw endpoints retain exact native float scaling") {
    for (std::uint16_t raw : {0U, 1U, 8191U, 8192U, 16383U}) {
        Rig rig; rig.fake.raw = raw; const auto read = rig.prime();
        CHECK(read.sample.raw == raw); CHECK(read.sample.voltage_v == voltage(raw));
        CHECK(rig.owner.report().battery_available); same(rig.owner.report().battery, read.sample);
    }
}

TEST_CASE("B6 D093 malformed successful battery shape never becomes retained evidence") {
    for (unsigned variant = 0; variant < 9U; ++variant) {
        Rig rig; rig.begin(); rig.fake.auto_battery = false;
        rig.fake.battery = {Status::OK, Shutdown::NOT_ATTEMPTED, 8192U, 100U, 103U, voltage(8192U), true};
        auto& sample = rig.fake.battery;
        if (variant == 0U) sample.raw = 16384U;
        if (variant == 1U) sample.voltage_v = std::nextafter(sample.voltage_v, 100.0F);
        if (variant == 2U) sample.voltage_v = std::numeric_limits<float>::quiet_NaN();
        if (variant == 3U) sample.voltage_v = std::numeric_limits<float>::infinity();
        if (variant == 4U) sample.valid = false;
        if (variant == 5U) sample.shutdown = Shutdown::DISABLED;
        if (variant == 6U) sample.status = static_cast<Status>(255U);
        if (variant == 7U) sample.shutdown = static_cast<Shutdown>(255U);
        if (variant == 8U) sample.status = Status::INVALID_DATA;
        const auto read = rig.owner.readBatteryIfDue(true);
        CHECK(read.attempted); CHECK_FALSE(read.accepted); same(read.sample, sample);
        CHECK(rig.owner.report().battery_generation == 0U);
        blocked(rig, InputFault::SOURCE, InputOperation::BATTERY);
    }
}

TEST_CASE("B6 D093 A0 and A1 interval99 succeeds exact100 fails including brackets") {
    for (bool buttons : {false, true}) for (auto duration : {0U, 99U, 100U, 101U}) {
        Rig rig; rig.begin(); rig.fake.duration = duration; rig.fake.tail = 0U;
        const bool accepted = buttons ? rig.owner.readButtons(true).accepted : rig.owner.readBatteryIfDue(true).accepted;
        CHECK(accepted == (duration < 100U));
        if (duration >= 100U) blocked(rig, InputFault::SOURCE, buttons ? InputOperation::BUTTONS : InputOperation::BATTERY);
    }
}

TEST_CASE("B6 D093 sample start completion and return boundaries share the actual call anchor") {
    for (bool buttons : {false, true}) for (unsigned variant = 0; variant < 5U; ++variant) {
        Rig rig; rig.begin(); rig.fake.auto_battery = false; rig.fake.auto_buttons = false;
        std::uint32_t start = 100U, complete = 103U;
        if (variant == 0U) start = 99U;
        if (variant == 1U) complete = 99U;
        if (variant == 2U) start = 104U;
        if (variant == 3U) complete = 106U;
        if (variant == 4U) { start += 0x80000000U; complete += 0x80000000U; }
        rig.fake.battery = {Status::OK, Shutdown::NOT_ATTEMPTED, 0U, start, complete, 0.0F, true};
        rig.fake.button = {Status::OK, Shutdown::NOT_ATTEMPTED, 0U, start, complete, 1U, true};
        const bool accepted = buttons ? rig.owner.readButtons(true).accepted : rig.owner.readBatteryIfDue(true).accepted;
        CHECK_FALSE(accepted);
        blocked(rig, InputFault::SOURCE, buttons ? InputOperation::BUTTONS : InputOperation::BATTERY);
    }
}

TEST_CASE("B6 D093 common clock rejects reversal half range and post success discontinuity") {
    for (auto delta : {0x7FFFFFFFU, 0x80000000U, 0x80000001U, 0xFFFFFFFFU}) {
        Rig rig; rig.prime(); const auto last = rig.fake.now;
        const auto report = rig.owner.observe(last + delta);
        CHECK(report.fault == (delta < 0x80000000U ? InputFault::NONE : InputFault::CLOCK));
        if (delta >= 0x80000000U) blocked(rig, InputFault::CLOCK, InputOperation::OBSERVE);
    }
    for (bool buttons : {false, true}) {
        Rig rig; rig.begin(); rig.fake.tail = 0x80000000U;
        const bool accepted = buttons ? rig.owner.readButtons(true).accepted : rig.owner.readBatteryIfDue(true).accepted;
        CHECK_FALSE(accepted);
        blocked(rig, InputFault::CLOCK, buttons ? InputOperation::BUTTONS : InputOperation::BATTERY);
        CHECK(rig.owner.report().first_status == Status::OK);
    }
}

TEST_CASE("B6 D093 observed full wraps saturate age without resurrection and new read can replace") {
    Rig rig; rig.fake.now = 0xFFFFFFFEU; const auto first = rig.prime();
    CHECK(first.sample.completed_us == 1U); CHECK(rig.owner.report().battery_age_us == 5U);
    for (unsigned i = 0; i < 8U; ++i) {
        rig.fake.now += 0x40000000U;
        const auto report = rig.owner.observe(rig.fake.now);
        CHECK_FALSE(report.battery_available); CHECK(report.battery_due); CHECK(report.fault == InputFault::NONE);
    }
    CHECK(rig.owner.report().battery_age_us == 0xFFFFFFFFU);
    rig.fake.now += 0x7FFFFFFFU; rig.owner.observe(rig.fake.now);
    rig.fake.now += 0x7FFFFFFCU; rig.owner.observe(rig.fake.now);
    CHECK(rig.fake.now == first.sample.started_us);
    CHECK(rig.owner.readBatteryIfDue(true).accepted);
    CHECK(rig.owner.report().battery_generation == 2U); CHECK(rig.owner.report().battery_age_us == 5U);
    same(rig.owner.report().battery, first.sample);
}

TEST_CASE("B6 D093 native A0 or A1 failure beats postclock errors and invalidates young cache") {
    for (bool buttons : {false, true}) for (auto shutdown : {Shutdown::NOT_ATTEMPTED, Shutdown::DISABLED, Shutdown::UNCONFIRMED}) {
        Rig rig; const auto first = rig.prime(); rig.fake.now = first.sample.started_us + 10000U;
        rig.fake.auto_battery = false; rig.fake.auto_buttons = false; rig.fake.tail = 0x80000000U;
        rig.fake.battery = {Status::CONVERSION_TIMEOUT, shutdown, 0U, rig.fake.now, rig.fake.now+100U, 0.0F, false};
        rig.fake.button = {Status::READBACK, shutdown, 0U, rig.fake.now, rig.fake.now+100U, 0U, false};
        if (buttons) { const auto read = rig.owner.readButtons(true); CHECK(read.attempted); CHECK_FALSE(read.accepted); CHECK(read.sample.status == Status::READBACK); }
        else { const auto read = rig.owner.readBatteryIfDue(true); CHECK(read.attempted); CHECK_FALSE(read.accepted); CHECK(read.sample.status == Status::CONVERSION_TIMEOUT); }
        blocked(rig, InputFault::ADC, buttons ? InputOperation::BUTTONS : InputOperation::BATTERY);
        CHECK(rig.owner.report().first_status == (buttons ? Status::READBACK : Status::CONVERSION_TIMEOUT));
        CHECK(rig.owner.report().first_shutdown == shutdown); same(rig.owner.report().battery, first.sample);
    }
}

TEST_CASE("B6 D093 every known native nonOK status remains specific ADC evidence") {
    for (unsigned code = 1U; code <= 14U; ++code) for (bool buttons : {false, true}) {
        Rig rig; rig.begin(); rig.fake.auto_battery = false; rig.fake.auto_buttons = false;
        const auto status = static_cast<Status>(code);
        rig.fake.battery = {status, Shutdown::UNCONFIRMED, 0U, 100U, 103U, 0.0F, false};
        rig.fake.button = {status, Shutdown::UNCONFIRMED, 0U, 100U, 103U, 0U, false};
        const bool accepted = buttons ? rig.owner.readButtons(true).accepted : rig.owner.readBatteryIfDue(true).accepted;
        CHECK_FALSE(accepted);
        blocked(rig, InputFault::ADC, buttons ? InputOperation::BUTTONS : InputOperation::BATTERY);
        CHECK(rig.owner.report().first_status == status);
    }
}

TEST_CASE("B6 D093 A1 grant refusal and success advance battery age without refreshing source") {
    Rig rig; const auto first = rig.prime(); rig.fake.now += 1000U;
    CHECK_FALSE(rig.owner.readButtons(false).attempted); CHECK(rig.owner.report().button_refused == 1U);
    CHECK(rig.fake.buttons == 0U); CHECK(rig.owner.report().battery_age_us == 1005U);
    CHECK(rig.owner.readButtons(true).accepted); CHECK(rig.owner.report().button_attempts == 1U);
    CHECK(rig.owner.report().battery_age_us == 1010U); CHECK(rig.owner.report().battery_generation == 1U);
    same(rig.owner.report().battery, first.sample); CHECK(rig.fake.batteries == 1U);
}

TEST_CASE("B6 D093 first A1 sequence is1 and later replay skip or malformed shape faults") {
    for (unsigned variant = 0; variant < 8U; ++variant) {
        Rig rig; rig.begin();
        if (variant < 2U) CHECK(rig.owner.readButtons(true).accepted);
        rig.fake.auto_buttons = false;
        rig.fake.button = {Status::OK, Shutdown::NOT_ATTEMPTED, 16383U, rig.fake.now, rig.fake.now+3U, 1U, true};
        if (variant == 1U) rig.fake.button.sequence = 3U;
        if (variant == 2U) rig.fake.button.sequence = 0U;
        if (variant == 3U) rig.fake.button.raw = 16384U;
        if (variant == 4U) rig.fake.button.valid = false;
        if (variant == 5U) rig.fake.button.shutdown = Shutdown::DISABLED;
        if (variant == 6U) rig.fake.button.status = static_cast<Status>(255U);
        if (variant == 7U) rig.fake.button.status = Status::OVERRUN;
        const auto read = rig.owner.readButtons(true); CHECK(read.attempted); CHECK_FALSE(read.accepted);
        CHECK(read.sample.sequence == rig.fake.button.sequence); CHECK(read.sample.raw == rig.fake.button.raw);
        blocked(rig, InputFault::SOURCE, InputOperation::BUTTONS);
    }
}

TEST_CASE("B6 D093 battery projection changes only voltage validity and preserves caller startup") {
    Rig rig; rig.begin(); fsm::RobotInput input;
    input.t_us = rig.fake.now; input.initialization_complete = true; input.raw_heading_deg = 123.0F;
    input.previous.token = 12345U; input.timing = {true, true, 77U}; input.buttons.raw = 7654U;
    CHECK_FALSE(rig.owner.applyBattery(input)); CHECK(input.vbat_v == 0.0F); CHECK_FALSE(input.vbat_valid);
    CHECK(input.initialization_complete); CHECK(rig.owner.readBatteryIfDue(true).accepted);
    input.t_us = rig.fake.now; CHECK(rig.owner.applyBattery(input)); CHECK(input.vbat_v == voltage(8192U));
    CHECK(input.raw_heading_deg == 123.0F); CHECK(input.previous.token == 12345U);
    CHECK(input.timing.started_us == 77U); CHECK(input.timing.explicit_start); CHECK(input.buttons.raw == 7654U);
    CHECK(input.initialization_complete); CHECK(input.t_us == rig.fake.now);
}

TEST_CASE("B6 D093 button projection preserves other inputs and rejects contradictory read flags") {
    Rig rig; rig.begin(); fsm::RobotInput input; input.t_us = rig.fake.now;
    input.vbat_v = 12.0F; input.vbat_valid = true; input.initialization_complete = true;
    CHECK(rig.owner.applyButtons(input, {}) == ui::ButtonQualification::ABSENT);
    CHECK(input.buttons.explicit_values); CHECK(input.buttons.presence == core::ButtonPresence::ABSENT);
    auto read = rig.owner.readButtons(true); input.t_us = rig.fake.now;
    auto expected = input; const auto qualification = ui::applyButtons(expected, read.sample);
    CHECK(rig.owner.applyButtons(input, read) == qualification);
    CHECK(input.buttons.raw == expected.buttons.raw); CHECK(input.buttons.sequence == expected.buttons.sequence);
    CHECK(input.buttons.started_us == expected.buttons.started_us); CHECK(input.buttons.contract_valid == expected.buttons.contract_valid);
    for (unsigned variant = 0; variant < 2U; ++variant) {
        read.attempted = variant == 0U; read.accepted = variant != 0U;
        CHECK(rig.owner.applyButtons(input, read) == ui::ButtonQualification::INVALID);
        CHECK_FALSE(input.buttons.contract_valid); CHECK(input.buttons.presence == core::ButtonPresence::INVALID);
    }
    CHECK(input.vbat_v == 12.0F); CHECK(input.vbat_valid); CHECK(input.initialization_complete);
    CHECK(input.t_us == rig.fake.now); CHECK(rig.owner.report().fault == InputFault::NONE);
}

TEST_CASE("B6 D093 held voltage drives unchanged perdecision filter and final cap slew") {
    Rig rig; rig.fake.duration = 0U; rig.fake.tail = 0U; rig.fake.now = 0U; rig.fake.raw = 8000U; rig.prime();
    governor::Governor governor; governor::Request request;
    request.profile = governor::Profile::OPENER; request.inhibited = false; request.duty_l = 1.0F; request.duty_r = 1.0F;
    request.vbat_v = voltage(8000U); auto last = governor.step(0U, request);
    rig.fake.raw = 11000U; const double initial = voltage(8000U), held = voltage(11000U);
    for (unsigned tick = 1U; tick <= 28U; ++tick) {
        rig.fake.now = tick * 1000U;
        if (tick == 10U) CHECK(rig.owner.readBatteryIfDue(true).accepted);
        fsm::RobotInput input; input.t_us = rig.fake.now; CHECK(rig.owner.applyBattery(input));
        request.vbat_v = input.vbat_v; const auto result = governor.step(input.t_us, request);
        const double expected = tick < 10U ? initial : held + (initial-held) * std::pow(1000.0/1001.0, tick-9U);
        CHECK(result.filtered_vbat_v == doctest::Approx(expected).epsilon(0.00001));
        CHECK(result.duty_l <= config::OPENER_DUTY_MAX); CHECK(result.duty_r <= config::OPENER_DUTY_MAX);
        CHECK(result.duty_l - last.duty_l <= config::SLEW_DUTY_PER_MS + 0.00001F);
        CHECK(result.valid); last = result;
    }
    CHECK(rig.fake.batteries == 2U);
}

TEST_CASE("B6 D093 actual Robot MotorGate inhibit on expired or shared failed battery and stay latched") {
    for (bool adc_failure : {false, true}) {
        timing_test::Rig robot(true, true); const auto go = robot.go();
        Rig rig; rig.fake.now = go; rig.prime();
        for (std::uint32_t elapsed = 1000U; elapsed <= 19000U; elapsed += 1000U) {
            auto input = robot.at(go + elapsed, go + elapsed); CHECK(rig.owner.applyBattery(input));
            CHECK(robot.submit(input).contract_faults == 0U);
        }
        if (adc_failure) {
            rig.fake.now = go + 19001U; rig.fake.auto_buttons = false;
            rig.fake.button = {Status::OVERRUN, Shutdown::DISABLED, 0U, rig.fake.now, rig.fake.now+3U, 0U, false};
            CHECK_FALSE(rig.owner.readButtons(true).accepted);
        }
        auto input = robot.at(go + 20000U, go + 20000U); CHECK_FALSE(rig.owner.applyBattery(input));
        const auto stopped = robot.submit(input);
        CHECK((stopped.contract_faults & fsm::INVALID_CONTEXT) != 0U);
        CHECK(stopped.outputs.ui_state == core::State::STOPPED); CHECK_FALSE(robot.port.enabled);
        CHECK_FALSE(robot.previous.motors_enabled); CHECK(robot.previous.duty_l == 0.0F); CHECK(robot.previous.duty_r == 0.0F);
        rig.fake.now = go + 21000U;
        if (!adc_failure) CHECK(rig.owner.readBatteryIfDue(true).accepted);
        input = robot.at(go + 22000U, go + 22000U); CHECK(rig.owner.applyBattery(input) == !adc_failure);
        CHECK(robot.submit(input).outputs.ui_state == core::State::STOPPED); CHECK_FALSE(robot.port.enabled);
        if (adc_failure) { robot.robot.reset(); input = robot.at(go+23000U,go+23000U); CHECK_FALSE(rig.owner.applyBattery(input)); CHECK(robot.submit(input).outputs.ui_state == core::State::STOPPED); }
    }
}

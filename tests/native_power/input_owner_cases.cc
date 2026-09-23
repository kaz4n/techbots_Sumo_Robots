// Exercises actual D093 Reader binding and input owner in isolated native boots.
// Channel identity and shared native failures cannot be supplied by cached values.
// Opaque production compilation uses the established register and allocation fixture.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power_inputs.h"
namespace {
unsigned io() { return fixture::hw.accesses + fixture::hw.micros_calls + fixture::hw.ready_reads + fixture::hw.clock_on + fixture::hw.clock_rate; }
}
TEST_CASE("B6 D093 actual native factory owner construction and prebegin operations do no IO") {
    fixture::isolated([] {
        fixture::reset(); unsigned before = 0;
        { power::Reader reader; const auto port = power::readerInputPort(reader);
          power::InputOwner owner(port); CHECK(io() == 0U);
          CHECK_FALSE(owner.readBatteryIfDue(true).attempted);
          CHECK_FALSE(owner.readButtons(true).attempted); owner.observe(123U);
          CHECK(io() == 0U); CHECK(owner.begin()); CHECK(fixture::hw.start_count == 0U);
          CHECK(fixture::hw.cal_count == 1U); CHECK(fixture::hw.enable_count == 1U);
          CHECK(ADC1->PCSEL.value == 0x600U); CHECK(ADC1->SMPR2.value == 7U);
          before = io(); CHECK_FALSE(owner.begin()); CHECK(io() == before);
        }
        CHECK(io() == before);
    });
}
TEST_CASE("B6 D093 actual native pair channel values and timing feed one retained battery") {
    fixture::isolated([] {
        fixture::reset(); fixture::hw.samples_by_rank = true;
        fixture::hw.battery_sample = 9000U; fixture::hw.button_sample = 321U;
        power::Reader reader; power::InputOwner owner(power::readerInputPort(reader));
        CHECK(owner.begin()); const auto first = owner.readBatteryIfDue(true);
        CHECK(first.accepted); CHECK(first.sample.raw == 9000U); CHECK(ADC1->SQR1.value == (9U<<6));
        CHECK(owner.report().battery_age_us >= first.sample.completed_us-first.sample.started_us);
        const auto button = owner.readButtons(true);
        CHECK(button.accepted); CHECK(button.sample.raw == 321U); CHECK(button.sample.sequence == 1U);
        CHECK(ADC1->SQR1.value == (10U<<6)); CHECK(owner.report().battery_generation == 1U);
        CHECK(owner.report().battery.raw == 9000U); CHECK_FALSE(owner.readBatteryIfDue(true).attempted);
        fixture::hw.now = first.sample.started_us + 10000U;
        const auto second = owner.readBatteryIfDue(true); CHECK(second.accepted);
        CHECK(second.sample.raw == 9000U); CHECK(second.sample.started_us != first.sample.started_us);
        CHECK(owner.report().battery_generation == 2U); CHECK(ADC1->SQR1.value == (9U<<6));
        CHECK(fixture::hw.start_count == 3U); CHECK(fixture::hw.data_reads == 3U);
        CHECK(fixture::hw.cal_count == 1U); CHECK(fixture::hw.command_errors == 0U);
    });
}
TEST_CASE("B6 D093 actual A1 native fault invalidates young A0 and suppresses every callback") {
    fixture::isolated([] {
        fixture::reset(); fixture::hw.samples_by_rank = true;
        power::Reader reader; power::InputOwner owner(power::readerInputPort(reader));
        CHECK(owner.begin()); CHECK(owner.readBatteryIfDue(true).accepted);
        fixture::hw.button_sample = 0x10000U;
        const auto failed = owner.readButtons(true);
        CHECK(failed.attempted); CHECK_FALSE(failed.accepted);
        CHECK(failed.sample.status == power::Status::INVALID_DATA);
        CHECK(failed.sample.shutdown == power::Shutdown::DISABLED);
        CHECK(owner.report().fault == power::InputFault::ADC);
        CHECK(owner.report().fault_operation == power::InputOperation::BUTTONS);
        CHECK_FALSE(owner.report().battery_available); const auto before = io();
        CHECK_FALSE(owner.readBatteryIfDue(true).attempted); CHECK_FALSE(owner.readButtons(true).attempted);
        CHECK_FALSE(owner.begin()); owner.observe(fixture::hw.now + 1000U);
        fsm::RobotInput input; input.t_us = fixture::hw.now + 2000U;
        CHECK_FALSE(owner.applyBattery(input)); CHECK(io() == before);
        CHECK(owner.report().first_status == power::Status::INVALID_DATA);
        CHECK(owner.report().battery.valid); CHECK(owner.report().battery_generation == 1U);
    });
}
TEST_CASE("B6 D093 actual native timeout shutdown diagnostics survive owner projection") {
    for (bool disabled : {false, true}) fixture::isolated([=] {
        fixture::reset(); power::Reader reader; power::InputOwner owner(power::readerInputPort(reader));
        CHECK(owner.begin()); fixture::hw.conversion_after = -1;
        if (!disabled) fixture::hw.stop_after = -1;
        const auto failed = owner.readBatteryIfDue(true);
        CHECK(failed.attempted); CHECK_FALSE(failed.accepted);
        CHECK(failed.sample.status == power::Status::CONVERSION_TIMEOUT);
        CHECK(failed.sample.shutdown == (disabled ? power::Shutdown::DISABLED : power::Shutdown::UNCONFIRMED));
        CHECK(owner.report().first_status == failed.sample.status);
        CHECK(owner.report().first_shutdown == failed.sample.shutdown);
        const auto before = io(); CHECK_FALSE(owner.readButtons(true).attempted); CHECK(io() == before);
        CHECK(fixture::hw.command_errors == 0U);
    });
}
TEST_CASE("B6 D093 actual native setup acquisition projection and destruction allocate nothing") {
    fixture::isolated([] {
        fixture::reset(); bool good = true; unsigned allocations = 99U;
        { fixture::AllocationGuard guard; power::Reader reader;
          power::InputOwner owner(power::readerInputPort(reader)); good &= owner.begin();
          for (unsigned index = 0; index < 100U; ++index) {
              fixture::hw.now += 10000U;
              good &= owner.readBatteryIfDue(true).accepted;
              good &= owner.readButtons(true).accepted;
              fsm::RobotInput input; input.t_us = fixture::hw.now;
              good &= owner.applyBattery(input);
          }
          allocations = fixture::hw.allocations;
        }
        CHECK(good); CHECK(allocations == 0U); CHECK(fixture::hw.start_count == 200U);
        CHECK(fixture::hw.cal_count == 1U); CHECK(fixture::hw.command_errors == 0U);
    });
}

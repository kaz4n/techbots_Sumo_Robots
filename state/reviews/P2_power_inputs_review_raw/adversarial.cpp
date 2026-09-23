// Exercises malformed source metadata and lifetime boundaries independently.
// Cross-products expose acceptance or priority gaps without implementation helpers.
// Compiled against the actual D093 owner and UI in normal and sanitized runs.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest.h>
#include "hal/power_inputs.h"
#include "config.h"
#include <cstdint>
#include <limits>

namespace {
using power::InputFault;
struct Port {
    std::uint32_t now = 100U, setup_after = 110U, read_after = 1200U;
    unsigned clocks = 0U, setups = 0U, batteries = 0U, buttons = 0U;
    power::InitResult init{power::Status::OK, power::Shutdown::NOT_ATTEMPTED, true};
    power::Sample battery;
    power::ButtonSample button;
    static std::uint32_t clock(void* p) { auto& x=*static_cast<Port*>(p); ++x.clocks; return x.now; }
    static power::InitResult begin(void* p) { auto& x=*static_cast<Port*>(p); ++x.setups; x.now=x.setup_after; return x.init; }
    static power::Sample a0(void* p) { auto& x=*static_cast<Port*>(p); ++x.batteries; x.now=x.read_after; return x.battery; }
    static power::ButtonSample a1(void* p) { auto& x=*static_cast<Port*>(p); ++x.buttons; x.now=x.read_after; return x.button; }
    power::InputPort port() { return {this,begin,a0,a1,clock}; }
    void fresh(std::uint32_t before, std::uint32_t start, std::uint32_t complete, std::uint32_t after) {
        now=before; read_after=after;
        battery={power::Status::OK,power::Shutdown::NOT_ATTEMPTED,12000U,start,complete,
            static_cast<float>(12000U)/16383.0F*config::VBAT_ADC_REFERENCE_V*config::VBAT_DIVIDER_RATIO,true};
        button={power::Status::OK,power::Shutdown::NOT_ATTEMPTED,12000U,start,complete,1U,true};
    }
    unsigned callbacks() const { return clocks+setups+batteries+buttons; }
};
InputFault sourceFault(unsigned status,unsigned shutdown,bool valid) {
    if(status>14U || shutdown>2U || valid!=(status==0U)) return InputFault::SOURCE;
    if(status!=0U) return InputFault::ADC;
    return shutdown==0U ? InputFault::NONE : InputFault::SOURCE;
}
void frozen(power::InputOwner& owner,Port& port) {
    const auto before=owner.report(); const auto calls=port.callbacks();
    CHECK_FALSE(owner.begin()); CHECK_FALSE(owner.readBatteryIfDue(true).attempted);
    CHECK_FALSE(owner.readButtons(true).attempted); owner.observe(0xEFFFFFFFU);
    fsm::RobotInput input; input.t_us=0x70000000U; input.vbat_valid=true; input.vbat_v=12.0F;
    CHECK_FALSE(owner.applyBattery(input)); CHECK(input.vbat_v==0.0F);
    CHECK(owner.applyButtons(input,{})==ui::ButtonQualification::INVALID);
    CHECK(input.buttons.presence==core::ButtonPresence::INVALID);
    CHECK_FALSE(input.buttons.contract_valid); CHECK(port.callbacks()==calls);
    CHECK(owner.report().fault==before.fault); CHECK(owner.report().first_status==before.first_status);
    CHECK(owner.report().first_shutdown==before.first_shutdown);
    CHECK(owner.report().fault_operation==before.fault_operation);
}
}

TEST_CASE("D093 reviewer exhaustive native-result classification and clock priority") {
    for(unsigned channel=0;channel<2;++channel) for(unsigned status=0;status<17;++status)
    for(unsigned shutdown=0;shutdown<4;++shutdown) for(bool valid:{false,true})
    for(bool reverse:{false,true}) {
        Port p; power::InputOwner owner(p.port()); REQUIRE(owner.begin());
        p.fresh(1000U,1001U,1002U,reverse?999U:1003U);
        p.battery.status=p.button.status=static_cast<power::Status>(status);
        p.battery.shutdown=p.button.shutdown=static_cast<power::Shutdown>(shutdown);
        p.battery.valid=p.button.valid=valid;
        auto expected=sourceFault(status,shutdown,valid);
        if(expected==InputFault::NONE && reverse) expected=InputFault::CLOCK;
        bool accepted;
        if(channel==0U) { auto read=owner.readBatteryIfDue(true); CHECK(read.attempted); accepted=read.accepted; CHECK(read.sample.status==p.battery.status); }
        else { auto read=owner.readButtons(true); CHECK(read.attempted); accepted=read.accepted; CHECK(read.sample.status==p.button.status); }
        CHECK(accepted==(expected==InputFault::NONE)); CHECK(owner.report().fault==expected);
        if(expected!=InputFault::NONE) frozen(owner,p);
    }
}

TEST_CASE("D093 reviewer setup exhaustive known enum and reversed-clock precedence") {
    for(unsigned status=0;status<17;++status) for(unsigned shutdown=0;shutdown<4;++shutdown)
    for(bool ready:{false,true}) for(bool reverse:{false,true}) {
        Port p; p.init={static_cast<power::Status>(status),static_cast<power::Shutdown>(shutdown),ready};
        p.setup_after=reverse?99U:101U;
        power::InputOwner owner(p.port());
        InputFault expected=InputFault::NONE;
        if(status>14U || shutdown>2U) expected=InputFault::SOURCE;
        else if(status!=0U) expected=InputFault::SETUP;
        else if(!ready || shutdown!=0U) expected=InputFault::SOURCE;
        else if(reverse) expected=InputFault::CLOCK;
        CHECK(owner.begin()==(expected==InputFault::NONE)); CHECK(owner.report().fault==expected);
        CHECK(p.setups==1U); CHECK(p.clocks==2U);
        if(expected!=InputFault::NONE) frozen(owner,p);
    }
}

TEST_CASE("D093 reviewer call bracket cross product accepts only ordered bounded source") {
    const std::uint32_t offsets[]={0U,1U,2U,49U,50U,98U,99U,100U,101U,199U,200U,201U,0x7FFFFFFFU,0x80000000U,0xFFFFFFFFU};
    for(const auto base:{1000U,0xFFFFFFC0U}) for(const auto start:offsets)
    for(const auto completion:offsets) for(const auto duration:{50U,100U,200U}) {
        Port p; p.now=base-10U; p.setup_after=base-9U;
        power::InputOwner owner(p.port()); REQUIRE(owner.begin());
        p.fresh(base,base+start,base+completion,base+duration);
        const bool expected=start<=completion && completion<=duration && completion-start<100U;
        const auto read=owner.readBatteryIfDue(true);
        CHECK(read.attempted); CHECK(read.accepted==expected);
        CHECK(owner.report().fault==(expected?InputFault::NONE:InputFault::SOURCE));
        if(expected) CHECK(owner.report().battery_age_us==duration-start);
    }
}

TEST_CASE("D093 reviewer observed full wraps cannot revive saturated battery evidence") {
    Port p; power::InputOwner owner(p.port()); REQUIRE(owner.begin());
    p.fresh(1000U,1000U,1001U,1001U); REQUIRE(owner.readBatteryIfDue(true).accepted);
    std::uint32_t time=1001U;
    for(unsigned i=0U;i<6U;++i) {
        time+=0x7FFFFFFFU; const auto report=owner.observe(time);
        CHECK(report.fault==InputFault::NONE); CHECK_FALSE(report.battery_available); CHECK(report.battery_due);
        if(i>=2U) CHECK(report.battery_age_us==std::numeric_limits<std::uint32_t>::max());
    }
    const auto source=owner.report().battery.started_us;
    p.now=time; CHECK_FALSE(owner.readBatteryIfDue(false).attempted);
    CHECK(owner.report().battery.started_us==source); CHECK(owner.report().battery_generation==1U);
    p.fresh(time,time,time+1U,time+1U); REQUIRE(owner.readBatteryIfDue(true).accepted);
    CHECK(owner.report().battery_available); CHECK(owner.report().battery_age_us==1U);
    CHECK(owner.report().battery_generation==2U);
    owner.observe(time+1U+0x80000000U); CHECK(owner.report().fault==InputFault::CLOCK); frozen(owner,p);
}

TEST_CASE("D093 reviewer absent prebegin is inert and repeated projections age only once") {
    Port p; power::InputOwner owner(p.port());
    fsm::RobotInput input; input.t_us=0xF0000000U; input.initialization_complete=true;
    CHECK_FALSE(owner.readBatteryIfDue(true).attempted); CHECK_FALSE(owner.readButtons(true).attempted);
    owner.observe(input.t_us); CHECK_FALSE(owner.applyBattery(input)); owner.applyButtons(input,{});
    CHECK(p.callbacks()==0U); CHECK(owner.report().observed_us==0U); CHECK(input.initialization_complete);
    REQUIRE(owner.begin()); p.fresh(1000U,1000U,1001U,1001U); REQUIRE(owner.readBatteryIfDue(true).accepted);
    input.t_us=2000U; REQUIRE(owner.applyBattery(input)); owner.applyButtons(input,{});
    CHECK(owner.report().battery_age_us==1000U); REQUIRE(owner.applyBattery(input));
    CHECK(owner.report().battery_age_us==1000U); CHECK(input.initialization_complete);
    input.t_us=21000U; CHECK_FALSE(owner.applyBattery(input)); CHECK(owner.report().fault==InputFault::NONE);
    CHECK(owner.report().battery_due); CHECK(input.vbat_v==0.0F); CHECK_FALSE(input.vbat_valid);
}

TEST_CASE("D093 reviewer shared A1 failure clears a young A0 projection without erasing diagnostics") {
    Port p; power::InputOwner owner(p.port()); REQUIRE(owner.begin());
    p.fresh(1000U,1000U,1001U,1001U); REQUIRE(owner.readBatteryIfDue(true).accepted);
    p.fresh(1002U,1002U,1003U,1003U); p.button.sequence=2U;
    const auto read=owner.readButtons(true); CHECK(read.attempted); CHECK_FALSE(read.accepted);
    CHECK(read.sample.sequence==2U); CHECK(owner.report().fault==InputFault::SOURCE);
    CHECK(owner.report().battery.valid); CHECK(owner.report().battery_generation==1U);
    CHECK_FALSE(owner.report().battery_available); CHECK_FALSE(owner.report().battery_due); frozen(owner,p);
}

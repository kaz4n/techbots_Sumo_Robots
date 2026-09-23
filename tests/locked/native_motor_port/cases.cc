// Proves B3/B6/B7 and D077 through the actual native backend and MotorGate.
// Expectations come from finalized contracts and installed-source reports only.
// The Python runner builds default-disabled and separate host-only active binaries.
#include "doctest.h"
#include "native_fixture.h"
#include "config.h"
#include "hal/motor_port_unoq.h"
#include <cstdlib>
#include <limits>
#include <type_traits>
#define NEED(...) do { const bool ok=(__VA_ARGS__);CHECK_MESSAGE(ok,#__VA_ARGS__);if(!ok)std::abort(); } while(false)
namespace {
using fixture::hw;
constexpr bool ALLOWED=MOTORS_ALLOWED!=0;
constexpr std::uint32_t PERIODS[4]={3200,250,3200,3200};
constexpr std::uint32_t HOLD_US=(config::COUNTDOWN_MS+config::COUNTDOWN_MARGIN_MS)*1000U;
motors::Channel ch(unsigned i){return static_cast<motors::Channel>(i);}
struct Native {
    motors::UnoQPort native;
    motors::Port p=native.port();
    bool low(){return p.writeEnable(p.context,false);}
    bool high(){return p.writeEnable(p.context,true);}
    bool write(unsigned i,std::uint32_t pulse=0){return p.writePwm(p.context,ch(i),p.period_cycles[i],pulse);}
    bool settle(){return p.settle(p.context);}
    void configure(){NEED(p.configureEnableLow(p.context));NEED(low());for(unsigned i=0;i<4;++i)NEED(p.configurePwm(p.context,ch(i)));}
    void writeAll(){for(unsigned i=0;i<4;++i)NEED(write(i));}
    void ready(){configure();writeAll();NEED(settle());}
};
fsm::RobotResult idle(std::uint64_t token=1){fsm::RobotResult r;r.token=token;r.fresh=true;r.outputs.ui_state=core::State::IDLE;return r;}
fsm::RobotResult hold(std::uint64_t token,std::uint32_t start,bool released=false){auto r=idle(token);r.outputs.ui_state=core::State::COUNTDOWN;r.lifecycle.gate.phase=countdown::Phase::HOLDING;r.lifecycle.gate.release_us=start;r.lifecycle.gate.start_release=released;return r;}
fsm::RobotResult move(std::uint64_t token,std::uint32_t start,float l=.25F,float r=-.25F){auto o=hold(token,start);o.outputs={l,r,true,core::State::SEARCH};o.lifecycle.gate.phase=countdown::Phase::READY;o.lifecycle.gate.motion_permitted=true;return o;}
void off(){CHECK((GPIOB->ODR&(1U<<9))==0);for(unsigned i=0;i<3;++i)for(unsigned j=0;j<4;++j)CHECK(hw.active[i][j]==0);CHECK_FALSE(hw.unsafe_high);CHECK_FALSE(hw.writes_while_high);}
void noHigh(){for(unsigned i=0;i<hw.trace_size;++i)if(hw.trace[i].kind==fixture::WRITE_GPIO)CHECK(hw.trace[i].b==0);}
}
TEST_CASE("B3 D077 native factory is inert immutable and noncopyable") {
    fixture::reset();
    static_assert(!std::is_copy_constructible<motors::UnoQPort>::value);
    static_assert(!std::is_copy_assignable<motors::UnoQPort>::value);
    {fixture::NoAllocation guard;motors::UnoQPort n;auto a=n.port();auto b=n.port();CHECK(a.context==b.context);for(unsigned i=0;i<4;++i)CHECK(a.period_cycles[i]==PERIODS[i]);}
    CHECK(hw.trace_size==0);CHECK(hw.allocations==0);CHECK(hw.deallocations==0);
}
TEST_CASE("B3 D077 native setup maps each channel exactly after EN LOW") {
    fixture::reset();Native n;n.configure();
    CHECK(hw.calls[fixture::CONFIGURE]==1);CHECK(hw.calls[fixture::ROUTE]==4);CHECK(hw.calls[fixture::PWM]==0);
    unsigned count=0;constexpr unsigned expected_device[4]={1,0,1,2},expected_state[4]={0,0,1,0};
    bool low_seen=false;
    for(unsigned i=0;i<hw.trace_size;++i){auto c=hw.trace[i];if(c.kind==fixture::WRITE_GPIO&&c.b==0)low_seen=true;if(c.kind==fixture::ROUTE){CHECK(low_seen);NEED(count<4);CHECK(c.index==expected_device[count]);CHECK(c.a==expected_state[count]);++count;}}
    for(auto i:hw.timer_init){CHECK(i==1);}
    noHigh();
}
TEST_CASE("B3 D077 unconfigured callbacks cannot initialize or enable") {
    fixture::reset();Native n;
    CHECK_FALSE(n.low());CHECK_FALSE(n.high());CHECK_FALSE(n.settle());
    for(unsigned i=0;i<4;++i){CHECK_FALSE(n.write(i));CHECK_FALSE(n.p.configurePwm(n.p.context,ch(i)));}
    CHECK(hw.calls[fixture::CONFIGURE]==0);CHECK(hw.calls[fixture::ROUTE]==0);CHECK(hw.calls[fixture::PWM]==0);CHECK(hw.calls[fixture::CLEAR]==0);noHigh();
}
TEST_CASE("B3 D077 invalid enum period and duty fail before native PWM") {
    fixture::reset();Native n;n.configure();fixture::clearTrace();
    CHECK_FALSE(n.p.configurePwm(n.p.context,ch(255)));
    CHECK_FALSE(n.p.writePwm(n.p.context,ch(255),3200,0));
    for(unsigned i=0;i<4;++i){CHECK_FALSE(n.p.writePwm(n.p.context,ch(i),0,0));CHECK_FALSE(n.p.writePwm(n.p.context,ch(i),PERIODS[i]+1,0));CHECK_FALSE(n.p.writePwm(n.p.context,ch(i),PERIODS[i],PERIODS[i]+1));}
    CHECK(hw.calls[fixture::PWM]==0);CHECK_FALSE(n.high());
}
TEST_CASE("B3 D077 entire GPIO bank masks validate before configuration") {
    for(unsigned slot=0;slot<5;++slot){fixture::reset();auto spec=gpioBase(selected_pins[slot]);fixture_gpio_configs[spec.port->index-7].port_pin_mask&=~(1U<<spec.pin);Native n;CHECK_FALSE(n.p.configureEnableLow(n.p.context));CHECK(hw.calls[fixture::CONFIGURE]==0);CHECK(hw.calls[fixture::ROUTE]==0);}
}
TEST_CASE("B3 D077 EN configure status readiness and raw readback fail closed") {
    for(int status:{-2147483647,-19,-5,-1,1,2,7,2147483647}){
        fixture::reset();Native n;hw.fail_ordinal[fixture::CONFIGURE]=1;hw.fail_status=status;CHECK_FALSE(n.p.configureEnableLow(n.p.context));CHECK_FALSE(n.low());CHECK(hw.calls[fixture::ROUTE]==0);
        fixture::reset();Native m;hw.read_override=status;CHECK_FALSE(m.p.configureEnableLow(m.p.context));CHECK_FALSE(m.high());
    }
    fixture::reset();Native n;hw.ready[8]=false;CHECK_FALSE(n.p.configureEnableLow(n.p.context));CHECK(hw.calls[fixture::CONFIGURE]==0);
}
TEST_CASE("B3 D077 preowned timers are rejected without resetting them") {
    for(unsigned i=0;i<3;++i){fixture::reset();hw.ready[i]=true;fixture::timer(i)->CR1=0x1234;Native n;NEED(n.p.configureEnableLow(n.p.context));NEED(n.low());unsigned slot=i==0?1:i==1?0:3;CHECK_FALSE(n.p.configurePwm(n.p.context,ch(slot)));CHECK(hw.calls[fixture::ROUTE]==0);CHECK(fixture::timer(i)->CR1==0x1234);}
}
TEST_CASE("B3 D077 routing and cycle getter errors remain errors at every slot") {
    for(auto kind:{fixture::ROUTE,fixture::RATE})for(unsigned slot=0;slot<4;++slot)for(int status:{-19,-1,1,7}){
        fixture::reset();Native n;NEED(n.p.configureEnableLow(n.p.context));NEED(n.low());
        for(unsigned i=0;i<slot;++i)NEED(n.p.configurePwm(n.p.context,ch(i)));
        hw.fail_ordinal[kind]=static_cast<int>(hw.calls[kind]+1);hw.fail_status=status;
        CHECK_FALSE(n.p.configurePwm(n.p.context,ch(slot)));auto routes=hw.calls[fixture::ROUTE];CHECK_FALSE(n.write(slot));CHECK(hw.calls[fixture::ROUTE]==routes);noHigh();
    }
}
TEST_CASE("B3 D077 live zero incorrect and fractional carrier rates never adjust candidates") {
    for(unsigned slot=0;slot<4;++slot)for(std::uint64_t bad:{0ULL,1ULL,2499999ULL,2500001ULL,31999999ULL,32000001ULL,160000000ULL,0xffffffffffffffffULL}){
        fixture::reset();Native n;NEED(n.p.configureEnableLow(n.p.context));NEED(n.low());unsigned i=slot==1?0:slot==3?2:1;hw.rate[i]=bad;CHECK_FALSE(n.p.configurePwm(n.p.context,ch(slot)));CHECK(n.p.period_cycles[slot]==PERIODS[slot]);CHECK_FALSE(n.write(slot));
    }
}
TEST_CASE("B3 D077 current four writes are required and native zero means no duty") {
    for(unsigned missing=0;missing<4;++missing){fixture::reset();Native n;n.configure();for(unsigned i=0;i<4;++i)if(i!=missing)NEED(n.write(i));fixture::clearTrace();CHECK_FALSE(n.settle());CHECK_FALSE(n.high());CHECK(hw.calls[fixture::CLEAR]==0);CHECK(hw.calls[fixture::POLL]==0);}
    fixture::reset();Native n;n.ready();off();for(unsigned i=0;i<3;++i){CHECK(hw.active_arr[i]==(i==0?249:3199));CHECK(hw.clears[i]==1);}
}
TEST_CASE("B3 D077 stale initial UIF cannot settle a transaction") {
    fixture::reset();Native n;n.configure();n.writeAll();for(unsigned i=0;i<3;++i){CHECK((fixture::timer(i)->SR&1U)!=0);hw.fresh_after[i]=-1;}
    CHECK_FALSE(n.settle());CHECK_FALSE(n.high());for(auto c:hw.clears)CHECK(c==1);CHECK(hw.calls[fixture::POLL]<=3U*config::MOTOR_PWM_SETTLE_MAX_POLLS);noHigh();
}
TEST_CASE("B3 D077 three asynchronous updates transfer all preloads independently") {
    fixture::reset();Native n;n.ready();NEED(n.low());
    for(unsigned i=0;i<4;++i)NEED(n.write(i,ALLOWED?PERIODS[i]/2:0));
    for(unsigned i=0;i<3;++i)for(unsigned j=0;j<4;++j)CHECK(hw.active[i][j]==0);
    hw.fresh_after[0]=3;hw.fresh_after[1]=1;hw.fresh_after[2]=5;
    NEED(n.settle());CHECK(hw.update_mask==7);
    CHECK(hw.active[0][3]==(ALLOWED?125U:0U));CHECK(hw.active[1][2]==(ALLOWED?1600U:0U));CHECK(hw.active[1][3]==(ALLOWED?1600U:0U));CHECK(hw.active[2][2]==(ALLOWED?1600U:0U));
    CHECK(n.high()==ALLOWED);CHECK_FALSE(hw.unsafe_high);
}
TEST_CASE("B3 D077 either legitimate clear race outcome preserves safety") {
    for(bool survives:{false,true}){fixture::reset();Native n;n.configure();n.writeAll();hw.race_survives=survives;hw.race_cleared=!survives;for(auto& f:hw.fresh_after)f=survives?-1:2;NEED(n.settle());CHECK(hw.update_mask==7);for(auto c:hw.clears)CHECK(c==1);}
}
TEST_CASE("B3 D077 each stalled timer independently prevents enable") {
    for(unsigned stalled=0;stalled<3;++stalled){fixture::reset();Native n;n.configure();n.writeAll();hw.fresh_after[stalled]=-1;CHECK_FALSE(n.settle());CHECK_FALSE(n.high());CHECK(hw.polls[stalled]>0);CHECK(hw.calls[fixture::POLL]<=3U*config::MOTOR_PWM_SETTLE_MAX_POLLS);noHigh();}
}
TEST_CASE("B3 D077 strict whole-pass deadline rejects exact and late completion") {
    for(unsigned elapsed:{149U,150U,151U}){fixture::reset();Native n;n.configure();n.writeAll();hw.now=0;hw.ticks_per_poll=0;hw.use_event_elapsed=true;hw.event_elapsed=elapsed;CHECK(n.settle()==(elapsed<150U));CHECK(n.high()==(ALLOWED&&elapsed<150U));}
}
TEST_CASE("B3 D077 elapsed arithmetic survives micros wrap and frozen clocks terminate") {
    fixture::reset();Native n;n.configure();n.writeAll();hw.now=0xfffffffeU;NEED(n.settle());CHECK(hw.now<10U);
    fixture::reset();Native m;m.configure();m.writeAll();hw.ticks_per_poll=0;for(auto& f:hw.fresh_after)f=-1;CHECK_FALSE(m.settle());CHECK(hw.now==0);CHECK(hw.calls[fixture::POLL]<=3U*config::MOTOR_PWM_SETTLE_MAX_POLLS);CHECK(hw.calls[fixture::POLL]>0);CHECK_FALSE(m.high());
}
TEST_CASE("B3 D077 repeated writes and LOW invalidate previous settle receipts") {
    fixture::reset();Native n;n.ready();NEED(n.write(2));NEED(n.settle());NEED(n.write(2));CHECK_FALSE(n.high());CHECK_FALSE(n.settle());NEED(n.low());CHECK_FALSE(n.settle());CHECK_FALSE(n.high());
    NEED(n.low());n.writeAll();NEED(n.settle());hw.fail_ordinal[fixture::PWM]=static_cast<int>(hw.calls[fixture::PWM]+1);CHECK_FALSE(n.write(1));CHECK_FALSE(n.settle());CHECK_FALSE(n.high());
}
TEST_CASE("B3 D077 native PWM error at every channel invalidates current completion") {
    for(unsigned slot=0;slot<4;++slot)for(int status:{-19,-1,1,7}){fixture::reset();Native n;n.ready();NEED(n.low());for(unsigned i=0;i<4;++i){if(i==slot){hw.fail_ordinal[fixture::PWM]=static_cast<int>(hw.calls[fixture::PWM]+1);hw.fail_status=status;CHECK_FALSE(n.write(i));}else NEED(n.write(i));}CHECK_FALSE(n.settle());CHECK_FALSE(n.high());}
}
TEST_CASE("B3 D077 mode ownership flags and every guarded register bit reject settling") {
    for(unsigned timer=0;timer<3;++timer)for(unsigned reg=0;reg<10;++reg)for(unsigned bit=0;bit<32;++bit){
        if(timer!=0&&(reg==8||reg==9))continue;
        fixture::reset();Native n;n.ready();NEED(n.low());n.writeAll();auto* t=fixture::timer(timer);
        volatile std::uint32_t* regs[]={&t->CR1,&t->CR2,&t->SMCR,&t->DIER,&t->PSC,&t->ARR,&t->CCMR1,&t->CCMR2,&t->RCR,&t->BDTR};
        *regs[reg]^=1U<<bit;fixture::clearTrace();CHECK_FALSE(n.settle());CHECK_FALSE(n.high());CHECK(hw.calls[fixture::CLEAR]==0);
    }
    for(unsigned timer=0;timer<3;++timer)for(unsigned bit=0;bit<32;++bit){fixture::reset();Native n;n.ready();NEED(n.low());n.writeAll();fixture::timer(timer)->CCER^=1U<<bit;CHECK_FALSE(n.settle());CHECK_FALSE(n.high());}
}
TEST_CASE("B3 D077 changed CCR values cannot reuse a successful write") {
    for(unsigned slot=0;slot<4;++slot){fixture::reset();Native n;n.ready();NEED(n.low());n.writeAll();auto* t=fixture::timer(slot==1?0:slot==3?2:1);if(slot==1||slot==2)t->CCR4=1;else t->CCR3=1;CHECK_FALSE(n.settle());CHECK_FALSE(n.high());}
}
TEST_CASE("B3 D077 EN remux pull or output-type change rejects all runtime motion work") {
    for(unsigned kind=0;kind<3;++kind){fixture::reset();Native n;n.ready();if(kind==0)GPIOB->MODER^=3U<<18;if(kind==1)GPIOB->OTYPER|=1U<<9;if(kind==2)GPIOB->PUPDR|=1U<<18;fixture::clearTrace();CHECK_FALSE(n.write(0));CHECK_FALSE(n.settle());CHECK_FALSE(n.high());CHECK(hw.calls[fixture::PWM]==0);CHECK(hw.calls[fixture::ROUTE]==0);CHECK(hw.calls[fixture::CONFIGURE]==0);noHigh();}
}
TEST_CASE("B3 D077 changes during flag polling are checked before success") {
    for(unsigned timer=0;timer<3;++timer){fixture::reset();Native n;n.ready();NEED(n.low());n.writeAll();hw.corrupt_reg=&fixture::timer(timer)->DIER;hw.corrupt_value=1;hw.corrupt_at_poll=hw.calls[fixture::POLL]+1;CHECK_FALSE(n.settle());CHECK_FALSE(n.high());}
    for(unsigned index:{0U,1U,2U,8U}){fixture::reset();Native n;n.ready();NEED(n.low());n.writeAll();hw.lose_ready_index=index;hw.lose_ready_at_poll=hw.calls[fixture::POLL]+1;CHECK_FALSE(n.settle());CHECK_FALSE(n.high());}
}
TEST_CASE("B3 D077 activation rechecks EN and settings without rerouting hardware") {
    for(unsigned kind=0;kind<4;++kind){fixture::reset();Native n;n.ready();if(kind==0)TIM3->CCR3=1;if(kind==1)hw.ready[1]=false;if(kind==2)GPIOB->IDR|=1U<<9;if(kind==3)TIM1->CR1|=TIM_CR1_OPM;fixture::clearTrace();CHECK_FALSE(n.high());CHECK(hw.calls[fixture::ROUTE]==0);noHigh();}
}
TEST_CASE("B3 D077 default-disabled backend rejects nonzero pulses and HIGH") {
    if(ALLOWED)return;
    fixture::reset();Native n;n.ready();fixture::clearTrace();for(unsigned i=0;i<4;++i)CHECK_FALSE(n.write(i,1));CHECK_FALSE(n.high());CHECK(hw.calls[fixture::PWM]==0);noHigh();
}
TEST_CASE("B3 D077 actual Gate release hold boundary and unsigned wrap stay enforced") {
    for(std::uint32_t start:{0U,0xfffffff0U})for(unsigned offset:{HOLD_US-1,HOLD_US,HOLD_US+1}){
        fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());hw.now=start;NEED(gate.apply(start,hold(1,start,true)).feedback.applied_valid);fixture::clearTrace();hw.now=start+offset;auto r=gate.apply(hw.now,move(2,start));
        if(offset<HOLD_US){CHECK(r.fault==motors::Fault::COMMAND);CHECK_FALSE(r.feedback.applied_valid);noHigh();off();}
        else{CHECK(r.fault==motors::Fault::NONE);CHECK(r.feedback.applied_valid);CHECK(r.feedback.motors_enabled==ALLOWED);CHECK_FALSE(hw.unsafe_high);}
    }
}
TEST_CASE("B7 D077 actual Gate direction reversal full duty and active zero follow native settle") {
    fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());NEED(gate.apply(0,hold(1,0,true)).feedback.applied_valid);
    for(unsigned tick=0;tick<4;++tick){hw.now=HOLD_US+1000*tick;auto r=move(2+tick,0,tick==0?.5F:tick==1?-.5F:tick==2?1.F:0.F,tick==0?-.5F:tick==1?.5F:tick==2?1.F:0.F);if(tick==2){r.outputs.ui_state=core::State::ATTACK;r.contact=true;r.opponent_mask=2;}fixture::clearTrace();auto a=gate.apply(hw.now,r);CHECK(a.feedback.applied_valid);CHECK(a.feedback.motors_enabled==ALLOWED);CHECK_FALSE(hw.unsafe_high);CHECK_FALSE(hw.writes_while_high);CHECK(hw.calls[fixture::PWM]==4);CHECK(hw.calls[fixture::CLEAR]==3);if(ALLOWED){CHECK(hw.active[1][2]==(tick==0?1600U:tick==2?3200U:0U));CHECK(hw.active[0][3]==(tick==1?125U:0U));}else off();}
}
TEST_CASE("B3 D077 actual Gate failed writes try all zero cleanup and report invalid receipt") {
    for(unsigned slot=0;slot<4;++slot){fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());NEED(gate.apply(0,hold(1,0,true)).feedback.applied_valid);fixture::clearTrace();hw.fail_ordinal[fixture::PWM]=static_cast<int>(slot+1);hw.now=HOLD_US;auto a=gate.apply(hw.now,move(2,0));CHECK(a.fault==motors::Fault::IO);CHECK_FALSE(a.feedback.applied_valid);CHECK(a.consumed);CHECK(hw.calls[fixture::PWM]==slot+5);noHigh();off();auto routes=hw.calls[fixture::ROUTE];NEED(gate.reset());CHECK(hw.calls[fixture::ROUTE]==routes);}
}
TEST_CASE("B3 D077 partial setup failure cleanup never initializes untouched devices") {
    for(unsigned slot=0;slot<4;++slot){fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());hw.fail_ordinal[fixture::ROUTE]=static_cast<int>(slot+1);CHECK_FALSE(gate.begin());CHECK(gate.fault()==motors::Fault::IO);auto routes=hw.calls[fixture::ROUTE];CHECK_FALSE(gate.reset());CHECK(hw.calls[fixture::ROUTE]==routes);noHigh();}
}
TEST_CASE("B3 D077 actual Robot Gate composition remains off throughout accepted hold") {
    fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());fsm::Robot robot;NEED(gate.begin());fsm::RobotInput in;in.initialization_complete=true;in.observations_fresh=true;in.vbat_valid=true;in.vbat_v=config::V_NOM_V;in.opp_raw_mask=0x78;for(auto& value:in.line_raw_us)value=500;std::uint32_t release=0;bool seen=false,go=false;
    for(unsigned tick=0;tick<5200;++tick){in.t_us=tick*1000U;hw.now=in.t_us;in.button=tick>=30&&tick<60?core::ButtonLevel::START:core::ButtonLevel::NONE;fixture::clearTrace();auto command=robot.step(in);if(command.lifecycle.gate.start_release){release=in.t_us;seen=true;}auto applied=gate.apply(in.t_us,command);NEED(applied.feedback.applied_valid);if(!seen||in.t_us-release<HOLD_US){off();noHigh();}else if(command.outputs.motors_enabled){CHECK(applied.feedback.motors_enabled==ALLOWED);go=true;}in.previous=applied.feedback;}
    CHECK(seen);CHECK(go);CHECK_FALSE(hw.unsafe_high);CHECK_FALSE(hw.writes_while_high);
}
TEST_CASE("B3 D077 runtime callbacks stay allocation-free with finite native counts") {
    fixture::reset();Native n;n.ready();fixture::clearTrace();bool ok=true;
    {fixture::NoAllocation guard;for(unsigned tick=0;tick<10000;++tick){ok=n.low()&&ok;for(unsigned i=0;i<4;++i)ok=n.write(i)&&ok;ok=n.settle()&&ok;}}
    CHECK(ok);CHECK(hw.allocations==0);CHECK(hw.deallocations==0);CHECK(hw.calls[fixture::PWM]==40000);CHECK(hw.calls[fixture::ROUTE]==0);CHECK(hw.calls[fixture::CONFIGURE]==0);CHECK(hw.calls[fixture::CLEAR]==30000);CHECK(hw.calls[fixture::POLL]<=120000);CHECK(hw.calls[fixture::CLOCK]<=40000);
}

TEST_CASE("B3 D077 mismatched native initial state fails setup without resetting again") {
    for(unsigned timer=0;timer<3;++timer)for(unsigned reg=0;reg<11;++reg){
        if(timer!=0&&reg>=9)continue;
        fixture::reset();Native n;NEED(n.p.configureEnableLow(n.p.context));NEED(n.low());hw.init_bad_register=static_cast<int>(reg);hw.init_flip=1;
        CHECK_FALSE(n.p.configurePwm(n.p.context,ch(timer==0?1:timer==1?0:3)));CHECK(hw.calls[fixture::ROUTE]==1);CHECK_FALSE(n.write(timer==0?1:timer==1?0:3));
    }
}
TEST_CASE("B3 D077 EN write and readback failures invalidate any previous settle") {
    for(auto kind:{fixture::WRITE_GPIO,fixture::READ_GPIO})for(int status:{-19,-1,1,2,7}){
        fixture::reset();Native n;n.ready();hw.fail_ordinal[kind]=static_cast<int>(hw.calls[kind]+1);hw.fail_status=status;CHECK_FALSE(n.low());CHECK_FALSE(n.high());
    }
    if(ALLOWED)for(int status:{-19,-1,1,2,7}){
        fixture::reset();Native n;n.ready();hw.fail_ordinal[fixture::WRITE_GPIO]=static_cast<int>(hw.calls[fixture::WRITE_GPIO]+1);hw.fail_status=status;CHECK_FALSE(n.high());CHECK_FALSE(n.high());
    }
}
TEST_CASE("B3 D077 SR unrelated flags and general timer reserved advanced words do not fake owners") {
    fixture::reset();Native n;n.ready();NEED(n.low());n.writeAll();
    TIM3->BDTR=0xffffffff;TIM4->BDTR=0xffffffff;TIM3->RCR=0xffffffff;TIM4->RCR=0xffffffff;
    for(unsigned i=0;i<3;++i)fixture::timer(i)->SR=0xffff;
    NEED(n.settle());for(unsigned i=0;i<3;++i)CHECK((fixture::timer(i)->SR&0xfffe)==0xfffe);
}

TEST_CASE("B3 D077 channel routing success cannot mask an unready native timer") {
    for(unsigned slot:{0U,1U,3U}){fixture::reset();Native n;NEED(n.p.configureEnableLow(n.p.context));NEED(n.low());hw.route_without_ready=1;CHECK_FALSE(n.p.configurePwm(n.p.context,ch(slot)));CHECK_FALSE(n.write(slot));CHECK(hw.calls[fixture::ROUTE]==1);CHECK(hw.calls[fixture::PWM]==0);}
}
TEST_CASE("B3 D077 reading a Port again has no reset or peripheral effect") {
    fixture::reset();Native n;n.ready();fixture::clearTrace();auto second=n.native.port();CHECK(hw.trace_size==0);CHECK(second.context==n.p.context);CHECK(n.high()==ALLOWED);CHECK_FALSE(hw.unsafe_high);
}

TEST_CASE("B3 D077 actual Gate handles failure at every observed setup raw-read position") {
    fixture::reset();unsigned reads=0;
    {motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());reads=hw.calls[fixture::READ_GPIO];}
    NEED(reads>0);
    for(unsigned ordinal=1;ordinal<=reads;++ordinal)for(int status:{-5,2}){
        fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());hw.fail_ordinal[fixture::READ_GPIO]=static_cast<int>(ordinal);hw.fail_status=status;
        CHECK_FALSE(gate.begin());CHECK(gate.fault()==motors::Fault::IO);noHigh();CHECK_FALSE(hw.writes_while_high);
    }
}
TEST_CASE("B3 D077 actual Gate handles failure at every observed transaction raw-read position") {
    fixture::reset();unsigned reads=0;
    {motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());NEED(gate.apply(0,hold(1,0,true)).feedback.applied_valid);fixture::clearTrace();hw.now=HOLD_US;NEED(gate.apply(hw.now,move(2,0)).feedback.applied_valid);reads=hw.calls[fixture::READ_GPIO];}
    NEED(reads>0);
    for(unsigned ordinal=1;ordinal<=reads;++ordinal)for(int status:{-5,2}){
        fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());NEED(gate.apply(0,hold(1,0,true)).feedback.applied_valid);fixture::clearTrace();hw.now=HOLD_US;hw.fail_ordinal[fixture::READ_GPIO]=static_cast<int>(ordinal);hw.fail_status=status;
        const auto result=gate.apply(hw.now,move(2,0));CHECK(result.fault==motors::Fault::IO);CHECK_FALSE(result.feedback.applied_valid);CHECK(result.consumed);off();
    }
}
TEST_CASE("B3 D077 actual Gate invalidates HIGH after failed or mismatched postwrite readback") {
    if(!ALLOWED)return;
    for(int status:{-19,-1,0,2,7}){
        fixture::reset();motors::UnoQPort n;motors::MotorGate gate(n.port());NEED(gate.begin());NEED(gate.apply(0,hold(1,0,true)).feedback.applied_valid);fixture::clearTrace();hw.now=HOLD_US;hw.high_read_override=status;
        const auto result=gate.apply(hw.now,move(2,0));CHECK(result.fault==motors::Fault::IO);CHECK_FALSE(result.feedback.applied_valid);CHECK(result.consumed);CHECK(hw.calls[fixture::PWM]==8);off();
        unsigned highs=0;for(unsigned i=0;i<hw.trace_size;++i)if(hw.trace[i].kind==fixture::WRITE_GPIO&&hw.trace[i].b==1)++highs;CHECK(highs==1);
    }
}

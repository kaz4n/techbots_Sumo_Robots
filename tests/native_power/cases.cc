// Tests the B5 public contract using source-derived silicon and ownership facts.
// No expectation is derived from the opaque production power implementation.
// Native execution checks fresh samples, latched faults and bounded cleanup.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
#include "config.h"
#include <cmath>
#include <cstdint>
#include <limits>
#include <type_traits>
using power::Status;using power::Shutdown;
namespace {
void invalid(const power::Sample& s,Status status) {
    CHECK(s.status==status);CHECK_FALSE(s.valid);CHECK(s.raw==0);CHECK(s.voltage_v==0.0F);
}
void noMoreIo(power::Reader& r,Shutdown shutdown) {
    fixture::clearTrace();auto s=r.read();invalid(s,Status::FAULT_LATCHED);CHECK(s.shutdown==shutdown);
    auto b=r.begin();CHECK(b.status==Status::ALREADY_STARTED);CHECK_FALSE(b.ready);CHECK(b.shutdown==shutdown);
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);
}
void ready(power::Reader& r) {
    auto b=r.begin();REQUIRE(b.status==Status::OK);REQUIRE(b.ready);
    CHECK(fixture::hw.gated_reads==0);CHECK(fixture::hw.command_errors==0);CHECK(fixture::hw.cal_count==1);CHECK(fixture::hw.enable_count==1);
    CHECK(fixture::hw.enable_us-fixture::hw.cal_done_us>=2);
}
fixture::Point inject_point;unsigned writes_at_loss;bool injected;
void loseOwnership(fixture::Point p,std::uintptr_t) {
    if(!injected&&p==inject_point){injected=true;SYSCFG->CFGR1.value|=SYSCFG_CFGR1_BOOSTEN;writes_at_loss=fixture::hw.writes;}
}
std::uint32_t origin;fixture::Point late_point;
void becomeLate(fixture::Point p,std::uintptr_t) {
    if(p==late_point)fixture::hw.now=origin+config::VBAT_ADC_CONVERSION_US;
}
}
TEST_CASE("B5 construction destruction and prebegin reads have no native I/O or allocation") {fixture::isolated([&] {
    fixture::reset();
    {fixture::AllocationGuard g;power::Reader r;invalid(r.read(),Status::NOT_INITIALIZED);}
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);CHECK(fixture::hw.ready_reads==0);CHECK(fixture::hw.allocations==0);
    static_assert(!std::is_copy_constructible<power::Reader>::value);
    static_assert(!std::is_copy_assignable<power::Reader>::value);

});}
TEST_CASE("B5 setup uses one ordinary calibration and exact narrow conversion mode") {fixture::isolated([&] {
    fixture::reset();power::Reader r;ready(r);
    CHECK(fixture::peek(ADC1->CFGR1)==0x80000000U);CHECK(fixture::peek(ADC1->CFGR2)==ADC_CFGR2_LFTRIG);
    CHECK(fixture::peek(ADC1->SMPR1)==(7U<<27));CHECK(fixture::peek(ADC1->PCSEL)==512U);
    CHECK(fixture::peek(ADC1->SQR1)==(9U<<6));CHECK(fixture::peek(ADC1->DIFSEL)==0U);
    CHECK(fixture::peek(ADC1->IER)==0U);CHECK(fixture::peek(ADC12_COMMON->CCR)==0x80000U);
    CHECK(fixture::peek(GPIOA->MODER)==0xffffffffU);CHECK(fixture::peek(GPIOA->PUPDR)==0U);
    fixture::clearTrace();auto b=r.begin();CHECK(b.status==Status::ALREADY_STARTED);CHECK(b.ready);
    CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);CHECK(fixture::hw.micros_calls==0);

});}
TEST_CASE("B5 every successful read is fresh 14-bit raw data with nominal unfiltered voltage") {fixture::isolated([&] {
    fixture::reset();power::Reader r;ready(r);
    unsigned n=0;
    for(auto raw:{0U,1U,8192U,16382U,16383U,37U,0U}) {
        fixture::hw.sample=raw;fixture::hw.conversion_after=1;
        auto s=r.read();CAPTURE(raw);CHECK(s.status==Status::OK);CHECK(s.valid);CHECK(s.raw==raw);
        CHECK(s.voltage_v==doctest::Approx(float(raw)/16383.0F*3.3F*(122.0F/22.0F)));
        CHECK(s.completed_us-s.started_us<100U);CHECK(s.completed_us-s.started_us>0U);
        CHECK(fixture::hw.start_count==++n);CHECK(fixture::hw.data_reads==n);CHECK(fixture::hw.command_errors==0);
        CHECK((fixture::peek(ADC1->ISR)&(ADC_ISR_EOC|ADC_ISR_EOS))==0U);
    }

});}
TEST_CASE("B5 read clears stale regular flags by W1C without consuming stale DR") {fixture::isolated([&] {
    fixture::reset();power::Reader r;ready(r);
    ADC1->ISR.value|=ADC_ISR_EOC|ADC_ISR_EOS|ADC_ISR_OVR|ADC_ISR_EOSMP|ADC_ISR_AWD1;
    ADC1->DR.value=123U;fixture::hw.sample=987U;
    auto s=r.read();REQUIRE(s.valid);CHECK(s.raw==987U);CHECK(fixture::hw.data_reads==1);
    CHECK((fixture::peek(ADC1->ISR)&ADC_ISR_AWD1)!=0U);CHECK(fixture::hw.command_errors==0);

});}
TEST_CASE("B5 stale flags that cannot clear are not accepted as a new sample") {fixture::isolated([&] {
    fixture::reset();power::Reader r;ready(r);
    ADC1->ISR.value|=ADC_ISR_EOC|ADC_ISR_EOS;fixture::hw.freeze_stale=true;
    auto s=r.read();invalid(s,Status::READBACK);CHECK(fixture::hw.start_count==0);CHECK(fixture::hw.data_reads==0);
    noMoreIo(r,s.shutdown);

});}
TEST_CASE("B5 invalid 32-bit raw values never narrow to apparently healthy data") {
    for(auto raw:{16384U,65536U,0xffffffffU}) {fixture::isolated([&] {
        fixture::reset();power::Reader r;ready(r);fixture::hw.sample=raw;
        auto s=r.read();invalid(s,Status::INVALID_DATA);CHECK(fixture::hw.data_reads==1);noMoreIo(r,s.shutdown);
    
});}
}
TEST_CASE("B5 second live owner cannot gain admission") {
    fixture::isolated([&] {
        fixture::reset();power::Reader first;ready(first);fixture::clearTrace();power::Reader second;
        auto b=second.begin();CHECK(b.status==Status::OWNERSHIP);CHECK_FALSE(b.ready);
        CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);noMoreIo(second,b.shutdown);
    });
}
TEST_CASE("B5 initialized and failed stock ADC owner state rejects a fresh boot") {
    for(auto res:{0,5})fixture::isolated([&] {
        fixture::reset();fixture_devices[0].state->initialized=true;fixture_devices[0].state->init_res=res;
        power::Reader r;auto b=r.begin();CHECK(b.status==Status::OWNERSHIP);
        CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);
        CHECK(fixture::hw.clock_on==0);noMoreIo(r,b.shutdown);
    });
}
TEST_CASE("B5 admission excludes each documented shared owner and incompatible supply mode") {fixture::isolated([&] {
    struct Bad {volatile Reg* word;std::uint32_t bit;};
    fixture::reset();
    const Bad bad[]={
        {&ADC4->CR,ADC_CR_ADEN},{&ADC4->CR,ADC_CR_ADSTART},{&ADC4->CR,ADC_CR_ADSTP},
        {&ADC4->CR,ADC_CR_ADDIS},{&ADC4->CR,ADC_CR_ADCAL},{&ADC4->IER,ADC_IER_EOCIE},
        {&ADC4->CFGR1,ADC_CFGR1_EXTEN_0},{&ADC4->CFGR1,ADC_CFGR1_CONT},
        {&DAC1->CR,DAC_CR_EN1},{&DAC1->CR,DAC_CR_CEN1},{&DAC1->CR,DAC_CR_TEN1},
        {&DAC1->CR,DAC_CR_DMAEN1},{&DAC1->CR,DAC_CR_WAVE1_0},
        {&GPIOA->LCKR,GPIO_LCKR_LCK4},{&GPIOA->PUPDR,1U<<8},
        {&SYSCFG->CFGR1,SYSCFG_CFGR1_BOOSTEN},{&SYSCFG->CFGR1,SYSCFG_CFGR1_ANASWVDD},
        {&RCC->CCIPR3,RCC_CCIPR3_ADCDACSEL_0},{&RCC->CFGR2,RCC_CFGR2_HPRE_0},
        {&RCC->PLL1CFGR,RCC_PLL1CFGR_PLL1FRACEN}
    };
    for(const auto& x:bad) {fixture::isolated([&] {
        fixture::reset();x.word->value|=x.bit;power::Reader r;
        auto b=r.begin();CAPTURE(reinterpret_cast<std::uintptr_t>(x.word));CAPTURE(x.bit);
        CHECK(b.status==Status::OWNERSHIP);CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);
    
});}
    for(unsigned irq=0;irq<5;++irq) {fixture::isolated([&] {
        fixture::reset();if(irq<2)fixture::hw.irq_pending[irq]=true;
        else if(irq<4)fixture::hw.irq_active[irq-2]=true;else fixture::hw.irq_enable[0]=true;
        power::Reader r;auto b=r.begin();CHECK(b.status==Status::OWNERSHIP);CHECK(fixture::hw.writes==0);
    
});}
    for(unsigned k=0;k<4;++k) {fixture::isolated([&] {
        fixture::reset();if(k==0)PWR->SVMCR.value&=~PWR_SVMCR_ASV;
        if(k==1)PWR->VOSR.value&=~PWR_VOSR_VOSRDY;
        if(k==2)GPIOA->MODER.value&=~(3U<<8);
        if(k==3)RCC->AHB2ENR1.value&=~RCC_AHB2ENR1_GPIOAEN;
        power::Reader r;CHECK(r.begin().status==Status::OWNERSHIP);CHECK(fixture::hw.writes==0);
    
});}

});}
TEST_CASE("B5 ADC nonreset register admission never steals or rewrites an owner") {fixture::isolated([&] {
    fixture::reset();volatile Reg* words[]={&ADC1->IER,&ADC1->CFGR2,&ADC1->SMPR1,&ADC1->PCSEL,
        &ADC1->SQR1,&ADC1->SQR2,&ADC1->SQR3,&ADC1->SQR4,&ADC1->JSQR,&ADC1->DIFSEL,
        &ADC1->OFR1,&ADC1->OFR2,&ADC1->OFR3,&ADC1->OFR4,&ADC1->GCOMP,&ADC1->AWD2CR,&ADC1->AWD3CR,&ADC12_COMMON->CCR};
    for(auto* reg:words) {fixture::isolated([&] {
        fixture::reset();reg->value=1U;power::Reader r;auto b=r.begin();CAPTURE(reinterpret_cast<std::uintptr_t>(reg));
        CHECK(b.status==Status::OWNERSHIP);CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);
    
});}

});}
TEST_CASE("B5 regulator calibration enable deadlines and frozen clocks fail closed") {
    for(unsigned stage=0;stage<3;++stage)for(bool frozen:{false,true}) {fixture::isolated([&] {
        fixture::reset();if(stage==0)fixture::hw.ldo_after=-1;
        if(stage==1)fixture::hw.cal_after=-1;
        if(stage==2)fixture::hw.enable_after=-1;
        if(frozen)fixture::hw.tick=0;
        power::Reader r;auto b=r.begin();CAPTURE(stage);CAPTURE(frozen);
        CHECK_FALSE(b.ready);CHECK(b.status==(frozen?Status::POLL_LIMIT:stage==0?Status::REGULATOR_TIMEOUT:stage==1?Status::CALIBRATION_TIMEOUT:Status::ENABLE_TIMEOUT));
        CHECK(fixture::hw.accesses<10000000U);CHECK(fixture::hw.command_errors==0);noMoreIo(r,b.shutdown);
    
});}
}
TEST_CASE("B5 runtime needs both fresh completion flags and rejects overrun") {
    for(std::uint32_t flags:std::array<std::uint32_t,4>{0U,ADC_ISR_EOC,ADC_ISR_EOS,ADC_ISR_EOC|ADC_ISR_EOS|ADC_ISR_OVR}) {fixture::isolated([&] {
        fixture::reset();power::Reader r;ready(r);fixture::hw.completion_flags=flags;
        auto s=r.read();invalid(s,(flags&ADC_ISR_OVR)?Status::OVERRUN:Status::CONVERSION_TIMEOUT);
        CHECK(fixture::hw.data_reads==0);CHECK(fixture::hw.command_errors==0);noMoreIo(r,s.shutdown);
    
});}
}
TEST_CASE("B5 single runtime deadline includes data and EOS cleanup equality") {
    for(auto point:{fixture::Point::START,fixture::Point::DATA,fixture::Point::EOS_CLEAR}) {fixture::isolated([&] {
        fixture::reset();power::Reader r;ready(r);origin=fixture::hw.now;late_point=point;fixture::hw.hook=becomeLate;
        auto s=r.read();fixture::hw.hook=nullptr;invalid(s,Status::CONVERSION_TIMEOUT);noMoreIo(r,s.shutdown);
    
});}
}
TEST_CASE("B5 ownership lost at setup conversion or cleanup forbids blind shutdown writes") {
    for(auto point:{fixture::Point::LDO_READY,fixture::Point::CAL_DONE,fixture::Point::ENABLE_READY,
                   fixture::Point::START,fixture::Point::DATA,fixture::Point::EOS_CLEAR}) {fixture::isolated([&] {
        fixture::reset();power::Reader r;inject_point=point;injected=false;
        if(point==fixture::Point::LDO_READY||point==fixture::Point::CAL_DONE||point==fixture::Point::ENABLE_READY) {
            fixture::hw.hook=loseOwnership;auto b=r.begin();CHECK(b.status==Status::OWNERSHIP);CHECK(b.shutdown==Shutdown::UNCONFIRMED);
        } else {ready(r);fixture::hw.hook=loseOwnership;auto s=r.read();invalid(s,Status::OWNERSHIP);CHECK(s.shutdown==Shutdown::UNCONFIRMED);}
        fixture::hw.hook=nullptr;CHECK(injected);CHECK(fixture::hw.writes==writes_at_loss);noMoreIo(r,Shutdown::UNCONFIRMED);
    
});}
}
TEST_CASE("B5 abort and disable acknowledgements control shutdown result") {
    for(unsigned kind=0;kind<3;++kind) {fixture::isolated([&] {
        fixture::reset();power::Reader r;ready(r);fixture::hw.conversion_after=-1;
        if(kind==1)fixture::hw.stop_after=-1;
        if(kind==2)fixture::hw.disable_after=-1;
        auto s=r.read();invalid(s,Status::CONVERSION_TIMEOUT);CHECK(s.shutdown==(kind?Shutdown::UNCONFIRMED:Shutdown::DISABLED));
        CHECK(fixture::hw.stop_count==1);CHECK(fixture::hw.disable_count==(kind==1?0U:1U));
        CHECK(fixture::hw.command_errors==0);CHECK(fixture::hw.now-s.started_us<250U);noMoreIo(r,s.shutdown);
    
});}
}
TEST_CASE("B5 frozen runtime clock obeys finite poll guard and never reuses last voltage") {fixture::isolated([&] {
    fixture::reset();power::Reader r;ready(r);REQUIRE(r.read().valid);
    fixture::hw.tick=0;fixture::hw.conversion_after=-1;
    auto s=r.read();invalid(s,Status::POLL_LIMIT);CHECK(fixture::hw.conversion_polls<=4096U);
    CHECK(fixture::hw.accesses<1500000U);CHECK(fixture::hw.data_reads==1);noMoreIo(r,s.shutdown);

});}
TEST_CASE("B5 unsigned timer wrap works during setup and successful conversion") {fixture::isolated([&] {
    fixture::reset();fixture::hw.now=0xfffffffcU;power::Reader r;ready(r);
    fixture::hw.now=0xfffffffeU;auto s=r.read();REQUIRE(s.valid);
    CHECK(s.started_us==0xfffffffeU);CHECK(s.completed_us<s.started_us);CHECK(s.completed_us-s.started_us<100U);

});}
TEST_CASE("B5 all setup success fault and latched operations allocate nothing") {fixture::isolated([&] {
    fixture::reset();power::Reader r;
    power::InitResult b;power::Sample good,bad;
    {fixture::AllocationGuard guard;b=r.begin();good=r.read();fixture::hw.sample=0xffffffffU;bad=r.read();r.read();r.begin();}
    CHECK(b.ready);CHECK(good.valid);CHECK_FALSE(bad.valid);CHECK(fixture::hw.allocations==0);

});}

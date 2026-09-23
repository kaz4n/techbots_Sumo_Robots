// Tests the frozen D086 fixed A0/A1 profile through its public native interface.
// Raw channel identity and source sequence must never be inferred from cached data.
// Actual power.cpp is compiled opaquely against the existing installed-shaped fixture.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
#include <cstddef>
#include <type_traits>
using namespace fixture;
using power::Status;using power::Shutdown;
namespace {
unsigned io(){return hw.accesses+hw.micros_calls+hw.clock_on+hw.clock_rate+hw.ready_reads;}
void pairReady(power::Reader& r){const auto b=r.beginWithButtons();REQUIRE(b.ready);REQUIRE(b.status==Status::OK);}
void noButton(const power::ButtonSample& s,Status status){CHECK(s.status==status);CHECK_FALSE(s.valid);CHECK(s.raw==0);CHECK(s.sequence==0);}
unsigned countWrites(const volatile Reg* r){unsigned n=0;for(unsigned i=0;i<hw.writes&&i<hw.trace.size();++i)if(hw.trace[i].address==reinterpret_cast<std::uintptr_t>(r))++n;return n;}
}
TEST_CASE("B5 B6 D086 old public ABI statuses and member signatures remain compatible") {
 static_assert(std::is_same<decltype(&power::Reader::begin),power::InitResult(power::Reader::*)()>::value);
 static_assert(std::is_same<decltype(&power::Reader::read),power::Sample(power::Reader::*)()>::value);
 static_assert(sizeof(power::Sample)==20&&offsetof(power::Sample,voltage_v)==12&&offsetof(power::Sample,valid)==16);
 static_assert(sizeof(power::ButtonSample)==20&&offsetof(power::ButtonSample,sequence)==12);
 const Status old[]={Status::OK,Status::NOT_INITIALIZED,Status::ALREADY_STARTED,Status::INVALID_CONFIG,Status::OWNERSHIP,Status::REGULATOR_TIMEOUT,Status::CALIBRATION_TIMEOUT,Status::ENABLE_TIMEOUT,Status::CONVERSION_TIMEOUT,Status::POLL_LIMIT,Status::READBACK,Status::OVERRUN,Status::INVALID_DATA,Status::FAULT_LATCHED,Status::NOT_ENABLED};
 for(unsigned i=0;i<15;++i)CHECK(static_cast<unsigned>(old[i])==i);
}
TEST_CASE("B5 B6 D086 construction uninitialized calls and repeated begin are inert") {
 isolated([]{reset();unsigned before_destruction=0;{power::Reader r;CHECK(io()==0);const auto b=r.readButtons();noButton(b,Status::NOT_INITIALIZED);CHECK(b.started_us==0);CHECK(b.completed_us==0);CHECK(io()==0);pairReady(r);const auto before=io();CHECK(r.begin().status==Status::ALREADY_STARTED);CHECK(r.beginWithButtons().status==Status::ALREADY_STARTED);CHECK(io()==before);before_destruction=io();}CHECK(io()==before_destruction);});
}
TEST_CASE("B5 B6 D086 battery-only owner neither requires PA5 DAC2 nor upgrades its profile") {
 isolated([]{reset();GPIOA->MODER.value&=~(3U<<10);GPIOA->PUPDR.value|=3U<<10;GPIOA->LCKR.value|=1U<<5;DAC1->CR.value|=DAC_CR_EN2|DAC_CR_CEN2|DAC_CR_TEN2|DAC_CR_DMAEN2|DAC_CR_WAVE2|DAC_CR_DMAUDRIE2;DAC1->MCR.value=0xffffffffU;power::Reader r;REQUIRE(r.begin().ready);CHECK(ADC1->SMPR2.value==0);CHECK(ADC1->PCSEL.value==0x200);const auto n=io();noButton(r.readButtons(),Status::NOT_ENABLED);CHECK(io()==n);CHECK(r.beginWithButtons().status==Status::ALREADY_STARTED);CHECK(io()==n);CHECK(r.read().valid);noButton(r.readButtons(),Status::NOT_ENABLED);});
}
TEST_CASE("B5 B6 D086 pair sets exact channel modes preserving PA5 and all unrelated pad fields") {
 isolated([]{reset();GPIOA->MODER.value=(0xffffffffU&~(3U<<12))|(1U<<12);GPIOA->PUPDR.value=2U<<12;const auto mode=GPIOA->MODER.value;const auto pull=GPIOA->PUPDR.value;DAC1->MCR.value=0x10000005U;power::Reader r;pairReady(r);CHECK(ADC1->SMPR1.value==(7U<<27));CHECK(ADC1->SMPR2.value==7);CHECK(ADC1->PCSEL.value==0x600);CHECK(ADC1->SQR1.value==0x240);CHECK((ADC1->CFGR2.value&ADC_CFGR2_LFTRIG)!=0);CHECK(hw.cal_count==1);CHECK(hw.enable_count==1);for(unsigned i=0;i<hw.writes&&i<hw.trace.size();++i){if(hw.trace[i].address==reinterpret_cast<std::uintptr_t>(&GPIOA->MODER))CHECK(hw.trace[i].value==mode);if(hw.trace[i].address==reinterpret_cast<std::uintptr_t>(&GPIOA->PUPDR))CHECK(hw.trace[i].value==pull);}CHECK(countWrites(&GPIOA->LCKR)==0);CHECK(countWrites(&DAC1->CR)==0);CHECK(countWrites(&DAC1->MCR)==0);CHECK(DAC1->MCR.value==0x10000005U);CHECK(hw.start_count==0);CHECK(hw.command_errors==0);});
}
TEST_CASE("B5 B6 D086 alternating ranks publish channel-specific raw values and button-only sequence") {
 isolated([]{reset();hw.samples_by_rank=true;power::Reader r;pairReady(r);const unsigned channels[]={9,10,10,9,9,10,9,10};unsigned sequence=0;unsigned previous=9;
  for(unsigned index=0;index<8;++index){const auto rank=channels[index];hw.battery_sample=1000+index;hw.button_sample=12000+index;clearTrace();const auto starts=hw.start_count;const auto reads=hw.data_reads;const auto rank_writes=hw.rank_writes;
   if(rank==10){const auto s=r.readButtons();CHECK(s.valid);CHECK(s.status==Status::OK);CHECK(s.raw==12000+index);CHECK(s.sequence==++sequence);CHECK(s.completed_us-s.started_us<100);}
   else {const auto s=r.read();CHECK(s.valid);CHECK(s.status==Status::OK);CHECK(s.raw==1000+index);CHECK(s.voltage_v>0);CHECK(s.completed_us-s.started_us<100);}
   CHECK(ADC1->SQR1.value==(rank<<6));CHECK(hw.rank_writes-rank_writes==(rank!=previous?1:0));CHECK(hw.start_count-starts==1);CHECK(hw.data_reads-reads==1);CHECK(hw.command_errors==0);CHECK(hw.cal_count==1);CHECK(hw.enable_count==1);CHECK(hw.stop_count==0);CHECK(hw.disable_count==0);CHECK(countWrites(&ADC1->SMPR2)==0);CHECK(countWrites(&ADC1->PCSEL)==0);previous=rank;
  }
 });
}
TEST_CASE("B6 D086 button raw endpoints are valid and equal values remain distinct observations") {
 isolated([]{reset();hw.samples_by_rank=true;power::Reader r;pairReady(r);unsigned sequence=0;for(auto value:{0U,0U,16383U,16383U,1U,8192U}){hw.button_sample=value;const auto s=r.readButtons();CHECK(s.valid);CHECK(s.raw==value);CHECK(s.sequence==++sequence);CHECK(hw.data_reads==sequence);}CHECK(hw.cal_count==1);});
 for(auto value:{16384U,65535U,0x10000U,0xffffffffU})isolated([=]{reset();hw.samples_by_rank=true;hw.button_sample=value;power::Reader r;pairReady(r);const auto s=r.readButtons();noButton(s,Status::INVALID_DATA);CHECK(s.shutdown==Shutdown::DISABLED);CHECK(s.completed_us!=0);const auto n=io();noButton(r.readButtons(),Status::FAULT_LATCHED);CHECK(r.read().status==Status::FAULT_LATCHED);CHECK(io()==n);});
}
TEST_CASE("B5 B6 D086 one boot-lifetime claim covers both API profiles and faults") {
 for(bool buttons:{false,true})isolated([=]{reset();power::Reader first;REQUIRE((buttons?first.beginWithButtons():first.begin()).ready);power::Reader second;const auto n=hw.writes;CHECK(second.beginWithButtons().status==Status::OWNERSHIP);CHECK(hw.writes==n);first.read();hw.sample=0xffffffffU;CHECK(first.read().status==Status::INVALID_DATA);const auto before=io();CHECK(first.begin().status==Status::ALREADY_STARTED);CHECK(first.beginWithButtons().status==Status::ALREADY_STARTED);noButton(first.readButtons(),Status::FAULT_LATCHED);CHECK(first.read().status==Status::FAULT_LATCHED);CHECK(io()==before);});
}
TEST_CASE("B5 B6 D086 actual pair setup alternating reads and destruction allocate nothing") {
 isolated([]{reset();bool good=true;unsigned allocations;{AllocationGuard guard;power::Reader r;good&=r.beginWithButtons().ready;for(unsigned i=0;i<100;++i){good&=r.read().valid;const auto s=r.readButtons();good&=s.valid&&s.sequence==i+1;}allocations=hw.allocations;}CHECK(good);CHECK(allocations==0);CHECK(hw.cal_count==1);CHECK(hw.enable_count==1);CHECK(hw.command_errors==0);});
}

// Covers D086 single-conversion deadlines, complete flags and shared fault lifetime.
// Switching, final data validation and cleanup belong to the same acceptance budget.
// Frozen clocks and modulo wrap are driven by independent native event hooks.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include <cstdint>
#define private public
#include "hal/power.h"
#undef private
using namespace fixture;
using power::Status;using power::Shutdown;
namespace {
Point at;std::uint32_t anchor,elapsed;bool injected;
void late(Point p,std::uintptr_t){if(p==at&&!injected){injected=true;hw.now=anchor+elapsed;hw.tick=0;}}
bool wait_for_cleanup,cleanup_seen;
void guardCost(Point p,std::uintptr_t address){
 if(p==Point::EOS_CLEAR)cleanup_seen=true;
 if(p==Point::ACCESS&&address==reinterpret_cast<std::uintptr_t>(&DAC1->MCR)&&
    (!wait_for_cleanup||cleanup_seen)&&!injected){injected=true;hw.now=anchor+100;hw.tick=0;}
}
void zero(const power::ButtonSample& s,Status status){CHECK_FALSE(s.valid);CHECK(s.status==status);CHECK(s.raw==0);CHECK(s.sequence==0);}
void sharedLatch(power::Reader& r,Shutdown expected){clearTrace();auto a=r.read();auto b=r.readButtons();CHECK(a.status==Status::FAULT_LATCHED);zero(b,Status::FAULT_LATCHED);CHECK(a.shutdown==expected);CHECK(b.shutdown==expected);CHECK(hw.accesses==0);CHECK(hw.micros_calls==0);CHECK(hw.ready_reads==0);}
}
TEST_CASE("B6 D086 exact 99us acceptance and 100us failure include switching data and EOS cleanup") {
 for(auto point:{Point::RANK_AFTER,Point::START,Point::DATA,Point::EOS_CLEAR})for(unsigned duration:{99U,100U,101U})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);at=point;anchor=hw.now;elapsed=duration;injected=false;hw.hook=late;const auto s=r.readButtons();hw.hook=nullptr;CHECK(injected);CHECK(s.started_us==anchor);if(duration<100){CHECK(s.valid);CHECK(s.completed_us-s.started_us==99);CHECK(s.sequence==1);}else{zero(s,Status::CONVERSION_TIMEOUT);CHECK(s.completed_us-s.started_us>=100);sharedLatch(r,s.shutdown);}CHECK(hw.command_errors==0);});
}
TEST_CASE("B6 D086 rank switch elapsed time consumes the original read budget") {
 for(unsigned duration:{0U,100U})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);hw.rank_write_us=duration;const auto s=r.readButtons();if(duration==0)CHECK(s.valid);else{zero(s,Status::CONVERSION_TIMEOUT);CHECK(hw.start_count==0);CHECK(s.shutdown==Shutdown::DISABLED);}CHECK(hw.cal_count==1);CHECK(hw.enable_count==1);});
}
TEST_CASE("B6 D086 stale flags cannot masquerade as the selected channel conversion") {
 for(bool frozen:{false,true})isolated([=]{reset();hw.samples_by_rank=true;hw.button_sample=7654;power::Reader r;REQUIRE(r.beginWithButtons().ready);REQUIRE(r.read().valid);ADC1->ISR.value|=ADC_ISR_EOC|ADC_ISR_EOS|ADC_ISR_OVR|ADC_ISR_EOSMP;ADC1->DR.value=1;hw.freeze_stale=frozen;const auto reads=hw.data_reads;const auto starts=hw.start_count;const auto s=r.readButtons();if(frozen){zero(s,Status::READBACK);CHECK(hw.start_count==starts);CHECK(hw.data_reads==reads);sharedLatch(r,s.shutdown);}else{CHECK(s.valid);CHECK(s.raw==7654);CHECK(s.sequence==1);CHECK(hw.data_reads==reads+1);CHECK(hw.start_count==starts+1);}});
}
TEST_CASE("B6 D086 both fresh flags and bounded raw read are mandatory for selected A1") {
 for(std::uint32_t flags:std::array<std::uint32_t,4>{0U,ADC_ISR_EOC,ADC_ISR_EOS,ADC_ISR_EOC|ADC_ISR_EOS|ADC_ISR_OVR})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);hw.completion_flags=flags;const auto s=r.readButtons();zero(s,(flags&ADC_ISR_OVR)?Status::OVERRUN:Status::CONVERSION_TIMEOUT);CHECK(hw.data_reads==0);CHECK(hw.start_count==1);sharedLatch(r,s.shutdown);});
}
TEST_CASE("B6 D086 shared latch keeps first failure status and bounded command-safe shutdown") {
 for(unsigned kind=0;kind<3;++kind)isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);hw.conversion_after=-1;if(kind==1)hw.stop_after=-1;if(kind==2)hw.disable_after=-1;const auto s=r.readButtons();zero(s,Status::CONVERSION_TIMEOUT);CHECK(s.shutdown==(kind?Shutdown::UNCONFIRMED:Shutdown::DISABLED));CHECK(hw.stop_count==1);CHECK(hw.disable_count==(kind==1?0:1));CHECK(hw.command_errors==0);CHECK(hw.now-s.started_us<250);CHECK(ADC1->SQR1.value==(10U<<6));CHECK(ADC1->PCSEL.value==0x600);CHECK(ADC1->SMPR2.value==7);sharedLatch(r,s.shutdown);});
}
TEST_CASE("B6 D086 frozen runtime clock has finite count while ordinary wrapping clock succeeds") {
 isolated([]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);REQUIRE(r.readButtons().valid);hw.tick=0;hw.conversion_after=-1;const auto before=hw.data_reads;const auto s=r.readButtons();zero(s,Status::POLL_LIMIT);CHECK(hw.conversion_polls<=4096);CHECK(hw.data_reads==before);CHECK(hw.accesses<1500000);sharedLatch(r,s.shutdown);});
 isolated([]{reset();hw.now=0xfffffffcU;power::Reader r;REQUIRE(r.beginWithButtons().ready);hw.now=0xfffffffeU;const auto s=r.readButtons();CHECK(s.valid);CHECK(s.started_us==0xfffffffeU);CHECK(s.completed_us<s.started_us);CHECK(s.completed_us-s.started_us<100);CHECK(s.sequence==1);});
}
TEST_CASE("B6 D086 seeded successful-button sequence wraps through zero independently from battery") {
 isolated([]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);REQUIRE(r.readButtons().valid);r.button_sequence_=0xfffffffeU;CHECK(r.read().valid);CHECK(r.readButtons().sequence==0xffffffffU);CHECK(r.read().valid);const auto s=r.readButtons();CHECK(s.valid);CHECK(s.sequence==0U);CHECK(r.readButtons().sequence==1U);});
}
TEST_CASE("B6 D086 initial and final native ownership guard cost belongs to the conversion deadline") {
 for(bool final_guard:{false,true})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);wait_for_cleanup=final_guard;cleanup_seen=false;injected=false;anchor=hw.now;hw.hook=guardCost;const auto s=r.readButtons();hw.hook=nullptr;CHECK(injected);zero(s,Status::CONVERSION_TIMEOUT);CHECK(s.completed_us-s.started_us>=100);sharedLatch(r,s.shutdown);});
}

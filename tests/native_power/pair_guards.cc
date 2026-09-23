// Tests D086's additive PA5/DAC2 guards and narrow tracked-rank ownership.
// A register mismatch is never permission to repair another peripheral or pad.
// Forked boots exercise independent admission, runtime and partial-write failures.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
#include <array>
using namespace fixture;
using power::Status;using power::Shutdown;
namespace {
struct Change{volatile Reg* reg;std::uint32_t bits;bool clear;};
std::array<Change,15> changes(){return {{
 {&GPIOA->LCKR,1U<<5,false},{&GPIOA->LCKR,1U<<4,false},
 {&GPIOA->MODER,3U<<10,true},{&GPIOA->PUPDR,1U<<10,false},{&GPIOA->PUPDR,2U<<10,false},
 {&DAC1->CR,DAC_CR_EN2,false},{&DAC1->CR,DAC_CR_CEN2,false},{&DAC1->CR,DAC_CR_TEN2,false},
 {&DAC1->CR,DAC_CR_DMAEN2,false},{&DAC1->CR,DAC_CR_DMAUDRIE2,false},
 {&DAC1->CR,DAC_CR_WAVE2_0,false},{&DAC1->CR,DAC_CR_WAVE2_1,false},
 {&DAC1->MCR,DAC_MCR_MODE2_0,false},{&DAC1->MCR,DAC_MCR_MODE2_1,false},{&DAC1->MCR,DAC_MCR_MODE2_2,false}}};}
void apply(const Change& c){if(c.clear)c.reg->value&=~c.bits;else c.reg->value|=c.bits;}
void latched(power::Reader& r,Shutdown expected){clearTrace();const auto b=r.readButtons();CHECK(b.status==Status::FAULT_LATCHED);CHECK(b.shutdown==expected);CHECK_FALSE(b.valid);CHECK(b.raw==0);CHECK(b.sequence==0);CHECK(b.started_us==0);CHECK(b.completed_us==0);CHECK(r.read().status==Status::FAULT_LATCHED);CHECK(hw.accesses==0);CHECK(hw.micros_calls==0);CHECK(hw.ready_reads==0);}
Point loss_point;unsigned loss_kind,writes_at_loss;bool lost;
void lose(Point p,std::uintptr_t){if(p!=loss_point||lost)return;lost=true;if(loss_kind==0)DAC1->CR.value|=DAC_CR_EN2;if(loss_kind==1)GPIOA->LCKR.value|=1U<<5;if(loss_kind==2)ADC1->SQR1.value=11U<<6;writes_at_loss=hw.writes;}
std::uintptr_t setup_address;std::uint32_t setup_replacement;bool setup_changed;
void changeSetup(Point p,std::uintptr_t address){if(p!=Point::ACCESS||address!=setup_address||setup_changed)return;auto* r=reinterpret_cast<volatile Reg*>(address);if(r->value==0)return;r->value=setup_replacement;setup_changed=true;}
void readyLostInSetup(Point p,std::uintptr_t address){if(p!=Point::ACCESS||address!=setup_address||setup_changed)return;auto* r=reinterpret_cast<volatile Reg*>(address);if(r->value==0)return;ADC1->ISR.value&=~ADC_ISR_ADRDY;setup_changed=true;writes_at_loss=hw.writes;}
}
TEST_CASE("B6 D086 each new pad and DAC2 guard rejects admission before a claim write") {
 for(unsigned index=0;index<15;++index)isolated([=]{reset();const auto c=changes()[index];apply(c);power::Reader r;const auto b=r.beginWithButtons();CHECK(b.status==Status::OWNERSHIP);CHECK_FALSE(b.ready);CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(hw.writes==0);CHECK(hw.clock_on==0);});
 for(unsigned mode:{1U,2U})isolated([=]{reset();GPIOA->MODER.value=(GPIOA->MODER.value&~(3U<<10))|(mode<<10);power::Reader r;CHECK(r.beginWithButtons().status==Status::OWNERSHIP);CHECK(hw.writes==0);});
 isolated([]{reset();gpio_config.port_pin_mask&=~(1U<<5);power::Reader r;CHECK_FALSE(r.beginWithButtons().ready);CHECK(hw.writes==0);});
}
TEST_CASE("B5 B6 D086 all new guards protect both read methods after the pair is configured") {
 for(unsigned index=0;index<15;++index)for(bool buttons:{false,true})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);apply(changes()[index]);clearTrace();const auto status=buttons?r.readButtons().status:r.read().status;CHECK(status==Status::OWNERSHIP);CHECK(hw.writes==0);CHECK(hw.start_count==0);latched(r,Shutdown::UNCONFIRMED);});
}
TEST_CASE("B5 B6 D086 wrong externally selected rank is rejected rather than restored") {
 for(bool button_rank:{false,true})for(bool buttons:{false,true})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);if(button_rank)REQUIRE(r.readButtons().valid);ADC1->SQR1.value=(button_rank?9U:10U)<<6;clearTrace();const auto status=buttons?r.readButtons().status:r.read().status;CHECK(status==Status::OWNERSHIP);CHECK(hw.writes==0);latched(r,Shutdown::UNCONFIRMED);});
}
TEST_CASE("B5 B6 D086 exact fixed SMPR2 PCSEL SQR1 and idle state remain owned") {
 for(unsigned field=0;field<12;++field)isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);switch(field){case 0:ADC1->SMPR2.value=0;break;case 1:ADC1->SMPR2.value|=1U<<3;break;case 2:ADC1->PCSEL.value=0x200;break;case 3:ADC1->PCSEL.value|=1U<<11;break;case 4:ADC1->SQR1.value|=1;break;case 5:ADC1->SQR1.value|=1U<<12;break;case 6:ADC1->CR.value|=ADC_CR_ADSTART;break;case 7:ADC1->CR.value|=ADC_CR_JADSTART;break;case 8:ADC1->CR.value|=ADC_CR_ADSTP;break;case 9:ADC1->CR.value|=ADC_CR_ADDIS;break;case 10:ADC1->CR.value|=ADC_CR_ADCAL;break;case 11:ADC1->ISR.value&=~ADC_ISR_ADRDY;break;}clearTrace();const auto s=r.readButtons();CHECK_FALSE(s.valid);CHECK(s.status==Status::OWNERSHIP);CHECK(s.shutdown==Shutdown::UNCONFIRMED);CHECK(hw.writes==0);});
}
TEST_CASE("B5 B6 D086 ignored tracked rank switch permits bounded disable without restoration") {
 for(bool reverse:{false,true})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);if(reverse)REQUIRE(r.readButtons().valid);hw.rank_write_effect=false;clearTrace();const auto old=ADC1->SQR1.value;const auto start_count=hw.start_count;const auto status=reverse?r.read().status:r.readButtons().status;CHECK(status==Status::READBACK);CHECK(ADC1->SQR1.value==old);CHECK(hw.start_count==start_count);CHECK(hw.stop_count==0);CHECK(hw.disable_count==1);CHECK(hw.command_errors==0);latched(r,Shutdown::DISABLED);});
}
TEST_CASE("B5 B6 D086 partial unrecognized rank switch never authorizes blind cleanup") {
 for(std::uint32_t extra:{1U,1U<<12,1U<<31})isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);hw.rank_write_xor=extra;clearTrace();const auto s=r.readButtons();CHECK_FALSE(s.valid);CHECK((s.status==Status::OWNERSHIP||s.status==Status::READBACK));CHECK(s.shutdown==Shutdown::UNCONFIRMED);CHECK(hw.writes==1);CHECK(hw.start_count==0);CHECK(hw.disable_count==0);CHECK(hw.stop_count==0);CHECK(ADC1->SQR1.value==((10U<<6)^extra));latched(r,Shutdown::UNCONFIRMED);});
}
TEST_CASE("B6 D086 every switch and final readback boundary observes a newly conflicting owner") {
 for(auto point:{Point::RANK_AFTER,Point::START,Point::DATA,Point::EOS_CLEAR})for(unsigned kind=0;kind<3;++kind)isolated([=]{reset();power::Reader r;REQUIRE(r.beginWithButtons().ready);loss_point=point;loss_kind=kind;lost=false;hw.hook=lose;const auto s=r.readButtons();hw.hook=nullptr;CHECK(lost);CHECK_FALSE(s.valid);CHECK(s.status==((point==Point::RANK_AFTER&&kind==2)?Status::READBACK:Status::OWNERSHIP));CHECK(s.shutdown==Shutdown::UNCONFIRMED);CHECK(hw.writes==writes_at_loss);latched(r,Shutdown::UNCONFIRMED);});
}
TEST_CASE("B6 D086 partial added setup fields only admit the exact tracked old or requested word") {
 for(unsigned word=0;word<2;++word)for(bool foreign:{false,true})isolated([=]{reset();setup_address=reinterpret_cast<std::uintptr_t>(word==0?&ADC1->SMPR2:&ADC1->PCSEL);setup_replacement=foreign?1U:0U;setup_changed=false;hw.hook=changeSetup;power::Reader r;const auto result=r.beginWithButtons();hw.hook=nullptr;CHECK(setup_changed);CHECK_FALSE(result.ready);CHECK((result.status==Status::READBACK||result.status==Status::OWNERSHIP));CHECK(result.shutdown==(foreign?Shutdown::UNCONFIRMED:Shutdown::DISABLED));CHECK(hw.command_errors==0);latched(r,result.shutdown);power::Reader second;clearTrace();CHECK(second.beginWithButtons().status==Status::OWNERSHIP);CHECK(hw.writes==0);});
}
TEST_CASE("B6 D086 ADRDY loss during each enabled setup mode transition prevents publication or cleanup") {
 for(unsigned word=0;word<4;++word)isolated([=]{reset();volatile Reg* words[]={&ADC1->SMPR1,&ADC1->SMPR2,&ADC1->PCSEL,&ADC1->SQR1};setup_address=reinterpret_cast<std::uintptr_t>(words[word]);setup_changed=false;hw.hook=readyLostInSetup;power::Reader r;const auto result=r.beginWithButtons();hw.hook=nullptr;CHECK(setup_changed);CHECK_FALSE(result.ready);CHECK(result.status==Status::OWNERSHIP);CHECK(result.shutdown==Shutdown::UNCONFIRMED);CHECK(hw.writes==writes_at_loss);latched(r,result.shutdown);});
}

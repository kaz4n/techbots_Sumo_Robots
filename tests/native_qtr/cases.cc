// Exercises D085 native RC timing through the frozen public interface.
// Assertions derive from the contract and source-audited native ABI only.
// Actual line_qtr.cpp is linked opaquely under independently controlled hardware.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/line_qtr.h"
#include "config.h"
#include <type_traits>
using namespace fixture;
using namespace line_qtr;
namespace {
void begun(Reader& r){REQUIRE(r.begin(true)==Status::OK);REQUIRE(r.report().phase==Phase::IDLE);}
void charging(Reader& r){begun(r);REQUIRE(r.start()==Status::OK);REQUIRE(r.report().phase==Phase::CHARGING);}
void released(Reader& r){charging(r);for(auto& v:hw.values)v=1;hw.now=r.report().drive_completed_us+11U;REQUIRE(r.advance().phase==Phase::DISCHARGING);}
void neutralBank(){for(unsigned p=0;p<4;++p){CHECK(mode(p)==0);CHECK(((port(p)->PUPDR.value>>(padBit(p)*2U))&3U)==0);}}
void latched(Reader& r,Status why){const auto s=r.report();CHECK(s.phase==Phase::FAULT);CHECK(s.status==why);CHECK_FALSE(s.valid);const auto n=hw.config_calls;r.start();r.advance();r.cancel();CHECK(hw.config_calls==n);CHECK_FALSE(r.report().valid);}
}
TEST_CASE("B2 D085 construction no grant one attempt and uninitialized calls are inert") {
 static_assert(!std::is_copy_constructible<Reader>::value);static_assert(!std::is_copy_assignable<Reader>::value);
 isolated([]{reset();{Reader r;CHECK(hw.reg_reads==0);CHECK(r.start()==Status::NOT_INITIALIZED);CHECK_FALSE(r.advance().valid);r.cancel();CHECK(hw.config_calls==0);CHECK(r.begin()==Status::OWNERSHIP);CHECK(r.begin(true)==Status::ALREADY_STARTED);}CHECK(hw.config_calls==0);CHECK(hw.set_calls==0);});
}
TEST_CASE("B2 D085 boot lifetime claim survives complete fault and owner destruction") {
 isolated([]{reset();{Reader r;begun(r);Reader second;CHECK(second.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==4);}Reader third;CHECK(third.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==4);});
 isolated([]{reset();hw.configure_status[0]=-7;Reader r;CHECK(r.begin(true)!=Status::OK);Reader second;auto n=hw.config_calls;CHECK(second.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==n);});
}
TEST_CASE("B2 D085 denied preflight does not claim bank for an independently admitted owner") {
 isolated([]{reset();Reader denied;CHECK(denied.begin(false)==Status::OWNERSHIP);Reader accepted;begun(accepted);});
}
TEST_CASE("B2 D085 granted neutralization accepts every INPUT ANALOG fingerprint and scoped AF0") {
 for(unsigned p=0;p<4;++p)for(unsigned m:{0U,3U})isolated([=]{reset();setMode(p,m);setField(port(p)->PUPDR,2*padBit(p),3);setField(port(p)->OSPEEDR,2*padBit(p),3);port(p)->OTYPER.value|=1U<<padBit(p);setField(port(p)->AFR[padBit(p)/8],(padBit(p)%8)*4,7,4);Reader r;begun(r);neutralBank();CHECK(((port(p)->AFR[padBit(p)/8].value>>((padBit(p)%8)*4))&15U)==7U);});
 for(unsigned p:{0U,3U})isolated([=]{reset();setMode(p,2);Reader r;begun(r);neutralBank();});
}
TEST_CASE("B2 D085 initial output other alternate trace clocks reset and single locks reject without writes") {
 for(unsigned p=0;p<4;++p)for(unsigned kind=0;kind<4;++kind)isolated([=]{reset();if(kind==0)setMode(p,1);if(kind==1){setMode(p,2);setField(port(p)->AFR[padBit(p)/8],(padBit(p)%8)*4,1,4);}if(kind==2)port(p)->LCKR.value=1U<<padBit(p);if(kind==3){setMode(p,2);if(p==0||p==3)setField(port(p)->AFR[0],padBit(p)*4,15,4);}Reader r;CHECK(r.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==0);CHECK(hw.reg_writes==0);});
 for(unsigned kind=0;kind<5;++kind)isolated([=]{reset();if(kind==0)RCC->AHB2ENR1.value&=~RCC_AHB2ENR1_GPIOAEN;if(kind==1)RCC->AHB2ENR1.value&=~RCC_AHB2ENR1_GPIOBEN;if(kind==2)RCC->AHB2RSTR1.value|=RCC_AHB2RSTR1_GPIOARST;if(kind==3)RCC->AHB2RSTR1.value|=RCC_AHB2RSTR1_GPIOBRST;if(kind==4)DBGMCU->CR.value=DBGMCU_CR_TRACE_IOEN;Reader r;CHECK(r.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==0);CHECK(hw.gated_reads==0);CHECK(hw.reg_writes==0);});
}
TEST_CASE("B2 D085 every selected EXTI and NVIC bit rejects without clearing foreign state") {
 for(unsigned field=0;field<7;++field)for(unsigned n:{2U,3U,4U,12U})isolated([=]{reset();volatile Reg* fields[]={&EXTI->IMR1,&EXTI->EMR1,&EXTI->RTSR1,&EXTI->FTSR1,&EXTI->SWIER1,&EXTI->RPR1,&EXTI->FPR1};fields[field]->value=1U<<n;Reader r;CHECK(r.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==0);CHECK(fields[field]->value==(1U<<n));CHECK(hw.reg_writes==0);});
 for(unsigned field=0;field<3;++field)for(unsigned n:{13U,14U,15U,23U})isolated([=]{reset();auto* f=field==0?&hw.irq_enabled:field==1?&hw.irq_pending:&hw.irq_active;*f=1U<<n;Reader r;CHECK(r.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==0);CHECK(*f==(1U<<n));});
 isolated([]{reset();EXTI->EXTICR[0].value=0x01010000U;EXTI->EXTICR[1].value=1;EXTI->EXTICR[3].value=0;EXTI->IMR1.value=1U<<7;hw.irq_enabled=1U<<9;Reader r;begun(r);CHECK(EXTI->IMR1.value==(1U<<7));CHECK(hw.reg_writes==0);});
}
TEST_CASE("B2 D085 metadata and readiness are whole-bank predicates") {
 for(unsigned d=0;d<2;++d)for(unsigned kind=0;kind<10;++kind)isolated([=]{reset();if(kind==0)fixture_devices[d].config=nullptr;if(kind==1)fixture_devices[d].data=nullptr;if(kind==2)fixture_devices[d].api=nullptr;if(kind==3)fixture_devices[d].state=nullptr;if(kind==4)hw.ready[d]=false;if(kind==5)apis[d].pin_configure=nullptr;if(kind==6)apis[d].port_get_raw=nullptr;if(kind==7)apis[d].port_set_bits_raw=nullptr;if(kind==8)apis[d].port_clear_bits_raw=nullptr;if(kind==9)configs[d].port_pin_mask=0;Reader r;CHECK(r.begin(true)!=Status::OK);CHECK(hw.config_calls==0);CHECK(hw.reg_writes==0);});
}
TEST_CASE("B2 D085 native HIGH configuration release guard and replay identity") {
 isolated([]{reset();Reader r;charging(r);const auto s=r.report();CHECK(s.sequence==1);CHECK(hw.config_calls==8);for(unsigned i=4;i<8;++i){CHECK(hw.operations[i].flags==GPIO_OUTPUT_HIGH);CHECK(mode(i-4)==1);CHECK((port(i-4)->ODR.value&(1U<<padBit(i-4)))!=0);}CHECK(r.start()==Status::BUSY);CHECK(r.report().sequence==s.sequence);hw.now=s.drive_completed_us+10;CHECK(r.advance().phase==Phase::CHARGING);CHECK(hw.config_calls==8);hw.now=s.drive_completed_us+11;const auto done=r.advance();CHECK(done.valid);CHECK(done.phase==Phase::COMPLETE);CHECK(done.released_mask==15);CHECK(done.low_mask==15);CHECK(done.timeout_mask==0);CHECK(done.cleanup.attempted_mask==15);neutralBank();CHECK(hw.set_calls==0);CHECK(hw.reg_writes==0);CHECK(hw.invalid_ops==0);CHECK(r.report().completed_us==done.completed_us);r.cancel();CHECK(r.report().valid);hw.now=s.started_us+1999;CHECK(r.start()==Status::NOT_DUE);CHECK(r.report().sequence==1);hw.now=s.started_us+2000;CHECK(r.start()==Status::OK);CHECK(r.report().sequence==2);CHECK_FALSE(r.report().valid);CHECK(r.report().low_mask==0);});
}
TEST_CASE("B2 D085 all sixteen raw patterns are sampled once and completed pads stay complete") {
 for(unsigned mask=0;mask<16;++mask)isolated([=]{reset();Reader r;charging(r);for(unsigned p=0;p<4;++p)hw.values[p]=(mask>>p)&1;hw.now=r.report().drive_completed_us+11;auto s=r.advance();CHECK(s.low_mask==(15U^mask));CHECK(s.high_mask==mask);unsigned gets[4];for(unsigned p=0;p<4;++p)gets[p]=hw.gets[p];hw.now+=200;for(auto& v:hw.values)v=0;if(mask)s=r.advance();CHECK(s.valid);CHECK(s.low_mask==15);for(unsigned p=0;p<4;++p)CHECK(hw.gets[p]==gets[p]+((mask>>p)&1));});
}
TEST_CASE("B2 D085 brackets preserve each release skew and exclusive first LOW endpoint") {
 isolated([]{reset();hw.configure_us=2;hw.read_us=3;Reader r;charging(r);hw.now=r.report().drive_completed_us+11;const auto s=r.advance();REQUIRE(s.valid);for(unsigned p=0;p<4;++p){const auto& a=s.pad[p];CHECK(a.release_after_us-a.release_before_us==2);CHECK(a.lower_us==0);CHECK(a.upper_us==a.first_low_after_us-a.release_before_us+1);if(p)CHECK(a.release_before_us>=s.pad[p-1].release_after_us);}CHECK(s.completed_us>=s.pad[3].first_low_after_us);});
 isolated([]{reset();Reader r;released(r);const auto a=r.report();hw.now+=299;const auto h=r.advance();for(unsigned p=0;p<4;++p){CHECK(h.pad[p].lower_us==298);CHECK(h.pad[p].last_high_before_us==hw.now);}hw.now+=5;for(auto& v:hw.values)v=0;const auto s=r.advance();REQUIRE(s.valid);for(unsigned p=0;p<4;++p){CHECK(s.pad[p].lower_us==298);CHECK(s.pad[p].upper_us==s.pad[p].first_low_after_us-a.pad[p].release_before_us+1);}});
}
TEST_CASE("B2 D085 timeout lower equality is censored and late LOW has precedence") {
 for(bool low:{false,true})isolated([=]{reset();Reader r;released(r);auto s=r.report();hw.now=s.pad[0].release_after_us+1500;CHECK_FALSE(r.advance().valid);hw.now+=1;if(low)for(auto& v:hw.values)v=0;s=r.advance();REQUIRE(s.valid);CHECK(s.low_mask==(low?15:0));CHECK(s.timeout_mask==(low?0:15));for(auto& p:s.pad){CHECK(p.lower_us==(low?1499:1500));CHECK(p.upper_us==(low?1502:0));}});
}
TEST_CASE("B2 D085 every charge pad LOW or unexpected native read fails explicitly") {
 for(unsigned p=0;p<4;++p)for(int value:{0,-5,2})isolated([=]{reset();Reader r;charging(r);hw.charge_values[p]=value;hw.now=r.report().drive_completed_us+11;r.advance();CHECK_FALSE(r.report().valid);CHECK(r.report().phase==Phase::FAULT);CHECK(r.report().status==(value==0?Status::CHARGE_LOW:Status::NATIVE_ERROR));CHECK(r.report().cleanup.attempted_mask==15);neutralBank();});
 for(unsigned p=0;p<4;++p)for(int value:{-11,2})isolated([=]{reset();Reader r;released(r);hw.values[p]=value;++hw.now;r.advance();latched(r,Status::NATIVE_ERROR);CHECK(r.report().status_by_pad[p]==value);CHECK(r.report().cleanup.attempted_mask==15);neutralBank();});
}
TEST_CASE("B2 D085 cancellation is explicit reset-only and idle cancellation preserves identity") {
 isolated([]{reset();Reader r;begun(r);const auto n=hw.config_calls;r.cancel();CHECK(hw.config_calls==n);CHECK(r.report().phase==Phase::IDLE);CHECK(r.start()==Status::OK);const auto s=r.cancel();CHECK(s.cleanup.attempted_mask==15);neutralBank();latched(r,Status::CANCELLED);});
}
TEST_CASE("B2 D085 native operations never allocate or write peripheral ownership registers") {
 isolated([]{reset();unsigned allocation_count;{AllocationGuard guard;Reader r;r.begin(true);r.start();hw.now+=11;r.advance();r.report();r.cancel();allocation_count=hw.allocations;}CHECK(allocation_count==0);CHECK(hw.reg_writes==0);CHECK(hw.set_calls==0);});
}

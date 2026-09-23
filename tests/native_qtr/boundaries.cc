// Tests exact D085 deadlines, partial transitions and reset-only failure evidence.
// Private visibility is used solely to seed a generation-wrap boundary after completion.
// No assertion or expected result is derived from a production implementation body.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include <cstdint>
#define private public
#include "hal/line_qtr.h"
#undef private
#include "config.h"
using namespace fixture;
using namespace line_qtr;
namespace {
void begin(Reader& r){REQUIRE(r.begin(true)==Status::OK);}
void start(Reader& r){begin(r);REQUIRE(r.start()==Status::OK);}
void discharge(Reader& r){start(r);for(auto& v:hw.values)v=1;hw.now=r.report().drive_completed_us+11;REQUIRE(r.advance().phase==Phase::DISCHARGING);}
unsigned hook_pad=0,hook_kind=0;
bool delayed_guard=false;
void guardDelay(Point p,unsigned pad){if((p==Point::CONFIG_AFTER||p==Point::GET_AFTER)&&pad==3)delayed_guard=true;if(p==Point::ACCESS&&delayed_guard){hw.now+=100;hw.hook=nullptr;delayed_guard=false;}}
void corrupt(Point p,unsigned pad){if(p!=Point::CONFIG_AFTER||pad!=hook_pad)return;auto* g=port(pad);const auto n=padBit(pad);switch(hook_kind){case 0:setMode(pad,2);break;case 1:setField(g->PUPDR,2*n,1);break;case 2:g->OTYPER.value|=1U<<n;break;case 3:setField(g->OSPEEDR,2*n,1);break;case 4:setField(g->AFR[n/8],(n%8)*4,1,4);break;case 5:g->LCKR.value|=1U<<n;break;case 6:g->ODR.value&=~(1U<<n);break;}hw.hook=nullptr;}
void globalLoss(unsigned kind){switch(kind){case 0:RCC->AHB2ENR1.value=0;break;case 1:RCC->AHB2RSTR1.value=RCC_AHB2RSTR1_GPIOBRST;break;case 2:EXTI->IMR1.value=1U<<3;break;case 3:EXTI->RPR1.value=1U<<12;break;case 4:hw.irq_pending=1U<<14;break;case 5:EXTI->EXTICR[0].value^=1U<<24;break;case 6:DBGMCU->CR.value^=DBGMCU_CR_TRACE_CLKEN;break;}}
}
TEST_CASE("B2 D085 each partial setup charge and release failure preserves original native status") {
 for(unsigned phase=0;phase<3;++phase)for(unsigned p=0;p<4;++p)for(bool effect:{false,true})isolated([=]{reset();Reader r;const unsigned failing=phase*4+p;hw.configure_status[failing]=-17;hw.configure_effect[failing]=effect;if(phase==0)r.begin(true);else {begin(r);r.start();if(phase==2){hw.now=r.report().drive_completed_us+11;r.advance();}}const auto s=r.report();CHECK(s.phase==Phase::FAULT);CHECK(s.status==Status::NATIVE_ERROR);CHECK(s.status_by_pad[p]==-17);CHECK_FALSE(s.valid);CHECK(s.cleanup.attempted_mask==15);CHECK(s.cleanup.skipped_mask==0);for(unsigned pad=0;pad<4;++pad)CHECK(mode(pad)==0);Reader second;const auto calls=hw.config_calls;CHECK(second.begin(true)==Status::OWNERSHIP);CHECK(hw.config_calls==calls);});
}
TEST_CASE("B2 D085 every unexpected post-configure field rejects and does not blindly restore takeover") {
 for(unsigned phase=0;phase<3;++phase)for(unsigned p=0;p<4;++p)for(unsigned kind=0;kind<(phase==1?7U:6U);++kind)isolated([=]{reset();Reader r;if(phase>=1)begin(r);if(phase==2)REQUIRE(r.start()==Status::OK);hook_pad=p;hook_kind=kind;hw.hook=corrupt;if(phase==0)r.begin(true);if(phase==1)r.start();if(phase==2){hw.now=r.report().drive_completed_us+11;r.advance();}CHECK(r.report().phase==Phase::FAULT);CHECK_FALSE(r.report().valid);CHECK((r.report().cleanup.skipped_mask&(1U<<p))!=0);CHECK((r.report().cleanup.attempted_mask&(1U<<p))==0);});
}
TEST_CASE("B2 D085 global ownership loss in every live phase skips all cleanup writes") {
 for(unsigned phase=0;phase<3;++phase)for(unsigned kind=0;kind<7;++kind)isolated([=]{reset();Reader r;if(phase==0)begin(r);if(phase==1)start(r);if(phase==2)discharge(r);globalLoss(kind);const auto n=hw.config_calls;if(phase==0)r.start();else r.advance();CHECK(r.report().phase==Phase::FAULT);CHECK(r.report().status==Status::OWNERSHIP);CHECK(r.report().cleanup.skipped_mask==15);CHECK(r.report().cleanup.attempted_mask==0);CHECK(hw.config_calls==n);CHECK(hw.gated_reads==0);CHECK(hw.reg_writes==0);});
}
TEST_CASE("B2 D085 cleanup attempts all eligible pads after status failure and records each") {
 for(unsigned p=0;p<4;++p)isolated([=]{reset();Reader r;start(r);hw.configure_status[8+p]=-23;const auto s=r.cancel();CHECK(s.phase==Phase::FAULT);CHECK_FALSE(s.valid);CHECK(s.cleanup.attempted_mask==15);CHECK(s.cleanup.failed_mask==(1U<<p));CHECK(s.cleanup.status[p]==-23);CHECK(hw.config_calls==12);});
 for(unsigned p=0;p<4;++p)isolated([=]{reset();Reader r;start(r);hw.configure_effect[8+p]=false;const auto s=r.cancel();CHECK(s.cleanup.attempted_mask==15);CHECK(s.cleanup.nonneutral_mask==(1U<<p));CHECK(hw.config_calls==12);CHECK_FALSE(s.valid);});
}
TEST_CASE("B2 D085 call charge cleanup and frame budget equality always fails") {
 for(unsigned duration:{99U,100U})isolated([=]{reset();Reader r;start(r);hw.now=r.report().drive_completed_us+duration;const auto s=r.advance();CHECK(s.valid==(duration==99));if(duration==100)CHECK(s.status==Status::CHARGE_DEADLINE);});
 for(unsigned duration:{24U,25U})isolated([=]{reset();Reader r;begin(r);hw.configure_us=duration;r.start();const auto s=r.report();CHECK((s.phase==Phase::CHARGING)==(duration==24));if(duration==25)CHECK(s.status==Status::CALL_DEADLINE);});
 for(unsigned duration:{24U,25U})isolated([=]{reset();Reader r;discharge(r);hw.configure_us=duration;for(auto& v:hw.values)v=0;++hw.now;const auto s=r.advance();CHECK(s.cleanup.attempted_mask==15);CHECK(s.cleanup.completed_us-s.cleanup.started_us==4*duration);CHECK(s.cleanup.deadline_exceeded==(duration==25));CHECK(s.valid==(duration==24));});
 for(unsigned duration:{2499U,2500U})isolated([=]{reset();Reader r;discharge(r);hw.now=r.report().started_us+duration;for(auto& v:hw.values)v=0;const auto s=r.advance();CHECK(s.valid==(duration==2499));if(duration==2500)CHECK(s.status==Status::FRAME_DEADLINE);});
 isolated([]{reset();Reader r;start(r);hw.configure_us=100;const auto s=r.cancel();CHECK(s.cleanup.attempted_mask==15);CHECK(s.cleanup.deadline_exceeded);CHECK(hw.config_calls==12);CHECK_FALSE(s.valid);});
}
TEST_CASE("B2 D085 max advance frozen clock is finite and successful last call wins") {
 for(bool complete:{false,true})isolated([=]{reset();Reader r;start(r);for(auto& v:hw.values)v=1;hw.now=r.report().drive_completed_us+11;for(unsigned i=1;i<config::QTR_MAX_ADVANCES;++i){const auto s=r.advance();REQUIRE(s.phase==Phase::DISCHARGING);}if(complete)for(auto& v:hw.values)v=0;const auto s=r.advance();CHECK(s.advances==config::QTR_MAX_ADVANCES);CHECK(s.valid==complete);CHECK(s.status==(complete?Status::OK:Status::ADVANCE_LIMIT));const auto reads=hw.get_calls;r.advance();CHECK(hw.get_calls==reads);});
 isolated([]{reset();Reader r;start(r);for(unsigned i=1;i<config::QTR_MAX_ADVANCES;++i)REQUIRE(r.advance().phase==Phase::CHARGING);const auto s=r.advance();CHECK(s.status==Status::ADVANCE_LIMIT);CHECK(s.cleanup.attempted_mask==15);});
}
TEST_CASE("B2 D085 reverse half-range clocks fail while wrapping timestamps remain valid") {
 for(std::uint32_t step:{0xffffffffU,0x80000000U})isolated([=]{reset();Reader r;start(r);hw.now+=step;const auto s=r.advance();CHECK(s.phase==Phase::FAULT);CHECK(s.status==Status::TIME_ORDER);CHECK_FALSE(s.valid);});
 isolated([]{reset();hw.now=0xfffffff8U;Reader r;start(r);hw.now+=11;const auto s=r.advance();REQUIRE(s.valid);CHECK(s.started_us==0xfffffff8U);CHECK(s.completed_us==3U);CHECK(s.pad[0].upper_us==1U);hw.now=s.started_us+2000U;CHECK(r.start()==Status::OK);CHECK(r.report().sequence==2U);});
}
TEST_CASE("B2 D085 seeded generation boundary includes zero without inventing billions of frames") {
 isolated([]{reset();Reader r;start(r);hw.now+=11;REQUIRE(r.advance().valid);r.generation_=0xfffffffeU;hw.now=r.report().started_us+2000;REQUIRE(r.start()==Status::OK);CHECK(r.report().sequence==0xffffffffU);hw.now+=11;REQUIRE(r.advance().valid);hw.now=r.report().started_us+2000;REQUIRE(r.start()==Status::OK);CHECK(r.report().sequence==0U);});
}
TEST_CASE("B2 D085 final native guard cost belongs to setup charge and sample call budgets") {
 for(unsigned phase=0;phase<3;++phase)isolated([=]{reset();Reader r;if(phase==1)begin(r);if(phase==2)discharge(r);delayed_guard=false;hw.hook=guardDelay;if(phase==0)r.begin(true);if(phase==1)r.start();if(phase==2){++hw.now;r.advance();}CHECK(r.report().phase==Phase::FAULT);CHECK(r.report().status==Status::CALL_DEADLINE);CHECK_FALSE(r.report().valid);});
}
TEST_CASE("B2 D085 completion includes cleanup time and each cleanup status remains evidence") {
 isolated([]{reset();Reader r;discharge(r);hw.now=r.report().started_us+2496;for(auto& v:hw.values)v=0;hw.configure_us=1;const auto s=r.advance();CHECK(s.cleanup.attempted_mask==15);CHECK(s.completed_us-s.started_us>=2500);CHECK(s.phase==Phase::FAULT);CHECK_FALSE(s.valid);});
 for(unsigned p=0;p<4;++p)isolated([=]{reset();Reader r;discharge(r);for(auto& v:hw.values)v=0;hw.configure_status[12+p]=-31;++hw.now;const auto s=r.advance();CHECK(s.phase==Phase::FAULT);CHECK_FALSE(s.valid);CHECK(s.cleanup.failed_mask==(1U<<p));CHECK(s.cleanup.status[p]==-31);CHECK(s.cleanup.attempted_mask==15);});
}

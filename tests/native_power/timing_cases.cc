// Tests exact acceptance deadlines and transition-time ownership observations.
// Clock values are injected at externally visible native hardware events.
// Fresh operating-system children preserve the production reset-only claim.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
#include "config.h"
#include <array>
namespace {
unsigned stage,deadline_delta;std::uint32_t stage_anchor,read_anchor;bool recorded;
void stageDeadline(fixture::Point p,std::uintptr_t) {
 auto start=stage==0?fixture::Point::REGULATOR_START:stage==1?fixture::Point::CAL_START:fixture::Point::ENABLE_START;
 auto done=stage==0?fixture::Point::LDO_READY:stage==1?fixture::Point::CAL_DONE:fixture::Point::ENABLE_READY;
 if(p==start){stage_anchor=fixture::hw.last_clock;recorded=true;}
 if(p==done&&recorded)fixture::hw.now=stage_anchor+deadline_delta;
}
void cleanupDeadline(fixture::Point p,std::uintptr_t){if(p==fixture::Point::EOS_CLEAR){fixture::hw.now=read_anchor+deadline_delta;fixture::hw.tick=0;}}
unsigned loss_clock;bool clock_lost;
void clockOwnership(fixture::Point p,std::uintptr_t) {
 if(p==fixture::Point::CLOCK&&fixture::hw.micros_calls==loss_clock){SYSCFG->CFGR1.value|=SYSCFG_CFGR1_ANASWVDD;clock_lost=true;}
}
}
TEST_CASE("B5 setup readiness at deadline equality is rejected at all three stages") {
 for(stage=0;stage<3;++stage)for(unsigned extra:{0U,1U})fixture::isolated([&]{
  fixture::reset();recorded=false;deadline_delta=(stage==1?5000U:100U)+extra;fixture::hw.hook=stageDeadline;
  power::Reader r;auto b=r.begin();CHECK(recorded);CHECK_FALSE(b.ready);
  CHECK(b.status==(stage==0?power::Status::REGULATOR_TIMEOUT:stage==1?power::Status::CALIBRATION_TIMEOUT:power::Status::ENABLE_TIMEOUT));
  CHECK(fixture::hw.command_errors==0);
 });
}
TEST_CASE("B5 readiness leaves time for final validation immediately before each setup deadline") {
 for(stage=0;stage<3;++stage)fixture::isolated([&]{
  fixture::reset();recorded=false;deadline_delta=(stage==1?5000U:100U)-2U;fixture::hw.hook=stageDeadline;
  power::Reader r;auto b=r.begin();CHECK(recorded);CHECK(b.ready);CHECK(b.status==power::Status::OK);
  CHECK(fixture::hw.command_errors==0);
 });
}
TEST_CASE("B5 cleanup immediately before and at the runtime deadline uses one origin") {
 for(unsigned delta:{98U,99U,100U,101U})fixture::isolated([&]{
  fixture::reset();power::Reader r;REQUIRE(r.begin().ready);read_anchor=fixture::hw.now;
  deadline_delta=delta;fixture::hw.hook=cleanupDeadline;auto s=r.read();
  if(delta<100U){CHECK(s.valid);CHECK(s.status==power::Status::OK);CHECK(s.completed_us-s.started_us<100U);}
  else {CHECK_FALSE(s.valid);CHECK(s.status==power::Status::CONVERSION_TIMEOUT);CHECK(s.raw==0);CHECK(s.voltage_v==0.0F);}
 });
}
TEST_CASE("B5 every setup clock observation detects a new conflicting owner") {
 for(unsigned at=1;at<=12;++at)fixture::isolated([&]{
  fixture::reset();loss_clock=at;clock_lost=false;fixture::hw.hook=clockOwnership;
  power::Reader r;auto b=r.begin();if(clock_lost){CHECK_FALSE(b.ready);CHECK(b.status==power::Status::OWNERSHIP);}
  else CHECK(b.ready);
 });
}

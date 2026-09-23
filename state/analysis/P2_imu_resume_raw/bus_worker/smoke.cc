#include "native_fixture.h"
#include "hal/imu_bus_unoq.h"
#include <cassert>
#include <cstdio>
#include <cstring>
static unsigned clears=0;
static void hook(fixture::Point p,std::uintptr_t){if(p==fixture::Point::STOP_CLEAR)++clears;}
static void empty(const imu::BusAcquisition& a){assert(a.state==imu::AcquisitionState::FAULT);assert(a.transfer.status==imu::BusStatus::NOT_INITIALIZED);assert(a.transfer.count==0 && !a.transfer.complete);for(auto b:a.transfer.bytes)assert(b==0);assert(!a.readiness_observed&&!a.motion_attempted&&!a.motion_status_observed);}
int main(int argc,char** argv){
 fixture::reset();imu::Bus bus;
 auto idle=bus.advanceMotion();assert(idle.state==imu::AsyncState::IDLE);
 auto pre=bus.beginMotion();assert(pre.completed&&pre.acquisition.transfer.status==imu::BusStatus::NOT_INITIALIZED);
 assert(bus.begin().ready);fixture::hw.tick=0;fixture::hw.hook=hook;
 fixture::hw.bytes[0]=(argc>1&&std::strcmp(argv[1],"none")==0)?0:1;
 auto p=bus.beginMotion();assert(p.started&&!p.completed&&p.polls==0);empty(p.acquisition);
 auto accesses=fixture::hw.accesses;auto clocks=fixture::hw.micros_calls;
 auto dup=bus.beginMotion();assert(!dup.started&&!dup.completed);assert(fixture::hw.accesses==accesses&&fixture::hw.micros_calls==clocks);
 if(argc>1&&std::strcmp(argv[1],"collision")==0){
  auto bad=bus.writeRegister(imu::Register::IDENTITY,0);assert(bad.status==imu::BusStatus::INVALID_REQUEST);assert(fixture::hw.accesses==accesses);
  auto cancel=bus.readMotion();assert(cancel.status==imu::BusStatus::CANCELLED&&cancel.count==0&&!cancel.complete);assert(fixture::hw.disable_count==1);
  accesses=fixture::hw.accesses;clocks=fixture::hw.micros_calls;auto end=bus.cancelMotion();assert(end.state==imu::AsyncState::FAULT&&!end.completed);assert(fixture::hw.accesses==accesses&&fixture::hw.micros_calls==clocks);
  std::puts("collision PASS");return 0;
 }
 unsigned calls=0;
 while(p.state==imu::AsyncState::PENDING&&calls<64){
  auto actions=fixture::hw.start_count+fixture::hw.tx_count+fixture::hw.rx_count+clears;auto polls=p.polls;
  p=bus.advanceMotion();++calls;
  assert(p.polls>polls&&p.polls-polls<=3);
  assert(fixture::hw.start_count+fixture::hw.tx_count+fixture::hw.rx_count+clears-actions<=1);
  assert(!p.started);if(p.state==imu::AsyncState::PENDING){assert(!p.completed);empty(p.acquisition);}
 }
 assert(p.state==imu::AsyncState::COMPLETE&&p.completed);assert(p.acquisition.transfer.status==imu::BusStatus::OK);assert(fixture::hw.command_errors==0);
 bool none=fixture::hw.bytes[0]==0;assert(calls==(none?6U:26U));assert(p.acquisition.transfer.count==(none?0:15));assert(p.acquisition.state==(none?imu::AcquisitionState::NO_NEW:imu::AcquisitionState::OBSERVATION));
 accesses=fixture::hw.accesses;clocks=fixture::hw.micros_calls;auto report=bus.advanceMotion();assert(!report.completed&&!report.started);assert(fixture::hw.accesses==accesses&&fixture::hw.micros_calls==clocks);
 auto again=bus.beginMotion();assert(again.started&&again.state==imu::AsyncState::PENDING);auto cancel=bus.cancelMotion();assert(cancel.completed&&cancel.acquisition.transfer.status==imu::BusStatus::CANCELLED&&fixture::hw.disable_count==1);
 std::printf("success PASS calls=%u polls=%u\n",calls,p.polls);
}

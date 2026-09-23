// Checks operation-wide deadlines, wrap arithmetic and finite frozen-clock waits.
// Final observation must still precede the original acceptance deadline.
// Read bytes and flag arrival never imply valid time or permission to publish.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"
namespace {
std::uint32_t deadline_time=0;
fixture::Point advance_at=fixture::Point::LAST_RX;
bool cleared=false,late_time_seen=false;
unsigned clocks_after_clear=0;
void advance(fixture::Point p,std::uintptr_t){if(p==advance_at)fixture::hw.now=deadline_time;}
void empty(const imu::BusTransfer& r){CHECK_FALSE(r.complete);CHECK(r.count==0);for(auto b:r.bytes)CHECK(b==0);}
}
TEST_CASE("B3 transfer last-byte and final-clear boundaries accept deadline minus one and reject equality") {
 for(auto point:{fixture::Point::LAST_RX,fixture::Point::STOP_CLEAR})for(unsigned offset:{0U,0xfffffe00U})for(unsigned late:{0U,1U}){
 fixture::isolated([point,offset,late]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);fixture::hw.now=offset;fixture::hw.tick=0;
    deadline_time=offset+config::IMU_I2C_TRANSFER_US-1+late;advance_at=point;fixture::hw.hook=advance;
    const auto r=bus.readMotion();CHECK(r.started_us==offset);
    if(late){empty(r);CHECK(r.status==imu::BusStatus::TIMEOUT);}
    else{CHECK(r.complete);CHECK(r.status==imu::BusStatus::OK);CHECK(r.completed_us==deadline_time);}
 });}
}
TEST_CASE("B3 missing START acknowledgement terminates by time or total poll budget") {
 for(bool frozen:{false,true})fixture::isolated([frozen]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);fixture::hw.tick=frozen?0:1;fixture::hw.start_after=-1;
    const auto r=bus.readMotion();empty(r);
    CHECK(r.status==(frozen?imu::BusStatus::POLL_LIMIT:imu::BusStatus::TIMEOUT));
    CHECK(fixture::hw.start_count==1);CHECK(fixture::hw.tx_count==0);CHECK(fixture::hw.stop_count==0);
    CHECK(fixture::hw.accesses<1000000);CHECK(fixture::hw.micros_calls<100000);
 });
}
TEST_CASE("B3 byte progress does not restart the absolute transfer deadline") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);fixture::hw.now=0;fixture::hw.tick=0;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t){if(p==fixture::Point::RX)fixture::hw.now+=50;};
    const auto r=bus.readMotion();empty(r);CHECK(r.status==imu::BusStatus::TIMEOUT);
    CHECK(fixture::hw.rx_count<=12);CHECK(fixture::hw.rx_count>=11);CHECK(fixture::hw.start_count==2);
 });
}
TEST_CASE("B3 local disable confirmation must remain inside its separate cleanup deadline") {
 for(unsigned late:{0U,1U})fixture::isolated([late]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);fixture::hw.now=1000;fixture::hw.tick=0;
    deadline_time=1000+config::IMU_I2C_CLEANUP_US-1+late;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t){
        if(p==fixture::Point::TX)I2C4->ISR.value|=I2C_ISR_NACKF;
        if(p==fixture::Point::DISABLE)fixture::hw.now=deadline_time;
    };
    const auto r=bus.readMotion();empty(r);CHECK(r.status==imu::BusStatus::NACK);
    CHECK(r.cleanup==(late?imu::BusCleanup::UNCONFIRMED:imu::BusCleanup::DISABLED));
 });
}
TEST_CASE("B3 total frozen-clock poll budget is shared by every byte and phase") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);
    fixture::hw.tick=0;fixture::hw.byte_after=1000;
    const auto r=bus.readMotion();empty(r);CHECK(r.status==imu::BusStatus::POLL_LIMIT);
    CHECK(fixture::hw.rx_count>1);CHECK(fixture::hw.rx_count<15);
    CHECK(fixture::hw.accesses<1000000);CHECK(fixture::hw.start_count==2);
 });
}
TEST_CASE("B3 setup acceptance checks elapsed time after peripheral enable readback") {
 for(unsigned late:{0U,1U})fixture::isolated([late]{
    fixture::reset();fixture::hw.tick=0;deadline_time=config::IMU_I2C_SETUP_US-1+late;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t a){
        if(p==fixture::Point::ACCESS&&a==reinterpret_cast<std::uintptr_t>(&I2C4->CR1)&&
           (I2C4->CR1.value&I2C_CR1_PE))fixture::hw.now=deadline_time;
    };
    imu::Bus bus;const auto r=bus.begin();
    CHECK(r.ready==!late);CHECK(r.status==(late?imu::BusStatus::TIMEOUT:imu::BusStatus::OK));
 });
}
TEST_CASE("B3 final acceptance rejects deadline expiry during the final ownership scan") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);fixture::hw.now=0;fixture::hw.tick=0;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t){
        if(p==fixture::Point::STOP_CLEAR)cleared=true;
        if(cleared&&p==fixture::Point::CLOCK)++clocks_after_clear;
        if(cleared&&p==fixture::Point::ACCESS&&clocks_after_clear==4){
            fixture::hw.now=config::IMU_I2C_TRANSFER_US;late_time_seen=true;
        }
    };
    const auto r=bus.readMotion();REQUIRE(late_time_seen);empty(r);CHECK(r.status==imu::BusStatus::TIMEOUT);
 });
}

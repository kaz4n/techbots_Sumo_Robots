// Independently exercises the last acceptance scan after owned STOP clearing.
// Error and elapsed evidence observed during that scan must prevent publication.
// Reviewer-only supplemental cases do not alter the independent author tests.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"
namespace {
bool cleared=false, injected=false;
unsigned clocks_after_clear=0;
void finalError(fixture::Point point,std::uintptr_t) {
    if(point==fixture::Point::STOP_CLEAR)cleared=true;
    if(cleared&&point==fixture::Point::CLOCK&&++clocks_after_clear==3){
        I2C4->ISR.value|=I2C_ISR_BERR;injected=true;
    }
}
void finalTime(fixture::Point point,std::uintptr_t) {
    if(point==fixture::Point::STOP_CLEAR)cleared=true;
    if(cleared&&point==fixture::Point::CLOCK)++clocks_after_clear;
    if(cleared&&point==fixture::Point::ACCESS&&clocks_after_clear==3){
        fixture::hw.now=config::IMU_I2C_TRANSFER_US;injected=true;
    }
}
}
TEST_CASE("B3 final acceptance excludes error arising during final observation") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);
    fixture::hw.now=0;fixture::hw.tick=0;fixture::hw.hook=finalError;
    const auto result=bus.readMotion();REQUIRE(injected);
    CHECK(result.status==imu::BusStatus::BUS_ERROR);CHECK_FALSE(result.complete);
    CHECK(result.count==0);for(auto byte:result.bytes)CHECK(byte==0);
    CHECK((result.error_flags&I2C_ISR_BERR)!=0);
 });
}
TEST_CASE("B3 final acceptance excludes deadline expiring within final ownership scan") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);
    fixture::hw.now=0;fixture::hw.tick=0;fixture::hw.hook=finalTime;
    const auto result=bus.readMotion();REQUIRE(injected);
    CHECK(result.status==imu::BusStatus::TIMEOUT);CHECK_FALSE(result.complete);
    CHECK(result.count==0);for(auto byte:result.bytes)CHECK(byte==0);
 });
}
TEST_CASE("B3 setup acceptance timestamps its final ownership scan") {
 fixture::isolated([]{
    fixture::reset();fixture::hw.now=0;fixture::hw.tick=0;
    fixture::hw.hook=[](fixture::Point point,std::uintptr_t){
        if((I2C4->CR1.value&I2C_CR1_PE)&&point==fixture::Point::CLOCK)++clocks_after_clear;
        if(clocks_after_clear==2&&point==fixture::Point::ACCESS){
            fixture::hw.now=config::IMU_I2C_SETUP_US;injected=true;
        }
    };
    imu::Bus bus;const auto result=bus.begin();REQUIRE(injected);
    CHECK(result.status==imu::BusStatus::TIMEOUT);CHECK_FALSE(result.ready);
 });
}
TEST_CASE("B3 cleanup acceptance timestamps its final ownership scan") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;REQUIRE(bus.begin().ready);
    fixture::hw.now=0;fixture::hw.tick=0;
    fixture::hw.hook=[](fixture::Point point,std::uintptr_t){
        if(point==fixture::Point::TX)I2C4->ISR.value|=I2C_ISR_NACKF;
        if(point==fixture::Point::DISABLE)cleared=true;
        if(cleared&&point==fixture::Point::CLOCK)++clocks_after_clear;
        if(cleared&&clocks_after_clear==2&&point==fixture::Point::ACCESS){
            fixture::hw.now=config::IMU_I2C_CLEANUP_US;injected=true;
        }
    };
    const auto result=bus.readMotion();REQUIRE(injected);
    CHECK(result.status==imu::BusStatus::NACK);
    CHECK(result.cleanup==imu::BusCleanup::UNCONFIRMED);
 });
}

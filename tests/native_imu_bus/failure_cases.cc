// Exercises transport fault priority, lossless error snapshots and cleanup limits.
// A local peripheral disable never constitutes external bus recovery.
// Expectations come from the D079 public contract, not implementation internals.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"
namespace {
using imu::BusStatus;using imu::BusCleanup;
std::uint32_t injected=0;
unsigned writes_at_loss=0;
bool cleared=false,late_error_seen=false;
unsigned clocks_after_clear=0;
void begin(imu::Bus& b){REQUIRE(b.begin().ready);}
void empty(const imu::BusTransfer& r){CHECK_FALSE(r.complete);CHECK(r.count==0);for(auto b:r.bytes)CHECK(b==0);}
void injectAfterTx(fixture::Point p,std::uintptr_t){if(p==fixture::Point::TX)I2C4->ISR.value|=injected;}
void latched(imu::Bus& b){
    const auto accesses=fixture::hw.accesses,micros=fixture::hw.micros_calls;
    const auto r=b.readMotion();CHECK(r.status==BusStatus::FAULT_LATCHED);empty(r);
    CHECK(fixture::hw.accesses==accesses);CHECK(fixture::hw.micros_calls==micros);
}
}
TEST_CASE("B3 every hardware error fails with its original flags and terminal local cleanup") {
 struct Fault {std::uint32_t flag;BusStatus status;};
 for(auto f:{Fault{I2C_ISR_ARLO,BusStatus::ARBITRATION_LOST},Fault{I2C_ISR_BERR,BusStatus::BUS_ERROR},
     Fault{I2C_ISR_NACKF,BusStatus::NACK},Fault{I2C_ISR_OVR,BusStatus::OVERRUN},
     Fault{I2C_ISR_PECERR,BusStatus::PROTOCOL},Fault{I2C_ISR_TIMEOUT,BusStatus::PROTOCOL},
     Fault{I2C_ISR_ALERT,BusStatus::PROTOCOL},Fault{I2C_ISR_ADDR,BusStatus::PROTOCOL},
     Fault{I2C_ISR_TCR,BusStatus::PROTOCOL},
     Fault{I2C_ISR_ARLO|I2C_ISR_BERR|I2C_ISR_NACKF|I2C_ISR_OVR,BusStatus::ARBITRATION_LOST},
     Fault{I2C_ISR_BERR|I2C_ISR_NACKF|I2C_ISR_OVR,BusStatus::BUS_ERROR},
     Fault{I2C_ISR_NACKF|I2C_ISR_OVR,BusStatus::NACK}})fixture::isolated([f]{
    fixture::reset();imu::Bus bus;begin(bus);injected=f.flag;fixture::hw.hook=injectAfterTx;
    const auto r=bus.readMotion();empty(r);CHECK(r.status==f.status);CHECK((r.error_flags&f.flag)==f.flag);
    CHECK(r.cleanup==BusCleanup::DISABLED);CHECK(fixture::hw.disable_count==1);
    CHECK(fixture::hw.stop_count==0);CHECK(fixture::hw.start_count==1);latched(bus);
 });
}
TEST_CASE("B3 stale events BUSY pending commands and low physical lines cannot start a request") {
 for(unsigned k=0;k<11;++k)fixture::isolated([k]{
    fixture::reset();imu::Bus bus;begin(bus);
    constexpr std::uint32_t flags[]={I2C_ISR_RXNE,I2C_ISR_STOPF,I2C_ISR_TC,I2C_ISR_TXIS,I2C_ISR_TCR,I2C_ISR_BUSY};
    if(k<6)I2C4->ISR.value|=flags[k];
    if(k==6)I2C4->CR2.value|=I2C_CR2_START;
    if(k==7)I2C4->CR2.value|=I2C_CR2_STOP;
    if(k==8)GPIOD->IDR.value&=~(1U<<12);
    if(k==9)GPIOD->IDR.value&=~(1U<<13);
    if(k==10)GPIOD->IDR.value=0;
    const auto r=bus.readMotion();empty(r);CHECK(r.status!=BusStatus::OK);
    CHECK(fixture::hw.start_count==0);CHECK(fixture::hw.tx_count==0);CHECK(fixture::hw.stop_count==0);latched(bus);
 });
}
TEST_CASE("B3 early STOP extra RXNE and wrong phase TXIS TC never publish partial data") {
 for(unsigned k=0;k<4;++k)fixture::isolated([k]{
    fixture::reset();imu::Bus bus;begin(bus);injected=k;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t){
        if(p==fixture::Point::RX&&fixture::hw.rx_count==7){
            if(injected==0){I2C4->ISR.value|=I2C_ISR_STOPF;I2C4->ISR.value&=~I2C_ISR_BUSY;}
            if(injected==2)I2C4->ISR.value|=I2C_ISR_TXIS;
            if(injected==3)I2C4->ISR.value|=I2C_ISR_TC;
        }
        if(injected==1&&p==fixture::Point::RX&&fixture::hw.rx_count==15)I2C4->ISR.value|=I2C_ISR_RXNE;
    };
    const auto r=bus.readMotion();empty(r);CHECK(r.status==BusStatus::PROTOCOL);latched(bus);
 });
}
TEST_CASE("B3 disabled cleanup is local even when pins stay low and no STOP occurred") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;begin(bus);GPIOD->IDR.value=0;
    const auto r=bus.readMotion();empty(r);CHECK(r.cleanup==BusCleanup::DISABLED);
    CHECK(GPIOD->IDR.value==0);CHECK(fixture::hw.stop_count==0);CHECK(fixture::hw.disable_count==1);
 });
}
TEST_CASE("B3 failed disable reports unconfirmed and remains bounded with frozen time") {
 for(bool frozen:{false,true})fixture::isolated([frozen]{
    fixture::reset();imu::Bus bus;begin(bus);fixture::hw.tick=frozen?0:1;
    fixture::hw.ignore_disable=true;injected=I2C_ISR_NACKF;fixture::hw.hook=injectAfterTx;
    const auto r=bus.readMotion();empty(r);CHECK(r.status==BusStatus::NACK);
    CHECK(r.cleanup==BusCleanup::UNCONFIRMED);CHECK(fixture::hw.disable_count==1);
    CHECK(fixture::hw.accesses<1000000);CHECK(fixture::hw.micros_calls<100000);latched(bus);
 });
}
TEST_CASE("B3 observed ownership loss at progress and final boundaries forbids cleanup writes") {
 for(auto point:{fixture::Point::START_ACK,fixture::Point::TC,fixture::Point::RX,fixture::Point::LAST_RX,fixture::Point::STOP_CLEAR}){
 fixture::isolated([point]{
    fixture::reset();imu::Bus bus;begin(bus);injected=static_cast<std::uint32_t>(point);
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t){if(static_cast<std::uint32_t>(p)==injected){
        fixture::hw.irq_enable[0]=true;writes_at_loss=fixture::hw.writes;fixture::hw.hook=nullptr;}};
    const auto r=bus.readMotion();empty(r);CHECK(r.status==BusStatus::OWNERSHIP);
    CHECK(r.cleanup==BusCleanup::NOT_ATTEMPTED);CHECK(fixture::hw.writes==writes_at_loss);
    CHECK(fixture::hw.disable_count==0);fixture::hw.irq_enable[0]=false;latched(bus);
 });}
}
TEST_CASE("B3 final acceptance rejects a new error during its final clock observation") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;begin(bus);fixture::hw.now=0;fixture::hw.tick=0;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t){
        if(p==fixture::Point::STOP_CLEAR)cleared=true;
        if(cleared&&p==fixture::Point::CLOCK&&++clocks_after_clear==3){
            I2C4->ISR.value|=I2C_ISR_BERR;late_error_seen=true;
        }
    };
    const auto r=bus.readMotion();REQUIRE(late_error_seen);empty(r);
    CHECK(r.status==BusStatus::BUS_ERROR);CHECK((r.error_flags&I2C_ISR_BERR)!=0);
 });
}

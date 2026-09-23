// Checks frozen public MPU6050 transfer behavior without reading production CPP.
// Complete transport data, retained ownership and finite termination are separate.
// Every modeled boot is isolated while same-boot owner claims remain irreversible.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"
#include <type_traits>
namespace {
using imu::BusStatus;
using imu::BusCleanup;
using imu::Register;
void begin(imu::Bus& bus){const auto r=bus.begin();REQUIRE(r.status==BusStatus::OK);REQUIRE(r.ready);}
void empty(const imu::BusTransfer& r){CHECK_FALSE(r.complete);CHECK(r.count==0);for(auto b:r.bytes)CHECK(b==0);}
void expectRead(const imu::BusTransfer& r,unsigned n){
    REQUIRE(r.status==BusStatus::OK);REQUIRE(r.complete);CHECK(r.count==n);
    CHECK(r.cleanup==BusCleanup::NOT_ATTEMPTED);CHECK(r.error_flags==0);
    for(unsigned i=0;i<n;++i)CHECK(r.bytes[i]==fixture::hw.bytes[i]);
    for(unsigned i=n;i<15;++i)CHECK(r.bytes[i]==0);
    CHECK(fixture::hw.command_errors==0);CHECK(fixture::hw.gated_reads==0);
}
void noIo(){CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.micros_calls==0);
    CHECK(fixture::hw.ready_reads==0);CHECK(fixture::hw.irq_reads==0);}
}
TEST_CASE("B3 transport constructor and pre-begin requests perform no I/O") {
 fixture::isolated([]{
    fixture::reset();{imu::Bus temporary;}noIo();imu::Bus bus;noIo();
    empty(bus.readMotion());empty(bus.readRegister(Register::IDENTITY));
    empty(bus.writeRegister(Register::POWER_1,0));noIo();
    CHECK_FALSE(std::is_copy_constructible<imu::Bus>::value);
 });
}
TEST_CASE("B3 transport setup claims once and configures only the approved clock and pads") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;begin(bus);
    CHECK((fixture::peek(I2C4->CR1)&I2C_CR1_PE)!=0);CHECK(fixture::hw.start_count==0);
    CHECK(LL_GPIO_GetPinMode(GPIOD,1U<<12)==LL_GPIO_MODE_ALTERNATE);
    CHECK(LL_GPIO_GetPinMode(GPIOD,1U<<13)==LL_GPIO_MODE_ALTERNATE);
    CHECK(LL_GPIO_GetAFPin_8_15(GPIOD,1U<<12)==LL_GPIO_AF_4);
    CHECK(LL_GPIO_GetAFPin_8_15(GPIOD,1U<<13)==LL_GPIO_AF_4);
    CHECK(LL_GPIO_GetPinOutputType(GPIOD,1U<<12)==LL_GPIO_OUTPUT_OPENDRAIN);
    CHECK(LL_GPIO_GetPinPull(GPIOD,1U<<13)==LL_GPIO_PULL_UP);
    CHECK(LL_GPIO_GetPinSpeed(GPIOD,1U<<12)==LL_GPIO_SPEED_FREQ_LOW);
    CHECK((fixture::peek(GPIOD->MODER)&0xf0ffffffU)==0xf0ffffffU);
    const auto writes=fixture::hw.writes,accesses=fixture::hw.accesses,micros=fixture::hw.micros_calls;
    CHECK(bus.begin().status==BusStatus::ALREADY_STARTED);CHECK(fixture::hw.accesses==accesses);CHECK(fixture::hw.micros_calls==micros);
    imu::Bus second;CHECK_FALSE(second.begin().ready);CHECK(fixture::hw.writes==writes);
    CHECK(fixture::hw.gated_reads==0);CHECK(fixture::hw.stop_count==0);
 });
}
TEST_CASE("B3 readMotion uses one pointer write then repeated START and exactly fifteen bytes") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;begin(bus);const auto r=bus.readMotion();expectRead(r,15);
    REQUIRE(fixture::hw.start_count==2);CHECK(fixture::hw.tx_count==1);CHECK(fixture::hw.transmitted[0]==0x3a);
    CHECK(fixture::hw.rx_count==15);CHECK(fixture::hw.stop_count==0);CHECK(fixture::hw.disable_count==0);
    const auto first=fixture::hw.starts[0].cr2,second=fixture::hw.starts[1].cr2;
    CHECK((first&I2C_CR2_SADD)==(config::IMU_I2C_ADDRESS<<1));
    CHECK((first&I2C_CR2_SADD)==(second&I2C_CR2_SADD));
    CHECK(((first&I2C_CR2_NBYTES)>>I2C_CR2_NBYTES_Pos)==1);
    CHECK((first&(I2C_CR2_RD_WRN|I2C_CR2_AUTOEND|I2C_CR2_RELOAD|I2C_CR2_ADD10))==0);
    CHECK(((second&I2C_CR2_NBYTES)>>I2C_CR2_NBYTES_Pos)==15);
    CHECK((second&(I2C_CR2_RD_WRN|I2C_CR2_AUTOEND))==(I2C_CR2_RD_WRN|I2C_CR2_AUTOEND));
    CHECK((second&(I2C_CR2_RELOAD|I2C_CR2_ADD10|I2C_CR2_STOP))==0);
    CHECK((fixture::peek(I2C4->ISR)&(I2C_ISR_RXNE|I2C_ISR_STOPF|I2C_ISR_BUSY))==0);
 });
}
TEST_CASE("B3 register reads preserve all byte values and fresh repeated requests") {
 for(auto reg:{Register::SAMPLE_DIVIDER,Register::FILTER,Register::GYRO_RANGE,Register::ACCEL_RANGE,
     Register::FIFO_ENABLE,Register::INTERRUPT_CONFIG,Register::INTERRUPT_ENABLE,Register::INTERRUPT_STATUS,
     Register::USER_CONTROL,Register::POWER_1,Register::POWER_2,Register::IDENTITY}){
 fixture::isolated([reg]{
    fixture::reset();imu::Bus bus;begin(bus);fixture::hw.bytes[0]=0xff;expectRead(bus.readRegister(reg),1);
    CHECK(fixture::hw.transmitted[0]==static_cast<std::uint8_t>(reg));
    fixture::hw.bytes[0]=0;expectRead(bus.readRegister(reg),1);CHECK(fixture::hw.rx_count==2);
 });}
}
TEST_CASE("B3 unsupported register requests have no I/O and do not consume a valid owner") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;begin(bus);fixture::clearTrace();fixture::hw.irq_reads=0;
    const auto a=bus.readRegister(static_cast<Register>(0x00));CHECK(a.status==BusStatus::INVALID_REQUEST);empty(a);
    for(auto reg:{Register::IDENTITY,Register::INTERRUPT_STATUS,static_cast<Register>(0xff)}){
        const auto r=bus.writeRegister(reg,0);CHECK(r.status==BusStatus::INVALID_REQUEST);empty(r);}
    noIo();expectRead(bus.readMotion(),15);
 });
}
TEST_CASE("B3 single register writes emit pointer and value without receive or repeated START") {
 for(auto reg:{Register::SAMPLE_DIVIDER,Register::FILTER,Register::GYRO_RANGE,Register::ACCEL_RANGE,
     Register::FIFO_ENABLE,Register::INTERRUPT_CONFIG,Register::INTERRUPT_ENABLE,
     Register::USER_CONTROL,Register::POWER_1,Register::POWER_2}){
 fixture::isolated([reg]{
    fixture::reset();imu::Bus bus;begin(bus);const auto r=bus.writeRegister(reg,0xa5);
    REQUIRE(r.status==BusStatus::OK);REQUIRE(r.complete);CHECK(r.count==0);for(auto byte:r.bytes)CHECK(byte==0);
    CHECK(fixture::hw.start_count==1);
    CHECK(fixture::hw.tx_count==2);CHECK(fixture::hw.rx_count==0);
    CHECK(fixture::hw.transmitted[0]==static_cast<std::uint8_t>(reg));CHECK(fixture::hw.transmitted[1]==0xa5);
    CHECK(((fixture::hw.starts[0].cr2&I2C_CR2_NBYTES)>>I2C_CR2_NBYTES_Pos)==2);
    CHECK((fixture::hw.starts[0].cr2&I2C_CR2_AUTOEND)!=0);CHECK(fixture::hw.command_errors==0);
 });}
}
TEST_CASE("B3 transfer success requires final STOP acknowledgement and no residual bus activity") {
 for(unsigned kind=0;kind<4;++kind)fixture::isolated([kind]{
    fixture::reset();imu::Bus bus;begin(bus);
    if(kind==0){fixture::hw.with_final_stop=false;fixture::hw.stop_after=-1;}
    if(kind==1)fixture::hw.keep_busy=true;
    if(kind==2)fixture::hw.ignore_clear=true;
    if(kind==3)fixture::hw.halt_after=7;
    const auto r=bus.readMotion();empty(r);CHECK(r.status!=BusStatus::OK);
    CHECK(fixture::hw.stop_count==0);CHECK(fixture::hw.accesses<500000);
    const auto writes=fixture::hw.writes;empty(bus.readMotion());CHECK(fixture::hw.writes==writes);
 });
}
TEST_CASE("B3 data bytes alone including zero INT_STATUS do not imply freshness") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;begin(bus);fixture::hw.bytes.fill(0);expectRead(bus.readMotion(),15);
 });
}
TEST_CASE("B3 setup and accepted transfer allocate no heap memory") {
 fixture::isolated([]{
    fixture::reset();imu::Bus bus;imu::BusInit init;imu::BusTransfer r;
    {fixture::AllocationGuard guard;init=bus.begin();r=bus.readMotion();}
    CHECK(init.ready);expectRead(r,15);CHECK(fixture::hw.allocations==0);
 });
}

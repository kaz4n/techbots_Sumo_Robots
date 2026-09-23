// Injects invalid installed-state premises before claim and after configuration.
// A second instance cannot recover an irreversible partially configured claim.
// Native admission and runtime ownership guards must fail without stealing I/O.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
namespace {
void reject(imu::Bus& b){const auto r=b.begin();CHECK_FALSE(r.ready);CHECK(r.status!=imu::BusStatus::OK);CHECK(fixture::hw.start_count==0);}
void stateMutation(unsigned k){
    switch(k){
    case 0:fixture_devices[0].state=nullptr;break;
    case 1:fixture_devices[0].state->initialized=true;break;
    case 2:fixture_devices[0].state->init_res=1;break;
    case 3:fixture::hw.ready[1]=false;break;
    case 4:fixture::hw.ready[2]=false;break;
    case 5:fixture::hw.irq_enable[0]=true;break;
    case 6:fixture::hw.irq_enable[1]=true;break;
    case 7:fixture::hw.irq_pending[0]=true;break;
    case 8:fixture::hw.irq_pending[1]=true;break;
    case 9:fixture::hw.irq_active[0]=true;break;
    case 10:fixture::hw.irq_active[1]=true;break;
    case 11:RCC->AHB2ENR1.value&=~RCC_AHB2ENR1_GPIODEN;break;
    case 12:RCC->CCIPR1.value|=RCC_CCIPR1_I2C4SEL_0;break;
    case 13:RCC->CFGR2.value|=RCC_CFGR2_PPRE1_2;break;
    case 14:RCC->CFGR2.value|=RCC_CFGR2_HPRE_3;break;
    case 15:RCC->CR.value&=~RCC_CR_PLL1RDY;break;
    case 16:RCC->CR.value&=~RCC_CR_MSISRDY;break;
    case 17:RCC->PLL1DIVR.value^=1U;break;
    case 18:RCC->PLL1CFGR.value&=~RCC_PLL1CFGR_PLL1REN;break;
    case 19:RCC->PLL1CFGR.value|=RCC_PLL1CFGR_PLL1FRACEN;break;
    case 20:RCC->AHB3ENR.value&=~RCC_AHB3ENR_PWREN;break;
    case 21:PWR->VOSR.value&=~PWR_VOSR_VOSRDY;break;
    case 22:PWR->VOSR.value&=~PWR_VOSR_BOOSTRDY;break;
    case 23:PWR->SVMCR.value&=~PWR_SVMCR_ASV;break;
    case 24:PWR->SVMSR.value&=~PWR_SVMSR_ACTVOSRDY;break;
    case 25:GPIOD->LCKR.value=(1U<<12)|GPIO_LCKR_LCKK;break;
    case 26:GPIOD->LCKR.value=(1U<<13)|GPIO_LCKR_LCKK;break;
    }
}
}
TEST_CASE("B3 stock device IRQ clock power and GPIO ownership failures are rejected before pad writes") {
 for(unsigned k=0;k<27;++k)fixture::isolated([k]{
    INFO("mutation="<<k);
    fixture::reset();stateMutation(k);imu::Bus b;reject(b);
    CHECK(fixture::hw.writes==0);CHECK(fixture::hw.disable_count==0);
 });
}
TEST_CASE("B3 native clock dispatch failure and missing gate readback never read disabled I2C") {
 for(unsigned k=0;k<3;++k)fixture::isolated([k]{
    fixture::reset();if(k==0)fixture::hw.clock_status=-5;
    if(k==1)fixture::hw.ignore_gate=true;
    if(k==2)fixture_devices[2].api=nullptr;
    imu::Bus b;reject(b);CHECK(fixture::hw.gated_reads==0);CHECK(fixture::hw.writes==0);
 });
}
TEST_CASE("B3 nonpristine registers and already configured pads are never reset to force admission") {
 for(unsigned k=0;k<11;++k)fixture::isolated([k]{
    fixture::reset();
    volatile Reg* regs[]={&I2C4->CR1,&I2C4->CR2,&I2C4->OAR1,&I2C4->OAR2,&I2C4->TIMINGR,&I2C4->TIMEOUTR,&I2C4->AUTOCR,&I2C4->ISR};
    if(k<8)regs[k]->value|=(k==7?I2C_ISR_STOPF:1U);
    if(k==8)GPIOD->MODER.value&=~(3U<<24);
    if(k==9)GPIOD->MODER.value&=~(3U<<26);
    if(k==10)GPIOD->PUPDR.value|=1U<<24;
    imu::Bus b;reject(b);CHECK(fixture::hw.writes==0);CHECK(fixture::hw.gated_reads==0);
 });
}
TEST_CASE("B3 runtime control and resource changes forbid a new command and cleanup mutation") {
 for(unsigned k=0;k<35;++k)fixture::isolated([k]{
    INFO("mutation="<<k);
    fixture::reset();imu::Bus b;REQUIRE(b.begin().ready);
    if(k<27)stateMutation(k);
    if(k==27)I2C4->CR1.value|=I2C_CR1_RXIE;
    if(k==28)I2C4->TIMINGR.value^=1U;
    if(k==29)I2C4->OAR1.value=1;
    if(k==30)I2C4->TIMEOUTR.value=1;
    if(k==31)I2C4->AUTOCR.value=1;
    if(k==32)GPIOD->AFR[1].value^=1U<<16;
    if(k==33)GPIOD->OTYPER.value&=~(1U<<13);
    if(k==34)GPIOD->PUPDR.value^=1U<<24;
    const auto writes=fixture::hw.writes;const auto r=b.readMotion();CHECK_FALSE(r.complete);
    CHECK(r.status==imu::BusStatus::OWNERSHIP);CHECK(r.cleanup==imu::BusCleanup::NOT_ATTEMPTED);
    CHECK(fixture::hw.writes==writes);CHECK(fixture::hw.start_count==0);
 });
}
TEST_CASE("B3 ignored first pad or timing write consumes the boot claim until process reset") {
 for(unsigned k=0;k<3;++k)fixture::isolated([k]{
    fixture::reset();volatile Reg* regs[]={&GPIOD->MODER,&GPIOD->AFR[1],&I2C4->TIMINGR};
    fixture::hw.ignored_write=reinterpret_cast<std::uintptr_t>(regs[k]);
    {imu::Bus first;reject(first);}fixture::hw.ignored_write=0;
    GPIOD->MODER.value=0xffffffffU;GPIOD->PUPDR.value=0;GPIOD->OTYPER.value=0;GPIOD->AFR[1].value=0;
    I2C4->CR1.value=0;I2C4->TIMINGR.value=0;I2C4->ISR.value=I2C_ISR_TXE;
    const auto writes=fixture::hw.writes;imu::Bus second;reject(second);CHECK(fixture::hw.writes==writes);
 });
}
TEST_CASE("B3 a rejected preclaim admission leaves a fresh instance eligible in the same boot") {
 for(unsigned k=0;k<3;++k)fixture::isolated([k]{
    fixture::reset();if(k==0)fixture::hw.ready[1]=false;
    if(k==1)fixture::hw.clock_status=-5;
    if(k==2)I2C4->TIMINGR.value=1;
    {imu::Bus first;reject(first);}
    fixture::hw.ready[1]=true;fixture::hw.clock_status=0;I2C4->TIMINGR.value=0;
    imu::Bus second;CHECK(second.begin().ready);
 });
}
TEST_CASE("B3 ownership changing during pristine ISR observation forbids the first pad write") {
 fixture::isolated([]{
    fixture::reset();bool observed=false;
    fixture::hw.hook=[](fixture::Point p,std::uintptr_t a){
        if(p==fixture::Point::ACCESS&&a==reinterpret_cast<std::uintptr_t>(&I2C4->ISR)){
            GPIOD->MODER.value&=~(3U<<24);fixture::hw.hook=nullptr;
        }
    };
    imu::Bus b;const auto r=b.begin();observed=fixture::hw.hook==nullptr;
    REQUIRE(observed);CHECK_FALSE(r.ready);CHECK(fixture::hw.writes==0);
 });
}

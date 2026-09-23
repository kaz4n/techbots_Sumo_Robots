// Extends B5 fault injection across nominal clock metadata and owned mode fields.
// Each predicate comes from the public contract and retained ownership audit.
// Changes are injected before requests and at post-calibration transitions.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
#include <array>
#include <cstdint>
using power::Status;using power::Shutdown;
namespace {
struct Change {volatile Reg* reg;std::uint32_t bits;bool clear;};
void apply(const Change& c){c.reg->value=c.clear?(c.reg->value&~c.bits):(c.reg->value|c.bits);}
std::array<Change,33> changes() {return {{
 {&RCC->CR,RCC_CR_MSISRDY,true},{&RCC->CR,RCC_CR_PLL1RDY,true},
 {&RCC->CR,RCC_CR_MSIPLLEN,true},{&RCC->CR,RCC_CR_MSIPLLSEL,true},
 {&RCC->ICSCR1,RCC_ICSCR1_MSIRGSEL,true},{&RCC->ICSCR1,RCC_ICSCR1_MSISRANGE_0,false},
 {&RCC->CFGR1,RCC_CFGR1_SWS,true},{&RCC->CFGR2,RCC_CFGR2_HPRE_3,false},
 {&RCC->PLL1CFGR,RCC_PLL1CFGR_PLL1SRC_1,false},{&RCC->PLL1CFGR,RCC_PLL1CFGR_PLL1M_0,false},
 {&RCC->PLL1CFGR,RCC_PLL1CFGR_PLL1REN,true},{&RCC->PLL1CFGR,RCC_PLL1CFGR_PLL1FRACEN,false},
 {&RCC->PLL1DIVR,RCC_PLL1DIVR_PLL1N_0,true},{&RCC->PLL1DIVR,RCC_PLL1DIVR_PLL1R_0,true},
 {&RCC->CCIPR3,RCC_CCIPR3_ADCDACSEL_0,false},
 {&RCC->AHB3ENR,RCC_AHB3ENR_ADC4EN,true},{&RCC->AHB3ENR,RCC_AHB3ENR_DAC1EN,true},
 {&RCC->AHB3ENR,RCC_AHB3ENR_PWREN,true},{&RCC->APB3ENR,RCC_APB3ENR_SYSCFGEN,true},
 {&RCC->AHB2ENR1,RCC_AHB2ENR1_GPIOAEN,true},
 {&PWR->SVMSR,PWR_SVMSR_ACTVOSRDY,true},{&PWR->SVMSR,PWR_SVMSR_ACTVOS_0,true},
 {&PWR->VOSR,PWR_VOSR_BOOSTEN,true},{&PWR->VOSR,PWR_VOSR_BOOSTRDY,true},
 {&RCC->PLL1CFGR,RCC_PLL1CFGR_PLL1MBOOST_0,false},
 {&PWR->VOSR,PWR_VOSR_VOSRDY,true},{&PWR->VOSR,PWR_VOSR_VOS_0,true},
 {&PWR->SVMCR,PWR_SVMCR_ASV,true},{&SYSCFG->CFGR1,SYSCFG_CFGR1_ANASWVDD,false},
 {&ADC4->CFGR1,ADC4_CFGR1_DMAEN,false},{&ADC4->CFGR1,ADC4_CFGR1_DMACFG,false},
 {&ADC4->CFGR1,ADC_CFGR1_CONT,false},{&DAC1->CR,DAC_CR_EN1,false}
}};}
void badSample(const power::Sample& s) {
 CHECK(s.status==Status::OWNERSHIP);CHECK_FALSE(s.valid);CHECK(s.raw==0);CHECK(s.voltage_v==0.0F);
 CHECK(s.shutdown==Shutdown::UNCONFIRMED);CHECK(fixture::hw.writes==0);
}
}
TEST_CASE("B5 every finite live clock supply and peer guard excludes admission") {fixture::isolated([&] {
 fixture::reset();const auto list=changes();
 for(const auto& c:list){fixture::isolated([&] {fixture::reset();apply(c);power::Reader r;auto b=r.begin();
  CAPTURE(reinterpret_cast<std::uintptr_t>(c.reg));CAPTURE(c.bits);
  CHECK(b.status==Status::OWNERSHIP);CHECK_FALSE(b.ready);CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);
  CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==0);

});}

});}
TEST_CASE("B5 each shared owner clock and supply guard is repeated at runtime") {fixture::isolated([&] {
 fixture::reset();const auto list=changes();
 for(const auto& c:list){fixture::isolated([&] {fixture::reset();power::Reader r;REQUIRE(r.begin().ready);apply(c);
  fixture::clearTrace();auto s=r.read();CAPTURE(reinterpret_cast<std::uintptr_t>(c.reg));CAPTURE(c.bits);badSample(s);

});}

});}
TEST_CASE("B5 each owned ADC mode field and command state is validated before a request") {fixture::isolated([&] {
 fixture::reset();const Change list[]={
  {&ADC1->CR,ADC_CR_ADEN,true},{&ADC1->CR,ADC_CR_ADSTART,false},
  {&ADC1->CR,ADC_CR_ADSTP,false},{&ADC1->CR,ADC_CR_JADSTART,false},
  {&ADC1->CR,ADC_CR_JADSTP,false},{&ADC1->CR,ADC_CR_ADDIS,false},
  {&ADC1->CR,ADC_CR_ADCAL,false},{&ADC1->CR,ADC_CR_DEEPPWD,false},
  {&ADC1->CR,ADC_CR_ADVREGEN,true},{&ADC1->IER,ADC_IER_EOCIE,false},
  {&ADC1->CFGR1,ADC_CFGR1_CONT,false},{&ADC1->CFGR2,ADC_CFGR2_LFTRIG,true},
  {&ADC1->PCSEL,512U,true},{&ADC1->SMPR1,1U<<27,true},{&ADC1->DIFSEL,512U,false},
  {&ADC1->SQR1,1U,false},{&ADC1->SQR2,1U,false},{&ADC1->SQR3,1U,false},{&ADC1->SQR4,1U,false},
  {&ADC1->JSQR,1U,false},{&ADC1->OFR1,1U,false},{&ADC1->OFR2,1U,false},
  {&ADC1->OFR3,1U,false},{&ADC1->OFR4,1U,false},{&ADC1->GCOMP,1U,false},
  {&ADC1->AWD2CR,1U,false},{&ADC1->AWD3CR,1U,false},{&ADC12_COMMON->CCR,0x80000U,true}
 };
 for(const auto& c:list){fixture::isolated([&] {fixture::reset();power::Reader r;REQUIRE(r.begin().ready);apply(c);
  fixture::clearTrace();auto s=r.read();CAPTURE(reinterpret_cast<std::uintptr_t>(c.reg));CAPTURE(c.bits);badSample(s);

});}

});}
TEST_CASE("B5 ready peer devices ADC state and valid pad mask are mandatory") {fixture::isolated([&] {
 for(unsigned i=1;i<5;++i){fixture::isolated([&] {fixture::reset();fixture::hw.ready[i]=false;power::Reader r;
  CHECK(r.begin().status==Status::OWNERSHIP);CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==0);

});}
 fixture::reset();fixture_devices[0].state->init_res=1;power::Reader r;
 CHECK(r.begin().status==Status::OWNERSHIP);CHECK(fixture::hw.writes==0);
 fixture::reset();fixture::gpio_config.port_pin_mask&=~(1U<<4);power::Reader mask;
 CHECK_FALSE(mask.begin().ready);CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==0);

});}
TEST_CASE("B5 failed clock enable status and readback never touch ADC controls") {
 for(unsigned k=0;k<2;++k){fixture::isolated([&] {fixture::reset();if(k==0)fixture::hw.clock_status=-5;else fixture::hw.enable_clock=false;
  power::Reader r;auto b=r.begin();CHECK_FALSE(b.ready);CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);
  CHECK(fixture::hw.writes==0);CHECK(fixture::hw.clock_on==1);CHECK_FALSE(r.read().valid);

});}
}
TEST_CASE("B5 dormant disabled fraction and DAC channel2 preserve valid stock ownership") {fixture::isolated([&] {
 fixture::reset();RCC->PLL1FRACR.value=RCC_PLL1FRACR_PLL1FRACN_0;
 DAC1->CR.value=DAC_CR_EN2;ADC4->CR.value=ADC_CR_ADVREGEN;
 ADC4->ISR.value=ADC_ISR_ADRDY|ADC_ISR_EOC;
 power::Reader r;CHECK(r.begin().ready);CHECK(r.read().valid);
 CHECK(fixture::peek(DAC1->CR)==DAC_CR_EN2);CHECK(fixture::peek(ADC4->CR)==ADC_CR_ADVREGEN);
 CHECK(fixture::hw.irq_enable[1]);

});}

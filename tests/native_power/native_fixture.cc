// Models W1C flags, read-as-set commands and finite native device dispatch.
// Silicon acknowledgements occur independently and can be delayed or denied.
// Independent contract cases link this fixture to the uninspected production CPP.
#include "native_fixture.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <sys/mman.h>
namespace fixture {
Hardware hw;
gpio_driver_config gpio_config{0xffff};
void event(Point p,std::uintptr_t a) { if(hw.hook)hw.hook(p,a); }
void poke(volatile Reg& r,std::uint32_t v){r.value=v;}
std::uint32_t peek(const volatile Reg& r){return r.value;}
void clearTrace(){hw.reads=hw.writes=hw.accesses=hw.micros_calls=hw.ready_reads=0;}
static void acknowledgement(const volatile Reg* r) {
    if(r==&ADC1->ISR) {
        if(hw.ldo_pending&&hw.ldo_after>=0&&++hw.ldo_polls>=unsigned(hw.ldo_after)) {
            ADC1->ISR.value|=ADC_ISR_LDORDY;hw.ldo_pending=false;event(Point::LDO_READY);
        }
        if(hw.enable_pending&&hw.enable_after>=0&&++hw.enable_polls>=unsigned(hw.enable_after)) {
            ADC1->ISR.value|=ADC_ISR_ADRDY;hw.enable_pending=false;event(Point::ENABLE_READY);
        }
        if(hw.conversion_pending&&hw.conversion_after>=0&&++hw.conversion_polls>=unsigned(hw.conversion_after)) {
            ADC1->ISR.value|=hw.completion_flags;ADC1->DR.value=hw.sample;
            ADC1->CR.value&=~ADC_CR_ADSTART;hw.conversion_pending=false;
        }
    }
    if(r==&ADC1->CR) {
        if(hw.cal_pending&&hw.cal_after>=0&&++hw.cal_polls>=unsigned(hw.cal_after)) {
            ADC1->CR.value&=~ADC_CR_ADCAL;hw.cal_pending=false;
            hw.cal_done_us=hw.now;event(Point::CAL_DONE);
        }
        if(hw.stop_pending&&hw.stop_after>=0&&++hw.stop_polls>=unsigned(hw.stop_after)) {
            ADC1->CR.value&=~(ADC_CR_ADSTART|ADC_CR_ADSTP);hw.stop_pending=false;hw.conversion_pending=false;
        }
        if(hw.disable_pending&&hw.disable_after>=0&&++hw.disable_polls>=unsigned(hw.disable_after)) {
            ADC1->CR.value&=~(ADC_CR_ADEN|ADC_CR_ADDIS);hw.disable_pending=false;
        }
    }
}
}
Reg::operator std::uint32_t() const volatile {
    auto a=reinterpret_cast<std::uintptr_t>(this);
    if(!((a>=0x42020000UL&&a<0x42029000UL)||(a>=0x46020000UL&&a<0x46022000UL)||(a>=0x46000000UL&&a<0x46001000UL)))return value;
    if(a>=0x42028000UL&&a<0x42028400UL&&!(RCC->AHB2ENR1.value&RCC_AHB2ENR1_ADC12EN))++fixture::hw.gated_reads;
    ++fixture::hw.reads;++fixture::hw.accesses;
    fixture::acknowledgement(this);
    fixture::event(fixture::Point::ACCESS,reinterpret_cast<std::uintptr_t>(this));
    auto v=value;
    if(this==&ADC1->DR) {
        ++fixture::hw.data_reads;ADC1->ISR.value&=~ADC_ISR_EOC;
        fixture::event(fixture::Point::DATA);
    }
    return v;
}
void Reg::operator=(std::uint32_t v) volatile {
    auto& h=fixture::hw;auto a=reinterpret_cast<std::uintptr_t>(this);
    if(h.writes<h.trace.size())h.trace[h.writes]={a,v,h.now};
    ++h.writes;++h.accesses;
    if(this==&ADC1->ISR) {
        if(!h.freeze_stale)value&=~v;
        if(v==ADC_ISR_EOS)fixture::event(fixture::Point::EOS_CLEAR);
    } else if(this==&ADC1->CR) {
        auto commands=v&ADC_CR_BITS_PROPERTY_RS;
        if(__builtin_popcount(commands)>1)++h.command_errors;
        if(v&ADC_CR_JADSTP)++h.command_errors;
        auto old=value;value=(v&~ADC_CR_BITS_PROPERTY_RS)|(old&ADC_CR_BITS_PROPERTY_RS)|commands;
        if((v&ADC_CR_ADVREGEN)&&!(old&ADC_CR_ADVREGEN)){h.ldo_pending=true;fixture::event(fixture::Point::REGULATOR_START);}
        if(commands&ADC_CR_ADCAL) {
            ++h.cal_count;h.cal_pending=true;fixture::event(fixture::Point::CAL_START);
            if((old&ADC_CR_ADEN)||!(ADC1->ISR.value&ADC_ISR_LDORDY)||!(v&ADC_CR_ADCALLIN)||
               (ADC1->CALFACT.value&(ADC_CALFACT_CAPTURE_COEF|ADC_CALFACT_LATCH_COEF)))++h.command_errors;
        }
        if(commands&ADC_CR_ADEN) {
            ++h.enable_count;h.enable_pending=true;h.enable_us=h.now;fixture::event(fixture::Point::ENABLE_START);
            if(h.cal_pending||h.now-h.cal_done_us<2||!h.dmb||
               (ADC1->ISR.value&ADC_ISR_ADRDY))++h.command_errors;
        }
        if(commands&ADC_CR_ADSTART) {
            ++h.start_count;h.conversion_pending=true;h.conversion_polls=0;h.elapsed_start=h.now;
            if(!(old&ADC_CR_ADEN)||(old&(ADC_CR_ADCAL|ADC_CR_ADDIS|ADC_CR_ADSTP|ADC_CR_JADSTART|ADC_CR_JADSTP)))++h.command_errors;
            fixture::event(fixture::Point::START);
        }
        if(commands&ADC_CR_ADSTP) {
            ++h.stop_count;h.stop_pending=true;fixture::event(fixture::Point::STOP);
            if(!(old&ADC_CR_ADSTART))++h.command_errors;
        }
        if(commands&ADC_CR_ADDIS) {
            ++h.disable_count;h.disable_pending=true;fixture::event(fixture::Point::DISABLE);
            if(!(old&ADC_CR_ADEN)||(old&(ADC_CR_ADSTART|ADC_CR_ADSTP|ADC_CR_ADCAL)))++h.command_errors;
        }
    } else value=v;
    fixture::event(fixture::Point::ACCESS,a);
}
namespace {
device_state states[7]{};
int clockOn(const device* d,clock_control_subsys_t s) {
    ++fixture::hw.clock_on;
    auto* c=static_cast<const stm32_pclken*>(s);
    if(d!=&fixture_devices[2]||c->bus!=140||c->enr!=1024)std::abort();
    if(fixture::hw.clock_status)return fixture::hw.clock_status;
    if(fixture::hw.enable_clock)RCC->AHB2ENR1.value|=RCC_AHB2ENR1_ADC12EN;
    return 0;
}
int clockRate(const device*,clock_control_subsys_t,std::uint32_t* r) {
    ++fixture::hw.clock_rate;*r=fixture::hw.rate;return fixture::hw.rate_status;
}
const clock_control_driver_api clock_api={clockOn,nullptr,nullptr,clockRate,nullptr,nullptr};
}
device fixture_devices[5]={{nullptr,nullptr,&states[0],0},{&fixture::gpio_config,nullptr,&states[1],1},
    {nullptr,&clock_api,&states[2],2},{nullptr,nullptr,&states[3],3},{nullptr,nullptr,&states[4],4}};
device fixture_other_ports[2]={{&fixture::gpio_config,nullptr,&states[5],5},{&fixture::gpio_config,nullptr,&states[6],6}};
bool device_is_ready(const device* d){++fixture::hw.ready_reads;return d&&d->index<5&&fixture::hw.ready[d->index];}
int clock_control_on(const device* d,clock_control_subsys_t s){return clockOn(d,s);}
int clock_control_get_rate(const device* d,clock_control_subsys_t s,std::uint32_t* r){return clockRate(d,s,r);}
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type n){++fixture::hw.reads;return fixture::hw.irq_enable[n==ADC4_IRQn?1:0];}
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type n){++fixture::hw.reads;return fixture::hw.irq_pending[n==ADC4_IRQn?1:0];}
std::uint32_t NVIC_GetActive(IRQn_Type n){++fixture::hw.reads;return fixture::hw.irq_active[n==ADC4_IRQn?1:0];}
void __DMB(){++fixture::hw.dmb;}
unsigned long micros(){++fixture::hw.micros_calls;fixture::event(fixture::Point::CLOCK);auto t=fixture::hw.now;fixture::hw.now+=fixture::hw.tick;fixture::hw.last_clock=t;return t;}
namespace fixture {
void reset() {
    static bool mapped=false;
    if(!mapped){for(auto a:{0x42020000UL,0x42028000UL,0x46020000UL,0x46021000UL,0x46000000UL}) {
        void* p=mmap(reinterpret_cast<void*>(a),4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
        if(p!=reinterpret_cast<void*>(a)){std::perror("native ADC mmap");std::abort();}
    }mapped=true;}
    hw=Hardware{};
    for(auto a:{0x42020000UL,0x42028000UL,0x46020000UL,0x46021000UL,0x46000000UL})std::memset(reinterpret_cast<void*>(a),0,4096);
    for(auto& s:states)s=device_state{};
    gpio_config.port_pin_mask=0xffff;
    ADC1->CR.value=ADC_CR_DEEPPWD;ADC1->CFGR1.value=0x80000000U;
    GPIOA->MODER.value=0xffffffffU;
    RCC->AHB2ENR1.value=RCC_AHB2ENR1_GPIOAEN;
    RCC->CR.value=RCC_CR_MSISON|RCC_CR_MSISRDY|RCC_CR_MSIPLLEN|RCC_CR_MSIPLLSEL|RCC_CR_PLL1ON|RCC_CR_PLL1RDY;
    RCC->ICSCR1.value=RCC_ICSCR1_MSIRGSEL|(4U<<RCC_ICSCR1_MSISRANGE_Pos);
    RCC->CFGR1.value=RCC_CFGR1_SW|RCC_CFGR1_SWS;
    RCC->PLL1CFGR.value=RCC_PLL1CFGR_PLL1SRC_0|RCC_PLL1CFGR_PLL1REN;
    RCC->PLL1DIVR.value=79U|(1U<<RCC_PLL1DIVR_PLL1R_Pos);
    RCC->AHB3ENR.value=RCC_AHB3ENR_ADC4EN|RCC_AHB3ENR_DAC1EN|RCC_AHB3ENR_PWREN;
    RCC->APB3ENR.value=RCC_APB3ENR_SYSCFGEN;
    PWR->SVMSR.value=PWR_SVMSR_ACTVOSRDY|PWR_SVMSR_ACTVOS;
    PWR->SVMCR.value=PWR_SVMCR_ASV;
    PWR->VOSR.value=PWR_VOSR_VOS|PWR_VOSR_VOSRDY|PWR_VOSR_BOOSTEN|PWR_VOSR_BOOSTRDY;
}
}
extern "C" void* __real_malloc(std::size_t);extern "C" void* __real_calloc(std::size_t,std::size_t);
extern "C" void* __real_realloc(void*,std::size_t);extern "C" void __real_free(void*);
extern "C" void* __wrap_malloc(std::size_t n){if(fixture::hw.count_allocations)++fixture::hw.allocations;return __real_malloc(n);}
extern "C" void* __wrap_calloc(std::size_t n,std::size_t s){if(fixture::hw.count_allocations)++fixture::hw.allocations;return __real_calloc(n,s);}
extern "C" void* __wrap_realloc(void* p,std::size_t n){if(fixture::hw.count_allocations)++fixture::hw.allocations;return __real_realloc(p,n);}
extern "C" void __wrap_free(void* p){if(fixture::hw.count_allocations)++fixture::hw.allocations;__real_free(p);}
void* operator new(std::size_t n){return __wrap_malloc(n);}void* operator new[](std::size_t n){return __wrap_malloc(n);}
void operator delete(void* p) noexcept{__wrap_free(p);}void operator delete[](void* p) noexcept{__wrap_free(p);}
void operator delete(void* p,std::size_t) noexcept{__wrap_free(p);}void operator delete[](void* p,std::size_t) noexcept{__wrap_free(p);}

// Models I2C event progression, RXDR/TXDR effects and W1C status independently.
// Requested operations do not imply acknowledgement, completion or bus release.
// Native contract cases link this fixture with opaque production source bytes.
#include "native_fixture.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <sys/mman.h>
namespace fixture {
Hardware hw;
void event(Point p,std::uintptr_t a){if(hw.hook)hw.hook(p,a);}
void poke(volatile Reg& r,std::uint32_t v){r.value=v;}
std::uint32_t peek(const volatile Reg& r){return r.value;}
void clearTrace(){hw.reads=hw.writes=hw.accesses=hw.micros_calls=hw.ready_reads=0;}
static void finishStop(){
    I2C4->ISR.value|=I2C_ISR_STOPF;
    if(!hw.keep_busy)I2C4->ISR.value&=~I2C_ISR_BUSY;
    I2C4->CR2.value&=~I2C_CR2_STOP;
    hw.stop_pending=false;hw.transfer_pending=false;event(Point::STOP);
}
static void acknowledge(const volatile Reg* r){
    if(r!=&I2C4->ISR&&r!=&I2C4->CR2)return;
    if(hw.stop_pending&&hw.stop_after>=0&&++hw.stop_polls>=unsigned(hw.stop_after))finishStop();
    if(hw.start_pending){
        if(hw.start_after>=0&&++hw.phase_polls>=unsigned(hw.start_after)){
            I2C4->CR2.value&=~I2C_CR2_START;I2C4->ISR.value|=I2C_ISR_BUSY;
            hw.start_pending=false;hw.transfer_pending=true;hw.phase_polls=0;event(Point::START_ACK);
        }
        return;
    }
    if(r!=&I2C4->ISR||!hw.transfer_pending)return;
    if(hw.halt_after>=0&&hw.byte_index>=unsigned(hw.halt_after))return;
    if(hw.byte_after<0||++hw.phase_polls<unsigned(hw.byte_after))return;
    if(!hw.remaining){
        if(hw.autoend){hw.stop_pending=true;if(hw.stop_after==1)finishStop();}
        else if(!(I2C4->ISR.value&I2C_ISR_TC)){I2C4->ISR.value|=I2C_ISR_TC;event(Point::TC);}
    }else if(hw.read_phase){
        if(I2C4->ISR.value&I2C_ISR_RXNE)return;
        I2C4->RXDR.value=hw.bytes[hw.byte_index%hw.bytes.size()];I2C4->ISR.value|=I2C_ISR_RXNE;
        if(hw.remaining==1&&hw.autoend&&hw.with_final_stop){
            if(!hw.keep_busy)I2C4->ISR.value&=~I2C_ISR_BUSY;
            I2C4->ISR.value|=I2C_ISR_STOPF;event(Point::LAST_RX);
        }
    }else I2C4->ISR.value|=I2C_ISR_TXIS;
}
static void command(std::uint32_t v,std::uint32_t old){
    if(old&I2C_CR2_START)++hw.command_errors;
    if(v&I2C_CR2_STOP){
        ++hw.stop_count;hw.stop_pending=true;hw.stop_polls=0;
        if((v&I2C_CR2_START)||(I2C4->ISR.value&I2C_ISR_ARLO))++hw.command_errors;
    }
    if(!(v&I2C_CR2_START))return;
    if(!(I2C4->CR1.value&I2C_CR1_PE))++hw.command_errors;
    if(hw.start_count<hw.starts.size())hw.starts[hw.start_count]={v,hw.now};
    ++hw.start_count;hw.start_pending=true;hw.phase_polls=0;hw.byte_index=0;
    hw.remaining=(v&I2C_CR2_NBYTES)>>I2C_CR2_NBYTES_Pos;
    hw.read_phase=(v&I2C_CR2_RD_WRN)!=0;hw.autoend=(v&I2C_CR2_AUTOEND)!=0;
    I2C4->ISR.value&=~(I2C_ISR_TC|I2C_ISR_TXIS);event(Point::START);
}
static std::uint32_t lockedPreserve(const volatile Reg* r,std::uint32_t old,std::uint32_t v){
    if(!(GPIOD->LCKR.value&GPIO_LCKR_LCKK))return v;
    unsigned width=0,first=0,last=16;
    if(r==&GPIOD->MODER||r==&GPIOD->OSPEEDR||r==&GPIOD->PUPDR)width=2;
    if(r==&GPIOD->OTYPER)width=1;
    if(r==&GPIOD->AFR[0]){width=4;last=8;}
    if(r==&GPIOD->AFR[1]){width=4;first=8;}
    if(!width)return v;
    for(unsigned pin=first;pin<last;++pin)if(GPIOD->LCKR.value&(1U<<pin)){
        const auto mask=((1U<<width)-1U)<<(width*(pin-first));v=(v&~mask)|(old&mask);
    }
    return v;
}
}
Reg::operator std::uint32_t() const volatile {
    auto a=reinterpret_cast<std::uintptr_t>(this);
    if(a<0x40000000UL||a>=0x47000000UL)return value;
    auto& h=fixture::hw;++h.reads;++h.accesses;
    if(a>=I2C4_BASE&&a<I2C4_BASE+sizeof(I2C_TypeDef)&&!(RCC->APB1ENR2.value&RCC_APB1ENR2_I2C4EN))++h.gated_reads;
    fixture::acknowledge(this);fixture::event(fixture::Point::ACCESS,a);auto v=value;
    if(this==&I2C4->RXDR){
        if(!(I2C4->ISR.value&I2C_ISR_RXNE)||!h.remaining)++h.command_errors;
        I2C4->ISR.value&=~I2C_ISR_RXNE;++h.rx_count;++h.byte_index;h.phase_polls=0;
        if(h.remaining)--h.remaining;
        if(!h.remaining&&(I2C4->ISR.value&I2C_ISR_STOPF))h.transfer_pending=false;
        fixture::event(fixture::Point::RX);
    }
    return v;
}
void Reg::operator=(std::uint32_t v) volatile {
    auto& h=fixture::hw;auto a=reinterpret_cast<std::uintptr_t>(this);auto old=value;
    if(h.writes<h.trace.size())h.trace[h.writes]={a,v,h.now};
    ++h.writes;++h.accesses;
    if(a==h.ignored_write)return;
    if(this==&I2C4->ICR){
        if(!h.ignore_clear)I2C4->ISR.value&=~v;
        if(v&I2C_ICR_STOPCF)fixture::event(fixture::Point::STOP_CLEAR);
    }else if(this==&I2C4->CR2){value=v;fixture::command(v,old);
    }else if(this==&I2C4->TXDR){
        if(!(I2C4->ISR.value&I2C_ISR_TXIS)||!h.remaining)++h.command_errors;
        if(h.tx_count<h.transmitted.size())h.transmitted[h.tx_count]=static_cast<std::uint8_t>(v);
        ++h.tx_count;++h.byte_index;if(h.remaining)--h.remaining;h.phase_polls=0;
        I2C4->ISR.value&=~I2C_ISR_TXIS;value=v;fixture::event(fixture::Point::TX);
    }else if(this==&I2C4->CR1&&!(v&I2C_CR1_PE)&&(old&I2C_CR1_PE)){
        ++h.disable_count;if(!h.ignore_disable){value=v;I2C4->ISR.value=I2C_ISR_TXE;
            I2C4->CR2.value&=~(I2C_CR2_START|I2C_CR2_STOP);h.start_pending=h.transfer_pending=h.stop_pending=false;}
        fixture::event(fixture::Point::DISABLE);
    }else if(this==&RCC->APB1ENR2){if(!h.ignore_gate)value=v;fixture::event(fixture::Point::GATE);
    }else value=fixture::lockedPreserve(this,old,v);
    fixture::event(fixture::Point::ACCESS,a);
}
namespace {
device_state states[3]{};
int clockOn(const device* d,clock_control_subsys_t s){
    ++fixture::hw.clock_on;const auto c=static_cast<const stm32_pclken*>(s);
    if(d!=&fixture_devices[2]||c->bus!=160||c->enr!=2)std::abort();
    if(fixture::hw.clock_status)return fixture::hw.clock_status;
    if(!fixture::hw.ignore_gate)RCC->APB1ENR2.value|=RCC_APB1ENR2_I2C4EN;
    fixture::event(fixture::Point::GATE);return 0;
}
int clockRate(const device*,clock_control_subsys_t,std::uint32_t* r){
    ++fixture::hw.clock_rate;*r=fixture::hw.rate;return fixture::hw.rate_status;
}
const clock_control_driver_api clock_api={clockOn,nullptr,nullptr,clockRate,nullptr,nullptr};
}
device fixture_devices[3]={{nullptr,nullptr,&states[0],0},{nullptr,nullptr,&states[1],1},{nullptr,&clock_api,&states[2],2}};
bool device_is_ready(const device* d){++fixture::hw.ready_reads;return d&&d->index<3&&fixture::hw.ready[d->index];}
int clock_control_on(const device* d,clock_control_subsys_t s){return clockOn(d,s);}
int clock_control_get_rate(const device* d,clock_control_subsys_t s,std::uint32_t* r){return clockRate(d,s,r);}
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type n){++fixture::hw.irq_reads;return fixture::hw.irq_enable[n==I2C4_EV_IRQn?1:0];}
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type n){++fixture::hw.irq_reads;return fixture::hw.irq_pending[n==I2C4_EV_IRQn?1:0];}
std::uint32_t NVIC_GetActive(IRQn_Type n){++fixture::hw.irq_reads;return fixture::hw.irq_active[n==I2C4_EV_IRQn?1:0];}
void __DMB(){++fixture::hw.dmb;}
unsigned long micros(){++fixture::hw.micros_calls;fixture::event(fixture::Point::CLOCK);auto t=fixture::hw.now;fixture::hw.now+=fixture::hw.tick;fixture::hw.last_clock=t;return t;}
namespace fixture {
void reset(){
    static bool mapped=false;
    if(!mapped){for(auto a:{0x40008000UL,0x42020000UL,0x46020000UL,0x46000000UL}){
        auto p=mmap(reinterpret_cast<void*>(a),4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
        if(p!=reinterpret_cast<void*>(a)){std::perror("native I2C mmap");std::abort();}
    }mapped=true;}
    hw=Hardware{};
    for(auto a:{0x40008000UL,0x42020000UL,0x46020000UL,0x46000000UL})std::memset(reinterpret_cast<void*>(a),0,4096);
    for(auto& s:states)s=device_state{};
    I2C4->ISR.value=I2C_ISR_TXE;GPIOD->MODER.value=0xffffffffU;GPIOD->IDR.value=(1U<<12)|(1U<<13);
    RCC->AHB2ENR1.value=RCC_AHB2ENR1_GPIODEN;
    RCC->CR.value=RCC_CR_MSISON|RCC_CR_MSISRDY|RCC_CR_MSIPLLEN|RCC_CR_MSIPLLSEL|RCC_CR_PLL1ON|RCC_CR_PLL1RDY;
    RCC->ICSCR1.value=RCC_ICSCR1_MSIRGSEL|(4U<<RCC_ICSCR1_MSISRANGE_Pos);
    RCC->CFGR1.value=RCC_CFGR1_SW|RCC_CFGR1_SWS;
    RCC->PLL1CFGR.value=RCC_PLL1CFGR_PLL1SRC_0|RCC_PLL1CFGR_PLL1REN;
    RCC->PLL1DIVR.value=79U|(1U<<RCC_PLL1DIVR_PLL1R_Pos);
    RCC->AHB3ENR.value=RCC_AHB3ENR_PWREN;
    RCC->APB3ENR.value=RCC_APB3ENR_SYSCFGEN;
    PWR->SVMSR.value=PWR_SVMSR_ACTVOSRDY|PWR_SVMSR_ACTVOS;
    PWR->SVMCR.value=PWR_SVMCR_ASV;
    PWR->VOSR.value=PWR_VOSR_VOS|PWR_VOSR_VOSRDY|PWR_VOSR_BOOSTEN|PWR_VOSR_BOOSTRDY;
    for(unsigned i=0;i<hw.bytes.size();++i)hw.bytes[i]=static_cast<std::uint8_t>(0x80+i);
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

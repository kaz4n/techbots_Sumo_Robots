// Models installed GPIO/PWM operations and STM32 timer update behavior.
// Call success is deliberately weaker than fresh active-shadow transfer.
// Native cases inject each status, mode fault and stalled timer independently.
#include "native_fixture.h"
#include "zephyrPinctrl.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <sys/mman.h>
#ifndef NATIVE_NULL_CONFIG
#define NATIVE_NULL_CONFIG 0
#endif
gpio_driver_config fixture_gpio_configs[4]={{0xffff},{0xffff},{0xffff},{0xffff}};
const device fixture_gpio_ports[4]={{&fixture_gpio_configs[0],7},{NATIVE_NULL_CONFIG==1?nullptr:&fixture_gpio_configs[1],8},{&fixture_gpio_configs[2],9},{&fixture_gpio_configs[3],10}};
namespace { const std::uint32_t pwm_configs[7]={1,1,1,1,1,1,1}; }
const device fixture_pwm_devices[7]={{NATIVE_NULL_CONFIG==2?nullptr:&pwm_configs[0],0},{NATIVE_NULL_CONFIG==3?nullptr:&pwm_configs[1],1},{NATIVE_NULL_CONFIG==4?nullptr:&pwm_configs[2],2},{&pwm_configs[3],3},{&pwm_configs[4],4},{&pwm_configs[5],5},{&pwm_configs[6],6}};
namespace fixture {
Hardware hw;
TIM_TypeDef* timer(unsigned i) { return i==0?TIM1:i==1?TIM3:TIM4; }
unsigned timerIndex(const TIM_TypeDef* t) { if(t==TIM1)return 0;if(t==TIM3)return 1;if(t==TIM4)return 2;std::abort(); }
unsigned record(Kind k,unsigned i,std::uint32_t a,std::uint32_t b) {
    if(hw.trace_size<hw.trace.size())hw.trace[hw.trace_size++]={k,i,a,b};
    return ++hw.calls[k];
}
bool fails(Kind k,unsigned ordinal) { return hw.fail_ordinal[k]>=0 && ordinal==static_cast<unsigned>(hw.fail_ordinal[k]); }
void transfer(unsigned i) {
    const auto* t=timer(i);
    hw.active[i][0]=t->CCR1;hw.active[i][1]=t->CCR2;hw.active[i][2]=t->CCR3;hw.active[i][3]=t->CCR4;
    hw.active_arr[i]=t->ARR;
    timer(i)->SR|=TIM_SR_UIF;
    hw.update_mask|=1U<<i;
}
void reset() {
    static bool mapped=false;
    if(!mapped) {
        for(const auto address:{0x40000000UL,0x40012000UL,0x42020000UL}) {
            void* p=mmap(reinterpret_cast<void*>(address),4096,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
            if(p!=reinterpret_cast<void*>(address)){std::perror("native fixture mmap");std::abort();}
        }
        mapped=true;
    }
    hw=Hardware{};
    std::fill(std::begin(hw.fail_ordinal),std::end(hw.fail_ordinal),-1);
    for(unsigned i=0;i<3;++i){std::memset(timer(i),0,sizeof(TIM_TypeDef));hw.fresh_after[i]=1;}
    std::memset(GPIOB,0,sizeof(GPIO_TypeDef));
    for(auto& c:fixture_gpio_configs)c.port_pin_mask=0xffff;
    for(unsigned i=7;i<11;++i)hw.ready[i]=true;
    hw.rate[0]=2500000;hw.rate[1]=32000000;hw.rate[2]=32000000;
}
void clearTrace() { std::fill(std::begin(hw.calls),std::end(hw.calls),0);hw.trace_size=0; }
}
bool device_is_ready(const device* d) {
    auto n=fixture::record(fixture::READY,d?d->index:99);
    return d&&d->index<11&&fixture::hw.ready[d->index]&&!fixture::fails(fixture::READY,n);
}
int gpio_pin_configure_dt(const gpio_dt_spec* s,gpio_flags_t flags) {
    auto n=fixture::record(fixture::CONFIGURE,s->port?s->port->index:99,s->pin,flags);
    if(fixture::fails(fixture::CONFIGURE,n))return fixture::hw.fail_status;
    if(s->port!=&fixture_gpio_ports[1]||s->pin!=9||s->dt_flags||flags!=GPIO_OUTPUT_LOW)std::abort();
    GPIOB->ODR&=~(1U<<9);GPIOB->IDR&=~(1U<<9);
    GPIOB->MODER=(GPIOB->MODER&~(3U<<18))|(1U<<18);
    GPIOB->OTYPER&=~(1U<<9);GPIOB->PUPDR&=~(3U<<18);
    return 0;
}
int gpio_pin_set_raw(const device* d,gpio_pin_t pin,int value) {
    auto n=fixture::record(fixture::WRITE_GPIO,d?d->index:99,pin,static_cast<unsigned>(value));
    if(d!=&fixture_gpio_ports[1]||pin!=9||(value!=0&&value!=1))std::abort();
    if(value && (fixture::hw.all_write_mask!=15U||fixture::hw.update_mask!=7U))fixture::hw.unsafe_high=true;
    if(!value){fixture::hw.all_write_mask=0;fixture::hw.update_mask=0;}
    if(fixture::fails(fixture::WRITE_GPIO,n))return fixture::hw.fail_status;
    GPIOB->ODR=(GPIOB->ODR&~(1U<<9))|(static_cast<unsigned>(value)<<9);
    GPIOB->IDR=(GPIOB->IDR&~(1U<<9))|(static_cast<unsigned>(value)<<9);
    return 0;
}
int gpio_pin_get_raw(const device* d,gpio_pin_t pin) {
    auto n=fixture::record(fixture::READ_GPIO,d?d->index:99,pin);
    if(d!=&fixture_gpio_ports[1]||pin!=9)std::abort();
    if(fixture::fails(fixture::READ_GPIO,n))return fixture::hw.fail_status;
    if((GPIOB->ODR&(1U<<9))&&fixture::hw.high_read_override!=-999)return fixture::hw.high_read_override;
    return fixture::hw.read_override!=-999?fixture::hw.read_override:static_cast<int>((GPIOB->IDR>>9)&1U);
}
namespace zephyr { namespace arduino {
int init_dev_apply_channel_pinctrl(const device* d,std::size_t index) {
    auto n=fixture::record(fixture::ROUTE,d?d->index:99,static_cast<unsigned>(index));
    if((GPIOB->ODR&(1U<<9))!=0)fixture::hw.writes_while_high=true;
    if(fixture::fails(fixture::ROUTE,n))return fixture::hw.fail_status;
    if(static_cast<int>(n)==fixture::hw.route_without_ready)return 0;
    if(!d||d->index>2)std::abort();
    auto i=d->index;
    if(!fixture::hw.ready[i]) {
        fixture::hw.ready[i]=true;fixture::hw.timer_init[i]++;
        auto* t=fixture::timer(i);t->CR1=1;t->PSC=i==0?63:4;t->ARR=0;
        if(i==0)t->BDTR=0x8000;
        volatile std::uint32_t* initial[]={&t->CR1,&t->CR2,&t->SMCR,&t->DIER,&t->PSC,&t->ARR,&t->CCMR1,&t->CCMR2,&t->CCER,&t->RCR,&t->BDTR};
        if(fixture::hw.init_bad_register>=0)*initial[fixture::hw.init_bad_register]^=fixture::hw.init_flip;
    }
    return 0;
}
}}
int pwm_get_cycles_per_sec(const device* d,std::uint32_t channel,std::uint64_t* cycles) {
    auto n=fixture::record(fixture::RATE,d?d->index:99,channel);
    if(fixture::fails(fixture::RATE,n))return fixture::hw.fail_status;
    if(!d||d->index>2||!cycles)std::abort();
    *cycles=fixture::hw.rate[d->index];return 0;
}
int pwm_set_cycles(const device* d,std::uint32_t channel,std::uint32_t period,std::uint32_t pulse,pwm_flags_t flags) {
    auto n=fixture::record(fixture::PWM,d?d->index:99,channel,pulse);
    if((GPIOB->ODR&(1U<<9))!=0)fixture::hw.writes_while_high=true;
    if(fixture::fails(fixture::PWM,n))return fixture::hw.fail_status;
    if(!d||d->index>2||!fixture::hw.ready[d->index]||flags||pulse>period||!period)std::abort();
    unsigned i=d->index;unsigned slot=i==0?1:i==2?3:channel==3?0:2;
    if(channel!=(i==0?4:i==2?3:channel)||channel<3||channel>4)std::abort();
    auto* t=fixture::timer(i);unsigned shift=channel==3?0:8;
    bool was_enabled=(t->CCER&(1U<<(channel==3?8:12)))!=0;
    if(channel==3)t->CCR3=pulse;else t->CCR4=pulse;
    t->ARR=period-1;t->CR1|=0x80;t->CCMR2|=0x68U<<shift;t->CCER|=1U<<(channel==3?8:12);
    fixture::hw.all_write_mask|=1U<<slot;
    if(!was_enabled){fixture::transfer(i);fixture::hw.update_mask=0;} // Native first-enable UG is stale.
    return 0;
}
void LL_TIM_ClearFlag_UPDATE(TIM_TypeDef* t) {
    auto i=fixture::timerIndex(t);fixture::record(fixture::CLEAR,i);
    fixture::hw.clears[i]++;fixture::hw.polls[i]=0;
    // rc_w0: the U5 LL writes ~UIF, preserving every other status bit.
    if(fixture::hw.race_cleared)fixture::transfer(i);
    t->SR&=~TIM_SR_UIF;
    fixture::hw.update_mask&=~(1U<<i);
    if(fixture::hw.race_survives)fixture::transfer(i);
}
std::uint32_t LL_TIM_IsActiveFlag_UPDATE(const TIM_TypeDef* t) {
    auto i=fixture::timerIndex(t);auto n=fixture::record(fixture::POLL,i);
    auto& h=fixture::hw;h.polls[i]++;
    h.now+=h.ticks_per_poll;
    if(h.use_event_elapsed)h.now=h.event_elapsed;
    if(h.corrupt_reg&&h.corrupt_at_poll==n)*h.corrupt_reg=h.corrupt_value;
    if(h.lose_ready_at_poll==n)h.ready[h.lose_ready_index]=false;
    if(h.fresh_after[i]>=0 && h.polls[i]==static_cast<unsigned>(h.fresh_after[i]))fixture::transfer(i);
    return (t->SR&TIM_SR_UIF)!=0;
}
unsigned long micros() { fixture::record(fixture::CLOCK);return fixture::hw.now; }
extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t,std::size_t);
extern "C" void* __real_realloc(void*,std::size_t);
extern "C" void __real_free(void*);
extern "C" void* __wrap_malloc(std::size_t n){if(fixture::hw.count_allocations)++fixture::hw.allocations;return __real_malloc(n);}
extern "C" void* __wrap_calloc(std::size_t n,std::size_t s){if(fixture::hw.count_allocations)++fixture::hw.allocations;return __real_calloc(n,s);}
extern "C" void* __wrap_realloc(void* p,std::size_t n){if(fixture::hw.count_allocations)++fixture::hw.allocations;return __real_realloc(p,n);}
extern "C" void __wrap_free(void* p){if(fixture::hw.count_allocations)++fixture::hw.deallocations;__real_free(p);}
void* operator new(std::size_t n){if(fixture::hw.count_allocations)++fixture::hw.allocations;void* p=__real_malloc(n);if(!p)std::abort();return p;}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept {if(fixture::hw.count_allocations)++fixture::hw.deallocations;__real_free(p);}
void operator delete[](void* p) noexcept {::operator delete(p);}
void operator delete(void* p,std::size_t) noexcept {::operator delete(p);}
void operator delete[](void* p,std::size_t) noexcept {::operator delete(p);}

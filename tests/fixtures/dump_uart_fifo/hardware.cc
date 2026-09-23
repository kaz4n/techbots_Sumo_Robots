// Models register observations and independent115200 8N1 byte completion for D117.
// FIFO room reflects eight queued entries plus one shifting byte; TC waits for stop-bit completion.
// This is a deterministic reference model, not hardware timing or source inspection.
#include "fixture.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <sys/mman.h>

namespace fifo_test {
Hardware hw;
unsigned checks=0,failures=0;
device_state states[4]={{0,false},{0,true},{0,true},{0,true}};
int api=1;
gpio_driver_config gpio_metadata{0xffffU};
int configure(const device*,gpio_pin_t,gpio_flags_t){return 0;}
int read(const device*,gpio_port_value_t*){return 0;}
gpio_driver_api gpio_api{configure,read};
stm32_pclken clocks{168U,0U,64U};
pinctrl_dev_config pins{1U};
void irq(const device*){}
uart_config settings{115200U,0U,1U,3U,0U};
uart_stm32_data uart_data{&settings,nullptr,nullptr};
uart_stm32_config metadata{LPUART1,&dump_devices[2],{&dump_devices[3],4102U},
    &clocks,1U,false,false,false,false,false,0U,0U,false,false,&pins,irq};
void verify(bool value,const char* text,unsigned line) {
    ++checks;if(value)return;
    if(failures++<30)std::fprintf(stderr,"line%u: %s\n",line,text);
}
void map(std::uintptr_t address) {
    auto* result=mmap(reinterpret_cast<void*>(address&~std::uintptr_t(4095)),4096,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    if(result==MAP_FAILED)std::abort();
}
void initialize() {
    map(0x46002400);map(0x42021800);map(0x46020c00);
    hw.submitted.reserve(2097152);hw.emitted.reserve(2097152);hw.trace.reserve(1024);
    RCC->APB3ENR.value=RCC_APB3ENR_LPUART1EN;RCC->AHB2ENR1.value=RCC_AHB2ENR1_GPIOGEN;
    GPIOG->MODER.value=2U<<14U;GPIOG->AFR[0].value=8U<<28U;
    LPUART1->CR1.value=USART_CR1_UE|USART_CR1_TE|USART_CR1_RE;
    LPUART1->BRR.value=355556U;LPUART1->ISR.value=USART_ISR_TEACK|USART_ISR_TC|USART_ISR_TXE;
}
void synchronize() {
    const auto time=hw.last*115200ULL;
    while(hw.shifting && !hw.frozen_serial && hw.finish<=time) {
        hw.emitted.push_back(hw.shifting_byte);
        if(hw.count) {
            hw.shifting_byte=hw.queue[hw.head];hw.head=(hw.head+1)%8;--hw.count;
            hw.finish+=10000000ULL;
        } else hw.shifting=false;
    }
    auto& flags=LPUART1->ISR.value;flags&=~(USART_ISR_TXE|USART_ISR_TC);
    const unsigned capacity=(LPUART1->CR1.value&USART_CR1_FIFOEN)?8U:1U;
    if(hw.count<capacity)flags|=USART_ISR_TXE;
    if(!hw.shifting && !hw.count)flags|=USART_ISR_TC;
}
void moveTime(std::uint64_t value) {hw.now=value;hw.last=value;synchronize();}
void corrupt(unsigned kind) {
    switch(kind) {
    case 0:hw.control=1;break;
    case 1:hw.ipsr=16;break;
    case 2:metadata.fifo_enable=true;break;
    case 3:hw.irq_enabled=1;break;
    case 4:RCC->PLL1DIVR.value^=1U;break;
    case 5:LPUART1->AUTOCR.value=1;break;
    case 6:LPUART1->AUTOCR.value=1U<<31;break;
    case 7:LPUART1->CR3.value=USART_CR3_DMAT;break;
    case 8:LPUART1->CR1.value^=USART_CR1_FIFOEN;break;
    case 9:hw.ready=0;break;
    case 10:hw.ready=-5;break;
    case 11:hw.irq_pending=1;break;
    case 12:hw.irq_active=1;break;
    case 13:GPIOG->AFR[0].value=0;break;
    default:LPUART1->BRR.value^=1U;break;
    }
}
void injectSetup() {
    if(hw.fault_fired || !hw.target_stage || hw.cr1_writes!=hw.target_stage)return;
    hw.fault_fired=true;
    switch(hw.fault_kind) {
    case 0:LPUART1->CR1.value=hw.target_stage==1?(USART_CR1_UE|USART_CR1_TE|USART_CR1_RE):
                hw.target_stage==2?0U:(USART_CR1_TE|USART_CR1_FIFOEN);break;
    case 1:LPUART1->CR1.value=0x80000000U;break;
    case 2:LPUART1->ISR.value&=~USART_ISR_TEACK;break;
    case 3:corrupt(5);break;
    case 4:corrupt(0);break;
    case 5:corrupt(2);break;
    case 6:corrupt(3);break;
    case 7:corrupt(4);break;
    case 8:LPUART1->CR1.value=0x80000000U;corrupt(0);break;
    case 9:hw.ready=-5;break;
    default:std::abort();
    }
}
void storeByte(unsigned char value) {
    synchronize();VERIFY(hw.mask==1U);VERIFY(hw.control==0U&&hw.ipsr==0U);
    if(hw.enforce_budget)VERIFY(std::uint32_t(hw.last)-hw.call_started<80U);
    hw.submitted.push_back(value);
    if(!hw.shifting) {hw.shifting=true;hw.shifting_byte=value;hw.finish=hw.last*115200ULL+10000000ULL;}
    else if(hw.count<8U) {hw.queue[(hw.head+hw.count)%8]=value;++hw.count;}
    else ++hw.overflow;
    hw.max_queue=std::max(hw.max_queue,hw.count);
    if(hw.live_after_tdr==hw.submitted.size())corrupt(hw.live_kind);
    synchronize();
}
}
device dump_devices[4]={{&fifo_test::metadata,&fifo_test::uart_data,&fifo_test::api,&fifo_test::states[0]},
    {&fifo_test::gpio_metadata,&fifo_test::api,&fifo_test::gpio_api,&fifo_test::states[1]},
    {&fifo_test::api,&fifo_test::api,&fifo_test::api,&fifo_test::states[2]},
    {&fifo_test::api,&fifo_test::api,&fifo_test::api,&fifo_test::states[3]}};
bool dump_clock_good=true;
Reg::operator std::uint32_t() const volatile {
    using namespace fifo_test;++hw.reads;
    if(this==&LPUART1->RDR)++hw.rdr_reads;
    if(this==&LPUART1->ISR)synchronize();
    if(this==&LPUART1->CR1 && hw.await_readback) {
        VERIFY(!hw.await_dmb);hw.trace.push_back({'R',value});hw.await_readback=false;
    }
    return value;
}
void Reg::operator=(std::uint32_t v) volatile {
    using namespace fifo_test;++hw.writes;value=v;
    if(this==&LPUART1->CR1) {
        VERIFY(hw.mask==1U);VERIFY(!hw.await_dmb&&!hw.await_readback);
        ++hw.cr1_writes;hw.trace.push_back({'W',v});hw.await_dmb=true;hw.await_readback=true;
        if(!(v&USART_CR1_UE)) {hw.shifting=false;hw.count=0;hw.head=0;LPUART1->ISR.value&=~USART_ISR_TEACK;}
        else if(v&USART_CR1_TE)LPUART1->ISR.value|=USART_ISR_TEACK;
        if(hw.cleanup_corrupt&&hw.fault_fired&&v==0)LPUART1->CR1.value=0x40000000U;
    } else if(this==&LPUART1->TDR) {VERIFY(!hw.setup);storeByte(static_cast<unsigned char>(v));}
    else ++hw.forbidden_writes;
}
unsigned long micros() {
    using namespace fifo_test;++hw.clocks;hw.last=hw.now;synchronize();hw.now+=hw.step;
    return static_cast<std::uint32_t>(hw.last);
}
std::uint32_t __get_CONTROL(){++fifo_test::hw.context_queries;return fifo_test::hw.control;}
std::uint32_t __get_IPSR(){++fifo_test::hw.context_queries;return fifo_test::hw.ipsr;}
std::uint32_t __get_PRIMASK(){return fifo_test::hw.mask;}
void __disable_irq(){fifo_test::hw.mask=1;}
void __set_PRIMASK(std::uint32_t value){fifo_test::hw.mask=value;}
void __DMB(){using namespace fifo_test;if(hw.await_dmb){hw.trace.push_back({'B',0});hw.await_dmb=false;injectSetup();}}
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type n){VERIFY(n==LPUART1_IRQn);return fifo_test::hw.irq_enabled;}
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type n){VERIFY(n==LPUART1_IRQn);return fifo_test::hw.irq_pending;}
std::uint32_t NVIC_GetActive(IRQn_Type n){VERIFY(n==LPUART1_IRQn);return fifo_test::hw.irq_active;}
void NVIC_DisableIRQ(IRQn_Type n){VERIFY(n==LPUART1_IRQn);++fifo_test::hw.disabled;fifo_test::hw.irq_enabled=0;}
void NVIC_ClearPendingIRQ(IRQn_Type n){VERIFY(n==LPUART1_IRQn);++fifo_test::hw.cleared;fifo_test::hw.irq_pending=0;}
bool device_is_ready(const device* dev){return dev&&dev->state&&dev->state->initialized&&dev->state->init_res==0;}
int device_init(const device* dev){using namespace fifo_test;++hw.init;if(!hw.init_result)dev->state->initialized=true;
    if(hw.post_init_fault==1)metadata.fifo_enable=true;
    return hw.init_result;}
int gpio_pin_configure_dt(const gpio_dt_spec* s,gpio_flags_t flags){using namespace fifo_test;++hw.configure;
    VERIFY(s->port==&dump_devices[1]&&s->pin==13);VERIFY(flags==(GPIO_INPUT|GPIO_PULL_DOWN));
    GPIOG->PUPDR.value|=2U<<26U;return 0;}
int gpio_pin_get_dt(const gpio_dt_spec* s){using namespace fifo_test;++hw.ready_calls;
    VERIFY(s->port==&dump_devices[1]&&s->pin==13);return hw.ready;}

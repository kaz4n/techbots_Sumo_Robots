// Models exact GPIO configuration effects separately from native return status.
// Physical levels, clocks and ownership can change at each observed boundary.
// Fork-isolated tests preserve the real driver's boot-lifetime static claim.
#include "native_fixture.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <sys/mman.h>
namespace fixture {
Hardware hw;
gpio_driver_config configs[3]={{0xffff},{0xffff},{0xffff}};
GPIO_TypeDef* port(unsigned p){return p==1?GPIOA:GPIOB;}
unsigned padBit(unsigned p){constexpr unsigned b[]={3,12,2,4};return b[p];}
void event(Point p,unsigned i){if(hw.hook)hw.hook(p,i);}
void setField(volatile Reg& r,unsigned pos,unsigned value,unsigned width){r.value=(r.value&~(((1U<<width)-1U)<<pos))|(value<<pos);}
void setMode(unsigned p,unsigned m){setField(port(p)->MODER,padBit(p)*2U,m);}
unsigned mode(unsigned p){return (port(p)->MODER.value>>(padBit(p)*2U))&3U;}
void neutral(unsigned p){auto* g=port(p);const auto n=padBit(p);setMode(p,0);setField(g->PUPDR,n*2,0);setField(g->OSPEEDR,n*2,0);g->OTYPER.value&=~(1U<<n);}
}
namespace {
device_state states[3]{};
gpio_driver_data datas[3]{};
unsigned corner(const device* d,gpio_pin_t n){
 for(unsigned i=0;i<4;++i)if(d==&fixture_devices[i==1?0:1]&&n==fixture::padBit(i))return i;
 std::abort();
}
int configure(const device* d,gpio_pin_t n,gpio_flags_t flags){
 using namespace fixture;const auto p=corner(d,n);const auto index=hw.config_calls++;
 if(index>=64)std::abort();
 event(Point::CONFIG_BEFORE,p);
 const auto before=hw.now;const auto status=hw.configure_status[index];
 if(flags!=GPIO_INPUT&&flags!=GPIO_OUTPUT_HIGH){++hw.invalid_ops;return -95;}
 if(hw.configure_effect[index]) {
  auto* g=port(p);const auto pin=padBit(p);
  if(flags==GPIO_OUTPUT_HIGH)g->ODR.value|=1U<<pin;
  neutral(p);if(flags==GPIO_OUTPUT_HIGH)setMode(p,1);
 }
 hw.now+=hw.configure_us;event(Point::CONFIG_AFTER,p);
 hw.operations[index]={p,flags,before,hw.now,status};return status;
}
int portGet(const device*,gpio_port_value_t*){return 0;}
int portSet(const device*,gpio_port_pins_t){++fixture::hw.set_calls;return 0;}
int portClear(const device*,gpio_port_pins_t){++fixture::hw.set_calls;return 0;}
}
namespace fixture {gpio_driver_api apis[3]={{configure,portGet,portSet,portClear},{configure,portGet,portSet,portClear},{configure,portGet,portSet,portClear}};}
device fixture_devices[3]={{&fixture::configs[0],&datas[0],&fixture::apis[0],&states[0],0},
 {&fixture::configs[1],&datas[1],&fixture::apis[1],&states[1],1},
 {&fixture::configs[2],&datas[2],&fixture::apis[2],&states[2],2}};
device fixture_unknown_device={&fixture::configs[2],&datas[2],&fixture::apis[2],&states[2],2};
bool device_is_ready(const device* d){++fixture::hw.ready_reads;return d&&d->index<3&&fixture::hw.ready[d->index];}
int gpio_pin_configure_dt(const gpio_dt_spec* s,gpio_flags_t f){return static_cast<const gpio_driver_api*>(s->port->api)->pin_configure(s->port,s->pin,f|s->dt_flags);}
int gpio_pin_set_raw(const device*,gpio_pin_t,int){++fixture::hw.set_calls;return 0;}
int gpio_pin_get_raw(const device* d,gpio_pin_t n){
 using namespace fixture;const auto p=corner(d,n);++hw.get_calls;++hw.gets[p];event(Point::GET_BEFORE,p);
 const int value=mode(p)==1?hw.charge_values[p]:hw.values[p];hw.now+=hw.read_us;event(Point::GET_AFTER,p);return value;
}
std::uint32_t NVIC_GetEnableIRQ(IRQn_Type n){++fixture::hw.irq_reads;return (fixture::hw.irq_enabled>>n)&1U;}
std::uint32_t NVIC_GetPendingIRQ(IRQn_Type n){++fixture::hw.irq_reads;return (fixture::hw.irq_pending>>n)&1U;}
std::uint32_t NVIC_GetActive(IRQn_Type n){++fixture::hw.irq_reads;return (fixture::hw.irq_active>>n)&1U;}
unsigned long micros(){using namespace fixture;++hw.clocks;event(Point::CLOCK);const auto t=hw.now;hw.now+=hw.clock_step;return t;}
Reg::operator std::uint32_t() const volatile {
 auto a=reinterpret_cast<std::uintptr_t>(this);++fixture::hw.reg_reads;
 if(a>=0x42020000UL&&a<0x42020800UL){
  const auto mask=a<0x42020400UL?RCC_AHB2ENR1_GPIOAEN:RCC_AHB2ENR1_GPIOBEN;
  if(!(RCC->AHB2ENR1.value&mask))++fixture::hw.gated_reads;
 }
 fixture::event(fixture::Point::ACCESS);return value;
}
void Reg::operator=(std::uint32_t v) volatile {++fixture::hw.reg_writes;value=v;fixture::event(fixture::Point::ACCESS);}
namespace fixture {
void reset(){
 static bool mapped=false;
 if(!mapped){for(auto a:{0x42020000UL,0x46020000UL,0x46022000UL,0xE0044000UL}){
  void* p=mmap(reinterpret_cast<void*>(a),4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
  if(p!=reinterpret_cast<void*>(a)){std::perror("native QTR mmap");std::abort();}
 }mapped=true;}
 hw=Hardware{};std::fill(std::begin(hw.configure_effect),std::end(hw.configure_effect),true);
 for(auto a:{0x42020000UL,0x46020000UL,0x46022000UL,0xE0044000UL})std::memset(reinterpret_cast<void*>(a),0,4096);
 for(unsigned i=0;i<3;++i){states[i]={0,true};datas[i]={0};configs[i]={0xffff};apis[i]={configure,portGet,portSet,portClear};fixture_devices[i]={&configs[i],&datas[i],&apis[i],&states[i],i};}
 RCC->AHB2ENR1.value=RCC_AHB2ENR1_GPIOAEN|RCC_AHB2ENR1_GPIOBEN;
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

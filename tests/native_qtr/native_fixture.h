// Defines deterministic native events independently of the QTR implementation.
// Fault injection can change status, time, physical level or register ownership.
// All tests call only the public driver interface and inspect observable evidence.
#pragma once
#include "native_cmsis.h"
#include <zephyr/drivers/gpio.h>
#include <array>
namespace fixture {
enum class Point { CONFIG_BEFORE, CONFIG_AFTER, GET_BEFORE, GET_AFTER, CLOCK, ACCESS };
struct Operation { unsigned pad; gpio_flags_t flags; std::uint32_t before,after; int status; };
struct Hardware {
 std::uint32_t now=1000U,clock_step=0U,configure_us=0U,read_us=0U;
 unsigned clocks=0,reg_reads=0,reg_writes=0,gated_reads=0,ready_reads=0,irq_reads=0;
 unsigned config_calls=0,get_calls=0,set_calls=0,allocations=0,invalid_ops=0;
 bool count_allocations=false,ready[3]={true,true,true};
 std::uint32_t irq_enabled=0,irq_pending=0,irq_active=0;
 int values[4]={0,0,0,0};
 int charge_values[4]={1,1,1,1};
 int configure_status[64]={};
 bool configure_effect[64]={};
 unsigned gets[4]={};
 void (*hook)(Point,unsigned)=nullptr;
 std::array<Operation,256> operations{};
};
extern Hardware hw;
extern gpio_driver_config configs[3];
extern gpio_driver_api apis[3];
GPIO_TypeDef* port(unsigned);
unsigned padBit(unsigned);
void reset();
void event(Point,unsigned=0);
void setMode(unsigned,unsigned);
void setField(volatile Reg&,unsigned,unsigned,unsigned=2);
unsigned mode(unsigned);
void neutral(unsigned);
struct AllocationGuard { AllocationGuard(){hw.count_allocations=true;} ~AllocationGuard(){hw.count_allocations=false;} };
}

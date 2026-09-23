// Declares the independent deterministic ADC hardware and observation controls.
// Flags and command acknowledgements are separate from a requested operation.
// Contract cases inject boundary times and ownership changes without driver access.
#pragma once
#include "stm32u5xx_ll_adc.h"
#include "stm32u5xx_ll_gpio.h"
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/clock_control/stm32_clock_control.h>
#include <array>
#include <cstdint>
namespace fixture {
enum class Point { ACCESS, LDO_READY, CAL_DONE, ENABLE_READY, START, DATA, EOS_CLEAR, STOP, DISABLE, CLOCK, REGULATOR_START, CAL_START, ENABLE_START };
struct Write { std::uintptr_t address; std::uint32_t value,time; };
struct Hardware {
    std::uint32_t now=0, tick=1, sample=8192, elapsed_start=0;
    unsigned accesses=0, reads=0, writes=0, micros_calls=0, data_reads=0, gated_reads=0;
    std::uint32_t last_clock=0;
    unsigned start_count=0, stop_count=0, disable_count=0, cal_count=0, enable_count=0;
    unsigned ldo_polls=0, cal_polls=0, enable_polls=0, conversion_polls=0;
    unsigned stop_polls=0, disable_polls=0, dmb=0, command_errors=0;
    unsigned allocations=0, clock_on=0, clock_rate=0, ready_reads=0;
    std::uint32_t cal_done_us=0, enable_us=0;
    int ldo_after=1, cal_after=2, enable_after=1, conversion_after=1;
    int stop_after=1, disable_after=1;
    int clock_status=0, rate_status=0;
    std::uint32_t rate=160000000U, completion_flags=ADC_ISR_EOC|ADC_ISR_EOS;
    bool enable_clock=true, count_allocations=false, freeze_stale=false;
    bool ready[5]={false,true,true,true,true};
    bool irq_enable[2]={false,true},irq_pending[2]={false,false},irq_active[2]={false,false};
    bool ldo_pending=false,cal_pending=false,enable_pending=false,conversion_pending=false;
    bool stop_pending=false,disable_pending=false;
    void (*hook)(Point, std::uintptr_t)=nullptr;
    std::array<Write,1000> trace{};
};
extern Hardware hw;
extern gpio_driver_config gpio_config;
void reset();
void clearTrace();
void event(Point,std::uintptr_t=0);
void poke(volatile Reg&,std::uint32_t);
std::uint32_t peek(const volatile Reg&);
struct AllocationGuard {
    AllocationGuard(){hw.count_allocations=true;}
    ~AllocationGuard(){hw.count_allocations=false;}
};
}

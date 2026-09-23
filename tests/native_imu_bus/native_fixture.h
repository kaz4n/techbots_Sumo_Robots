// Declares independent I2C4 hardware progression and fault-injection controls.
// TXIS, TC, RXNE and STOP acknowledgements occur separately from register requests.
// Contract tests observe transfer order, deadlines, cleanup and resource ownership.
#pragma once
#include "stm32u5xx_ll_i2c.h"
#include "stm32u5xx_ll_gpio.h"
#include "stm32u5xx_ll_rcc.h"
#include <zephyr/device.h>
#include <zephyr/drivers/clock_control/stm32_clock_control.h>
#include <array>
#include <cstdint>
namespace fixture {
enum class Point { ACCESS, CLOCK, START, START_ACK, TX, RX, TC, LAST_RX, STOP, STOP_CLEAR, DISABLE, GATE };
struct Write { std::uintptr_t address; std::uint32_t value,time; };
struct Start { std::uint32_t cr2,time; };
struct Hardware {
    std::uint32_t now=0,tick=1,last_clock=0;
    unsigned accesses=0,reads=0,writes=0,micros_calls=0,ready_reads=0;
    unsigned gated_reads=0,command_errors=0,irq_reads=0,dmb=0,allocations=0;
    unsigned clock_on=0,clock_rate=0;
    int clock_status=0,rate_status=0;
    std::uint32_t rate=160000000U;
    unsigned start_count=0,tx_count=0,rx_count=0,stop_count=0,disable_count=0;
    unsigned phase_polls=0,stop_polls=0,byte_index=0,remaining=0;
    int start_after=1,byte_after=1,stop_after=1,halt_after=-1;
    bool start_pending=false,stop_pending=false,read_phase=false,autoend=false;
    bool transfer_pending=false,with_final_stop=true,keep_busy=false;
    bool ignore_disable=false,ignore_gate=false,ignore_clear=false,count_allocations=false;
    bool ready[3]={false,true,true};
    bool irq_enable[2]={false,false},irq_pending[2]={false,false},irq_active[2]={false,false};
    std::uintptr_t ignored_write=0;
    std::array<std::uint8_t,15> bytes{};
    std::array<std::uint8_t,64> transmitted{};
    std::array<Write,2048> trace{};
    std::array<Start,16> starts{};
    void (*hook)(Point,std::uintptr_t)=nullptr;
};
extern Hardware hw;
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

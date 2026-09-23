// Defines independent D117 observed hardware and an eight-entry serial FIFO model.
// Time, injected faults and emitted bytes belong to the fixture, never native private state.
// Fresh subprocesses isolate actual lifetime ownership for normal and sanitizer cases.
#pragma once
#include "hal/dump_uart_unoq.h"
#include "app/dump_port.h"
#include "uart_stm32.h"
#include "stm32u5xx_ll_rcc.h"
#include <zephyr/drivers/gpio.h>
#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace fifo_test {
using namespace recorder::dump;
struct Trace {char kind;std::uint32_t value;};
struct Hardware {
    std::uint64_t now=10000,last=10000,finish=0;
    std::uint32_t step=0,control=0,ipsr=0,mask=0,call_started=0;
    unsigned clocks=0,init=0,configure=0,ready_calls=0,reads=0,writes=0,cr1_writes=0,context_queries=0;
    unsigned irq_enabled=0,irq_pending=0,irq_active=0,disabled=0,cleared=0;
    unsigned rdr_reads=0,forbidden_writes=0,overflow=0,max_queue=0;
    unsigned target_stage=0,fault_kind=0,live_after_tdr=0,live_kind=0;
    unsigned head=0,count=0;unsigned char shifting_byte=0;
    int ready=1,init_result=0,post_init_fault=0;
    bool shifting=false,frozen_serial=false,fault_fired=false,await_dmb=false,await_readback=false;
    bool setup=true,enforce_budget=false,cleanup_corrupt=false;
    std::array<unsigned char,8> queue{};
    std::vector<unsigned char> submitted,emitted;
    std::vector<Trace> trace;
} ;
extern Hardware hw;
extern uart_stm32_config metadata;
extern uart_stm32_data uart_data;
extern uart_config settings;
extern device_state states[4];
extern unsigned checks,failures;
void verify(bool,const char*,unsigned);
#define VERIFY(c) ::fifo_test::verify(bool(c),#c,__LINE__)
void initialize();
void synchronize();
void moveTime(std::uint64_t);
void corrupt(unsigned);
SetupGrant grants();
bool start(UnoQDumpPort&);
WriteResult send(UnoQDumpPort&,const std::string&);
void terminal(UnoQDumpPort&);
std::vector<unsigned char> packet(const std::string&);
void replay(const std::string&,const std::string&);
void capacity(const std::string&);
}

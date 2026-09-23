// Declares the independent native hardware model and deterministic failure controls.
// Keeps setting acknowledgements, update events and applied shadow values separate.
// Used only by the locked native MotorGate contract executable.
#pragma once
#include "mapping.h"
#include "stm32u5xx_ll_tim.h"
#include "stm32u5xx_ll_gpio.h"
#include <array>
#include <cstddef>
#include <cstdint>
namespace fixture {
enum Kind : unsigned { READY, CONFIGURE, WRITE_GPIO, READ_GPIO, ROUTE, RATE, PWM, CLEAR, POLL, CLOCK, KINDS };
struct Call { Kind kind; unsigned index; std::uint32_t a,b; };
struct Hardware {
    bool ready[11]{};
    unsigned calls[KINDS]{};
    int fail_ordinal[KINDS]{};
    int fail_status=-5;
    int read_override=-999;
    int high_read_override=-999;
    std::uint64_t rate[3]{};
    int fresh_after[3]{};
    unsigned polls[3]{}, clears[3]{};
    std::uint32_t active[3][4]{};
    std::uint32_t active_arr[3]{};
    std::uint32_t now=0, ticks_per_poll=1, event_elapsed=0;
    bool use_event_elapsed=false, race_survives=false, race_cleared=false;
    bool writes_while_high=false, unsafe_high=false, count_allocations=false;
    unsigned allocations=0, deallocations=0, trace_size=0, timer_init[3]{};
    unsigned all_write_mask=0, update_mask=0;
    int init_bad_register=-1;
    int route_without_ready=-1;
    std::uint32_t init_flip=0;
    volatile std::uint32_t* corrupt_reg=nullptr;
    std::uint32_t corrupt_value=0;
    unsigned corrupt_at_poll=0;
    unsigned lose_ready_at_poll=0, lose_ready_index=0;
    std::array<Call,50000> trace{};
};
extern Hardware hw;
void reset();
void clearTrace();
void transfer(unsigned);
TIM_TypeDef* timer(unsigned);
unsigned timerIndex(const TIM_TypeDef*);
unsigned record(Kind,unsigned=0,std::uint32_t=0,std::uint32_t=0);
bool fails(Kind,unsigned);
struct NoAllocation {
    NoAllocation() { hw.count_allocations=true; }
    ~NoAllocation() { hw.count_allocations=false; }
};
}

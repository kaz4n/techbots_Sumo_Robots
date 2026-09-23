// Counts the opaque recorder sketch's unchanged false begin and loop delegation.
// D116 separately exercises actual Runner default passivity and full lifecycle unchanged.
// This public constructor substitute makes selected sketch behavior directly observable.
#pragma once
#include "app/dump_port.h"
static_assert(MATCH==0&&MOTORS_ALLOWED==0,"inert recorder");
namespace recorder_transport {
struct ClockPort {void*context=nullptr;std::uint32_t(*now_us)(void*)=nullptr;};
class Runner {
public:
    Runner(const ClockPort&,const app::DumpPort&){}
    bool begin(bool enabled=false,const recorder::dump::SetupGrant& g={}) {
        fifo_sketch::require(!enabled&&!g.setup_phase&&!g.exclusive_uart&&!g.ready_pin_owned&&!g.framing_clean);
        ++fifo_sketch::runner_begins;return false;
    }
    void poll(){++fifo_sketch::runner_polls;}
};
}

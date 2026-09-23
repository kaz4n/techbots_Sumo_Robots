// Counts only the public native-dump constructor selection and callback routing.
// Opaque real sketches compile against this substitute; native hardware uses a separate fixture.
// Bookkeeping in constructors is fixture observation, not production I/O or a new public seam.
#pragma once
#include "recorder_dump.h"
#include <cstdlib>
namespace fifo_sketch {
inline unsigned legacy=0,selected=0,invalid=0,begins=0,readies=0,writes=0,cancels=0;
inline unsigned runner_begins=0,runner_polls=0,clocks=0;
inline void require(bool value){if(!value)std::abort();}
inline void passive(){require(begins==0&&readies==0&&writes==0&&cancels==0);}
}
namespace recorder::dump {
enum class NativeStatus:std::uint8_t {NOT_INITIALIZED,OK,CONTEXT,OWNERSHIP,DEVICE,READY_LOW,READY_ERROR,
    REGISTER,POISONED,TIMEOUT,INVALID_ARGUMENT};
enum class Buffering:std::uint8_t {LEGACY_SINGLE=0,FIFO8=1};
struct SetupGrant {bool setup_phase=false,exclusive_uart=false,ready_pin_owned=false,framing_clean=false;};
class UnoQDumpPort {
public:
    UnoQDumpPort(){++fifo_sketch::legacy;}
    explicit UnoQDumpPort(Buffering b){if(b==Buffering::FIFO8)++fifo_sketch::selected;else ++fifo_sketch::invalid;}
    NativeStatus begin(const SetupGrant&){++fifo_sketch::begins;return NativeStatus::OWNERSHIP;}
    bool ready(){++fifo_sketch::readies;return false;}
    Port port(){return {this,write,cancel};}
    NativeStatus status()const{return NativeStatus::NOT_INITIALIZED;}
private:
    static WriteResult write(void*,const char*,std::size_t){++fifo_sketch::writes;return {WriteStatus::ERROR,0};}
    static void cancel(void*){++fifo_sketch::cancels;}
};
}

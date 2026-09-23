// Executes the real default sketch and real app native factory against counted owner methods.
// Distinguishes passive construction/disabled loops from explicitly invoked native callbacks.
// No board, UART, pins, private Runner state or production implementation is inspected.
#include "app/dump_port.h"
#include <cstdlib>
#include <cstdint>
namespace counted {
unsigned clocks=0,begins=0,readies=0,writes=0,cancels=0;
recorder::dump::UnoQDumpPort* seen=nullptr;
recorder::dump::SetupGrant grant{};
const char* data=nullptr;std::size_t count=0;
void require(bool value) {if(!value)std::abort();}
void silent() {require(clocks==0&&begins==0&&readies==0&&writes==0&&cancels==0);}
}
unsigned long micros() {++counted::clocks;return 37;}
namespace recorder::dump {
NativeStatus UnoQDumpPort::begin(const SetupGrant& g) {
    ++counted::begins;counted::seen=this;counted::grant=g;status_=NativeStatus::REGISTER;return status_;
}
bool UnoQDumpPort::ready() {++counted::readies;counted::seen=this;return false;}
Port UnoQDumpPort::port() {return {this,write,cancel};}
WriteResult UnoQDumpPort::write(void* p,const char* bytes,std::size_t size) {
    ++counted::writes;counted::seen=static_cast<UnoQDumpPort*>(p);
    counted::data=bytes;counted::count=size;return {WriteStatus::PROGRESS,3};
}
void UnoQDumpPort::cancel(void* p) {++counted::cancels;counted::seen=static_cast<UnoQDumpPort*>(p);}
}
void setup();void loop();
int main() {
    using counted::require;
    counted::silent();
    {recorder::dump::UnoQDumpPort local;(void)app::unoQDumpPort(local);counted::silent();}
    setup();counted::silent();for(unsigned i=0;i<10000;++i)loop();counted::silent();
    recorder::dump::UnoQDumpPort owner;const auto port=app::unoQDumpPort(owner);counted::silent();
    require(port.context==&owner&&port.output.context==&owner);
    require(port.begin&&port.ready&&port.output.write&&port.output.cancel);
    for(unsigned flags=0;flags<16;++flags) {
        const recorder::dump::SetupGrant g{bool(flags&1),bool(flags&2),bool(flags&4),bool(flags&8)};
        require(port.begin(port.context,g)==recorder::dump::NativeStatus::REGISTER);
        require(counted::seen==&owner&&counted::grant.setup_phase==g.setup_phase&&
          counted::grant.exclusive_uart==g.exclusive_uart&&counted::grant.ready_pin_owned==g.ready_pin_owned&&
          counted::grant.framing_clean==g.framing_clean);
    }
    require(!port.ready(port.context));require(counted::seen==&owner);
    const char bytes[]="actual callback bytes";const auto written=port.output.write(port.output.context,bytes,7);
    require(counted::seen==&owner&&counted::data==bytes&&counted::count==7);
    require(written.status==recorder::dump::WriteStatus::PROGRESS&&written.count==3);
    port.output.cancel(port.output.context);require(counted::seen==&owner);
    require(counted::clocks==0&&counted::begins==16&&counted::readies==1&&counted::writes==1&&counted::cancels==1);
}

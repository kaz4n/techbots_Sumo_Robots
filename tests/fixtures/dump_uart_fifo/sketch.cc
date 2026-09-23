// Executes actual sketch bytes with counted public native-owner substitution.
// App retains actual Runtime MotorGate/clock setup; only new dump I/O must remain absent.
// Recorder verifies explicit FIFO selection plus unchanged disabled delegation.
#include "hal/dump_uart_unoq.h"
#ifdef D117_APP
#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h"
#include "tests/fixtures/app_runtime_fixture.h"
#include "app/native_sources_unoq.h"
#include "hal/motor_port_unoq.h"
namespace {runtime_test::Fake motor,source;}
namespace app {
SourcePort NativeSources::port(){return source.sourcePort();}
power::InputPort NativeSources::adcPort(){return source.adcPort();}
}
namespace motors {Port UnoQPort::port(){return motor.motorPort();}}
#endif
unsigned long micros(){++fifo_sketch::clocks;return 10000;}
void setup();void loop();
int main() {
    using fifo_sketch::require;
    require(fifo_sketch::selected==1&&fifo_sketch::legacy==0&&fifo_sketch::invalid==0);
    fifo_sketch::passive();require(fifo_sketch::clocks==0);
#ifdef D117_APP
    require(motor.count==0&&source.count==0&&motor.clocks==0);
#endif
    setup();fifo_sketch::passive();
    for(unsigned i=0;i<1000;++i)loop();
    fifo_sketch::passive();require(fifo_sketch::selected==1);
#ifdef D117_APP
    require(motor.count>=11&&motor.clocks>0);require(!motor.enabled);
    for(auto pulse:motor.pulses)require(pulse==0);
#else
    require(fifo_sketch::runner_begins==1&&fifo_sketch::runner_polls==1000&&fifo_sketch::clocks==0);
#endif
}

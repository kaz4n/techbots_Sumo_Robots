// Exercises the actual D115 Native forwarding body and the actual default sketch.
// Counted public UnoQPort/Runner substitutes expose ownership and grant selection.
// Standalone normal/sanitized programs reject all allocation and backend activity.
#include "motor_stand_native.h"
#include <cstddef>
#include <cstdlib>
#include <type_traits>
void setup();
void loop();
namespace {
unsigned ports=0,backend=0,clocks=0;
void* contexts[8]{};
bool configEnable(void*) { ++backend; return true; }
bool configPwm(void*,motors::Channel) { ++backend; return true; }
bool enable(void*,bool) { ++backend; return true; }
bool pwm(void*,motors::Channel,std::uint32_t,std::uint32_t) { ++backend; return true; }
bool settle(void*) { ++backend; return true; }
std::uint32_t clockUs(void*) { ++clocks; return 0; }
void require(bool value) { if(!value) std::abort(); }
void exact(const motors::Port& p,void* context) {
    require(p.context==context && p.configureEnableLow==configEnable && p.configurePwm==configPwm);
    require(p.writeEnable==enable && p.writePwm==pwm && p.settle==settle && p.clockUs==clockUs);
    const std::uint32_t periods[4]={1,997,65535,16777216};
    for(unsigned i=0;i<4;++i) require(p.period_cycles[i]==periods[i]);
}
}
motors::Port motors::UnoQPort::port() {
    require(ports<8);contexts[ports++]=this;
    return {this,configEnable,configPwm,enable,pwm,settle,clockUs,{1,997,65535,16777216}};
}
void* operator new(std::size_t) { std::abort(); }
void* operator new[](std::size_t) { std::abort(); }
void operator delete(void*) noexcept { std::abort(); }
void operator delete[](void*) noexcept { std::abort(); }
void operator delete(void*,std::size_t) noexcept { std::abort(); }
void operator delete[](void*,std::size_t) noexcept { std::abort(); }
int main() {
    static_assert(!std::is_copy_constructible<motor_stand::Native>::value,"one native owner");
    static_assert(!std::is_copy_assignable<motor_stand::Native>::value,"one native owner");
    require(ports==1 && backend==0 && clocks==0);
    require(motor_stand_test::runners==1 && motor_stand_test::begins==0 && motor_stand_test::polls==0);
    exact(motor_stand_test::copied,contexts[0]);
    setup();
    require(motor_stand_test::begins==1 && motor_stand_test::polls==0);
    for(unsigned i=0;i<10000;++i) loop();
    require(motor_stand_test::runners==1 && motor_stand_test::begins==1 && motor_stand_test::polls==10000);
    require(ports==1 && backend==0 && clocks==0);
    { motor_stand::Native first,second;
      require(ports==1 && backend==0 && clocks==0);
      const auto a=first.port(),b=first.port(),c=second.port();
      exact(a,contexts[1]);exact(b,contexts[1]);exact(c,contexts[3]);
      require(contexts[1]==contexts[2] && contexts[1]!=contexts[3] && contexts[1]!=contexts[0]); }
    require(ports==4 && backend==0 && clocks==0);
}

// Tests D115 against its public contract using the actual existing MotorGate.
// Separates literal trace/phase assertions from supplemental Gate delegation comparisons.
// Isolated normal/sanitized builds guard allocation; no native hardware is invoked.
#include "doctest.h"
#include "../bench/motor_stand/src/motor_stand.h"
#include "fixtures/app_transaction_fixture.h"
#include <array>
#include <cstddef>
#include <cstdlib>
#include <type_traits>
#include <utility>

#ifdef D115_ALLOCATION_GUARD
namespace d115_heap { bool active=false; unsigned calls=0; }
extern "C" {
void* __real_malloc(std::size_t);
void* __real_calloc(std::size_t,std::size_t);
void* __real_realloc(void*,std::size_t);
void __real_free(void*);
void* __wrap_malloc(std::size_t n) { if(d115_heap::active) ++d115_heap::calls; return __real_malloc(n); }
void* __wrap_calloc(std::size_t n,std::size_t s) { if(d115_heap::active) ++d115_heap::calls; return __real_calloc(n,s); }
void* __wrap_realloc(void* p,std::size_t n) { if(d115_heap::active) ++d115_heap::calls; return __real_realloc(p,n); }
void __wrap_free(void* p) { if(d115_heap::active) ++d115_heap::calls; __real_free(p); }
}
void* operator new(std::size_t n) {
    if(d115_heap::active) ++d115_heap::calls;
    if(void* p=__real_malloc(n)) return p;
    std::abort();
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { if(d115_heap::active) ++d115_heap::calls; __real_free(p); }
void operator delete[](void* p) noexcept { ::operator delete(p); }
void operator delete(void* p,std::size_t) noexcept { ::operator delete(p); }
void operator delete[](void* p,std::size_t) noexcept { ::operator delete(p); }
#endif

namespace {
using motor_stand::Runner;
using motor_stand::Report;
using motor_stand::Phase;
using motors::Fault;
using app_test::Port;
using app_test::Kind;
bool same(const motors::HaltResult& a,const motors::HaltResult& b) {
    return a.fresh==b.fresh && a.attempted==b.attempted &&
        a.inhibition_confirmed==b.inhibition_confirmed && a.timing_valid==b.timing_valid &&
        a.started_us==b.started_us && a.completed_us==b.completed_us && a.fault==b.fault;
}
bool same(const Report& a,const Report& b) {
    return a.phase==b.phase && a.begin_called==b.begin_called && a.begin_ok==b.begin_ok &&
        a.begin_fault==b.begin_fault && a.halt_called==b.halt_called && same(a.halt,b.halt);
}
void assertZero(const Port& p) {
    CHECK(p.highs==0U); CHECK(p.nonzero==0U); app_test::zero(p);
    for(unsigned i=0;i<p.count;++i) {
        if(p.calls[i].kind==Kind::ENABLE) CHECK_FALSE(p.calls[i].high);
        if(p.calls[i].kind==Kind::PWM) CHECK(p.calls[i].pulse==0U);
    }
}
void terminal(Runner& r,Port& p) {
    const auto* address=&r.report(); const auto saved=*address;
    const auto count=p.count;
    for(unsigned i=0;i<1000;++i) {
        r.poll(); CHECK_FALSE(r.begin({i%2U!=0U}));
        CHECK(&r.report()==address); CHECK(same(saved,r.report()));
    }
    CHECK(p.count==count);
}
void haltPass(const Port& p,unsigned start) {
    APP_REQUIRE(p.count==start+8U);
    CHECK(p.calls[start].kind==Kind::CLOCK);
    CHECK(p.calls[start+1].kind==Kind::ENABLE);
    for(unsigned i=0;i<4;++i) {
        CHECK(p.calls[start+2+i].kind==Kind::PWM);
        CHECK(p.calls[start+2+i].channel==i);
        CHECK(p.calls[start+2+i].pulse==0U);
    }
    CHECK(p.calls[start+6].kind==Kind::SETTLE);
    CHECK(p.calls[start+7].kind==Kind::CLOCK);
}
void compareTrace(const Port& a,const Port& b) {
    APP_REQUIRE(a.count==b.count);
    for(unsigned i=0;i<a.count;++i) {
        CHECK(a.calls[i].kind==b.calls[i].kind); CHECK(a.calls[i].channel==b.calls[i].channel);
        CHECK(a.calls[i].pulse==b.calls[i].pulse); CHECK(a.calls[i].high==b.calls[i].high);
    }
    CHECK(a.clocks==b.clocks); CHECK(a.operations==b.operations); CHECK(a.settles==b.settles);
}
void removeCallback(motors::Port& p,unsigned which) {
    if(which==0) p.configureEnableLow=nullptr;
    if(which==1) p.configurePwm=nullptr;
    if(which==2) p.writeEnable=nullptr;
    if(which==3) p.writePwm=nullptr;
    if(which==4) p.settle=nullptr;
    if(which==5) p.clockUs=nullptr;
}
const Runner* observed=nullptr;
std::array<Report,3> observed_reports{};
unsigned observations=0;
bool observeBegin(void* context) {
    observed_reports[observations++]=observed->report();
    return Port::configureEnable(context);
}
std::uint32_t observeClock(void* context) {
    observed_reports[observations++]=observed->report();
    return Port::clock(context);
}
}

TEST_CASE("D115 default grant consumes one passive attempt including invalid ports") {
    for(bool invalid:{false,true}) {
        Port p; const auto port=invalid?motors::Port{}:p.port();
        { Runner r(port); CHECK(same(r.report(),Report{}));
          for(unsigned i=0;i<1000;++i) r.poll();
          CHECK(same(r.report(),Report{})); CHECK(p.count==0U);
          CHECK(r.begin({})); Report expected; expected.phase=Phase::DISABLED;
          CHECK(same(r.report(),expected)); terminal(r,p); }
        CHECK(p.count==0U);
    }
    static_assert(!std::is_copy_constructible<Runner>::value,"one owner");
    static_assert(!std::is_copy_assignable<Runner>::value,"one owner");
    static_assert(std::is_same<decltype(std::declval<const Runner&>().report()),const Report&>::value,"passive const report");
}

TEST_CASE("D115 actual successful begin then exactly one bracketed halt is literal LOW zero") {
    Port p; p.now=100; p.work_us=2; p.settle_us=5;
    Runner r(p.port()); CHECK(p.count==0U); CHECK(r.begin({true}));
    APP_REQUIRE(p.count==19U); CHECK(p.calls[0].kind==Kind::CONFIG_ENABLE);
    CHECK(p.calls[1].kind==Kind::ENABLE);
    for(unsigned i=0;i<4;++i) {
        CHECK(p.calls[2+i].kind==Kind::CONFIG_PWM); CHECK(p.calls[2+i].channel==i);
        CHECK(p.calls[6+i].kind==Kind::PWM); CHECK(p.calls[6+i].channel==i);
    }
    CHECK(p.calls[10].kind==Kind::SETTLE); haltPass(p,11); assertZero(p);
    const auto& report=r.report(); CHECK(report.phase==Phase::COMPLETE);
    CHECK(report.begin_called); CHECK(report.begin_ok); CHECK(report.begin_fault==Fault::NONE);
    CHECK(report.halt_called); CHECK(report.halt.fresh); CHECK(report.halt.attempted);
    CHECK(report.halt.inhibition_confirmed); CHECK(report.halt.timing_valid);
    CHECK(report.halt.started_us==127U); CHECK(report.halt.completed_us==144U);
    CHECK(report.halt.fault==Fault::STOPPED); CHECK(p.clocks==2U);
    terminal(r,p); CHECK(r.report().halt.fresh);
}

TEST_CASE("D115 report publishes ACTIVE before calls and saves immediate begin fault before halt") {
    for(unsigned fail:{0U,1U}) {
        Port p; p.fail_at=fail; auto port=p.port();
        port.configureEnableLow=observeBegin; port.clockUs=observeClock;
        Runner r(port); observed=&r; observations=0;
        CHECK(r.begin({true})==(fail==0)); APP_REQUIRE(observations==3U);
        CHECK(observed_reports[0].phase==Phase::ACTIVE); CHECK(observed_reports[0].begin_called);
        CHECK_FALSE(observed_reports[0].begin_ok); CHECK_FALSE(observed_reports[0].halt_called);
        for(unsigned i=1;i<3;++i) {
            CHECK(observed_reports[i].phase==Phase::ACTIVE); CHECK(observed_reports[i].halt_called);
            CHECK(observed_reports[i].begin_ok==(fail==0));
            CHECK(observed_reports[i].begin_fault==(fail==0?Fault::NONE:Fault::IO));
        }
        assertZero(p); terminal(r,p);
    }
    observed=nullptr;
}

TEST_CASE("D115 each actual begin callback failure retains IO even when final halt confirms") {
    for(unsigned fail=1;fail<=11;++fail) {
        CAPTURE(fail); Port p; p.fail_at=fail; Runner r(p.port());
        CHECK_FALSE(r.begin({true})); const auto& value=r.report();
        CHECK(value.phase==Phase::FAULT); CHECK(value.begin_called); CHECK_FALSE(value.begin_ok);
        CHECK(value.begin_fault==Fault::IO); CHECK(value.halt_called); CHECK(value.halt.fresh);
        CHECK(value.halt.attempted); CHECK(value.halt.inhibition_confirmed);
        CHECK(value.halt.timing_valid); CHECK(value.halt.fault==Fault::IO);
        APP_REQUIRE(p.count>=8U); haltPass(p,p.count-8); CHECK(p.clocks==2U); assertZero(p);
        terminal(r,p);
    }
}

TEST_CASE("D115 each final halt failure still attempts all remaining zero callbacks and settle") {
    for(unsigned fail=12;fail<=17;++fail) {
        CAPTURE(fail); Port p; p.fail_at=fail; Runner r(p.port());
        CHECK_FALSE(r.begin({true})); const auto& value=r.report();
        CHECK(value.phase==Phase::FAULT); CHECK(value.begin_ok); CHECK(value.begin_fault==Fault::NONE);
        CHECK(value.halt.fresh); CHECK(value.halt.attempted); CHECK_FALSE(value.halt.inhibition_confirmed);
        CHECK(value.halt.timing_valid); CHECK(value.halt.fault==Fault::IO);
        haltPass(p,11); CHECK(p.operations==17U); assertZero(p); terminal(r,p);
    }
}

TEST_CASE("D115 missing callbacks preserve actual PORT and partial terminal inhibition") {
    for(unsigned missing=0;missing<6;++missing) {
        CAPTURE(missing); Port actual,reference;
        auto a=actual.port(),b=reference.port(); removeCallback(a,missing);removeCallback(b,missing);
        motors::MotorGate baseline(b); CHECK_FALSE(baseline.begin());
        const auto before=baseline.fault(); const auto expected=baseline.halt();
        Runner r(a); CHECK_FALSE(r.begin({true})); const auto& value=r.report();
        CHECK(value.phase==Phase::FAULT); CHECK_FALSE(value.begin_ok); CHECK(value.begin_fault==Fault::PORT);
        CHECK(value.begin_fault==before); CHECK(value.halt_called); CHECK(value.halt.fresh);CHECK(value.halt.attempted);
        CHECK(same(value.halt,expected)); compareTrace(actual,reference); assertZero(actual);
        CHECK(actual.clocks==(missing==5?0U:2U)); terminal(r,actual);
    }
}

TEST_CASE("D115 invalid per channel periods preserve admission failure and actual partial halt") {
    for(unsigned channel=0;channel<4;++channel) for(std::uint32_t period:{0U,16777217U,0xffffffffU}) {
        CAPTURE(channel);CAPTURE(period); Port actual,reference;
        auto a=actual.port(),b=reference.port();a.period_cycles[channel]=period;b.period_cycles[channel]=period;
        motors::MotorGate baseline(b);CHECK_FALSE(baseline.begin());const auto before=baseline.fault();
        const auto expected=baseline.halt();Runner r(a);CHECK_FALSE(r.begin({true}));
        CHECK(r.report().phase==Phase::FAULT);CHECK(r.report().begin_fault==Fault::PORT);
        CHECK(r.report().begin_fault==before);CHECK(same(r.report().halt,expected));
        compareTrace(actual,reference);assertZero(actual);terminal(r,actual);
    }
}

TEST_CASE("D115 accepted period boundaries retain literal successful LOW zero trace") {
    for(unsigned channel=0;channel<4;++channel) for(std::uint32_t period:{1U,16777216U}) {
        Port p;auto port=p.port();port.period_cycles[channel]=period;Runner r(port);
        CHECK(r.begin({true}));CHECK(r.report().phase==Phase::COMPLETE);
        CHECK(r.report().begin_fault==Fault::NONE);CHECK(r.report().halt.fault==Fault::STOPPED);
        haltPass(p,11);assertZero(p);terminal(r,p);
    }
}

TEST_CASE("D115 unavailable port and actual halt IO upgrade retain distinct original cause") {
    { Runner r(motors::Port{});CHECK_FALSE(r.begin({true}));const auto& value=r.report();
      CHECK(value.phase==Phase::FAULT);CHECK_FALSE(value.begin_ok);CHECK(value.begin_fault==Fault::PORT);
      CHECK(value.halt_called);CHECK(value.halt.fresh);CHECK(value.halt.attempted);
      CHECK_FALSE(value.halt.inhibition_confirmed);CHECK_FALSE(value.halt.timing_valid);
      CHECK(value.halt.started_us==0U);CHECK(value.halt.completed_us==0U);CHECK(value.halt.fault==Fault::PORT);
      Port untouched;terminal(r,untouched); }
    Port p;p.fail_at=1;auto port=p.port();port.configureEnableLow=nullptr;Runner r(port);
    CHECK_FALSE(r.begin({true}));CHECK(r.report().phase==Phase::FAULT);
    CHECK(r.report().begin_fault==Fault::PORT);CHECK(r.report().halt.fault==Fault::IO);
    CHECK_FALSE(r.report().halt.inhibition_confirmed);CHECK(r.report().halt.timing_valid);
    haltPass(p,0);assertZero(p);terminal(r,p);
}

TEST_CASE("D115 real Gate comparison supplements literal tests for preexisting complex cleanup") {
    for(unsigned failed=0;failed<24;++failed) {
        CAPTURE(failed);Port actual,reference;actual.fail_at=reference.fail_at=failed;
        actual.work_us=reference.work_us=3;actual.settle_us=reference.settle_us=7;
        motors::MotorGate baseline(reference.port());const bool began=baseline.begin();
        const auto before=baseline.fault();const auto halt=baseline.halt();Runner r(actual.port());
        const bool complete=began && before==Fault::NONE && halt.fresh && halt.attempted &&
            halt.inhibition_confirmed && halt.timing_valid && halt.fault==Fault::STOPPED;
        CHECK(r.begin({true})==complete);const auto& value=r.report();
        CHECK(value.phase==(complete?Phase::COMPLETE:Phase::FAULT));CHECK(value.begin_called);
        CHECK(value.begin_ok==began);CHECK(value.begin_fault==before);CHECK(value.halt_called);
        CHECK(same(value.halt,halt));compareTrace(actual,reference);assertZero(actual);terminal(r,actual);
    }
}

TEST_CASE("D115 equal wrap and half range halt clocks preserve actual inhibition and STOPPED") {
    const std::array<std::uint32_t,7> starts{0U,77U,0xfffffff0U,7U,7U,7U,100U};
    const std::array<std::uint32_t,7> ends{0U,77U,0x10U,0x80000006U,0x80000007U,0x80000008U,99U};
    for(unsigned i=0;i<starts.size();++i) {
        CAPTURE(i);Port p;p.scripted=2;p.clock_script[0]=starts[i];p.clock_script[1]=ends[i];
        Runner r(p.port());CHECK(r.begin({true})==(i<4));const auto& value=r.report();
        CHECK(value.phase==(i<4?Phase::COMPLETE:Phase::FAULT));CHECK(value.begin_ok);
        CHECK(value.begin_fault==Fault::NONE);CHECK(value.halt.fault==Fault::STOPPED);
        CHECK(value.halt.timing_valid==(i<4));CHECK(value.halt.inhibition_confirmed);
        CHECK(value.halt.started_us==starts[i]);CHECK(value.halt.completed_us==ends[i]);
        haltPass(p,11);CHECK(p.clocks==2U);assertZero(p);terminal(r,p);
    }
}

#ifdef D115_ALLOCATION_GUARD
TEST_CASE("D115 entire Runner construction begin terminal polling and destruction allocate nothing") {
    for(unsigned fail=0;fail<=17;++fail) for(bool granted:{false,true}) {
        Port p;p.fail_at=fail;d115_heap::calls=0;d115_heap::active=true;
        { Runner r(p.port());r.poll();(void)r.begin({granted});
          for(unsigned i=0;i<10000;++i) {r.poll();(void)r.begin({!granted});(void)r.report();} }
        d115_heap::active=false;CHECK(d115_heap::calls==0U);assertZero(p);
    }
}
#endif

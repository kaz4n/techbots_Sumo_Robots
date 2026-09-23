// Tests D116 from its frozen public contract using actual existing owners.
// Preserves full 200-second recording, reset, source bytes and stream failures.
// Isolated normal/sanitized binaries export independent receiver comparison inputs.
#include "fixtures/recorder_transport/fixture.h"
#include <fstream>
#include <string>
#include <type_traits>

#ifdef D116_ALLOCATION_GUARD
namespace d116_heap { bool active=false; std::uint64_t calls=0; }
extern "C" {
void* __real_malloc(std::size_t);void* __real_calloc(std::size_t,std::size_t);
void* __real_realloc(void*,std::size_t);void __real_free(void*);
void* __wrap_malloc(std::size_t n) {if(d116_heap::active)++d116_heap::calls;return __real_malloc(n);}
void* __wrap_calloc(std::size_t n,std::size_t s) {if(d116_heap::active)++d116_heap::calls;return __real_calloc(n,s);}
void* __wrap_realloc(void* p,std::size_t n) {if(d116_heap::active)++d116_heap::calls;return __real_realloc(p,n);}
void __wrap_free(void* p) {if(d116_heap::active)++d116_heap::calls;__real_free(p);}
}
void* operator new(std::size_t n) {if(d116_heap::active)++d116_heap::calls;if(auto p=__real_malloc(n))return p;std::abort();}
void* operator new[](std::size_t n) {return ::operator new(n);}
void operator delete(void* p) noexcept {if(d116_heap::active)++d116_heap::calls;__real_free(p);}
void operator delete[](void* p) noexcept {::operator delete(p);}
void operator delete(void* p,std::size_t) noexcept {::operator delete(p);}
void operator delete[](void* p,std::size_t) noexcept {::operator delete(p);}
#endif

namespace {
using namespace d116;
void cleanSource(const Runner& r) {
    const auto& s=r.source();const auto& a=s.summary();
    CHECK(s.phase()==recorder::AttemptPhase::SEALED);CHECK_FALSE(s.incomplete());
    CHECK(s.frames().size()==5001U);CHECK(a.observed_results==200002U);
    CHECK(a.epoch_token==69U);CHECK(a.last_frame_token==200069U);
    CHECK(a.ticks.ticks==194901U);CHECK(a.ticks.overruns==0U);CHECK(a.ticks.max_us==0U);
    CHECK(a.go_seen);CHECK_FALSE(a.final_frame_missing);CHECK_FALSE(a.interrupted);
    CHECK_FALSE(a.timing_incomplete);CHECK_FALSE(a.recording_incomplete);
    CHECK(a.missing_results==0U);CHECK(a.rejected_results==0U);CHECK(a.identity_rejected==0U);
    CHECK(a.skipped_frames==0U);CHECK(s.frames().overwrittenCount()==0U);
}
std::uint32_t u32(const std::uint8_t* p) {
    return p[0]|(std::uint32_t(p[1])<<8)|(std::uint32_t(p[2])<<16)|(std::uint32_t(p[3])<<24);
}
void frameAndEvents(const Runner& r) {
    for(std::size_t i=0;i<r.source().frames().size();++i) {
        recorder::StoredFrame frame;require(r.source().frames().read(i,frame));
        CHECK(frame.status==logframe::PackStatus::OK);CHECK(u32(frame.bytes.data)==40U*i);
        CHECK(frame.bytes.data[18]==0U);CHECK(frame.bytes.data[19]==0U);
    }
    unsigned starts=0,go=0,nonzero=0;
    for(std::size_t i=0;i<r.source().events().size();++i) {
        const auto* data=r.source().events().at(i)->data;
        if(data[4]==static_cast<unsigned>(core::Event::START_RELEASE)) {++starts;CHECK(u32(data)==r.report().release_us);}
        if(data[4]==static_cast<unsigned>(core::Event::GO)) {++go;CHECK(u32(data)==r.report().release_us+5100000U);}
        if(data[4]==static_cast<unsigned>(core::Event::FIRST_NONZERO_DUTY)) ++nonzero;
    }
    CHECK(starts==1U);CHECK(go==1U);CHECK(nonzero==0U);
}
void exportEvidence(const Rig& f,const char* label) {
    const char* folder=std::getenv("D116_OUTPUT");if(!folder)return;
    const std::string base=std::string(folder)+"/"+label;
    std::ofstream wire(base+".wire",std::ios::binary);wire.write(f.io.bytes.data(),f.io.size);
    std::ofstream frames(base+".frames",std::ios::binary),events(base+".events",std::ios::binary);
    for(std::size_t i=0;i<f.runner.source().frames().size();++i) {
        recorder::StoredFrame frame;require(f.runner.source().frames().read(i,frame));
        frames.write(reinterpret_cast<const char*>(frame.bytes.data),25);
        frames.put(static_cast<char>(frame.status));
    }
    for(std::size_t i=0;i<f.runner.source().events().size();++i)
        events.write(reinterpret_cast<const char*>(f.runner.source().events().at(i)->data),8);
    std::ofstream meta(base+".json");const auto values=summary(f.runner.source());
    meta<<"{\"summary\":[";for(unsigned i=0;i<values.size();++i){if(i)meta<<',';meta<<values[i];}
    const auto& d=f.runner.dump();
    meta<<"],\"bytes\":"<<f.io.size<<",\"write_calls\":"<<f.io.writes<<",\"largest_offer\":"<<f.io.largest_offer
        <<",\"phase\":"<<static_cast<unsigned>(d.phase)<<",\"reason\":"<<static_cast<unsigned>(d.reason)
        <<",\"session\":"<<d.session<<",\"epoch\":"<<d.epoch<<",\"frames\":"<<d.frames
        <<",\"events\":"<<d.events<<",\"crc\":"<<d.crc<<"}\n";
    CHECK(wire.good());CHECK(frames.good());CHECK(events.good());CHECK(meta.good());
}
void fullPipeline(Rig& f,bool save) {
    f.start();SourceCopy sealed;bool copied=false,reset_checked=false;
    for(unsigned i=0;i<230000U && !terminal(f.runner);++i) {
        const auto clocks=f.io.clocks;f.tick();
        if(terminal(f.runner) && f.runner.report().phase!=Phase::SENT_UNCONFIRMED) break;
        const auto& t=f.runner.transaction().report();const auto& r=t.robot;
        CHECK(f.io.clocks-clocks==8U);CHECK(t.finished);CHECK(t.timing_valid);
        CHECK(r.token==f.runner.report().epochs);CHECK(r.button_sequence==r.token);
        CHECK(r.button_source_us==t.decision_us);CHECK(r.button_updated);
        CHECK(t.applied.feedback.applied_valid);CHECK_FALSE(t.applied.feedback.motors_enabled);
        if(!copied && f.runner.source().phase()==recorder::AttemptPhase::SEALED) {
            cleanSource(f.runner);sealed.take(f.runner.source());copied=true;
        }
        if(f.runner.report().service_only) {
            CHECK(r.outputs.ui_state==core::State::IDLE);CHECK(r.line_raw_mode);CHECK(r.line_calibration_hold);
            CHECK_FALSE(r.lifecycle.gate.start_release);CHECK_FALSE(r.lifecycle.gate.go);
            CHECK(t.applied.fault==motors::Fault::STOPPED);CHECK(r.contract_faults==0U);
        }
        if(f.runner.report().reset_done && !reset_checked) {
            require(copied);sealed.check(f.runner.source());reset_checked=true;
            CHECK(f.runner.report().reset_from_token==201139U);CHECK(r.token==201140U);
        }
    }
    require(f.runner.report().phase==Phase::SENT_UNCONFIRMED);CHECK(f.runner.report().failure==Failure::NONE);
    CHECK(copied);CHECK(reset_checked);sealed.check(f.runner.source());cleanSource(f.runner);frameAndEvents(f.runner);
    CHECK(f.runner.report().release_token==69U);CHECK(f.runner.report().stop_token==200069U);
    CHECK(f.runner.report().request_token==202472U);CHECK(f.runner.dump().session==202472U);
    CHECK(f.runner.dump().epoch==69U);CHECK(f.runner.dump().bytes==f.io.size);
    CHECK(f.runner.dump().frames==5001U);CHECK(f.runner.dump().events==f.runner.source().events().size());
    CHECK(f.runner.report().maximum_execution_us==0U);CHECK(f.runner.report().missed_releases==0U);
    CHECK(f.io.errors==0U);CHECK(f.io.cancels==0U);CHECK(f.io.begins==1U);
    CHECK(f.runner.report().configure_enable_calls==1U);CHECK(f.runner.report().configure_pwm_calls==4U);
    if(save)exportEvidence(f,"positive");
    passive(f);sealed.check(f.runner.source());
}
}

TEST_CASE("D116 disabled defaults and poll before begin never invoke callbacks") {
    static_assert(!std::is_copy_constructible<d116::Runner>::value,"one owner");
    for(bool premature:{false,true}) {
        d116::Rig f;if(premature)f.runner.poll();else CHECK_FALSE(f.runner.begin());
        CHECK(f.runner.report().phase==(premature?d116::Phase::FAILED:d116::Phase::DISABLED));
        CHECK(f.runner.report().failure==(premature?d116::Failure::ORDER:d116::Failure::NONE));
        CHECK(f.io.clocks==0U);CHECK(f.io.begins==0U);CHECK(f.io.readies==0U);CHECK(f.io.writes==0U);
        CHECK(f.runner.report().configure_enable_calls==0U);d116::passive(f);
    }
    d116::Runner absent({});CHECK_FALSE(absent.begin());CHECK(absent.report().phase==d116::Phase::DISABLED);
}
TEST_CASE("D116 missing public callback precedes grants and initialization") {
    for(unsigned missing=0;missing<5;++missing) {
        d116::Port p;auto clock=p.clockPort();auto dump=p.dumpPort();
        if(missing==0)clock.now_us=nullptr;
        if(missing==1)dump.begin=nullptr;
        if(missing==2)dump.ready=nullptr;
        if(missing==3)dump.output.write=nullptr;
        if(missing==4)dump.output.cancel=nullptr;
        d116::Runner r(clock,dump);p.owner=&r;CHECK_FALSE(r.begin(true,{}));
        CHECK(r.report().failure==d116::Failure::PORT);CHECK(p.clocks==0U);CHECK(p.begins==0U);
        CHECK(r.report().configure_enable_calls==0U);
    }
}
TEST_CASE("D116 every absent setup predicate refuses before clock and native calls") {
    for(unsigned bits=0;bits<15;++bits) {
        d116::Rig f;recorder::dump::SetupGrant g{bool(bits&1),bool(bits&2),bool(bits&4),bool(bits&8)};
        CHECK_FALSE(f.runner.begin(true,g));CHECK(f.runner.report().failure==d116::Failure::GRANT);
        CHECK(f.io.clocks==0U);CHECK(f.io.begins==0U);CHECK(f.runner.report().configure_enable_calls==0U);
        d116::passive(f);
    }
}
TEST_CASE("D116 actual setup return remains distinct and failure cleanup is once only") {
    for(unsigned value=0;value<=static_cast<unsigned>(d116::NativeStatus::INVALID_ARGUMENT);++value) {
        if(value==static_cast<unsigned>(d116::NativeStatus::OK))continue;
        d116::Rig f;f.io.setup=static_cast<d116::NativeStatus>(value);
        CHECK_FALSE(f.runner.begin(true,d116::grants()));CHECK(f.runner.report().failure==d116::Failure::DUMP_SETUP);
        CHECK(f.runner.report().dump_setup==f.io.setup);CHECK(f.io.begins==1U);CHECK(f.io.setup_order_errors==0U);
        CHECK(f.runner.transaction().report().halt.inhibition_confirmed);CHECK(f.io.readies==0U);
        CHECK(f.io.writes==0U);CHECK(f.io.cancels==0U);d116::passive(f);
    }
}
TEST_CASE("D116 full 200 second real pipeline seals resets and exports every retained row") {
    d116::Rig f;fullPipeline(f,true);
#ifdef D116_ALLOCATION_GUARD
    CHECK(d116_heap::calls==0U);
#endif
}
TEST_CASE("D116 natural micros wrap retains full window and exact token identity") {
    d116::Rig f(0xffff0000U);fullPipeline(f,false);
}
TEST_CASE("D116 early calls equal poll stall exact bound and changed clock restart") {
    d116::Rig f;f.start();const auto setup=f.runner.report().setup_completed_us;
    f.io.now=setup;for(unsigned i=1;i<config::APP_CLOCK_STALL_MAX_POLLS;++i)f.runner.poll();
    CHECK(f.runner.report().phase==d116::Phase::STARTING);CHECK(f.runner.report().epochs==0U);
    f.runner.poll();CHECK(f.runner.report().failure==d116::Failure::CLOCK);d116::passive(f);
    d116::Rig changed;changed.start();changed.io.now+=1;changed.runner.poll();
    for(unsigned i=1;i<config::APP_CLOCK_STALL_MAX_POLLS;++i)changed.runner.poll();
    CHECK(changed.runner.report().phase==d116::Phase::STARTING);
    changed.runner.poll();CHECK(changed.runner.report().failure==d116::Failure::CLOCK);
}
TEST_CASE("D116 lateness boundary counts skipped releases and never fabricates catchup") {
    for(unsigned lateness:{999U,1000U,2999U}) {
        d116::Rig f;f.start();f.io.now=f.runner.report().next_release_us+lateness;f.runner.poll();
        if(lateness<1000) {CHECK(f.runner.report().epochs==1U);CHECK(f.runner.report().failure==d116::Failure::NONE);}
        else {CHECK(f.runner.report().epochs==0U);CHECK(f.runner.report().failure==d116::Failure::MISSED_RELEASE);
          CHECK(f.runner.report().missed_releases==lateness/1000U);d116::passive(f);}
        CHECK(f.runner.report().maximum_lateness_us==lateness);
    }
}
TEST_CASE("D116 all eight ordinary clock positions reject reversal with truthful missing closure") {
    for(unsigned position=1;position<=8;++position) {
        CAPTURE(position);d116::Rig f;f.start();f.io.now=f.runner.report().next_release_us;
        f.io.inject_at=f.io.clocks+position;f.io.injected=position==1?f.runner.report().setup_completed_us-1:f.io.now-1;
        f.runner.poll();CHECK(f.runner.report().failure==d116::Failure::CLOCK);
        CHECK(f.runner.report().epochs==0U);CHECK_FALSE(f.runner.transaction().report().finished);
        CHECK(f.io.writes==0U);CHECK(f.io.readies==(position>=6?1U:0U));d116::passive(f);
    }
}
TEST_CASE("D116 total admission deadline wins missed releases and half range wins deadline") {
    for(std::uint32_t age:{static_cast<std::uint32_t>(d116::TOTAL-1),static_cast<std::uint32_t>(d116::TOTAL),0x80000000U}) {
        d116::Rig f;f.start();f.io.now=f.runner.report().setup_completed_us+age;f.runner.poll();
        const auto expected=age==0x80000000U?d116::Failure::CLOCK:
          age==d116::TOTAL?d116::Failure::DEADLINE:d116::Failure::MISSED_RELEASE;
        CHECK(f.runner.report().failure==expected);CHECK(f.runner.report().epochs==0U);d116::passive(f);
    }
}
TEST_CASE("D116 closing C at global deadline retains finished actual transaction but fails") {
    d116::Rig f;f.start();f.io.now=f.runner.report().next_release_us;
    f.io.inject_at=f.io.clocks+8;f.io.injected=f.runner.report().setup_completed_us+static_cast<std::uint32_t>(d116::TOTAL);
    f.runner.poll();CHECK(f.runner.report().failure==d116::Failure::DEADLINE);
    CHECK(f.runner.transaction().report().finished);CHECK(f.runner.transaction().report().timing_valid);
    CHECK(f.runner.transaction().report().completed_us==f.io.injected);CHECK(f.runner.report().epochs==1U);
    d116::passive(f);
}
TEST_CASE("D116 ready bracket valid age below tick and equality refusal precede transfer") {
    for(unsigned elapsed:{999U,1000U,1001U}) {
        d116::Rig f;f.start();f.io.ready_cost=elapsed;f.tick();
        CHECK(f.io.readies==1U);CHECK(f.io.writes==0U);
        CHECK(f.runner.report().failure==(elapsed<1000?d116::Failure::NONE:d116::Failure::DEADLINE));
        CHECK(f.runner.transaction().report().finished==(elapsed<1000));
        if(elapsed<1000)CHECK(f.runner.report().maximum_execution_us==999U);else d116::passive(f);
    }
}
TEST_CASE("D116 pending and short progress preserve exact stream with no repeated byte") {
    d116::Rig f;f.io.max_ack=17;f.io.pending_every=3;f.start();d116::SourceCopy saved;
    f.sealed();saved.take(f.runner.source());f.until(recorder::dump::Phase::SENT_UNCONFIRMED);
    CHECK(f.runner.report().phase==d116::Phase::SENT_UNCONFIRMED);saved.check(f.runner.source());
    CHECK(f.runner.dump().bytes==f.io.size);CHECK(f.io.errors==0U);exportEvidence(f,"partial");d116::passive(f);
}
TEST_CASE("D116 one byte per epoch exposes TOTAL without shrinking full recorder") {
    d116::Rig f;f.io.max_ack=1;f.start();f.sealed();d116::SourceCopy saved;saved.take(f.runner.source());
    f.until(recorder::dump::Phase::FAILED);CHECK(f.runner.dump().reason==recorder::dump::Reason::TOTAL);
    CHECK(f.runner.report().failure==d116::Failure::DUMP);CHECK(f.io.size==300000U);
    CHECK(f.io.writes==300000U);CHECK(f.runner.dump().bytes==f.io.size);CHECK(f.io.cancels==1U);
    saved.check(f.runner.source());cleanSource(f.runner);exportEvidence(f,"slow");d116::passive(f);
}
TEST_CASE("D116 pending no acknowledgement reaches exact STALL with source retained") {
    d116::Rig f;f.io.keep_pending=true;f.start();f.until(recorder::dump::Phase::FAILED);
    CHECK(f.runner.dump().reason==recorder::dump::Reason::STALL);CHECK(f.runner.dump().bytes==0U);
    CHECK(f.io.writes==2000U);CHECK(f.io.cancels==1U);cleanSource(f.runner);d116::passive(f);
}
TEST_CASE("D116 invalid native progress combinations fail PORT without invented bytes") {
    const std::array<recorder::dump::WriteResult,5> invalid{{{d116::WriteStatus::PROGRESS,0},
      {d116::WriteStatus::PROGRESS,65},{d116::WriteStatus::PENDING,1},{d116::WriteStatus::ERROR,1},
      {static_cast<d116::WriteStatus>(255),0}}};
    for(const auto& returned:invalid) {
        d116::Rig f;f.io.malformed=true;f.io.status=returned.status;f.io.malformed_count=returned.count;
        f.start();f.until(recorder::dump::Phase::FAILED);CHECK(f.runner.dump().reason==recorder::dump::Reason::PORT);
        CHECK(f.io.writes==1U);CHECK(f.io.size==0U);CHECK(f.io.cancels==1U);d116::passive(f);
    }
}
TEST_CASE("D116 Linux loss cancels active delivery preserving actual prefix") {
    d116::Rig f;f.start();f.until(recorder::dump::Phase::ACTIVE);require(f.io.size>0U);
    const auto bytes=f.io.size;const auto writes=f.io.writes;f.io.ready_value=false;f.tick();
    CHECK(f.runner.dump().phase==recorder::dump::Phase::CANCELLED);
    CHECK(f.runner.dump().reason==recorder::dump::Reason::LINUX_UNAVAILABLE);
    CHECK(f.io.size==bytes);CHECK(f.io.writes==writes);CHECK(f.io.cancels==1U);d116::passive(f);
}
TEST_CASE("D116 active bracket reversal halts Gate before owner cancellation once") {
    for(unsigned position:{5U,6U,7U,8U}) {
        d116::Rig f;f.start();f.until(recorder::dump::Phase::ACTIVE);
        const auto bytes=f.io.size;const auto writes=f.io.writes;f.io.now=f.runner.report().next_release_us;
        f.io.inject_at=f.io.clocks+position;f.io.injected=f.io.now-1;f.runner.poll();
        CHECK(f.runner.report().failure==d116::Failure::CLOCK);CHECK(f.io.cancels==1U);
        CHECK(f.io.cancel_order_errors==0U);CHECK_FALSE(f.runner.transaction().report().finished);
        CHECK(f.io.writes==writes+(position>=7?1U:0U));CHECK(f.io.size>=bytes);
        CHECK(f.runner.dump().bytes==f.io.size);d116::passive(f);
    }
}
TEST_CASE("D116 callback time after actual write preserves progress then fails expiry") {
    d116::Rig f;f.start();f.until(recorder::dump::Phase::ACTIVE);const auto before=f.io.size;
    f.io.write_cost=1000;f.tick();CHECK(f.runner.report().failure==d116::Failure::DEADLINE);
    CHECK(f.io.size>before);CHECK(f.runner.dump().bytes==f.io.size);CHECK(f.io.cancels==1U);
    CHECK(f.io.cancel_order_errors==0U);CHECK_FALSE(f.runner.transaction().report().finished);d116::passive(f);
}
TEST_CASE("D116 setup endpoint anchors releases and active begin is passive") {
    for(unsigned cost:{0U,71U}) {
        d116::Rig f;f.io.begin_cost=cost;f.start();
        CHECK(f.runner.report().setup_completed);CHECK(f.runner.report().setup_completed_us==cost);
        CHECK(f.runner.report().next_release_us==cost+1000U);
        const auto saved=f.runner.report();const auto clocks=f.io.clocks;
        CHECK_FALSE(f.runner.begin(true,d116::grants()));CHECK_FALSE(f.runner.begin());
        CHECK(d116::same(saved,f.runner.report()));CHECK(f.io.clocks==clocks);CHECK(f.io.begins==1U);
        f.io.now=cost+999;f.runner.poll();CHECK(f.runner.report().epochs==0U);CHECK(f.io.clocks==clocks+1U);
        f.tick();CHECK(f.runner.report().epochs==1U);CHECK(f.runner.transaction().report().started_us==cost+1000U);
    }
}
TEST_CASE("D116 absent Linux at request refuses and actual error preserves zero bytes") {
    for(bool not_ready:{false,true}) {
        d116::Rig f;f.io.ready_value=!not_ready;f.io.status=d116::WriteStatus::ERROR;f.start();
        f.until(not_ready?recorder::dump::Phase::REFUSED:recorder::dump::Phase::FAILED);
        CHECK(f.runner.dump().reason==(not_ready?recorder::dump::Reason::LINUX_UNAVAILABLE:recorder::dump::Reason::PORT));
        CHECK(f.io.size==0U);CHECK(f.io.writes==(not_ready?0U:1U));CHECK(f.io.cancels==(not_ready?0U:1U));
        CHECK(f.runner.report().failure==d116::Failure::DUMP);cleanSource(f.runner);d116::passive(f);
    }
}
#ifdef D116_ALLOCATION_GUARD
TEST_CASE("D116 construction access and destruction allocate nothing or invoke callbacks") {
    d116::Port port;
    d116_heap::active=true;
    {
        d116::Runner runner(port.clockPort(),port.dumpPort());port.owner=&runner;
        (void)runner.report();(void)runner.source();(void)runner.transaction();(void)runner.dump();
    }
    d116_heap::active=false;
    CHECK(d116_heap::calls==0U);CHECK(port.clocks==0U);CHECK(port.begins==0U);
    CHECK(port.readies==0U);CHECK(port.writes==0U);CHECK(port.cancels==0U);
}
#endif

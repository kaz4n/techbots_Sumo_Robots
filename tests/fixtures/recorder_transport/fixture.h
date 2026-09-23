// Supplies independent D116 clock and bounded dump callbacks without native I/O.
// Preserves actual public owner observations; no production state is seeded.
// Full recording, fault and wire tests share only these controlled boundaries.
#pragma once
#include "doctest.h"
#include "../../../bench/recorder/src/recorder_transport.h"
#include "hal/recorder_csv.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#ifdef D116_ALLOCATION_GUARD
namespace d116_heap { extern bool active; extern std::uint64_t calls; }
#endif

namespace d116 {
using Runner = recorder_transport::Runner;
using Phase = recorder_transport::Phase;
using Failure = recorder_transport::Failure;
using NativeStatus = recorder::dump::NativeStatus;
using WriteStatus = recorder::dump::WriteStatus;
inline constexpr std::uint32_t T = config::TICK_US;
inline constexpr std::uint64_t G = config::BTN_DEBOUNCE_MS*1000ULL+4ULL*T;
inline constexpr std::uint64_t TOTAL = config::LOG_FRAME_WINDOW_MS*1000ULL+
    config::DUMP_TOTAL_MS*1000ULL+2ULL*(config::BTN_LONG_MS*1000ULL+G)+24ULL*G+
    config::BUTTON_SAMPLE_MAX_AGE_US+4ULL*T;
inline recorder::dump::SetupGrant grants() { return {true,true,true,true}; }
inline void require(bool value) { CHECK(value); if(!value) std::abort(); }
inline bool terminal(const Runner& r) {
    return r.report().phase==Phase::FAILED || r.report().phase==Phase::SENT_UNCONFIRMED ||
           r.report().phase==Phase::DISABLED;
}
inline bool same(const recorder_transport::Report& a,const recorder_transport::Report& b) {
#define D116_FIELD(x) a.x==b.x
    return D116_FIELD(phase)&&D116_FIELD(failure)&&D116_FIELD(dump_setup)&&
      D116_FIELD(setup_completed)&&D116_FIELD(go_seen)&&D116_FIELD(service_only)&&
      D116_FIELD(reset_pending)&&D116_FIELD(reset_done)&&D116_FIELD(counters_saturated)&&
      D116_FIELD(setup_completed_us)&&D116_FIELD(last_poll_us)&&D116_FIELD(next_release_us)&&
      D116_FIELD(epochs)&&D116_FIELD(missed_releases)&&D116_FIELD(maximum_lateness_us)&&
      D116_FIELD(maximum_execution_us)&&D116_FIELD(release_us)&&D116_FIELD(stop_us)&&
      D116_FIELD(reset_epoch_started_us)&&D116_FIELD(request_us)&&D116_FIELD(release_token)&&
      D116_FIELD(stop_token)&&D116_FIELD(reset_from_token)&&D116_FIELD(request_token)&&
      D116_FIELD(configure_enable_calls)&&D116_FIELD(configure_pwm_calls)&&
      D116_FIELD(write_enable_calls)&&D116_FIELD(write_pwm_calls)&&D116_FIELD(settle_calls)&&
      D116_FIELD(enabled_en)&&D116_FIELD(nonzero_pwm)&&D116_FIELD(invalid_motor_calls);
#undef D116_FIELD
}
inline std::array<std::uint64_t,36> summary(const recorder::AttemptRecorder& source) {
    const auto& a=source.summary();const auto& f=source.frames();const auto& e=source.events();
    return {1,a.epoch_token,a.last_frame_token,a.release_us,static_cast<unsigned>(a.mode),
      static_cast<unsigned>(source.phase()),a.observed_results,a.missing_results,a.rejected_results,
      a.identity_rejected,a.malformed_batches,a.event_semantic_rejected,a.upstream_event_rejected,
      a.upstream_event_invalid,a.source_regressions,a.skipped_frames,a.ticks.ticks,a.ticks.overruns,
      a.ticks.max_us,a.ticks.saturated,a.upstream_event_overflow,a.timing_incomplete,
      a.recording_incomplete,a.go_seen,a.final_frame_missing,a.interrupted,a.terminal_exhausted,
      f.size(),f.overwrittenCount(),f.rejectedStatusCount(),f.clampedCount(),f.invalidCount(),
      e.size(),e.overflowed(),e.rejectedCount(),source.incomplete()};
}
struct SourceCopy {
    std::array<recorder::StoredFrame,config::LOG_FRAME_CAPACITY> frames{};
    std::array<logframe::EventBytes,config::LOG_EVENT_CAPACITY> events{};
    std::array<std::uint64_t,36> values{};
    void take(const recorder::AttemptRecorder& source) {
        values=summary(source);
        for(std::size_t i=0;i<source.frames().size();++i) require(source.frames().read(i,frames[i]));
        for(std::size_t i=0;i<source.events().size();++i) events[i]=*source.events().at(i);
    }
    void check(const recorder::AttemptRecorder& source) const {
        CHECK(values==summary(source));
        for(std::size_t i=0;i<values[27];++i) {
            recorder::StoredFrame actual;require(source.frames().read(i,actual));
            CHECK(actual.status==frames[i].status);
            CHECK(std::memcmp(actual.bytes.data,frames[i].bytes.data,logframe::FRAME_BYTES)==0);
        }
        for(std::size_t i=0;i<values[32];++i)
            CHECK(std::memcmp(source.events().at(i)->data,events[i].data,logframe::EVENT_BYTES)==0);
    }
};
struct Port {
    Runner* owner=nullptr;
    std::array<char,1048576> bytes{};
    std::size_t size=0,max_ack=64,largest_offer=0;
    std::uint64_t clocks=0,inject_at=0;
    std::uint32_t now=0,injected=0,clock_cost=0,begin_cost=0,ready_cost=0,write_cost=0;
    unsigned begins=0,readies=0,writes=0,cancels=0,pending_every=0;
    unsigned errors=0,setup_order_errors=0,cancel_order_errors=0;
    NativeStatus setup=NativeStatus::OK;
    WriteStatus status=WriteStatus::PROGRESS;
    bool ready_value=true,malformed=false,keep_pending=false;
    std::size_t malformed_count=0;
    std::uint32_t writes_epoch=0,write_epoch=0;
    static Port& self(void* p) { return *static_cast<Port*>(p); }
    static std::uint32_t clock(void* p) {
        auto& f=self(p);++f.clocks;
        if(f.inject_at==f.clocks) return f.injected;
        const auto value=f.now;f.now+=f.clock_cost;return value;
    }
    static NativeStatus begin(void* p,const recorder::dump::SetupGrant& g) {
        auto& f=self(p);++f.begins;
        if(!g.setup_phase||!g.exclusive_uart||!g.ready_pin_owned||!g.framing_clean) ++f.errors;
        const auto& r=f.owner->report();
        if(r.configure_enable_calls!=1 || r.configure_pwm_calls!=4 ||
           r.write_enable_calls!=1 || r.write_pwm_calls!=4 || r.settle_calls!=1) ++f.setup_order_errors;
        f.now+=f.begin_cost;return f.setup;
    }
    bool inhibited() const {
        const auto& t=owner->transaction().report();const auto& r=t.robot;const auto& a=t.applied;
        return r.fresh && r.token!=0 && r.outputs.ui_state==core::State::IDLE &&
          r.lifecycle.gate.phase==countdown::Phase::IDLE && !r.outputs.motors_enabled &&
          r.outputs.duty_l==0 && r.outputs.duty_r==0 && a.consumed && a.feedback.applied_valid &&
          a.feedback.token==r.token && !a.feedback.motors_enabled &&
          a.feedback.duty_l==0 && a.feedback.duty_r==0;
    }
    static bool ready(void* p) {
        auto& f=self(p);++f.readies;if(!f.inhibited()) ++f.errors;
        f.now+=f.ready_cost;return f.ready_value;
    }
    static recorder::dump::WriteResult write(void* p,const char* data,std::size_t count) {
        auto& f=self(p);++f.writes;
        if(!f.inhibited() || count==0 || count>64 || !data) ++f.errors;
        const auto& r=f.owner->transaction().report().robot;
        if(!r.menu.selection.service_menu || r.menu.selection.service!=countdown::Service::LOG_DUMP) ++f.errors;
        if(f.write_epoch==r.token) ++f.writes_epoch;else {f.write_epoch=static_cast<std::uint32_t>(r.token);f.writes_epoch=1;}
        if(f.writes_epoch>1) ++f.errors;
        if(count>f.largest_offer) f.largest_offer=count;
        f.now+=f.write_cost;
        if(f.malformed) return {f.status,f.malformed_count};
        if(f.keep_pending || (f.pending_every && f.writes%f.pending_every==0)) return {WriteStatus::PENDING,0};
        if(f.status==WriteStatus::ERROR) return {WriteStatus::ERROR,0};
        const auto amount=count<f.max_ack?count:f.max_ack;
        if(f.size+amount>f.bytes.size()) {++f.errors;return {WriteStatus::ERROR,0};}
        std::memcpy(f.bytes.data()+f.size,data,amount);f.size+=amount;return {WriteStatus::PROGRESS,amount};
    }
    static void cancel(void* p) {
        auto& f=self(p);++f.cancels;
        // If Runner has selected failure, D116 requires real Gate halt first.
        if(f.owner->report().failure!=Failure::NONE &&
           !f.owner->transaction().report().halt.inhibition_confirmed) ++f.cancel_order_errors;
    }
    recorder_transport::ClockPort clockPort() { return {this,clock}; }
    app::DumpPort dumpPort() { return {this,begin,ready,{this,write,cancel}}; }
};
struct Rig {
    Port io;
    Runner runner{io.clockPort(),io.dumpPort()};
    explicit Rig(std::uint32_t origin=0) { io.owner=&runner;io.now=origin; }
    void start() {
#ifdef D116_ALLOCATION_GUARD
        d116_heap::active=true;
#endif
        const bool result=runner.begin(true,grants());
#ifdef D116_ALLOCATION_GUARD
        d116_heap::active=false;
#endif
        require(result);CHECK(io.setup_order_errors==0U);
    }
    void tick() {
        io.now=runner.report().next_release_us;
#ifdef D116_ALLOCATION_GUARD
        d116_heap::active=true;
#endif
        runner.poll();
#ifdef D116_ALLOCATION_GUARD
        d116_heap::active=false;
#endif
    }
    void until(recorder::dump::Phase wanted,unsigned limit=800000U) {
        for(unsigned i=0;i<limit && runner.dump().phase!=wanted && !terminal(runner);++i) tick();
        require(runner.dump().phase==wanted);
    }
    void sealed(unsigned limit=210000U) {
        for(unsigned i=0;i<limit && runner.source().phase()!=recorder::AttemptPhase::SEALED && !terminal(runner);++i) tick();
        require(runner.source().phase()==recorder::AttemptPhase::SEALED);
    }
};
inline void passive(Rig& f) {
    const auto saved=f.runner.report();const auto dump=f.runner.dump();
    const auto clocks=f.io.clocks;const auto begins=f.io.begins,ready=f.io.readies,writes=f.io.writes,cancels=f.io.cancels;
    for(unsigned i=0;i<100;++i) {
        f.io.now+=T;f.runner.poll();CHECK_FALSE(f.runner.begin(i%2!=0,grants()));
        CHECK(same(saved,f.runner.report()));
    }
    CHECK(f.io.clocks==clocks);CHECK(f.io.begins==begins);CHECK(f.io.readies==ready);
    CHECK(f.io.writes==writes);CHECK(f.io.cancels==cancels);
    CHECK(f.runner.dump().phase==dump.phase);CHECK(f.runner.dump().reason==dump.reason);
    CHECK(f.runner.dump().bytes==dump.bytes);CHECK(f.runner.report().enabled_en==0U);
    CHECK(f.runner.report().nonzero_pwm==0U);CHECK(f.runner.report().invalid_motor_calls==0U);
}
} // namespace d116

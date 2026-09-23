// Exercises the production Runtime with fixed synthetic native callbacks.
// Checks scheduling, inhibition, source publication and bounded cancellation.
// Independent authored suites provide the wider integration acceptance matrix.
#include "app/runtime.h"
#include <cassert>
#include <cstdio>
struct Fake {
    std::uint32_t now=0, writes=0, clocks=0, line_advances=0, cancels=0, submissions=0;
    unsigned imu_reads=0;
    line_qtr::Snapshot line;
    static Fake& self(void* p) { return *static_cast<Fake*>(p); }
    static bool config(void* p) { ++self(p).writes; return true; }
    static bool configPwm(void* p,motors::Channel) { return config(p); }
    static bool enable(void* p,bool high) { assert(!high); return config(p); }
    static bool pwm(void* p,motors::Channel,std::uint32_t,std::uint32_t duty) {
        assert(duty==0); return config(p);
    }
    static bool settle(void*) { return true; }
    static std::uint32_t clock(void* p) { ++self(p).clocks; return self(p).now; }
    motors::Port port() { return {this,config,configPwm,enable,pwm,settle,clock,{1000,1000,1000,1000}}; }
    static ui::MatrixStatus matrixBegin(void*,ui::MatrixGrant) { return ui::MatrixStatus::INIT_UNCONFIRMED; }
    static ui::MatrixStatus matrixSubmit(void* p,std::uint32_t,const ui::Frame&) {
        auto& f=self(p); ++f.submissions; f.now+=1200;
        return ui::MatrixStatus::SUBMITTED_UNCONFIRMED;
    }
    static line_qtr::Status lineBegin(void* p,bool exclusive) {
        assert(exclusive); auto& s=self(p).line; s.phase=line_qtr::Phase::IDLE;
        s.status=line_qtr::Status::OK; return s.status;
    }
    static line_qtr::Status lineStart(void* p) {
        auto& s=self(p).line; s.phase=line_qtr::Phase::CHARGING; return s.status;
    }
    static line_qtr::Snapshot lineAdvance(void* p) { ++self(p).line_advances; return self(p).line; }
    static line_qtr::Snapshot lineCancel(void* p) {
        auto& f=self(p); ++f.cancels; f.line.phase=line_qtr::Phase::FAULT;
        f.line.status=line_qtr::Status::CANCELLED; return f.line;
    }
    static line_qtr::Snapshot lines(void* p) { return self(p).line; }
    static imu::SetupReport imuStart(void*,std::uint32_t,bool power) {
        assert(power); imu::SetupReport r; r.state=imu::SetupState::PROFILE_READY; return r;
    }
    static imu::SetupReport imuSetup(void*,std::uint32_t) { assert(false); return {}; }
    static imu::SampleProgress imuRead(void* p,std::uint32_t now) {
        auto& f=self(p); imu::SampleProgress r; r.state=imu::AsyncState::COMPLETE;
        r.started=r.completed=true; r.sample.bus_status=imu::BusStatus::OK;
        r.sample.checked_us=now; r.sample.sequence=1;
        if (f.imu_reads++==0) {
            r.sample.state=imu::SampleState::OBSERVATION;
            r.sample.motion.status=imu::DecodeStatus::OK; r.sample.motion.coherent=true;
            r.sample.motion.started_us=r.sample.motion.completed_us=now;
            r.sample.motion.gyro_dps[2]=4.0F;
        } else r.sample.state=imu::SampleState::NO_NEW;
        return r;
    }
    static imu::SampleProgress imuAdvance(void*,std::uint32_t) { assert(false); return {}; }
    static imu::SampleProgress imuCancel(void*,std::uint32_t) { assert(false); return {}; }
    static imu::Sample imuFailure(void*,std::uint32_t) { assert(false); return {}; }
};
static void noGrants() {
    Fake f; app::Runtime r(f.port(),{},{}); assert(f.writes==0 && f.clocks==0);
    assert(r.begin({})); auto calls=f.writes+f.clocks; assert(!r.begin({}));
    assert(calls==f.writes+f.clocks); assert(r.step());
    assert(r.report().epochs==1 && r.transaction().report().robot.outputs.ui_state==core::State::BOOT);
    assert(r.decisionInput().line.explicit_values && r.decisionInput().buttons.explicit_values);
    assert(r.decisionInput().imu.explicit_values && !r.report().initialization_complete);
    calls=f.writes; f.now=999; assert(!r.step() && f.writes==calls);
    f.now=2500; assert(r.step() && r.report().missed_releases==1 && r.report().next_release_us==3000);
    r.abort(); calls=f.writes+f.clocks; assert(!r.step()); r.abort(); assert(!r.begin({}));
    assert(calls==f.writes+f.clocks);
}
static void badPortAndFrozenClock() {
    Fake f; app::Runtime r(f.port(),{},{}); app::SetupGrants g; g.opponents=true;
    assert(!r.begin(g) && r.report().fault==app::RuntimeFault::PORT);
    Fake frozen; app::Runtime t(frozen.port(),{},{}); assert(t.begin({}) && t.step());
    for (std::uint32_t i=1;i<config::APP_CLOCK_STALL_MAX_POLLS;++i) {
        assert(!t.step()); assert(t.report().phase==app::RuntimePhase::RUNNING);
    }
    assert(!t.step() && t.report().fault==app::RuntimeFault::CLOCK);
}
static void fullDuration() {
    Fake f; app::SourcePort s; s.context=&f; s.beginMatrix=Fake::matrixBegin;
    s.submitMatrix=Fake::matrixSubmit; app::Runtime r(f.port(),{},s);
    app::SetupGrants g; g.matrix_enabled=true; assert(r.begin(g) && r.step());
    assert(r.report().maximum_execution_us==1200 && r.report().missed_releases==1);
    assert(r.report().next_release_us==2000 && r.report().phase==app::RuntimePhase::RUNNING);
    assert(r.transaction().report().completed_us==1200 && f.submissions==1);
}
static void boundedCharge() {
    Fake f; app::SourcePort s; s.context=&f; s.beginLines=Fake::lineBegin;
    s.startLines=Fake::lineStart; s.advanceLines=Fake::lineAdvance;
    s.cancelLines=Fake::lineCancel; s.lines=Fake::lines;
    app::Runtime r(f.port(),{},s); app::SetupGrants g; g.qtr_exclusive_pads=true;
    assert(r.begin(g) && !r.step()); assert(r.report().fault==app::RuntimeFault::SERVICE_LIMIT);
    assert(f.line_advances==config::APP_SERVICE_MAX_PASSES && f.cancels==1);
    assert(!r.transaction().report().decision_made && r.transaction().report().halt.attempted);
    assert(r.report().line_shutdown.status==line_qtr::Status::CANCELLED);
    const auto calls=f.clocks+f.writes+f.cancels; r.abort(); assert(!r.step());
    assert(calls==f.clocks+f.writes+f.cancels);
}
static void noNewMailbox() {
    Fake f; app::SourcePort s; s.context=&f; s.startImu=Fake::imuStart;
    s.advanceImuSetup=Fake::imuSetup; s.beginImu=Fake::imuRead; s.advanceImu=Fake::imuAdvance;
    s.cancelImu=Fake::imuCancel; s.imuSetupFailure=Fake::imuFailure;
    app::Runtime r(f.port(),{},s); app::SetupGrants g; g.imu_enabled=g.imu_power_confirmed=true;
    g.mounting={{1,2,3},true}; assert(r.begin(g) && r.step());
    assert(r.decisionInput().imu.heading_updated && r.imuEvidence().raw_gyro_z_dps==4.0F);
    f.now=2000; assert(r.step()); assert(r.imuEvidence().heading_updated);
    assert(r.decisionInput().imu.heading_available && !r.report().imu_expired);
    assert(r.transaction().report().robot.contract_faults==0);
}
int main() {
    noGrants(); badPortAndFrozenClock(); fullDuration(); boundedCharge(); noNewMailbox();
    std::puts("Runtime worker smoke PASS (synthetic callbacks, no hardware)");
}

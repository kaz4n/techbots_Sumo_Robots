// Independently probes D096 late clock regressions using actual runtime sources.
// Keeps source grants absent so only the scheduler and true owner clocks vary.
// Sanitized isolated builds run this harness with both motor settings.
#include "app/runtime.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>

namespace {
unsigned checks = 0;
void check(bool value, int line) {
    ++checks;
    if (!value) { std::fprintf(stderr, "check %d failed\n", line); std::exit(1); }
}
#define CHECK(v) check((v), __LINE__)
struct Device {
    unsigned reads = 0, inject = 0xffffffffU, calls = 0, highs = 0;
    std::uint32_t anchor = 10000, tick = 1;
    static Device& self(void* p) { return *static_cast<Device*>(p); }
    static bool setup(void* p) { ++self(p).calls; return true; }
    static bool setupPwm(void* p, motors::Channel) { return setup(p); }
    static bool enable(void* p, bool high) { ++self(p).calls; self(p).highs += high; return true; }
    static bool pwm(void* p, motors::Channel, std::uint32_t, std::uint32_t pulse) {
        CHECK(pulse == 0); return setup(p);
    }
    static std::uint32_t clock(void* p) {
        auto& d = self(p); const auto index = ++d.reads;
        return d.anchor + index*d.tick - (index == d.inject ? 2U : 0U);
    }
    static ui::MatrixStatus matrixBegin(void*, ui::MatrixGrant) { return ui::MatrixStatus::INIT_UNCONFIRMED; }
    static ui::MatrixStatus matrix(void*, std::uint32_t, const ui::Frame&) {
        return ui::MatrixStatus::SUBMITTED_UNCONFIRMED;
    }
    motors::Port port() { return {this, setup, setupPwm, enable, pwm, setup, clock,
        {1000U, 1000U, 1000U, 1000U}}; }
};
struct Sources : Device {
    line_qtr::Snapshot line;
    unsigned qtr_starts=0, qtr_advances=0, imu_begins=0, imu_advances=0, cancelled=0;
    unsigned violations=0;
    bool frozen_charge=false, skip_new=false, imu_off=false, pending=false;
    bool defer_complete=false, crossed_threshold=false;
    std::uint32_t imu_started=0;
    static Sources& source(void* p) { return *static_cast<Sources*>(p); }
    static line_qtr::Status beginLine(void* p,bool exclusive) {
        CHECK(exclusive); auto& d=source(p); d.line.phase=line_qtr::Phase::IDLE;
        d.line.status=line_qtr::Status::OK; return line_qtr::Status::OK;
    }
    static line_qtr::Status startLine(void* p) {
        auto& d=source(p); ++d.qtr_starts;
        if(d.line.phase==line_qtr::Phase::DISCHARGING) return line_qtr::Status::BUSY;
        if (d.skip_new) return line_qtr::Status::NOT_DUE;
        d.line={}; d.line.phase=line_qtr::Phase::CHARGING; d.line.status=line_qtr::Status::OK;
        d.line.sequence=1; d.line.started_us=d.anchor; d.line.drive_completed_us=d.anchor+1;
        return line_qtr::Status::OK;
    }
    static line_qtr::Snapshot readLine(void* p) { return source(p).line; }
    static line_qtr::Snapshot advanceLine(void* p) {
        auto& d=source(p); ++d.qtr_advances;
        if (d.frozen_charge) return d.line;
        if (d.line.phase==line_qtr::Phase::CHARGING) {
            d.anchor+=12; d.line.phase=line_qtr::Phase::DISCHARGING;
            d.line.released_mask=15; return d.line;
        }
        const auto s=d.line.started_us;
        if (d.defer_complete && !d.crossed_threshold) {
            d.crossed_threshold=true; d.anchor=s+417;
            for(auto& pad:d.line.pad) pad.lower_us=400;
            return d.line;
        }
        if(d.anchor-s<417) d.anchor=s+417;
        const auto lower=d.anchor-s-17;
        auto& l=d.line; l.phase=line_qtr::Phase::COMPLETE; l.valid=true;
        l.checked_us=l.completed_us=d.anchor; l.advances=2; l.high_mask=l.low_mask=15;
        l.cleanup.attempted_mask=15; l.cleanup.started_us=d.anchor-1; l.cleanup.completed_us=d.anchor;
        for (auto& pad:l.pad) { pad.release_before_us=pad.release_after_us=s+12;
            pad.last_high_before_us=s+13+lower; pad.first_low_after_us=s+14+lower;
            pad.lower_us=lower; pad.upper_us=lower+3; }
        return l;
    }
    static line_qtr::Snapshot cancelLine(void* p) {
        auto& d=source(p); ++d.cancelled; d.line.phase=line_qtr::Phase::FAULT;
        d.line.status=line_qtr::Status::CANCELLED; return d.line;
    }
    static imu::SetupReport beginImu(void*,std::uint32_t t,bool power) {
        CHECK(power); imu::SetupReport r; r.state=imu::SetupState::PROFILE_READY;
        r.started_us=r.observed_us=t; r.bus_status=imu::BusStatus::OK; return r;
    }
    static imu::SetupReport setupAdvance(void*,std::uint32_t) { CHECK(false); return {}; }
    static imu::SampleProgress requestImu(void* p,std::uint32_t t) {
        auto& d=source(p); ++d.imu_begins;
        if(d.imu_off) return {imu::AsyncState::FAULT,false,false,{}};
        d.pending=true; d.imu_started=t; return {imu::AsyncState::PENDING,true,false,{}};
    }
    static imu::SampleProgress advanceImu(void* p,std::uint32_t) {
        auto& d=source(p); ++d.imu_advances;
        if(d.line.phase==line_qtr::Phase::CHARGING) ++d.violations;
        d.anchor+=10; d.pending=false; imu::Sample s;
        s.state=imu::SampleState::OBSERVATION; s.checked_us=d.anchor; s.sequence=1;
        s.bus_status=imu::BusStatus::OK; s.motion.status=imu::DecodeStatus::OK;
        s.motion.coherent=true; s.motion.started_us=d.imu_started;
        s.motion.completed_us=d.anchor; s.motion.gyro_dps[2]=1; s.motion.accel_g[0]=0.1F;
        return {imu::AsyncState::COMPLETE,false,true,s};
    }
    static imu::SampleProgress cancelImu(void* p,std::uint32_t) {
        auto& d=source(p); ++d.cancelled; d.pending=false; return {};
    }
    static imu::Sample failure(void*,std::uint32_t) { CHECK(false); return {}; }
    app::SourcePort sources() { return {this,nullptr,nullptr,beginLine,startLine,advanceLine,
        cancelLine,readLine,beginImu,setupAdvance,requestImu,advanceImu,cancelImu,failure,nullptr,nullptr}; }
};
void sourceCases() {
    for (const auto age:{1999U,2000U,2001U,6000U}) {
        Sources d; d.tick=0; app::Runtime r(d.port(),{},d.sources());
        app::SetupGrants g; g.qtr_exclusive_pads=true; g.imu_enabled=true;
        g.imu_power_confirmed=true; g.mounting={{1,2,3},true};
        CHECK(r.begin(g)); CHECK(r.step()); CHECK(d.violations==0); CHECK(d.imu_advances==1);
        CHECK(r.decisionInput().imu_ok); CHECK(r.decisionInput().line.presence==core::LinePresence::VALID);
        const auto observed=r.imuEvidence().observation_us; const auto qtr_start=r.lineEvidence().started_us;
        d.skip_new=d.imu_off=true; d.anchor=observed+age; CHECK(r.step());
        CHECK(r.decisionInput().imu_ok==(age<=2000)); CHECK(r.report().imu_expired==(age>2000));
        CHECK(r.imuEvidence().observation_us==observed);
        CHECK(r.decisionInput().line.presence==(d.anchor-qtr_start<6000 ? core::LinePresence::VALID:core::LinePresence::ABSENT));
        if (age>2000) { CHECK(r.decisionInput().imu.sequence==0); CHECK(r.decisionInput().raw_gyro_z_dps==0); }
        // Three individually valid increments traverse a whole uint32 domain.
        for (unsigned i=0;i<3;++i) {
            d.anchor+=0x60000000U; CHECK(r.step()); CHECK(!r.decisionInput().imu_ok);
            CHECK(r.decisionInput().line.presence==core::LinePresence::ABSENT);
        }
        CHECK(r.imuEvidence().observation_us==observed); CHECK(d.violations==0);
    }
    Sources d; d.tick=0; d.frozen_charge=true;
    app::Runtime r(d.port(),{},d.sources()); app::SetupGrants g; g.qtr_exclusive_pads=true;
    CHECK(r.begin(g)); CHECK(!r.step()); CHECK(r.report().fault==app::RuntimeFault::SERVICE_LIMIT);
    CHECK(d.qtr_advances==config::APP_SERVICE_MAX_PASSES); CHECK(d.cancelled==1);
    CHECK(!r.transaction().report().decision_made); CHECK(d.highs==0);
    Sources continued; continued.tick=0; continued.defer_complete=true;
    app::Runtime control(continued.port(),{},continued.sources());
    app::SetupGrants control_grant; control_grant.qtr_exclusive_pads=true;
    control_grant.default_line_thresholds_confirmed=true;
    CHECK(control.begin(control_grant)); CHECK(control.step());
    CHECK(continued.line.phase==line_qtr::Phase::DISCHARGING);
    CHECK(control.decisionInput().line.presence==core::LinePresence::ABSENT);
    const auto advances=continued.qtr_advances;
    continued.anchor=control.report().next_release_us; CHECK(control.step());
    CHECK(continued.qtr_advances==advances+1);
    CHECK(control.decisionInput().line.presence==core::LinePresence::VALID);
    CHECK(control.lineEvidence().sequence==1);
}
void passive(app::Runtime& r, Device& d) {
    auto reads = d.reads, calls = d.calls;
    for (unsigned i=0;i<3;++i) { CHECK(!r.step()); CHECK(!r.begin({})); r.abort(); }
    CHECK(reads == d.reads); CHECK(calls == d.calls); CHECK(d.highs == 0);
}
}
int main() {
    for (unsigned inject=1;inject<=24;++inject) {
        Device d; app::SourcePort port; port.beginMatrix = Device::matrixBegin;
        port.submitMatrix = Device::matrix;
        app::Runtime r(d.port(), {}, port); app::SetupGrants grants; grants.matrix_enabled = true;
        CHECK(r.begin(grants));
        d.anchor += 100; d.reads = 0; d.inject = inject;
        bool result = r.step(); const auto& t = r.transaction().report();
        std::printf("inject=%u ok=%u runtime=%u fault=%u transaction=%u decision=%u finished=%u timing=%u clocks=%u S=%u D=%u A=%u C=%u\n",
            inject, result, unsigned(r.report().phase), unsigned(r.report().fault),
            unsigned(t.fault), t.decision_made, t.finished, t.timing_valid,
            d.reads,t.started_us,t.decision_us,t.applied.feedback.applied_us,t.completed_us);
#ifndef REVIEW_HISTORICAL
        if (inject>=2 && inject<=12) {
            CHECK(!result); CHECK(r.report().phase==app::RuntimePhase::FAULT);
            CHECK(!t.finished); CHECK(!t.timing_valid);
            if (inject<=8) CHECK(!t.decision_made);
        }
#endif
        if (r.report().phase == app::RuntimePhase::FAULT) passive(r,d);
    }
    Device frozen; app::Runtime r(frozen.port(),{},{}); CHECK(r.begin({}));
    frozen.anchor = r.report().next_release_us; frozen.tick = 0;
    CHECK(r.step()); CHECK(r.report().epochs == 1);
    for (unsigned i=1;i<config::APP_CLOCK_STALL_MAX_POLLS;++i) {
        CHECK(!r.step()); CHECK(r.report().phase == app::RuntimePhase::RUNNING);
    }
    CHECK(!r.step()); CHECK(r.report().fault == app::RuntimeFault::CLOCK);
    passive(r,frozen);
    sourceCases();
    std::printf("PASS checks=%u\n", checks);
}

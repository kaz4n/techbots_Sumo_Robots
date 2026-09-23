// Independent D095 adversarial review of actual transaction and halt sources.
// Expected chronology and callback counts are derived from the frozen contract.
// Standalone assertion harness runs under both motor macros with sanitizers.
#include "app/transaction.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

namespace {
unsigned checks = 0;
void check(bool value, int line) {
    ++checks;
    if (!value) { std::fprintf(stderr, "review assertion line %d\n", line); std::exit(1); }
}
#define EXPECT(v) check((v), __LINE__)
struct Device {
    std::array<std::uint32_t, 8> script{};
    std::uint32_t now = 0;
    unsigned reads = 0, scripted = 0, operations = 0, fail_at = 0, highs = 0;
    unsigned zeros = 0, settles = 0;
    bool enabled = false;
    static Device& self(void* p) { return *static_cast<Device*>(p); }
    bool operation() { return ++operations != fail_at; }
    static bool configure(void* p) { return self(p).operation(); }
    static bool configurePwm(void* p, motors::Channel) { return self(p).operation(); }
    static bool enable(void* p, bool high) {
        auto& d = self(p); if (high) ++d.highs;
        bool ok = d.operation(); if (ok) d.enabled = high; return ok;
    }
    static bool pwm(void* p, motors::Channel, std::uint32_t, std::uint32_t pulse) {
        auto& d = self(p); if (!pulse) ++d.zeros; return d.operation();
    }
    static bool settle(void* p) { auto& d = self(p); ++d.settles; return d.operation(); }
    static std::uint32_t clock(void* p) {
        auto& d = self(p); unsigned i = d.reads++;
        return i < d.scripted ? d.script[i] : d.now;
    }
    motors::Port port() { return {this, configure, configurePwm, enable, pwm,
                                  settle, clock, {1000, 1000, 1000, 1000}}; }
    void clear() { reads = operations = fail_at = highs = zeros = settles = scripted = 0; }
};
fsm::RobotInput input() {
    fsm::RobotInput in; in.initialization_complete = true; in.observations_fresh = true;
    in.opp_raw_mask = 0x78; in.imu_ok = true; in.vbat_valid = true; in.vbat_v = 11.1F;
    for (auto& v : in.line_raw_us) v = 1000;
    return in;
}
void passive(app::Transaction& owner, Device& d) {
    unsigned before = d.operations, clocks = d.reads;
    auto fault = owner.report().fault;
    EXPECT(!owner.open()); EXPECT(!owner.decide(input())); EXPECT(!owner.finish());
    EXPECT(!owner.initialize()); owner.abort(); owner.abort();
    EXPECT(d.operations == before); EXPECT(d.reads == clocks); EXPECT(owner.report().fault == fault);
}
void chronology() {
    const std::uint32_t offsets[] = {0U, 1U, 2U, 799U, 1001U, 0x7fffffffU,
                                     0x80000000U, 0x80000001U, 0xffffffffU};
    unsigned cases = 0;
    for (auto s : {0U, 0xfffffffeU}) for (auto d : offsets) for (auto a : offsets)
    for (auto c : offsets) {
        Device hw; app::Transaction owner(hw.port()); EXPECT(owner.initialize()); hw.clear();
        hw.scripted = 6; hw.script = {s, s+d, s+a, s+c, s+c, s+c, 0, 0};
        EXPECT(owner.open()); bool decision = owner.decide(input());
        bool decision_valid = d < 0x80000000U;
        EXPECT(decision == decision_valid);
        if (!decision_valid) EXPECT(owner.report().fault == app::Fault::CLOCK);
        else {
            bool finished = owner.finish();
            bool clock_valid = c < 0x80000000U && std::uint32_t(c-d) < 0x80000000U;
            bool receipt_valid = a >= d && a <= c;
            EXPECT(finished == (clock_valid && receipt_valid));
            if (!clock_valid) EXPECT(owner.report().fault == app::Fault::CLOCK);
            else if (!receipt_valid) EXPECT(owner.report().fault == app::Fault::RECEIPT);
            else {
                EXPECT(owner.previous().execution_us == c);
                EXPECT(owner.previous().applied_us == s+a);
                EXPECT(owner.previous().completed_us == s+c);
                EXPECT(owner.previous().applied_valid); EXPECT(owner.previous().duration_valid);
            }
        }
        if (owner.report().phase == app::Phase::FAULT) {
            EXPECT(!owner.previous().applied_valid); EXPECT(!owner.previous().duration_valid);
            EXPECT(owner.report().halt.attempted); EXPECT(hw.highs == 0); passive(owner, hw);
        }
        ++cases;
    }
    std::printf("chronology cases=%u\n", cases);
}
void haltFailurePriority() {
    for (unsigned cause = 0; cause <= 6; ++cause) {
        Device d; motors::MotorGate gate(d.port()); EXPECT(gate.begin()); d.clear();
        d.fail_at = cause; auto h = gate.halt();
        EXPECT(h.fresh && h.attempted && h.timing_valid);
        EXPECT(h.inhibition_confirmed == (cause == 0)); EXPECT(d.operations == 6);
        EXPECT(d.zeros == 4 && d.settles == 1 && d.highs == 0 && d.reads == 2);
        EXPECT(h.fault == (cause ? motors::Fault::IO : motors::Fault::STOPPED));
        unsigned operations = d.operations; EXPECT(!gate.halt().fresh);
        EXPECT(d.operations == operations && d.reads == 2);
        d.fail_at = d.operations + 1; EXPECT(!gate.reset());
        operations = d.operations; auto cached = gate.halt();
        EXPECT(!cached.fresh && cached.fault == h.fault); EXPECT(d.operations == operations);
    }
}
void lifecycle() {
    Device d; app::Transaction owner(d.port()); EXPECT(d.operations == 0 && d.reads == 0);
    EXPECT(owner.initialize()); auto source = input();
    auto tick = [&](std::uint32_t t, core::ButtonLevel button, bool stop = false) {
        d.now = t; source.button = button; source.stop_requested = stop;
        source.t_us = 9; source.timing = {}; source.previous.token = 888;
        EXPECT(owner.open()); EXPECT(owner.decide(source)); d.now += 10; EXPECT(owner.finish());
        EXPECT(owner.report().robot.contract_faults == 0); EXPECT(owner.previous().execution_us == 10);
    };
    tick(1000, core::ButtonLevel::NONE); tick(2000, core::ButtonLevel::NONE);
    tick(22000, core::ButtonLevel::NONE); tick(23000, core::ButtonLevel::START);
    tick(43000, core::ButtonLevel::START); tick(44000, core::ButtonLevel::NONE);
    tick(64000, core::ButtonLevel::NONE); EXPECT(owner.report().robot.lifecycle.gate.start_release);
    for (std::uint32_t t = 65000; t <= 5164000; t += 1000) tick(t, core::ButtonLevel::NONE);
    EXPECT(owner.report().robot.lifecycle.gate.go);
    EXPECT(d.enabled == (MOTORS_ALLOWED != 0));
    tick(5165000, core::ButtonLevel::NONE, true);
    EXPECT(!d.enabled); EXPECT(owner.recording().phase() == recorder::AttemptPhase::DRAINING);
    auto final_token = owner.report().robot.token;
    tick(5166000, core::ButtonLevel::NONE);
    EXPECT(owner.recording().phase() == recorder::AttemptPhase::SEALED);
    EXPECT(owner.report().robot.frame_token == final_token);
    EXPECT(!owner.recording().summary().final_frame_missing);
    EXPECT(!owner.recording().incomplete());
    auto frames = owner.recording().frames().size(); auto old = owner.previous(); owner.abort();
    EXPECT(owner.previous().token == old.token && owner.previous().applied_us == old.applied_us);
    EXPECT(owner.previous().execution_us == old.execution_us && !owner.previous().duration_valid);
    EXPECT(owner.report().finished && owner.report().timing_valid);
    EXPECT(owner.recording().phase() == recorder::AttemptPhase::SEALED);
    EXPECT(owner.recording().frames().size() == frames); passive(owner, d);
}
}
int main() {
    chronology(); haltFailurePriority(); lifecycle();
    std::printf("PASS checks=%u motor_macro=%d\n", checks, MOTORS_ALLOWED);
}

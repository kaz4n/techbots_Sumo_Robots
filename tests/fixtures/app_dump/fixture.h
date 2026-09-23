// Supplies D101 dump callbacks around the real public application pipeline.
// Keeps synthetic transport and source observations separate from native evidence.
// Independent application dump tests verify callback authority and lifetime.
#pragma once
#include "../app_runtime_fixture.h"
#include <algorithm>
#include <string>
#include <vector>

namespace app_dump_test {
namespace dump = recorder::dump;
struct Source : runtime_test::Fake {
    bool reject_enable = false;
    static bool writeEnable(void* c, bool value) {
        auto& f = *static_cast<Source*>(c);
        Fake::enable(c, value);
        return !f.reject_enable;
    }
    motors::Port motorPort() {
        auto p = Fake::motorPort(); p.writeEnable = writeEnable; return p;
    }
};
enum class Kind { BEGIN, READY, WRITE, CANCEL };
struct Observation {
    Kind kind; std::uint32_t at, end, decision; std::uint64_t token;
    unsigned source_calls; app::Phase transaction;
    bool consumed, applied_valid, enabled, halted;
    float left, right; core::State state; recorder::AttemptPhase recording;
};
struct Sink {
    Source& source;
    app::Runtime* runtime = nullptr;
    std::vector<Observation> calls;
    std::vector<std::string> offers;
    std::string bytes;
    dump::SetupGrant received;
    dump::NativeStatus setup = dump::NativeStatus::OK;
    dump::WriteStatus status = dump::WriteStatus::PROGRESS;
    std::size_t limit = 64U, forced_count = 0U;
    unsigned begins = 0U, readies = 0U, writes = 0U, cancels = 0U;
    std::uint32_t begin_work = 0U, ready_work = 0U, write_work = 0U, cancel_work = 0U;
    bool linux_ready = true, override_count = false, reverse_ready = false, reverse_write = false;
    explicit Sink(Source& s) : source(s) {}
    void observe(Kind kind, std::uint32_t work, bool reverse = false) {
        const auto& tx = runtime->transaction().report();
        const auto& applied = tx.applied.feedback;
        const auto at = source.now;
        source.now = reverse ? at - 1U : at + work;
        calls.push_back({kind, at, source.now, tx.decision_us, tx.robot.token,
            source.count, tx.phase, tx.applied.consumed, applied.applied_valid,
            applied.motors_enabled, tx.halt.attempted, applied.duty_l, applied.duty_r,
            tx.robot.outputs.ui_state, runtime->transaction().recording().phase()});
    }
    static dump::NativeStatus begin(void* c, const dump::SetupGrant& grant) {
        auto& s = *static_cast<Sink*>(c); ++s.begins; s.received = grant;
        s.observe(Kind::BEGIN, s.begin_work); return s.setup;
    }
    static bool ready(void* c) {
        auto& s = *static_cast<Sink*>(c); ++s.readies;
        s.observe(Kind::READY, s.ready_work, s.reverse_ready); return s.linux_ready;
    }
    static dump::WriteResult write(void* c, const char* data, std::size_t size) {
        auto& s = *static_cast<Sink*>(c); ++s.writes; s.offers.emplace_back(data, size);
        s.observe(Kind::WRITE, s.write_work, s.reverse_write);
        const auto count = s.override_count ? s.forced_count :
            (s.status == dump::WriteStatus::PROGRESS ? std::min(s.limit, size) : 0U);
        if (s.status == dump::WriteStatus::PROGRESS && count <= size) s.bytes.append(data, count);
        return {s.status, count};
    }
    static void cancel(void* c) {
        auto& s = *static_cast<Sink*>(c); ++s.cancels; s.observe(Kind::CANCEL, s.cancel_work);
    }
    app::DumpPort port() { return {this, begin, ready, {this, write, cancel}}; }
};
struct Rig {
    Source fake;
    Sink sink{fake};
    app::Runtime owner;
    explicit Rig(unsigned missing = 0U) : owner(fake.motorPort(), fake.adcPort(),
        fake.sourcePort(), selectedPort(missing)) { sink.runtime = &owner; }
    app::DumpPort selectedPort(unsigned missing) {
        auto p = sink.port();
        if (missing == 1U) p.begin = nullptr;
        if (missing == 2U) p.ready = nullptr;
        if (missing == 3U) p.output.write = nullptr;
        if (missing == 4U) p.output.cancel = nullptr;
        return p;
    }
    app::SetupGrants grants(bool enabled = true) const {
        auto g = runtime_test::grants(true, false);
#ifndef APP_TEST_CONFIGURED_BUTTONS
        g.adc_pair = false;
#endif
        g.dump_enabled = enabled; g.dump = {true, true, false, true};
        g.dump_origin = dump::Origin::SYNTHETIC; return g;
    }
    bool begin(bool enabled = true) { return owner.begin(grants(enabled)); }
    bool next() { fake.now = owner.report().next_release_us; return owner.step(); }
    bool run(unsigned ticks, std::uint16_t raw = 50U) {
        fake.button_raw = raw;
        for (unsigned i = 0U; i < ticks; ++i) if (!next()) return false;
        return true;
    }
    const fsm::RobotResult& robot() const { return owner.transaction().report().robot; }
    bool seal() {
        if (!run(35U) || !run(30U, 1000U) || !run(30U)) return false;
        if (robot().outputs.ui_state != core::State::COUNTDOWN) return false;
        if (!run(30U, 2000U) || !run(30U)) return false;
        return robot().outputs.ui_state == core::State::IDLE &&
            owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED;
    }
    bool selectDump() {
        if (!run(30U) || !run(1030U, 2000U) || !run(30U)) return false;
        for (unsigned i = 0U; i < 3U; ++i)
            if (!run(30U, 2000U) || !run(30U)) return false;
        return robot().menu.selection.service_menu &&
            robot().menu.selection.service == countdown::Service::LOG_DUMP;
    }
    bool requestDump() {
        if (!run(30U, 1000U)) return false;
        fake.button_raw = 50U;
        for (unsigned i = 0U; i < 30U; ++i) {
            if (!next()) return false;
            if (robot().menu.request == countdown::Service::LOG_DUMP) return true;
        }
        return false;
    }
    bool active() { return begin() && seal() && selectDump() && requestDump() &&
        owner.report().dump.phase == dump::Phase::ACTIVE; }
    bool finish() {
        for (unsigned i = 0U; i < 10000U && owner.report().dump.phase == dump::Phase::ACTIVE; ++i)
            if (!next()) return false;
        return owner.report().dump.phase == dump::Phase::SENT_UNCONFIRMED;
    }
};
} // namespace app_dump_test

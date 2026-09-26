// Tests supplied B15 session identity without changing protocol version or grants.
// Independent literal expectations cover legacy, cancellation and real 200 s recording.
// Host-only sinks preserve inhibited IDLE and never initialize physical hardware.
#include "doctest.h"
#include "fixtures/dump_fixture.h"
#include "fixtures/recorder_transport/fixture.h"
#include <fstream>
#include <cstdlib>
#include <string>

namespace {
using namespace dump_test;
constexpr std::uint64_t SESSION = 0xF123456789ABCDEFULL;
#define SESSION_REQUIRE(c) do { const bool ok = (c); CHECK(ok); if (!ok) return; } while(false)

void checkWire(const std::string& wire, std::uint64_t session, unsigned frames, unsigned events) {
    const auto token = std::to_string(session);
    CHECK(wire.find("SUMOX26_DUMP,1," + token + ",") == 0U);
    std::size_t offset = wire.find('\n') + 1U;
    while (offset < wire.size()) {
        const auto comma = wire.find(',', offset);
        const auto end = wire.find('\n', offset);
        SESSION_REQUIRE(comma != std::string::npos && end != std::string::npos);
        CHECK(wire.substr(comma + 1U, token.size() + 1U) == token + ",");
        offset = end + 1U;
    }
    const auto ending = wire.rfind("END,");
    SESSION_REQUIRE(ending != std::string::npos);
    CHECK(wire.substr(ending) == "END," + token + "," + std::to_string(frames) + "," +
          std::to_string(events) + "," + std::to_string(crc(wire.substr(0, ending))) + "\n");
}
struct SessionRig {
    d116::Port io;
    recorder::dump::SetupGrant observed{};
    recorder_transport::Runner runner;
    SessionRig() : runner(io.clockPort(), {this, begin, ready, {&io, d116::Port::write, d116::Port::cancel}}) {
        io.owner = &runner;
    }
    static recorder::dump::NativeStatus begin(void* context, const recorder::dump::SetupGrant& grant) {
        auto& self = *static_cast<SessionRig*>(context);
        self.observed = grant;
        ++self.io.begins;
        const auto& r = self.runner.report();
        CHECK(r.configure_enable_calls == 1U);
        CHECK(r.configure_pwm_calls == 4U);
        CHECK(r.write_enable_calls == 1U);
        CHECK(r.write_pwm_calls == 4U);
        CHECK(r.settle_calls == 1U);
        return self.io.setup;
    }
    static bool ready(void* context) { return d116::Port::ready(&static_cast<SessionRig*>(context)->io); }
    void tick() { io.now = runner.report().next_release_us; runner.poll(); }
    void untilActive() {
        for (unsigned i = 0; i < 210000U && runner.dump().phase != dump::Phase::ACTIVE && !d116::terminal(runner); ++i) tick();
        CHECK(runner.dump().phase == dump::Phase::ACTIVE);
    }
};
recorder::dump::SetupGrant untrusted(std::uint64_t session = SESSION) {
    return {true, true, true, false, recorder::dump::ReceiveStream::UNTRUSTED_RECEIVE_STREAM, session};
}
}

TEST_CASE("B15 supplied session zero preserves legacy bytes and nonzero uint64 binds every record") {
    for (const std::uint64_t session : std::array<std::uint64_t,4>{0U, 1U, SESSION, UINT64_MAX}) {
        Protocol p;
        p.context.session = session;
        SESSION_REQUIRE(p.finish());
        const auto expected = session == 0U ? 10U : session;
        CHECK(p.report.session == expected);
        CHECK(p.report.epoch == 1U);
        checkWire(p.sink.bytes, expected, 2U, 1U);
        Protocol another;
        another.context.session = session;
        another.sink.limit = 1U;
        SESSION_REQUIRE(another.finish());
        CHECK(another.sink.bytes == p.sink.bytes);
    }
}

TEST_CASE("B15 changing supplied session cancels before writes even when time and Robot result repeat") {
    for (const auto before : std::array<std::uint64_t,3>{0U, 10U, SESSION}) {
        for (const auto after : std::array<std::uint64_t,4>{0U, 10U, SESSION, 1U}) {
            if (before == after) continue;
            Protocol p;
            p.context.session = before;
            p.sink.limit = 1U;
            p.step();
            const auto bytes = p.sink.bytes;
            const auto calls = p.sink.offered.size();
            p.context.session = after;
            p.step();
            CHECK(p.report.phase == dump::Phase::CANCELLED);
            CHECK(p.report.reason == dump::Reason::SESSION_CHANGED);
            CHECK(p.report.session == (before == 0U ? 10U : before));
            CHECK(p.sink.bytes == bytes);
            CHECK(p.sink.offered.size() == calls);
            CHECK(p.sink.cancels == 1U);
            p.next();
            CHECK(p.sink.cancels == 1U);
            CHECK(p.sink.bytes == bytes);
        }
    }
}

TEST_CASE("B13 B15 session opt-in never relaxes ownership setup or readiness grants") {
    for (unsigned bits = 0; bits < 16; ++bits) {
        for (unsigned mode : {0U, 1U, 2U, 255U}) {
            for (const std::uint64_t session : std::array<std::uint64_t,2>{0U, SESSION}) {
                recorder::dump::SetupGrant g{bool(bits & 1), bool(bits & 2), bool(bits & 4), bool(bits & 8),
                    static_cast<recorder::dump::ReceiveStream>(mode), session};
                const bool accepted = (bits & 7) == 7 && ((mode == 0U && bool(bits & 8)) ||
                                                        (mode == 1U && session != 0U));
                CHECK(recorder::dump::setupGrantAccepted(g) == accepted);
                SessionRig f;
                CHECK(f.runner.begin(true, g) == accepted);
                if (!accepted) {
                    CHECK(f.runner.report().failure == d116::Failure::GRANT);
                    CHECK(f.io.begins == 0U);
                    CHECK(f.io.clocks == 0U);
                    CHECK(f.runner.report().configure_enable_calls == 0U);
                } else {
                    CHECK(f.io.begins == 1U);
                    CHECK(f.observed.framing_clean == g.framing_clean);
                    CHECK(f.observed.receive_stream == g.receive_stream);
                    CHECK(f.observed.session == session);
                }
                CHECK(f.runner.report().enabled_en == 0U);
                CHECK(f.runner.report().nonzero_pwm == 0U);
            }
        }
    }
}

TEST_CASE("B15 full synthetic 200 second pipeline preserves all rows with caller supplied session") {
    SessionRig f;
    SESSION_REQUIRE(f.runner.begin(true, untrusted()));
    d116::SourceCopy frozen;
    bool sealed = false;
    for (unsigned i = 0; i < 230000U && !d116::terminal(f.runner); ++i) {
        f.tick();
        if (!sealed && f.runner.source().phase() == recorder::AttemptPhase::SEALED) {
            frozen.take(f.runner.source());
            sealed = true;
        }
        if (f.runner.report().service_only) {
            CHECK(f.runner.transaction().report().robot.outputs.ui_state == core::State::IDLE);
            CHECK_FALSE(f.runner.transaction().report().applied.feedback.motors_enabled);
        }
    }
    SESSION_REQUIRE(f.runner.report().phase == d116::Phase::SENT_UNCONFIRMED);
    CHECK(sealed);
    frozen.check(f.runner.source());
    CHECK(f.runner.report().release_token == 69U);
    CHECK(f.runner.report().stop_token == 200069U);
    CHECK(f.runner.report().request_token == 202472U);
    CHECK(f.runner.dump().session == SESSION);
    CHECK(f.runner.dump().epoch == 69U);
    CHECK(f.runner.dump().frames == 5001U);
    CHECK(f.runner.dump().events == 8U);
    CHECK_FALSE(f.runner.source().incomplete());
    CHECK(f.io.errors == 0U);
    CHECK(f.io.cancels == 0U);
    CHECK(f.runner.report().enabled_en == 0U);
    CHECK(f.runner.report().nonzero_pwm == 0U);
    CHECK_FALSE(f.observed.framing_clean);
    const std::string wire(f.io.bytes.data(), f.io.size);
    checkWire(wire, SESSION, 5001U, 8U);
    if (const char* output = std::getenv("SUMOX_SESSION_WIRE")) {
        std::ofstream file(output, std::ios::binary);
        file.write(wire.data(), static_cast<std::streamsize>(wire.size()));
        CHECK(file.good());
    }
}

TEST_CASE("B13 B15 supplied session retains Linux readiness cancellation and slow total deadline") {
    for (bool slow : {false, true}) {
        SessionRig f;
        if (slow) f.io.max_ack = 1U;
        SESSION_REQUIRE(f.runner.begin(true, untrusted()));
        f.untilActive();
        const auto source = d116::summary(f.runner.source());
        if (!slow) f.io.ready_value = false;
        for (unsigned i = 0; i < 310000U && !d116::terminal(f.runner); ++i) f.tick();
        CHECK(f.runner.report().phase == d116::Phase::FAILED);
        CHECK(f.runner.dump().reason == (slow ? dump::Reason::TOTAL : dump::Reason::LINUX_UNAVAILABLE));
        CHECK(f.runner.dump().session == SESSION);
        CHECK(f.io.cancels == 1U);
        CHECK(f.runner.report().enabled_en == 0U);
        CHECK(f.runner.report().nonzero_pwm == 0U);
        CHECK(f.io.errors == 0U);
        CHECK(d116::summary(f.runner.source()) == source);
        const auto bytes = f.io.size;
        for (unsigned i = 0; i < 20U; ++i) f.tick();
        CHECK(f.io.size == bytes);
        CHECK(f.io.cancels == 1U);
    }
}

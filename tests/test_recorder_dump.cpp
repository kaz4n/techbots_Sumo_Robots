// Tests D090 retained-attempt streaming from B13/B15 public contracts.
// Independently exercises inhibition, identity, deadlines, bytes and cancellation.
// Run in the normal host suite and strict sanitizer build without hardware I/O.
#include "doctest.h"
#include "fixtures/dump_fixture.h"
#include <cmath>
#include <cstring>

#define DUMP_REQUIRE(condition) do { const bool dump_required = (condition); \
    CHECK(dump_required); if (!dump_required) return; } while (false)

namespace {
using namespace dump_test;
const char* SUMMARY_HEADER = "schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,event_overflow,event_rejected,incomplete\n";
const char* FRAME_HEADER = "schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex\n";
const char* EVENT_HEADER = "schema_version,ordinal,t_us,type,detail,value,raw_hex\n";
std::string literalPrefix() {
    return std::string("SUMOX26_DUMP,1,10,1,1,25,5001,4096,2,1\nSH,10,") + SUMMARY_HEADER +
        "SR,10,1,1,2,1234,1,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,1,0,0,0\nFH,10," + FRAME_HEADER +
        "FR,10,1,0,0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,00000000020100000000000000000000000000000000000000\n"
        "FR,10,1,1,0,0,10,1,0,0,0,0,0,0,0,0,0,0,0,000000000a0100000000000000000000000000000000000000\nEH,10," + EVENT_HEADER +
        "ER,10,1,0,1234,0,1,0,d204000000010000\n";
}
}

TEST_CASE("B13 B15 D090 actual Robot MotorGate recorder service pipeline preserves a stopped attempt through local reset") {
    Pipeline p;
    p.startAttempt();
    DUMP_REQUIRE(p.result.outputs.ui_state == core::State::COUNTDOWN);
    p.sealByStop();
    DUMP_REQUIRE(p.source.phase() == recorder::AttemptPhase::SEALED);
    const auto epoch = p.source.summary().epoch_token;
    const auto frames = p.source.frames().size();
    CHECK(p.result.outputs.ui_state == core::State::STOPPED);
    p.selectDump(); p.requestDump();
    CHECK(p.sink.bytes.empty());
    CHECK(p.requests == 0U);
    p.resetPreserving();
    CHECK(p.result.outputs.ui_state == core::State::IDLE);
    CHECK(p.source.summary().epoch_token == epoch);
    CHECK(p.source.frames().size() == frames);
    p.selectDump();
    DUMP_REQUIRE(p.result.menu.selection.service == countdown::Service::LOG_DUMP);
    p.requestDump();
    CHECK(p.requests == 1U);
    CHECK(p.finish());
    CHECK(p.source.summary().epoch_token == epoch);
    CHECK(p.source.frames().size() == frames);
    CHECK(p.writes.enabled == 0U);
    CHECK(p.writes.nonzero == 0U);
    CHECK(p.result.lifecycle.gate.phase == countdown::Phase::IDLE);
}

TEST_CASE("B15 D090 literal stream retains all records order decimal envelope and independent CRC") {
    Protocol p;
    DUMP_REQUIRE(p.finish());
    const auto prefix = literalPrefix();
    const auto expected = prefix + "END,10,2,1," + std::to_string(crc(prefix)) + "\n";
    CHECK(p.sink.bytes == expected);
    CHECK(p.report.crc == crc(prefix));
    CHECK(p.report.bytes == expected.size());
    CHECK(p.report.frames == 2U);
    CHECK(p.report.events == 1U);
    CHECK(p.report.phase == dump::Phase::SENT_UNCONFIRMED);
    for (const auto& offered : p.sink.offered) {
        CHECK(offered.size() <= config::DUMP_PAYLOAD_BYTES);
        CHECK(offered.size() > 0U);
    }
}

TEST_CASE("B15 D090 partial acknowledgments preserve exact bytes and never duplicate CRC") {
    for (const std::size_t limit : {1U, 7U, 63U, 64U}) {
        Protocol p; p.sink.limit = limit;
        DUMP_REQUIRE(p.finish());
        const auto prefix = literalPrefix();
        CHECK(p.sink.bytes == prefix + "END,10,2,1," + std::to_string(crc(prefix)) + "\n");
    }
}

TEST_CASE("B15 D090 a pending packet repeats identical offered bytes and does not acknowledge progress") {
    Protocol p; p.sink.status = dump::WriteStatus::PENDING;
    p.step();
    const auto bytes = p.report.bytes;
    for (unsigned n = 0U; n < 5U; ++n) p.next();
    CHECK(p.report.bytes == bytes);
    CHECK(p.sink.bytes.empty());
    DUMP_REQUIRE(!p.sink.offered.empty());
    for (const auto& offered : p.sink.offered) CHECK(offered == p.sink.offered.front());
    p.sink.status = dump::WriteStatus::PROGRESS;
    DUMP_REQUIRE(p.finish());
    CHECK(p.sink.bytes.find("SUMOX26_DUMP,1,10,") == 0U);
}

TEST_CASE("B13 D090 all non-IDLE final states cancel before another write") {
    for (unsigned state = 0U; state <= 11U; ++state) {
        if (state == static_cast<unsigned>(core::State::IDLE)) continue;
        Protocol p; p.step();
        const auto calls = p.sink.offered.size();
        p.result.outputs.ui_state = static_cast<core::State>(state);
        p.next();
        CHECK(p.report.phase == dump::Phase::CANCELLED);
        CHECK(p.report.reason == dump::Reason::CONTEXT);
        CHECK(p.sink.offered.size() == calls);
        CHECK(p.sink.cancels == 1U);
        CHECK(p.source.phase() == recorder::AttemptPhase::SEALED);
    }
}

TEST_CASE("B13 D090 faults duties permissions wrong menu and start pulses revoke transport") {
    for (unsigned condition = 0U; condition < 13U; ++condition) {
        Protocol p; p.step();
        const auto calls = p.sink.offered.size();
        switch (condition) {
        case 0: p.result.contract_faults = 1U; break;
        case 1: p.result.escape_fault = static_cast<edge::EscapeFault>(1U); break;
        case 2: p.result.outputs.motors_enabled = true; break;
        case 3: p.result.outputs.duty_l = 0.001F; break;
        case 4: p.result.outputs.duty_r = -0.001F; break;
        case 5: p.result.outputs.duty_l = std::numeric_limits<float>::quiet_NaN(); break;
        case 6: p.result.menu.selection.service_menu = false; break;
        case 7: p.result.menu.selection.service = countdown::Service::SENSOR_VIEW; break;
        case 8: p.result.lifecycle.gate.phase = countdown::Phase::READY; break;
        case 9: p.result.lifecycle.gate.start_release = true; break;
        case 10: p.result.lifecycle.gate.go = true; break;
        case 11: p.result.outputs.ui_state = static_cast<core::State>(255U); break;
        default: p.result.lifecycle.gate.phase = countdown::Phase::STOPPED; break;
        }
        p.next();
        CHECK(p.report.phase == dump::Phase::CANCELLED);
        CHECK(p.sink.offered.size() == calls);
    }
}

TEST_CASE("B15 D090 empty recording and draining owners refuse without writing") {
    for (unsigned phase = 0U; phase < 3U; ++phase) {
        recorder::AttemptRecorder source; Sink sink; dump::Transfer transfer(sink.port());
        if (phase > 0U) begin(source);
        if (phase > 1U) {
            auto stop = eligible(2U); stop.outputs.ui_state = core::State::STOPPED;
            source.consume(stop);
        }
        const auto report = transfer.step({100U, 100U, true, dump::Origin::UNKNOWN}, eligible(10U, true), source);
        CHECK(report.phase == dump::Phase::REFUSED);
        CHECK(report.reason == dump::Reason::NO_EVIDENCE);
        CHECK(sink.bytes.empty());
    }
}

TEST_CASE("B15 D090 interrupted empty-frame collection remains explicit and dumps headers") {
    recorder::AttemptRecorder source; begin(source); source.onRobotReset();
    Sink sink; dump::Transfer transfer(sink.port());
    auto result = eligible(10U, true);
    auto report = transfer.step({100U, 100U, true, dump::Origin::SYNTHETIC}, result, source);
    for (unsigned n = 1U; n < 1000U && report.phase == dump::Phase::ACTIVE; ++n) {
        result = eligible(10U + n);
        report = transfer.step({100U + n, 100U + n, true, dump::Origin::SYNTHETIC}, result, source);
    }
    CHECK(report.phase == dump::Phase::SENT_UNCONFIRMED);
    CHECK(report.frames == 0U);
    CHECK(report.events == 1U);
    CHECK(sink.bytes.find("\nFH,10,") != std::string::npos);
    CHECK(sink.bytes.find("\nFR,") == std::string::npos);
    CHECK(source.summary().interrupted);
    CHECK(source.incomplete());
}

TEST_CASE("B15 D090 clamped and invalid bytes are retained with their loss statuses") {
    recorder::AttemptRecorder source; sealed(source, true);
    Sink sink; dump::Transfer transfer(sink.port());
    auto report = transfer.step({100U, 100U, true, dump::Origin::UNKNOWN}, eligible(10U, true), source);
    for (unsigned n = 1U; n < 1000U && report.phase == dump::Phase::ACTIVE; ++n)
        report = transfer.step({100U + n, 100U + n, true, dump::Origin::UNKNOWN}, eligible(10U + n), source);
    CHECK(report.phase == dump::Phase::SENT_UNCONFIRMED);
    CHECK(sink.bytes.find("FR,10,1,0,1,0,2,1,") != std::string::npos);
    CHECK(sink.bytes.find("FR,10,1,1,2,0,10,1,") != std::string::npos);
    CHECK(source.frames().clampedCount() == 1U);
    CHECK(source.frames().invalidCount() == 1U);
}

TEST_CASE("B15 D090 reset cancels partial line before caller changes core or recorder") {
    Protocol p; p.sink.limit = 1U; p.step();
    const auto frozen = recorder::csv::captureSummary(p.source);
    const auto bytes = p.sink.bytes;
    p.transfer.onRobotReset();
    CHECK(p.transfer.report().phase == dump::Phase::CANCELLED);
    CHECK(p.transfer.report().reason == dump::Reason::RESET);
    CHECK(p.sink.cancels == 1U);
    CHECK(p.source.summary().epoch_token == frozen.attempt.epoch_token);
    CHECK(p.source.frames().size() == frozen.frame_count);
    p.next();
    CHECK(p.sink.bytes == bytes);
}

TEST_CASE("B15 D090 source object replacement and newly accepted epoch fail before I/O") {
    SUBCASE("same bytes in a different owner still changes source") {
        Protocol p; p.step(); recorder::AttemptRecorder replacement; sealed(replacement);
        const auto calls = p.sink.offered.size(); ++p.context.now_us; ++p.context.decision_us; ++p.result.token;
        const auto report = p.transfer.step(p.context, p.result, replacement);
        CHECK(report.reason == dump::Reason::SOURCE_CHANGED);
        CHECK(p.sink.offered.size() == calls);
    }
    SUBCASE("new attempt changes epoch before any old-row reuse") {
        Protocol p; p.step(); const auto calls = p.sink.offered.size();
        begin(p.source, 100U); p.next();
        CHECK(p.report.reason == dump::Reason::SOURCE_CHANGED);
        CHECK(p.sink.offered.size() == calls);
        CHECK(p.source.summary().epoch_token == 100U);
    }
}

TEST_CASE("B13 D090 exact repeated clock does no work but stale Robot feedback cancels") {
    Protocol p; p.step(); const auto calls = p.sink.offered.size();
    p.step(); CHECK(p.sink.offered.size() == calls);
    p.result.fresh = false; ++p.context.now_us;
    p.step();
    CHECK(p.report.phase == dump::Phase::CANCELLED);
    CHECK(p.report.reason == dump::Reason::STALE_CONTEXT);
    CHECK(p.sink.offered.size() == calls);
}

TEST_CASE("B13 D090 decision age is admitted below one tick and expires at equality") {
    for (const auto age : {config::TICK_US - 1U, config::TICK_US, config::TICK_US + 1U}) {
        Protocol p; p.context.now_us = p.context.decision_us + age;
        p.step();
        if (age < config::TICK_US) CHECK(p.report.phase == dump::Phase::ACTIVE);
        else { CHECK(p.report.reason == dump::Reason::STALE_CONTEXT); CHECK(p.sink.bytes.empty()); }
    }
}

TEST_CASE("B13 D090 the same authentic result may pump below its original decision deadline") {
    Protocol p; p.sink.limit = 1U; p.step();
    p.next(1U, false);
    CHECK(p.report.phase == dump::Phase::ACTIVE);
    CHECK(p.sink.bytes.size() == 2U);
    p.next(config::TICK_US - 2U, false);
    CHECK(p.report.phase == dump::Phase::ACTIVE);
    p.next(1U, false);
    CHECK(p.report.reason == dump::Reason::STALE_CONTEXT);
    CHECK(p.sink.bytes.size() == 3U);
}

TEST_CASE("B13 D090 result tokens reject zero regression skipped ticks and timestamp rewriting") {
    for (unsigned condition = 0U; condition < 6U; ++condition) {
        Protocol p; p.step(); const auto calls = p.sink.offered.size();
        ++p.context.now_us;
        switch (condition) {
        case 0: p.result.token = 0U; break;
        case 1: --p.result.token; break;
        case 2: p.result.token += 2U; ++p.context.decision_us; break;
        case 3: ++p.context.decision_us; break;
        case 4: ++p.result.token; break;
        default: ++p.result.token; --p.context.decision_us; break;
        }
        p.step();
        CHECK(p.report.phase == dump::Phase::CANCELLED);
        CHECK(p.sink.offered.size() == calls);
    }
}

TEST_CASE("B15 D090 natural micros wrap preserves stream while reverse or half-range time cancels") {
    SUBCASE("natural wrap") {
        Protocol p; p.context.now_us = p.context.decision_us = 0xFFFFFFF0U;
        p.step(); p.next(32U);
        CHECK(p.report.phase == dump::Phase::ACTIVE);
        CHECK(p.finish());
    }
    for (const auto delta : {0x80000000U, 0xFFFFFFFFU}) {
        Protocol p; p.step(); const auto calls = p.sink.offered.size();
        p.next(delta);
        CHECK(p.report.reason == dump::Reason::TIME_ORDER);
        CHECK(p.sink.offered.size() == calls);
    }
}

TEST_CASE("B15 D090 pending and no-progress expire exactly at stall deadline before I/O") {
    for (const auto delta : {config::DUMP_STALL_MS * 1000U - 1U,
                             config::DUMP_STALL_MS * 1000U,
                             config::DUMP_STALL_MS * 1000U + 1U}) {
        Protocol p; p.sink.status = dump::WriteStatus::PENDING; p.step();
        const auto calls = p.sink.offered.size(); p.next(delta);
        if (delta < config::DUMP_STALL_MS * 1000U) CHECK(p.report.phase == dump::Phase::ACTIVE);
        else { CHECK(p.report.reason == dump::Reason::STALL); CHECK(p.sink.offered.size() == calls); }
    }
}

TEST_CASE("B15 D090 acknowledgments renew stall deadline but cannot renew total deadline") {
    Protocol p; p.sink.limit = 1U; p.step();
    for (unsigned n = 0U; n < 300U; ++n) {
        p.next(999999U);
        DUMP_REQUIRE(p.report.phase == dump::Phase::ACTIVE);
    }
    p.next(299U);
    CHECK(p.report.phase == dump::Phase::ACTIVE);
    const auto calls = p.sink.offered.size(); p.next(1U);
    CHECK(p.report.reason == dump::Reason::TOTAL);
    CHECK(p.sink.offered.size() == calls);
}

TEST_CASE("B15 D090 invalid callback combinations fail without treating them as acknowledgment") {
    for (unsigned condition = 0U; condition < 5U; ++condition) {
        Protocol p;
        if (condition == 0U) { p.sink.status = dump::WriteStatus::PENDING; p.sink.bad_count = 1U; }
        if (condition == 1U) { p.sink.status = dump::WriteStatus::ERROR; p.sink.bad_count = 1U; }
        if (condition == 2U) p.sink.limit = 0U;
        if (condition == 3U) p.sink.bad_count = 65U;
        if (condition == 4U) p.sink.status = static_cast<dump::WriteStatus>(255U);
        p.step();
        CHECK(p.report.phase == dump::Phase::FAILED);
        CHECK(p.report.reason == dump::Reason::PORT);
        CHECK(p.report.bytes == 0U);
        CHECK(p.sink.cancels == 1U);
    }
}

TEST_CASE("B15 D090 Linux readiness loss cancels and recorder evidence remains inspectable") {
    Protocol p; p.step(); const auto calls = p.sink.offered.size();
    p.context.linux_ready = false; p.next();
    CHECK(p.report.reason == dump::Reason::LINUX_UNAVAILABLE);
    CHECK(p.sink.offered.size() == calls);
    CHECK(p.source.frames().size() == 2U);
    CHECK(p.source.events().size() == 1U);
}

TEST_CASE("B13 D090 service requests while active cannot replay after completion") {
    Protocol p; p.step();
    ++p.context.now_us; ++p.context.decision_us; ++p.result.token;
    p.result.menu.request = countdown::Service::LOG_DUMP; p.step();
    DUMP_REQUIRE(p.finish());
    const auto bytes = p.sink.bytes;
    p.next(); CHECK(p.sink.bytes == bytes);
    ++p.context.now_us; ++p.context.decision_us; ++p.result.token;
    p.result.menu.request = countdown::Service::LOG_DUMP; p.step();
    CHECK(p.report.phase == dump::Phase::ACTIVE);
    CHECK(p.report.session == p.result.token);
}

TEST_CASE("B15 D090 independent CRC uses standard check vector") {
    CHECK(crc("123456789") == 0xCBF43926U);
}

TEST_CASE("B13 D090 unavailable intents do not start and unsafe repeated-now observations cancel") {
    SUBCASE("unavailable intent") {
        Protocol p; p.result.menu.request_unavailable = true; p.step();
        CHECK(p.report.phase == dump::Phase::REFUSED);
        CHECK(p.sink.offered.empty());
    }
    for (unsigned condition = 0U; condition < 3U; ++condition) {
        Protocol p; p.step(); const auto calls = p.sink.offered.size();
        if (condition == 0U) p.result.outputs.ui_state = core::State::STOPPED;
        if (condition == 1U) p.result.fresh = false;
        if (condition == 2U) p.result.contract_faults = fsm::TOKEN_EXHAUSTED;
        p.step();
        CHECK(p.report.phase == dump::Phase::CANCELLED);
        CHECK(p.sink.offered.size() == calls);
    }
}

TEST_CASE("B15 D090 terminal-exhausted interrupted evidence cannot authorize a dump") {
    recorder::AttemptRecorder source;
    begin(source, std::numeric_limits<std::uint64_t>::max());
    fsm::RobotResult terminal;
    terminal.outputs.ui_state = core::State::STOPPED;
    terminal.contract_faults = fsm::TOKEN_EXHAUSTED;
    source.consume(terminal);
    DUMP_REQUIRE(source.summary().terminal_exhausted);
    Sink sink; dump::Transfer transfer(sink.port());
    const auto report = transfer.step({100U, 100U, true, dump::Origin::UNKNOWN}, eligible(10U, true), source);
    CHECK(report.phase == dump::Phase::REFUSED);
    CHECK(report.reason == dump::Reason::NO_EVIDENCE);
    CHECK(sink.offered.empty());
}

TEST_CASE("B15 D090 report counts acknowledge complete rows only and one call writes at most once") {
    Protocol p; p.sink.limit = 1U; p.step();
    CHECK(p.report.frames == 0U);
    CHECK(p.report.events == 0U);
    for (unsigned n = 0U; n < 2000U && p.report.phase == dump::Phase::ACTIVE; ++n) {
        const auto calls = p.sink.offered.size(); p.next();
        CHECK(p.sink.offered.size() <= calls + 1U);
        std::uint32_t frames = 0U, events = 0U;
        std::size_t offset = 0U;
        while (offset < p.sink.bytes.size()) {
            const auto end = p.sink.bytes.find('\n', offset);
            if (end == std::string::npos) break;
            if (p.sink.bytes.compare(offset, 3U, "FR,") == 0) ++frames;
            if (p.sink.bytes.compare(offset, 3U, "ER,") == 0) ++events;
            offset = end + 1U;
        }
        CHECK(p.report.frames == frames);
        CHECK(p.report.events == events);
    }
    CHECK(p.report.phase == dump::Phase::SENT_UNCONFIRMED);
}

TEST_CASE("B15 D090 maximum retained source streams oldest-first frames and insertion-order events") {
    recorder::AttemptRecorder source; begin(source);
    for (std::uint64_t token = 2U; token <= config::LOG_FRAME_CAPACITY + 1U; ++token) {
        auto result = eligible(token);
        result.outputs.ui_state = token >= config::LOG_FRAME_CAPACITY ? core::State::STOPPED : core::State::COUNTDOWN;
        storedFrame(result, token - 1U, 2U, logframe::PackStatus::OK);
        if (token <= config::LOG_EVENT_CAPACITY) {
            result.events.count = 1U;
            result.events.entries[0] = {static_cast<std::uint32_t>(token), core::Event::FAULT, 1U, 0U};
        }
        source.consume(result);
    }
    DUMP_REQUIRE(source.phase() == recorder::AttemptPhase::SEALED);
    DUMP_REQUIRE(source.frames().size() == config::LOG_FRAME_CAPACITY);
    DUMP_REQUIRE(source.events().size() == config::LOG_EVENT_CAPACITY);
    Sink sink; dump::Transfer transfer(sink.port());
    auto report = transfer.step({100U, 100U, true, dump::Origin::SYNTHETIC}, eligible(10000U, true), source);
    for (unsigned n = 1U; n < 100000U && report.phase == dump::Phase::ACTIVE; ++n)
        report = transfer.step({100U + n, 100U + n, true, dump::Origin::SYNTHETIC}, eligible(10000U + n), source);
    CHECK(report.phase == dump::Phase::SENT_UNCONFIRMED);
    CHECK(report.frames == config::LOG_FRAME_CAPACITY);
    CHECK(report.events == config::LOG_EVENT_CAPACITY);
    CHECK(sink.bytes.find("FR,10000,1,5000,") != std::string::npos);
    CHECK(sink.bytes.find("ER,10000,1,4095,") != std::string::npos);
    const auto end = sink.bytes.rfind("END,");
    DUMP_REQUIRE(end != std::string::npos);
    CHECK(report.crc == crc(sink.bytes.substr(0U, end)));
}

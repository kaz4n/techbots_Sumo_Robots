// Tests D101 actual application dump attachment against its frozen contract.
// Uses real Runtime, Robot, MotorGate and retained attempt without private seeding.
// Typed source/transport fixtures run in inert and enabled host-only builds.
#include "doctest.h"
#include "fixtures/app_dump/fixture.h"
#include <limits>

using namespace app_dump_test;
#define AD_REQUIRE(...) do { const bool ok = (__VA_ARGS__); CHECK_MESSAGE(ok, #__VA_ARGS__, \
    " runtimefault=", int(rig.owner.report().fault), " txfault=", int(rig.owner.transaction().report().fault), \
    " robotfault=", rig.robot().contract_faults, " state=", int(rig.robot().outputs.ui_state), \
    " dump=", int(rig.owner.report().dump.phase), "/", int(rig.owner.report().dump.reason)); \
    if (!ok) return; } while (false)

namespace {
void inhibited(const Rig& rig) {
    CHECK_FALSE(rig.fake.enabled);
    for (const auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
}
#ifdef APP_TEST_CONFIGURED_BUTTONS
void sameReport(const dump::Report& a, const dump::Report& b) {
    CHECK(a.phase == b.phase); CHECK(a.reason == b.reason);
    CHECK(a.session == b.session); CHECK(a.epoch == b.epoch);
    CHECK(a.bytes == b.bytes); CHECK(a.frames == b.frames);
    CHECK(a.events == b.events); CHECK(a.crc == b.crc);
}
#endif
}

TEST_CASE("B13 B15 D101 disabled dump is fully passive through setup ticks and abort") {
    Rig rig; CHECK(rig.sink.calls.empty()); AD_REQUIRE(rig.begin(false));
    AD_REQUIRE(rig.run(4U)); rig.owner.abort(); rig.owner.abort();
    CHECK_FALSE(rig.owner.step()); CHECK_FALSE(rig.owner.begin(rig.grants()));
    CHECK(rig.sink.calls.empty()); CHECK(rig.owner.report().dump_setup == dump::NativeStatus::NOT_INITIALIZED);
    CHECK(rig.owner.report().dump.phase == dump::Phase::IDLE); inhibited(rig);
}

TEST_CASE("B13 B15 D101 every missing dump callback is CONTEXT without dump I O or halted control") {
    for (unsigned missing = 1U; missing <= 4U; ++missing) {
        Rig rig(missing); AD_REQUIRE(rig.begin()); AD_REQUIRE(rig.run(3U));
        CHECK(rig.owner.report().dump_setup == dump::NativeStatus::CONTEXT);
        CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
        CHECK(rig.owner.report().epochs == 3U); CHECK(rig.sink.calls.empty());
        CHECK(rig.fake.opponents == 3U); rig.owner.abort(); CHECK(rig.sink.calls.empty());
    }
}

TEST_CASE("B0 B13 D101 setup is once after Gate and existing sources with exact supplied grants") {
    Rig rig; auto grants = rig.grants(); grants.imu_enabled = true;
    grants.imu_power_confirmed = true; grants.mounting = {{1, 2, 3}, true};
    grants.matrix_enabled = true; grants.matrix = {true, true};
    rig.sink.begin_work = 17U;
    AD_REQUIRE(rig.owner.begin(grants)); CHECK(rig.fake.trace[0].kind == runtime_test::Call::ENABLE_SETUP);
    CHECK(rig.sink.begins == 1U); CHECK(rig.sink.readies == 0U);
    const auto& setup = rig.sink.calls.front(); CHECK(setup.kind == Kind::BEGIN);
    CHECK(setup.source_calls == rig.fake.count); CHECK(rig.fake.imu_setups == 1U);
    CHECK(rig.fake.seen(runtime_test::Call::LINE_SETUP) == 1U);
    CHECK(rig.fake.seen(runtime_test::Call::MATRIX_SETUP) == 1U);
    CHECK(setup.end - setup.at == 17U); CHECK(rig.owner.report().next_release_us == setup.end);
    CHECK(rig.sink.received.setup_phase == grants.dump.setup_phase);
    CHECK(rig.sink.received.exclusive_uart == grants.dump.exclusive_uart);
    CHECK(rig.sink.received.ready_pin_owned == grants.dump.ready_pin_owned);
    CHECK(rig.sink.received.framing_clean == grants.dump.framing_clean);
    CHECK_FALSE(rig.owner.begin(grants)); AD_REQUIRE(rig.next()); CHECK(rig.sink.begins == 1U);
    inhibited(rig);
}

TEST_CASE("B13 B15 D101 unsuccessful setup statuses never sample readiness or retry and preserve sensors") {
    const dump::NativeStatus statuses[] = {dump::NativeStatus::CONTEXT, dump::NativeStatus::OWNERSHIP,
        dump::NativeStatus::DEVICE, dump::NativeStatus::READY_LOW, dump::NativeStatus::READY_ERROR,
        dump::NativeStatus::REGISTER, dump::NativeStatus::POISONED, dump::NativeStatus::TIMEOUT,
        dump::NativeStatus::INVALID_ARGUMENT, dump::NativeStatus::NOT_INITIALIZED};
    for (const auto status : statuses) {
        Rig rig; rig.sink.setup = status; AD_REQUIRE(rig.begin()); AD_REQUIRE(rig.run(4U));
        CHECK(rig.owner.report().dump_setup == status); CHECK(rig.sink.begins == 1U);
        CHECK(rig.sink.readies == 0U); CHECK(rig.sink.writes == 0U); CHECK(rig.sink.cancels == 0U);
        CHECK(rig.fake.opponents == 4U); CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
    }
}

TEST_CASE("B13 B15 D101 early step never pumps dump and terminal calls remain passive") {
    Rig rig; AD_REQUIRE(rig.begin()); AD_REQUIRE(rig.next());
    const auto count = rig.sink.calls.size(); const auto sources = rig.fake.count;
    const auto token = rig.robot().token; CHECK_FALSE(rig.owner.step());
    CHECK(rig.sink.calls.size() == count); CHECK(rig.fake.count == sources); CHECK(rig.robot().token == token);
    rig.owner.abort(); const auto terminal = rig.sink.calls.size();
    CHECK_FALSE(rig.owner.step()); rig.owner.abort(); CHECK(rig.sink.calls.size() == terminal);
}

#ifdef APP_TEST_CONFIGURED_BUTTONS
TEST_CASE("B13 B15 D234 Runtime retains configured identity from setup through every wire envelope") {
    for (const auto identity : {std::uint64_t{1U}, std::uint64_t{4294967296ULL},
                               std::numeric_limits<std::uint64_t>::max()}) {
        Rig rig; auto grants = rig.grants();
        grants.dump.receive_stream = dump::ReceiveStream::UNTRUSTED_RECEIVE_STREAM;
        grants.dump.session = identity;
        AD_REQUIRE(rig.owner.begin(grants));
        CHECK(rig.sink.received.session == identity);
        CHECK(rig.sink.received.receive_stream == dump::ReceiveStream::UNTRUSTED_RECEIVE_STREAM);
        grants.dump.session = 2U; // Caller changes cannot mutate the stored grant.
        AD_REQUIRE(rig.seal()); AD_REQUIRE(rig.selectDump()); AD_REQUIRE(rig.requestDump());
        AD_REQUIRE(rig.finish());
        CHECK(rig.owner.report().dump.session == identity);
        CHECK(rig.sink.cancels == 0U);
        const auto& wire = rig.sink.bytes;
        const std::string expected = std::to_string(identity) + ",";
        std::size_t offset = 0U, envelopes = 0U;
        while (offset < wire.size()) {
            const auto end = wire.find('\n', offset);
            REQUIRE(end != std::string::npos);
            const auto value = envelopes == 0U ? offset + 15U : wire.find(',', offset) + 1U;
            CHECK(wire.compare(value, expected.size(), expected) == 0);
            offset = end + 1U; ++envelopes;
        }
        CHECK(envelopes > 3U);
        inhibited(rig);
    }
}

TEST_CASE("B3 B13 B15 D101 real cancelled countdown tail seals then genuine local menu exports exact attempt") {
    Rig rig; AD_REQUIRE(rig.begin()); AD_REQUIRE(rig.seal());
    const auto original = recorder::csv::captureSummary(rig.owner.transaction().recording());
    CHECK_FALSE(original.attempt.go_seen); CHECK_FALSE(original.attempt.final_frame_missing);
    CHECK(original.frame_count > 0U); CHECK(original.event_count > 0U);
    AD_REQUIRE(rig.selectDump()); CHECK(rig.sink.writes == 0U); AD_REQUIRE(rig.requestDump());
    const auto request = rig.robot().token; AD_REQUIRE(rig.finish());
    const auto& report = rig.owner.report().dump;
    CHECK(report.session == request); CHECK(report.epoch == original.attempt.epoch_token);
    CHECK(report.frames == original.frame_count); CHECK(report.events == original.event_count);
    CHECK(report.bytes == rig.sink.bytes.size()); CHECK(rig.sink.cancels == 0U);
    CHECK(rig.sink.bytes.find("SUMOX26_DUMP,1," + std::to_string(request) + "," +
        std::to_string(original.attempt.epoch_token) + ",1,") == 0U);
    const auto after = recorder::csv::captureSummary(rig.owner.transaction().recording());
    CHECK(after.frame_count == original.frame_count); CHECK(after.event_count == original.event_count);
    CHECK(after.attempt.observed_results == original.attempt.observed_results);
    const auto sent = report; const auto writes = rig.sink.writes; AD_REQUIRE(rig.run(4U));
    sameReport(sent, rig.owner.report().dump); CHECK(rig.sink.writes == writes); inhibited(rig);
}

TEST_CASE("B13 B15 D101 readiness and writes carry real current receipt after recorder inside complete epoch") {
    Rig rig; AD_REQUIRE(rig.active()); rig.sink.ready_work = 37U; rig.sink.write_work = 59U;
    rig.fake.motor_work = 2U; rig.fake.settle_work = 3U;
    auto g = rig.owner.transaction().report(); const auto before = rig.sink.calls.size();
    AD_REQUIRE(rig.next()); const auto& tx = rig.owner.transaction().report();
    CHECK(tx.robot.token == g.robot.token + 1U); CHECK(tx.timing_valid); CHECK(tx.finished);
    CHECK(rig.sink.calls.size() == before + 2U);
    for (std::size_t i = before; i < rig.sink.calls.size(); ++i) {
        const auto& call = rig.sink.calls[i];
        CHECK(call.transaction == app::Phase::DECIDED); CHECK(call.token == tx.robot.token);
        CHECK(call.decision == tx.decision_us); CHECK(call.state == core::State::IDLE);
        CHECK(call.consumed); CHECK(call.applied_valid); CHECK_FALSE(call.enabled);
        CHECK(call.left == 0.0F); CHECK(call.right == 0.0F);
        CHECK(call.recording == recorder::AttemptPhase::SEALED);
        CHECK(call.at - tx.started_us < 0x80000000U);
        CHECK(tx.completed_us - call.end < 0x80000000U);
    }
    CHECK(rig.sink.calls[before].kind == Kind::READY); CHECK(rig.sink.calls.back().kind == Kind::WRITE);
    CHECK(tx.execution_us == tx.completed_us - tx.started_us);
    CHECK(tx.completed_us == rig.sink.calls.back().end); CHECK(tx.execution_us >= 96U);
    CHECK(rig.owner.report().maximum_execution_us >= tx.execution_us);
}

TEST_CASE("B13 B15 D101 refusal requires real intent and preserves setup and no evidence reasons") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        Rig rig; if (scenario == 1U) rig.sink.setup = dump::NativeStatus::DEVICE;
        if (scenario == 2U) rig.sink.linux_ready = false;
        AD_REQUIRE(rig.begin()); if (scenario != 0U) AD_REQUIRE(rig.seal());
        else AD_REQUIRE(rig.run(35U));
        AD_REQUIRE(rig.selectDump()); CHECK(rig.owner.report().dump.phase == dump::Phase::IDLE);
        AD_REQUIRE(rig.requestDump()); CHECK(rig.owner.report().dump.phase == dump::Phase::REFUSED);
        CHECK(rig.owner.report().dump.reason == (scenario == 0U ? dump::Reason::NO_EVIDENCE : dump::Reason::LINUX_UNAVAILABLE));
        CHECK(rig.sink.writes == 0U); CHECK(rig.sink.cancels == 0U);
        if (scenario == 1U) CHECK(rig.sink.readies == 0U);
    }
}

TEST_CASE("B13 B15 D101 partial acknowledged writes and pending preserve one bounded offer per epoch") {
    Rig rig; rig.sink.limit = 7U; AD_REQUIRE(rig.active());
    const auto bytes = rig.sink.bytes; const auto report = rig.owner.report().dump;
    rig.sink.status = dump::WriteStatus::PENDING; AD_REQUIRE(rig.next());
    const auto pending = rig.sink.offers.back(); AD_REQUIRE(rig.next());
    CHECK(rig.sink.offers.back() == pending); CHECK(rig.sink.bytes == bytes);
    CHECK(rig.owner.report().dump.bytes == report.bytes);
    rig.sink.status = dump::WriteStatus::PROGRESS; AD_REQUIRE(rig.finish());
    for (const auto& offer : rig.sink.offers) { CHECK_FALSE(offer.empty()); CHECK(offer.size() <= 64U); }
    std::uint64_t previous = 0U;
    for (const auto& call : rig.sink.calls) if (call.kind == Kind::WRITE) {
        CHECK(call.token > previous); previous = call.token;
    }
}

TEST_CASE("B13 B15 D101 every malformed write result fails PORT and cancels once") {
    for (unsigned scenario = 0U; scenario < 5U; ++scenario) {
        Rig rig; AD_REQUIRE(rig.active()); rig.sink.override_count = true;
        rig.sink.forced_count = scenario == 0U ? 0U : (scenario == 1U ? 65U : 1U);
        rig.sink.status = scenario < 2U ? dump::WriteStatus::PROGRESS :
            (scenario == 2U ? dump::WriteStatus::PENDING : dump::WriteStatus::ERROR);
        if (scenario == 4U) rig.sink.forced_count = 0U;
        AD_REQUIRE(rig.next()); CHECK(rig.owner.report().dump.phase == dump::Phase::FAILED);
        CHECK(rig.owner.report().dump.reason == dump::Reason::PORT); CHECK(rig.sink.cancels == 1U);
        const auto writes = rig.sink.writes; AD_REQUIRE(rig.run(3U)); rig.owner.abort();
        CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
    }
}

TEST_CASE("B13 B15 D101 readiness loss immediately cancels without an additional byte") {
    Rig rig; AD_REQUIRE(rig.active()); const auto writes = rig.sink.writes;
    rig.sink.linux_ready = false; rig.sink.cancel_work = 43U; AD_REQUIRE(rig.next());
    CHECK(rig.owner.report().dump.phase == dump::Phase::CANCELLED);
    CHECK(rig.owner.report().dump.reason == dump::Reason::LINUX_UNAVAILABLE);
    CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
    CHECK(rig.owner.transaction().report().completed_us == rig.sink.calls.back().end);
    AD_REQUIRE(rig.run(3U)); CHECK(rig.sink.cancels == 1U); CHECK(rig.sink.begins == 1U);
}

TEST_CASE("B13 B15 D101 actual failed inhibition cancels before readiness or write without fake decision") {
    Rig rig; AD_REQUIRE(rig.active()); const auto readies = rig.sink.readies, writes = rig.sink.writes;
    const auto token = rig.robot().token; rig.fake.reject_enable = true; AD_REQUIRE(rig.next());
    const auto& tx = rig.owner.transaction().report(); CHECK(tx.robot.token == token + 1U);
    CHECK(tx.applied.consumed); CHECK_FALSE(tx.applied.feedback.applied_valid);
    CHECK(rig.owner.report().dump.phase == dump::Phase::CANCELLED);
    CHECK(rig.owner.report().dump.reason == dump::Reason::CONTEXT);
    CHECK(rig.sink.readies == readies); CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
    CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
}

TEST_CASE("B13 B15 D101 inactive failed receipt preserves passive dump report without readiness") {
    Rig rig; AD_REQUIRE(rig.begin()); AD_REQUIRE(rig.seal()); AD_REQUIRE(rig.selectDump());
    const auto before = rig.owner.report().dump; const auto readies = rig.sink.readies;
    rig.fake.reject_enable = true; AD_REQUIRE(rig.next());
    CHECK_FALSE(rig.owner.transaction().report().applied.feedback.applied_valid);
    sameReport(before, rig.owner.report().dump); CHECK(rig.sink.readies == readies);
    CHECK(rig.sink.writes == 0U); CHECK(rig.sink.cancels == 0U);
}

TEST_CASE("B13 B15 D101 actual pending epochs reach stall boundary without hidden between tick pumping") {
    Rig rig; rig.sink.status = dump::WriteStatus::PENDING; AD_REQUIRE(rig.active());
    const auto start = rig.owner.transaction().report().decision_us;
    for (unsigned i = 0U; i <= config::DUMP_STALL_MS &&
         rig.owner.report().dump.phase == dump::Phase::ACTIVE; ++i) {
        const auto writes = rig.sink.writes; AD_REQUIRE(rig.next());
        const auto age = rig.owner.transaction().report().decision_us - start;
        if (age < config::DUMP_STALL_MS * 1000U) CHECK(rig.sink.writes == writes + 1U);
        else { CHECK(rig.sink.writes == writes); CHECK(age == config::DUMP_STALL_MS * 1000U); }
    }
    CHECK(rig.owner.report().dump.phase == dump::Phase::FAILED);
    CHECK(rig.owner.report().dump.reason == dump::Reason::STALL);
    CHECK(rig.sink.cancels == 1U); CHECK(rig.sink.bytes.empty());
}

TEST_CASE("B13 B15 D101 after ready clock is used for freshness instead of fabricated decision time") {
    for (const auto age : {999U, 1000U, 1001U}) {
        Rig rig; AD_REQUIRE(rig.active()); const auto writes = rig.sink.writes;
        rig.sink.ready_work = age; AD_REQUIRE(rig.next());
        if (age < config::TICK_US) CHECK(rig.sink.writes == writes + 1U);
        else { CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
            CHECK(rig.owner.report().dump.reason == dump::Reason::STALE_CONTEXT); }
        CHECK(rig.owner.transaction().report().execution_us >= age);
    }
}

TEST_CASE("B14 B15 D101 regressing clock after readiness or writing inhibits aborts and never invents C") {
    for (unsigned callback = 0U; callback < 2U; ++callback) {
        Rig rig; AD_REQUIRE(rig.active()); const auto writes = rig.sink.writes;
        rig.sink.reverse_ready = callback == 0U; rig.sink.reverse_write = callback == 1U;
        CHECK_FALSE(rig.next()); CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
        CHECK(rig.owner.report().fault == app::RuntimeFault::CLOCK);
        CHECK_FALSE(rig.owner.transaction().report().timing_valid);
        CHECK_FALSE(rig.owner.transaction().report().finished);
        CHECK(rig.owner.transaction().report().halt.attempted);
        CHECK(rig.owner.report().dump.phase == dump::Phase::CANCELLED);
        CHECK(rig.owner.report().dump.reason == dump::Reason::CONTEXT);
        CHECK(rig.sink.cancels == 1U); CHECK(rig.sink.calls.back().kind == Kind::CANCEL);
        CHECK(rig.sink.calls.back().halted); CHECK(rig.sink.writes == writes + callback);
        const auto count = rig.fake.count; const auto dump_calls = rig.sink.calls.size();
        rig.owner.abort(); CHECK_FALSE(rig.owner.step()); CHECK(rig.fake.count == count);
        CHECK(rig.sink.calls.size() == dump_calls); inhibited(rig);
    }
}

TEST_CASE("B13 B15 D101 owner abort cancels after halt before active source cleanup only once") {
    Rig rig; AD_REQUIRE(rig.active()); rig.fake.line_lower = 1800U;
    for (unsigned i = 0U; i < 4U && rig.fake.line.phase != line_qtr::Phase::DISCHARGING; ++i)
        AD_REQUIRE(rig.next());
    AD_REQUIRE(rig.fake.line.phase == line_qtr::Phase::DISCHARGING);
    const auto before = rig.fake.count; rig.owner.abort();
    CHECK(rig.sink.cancels == 1U); CHECK(rig.sink.calls.back().halted);
    CHECK(rig.sink.calls.back().source_calls > before);
    CHECK(rig.fake.line_cancels == 1U);
    CHECK(rig.sink.calls.back().source_calls < rig.fake.count);
    const auto count = rig.fake.count; rig.owner.abort(); CHECK_FALSE(rig.owner.step());
    CHECK(rig.fake.count == count); CHECK(rig.sink.cancels == 1U); inhibited(rig);
}

TEST_CASE("B3 B13 B15 D101 current START selection loss and STOP preempt active transfer") {
    for (unsigned scenario = 0U; scenario < 2U; ++scenario) {
        Rig rig; rig.sink.status = dump::WriteStatus::PENDING; AD_REQUIRE(rig.active());
        if (scenario == 0U) {
            AD_REQUIRE(rig.run(30U)); AD_REQUIRE(rig.run(1030U, 2000U));
            CHECK_FALSE(rig.robot().menu.selection.service_menu);
            CHECK(rig.owner.report().dump.phase == dump::Phase::CANCELLED);
            const auto readies = rig.sink.readies; AD_REQUIRE(rig.run(30U));
            AD_REQUIRE(rig.run(30U, 1000U)); AD_REQUIRE(rig.run(30U));
            CHECK(rig.robot().outputs.ui_state == core::State::COUNTDOWN);
            CHECK(rig.sink.readies >= readies); const auto at_countdown = rig.sink.readies;
            AD_REQUIRE(rig.run(3U)); CHECK(rig.sink.readies == at_countdown);
        } else {
            rig.fake.button_raw = 3000U;
            for (unsigned i = 0U; i < 1100U && rig.robot().outputs.ui_state != core::State::STOPPED; ++i)
                AD_REQUIRE(rig.next());
            CHECK(rig.robot().outputs.ui_state == core::State::STOPPED);
            CHECK(rig.owner.report().dump.phase == dump::Phase::CANCELLED);
            const auto readies = rig.sink.readies, writes = rig.sink.writes;
            AD_REQUIRE(rig.next()); CHECK(rig.owner.report().phase == app::RuntimePhase::STOPPED);
            CHECK_FALSE(rig.owner.step()); CHECK(rig.sink.readies == readies); CHECK(rig.sink.writes == writes);
        }
        CHECK(rig.sink.cancels == 1U); CHECK(rig.sink.begins == 1U); inhibited(rig);
    }
}

TEST_CASE("B14 B15 D101 valid micros wrap does not cancel a real attempt export") {
    Rig rig; rig.fake.now = std::numeric_limits<std::uint32_t>::max() - 1485000U;
    AD_REQUIRE(rig.active()); AD_REQUIRE(rig.finish());
    CHECK(rig.fake.now < 1600000U); CHECK(rig.sink.cancels == 0U);
    CHECK(rig.owner.report().fault == app::RuntimeFault::NONE);
}

TEST_CASE("B15 D101 Transfer abort is passive when idle and preserves finished report") {
    Rig rig; AD_REQUIRE(rig.active()); Sink second(rig.fake); second.runtime = &rig.owner;
    dump::Transfer transfer(second.port().output); const auto idle = transfer.report();
    transfer.abort(); transfer.abort(); sameReport(idle, transfer.report()); CHECK(second.cancels == 0U);
    AD_REQUIRE(rig.finish()); const auto sent = rig.owner.report().dump;
    rig.owner.abort(); sameReport(sent, rig.owner.report().dump); CHECK(rig.sink.cancels == 0U);
}

TEST_CASE("B15 D101 Transfer abort preserves token decision and clock history") {
    Rig rig; AD_REQUIRE(rig.active()); Sink second(rig.fake); second.runtime = &rig.owner;
    dump::Transfer transfer(second.port().output); const auto actual = rig.robot();
    const auto decision = rig.owner.transaction().report().decision_us;
    const dump::Context context{rig.fake.now, decision, true, dump::Origin::SYNTHETIC};
    CHECK(transfer.step(context, actual, rig.owner.transaction().recording()).phase == dump::Phase::ACTIVE);
    transfer.abort(); const auto aborted = transfer.report(); CHECK(aborted.reason == dump::Reason::CONTEXT);
    CHECK(second.cancels == 1U); transfer.abort(); sameReport(aborted, transfer.report());
    transfer.step(context, actual, rig.owner.transaction().recording()); CHECK(second.cancels == 1U);
    CHECK(transfer.report().phase != dump::Phase::ACTIVE); CHECK(second.writes == 1U);
    auto reversed = context; reversed.now_us -= 1U;
    transfer.step(reversed, actual, rig.owner.transaction().recording());
    CHECK(transfer.report().phase != dump::Phase::ACTIVE); CHECK(second.writes == 1U);
    CHECK(second.cancels == 1U);
}
#endif

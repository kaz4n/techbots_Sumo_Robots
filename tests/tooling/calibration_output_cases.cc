// Tests D105 using eight genuine Runtime calibration requests and real receipts.
// Derives expectations from frozen public contracts without reading production cpp.
// Isolated normal, MATCH and sanitizer builds use synthetic physical callbacks only.
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
#include "fixtures/app_dump/fixture.h"
#include <cstdlib>
#include <fstream>
#include <limits>

namespace calibration_output_test {
namespace dump = recorder::dump;
using Phase = app::CalibrationOutputPhase;
using Reason = app::CalibrationOutputReason;
using Kind = app_dump_test::Kind;
constexpr std::uint16_t NONE = 50U, START = 1000U, MODE = 2000U, BOTH = 3000U;
constexpr const char* EXPECTED = "QTR_WHITE_US[4] = {350U, 350U, 350U, 350U}; // us\n";

struct Sink : app_dump_test::Sink {
    bool poisoned = false, ready_work_once = false;
    explicit Sink(app_dump_test::Source& source) : app_dump_test::Sink(source) {}
    static bool ready(void* context) {
        auto& sink = *static_cast<Sink*>(context);
        const bool observed = app_dump_test::Sink::ready(context);
        if (sink.ready_work_once) { sink.ready_work = 0U; sink.ready_work_once = false; }
        return observed && !sink.poisoned;
    }
    static void cancel(void* context) {
        auto& sink = *static_cast<Sink*>(context);
        app_dump_test::Sink::cancel(context); sink.poisoned = true;
    }
    app::DumpPort port() { return {this, begin, ready, {this, write, cancel}}; }
};
struct Rig {
    app_dump_test::Source fake;
    Sink sink{fake};
    app::Runtime owner;
    explicit Rig(unsigned missing = 0U) : owner(fake.motorPort(), fake.adcPort(),
        fake.sourcePort(), selectedPort(missing)) { sink.runtime = &owner; }
    app::DumpPort selectedPort(unsigned missing) {
        auto port = sink.port();
        if (missing == 1U) port.begin = nullptr;
        if (missing == 2U) port.ready = nullptr;
        if (missing == 3U) port.output.write = nullptr;
        if (missing == 4U) port.output.cancel = nullptr;
        return port;
    }
    bool begin(bool dump_enabled = true, bool output_enabled = true, bool control = false,
               bool service_reset = false) {
        auto grants = runtime_test::grants(control, false);
        grants.dump_enabled = dump_enabled; grants.calibration_output_enabled = output_enabled;
        grants.dump = {true, true, false, true}; grants.dump_origin = dump::Origin::SYNTHETIC;
        grants.local_service_reset = service_reset;
        return owner.begin(grants);
    }
    bool next() { fake.now = owner.report().next_release_us; return owner.step(); }
    bool run(unsigned count, std::uint16_t raw = NONE) {
        fake.button_raw = raw;
        for (unsigned i = 0U; i < count; ++i) if (!next()) return false;
        return true;
    }
    const fsm::RobotResult& robot() const { return owner.transaction().report().robot; }
    bool modeShort() { return run(30U, MODE) && run(30U); }
    bool modeLong() { return run(1030U, MODE) && run(30U); }
    bool selectQtr() {
        return run(40U) && modeLong() && modeShort() &&
            robot().menu.selection.service_menu &&
            robot().menu.selection.service == countdown::Service::QTR_CAL;
    }
    bool request(countdown::Service service = countdown::Service::QTR_CAL) {
        if (!run(30U, START)) return false;
        fake.button_raw = NONE;
        for (unsigned i = 0U; i < 35U; ++i) {
            if (!next()) return false;
            if (robot().menu.request == service) return true;
        }
        return false;
    }
    bool calibrate() {
        for (unsigned stage = 0U; stage < 8U; ++stage) {
            fake.line_lower = (stage & 1U) == 0U ? 197U : 500U;
            if (!request()) return false;
            for (unsigned i = 0U; i < 100U &&
                 owner.report().calibration.phase == qtr_cal::Phase::COLLECTING; ++i)
                if (!next()) return false;
            if (owner.report().calibration.reason != qtr_cal::Reason::NONE ||
                owner.report().calibration.phase != (stage == 7U ?
                    qtr_cal::Phase::SUCCESS : qtr_cal::Phase::WAITING)) return false;
        }
        return owner.report().calibration.committed;
    }
    bool prepared() { return begin() && selectQtr(); }
    bool active() {
        sink.status = dump::WriteStatus::PENDING;
        return prepared() && calibrate() && owner.calibrationOutput().phase == Phase::ACTIVE;
    }
    bool finish() {
        for (unsigned i = 0U; i < 100U && owner.calibrationOutput().phase == Phase::ACTIVE; ++i)
            if (!next()) return false;
        return owner.calibrationOutput().phase == Phase::SENT_UNCONFIRMED;
    }
    bool seal() {
        return run(35U) && run(30U, START) && run(30U) &&
            robot().outputs.ui_state == core::State::COUNTDOWN && modeShort() &&
            owner.transaction().recording().phase() == recorder::AttemptPhase::SEALED;
    }
    bool selectDumpFromQtr() { return modeShort() && modeShort() &&
        robot().menu.selection.service == countdown::Service::LOG_DUMP; }
    bool stop() {
        fake.button_raw = BOTH;
        for (unsigned i = 0U; i < 1100U; ++i) {
            if (!next()) return false;
            if (robot().outputs.ui_state == core::State::STOPPED) return next();
        }
        return false;
    }
};

void same(const app::CalibrationOutputReport& lhs, const app::CalibrationOutputReport& rhs) {
    CHECK(lhs.phase == rhs.phase); CHECK(lhs.reason == rhs.reason);
    CHECK(lhs.token == rhs.token); CHECK(lhs.version == rhs.version); CHECK(lhs.bytes == rhs.bytes);
}
void inhibited(const Rig& rig) {
    CHECK_FALSE(rig.fake.enabled); for (const auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
    CHECK_FALSE(rig.robot().outputs.motors_enabled);
    CHECK(rig.robot().outputs.duty_l == 0.0F); CHECK(rig.robot().outputs.duty_r == 0.0F);
}
void writesBounded(const Rig& rig) {
    std::uint64_t previous = 0U;
    for (const auto& call : rig.sink.calls) if (call.kind == Kind::WRITE) {
        CHECK(call.token > previous); previous = call.token;
        CHECK(call.transaction == app::Phase::DECIDED); CHECK(call.consumed);
        CHECK(call.applied_valid); CHECK_FALSE(call.enabled);
        CHECK(call.left == 0.0F); CHECK(call.right == 0.0F);
    }
    for (const auto& offer : rig.sink.offers) {
        CHECK_FALSE(offer.empty()); CHECK(offer.size() <= config::DUMP_PAYLOAD_BYTES);
    }
}
} // namespace calibration_output_test
using namespace calibration_output_test;
#define CO_REQUIRE(...) do { const bool passed = (__VA_ARGS__); \
    CHECK_MESSAGE(passed, #__VA_ARGS__, " runtime=", int(rig.owner.report().phase), \
        "/", int(rig.owner.report().fault), " cal=", int(rig.owner.report().calibration.phase), \
        "/", int(rig.owner.report().calibration.reason), " out=", int(rig.owner.calibrationOutput().phase), \
        "/", int(rig.owner.calibrationOutput().reason)); if (!passed) return; } while (false)

TEST_CASE("B13 D105 public defaults and structural formatter capacity are inert") {
    app::SetupGrants grants; app::CalibrationOutputReport report;
    CHECK_FALSE(grants.calibration_output_enabled); CHECK(report.phase == Phase::INACTIVE);
    CHECK(report.reason == Reason::NONE); CHECK(report.token == 0U);
    CHECK(report.version == 0U); CHECK(report.bytes == 0U);
    CHECK(qtr_cal::CONFIG_SNIPPET_CAPACITY == 80U);
    Rig rig; same(report, rig.owner.calibrationOutput()); CHECK(rig.sink.calls.empty());
}

TEST_CASE("B13 D105 all grant and MATCH combinations use actual eight request calibration") {
    for (bool dumping : {false, true}) for (bool exporting : {false, true}) {
        Rig rig; CO_REQUIRE(rig.begin(dumping, exporting)); CO_REQUIRE(rig.selectQtr());
        CO_REQUIRE(rig.calibrate()); const auto& result = rig.owner.calibrationOutput();
        CHECK(rig.sink.begins == (dumping ? 1U : 0U));
        if (!dumping) CHECK(rig.sink.calls.empty());
        if (!dumping || !exporting || MATCH != 0) {
            same(result, app::CalibrationOutputReport{}); CHECK(rig.sink.writes == 0U);
        } else {
            CHECK(result.phase == Phase::SENT_UNCONFIRMED); CHECK(result.reason == Reason::NONE);
            CHECK(result.version == 1U); CHECK(result.token == rig.robot().token);
            CHECK(rig.sink.bytes == EXPECTED);
        }
        CHECK(rig.owner.report().calibration.thresholds.version == 1U); inhibited(rig);
    }
}

TEST_CASE("B13 D105 real recorder export remains available with calibration grant in MATCH") {
    Rig rig; CO_REQUIRE(rig.begin(true, true, true)); CO_REQUIRE(rig.seal());
    CO_REQUIRE(rig.selectQtr()); CO_REQUIRE(rig.selectDumpFromQtr());
    CO_REQUIRE(rig.request(countdown::Service::LOG_DUMP));
    for (unsigned i = 0U; i < 2000U && rig.owner.report().dump.phase == dump::Phase::ACTIVE; ++i)
        CO_REQUIRE(rig.next());
    CHECK(rig.owner.report().dump.phase == dump::Phase::SENT_UNCONFIRMED);
    CHECK(rig.sink.bytes.find("SUMOX26_DUMP,1,") == 0U);
    same(rig.owner.calibrationOutput(), app::CalibrationOutputReport{}); writesBounded(rig);
}

#if MATCH == 0
TEST_CASE("B13 D105 actual committed bank exact snippet and first terminal report persist") {
    Rig rig; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
    const auto report = rig.owner.calibrationOutput();
    CHECK(report.phase == Phase::SENT_UNCONFIRMED); CHECK(report.reason == Reason::NONE);
    CHECK(report.token == rig.robot().token); CHECK(report.version == 1U);
    CHECK(report.bytes == rig.sink.bytes.size()); CHECK(rig.sink.bytes == EXPECTED);
    CHECK(rig.sink.cancels == 0U); CHECK(rig.owner.transaction().report().finished);
    CHECK(rig.owner.transaction().report().timing_valid);
    char line[qtr_cal::CONFIG_SNIPPET_CAPACITY]; std::size_t written = 0U;
    CHECK(qtr_cal::formatConfig(rig.owner.report().calibration, line, sizeof(line), written) == qtr_cal::FormatStatus::OK);
    CHECK(std::string(line, written) == rig.sink.bytes);
    if (const auto* path = std::getenv("SUMO_QTR_SNIPPET_OUTPUT")) {
        std::ofstream stream(path, std::ios::binary); stream << rig.sink.bytes; CHECK(stream.good());
    }
    const auto writes = rig.sink.writes; CO_REQUIRE(rig.run(10U));
    CHECK_FALSE(rig.owner.report().calibration.committed); same(report, rig.owner.calibrationOutput());
    CHECK(rig.sink.writes == writes); rig.owner.abort(); same(report, rig.owner.calibrationOutput());
    CHECK(rig.sink.cancels == 0U); writesBounded(rig); inhibited(rig);
}

TEST_CASE("B13 D105 pending partial offsets repeated bytes and one write per actual epoch") {
    Rig rig; rig.sink.limit = 7U; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
    CO_REQUIRE(rig.owner.calibrationOutput().phase == Phase::ACTIVE);
    CHECK(rig.owner.calibrationOutput().bytes == 7U);
    rig.sink.status = dump::WriteStatus::PENDING; CO_REQUIRE(rig.next());
    const auto offer = rig.sink.offers.back(); const auto sent = rig.sink.bytes;
    CO_REQUIRE(rig.next()); CHECK(rig.sink.offers.back() == offer);
    CHECK(rig.sink.bytes == sent); CHECK(rig.owner.calibrationOutput().bytes == 7U);
    const auto calls = rig.sink.calls.size(); const auto report = rig.owner.calibrationOutput();
    CHECK_FALSE(rig.owner.step()); CHECK(rig.sink.calls.size() == calls); same(report, rig.owner.calibrationOutput());
    rig.sink.status = dump::WriteStatus::PROGRESS; CO_REQUIRE(rig.finish());
    CHECK(rig.sink.bytes == EXPECTED); CHECK(rig.sink.cancels == 0U); writesBounded(rig);
}

TEST_CASE("B13 D105 pending absent raw lines are valid while captured bank is delivered") {
    Rig rig; CO_REQUIRE(rig.active()); rig.fake.qtr_no_start = true;
    CO_REQUIRE(rig.run(12U)); CHECK(rig.owner.decisionInput().line.presence == core::LinePresence::ABSENT);
    CHECK(rig.owner.decisionInput().line.use == core::LineUse::CALIBRATION);
    CHECK(rig.owner.calibrationOutput().phase == Phase::ACTIVE); CHECK(rig.sink.cancels == 0U);
    rig.sink.status = dump::WriteStatus::PROGRESS; CO_REQUIRE(rig.finish()); CHECK(rig.sink.bytes == EXPECTED);
}

TEST_CASE("B13 D105 readiness refusal consumes version without cancel retry or delayed intent") {
    Rig rig; rig.sink.linux_ready = false; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
    const auto refused = rig.owner.calibrationOutput(); CHECK(refused.phase == Phase::REFUSED);
    CHECK(refused.reason == Reason::LINUX_UNAVAILABLE); CHECK(refused.version == 1U);
    CHECK(refused.bytes == 0U); CHECK(rig.sink.writes == 0U); CHECK(rig.sink.cancels == 0U);
    rig.sink.linux_ready = true; CO_REQUIRE(rig.run(10U)); same(refused, rig.owner.calibrationOutput());
    CO_REQUIRE(rig.modeShort()); CO_REQUIRE(rig.modeShort()); CO_REQUIRE(rig.modeShort()); CO_REQUIRE(rig.modeShort());
    CHECK(rig.robot().menu.selection.service == countdown::Service::QTR_CAL);
    same(refused, rig.owner.calibrationOutput()); CHECK(rig.sink.writes == 0U);
    CO_REQUIRE(rig.calibrate()); CHECK(rig.owner.calibrationOutput().version == 2U);
    CHECK(rig.owner.calibrationOutput().phase == Phase::SENT_UNCONFIRMED);
    CHECK(rig.owner.calibrationOutput().token > refused.token); CHECK(rig.sink.bytes == EXPECTED);
}

TEST_CASE("B13 D105 later genuinely committed bank succeeds without reconstructing UART owner") {
    Rig rig; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
    const auto first = rig.owner.calibrationOutput(); CO_REQUIRE(rig.calibrate());
    CHECK(rig.owner.calibrationOutput().version == 2U); CHECK(rig.owner.calibrationOutput().token > first.token);
    CHECK(rig.sink.bytes == std::string(EXPECTED) + EXPECTED);
    CHECK(rig.sink.begins == 1U); CHECK(rig.sink.cancels == 0U); writesBounded(rig);
}

TEST_CASE("B13 D105 missing callbacks and failed setup refuse before readiness and do not poison") {
    for (unsigned failure = 1U; failure <= 5U; ++failure) {
        Rig rig(failure < 5U ? failure : 0U);
        if (failure == 5U) rig.sink.setup = dump::NativeStatus::DEVICE;
        CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
        CHECK(rig.owner.calibrationOutput().phase == Phase::REFUSED);
        CHECK(rig.owner.calibrationOutput().reason == Reason::PORT);
        CHECK(rig.owner.calibrationOutput().version == 1U);
        CHECK(rig.sink.readies == 0U); CHECK(rig.sink.writes == 0U); CHECK(rig.sink.cancels == 0U);
    }
}

TEST_CASE("B13 D105 malformed write results fail once and retain acknowledged prefix") {
    for (unsigned scenario = 0U; scenario < 6U; ++scenario) {
        Rig rig; rig.sink.limit = 3U; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
        const auto before = rig.owner.calibrationOutput(); CO_REQUIRE(before.phase == Phase::ACTIVE);
        rig.sink.override_count = true;
        rig.sink.status = scenario < 2U ? dump::WriteStatus::PROGRESS :
            (scenario == 2U ? dump::WriteStatus::PENDING : dump::WriteStatus::ERROR);
        rig.sink.forced_count = scenario == 0U || scenario == 4U ? 0U :
            (scenario == 1U ? 65U : 1U);
        if (scenario == 5U) rig.sink.status = static_cast<dump::WriteStatus>(255U);
        CO_REQUIRE(rig.next()); const auto result = rig.owner.calibrationOutput();
        CHECK(result.phase == Phase::FAILED); CHECK(result.reason == Reason::PORT);
        CHECK(result.bytes == before.bytes); CHECK(result.token == before.token); CHECK(result.version == before.version);
        CHECK(rig.sink.cancels == 1U); CHECK(rig.sink.poisoned);
        const auto writes = rig.sink.writes; CO_REQUIRE(rig.run(4U)); rig.owner.abort();
        same(result, rig.owner.calibrationOutput()); CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
    }
}

TEST_CASE("B13 D105 readiness loss cancels once and preserves its measured cleanup time") {
    Rig rig; CO_REQUIRE(rig.active()); const auto writes = rig.sink.writes;
    rig.sink.linux_ready = false; rig.sink.cancel_work = 43U; CO_REQUIRE(rig.next());
    CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::LINUX_UNAVAILABLE);
    CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
    CHECK(rig.sink.calls.back().kind == Kind::CANCEL);
    CHECK(rig.owner.transaction().report().completed_us == rig.sink.calls.back().end);
    const auto report = rig.owner.calibrationOutput(); rig.sink.linux_ready = true;
    CO_REQUIRE(rig.run(5U)); same(report, rig.owner.calibrationOutput()); CHECK(rig.sink.cancels == 1U);
}

TEST_CASE("B13 D105 bad real receipt cancels before every additional readiness or byte") {
    Rig rig; CO_REQUIRE(rig.active()); const auto readies = rig.sink.readies, writes = rig.sink.writes;
    rig.fake.reject_enable = true; CO_REQUIRE(rig.next());
    CHECK_FALSE(rig.owner.transaction().report().applied.feedback.applied_valid);
    CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::RECEIPT);
    CHECK(rig.sink.readies == readies); CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
}

TEST_CASE("B13 D105 new capture cancels old export before its phase changes can leak bytes") {
    Rig rig; CO_REQUIRE(rig.active()); const auto old = rig.owner.calibrationOutput();
    CO_REQUIRE(rig.request()); CHECK(rig.owner.report().calibration.phase == qtr_cal::Phase::COLLECTING);
    CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::BANK_CHANGED);
    CHECK(rig.owner.calibrationOutput().token == old.token); CHECK(rig.sink.cancels == 1U);
    CHECK(rig.sink.calls.back().kind == Kind::READY); // Recorder observes fresh poisoned readiness after cancellation.
    const auto last_cancel = std::find_if(rig.sink.calls.rbegin(), rig.sink.calls.rend(),
        [](const auto& call) { return call.kind == Kind::CANCEL; });
    CO_REQUIRE(last_cancel != rig.sink.calls.rend()); CHECK(last_cancel->token == rig.robot().token);
}

TEST_CASE("B13 D105 all transport work carries real post-Gate authority inside completed S to C") {
    Rig rig; CO_REQUIRE(rig.active()); rig.sink.ready_work = 7U; rig.sink.write_work = 19U;
    const auto before = rig.sink.calls.size(); CO_REQUIRE(rig.next());
    const auto& tx = rig.owner.transaction().report(); CHECK(tx.finished); CHECK(tx.timing_valid);
    for (std::size_t i = before; i < rig.sink.calls.size(); ++i) {
        const auto& call = rig.sink.calls[i]; CHECK(call.transaction == app::Phase::DECIDED);
        CHECK(call.token == tx.robot.token); CHECK(call.decision == tx.decision_us);
        CHECK(call.consumed); CHECK(call.applied_valid); CHECK(call.state == core::State::IDLE);
        CHECK(call.at - tx.started_us <= tx.execution_us);
        CHECK(call.end - tx.started_us <= tx.execution_us);
    }
    CHECK(tx.completed_us == rig.sink.calls.back().end); CHECK(tx.execution_us >= 26U);
    CHECK(rig.owner.report().maximum_execution_us >= tx.execution_us); writesBounded(rig);
}

TEST_CASE("B14 D105 global clock failure after ready or write retains real TIME_ORDER and no fabricated C") {
    for (unsigned scenario = 0U; scenario < 2U; ++scenario) {
        Rig rig; CO_REQUIRE(rig.active()); rig.sink.reverse_ready = scenario == 0U;
        rig.sink.reverse_write = scenario == 1U; CHECK_FALSE(rig.next());
        CHECK(rig.owner.report().fault == app::RuntimeFault::CLOCK);
        CHECK(rig.owner.calibrationOutput().phase == Phase::FAILED);
        CHECK(rig.owner.calibrationOutput().reason == Reason::TIME_ORDER);
        CHECK_FALSE(rig.owner.transaction().report().finished);
        CHECK_FALSE(rig.owner.transaction().report().timing_valid);
        CHECK(rig.sink.cancels == 1U); const auto report = rig.owner.calibrationOutput();
        const auto calls = rig.sink.calls.size(); rig.owner.abort(); CHECK_FALSE(rig.owner.step());
        CHECK(rig.sink.calls.size() == calls); same(report, rig.owner.calibrationOutput());
    }
}

TEST_CASE("B13 D105 forward context expiry uses actual after-readiness clock at exact tick boundary") {
    for (const auto age : {999U, 1000U, 1001U}) {
        Rig rig; CO_REQUIRE(rig.active()); const auto writes = rig.sink.writes;
        rig.sink.ready_work = age; rig.sink.ready_work_once = true; CO_REQUIRE(rig.next());
        if (age < config::TICK_US) {
            CHECK(rig.owner.calibrationOutput().phase == Phase::ACTIVE);
            CHECK(rig.sink.writes == writes + 1U); CHECK(rig.sink.cancels == 0U);
        } else {
            CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
            CHECK(rig.owner.calibrationOutput().reason == Reason::CONTEXT);
            CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U);
        }
    }
}

TEST_CASE("B13 D105 actual invalid sources preempt bytes with receipt then context then source precedence") {
    for (unsigned source = 0U; source < 3U; ++source) {
        Rig rig; CO_REQUIRE(rig.active());
        if (source == 0U) rig.fake.buttons_failure = true;
        if (source == 1U) rig.fake.opponent_error = 1U;
        if (source == 2U) rig.fake.qtr_fault = true;
        for (unsigned i = 0U; i < 5U && rig.owner.calibrationOutput().phase == Phase::ACTIVE; ++i) {
            const auto before_writes = rig.sink.writes; CO_REQUIRE(rig.next());
            const auto& input = rig.owner.decisionInput();
            const auto& observed = rig.owner.transaction().report();
            const bool valid_source = input.buttons.contract_valid &&
                input.buttons.presence == core::ButtonPresence::VALID && input.opponent_fresh &&
                input.line.contract_valid && input.line.presence != core::LinePresence::INVALID;
            const bool valid_context = observed.robot.outputs.ui_state == core::State::IDLE &&
                observed.robot.contract_faults == 0U && observed.robot.escape_fault == edge::EscapeFault::NONE;
            const bool valid_receipt = observed.applied.consumed && observed.applied.feedback.applied_valid &&
                observed.applied.feedback.token == observed.robot.token && observed.applied.fault == motors::Fault::NONE;
            if (!valid_source || !valid_context || !valid_receipt) {
                CHECK(rig.sink.writes == before_writes);
                CHECK(rig.owner.calibrationOutput().phase != Phase::ACTIVE);
            } else CHECK(rig.sink.writes <= before_writes + 1U);
        }
        const auto& tx = rig.owner.transaction().report();
        const bool invalid_receipt = !tx.applied.consumed || !tx.applied.feedback.applied_valid ||
            tx.applied.feedback.token != tx.robot.token || tx.applied.fault != motors::Fault::NONE;
        const bool invalid_context = tx.robot.outputs.ui_state != core::State::IDLE ||
            tx.robot.contract_faults != 0U || tx.robot.escape_fault != edge::EscapeFault::NONE;
        const auto expected = invalid_receipt ? Reason::RECEIPT :
            (invalid_context ? Reason::CONTEXT : Reason::SOURCE);
        CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
        CHECK(rig.owner.calibrationOutput().reason == expected);
        CHECK(rig.sink.cancels == 1U);
    }
}

TEST_CASE("B3 B13 D105 real STOP cancels export and terminal owner remains passive") {
    Rig rig; CO_REQUIRE(rig.active()); CO_REQUIRE(rig.stop());
    CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::RECEIPT);
    CHECK(rig.sink.cancels == 1U); const auto report = rig.owner.calibrationOutput();
    const auto calls = rig.sink.calls.size(); CHECK_FALSE(rig.owner.step()); rig.owner.abort();
    CHECK(rig.sink.calls.size() == calls); same(report, rig.owner.calibrationOutput()); inhibited(rig);
}

TEST_CASE("B3 B13 D105 actual service-only reset cannot retry a retained completed calibration") {
    Rig rig; CO_REQUIRE(rig.begin(true, true, false, true)); CO_REQUIRE(rig.selectQtr());
    CO_REQUIRE(rig.calibrate()); const auto sent = rig.owner.calibrationOutput();
    CO_REQUIRE(rig.stop()); CHECK(rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING);
    CO_REQUIRE(rig.run(30U)); CO_REQUIRE(rig.run(1040U, MODE)); rig.fake.button_raw = NONE;
    for (unsigned i = 0U; i < 40U && !rig.owner.report().service_reset_pending; ++i)
        CO_REQUIRE(rig.next());
    CO_REQUIRE(rig.owner.report().service_reset_pending); CO_REQUIRE(rig.next());
    CO_REQUIRE(rig.owner.report().service_only); const auto writes = rig.sink.writes;
    CO_REQUIRE(rig.run(30U)); CO_REQUIRE(rig.modeLong()); CO_REQUIRE(rig.modeShort());
    CO_REQUIRE(rig.request()); CHECK(rig.owner.report().service_action.status == app::ServiceActionStatus::UNAVAILABLE);
    same(sent, rig.owner.calibrationOutput()); CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 0U);
}

TEST_CASE("B13 D105 explicit Runtime abort cancels active export RESET once without a synthetic epoch") {
    Rig rig; CO_REQUIRE(rig.active()); const auto before = rig.owner.calibrationOutput();
    const auto epochs = rig.owner.report().epochs; rig.owner.abort();
    CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::RESET);
    CHECK(rig.owner.calibrationOutput().token == before.token); CHECK(rig.owner.calibrationOutput().bytes == before.bytes);
    CHECK(rig.owner.report().epochs == epochs); CHECK(rig.sink.cancels == 1U);
    CHECK(rig.sink.calls.back().kind == Kind::CANCEL); CHECK(rig.sink.calls.back().halted);
    const auto calls = rig.sink.calls.size(); rig.owner.abort(); CHECK_FALSE(rig.owner.step());
    CHECK(rig.sink.calls.size() == calls); inhibited(rig);
}

TEST_CASE("B13 D105 stalled pending export fails before another deadline write") {
    Rig rig; CO_REQUIRE(rig.active()); const auto start = rig.owner.transaction().report().decision_us;
    std::uint32_t previous_age = 0U; unsigned count = 0U;
    while (rig.owner.calibrationOutput().phase == Phase::ACTIVE && count++ <= config::DUMP_STALL_MS + 2U) {
        const auto writes = rig.sink.writes; CO_REQUIRE(rig.next());
        const auto age = rig.owner.transaction().report().decision_us - start;
        if (rig.owner.calibrationOutput().phase == Phase::ACTIVE) {
            CHECK(age < config::DUMP_STALL_MS * 1000U); CHECK(rig.sink.writes == writes + 1U);
        } else { CHECK(previous_age < config::DUMP_STALL_MS * 1000U); CHECK(rig.sink.writes == writes); }
        previous_age = age;
    }
    CHECK(rig.owner.calibrationOutput().phase == Phase::FAILED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::STALL); CHECK(rig.sink.cancels == 1U);
}

TEST_CASE("B13 D105 total deadline counts progress without being reset by acknowledged bytes") {
#ifdef CO_SHORT_TOTAL
    Rig rig; rig.sink.limit = 1U; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate());
    const auto start = rig.owner.transaction().report().decision_us;
    for (unsigned i = 0U; i <= config::DUMP_TOTAL_MS + 2U &&
         rig.owner.calibrationOutput().phase == Phase::ACTIVE; ++i) {
        rig.sink.status = (i % 3U == 0U) ? dump::WriteStatus::PROGRESS : dump::WriteStatus::PENDING;
        const auto writes = rig.sink.writes; CO_REQUIRE(rig.next());
        if (rig.owner.transaction().report().decision_us - start >= config::DUMP_TOTAL_MS * 1000U)
            CHECK(rig.sink.writes == writes);
    }
    CHECK(rig.owner.calibrationOutput().phase == Phase::FAILED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::TOTAL);
    CHECK(rig.owner.calibrationOutput().bytes > 1U); CHECK(rig.sink.cancels == 1U);
#else
    CHECK(config::DUMP_TOTAL_MS > config::DUMP_STALL_MS);
#endif
}

TEST_CASE("B14 D105 natural micros wrap preserves genuine completed export") {
    Rig rig; rig.fake.now = UINT32_MAX - 1500000U;
    rig.sink.limit = 1U; CO_REQUIRE(rig.prepared()); CO_REQUIRE(rig.calibrate()); CO_REQUIRE(rig.finish());
    CHECK(rig.fake.now < 2000000U); CHECK(rig.sink.bytes == EXPECTED);
    CHECK(rig.owner.report().fault == app::RuntimeFault::NONE); CHECK(rig.sink.cancels == 0U);
}

TEST_CASE("B13 B15 D105 successful calibration then real recorder dump shares one clean owner") {
    Rig rig; CO_REQUIRE(rig.begin(true, true, true)); CO_REQUIRE(rig.seal());
    CO_REQUIRE(rig.selectQtr()); CO_REQUIRE(rig.calibrate()); const auto result = rig.owner.calibrationOutput();
    CO_REQUIRE(rig.selectDumpFromQtr()); CO_REQUIRE(rig.request(countdown::Service::LOG_DUMP));
    for (unsigned i = 0U; i < 2000U && rig.owner.report().dump.phase == dump::Phase::ACTIVE; ++i)
        CO_REQUIRE(rig.next());
    CHECK(rig.owner.report().dump.phase == dump::Phase::SENT_UNCONFIRMED);
    CHECK(rig.sink.bytes.find(std::string(EXPECTED) + "SUMOX26_DUMP,1,") == 0U);
    CHECK(rig.sink.begins == 1U); CHECK(rig.sink.cancels == 0U); same(result, rig.owner.calibrationOutput());
    writesBounded(rig);
}

TEST_CASE("B13 B15 D105 cancelled calibration poisons port before later recorder intent") {
    Rig rig; rig.sink.status = dump::WriteStatus::PENDING;
    CO_REQUIRE(rig.begin(true, true, true)); CO_REQUIRE(rig.seal()); CO_REQUIRE(rig.selectQtr());
    CO_REQUIRE(rig.calibrate()); CO_REQUIRE(rig.owner.calibrationOutput().phase == Phase::ACTIVE);
    CO_REQUIRE(rig.selectDumpFromQtr()); CHECK(rig.owner.calibrationOutput().phase == Phase::CANCELLED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::CONTEXT); CHECK(rig.sink.poisoned);
    const auto writes = rig.sink.writes; CO_REQUIRE(rig.request(countdown::Service::LOG_DUMP));
    CHECK(rig.owner.report().dump.phase == dump::Phase::REFUSED);
    CHECK(rig.owner.report().dump.reason == dump::Reason::LINUX_UNAVAILABLE);
    CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U); writesBounded(rig);
}

TEST_CASE("B13 B15 D105 cancelled recorder poisons port before later real calibration commit") {
    Rig rig; rig.sink.status = dump::WriteStatus::PENDING;
    CO_REQUIRE(rig.begin(true, true, true)); CO_REQUIRE(rig.seal()); CO_REQUIRE(rig.selectQtr());
    CO_REQUIRE(rig.selectDumpFromQtr()); CO_REQUIRE(rig.request(countdown::Service::LOG_DUMP));
    CO_REQUIRE(rig.owner.report().dump.phase == dump::Phase::ACTIVE);
    CO_REQUIRE(rig.run(30U)); CO_REQUIRE(rig.modeShort()); CO_REQUIRE(rig.modeShort());
    CHECK(rig.robot().menu.selection.service == countdown::Service::QTR_CAL);
    CHECK(rig.owner.report().dump.phase == dump::Phase::CANCELLED); CHECK(rig.sink.poisoned);
    const auto writes = rig.sink.writes; CO_REQUIRE(rig.calibrate());
    CHECK(rig.owner.calibrationOutput().phase == Phase::REFUSED);
    CHECK(rig.owner.calibrationOutput().reason == Reason::LINUX_UNAVAILABLE);
    CHECK(rig.sink.writes == writes); CHECK(rig.sink.cancels == 1U); writesBounded(rig);
}
#endif

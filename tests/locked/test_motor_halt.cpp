// Proves D095 terminal inhibition at the sole production motor callback boundary.
// Distinguishes actual acknowledged inhibition from tokens and measured stopping.
// New locked cases run identically under both host MOTORS_ALLOWED settings.
#include "../fixtures/app_transaction_fixture.h"
#include <limits>
#include <type_traits>
namespace {
using app_test::Port;
using app_test::Kind;
void pass(const Port& p) {
    APP_REQUIRE(p.count == 8U);
    CHECK(p.calls[0].kind == Kind::CLOCK);
    CHECK(p.calls[1].kind == Kind::ENABLE); CHECK_FALSE(p.calls[1].high);
    unsigned mask = 0U;
    for (unsigned i = 2; i < 6U; ++i) {
        CHECK(p.calls[i].kind == Kind::PWM); CHECK(p.calls[i].pulse == 0U);
        APP_REQUIRE(p.calls[i].channel < 4U); mask |= 1U << p.calls[i].channel;
    }
    CHECK(mask == 15U); CHECK(p.calls[6].kind == Kind::SETTLE);
    CHECK(p.calls[7].kind == Kind::CLOCK); CHECK(p.highs == 0U);
}
fsm::RobotResult idle(std::uint64_t token = 1U) {
    fsm::RobotResult value; value.fresh = true; value.token = token;
    value.outputs.ui_state = core::State::IDLE; return value;
}
}
TEST_CASE("B3 D095 halt before begin has no callbacks and cannot arm later") {
    Port p;
    { motors::MotorGate gate(p.port()); CHECK(p.count == 0U);
      const auto result = gate.halt(); CHECK(result.fresh); CHECK_FALSE(result.attempted);
      CHECK_FALSE(result.inhibition_confirmed); CHECK_FALSE(result.timing_valid);
      CHECK(result.fault == motors::Fault::NOT_INITIALIZED); CHECK(p.count == 0U);
      CHECK_FALSE(gate.halt().fresh); CHECK_FALSE(gate.begin()); CHECK(p.count == 0U); }
    CHECK(p.count == 0U);
    static_assert(!std::is_convertible<motors::HaltResult, fsm::PreviousTick>::value,
                  "halt is not an ordinary application receipt");
}
TEST_CASE("B3 D095 first halt brackets exactly one inhibit and repeats are passive") {
    Port p; motors::MotorGate gate(p.port()); APP_REQUIRE(gate.begin());
    p.clear(123U); p.work_us = 3U; p.settle_us = 41U;
    const auto h = gate.halt(); pass(p); app_test::zero(p);
    CHECK(h.fresh); CHECK(h.attempted); CHECK(h.inhibition_confirmed); CHECK(h.timing_valid);
    CHECK(h.started_us == 123U); CHECK(h.completed_us == 182U);
    CHECK(h.fault == motors::Fault::STOPPED);
    p.clear(999U); const auto again = gate.halt(); CHECK_FALSE(again.fresh);
    CHECK(again.completed_us == h.completed_us); CHECK(again.started_us == h.started_us);
    CHECK(again.inhibition_confirmed); CHECK(p.count == 0U);
}
TEST_CASE("B3 D095 halt attempts every zero and settle despite each callback failure") {
    for (unsigned failed = 1U; failed <= 6U; ++failed) {
        CAPTURE(failed); Port p; motors::MotorGate gate(p.port()); APP_REQUIRE(gate.begin());
        p.clear(100U); p.fail_at = failed; const auto h = gate.halt(); pass(p);
        CHECK_FALSE(h.inhibition_confirmed); CHECK(h.fault == motors::Fault::IO);
        CHECK(h.timing_valid); CHECK(p.operations == 6U);
        p.clear(); CHECK_FALSE(gate.halt().fresh); CHECK(p.count == 0U);
    }
}
TEST_CASE("B3 D095 halt clocks allow equality wrap and below half range only") {
    const std::uint32_t starts[] = {77U, 0xfffffff0U, 7U, 7U, 7U, 100U};
    const std::uint32_t ends[] = {77U, 0x10U, 0x80000006U, 0x80000007U, 0x80000008U, 99U};
    for (unsigned i = 0U; i < 6U; ++i) {
        CAPTURE(i); Port p; motors::MotorGate gate(p.port()); APP_REQUIRE(gate.begin());
        p.clear(); p.scripted = 2; p.clock_script[0] = starts[i]; p.clock_script[1] = ends[i];
        const auto h = gate.halt(); pass(p); CHECK(h.inhibition_confirmed);
        CHECK(h.timing_valid == (i < 3U)); CHECK(h.started_us == starts[i]);
        CHECK(h.completed_us == ends[i]); CHECK(h.fault == motors::Fault::STOPPED);
    }
}
TEST_CASE("B3 D095 halt preserves earlier command token and IO causes") {
    for (unsigned cause = 0; cause < 3U; ++cause) {
        Port p; motors::MotorGate gate(p.port()); APP_REQUIRE(gate.begin());
        p.clear(100U); auto command = idle();
        if (cause == 0) command.outputs.duty_l = 2.0F;
        if (cause == 1) command.token = 0U;
        if (cause == 2) p.fail_at = 1U;
        const auto applied = gate.apply(100U, command); const auto first = applied.fault;
        CHECK(first != motors::Fault::NONE); p.clear(110U);
        CHECK(gate.halt().fault == first); pass(p);
    }
}
TEST_CASE("B3 D095 halt after failed setup still performs one bounded inhibit") {
    for (unsigned failed = 1; failed <= 12U; ++failed) {
        Port p; p.fail_at = failed; motors::MotorGate gate(p.port());
        const bool initialized = gate.begin();
        if (initialized) continue;
        p.clear(19U); const auto h = gate.halt(); pass(p);
        CHECK(h.attempted); CHECK(h.fault == motors::Fault::IO);
    }
}
TEST_CASE("B3 D095 missing port clock does not suppress physical halt") {
    Port p; auto port = p.port(); port.clockUs = nullptr;
    motors::MotorGate gate(port); CHECK_FALSE(gate.begin()); p.clear();
    const auto h = gate.halt(); CHECK(h.attempted); CHECK_FALSE(h.timing_valid);
    CHECK(h.fault == motors::Fault::PORT); CHECK(p.operations == 6U);
    CHECK(p.clocks == 0U); CHECK(p.highs == 0U);
}
TEST_CASE("B3 D095 successful reset clears halt cache failed reset preserves it") {
    Port p; motors::MotorGate gate(p.port()); APP_REQUIRE(gate.begin());
    p.clear(10U); const auto first = gate.halt();
    p.clear(); p.fail_at = 1; CHECK_FALSE(gate.reset()); p.clear();
    const auto unchanged = gate.halt(); CHECK_FALSE(unchanged.fresh);
    CHECK(unchanged.started_us == first.started_us); CHECK(p.count == 0U);
    APP_REQUIRE(gate.reset()); p.clear(50U); const auto next = gate.halt();
    CHECK(next.fresh); CHECK(next.started_us == 50U); pass(p);
}
TEST_CASE("B3 D095 halt prevents a later ready command from enabling") {
    Port p; motors::MotorGate gate(p.port()); APP_REQUIRE(gate.begin());
    auto hold = idle(); hold.outputs.ui_state = core::State::COUNTDOWN;
    hold.lifecycle.gate.phase = countdown::Phase::HOLDING;
    hold.lifecycle.gate.start_release = true; hold.lifecycle.gate.release_us = 100U;
    p.now = 100U; APP_REQUIRE(gate.apply(100U, hold).feedback.applied_valid);
    auto ready = hold; ready.token = 2U; ready.lifecycle.gate.start_release = false;
    ready.lifecycle.gate.phase = countdown::Phase::READY; ready.lifecycle.gate.motion_permitted = true;
    ready.outputs = {0.25F, -0.25F, true, core::State::SEARCH}; p.now = 5100100U;
    APP_REQUIRE(gate.apply(p.now, ready).feedback.applied_valid);
    CHECK(p.enabled == (MOTORS_ALLOWED != 0)); APP_REQUIRE(gate.halt().inhibition_confirmed);
    p.clear(5101100U); ready.token = 3U; const auto refused = gate.apply(p.now, ready);
    CHECK_FALSE(refused.feedback.applied_valid); CHECK(p.highs == 0U); app_test::zero(p);
}

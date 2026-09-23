// Proves B3/B5/B6/B7 at the production MotorGate checked callback boundary.
// Independent contract-derived traces keep logical permission separate from applied receipts.
// Run unchanged in default-disabled and separate host-only MOTORS_ALLOWED=1 builds.
#include "doctest.h"
#include "config.h"
#include "hal/motors.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <initializer_list>
#include <limits>

// The project disables exceptions; failed prerequisites must not continue into
// dependent trace indexing or generate thousands of misleading later failures.
#define GATE_REQUIRE(...) do { \
    const bool gate_prerequisite = (__VA_ARGS__); \
    CHECK_MESSAGE(gate_prerequisite, #__VA_ARGS__); \
    if (!gate_prerequisite) std::abort(); \
} while (false)

namespace {
using Channel = motors::Channel;
using Fault = motors::Fault;
using Phase = countdown::Phase;
using State = core::State;
using Button = core::ButtonLevel;
constexpr std::uint32_t HOLD_US =
    (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
constexpr std::uint32_t DEBOUNCE_US = config::BTN_DEBOUNCE_MS * 1000U;
constexpr bool ALLOWED = MOTORS_ALLOWED != 0;
enum class Kind { CONFIG_ENABLE, CONFIG_PWM, ENABLE, PWM, SETTLE, CLOCK };
struct Call {
    Kind kind;
    unsigned channel = 0;
    std::uint32_t period = 0;
    std::uint32_t pulse = 0;
    bool value = false;
    bool ok = true;
};

struct Trace {
    std::array<Call, 64> calls{};
    std::array<bool, 64> fail{};
    std::array<std::uint32_t, 4> pulses{};
    std::size_t size = 0;
    unsigned checked = 0;
    std::uint32_t now = 0;
    bool enabled = false;
    bool latched = false;
    bool unsafe_high = false;

    bool record(Call call) {
        call.ok = !fail.at(checked++);
        calls.at(size++) = call;
        ++now;
        return call.ok;
    }
    void clear(std::uint32_t time = 0) {
        size = 0;
        checked = 0;
        fail.fill(false);
        now = time;
    }
    static Trace& self(void* context) { return *static_cast<Trace*>(context); }
    static bool configureEnable(void* context) {
        auto& t = self(context);
        const bool ok = t.record({Kind::CONFIG_ENABLE});
        if (ok) t.enabled = false;
        return ok;
    }
    static bool configurePwm(void* context, Channel channel) {
        auto& t = self(context);
        if (t.enabled) t.unsafe_high = true;
        return t.record({Kind::CONFIG_PWM, static_cast<unsigned>(channel)});
    }
    static bool enable(void* context, bool value) {
        auto& t = self(context);
        if (value && !t.latched) t.unsafe_high = true;
        const bool ok = t.record({Kind::ENABLE, 0, 0, 0, value});
        if (ok) t.enabled = value;
        return ok;
    }
    static bool pwm(void* context, Channel channel, std::uint32_t period,
                    std::uint32_t pulse) {
        auto& t = self(context);
        if (t.enabled) t.unsafe_high = true;
        const auto index = static_cast<unsigned>(channel);
        const bool ok = t.record({Kind::PWM, index, period, pulse});
        if (ok) { t.pulses.at(index) = pulse; t.latched = false; }
        return ok;
    }
    static bool settle(void* context) {
        auto& t = self(context);
        const bool ok = t.record({Kind::SETTLE});
        if (ok) t.latched = true;
        return ok;
    }
    static std::uint32_t clock(void* context) {
        auto& t = self(context);
        t.calls.at(t.size++) = {Kind::CLOCK};
        return t.now;
    }
    motors::Port port() {
        return {this, configureEnable, configurePwm, enable, pwm, settle, clock,
                {1000U, 997U, 251U, 65535U}};
    }
};

fsm::RobotResult idle(std::uint64_t token = 1) {
    fsm::RobotResult result;
    result.fresh = true;
    result.token = token;
    result.outputs.ui_state = State::IDLE;
    return result;
}

fsm::RobotResult holding(std::uint64_t token, std::uint32_t anchor,
                         bool release = false) {
    auto result = idle(token);
    result.outputs.ui_state = State::COUNTDOWN;
    result.lifecycle.gate.phase = Phase::HOLDING;
    result.lifecycle.gate.release_us = anchor;
    result.lifecycle.gate.start_release = release;
    return result;
}

fsm::RobotResult ready(std::uint64_t token, std::uint32_t anchor,
                       float left = 0.25F, float right = -0.3F) {
    auto result = holding(token, anchor);
    result.outputs = {left, right, true, State::SEARCH};
    result.lifecycle.gate.phase = Phase::READY;
    result.lifecycle.gate.motion_permitted = true;
    return result;
}

void checkZero(const Trace& trace) {
    CHECK_FALSE(trace.enabled);
    for (const auto pulse : trace.pulses) CHECK(pulse == 0U);
    for (std::size_t i = 0; i < trace.size; ++i) {
        const auto& call = trace.calls[i];
        if (call.kind == Kind::ENABLE) CHECK_FALSE(call.value);
        if (call.kind == Kind::PWM) CHECK(call.pulse == 0U);
    }
}

void checkReceipt(const motors::Result& result, const Trace& trace,
                  std::uint64_t token, bool valid) {
    CHECK(result.consumed);
    CHECK(result.feedback.token == token);
    CHECK(result.feedback.applied_valid == valid);
    CHECK(result.feedback.applied_us == trace.now);
    CHECK_FALSE(result.feedback.duration_valid);
    GATE_REQUIRE(trace.size > 0);
    CHECK(trace.calls[trace.size - 1].kind == Kind::CLOCK);
}

void checkSequence(const Trace& trace, std::size_t start, bool high,
                   bool zero = false) {
    GATE_REQUIRE(trace.size >= start + 6U);
    CHECK(trace.calls[start].kind == Kind::ENABLE);
    CHECK_FALSE(trace.calls[start].value);
    unsigned seen = 0;
    for (std::size_t i = start + 1; i < start + 5; ++i) {
        const auto& call = trace.calls[i];
        CHECK(call.kind == Kind::PWM);
        GATE_REQUIRE(call.channel < 4U);
        CHECK((seen & (1U << call.channel)) == 0U);
        seen |= 1U << call.channel;
        if (zero) CHECK(call.pulse == 0U);
    }
    CHECK(seen == 15U);
    CHECK(trace.calls[start + 5].kind == Kind::SETTLE);
    if (high) {
        GATE_REQUIRE(trace.size > start + 6);
        CHECK(trace.calls[start + 6].kind == Kind::ENABLE);
        CHECK(trace.calls[start + 6].value);
    }
}

struct Rig {
    Trace trace;
    motors::Port port = trace.port();
    motors::MotorGate gate{port};
    std::uint64_t token = 0;
    std::uint32_t anchor = 12345U;

    void begin() { GATE_REQUIRE(gate.begin()); trace.clear(); }
    motors::Result apply(std::uint32_t time, fsm::RobotResult command) {
        command.token = ++token;
        trace.clear(time + 10U);
        return gate.apply(time, command);
    }
    void arm() {
        const auto result = apply(anchor, holding(0, anchor, true));
        GATE_REQUIRE(result.fault == Fault::NONE);
        GATE_REQUIRE(result.feedback.applied_valid);
    }
    void go() {
        arm();
        const auto result = apply(anchor + HOLD_US, ready(0, anchor));
        GATE_REQUIRE(result.fault == Fault::NONE);
        GATE_REQUIRE(result.feedback.applied_valid);
    }
};

std::uint32_t next(std::uint32_t& seed) {
    seed ^= seed << 13U;
    seed ^= seed >> 17U;
    seed ^= seed << 5U;
    return seed;
}

struct Stream {
    Rig rig;
    countdown::Controller controller;
    std::uint64_t time = 0;

    void step(std::uint64_t at, Button button, bool permitted) {
        core::Inputs input;
        input.t_us = static_cast<std::uint32_t>(at);
        input.button_level = button;
        const auto lifecycle = controller.step(input);
        auto command = idle();
        command.lifecycle.gate = lifecycle;
        command.outputs.ui_state = lifecycle.phase == Phase::HOLDING ?
            State::COUNTDOWN : (permitted ? State::SEARCH : State::IDLE);
        if (permitted) command.outputs = {0.45F, -0.25F, true, State::SEARCH};
        const auto applied = rig.apply(input.t_us, command);
        CHECK(lifecycle.motion_permitted == permitted);
        CHECK(applied.fault == Fault::NONE);
        CHECK(applied.feedback.applied_valid);
        CHECK(applied.feedback.motors_enabled == (permitted && ALLOWED));
        if (!permitted || !ALLOWED) checkZero(rig.trace);
        CHECK_FALSE(rig.trace.unsafe_high);
        time = at;
    }
};

struct RobotRig {
    Rig rig;
    fsm::Robot robot;
    fsm::RobotInput input;
    fsm::RobotResult last;
    motors::Result receipt;

    RobotRig() {
        rig.begin();
        input.initialization_complete = true;
        input.observations_fresh = true;
        input.imu_ok = true;
        input.vbat_valid = true;
        input.vbat_v = config::V_NOM_V;
        input.opp_raw_mask = config::OPP_ACTIVE_LOW_MASK;
        for (auto& raw : input.line_raw_us) raw = config::QTR_TIMEOUT_US;
    }
    void step(std::uint32_t time, Button button = Button::NONE) {
        input.t_us = time;
        input.button = button;
        input.previous = receipt.feedback;
        last = robot.step(input);
        rig.trace.clear(time + 10U);
        receipt = rig.gate.apply(time, last);
    }
    std::uint32_t release(std::uint32_t base = 0) {
        step(base);
        step(base + DEBOUNCE_US);
        step(base + DEBOUNCE_US + 1000U, Button::START);
        step(base + 2U * DEBOUNCE_US + 1000U, Button::START);
        step(base + 2U * DEBOUNCE_US + 2000U);
        const auto anchor = base + 3U * DEBOUNCE_US + 2000U;
        step(anchor);
        GATE_REQUIRE(last.lifecycle.gate.start_release);
        GATE_REQUIRE(last.lifecycle.gate.release_us == anchor);
        return anchor;
    }
};
} // namespace

TEST_CASE("R1 B3 MotorGate construction and destruction perform no I/O") {
    Trace trace;
    { motors::MotorGate gate(trace.port()); CHECK(trace.size == 0U); }
    CHECK(trace.size == 0U);
}

TEST_CASE("R1 B3 MotorGate begin configures LOW before each PWM and settles zeros") {
    Rig rig;
    GATE_REQUIRE(rig.gate.begin());
    GATE_REQUIRE(rig.trace.size == 11U);
    CHECK(rig.trace.calls[0].kind == Kind::CONFIG_ENABLE);
    CHECK(rig.trace.calls[1].kind == Kind::ENABLE);
    CHECK_FALSE(rig.trace.calls[1].value);
    unsigned configured = 0;
    for (std::size_t i = 2; i < 6; ++i) {
        CHECK(rig.trace.calls[i].kind == Kind::CONFIG_PWM);
        configured |= 1U << rig.trace.calls[i].channel;
    }
    CHECK(configured == 15U);
    CHECK(rig.trace.calls[10].kind == Kind::SETTLE);
    checkZero(rig.trace);
    CHECK_FALSE(rig.trace.unsafe_high);
    rig.trace.clear();
    CHECK_FALSE(rig.gate.begin());
    checkZero(rig.trace);
}

TEST_CASE("R1 B3 MotorGate rejects every missing checked callback") {
    for (unsigned missing = 0; missing < 6; ++missing) {
        CAPTURE(missing);
        Trace trace;
        auto port = trace.port();
        if (missing == 0) port.configureEnableLow = nullptr;
        if (missing == 1) port.configurePwm = nullptr;
        if (missing == 2) port.writeEnable = nullptr;
        if (missing == 3) port.writePwm = nullptr;
        if (missing == 4) port.settle = nullptr;
        if (missing == 5) port.clockUs = nullptr;
        motors::MotorGate gate(port);
        CHECK_FALSE(gate.begin());
        CHECK(gate.fault() != Fault::NONE);
        checkZero(trace);
    }
}

TEST_CASE("B6 MotorGate validates all period bounds including the exact maximum") {
    for (unsigned channel = 0; channel < 4; ++channel) {
        for (const auto period : {0U, 16777217U, 0xffffffffU}) {
            Trace trace;
            auto port = trace.port();
            port.period_cycles[channel] = period;
            motors::MotorGate gate(port);
            CHECK_FALSE(gate.begin());
            checkZero(trace);
        }
    }
    Trace trace;
    auto port = trace.port();
    for (auto& period : port.period_cycles) period = 16777216U;
    motors::MotorGate gate(port);
    CHECK(gate.begin());
}

TEST_CASE("R1 B3 MotorGate initialization failure at every callback cleans up once") {
    for (unsigned failure = 0; failure < 11; ++failure) {
        CAPTURE(failure);
        Rig rig;
        rig.trace.fail[failure] = true;
        CHECK_FALSE(rig.gate.begin());
        CHECK(rig.gate.fault() == Fault::IO);
        GATE_REQUIRE(rig.trace.size == failure + 7U);
        checkSequence(rig.trace, failure + 1U, false, true);
        if (failure <= 1) {
            for (std::size_t i = 0; i < rig.trace.size; ++i)
                CHECK(rig.trace.calls[i].kind != Kind::CONFIG_PWM);
        }
        rig.trace.clear();
        CHECK_FALSE(rig.gate.begin());
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate apply before initialization never grants permission") {
    Rig rig;
    const auto result = rig.apply(0, idle());
    CHECK(result.fault == Fault::NOT_INITIALIZED);
    CHECK_FALSE(result.feedback.applied_valid);
    checkZero(rig.trace);
    rig.trace.clear();
    rig.gate.reset();
    const auto again = rig.apply(1, idle());
    CHECK_FALSE(again.feedback.applied_valid);
    checkZero(rig.trace);
}

TEST_CASE("R1 B3 MotorGate holds every 1kHz tick through full hold including micros wrap") {
    for (const auto anchor : {0U, 12345U, 0xfff00000U}) {
        Rig rig;
        rig.anchor = anchor;
        rig.begin();
        rig.arm();
        for (std::uint32_t age = 1; age < HOLD_US; age += 1000U) {
            const auto result = rig.apply(anchor + age, holding(0, anchor));
            GATE_REQUIRE(result.fault == Fault::NONE);
            CHECK(result.feedback.applied_valid);
            checkZero(rig.trace);
        }
        const auto before = rig.apply(anchor + HOLD_US - 1U, holding(0, anchor));
        CHECK(before.feedback.applied_valid);
        checkZero(rig.trace);
        const auto at = rig.apply(anchor + HOLD_US, ready(0, anchor));
        checkReceipt(at, rig.trace, rig.token, true);
        CHECK(at.fault == Fault::NONE);
        CHECK(at.feedback.motors_enabled == ALLOWED);
        checkSequence(rig.trace, 0, ALLOWED, !ALLOWED);
        const auto after = rig.apply(anchor + HOLD_US + 1U, ready(0, anchor));
        CHECK(after.feedback.motors_enabled == ALLOWED);
    }
}

TEST_CASE("R1 B3 MotorGate rejects READY one microsecond before the full deadline") {
    Rig rig;
    rig.begin();
    rig.arm();
    const auto result = rig.apply(rig.anchor + HOLD_US - 1U, ready(0, rig.anchor));
    checkReceipt(result, rig.trace, rig.token, false);
    CHECK(result.fault == Fault::COMMAND);
    checkZero(rig.trace);
}

TEST_CASE("R1 B3 MotorGate remembers completed hold over a complete micros wrap") {
    Rig rig;
    rig.begin();
    rig.go();
    for (const auto age : {0x80000000U, 0xfffffff0U, 1U, 1000U}) {
        const auto result = rig.apply(rig.anchor + age, ready(0, rig.anchor));
        CHECK(result.fault == Fault::NONE);
        CHECK(result.feedback.applied_valid);
        CHECK(result.feedback.motors_enabled == ALLOWED);
    }
}

TEST_CASE("R1 B3 MotorGate checks 10000 seeded debounced noisy release streams") {
    std::uint32_t seed = 0xa13c07e9U;
    for (unsigned stream = 0; stream < 10000; ++stream) {
        CAPTURE(stream);
        Stream s;
        s.rig.begin();
        const auto base = static_cast<std::uint64_t>(next(seed));
        s.step(base, Button::NONE, false);
        s.step(base + DEBOUNCE_US, Button::NONE, false);
        const auto press = s.time + 1U + next(seed) % 10000U;
        s.step(press, Button::START, false);
        s.step(press + DEBOUNCE_US, Button::START, false);
        for (unsigned bounce = 0; bounce < 3; ++bounce) {
            s.step(s.time + 1U + next(seed) % 3000U, Button::NONE, false);
            s.step(s.time + 1U + next(seed) % 3000U, Button::START, false);
        }
        const auto release = s.time + 1U + next(seed) % 10000U;
        s.step(release, Button::NONE, false);
        s.step(release + DEBOUNCE_US - 1U, Button::NONE, false);
        const auto anchor = release + DEBOUNCE_US;
        s.step(anchor, Button::NONE, false);
        for (unsigned sample = 1; sample <= 8; ++sample) {
            const auto age = sample * (HOLD_US / 10U) + next(seed) % 10000U;
            s.step(anchor + age, Button::NONE, false);
        }
        s.step(anchor + HOLD_US - 1U, Button::NONE, false);
        s.step(anchor + HOLD_US, Button::NONE, true);
        s.step(anchor + HOLD_US + 1000U, Button::NONE, true);
    }
}

TEST_CASE("R1 B3 MotorGate missed release cannot arm HOLDING or READY even disabled") {
    for (const bool is_ready : {false, true}) {
        for (const bool enabled : {false, true}) {
            Rig rig;
            rig.begin();
            auto command = is_ready ? ready(0, rig.anchor) : holding(0, rig.anchor);
            if (!enabled) command.outputs = {0, 0, false, command.outputs.ui_state};
            const auto result = rig.apply(rig.anchor + HOLD_US, command);
            CHECK(result.fault == Fault::COMMAND);
            CHECK_FALSE(result.feedback.applied_valid);
            checkZero(rig.trace);
        }
    }
}

TEST_CASE("R1 B3 MotorGate accepted release requires every contract field") {
    for (unsigned malformed = 0; malformed < 7; ++malformed) {
        Rig rig;
        rig.begin();
        auto command = holding(0, rig.anchor, true);
        if (malformed == 0) command.lifecycle.gate.phase = Phase::READY;
        if (malformed == 1) command.outputs.ui_state = State::SEARCH;
        if (malformed == 2) command.lifecycle.gate.motion_permitted = true;
        if (malformed == 3) --command.lifecycle.gate.release_us;
        if (malformed == 4) command.outputs.motors_enabled = true;
        if (malformed == 5) command.outputs.duty_l = 0.01F;
        if (malformed == 6) command.outputs.duty_r = -0.01F;
        const auto result = rig.apply(rig.anchor, command);
        CHECK(result.fault == Fault::COMMAND);
        CHECK_FALSE(result.feedback.applied_valid);
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate rejects changed release identity in HOLDING and READY") {
    for (const bool is_ready : {false, true}) {
        Rig rig;
        rig.begin();
        rig.arm();
        auto command = is_ready ? ready(0, rig.anchor + 1U) : holding(0, rig.anchor + 1U);
        const auto result = rig.apply(rig.anchor + HOLD_US, command);
        CHECK(result.fault == Fault::COMMAND);
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate BOOT and IDLE cancellation consume old release identity") {
    for (const auto state : {State::BOOT, State::IDLE}) {
        Rig rig;
        rig.begin();
        rig.arm();
        auto command = idle();
        command.outputs.ui_state = state;
        CHECK(rig.apply(rig.anchor + 100U, command).feedback.applied_valid);
        checkZero(rig.trace);
        const auto result = rig.apply(rig.anchor + HOLD_US, ready(0, rig.anchor));
        CHECK(result.fault == Fault::COMMAND);
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate cancel then new release requires a complete new hold") {
    Rig rig;
    rig.begin();
    rig.arm();
    CHECK(rig.apply(rig.anchor + 100U, idle()).feedback.applied_valid);
    rig.anchor += HOLD_US - 1U;
    rig.arm();
    const auto result = rig.apply(rig.anchor + 1U, ready(0, rig.anchor));
    CHECK(result.fault == Fault::COMMAND);
    checkZero(rig.trace);
}

TEST_CASE("R1 B3 MotorGate fresh false ignores malformed payload and does not consume") {
    Rig rig;
    rig.begin();
    auto command = ready(999, 0);
    command.fresh = false;
    command.outputs.duty_l = std::numeric_limits<float>::quiet_NaN();
    const auto ignored = rig.gate.apply(0, command);
    CHECK_FALSE(ignored.consumed);
    CHECK(rig.trace.size == 0U);
    CHECK(rig.gate.fault() == Fault::NONE);
    command = idle(1);
    CHECK(rig.gate.apply(0, command).feedback.applied_valid);
    rig.trace.clear();
    command.fresh = false;
    CHECK_FALSE(rig.gate.apply(0, command).consumed);
    CHECK(rig.trace.size == 0U);
}

TEST_CASE("R1 B3 MotorGate zero repeated and regressing fresh tokens latch inhibition") {
    for (const std::uint64_t token : {0ULL, 9ULL, 10ULL}) {
        Rig rig;
        rig.begin();
        GATE_REQUIRE(rig.gate.apply(0, idle(10)).feedback.applied_valid);
        rig.trace.clear(100);
        const auto result = rig.gate.apply(100, idle(token));
        CHECK(result.fault == Fault::TOKEN);
        CHECK_FALSE(result.consumed);
        CHECK_FALSE(result.feedback.applied_valid);
        checkZero(rig.trace);
        rig.trace.clear();
        CHECK(rig.gate.apply(200, idle(11)).fault == Fault::TOKEN);
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate accepts strict token gaps and the uint64 maximum without wrap") {
    Rig rig;
    rig.begin();
    for (const auto token : {1ULL, 400ULL, 0xffffffffffffffffULL}) {
        rig.trace.clear(100);
        const auto result = rig.gate.apply(100, idle(token));
        CHECK(result.fault == Fault::NONE);
        checkReceipt(result, rig.trace, token, true);
    }
    CHECK(rig.gate.apply(200, idle(1)).fault == Fault::TOKEN);
}

TEST_CASE("R1 B3 MotorGate STOP is acknowledged inhibition and reset-only recovery") {
    Rig rig;
    rig.begin();
    rig.go();
    auto stopped = idle();
    stopped.outputs.ui_state = State::STOPPED;
    stopped.lifecycle.gate.phase = Phase::STOPPED;
    for (unsigned repeat = 0; repeat < 3; ++repeat) {
        const auto result = rig.apply(rig.anchor + HOLD_US + repeat + 1U, stopped);
        CHECK(result.fault == Fault::STOPPED);
        checkReceipt(result, rig.trace, rig.token, true);
        checkZero(rig.trace);
    }
    CHECK_FALSE(rig.apply(rig.anchor + HOLD_US + 10U, ready(0, rig.anchor)).feedback.applied_valid);
    checkZero(rig.trace);
    rig.trace.clear();
    CHECK_FALSE(rig.gate.begin());
    CHECK(rig.gate.fault() == Fault::STOPPED);
    GATE_REQUIRE(rig.gate.reset());
    CHECK(rig.gate.fault() == Fault::NONE);
    CHECK(rig.apply(0, idle()).feedback.applied_valid);
    rig.anchor += HOLD_US + 1000U;
    rig.go();
}

TEST_CASE("R1 B3 MotorGate reset preserves token high water and removes release permission") {
    for (const bool replay : {false, true}) {
        Rig rig;
        rig.begin();
        rig.go();
        const auto old_token = rig.token;
        rig.trace.clear();
        GATE_REQUIRE(rig.gate.reset());
        checkSequence(rig.trace, 0, false, true);
        checkZero(rig.trace);
        auto command = replay ? idle(old_token) : ready(old_token + 1, rig.anchor);
        rig.trace.clear();
        const auto result = rig.gate.apply(rig.anchor + HOLD_US + 1U, command);
        CHECK(result.fault == (replay ? Fault::TOKEN : Fault::COMMAND));
        CHECK_FALSE(result.feedback.applied_valid);
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate rejects nonfinite out-of-range and disabled nonzero duty") {
    const float invalid[] = {std::numeric_limits<float>::quiet_NaN(),
        std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity(),
        std::nextafter(1.0F, 2.0F), std::nextafter(-1.0F, -2.0F)};
    for (const auto value : invalid) {
        for (const bool left : {false, true}) {
            Rig rig;
            rig.begin();
            rig.go();
            auto command = ready(0, rig.anchor);
            if (left) command.outputs.duty_l = value; else command.outputs.duty_r = value;
            CHECK(rig.apply(rig.anchor + HOLD_US + 1U, command).fault == Fault::COMMAND);
            checkZero(rig.trace);
        }
    }
    Rig rig;
    rig.begin();
    auto command = idle();
    command.outputs.duty_r = std::numeric_limits<float>::denorm_min();
    CHECK(rig.apply(0, command).fault == Fault::COMMAND);
    checkZero(rig.trace);
}

TEST_CASE("R1 B3 MotorGate rejects unknown state and lifecycle enums") {
    for (const bool state : {false, true}) {
        Rig rig;
        rig.begin();
        auto command = idle();
        if (state) command.outputs.ui_state = static_cast<State>(255);
        else command.lifecycle.gate.phase = static_cast<Phase>(255);
        CHECK(rig.apply(0, command).fault == Fault::COMMAND);
        checkZero(rig.trace);
    }
}

TEST_CASE("R1 B3 MotorGate every prohibited state and permission fault inhibits motion") {
    for (const auto state : {State::BOOT, State::IDLE, State::COUNTDOWN,
                              State::STOPPED, State::DRIVE_TEST}) {
        Rig rig;
        rig.begin();
        rig.go();
        auto command = ready(0, rig.anchor);
        command.outputs.ui_state = state;
        CHECK_FALSE(rig.apply(rig.anchor + HOLD_US + 1U, command).feedback.applied_valid);
        checkZero(rig.trace);
    }
    for (unsigned fault = 0; fault < 4; ++fault) {
        Rig rig;
        rig.begin();
        rig.go();
        auto command = ready(0, rig.anchor);
        if (fault == 0) command.lifecycle.gate.motion_permitted = false;
        if (fault == 1) command.lifecycle.gate.phase = Phase::HOLDING;
        if (fault == 2) command.contract_faults = 1;
        if (fault == 3) command.escape_fault = edge::EscapeFault::WHITE_PATTERN;
        CHECK_FALSE(rig.apply(rig.anchor + HOLD_US + 1U, command).feedback.applied_valid);
        checkZero(rig.trace);
    }
}

TEST_CASE("R6 B5 B6 MotorGate full duty requires current centered ATTACK contact") {
    for (unsigned mask = 0; mask < 256; ++mask) {
        for (const bool contact : {false, true}) {
            for (const auto state : {State::SEARCH, State::TRACK, State::ATTACK}) {
                Rig rig;
                rig.begin();
                rig.go();
                auto command = ready(0, rig.anchor, mask % 2U == 0 ? 1.0F : -1.0F, 0.1F);
                if (mask % 3U == 0) {
                    command.outputs.duty_r = command.outputs.duty_l;
                    command.outputs.duty_l = 0.1F;
                }
                command.outputs.ui_state = state;
                command.opponent_mask = static_cast<std::uint8_t>(mask);
                command.contact = contact;
                const bool valid = state == State::ATTACK && contact &&
                    opp_fusion::frontView(command.opponent_mask).centered;
                const auto result = rig.apply(rig.anchor + HOLD_US + 1U, command);
                CHECK(result.feedback.applied_valid == valid);
                CHECK(result.fault == (valid ? Fault::NONE : Fault::COMMAND));
                CHECK(result.feedback.motors_enabled == (valid && ALLOWED));
                if (!valid || !ALLOWED) checkZero(rig.trace);
            }
        }
    }
}

TEST_CASE("B6 MotorGate reports exact floored period fractions across signs and tiny duty") {
    for (const float left : {0.0F, -0.0F, 0.00001F, -0.00001F, 0.333333F, -0.631F}) {
        for (const float right : {0.0F, 0.001F, -0.257F, 0.753F}) {
            Rig rig;
            rig.begin();
            rig.go();
            const auto result = rig.apply(rig.anchor + HOLD_US + 1U, ready(0, rig.anchor, left, right));
            const unsigned li = left < 0.0F ? 1U : 0U;
            const unsigned ri = right < 0.0F ? 3U : 2U;
            const auto lp = ALLOWED ? static_cast<std::uint32_t>(std::floor(
                std::abs(static_cast<double>(left)) * rig.port.period_cycles[li])) : 0U;
            const auto rp = ALLOWED ? static_cast<std::uint32_t>(std::floor(
                std::abs(static_cast<double>(right)) * rig.port.period_cycles[ri])) : 0U;
            CHECK(rig.trace.pulses[li] == lp);
            CHECK(rig.trace.pulses[li ^ 1U] == 0U);
            CHECK(rig.trace.pulses[ri] == rp);
            CHECK(rig.trace.pulses[ri ^ 1U] == 0U);
            const float expected_l = static_cast<float>(lp) / rig.port.period_cycles[li];
            const float expected_r = static_cast<float>(rp) / rig.port.period_cycles[ri];
            CHECK(result.feedback.duty_l == (left < 0 ? -expected_l : expected_l));
            CHECK(result.feedback.duty_r == (right < 0 ? -expected_r : expected_r));
            for (std::size_t i = 0; i < rig.trace.size; ++i) {
                const auto& call = rig.trace.calls[i];
                if (call.kind == Kind::PWM)
                    CHECK(call.period == rig.port.period_cycles[call.channel]);
            }
            checkReceipt(result, rig.trace, rig.token, true);
            CHECK_FALSE(rig.trace.unsafe_high);
        }
    }
}

TEST_CASE("B7 MotorGate brake uses enabled zeros while coast uses disabled zeros") {
    Rig rig;
    rig.begin();
    rig.go();
    const auto brake = rig.apply(rig.anchor + HOLD_US + 1U, ready(0, rig.anchor, 0, 0));
    CHECK(brake.feedback.motors_enabled == ALLOWED);
    CHECK(brake.feedback.duty_l == 0.0F);
    CHECK(brake.feedback.duty_r == 0.0F);
    checkSequence(rig.trace, 0, ALLOWED, true);
    auto command = ready(0, rig.anchor, 0, 0);
    command.outputs.motors_enabled = false;
    const auto coast = rig.apply(rig.anchor + HOLD_US + 2U, command);
    CHECK(coast.feedback.applied_valid);
    CHECK_FALSE(coast.feedback.motors_enabled);
    checkSequence(rig.trace, 0, false, true);
    checkZero(rig.trace);
}

TEST_CASE("B6 B7 MotorGate lowers EN before reversal and settles all PWM before HIGH") {
    Rig rig;
    rig.begin();
    rig.go();
    for (const auto sign : {1.0F, -1.0F, 1.0F, -1.0F}) {
        const auto result = rig.apply(rig.anchor + HOLD_US + static_cast<std::uint32_t>(rig.token),
                                      ready(0, rig.anchor, sign * 0.5F, sign * 0.25F));
        CHECK(result.feedback.applied_valid);
        checkSequence(rig.trace, 0, ALLOWED, !ALLOWED);
        CHECK_FALSE(rig.trace.unsafe_high);
        CHECK_FALSE((rig.trace.pulses[0] != 0U && rig.trace.pulses[1] != 0U));
        CHECK_FALSE((rig.trace.pulses[2] != 0U && rig.trace.pulses[3] != 0U));
    }
}

TEST_CASE("R1 B7 MotorGate transaction failure at every checked position invalidates receipt") {
    const unsigned count = ALLOWED ? 7U : 6U;
    for (unsigned failure = 0; failure < count; ++failure) {
        CAPTURE(failure);
        Rig rig;
        rig.begin();
        rig.go();
        rig.trace.clear(rig.anchor + HOLD_US + 20U);
        rig.trace.fail[failure] = true;
        const auto command = ready(++rig.token, rig.anchor);
        const auto result = rig.gate.apply(rig.anchor + HOLD_US + 10U, command);
        CHECK(result.fault == Fault::IO);
        checkReceipt(result, rig.trace, rig.token, false);
        GATE_REQUIRE(rig.trace.size == failure + 8U);
        checkSequence(rig.trace, failure + 1U, false, true);
        CHECK_FALSE(rig.trace.enabled);
        for (auto pulse : rig.trace.pulses) CHECK(pulse == 0U);
    }
}

TEST_CASE("R1 B7 MotorGate cleanup attempts every zero even when cleanup itself fails") {
    for (unsigned cleanup_failure = 0; cleanup_failure < 6; ++cleanup_failure) {
        CAPTURE(cleanup_failure);
        Rig rig;
        rig.begin();
        rig.go();
        rig.trace.clear();
        rig.trace.fail[0] = true;
        rig.trace.fail[1U + cleanup_failure] = true;
        const auto result = rig.gate.apply(rig.anchor + HOLD_US + 10U, ready(++rig.token, rig.anchor));
        CHECK(result.fault == Fault::IO);
        CHECK_FALSE(result.feedback.applied_valid);
        GATE_REQUIRE(rig.trace.size == 8U);
        checkSequence(rig.trace, 1, false, true);
        rig.trace.clear();
        const auto later = rig.gate.apply(rig.anchor + HOLD_US + 20U, ready(++rig.token, rig.anchor));
        CHECK(later.fault == Fault::IO);
        CHECK_FALSE(later.feedback.applied_valid);
        checkZero(rig.trace);
        CHECK(rig.trace.checked <= 12U);
    }
}

TEST_CASE("R1 B7 MotorGate reset checks all inhibition callbacks and never auto-recovers") {
    for (unsigned failure = 0; failure < 6; ++failure) {
        Rig rig;
        rig.begin();
        rig.go();
        rig.trace.clear();
        rig.trace.fail[failure] = true;
        CHECK_FALSE(rig.gate.reset());
        CHECK(rig.gate.fault() == Fault::IO);
        unsigned zeros = 0;
        for (std::size_t i = 0; i < rig.trace.size; ++i) {
            const auto& call = rig.trace.calls[i];
            if (call.kind == Kind::ENABLE) CHECK_FALSE(call.value);
            if (call.kind == Kind::PWM && call.pulse == 0U) zeros |= 1U << call.channel;
        }
        CHECK(zeros == 15U);
        const auto later = rig.apply(100, idle());
        CHECK(later.fault == Fault::IO);
        CHECK_FALSE(later.feedback.applied_valid);
        rig.trace.clear();
        GATE_REQUIRE(rig.gate.reset());
        CHECK(rig.gate.fault() == Fault::NONE);
        CHECK(rig.apply(200, idle()).feedback.applied_valid);
    }
}

TEST_CASE("R1 B7 MotorGate prior COMMAND becomes IO if inhibition cannot be acknowledged") {
    Rig rig;
    rig.begin();
    rig.trace.clear();
    rig.trace.fail[0] = true;
    const auto result = rig.gate.apply(0, ready(++rig.token, rig.anchor));
    CHECK(result.fault == Fault::IO);
    CHECK_FALSE(result.feedback.applied_valid);
    CHECK(rig.trace.checked <= 12U);
}

TEST_CASE("R1 B3 B6 real Robot consumes actual MotorGate receipts through hold and attack") {
    for (const auto base : {0U, 0xfff00000U}) {
        RobotRig r;
        const auto anchor = r.release(base);
        bool saw_attack = false;
        bool saw_contact = false;
        bool saw_full = false;
        for (std::uint32_t age = 1000; age <= HOLD_US + 1600000U; age += 1000U) {
            if (age == HOLD_US) r.input.opp_raw_mask = config::OPP_ACTIVE_LOW_MASK ^ 7U;
            r.step(anchor + age);
            GATE_REQUIRE(r.last.contract_faults == 0U);
            GATE_REQUIRE(r.receipt.feedback.applied_valid);
            CHECK(r.receipt.feedback.token == r.last.token);
            CHECK_FALSE(r.receipt.feedback.duration_valid);
            saw_attack |= r.last.outputs.ui_state == State::ATTACK;
            saw_contact |= r.last.contact;
            if (age < HOLD_US) checkZero(r.rig.trace);
            if (std::abs(r.receipt.feedback.duty_l) == 1.0F ||
                std::abs(r.receipt.feedback.duty_r) == 1.0F) {
                saw_full = true;
                CHECK(r.last.outputs.ui_state == State::ATTACK);
                CHECK(r.last.contact);
                CHECK(opp_fusion::frontView(r.last.opponent_mask).centered);
            }
            CHECK_FALSE(r.rig.trace.unsafe_high);
        }
        CHECK(r.last.timing_incomplete);
        CHECK(r.last.lifecycle.gate.motion_permitted);
        CHECK(saw_attack);
        CHECK(saw_contact);
        CHECK(saw_full == ALLOWED);
    }
}

TEST_CASE("R1 B3 real Robot and MotorGate paired reset preserves receipt identity") {
    RobotRig r;
    const auto anchor = r.release();
    r.step(anchor + HOLD_US);
    const auto previous_token = r.last.token;
    r.input.stop_requested = true;
    r.step(anchor + HOLD_US + 1000U);
    CHECK(r.last.outputs.ui_state == State::STOPPED);
    CHECK(r.receipt.feedback.applied_valid);
    CHECK(r.receipt.fault == Fault::STOPPED);
    r.input.stop_requested = false;
    r.step(anchor + HOLD_US + 2000U);
    CHECK(r.last.contract_faults == 0U);
    CHECK(r.receipt.feedback.applied_valid);
    GATE_REQUIRE(r.rig.gate.reset());
    r.robot.reset();
    r.receipt = {};
    const auto new_anchor = r.release(anchor + HOLD_US + 3000U);
    CHECK(r.last.token > previous_token);
    r.step(new_anchor + HOLD_US);
    CHECK(r.last.contract_faults == 0U);
    CHECK(r.receipt.feedback.applied_valid);
}

TEST_CASE("R1 B3 MotorGate rejects a replayed accepted release with a fresh token") {
    Rig rig;
    rig.begin();
    rig.arm();
    const auto replay = rig.apply(rig.anchor, holding(0, rig.anchor, true));
    CHECK(replay.fault == Fault::COMMAND);
    CHECK_FALSE(replay.feedback.applied_valid);
    checkZero(rig.trace);
}

TEST_CASE("R1 B3 MotorGate traces boot-held START without accepting a match") {
    Stream stream;
    stream.rig.begin();
    stream.step(0xffff0000ULL, Button::START, false);
    stream.step(0xffff0000ULL + HOLD_US, Button::START, false);
    stream.step(0xffff0000ULL + HOLD_US + 1U, Button::NONE, false);
    stream.step(0xffff0000ULL + HOLD_US + DEBOUNCE_US + 1U, Button::NONE, false);
    stream.step(0xffff0000ULL + 2U * HOLD_US, Button::NONE, false);
}

TEST_CASE("R1 B3 MotorGate fresh false remains exact no-I/O after a latched fault") {
    Rig rig;
    rig.begin();
    CHECK(rig.apply(0, ready(0, 0)).fault == Fault::COMMAND);
    rig.trace.clear();
    auto command = idle(0xffffffffffffffffULL);
    command.fresh = false;
    CHECK_FALSE(rig.gate.apply(100, command).consumed);
    CHECK(rig.trace.size == 0U);
    CHECK(rig.gate.fault() == Fault::COMMAND);
    GATE_REQUIRE(rig.gate.reset());
    rig.trace.clear();
    CHECK(rig.gate.apply(200, idle(2)).feedback.applied_valid);
}

TEST_CASE("R1 B3 real Robot inhibits on the following tick after a failed MotorGate receipt") {
    RobotRig r;
    const auto anchor = r.release();
    r.step(anchor + HOLD_US);
    const auto failure_time = anchor + HOLD_US + 1000U;
    r.input.t_us = failure_time;
    r.input.previous = r.receipt.feedback;
    r.last = r.robot.step(r.input);
    r.rig.trace.clear(failure_time + 10U);
    r.rig.trace.fail[0] = true;
    r.receipt = r.rig.gate.apply(failure_time, r.last);
    CHECK_FALSE(r.receipt.feedback.applied_valid);
    CHECK(r.receipt.fault == Fault::IO);
    r.step(failure_time + 1000U);
    CHECK(r.last.outputs.ui_state == State::STOPPED);
    CHECK(r.last.contract_faults != 0U);
    CHECK_FALSE(r.last.outputs.motors_enabled);
    CHECK(r.receipt.fault == Fault::IO);
    checkZero(r.rig.trace);
}

#undef GATE_REQUIRE

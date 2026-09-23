// Tests D111 from the adopted contract and public declarations, without body reads.
// Distinguishes actual source/pure diagnostics from successfully closed checkpoints.
// Isolated normal, sanitizer, configuration and counted-native profiles run these cases.
#ifndef D111_TEST_SEPARATE_MAIN
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#endif
#include "doctest.h"
#include "imu_heading_bench.h"
#include "config.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <type_traits>
#ifdef TEST_NATIVE_BINDING
#include "imu_heading_bench_native.h"
void setup();
void loop();
#endif

namespace allocations { bool active = false; unsigned calls = 0; }
extern "C" {
void* __real_malloc(std::size_t);
void* __real_calloc(std::size_t, std::size_t);
void* __real_realloc(void*, std::size_t);
void __real_free(void*);
void* __wrap_malloc(std::size_t n) {
    if (allocations::active) ++allocations::calls;
    return __real_malloc(n);
}
void* __wrap_calloc(std::size_t n, std::size_t z) {
    if (allocations::active) ++allocations::calls;
    return __real_calloc(n, z);
}
void* __wrap_realloc(void* p, std::size_t n) {
    if (allocations::active) ++allocations::calls;
    return __real_realloc(p, n);
}
void __wrap_free(void* p) {
    if (allocations::active) ++allocations::calls;
    __real_free(p);
}
}
void* operator new(std::size_t n) {
    if (allocations::active) ++allocations::calls;
    if (void* p = __real_malloc(n)) return p;
    std::abort();
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept {
    if (allocations::active) ++allocations::calls;
    __real_free(p);
}
void operator delete[](void* p) noexcept { ::operator delete(p); }
void operator delete(void* p, std::size_t) noexcept { ::operator delete(p); }
void operator delete[](void* p, std::size_t) noexcept { ::operator delete(p); }

namespace {
using namespace imu_heading_bench;
constexpr std::uint32_t HALF = 0x80000000U;
struct Guard {
    Guard() { allocations::active = true; }
    ~Guard() { allocations::active = false; }
};
Grants granted() {
    Grants g; g.enabled = g.exclusive_i2c = g.power_confirmed = g.at_rest_confirmed = true;
    g.mounting.confirmed = true;
    g.mounting.body_axis[0] = 1; g.mounting.body_axis[1] = 2; g.mounting.body_axis[2] = 3;
    return g;
}
std::uint32_t bits(float f) {
    std::uint32_t n; static_assert(sizeof(n) == sizeof(f));
    std::memcpy(&n, &f, sizeof(n)); return n;
}
bool same(const imu::CoherentMotion& a, const imu::CoherentMotion& b) {
    for (unsigned i = 0; i < 3; ++i) {
        if (a.accel_raw[i] != b.accel_raw[i] || a.gyro_raw[i] != b.gyro_raw[i] ||
            bits(a.accel_g[i]) != bits(b.accel_g[i]) || bits(a.gyro_dps[i]) != bits(b.gyro_dps[i])) return false;
    }
    return a.status == b.status && a.temperature_raw == b.temperature_raw &&
        a.started_us == b.started_us && a.completed_us == b.completed_us &&
        a.interrupt_status == b.interrupt_status && a.rail_mask == b.rail_mask && a.coherent == b.coherent;
}
bool same(const imu::Sample& a, const imu::Sample& b) {
    return a.state == b.state && a.fault == b.fault && same(a.motion, b.motion) &&
        a.bus_status == b.bus_status && a.cleanup == b.cleanup && a.error_flags == b.error_flags &&
        a.sequence == b.sequence && a.checked_us == b.checked_us &&
        a.readiness_completed_us == b.readiness_completed_us && a.motion_started_us == b.motion_started_us &&
        a.observation_gap_us == b.observation_gap_us && a.had_previous_observation == b.had_previous_observation;
}
bool same(const imu::SampleProgress& a, const imu::SampleProgress& b) {
    return a.state == b.state && a.started == b.started && a.completed == b.completed && same(a.sample, b.sample);
}
bool same(const imu::SetupReport& a, const imu::SetupReport& b) {
    return a.state == b.state && a.fault == b.fault && a.bus_status == b.bus_status &&
        a.cleanup == b.cleanup && a.error_flags == b.error_flags && a.started_us == b.started_us &&
        a.observed_us == b.observed_us && a.advances == b.advances && a.requests == b.requests;
}
bool same(const imu::Estimate& a, const imu::Estimate& b) {
    return a.state == b.state && a.fault == b.fault && a.acquisition_fault == b.acquisition_fault &&
        a.gyro_observation == b.gyro_observation && a.accel_observation == b.accel_observation &&
        a.heading_available == b.heading_available && a.heading_updated == b.heading_updated &&
        bits(a.heading_deg) == bits(b.heading_deg) && bits(a.raw_gyro_z_dps) == bits(b.raw_gyro_z_dps) &&
        bits(a.gyro_z_dps) == bits(b.gyro_z_dps) && bits(a.ax_g) == bits(b.ax_g) && bits(a.ay_g) == bits(b.ay_g) &&
        bits(a.bias_dps) == bits(b.bias_dps) && a.checked_us == b.checked_us &&
        a.observation_us == b.observation_us && a.sequence == b.sequence && a.heading_age_us == b.heading_age_us;
}
bool same(const countdown::ServiceResult& a, const countdown::ServiceResult& b) {
    return bits(a.bias_dps) == bits(b.bias_dps) && a.calibration_samples == b.calibration_samples &&
        a.calibration_finished == b.calibration_finished && a.calibration_rejected == b.calibration_rejected &&
        a.line_warning == b.line_warning && a.opponent_snapshot == b.opponent_snapshot &&
        a.active == b.active && a.finished == b.finished;
}
[[maybe_unused]] bool same(const Checkpoint& a, const Checkpoint& b) {
    return same(a.sample, b.sample) && same(a.estimate, b.estimate) &&
        a.elapsed_source_us == b.elapsed_source_us && a.delivered_us == b.delivered_us && a.closed_us == b.closed_us;
}
bool same(const Timing& a, const Timing& b) {
    return a.calls == b.calls && a.measured_calls == b.measured_calls && a.last_us == b.last_us &&
        a.maximum_us == b.maximum_us && a.last_valid == b.last_valid;
}
bool same(const Measurement& a, const Measurement& b) {
    return a.anchored == b.anchored && a.started_us == b.started_us && a.ended_us == b.ended_us &&
        a.elapsed_us == b.elapsed_us && a.first_sequence == b.first_sequence && a.last_sequence == b.last_sequence &&
        a.observations == b.observations && bits(a.start_heading_deg) == bits(b.start_heading_deg) &&
        bits(a.end_heading_deg) == bits(b.end_heading_deg) && a.delta_deg == b.delta_deg &&
        a.minimum_delta_deg == b.minimum_delta_deg && a.maximum_delta_deg == b.maximum_delta_deg &&
        a.maximum_absolute_excursion_deg == b.maximum_absolute_excursion_deg;
}
bool same(const Report& a, const Report& b) {
    return a.phase == b.phase && a.fault == b.fault && a.checkpoint_fresh == b.checkpoint_fresh &&
        a.observation_fresh == b.observation_fresh && a.clock_fault == b.clock_fault &&
        a.counter_saturated == b.counter_saturated && a.bias_applied == b.bias_applied &&
        a.cancellation_attempted == b.cancellation_attempted && same(a.setup, b.setup) &&
        same(a.progress, b.progress) && same(a.cancellation, b.cancellation) && same(a.estimate, b.estimate) &&
        same(a.calibration, b.calibration) && a.calibration_started_us == b.calibration_started_us &&
        bits(a.accepted_bias_dps) == bits(b.accepted_bias_dps) && a.admitted_polls == b.admitted_polls &&
        a.checkpoints == b.checkpoints && a.setup_not_due == b.setup_not_due && a.read_not_due == b.read_not_due &&
        a.missed_setup_releases == b.missed_setup_releases && a.missed_read_releases == b.missed_read_releases &&
        a.pending_results == b.pending_results && a.completions == b.completions && a.observations == b.observations &&
        a.no_new == b.no_new && a.maximum_observation_gap_us == b.maximum_observation_gap_us &&
        same(a.measurement, b.measurement) && same(a.start_timing, b.start_timing) &&
        same(a.setup_timing, b.setup_timing) && same(a.begin_timing, b.begin_timing) &&
        same(a.advance_timing, b.advance_timing) && same(a.cancel_timing, b.cancel_timing) && same(a.poll_timing, b.poll_timing);
}
imu::SampleProgress pending(bool begin) {
    imu::SampleProgress p; p.state = imu::AsyncState::PENDING; p.started = begin; return p;
}
imu::SampleProgress nativeFault(imu::SampleFault cause = imu::SampleFault::TRANSPORT) {
    imu::SampleProgress p; p.state = imu::AsyncState::FAULT; p.completed = true;
    p.sample.state = imu::SampleState::FAULT; p.sample.fault = cause;
    p.sample.bus_status = imu::BusStatus::NACK; p.sample.cleanup = imu::BusCleanup::DISABLED;
    p.sample.error_flags = 0x5A7U; p.sample.sequence = 17; p.sample.checked_us = 0xDEADBEEFU; return p;
}
struct Fake {
    std::uint32_t clocks[3] = {}; unsigned position = 0, clocks_used = 0;
    unsigned starts = 0, setups = 0, begins = 0, advances = 0, cancels = 0;
    std::uint32_t arguments[5] = {}; bool power = false;
    imu::SetupReport start_result{}, setup_result{};
    imu::SampleProgress begin_result = pending(true), advance_result = pending(false), cancel_result = nativeFault();
    char events[32] = {}; unsigned event_count = 0;
    const Runner* watching = nullptr; bool inspect_a = false, saw_saved_result = false;
    void event(char c) { if (event_count < sizeof(events)) events[event_count++] = c; }
    static Fake& get(void* p) { return *static_cast<Fake*>(p); }
    static std::uint32_t clock(void* p) {
        auto& f = get(p); f.event('K'); ++f.clocks_used;
        if (f.inspect_a && f.position == 1 && f.watching)
            f.saw_saved_result = same(f.watching->report().progress, f.advance_result);
        const auto value = f.clocks[f.position < 3 ? f.position : 2]; ++f.position; return value;
    }
    static imu::SetupReport start(void* p, std::uint32_t t, bool power) {
        auto& f = get(p); f.event('S'); ++f.starts; f.arguments[0] = t; f.power = power; return f.start_result;
    }
    static imu::SetupReport advanceSetup(void* p, std::uint32_t t) {
        auto& f = get(p); f.event('U'); ++f.setups; f.arguments[1] = t; return f.setup_result;
    }
    static imu::SampleProgress begin(void* p, std::uint32_t t) {
        auto& f = get(p); f.event('B'); ++f.begins; f.arguments[2] = t; return f.begin_result;
    }
    static imu::SampleProgress advance(void* p, std::uint32_t t) {
        auto& f = get(p); f.event('A'); ++f.advances; f.arguments[3] = t; return f.advance_result;
    }
    static imu::SampleProgress cancel(void* p, std::uint32_t t) {
        auto& f = get(p); f.event('X'); ++f.cancels; f.arguments[4] = t; return f.cancel_result;
    }
    Port port() { return {this, clock, start, advanceSetup, begin, advance, cancel}; }
    void times(std::uint32_t s, std::uint32_t a, std::uint32_t c) {
        clocks[0] = s; clocks[1] = a; clocks[2] = c; position = event_count = 0;
    }
};
struct Rig {
    Fake f; Runner r{f.port()}; std::uint32_t origin = 0, read_start = 0, sequence = 0, prior_source = 0;
    bool begin(std::uint32_t s = 0, Grants g = granted()) {
        origin = s; f.start_result.state = imu::SetupState::IN_PROGRESS;
        f.start_result.started_us = f.start_result.observed_us = s; f.times(s, s + 1, s + 2);
        Guard guard; return r.begin(g);
    }
    bool poll(std::uint32_t s, std::uint32_t a, std::uint32_t c) {
        f.times(s, a, c); Guard guard; return r.poll();
    }
    void ready(std::uint32_t s = 0, Grants g = granted()) {
        REQUIRE(begin(s, g));
        f.setup_result = f.start_result; f.setup_result.state = imu::SetupState::PROFILE_READY;
        f.setup_result.bus_status = imu::BusStatus::OK; f.setup_result.advances = f.setup_result.requests = 1;
        f.setup_result.observed_us = s + config::TICK_US;
        CHECK_FALSE(poll(s + config::TICK_US, s + config::TICK_US + 1, s + config::TICK_US + 2));
        REQUIRE(r.report().phase == Phase::CALIBRATION);
    }
    void startRead(std::uint32_t s) {
        read_start = s; f.begin_result = pending(true);
        CHECK_FALSE(poll(s, s + 1, s + 2)); REQUIRE(r.report().fault == Fault::NONE);
    }
    imu::SampleProgress observation(std::uint32_t checked, float rate = 2.0F) {
        imu::SampleProgress p; p.state = imu::AsyncState::COMPLETE; p.completed = true;
        auto& x = p.sample; x.state = imu::SampleState::OBSERVATION; x.bus_status = imu::BusStatus::OK;
        x.checked_us = checked; x.readiness_completed_us = read_start + 1; x.motion_started_us = read_start + 2;
        x.sequence = ++sequence; x.had_previous_observation = sequence != 1;
        x.observation_gap_us = sequence == 1 ? 0 : checked - prior_source; prior_source = checked;
        x.motion.status = imu::DecodeStatus::OK; x.motion.coherent = true;
        x.motion.started_us = read_start; x.motion.completed_us = checked;
        x.motion.interrupt_status = 1; x.motion.gyro_dps[2] = rate;
        x.motion.accel_g[0] = 0.25F; x.motion.accel_g[1] = -0.5F; x.motion.accel_g[2] = 1.0F;
        x.motion.gyro_raw[2] = 67; x.motion.temperature_raw = -13; return p;
    }
    imu::SampleProgress absent(std::uint32_t checked) const {
        imu::SampleProgress p; p.state = imu::AsyncState::COMPLETE; p.completed = true;
        p.sample.state = imu::SampleState::NO_NEW; p.sample.bus_status = imu::BusStatus::OK;
        p.sample.sequence = sequence; p.sample.checked_us = p.sample.readiness_completed_us = checked; return p;
    }
    bool sample(std::uint32_t s, float rate = 2.0F, bool is_absent = false) {
        startRead(s); f.advance_result = is_absent ? absent(s + 4) : observation(s + 4, rate);
        return poll(s + 3, s + 5, s + 6);
    }
    std::uint32_t calibrate(float rate = 2.0F, float bias = 0.5F, std::uint32_t s = 0) {
        auto g = granted(); g.initial_bias_dps = bias; ready(s, g);
        const auto anchor = r.report().calibration_started_us;
        for (std::uint32_t i = 0; i < config::CAL_END_MS + 10; ++i) {
            const auto t = anchor + 100 + i * 1000;
            CHECK_FALSE(sample(t, rate));
            REQUIRE(r.report().fault == Fault::NONE);
            if (r.report().phase == Phase::MEASURING) return t + 1000;
        }
        FAIL("public calibration trace did not finish"); return 0;
    }
    void terminal() {
        auto before = r.report(); before.checkpoint_fresh = before.observation_fresh = false;
        const auto clocks = f.clocks_used, calls = f.starts + f.setups + f.begins + f.advances + f.cancels;
        for (unsigned i = 0; i < 7; ++i) CHECK_FALSE(r.poll());
        CHECK(same(r.report(), before)); CHECK_FALSE(r.begin(granted())); CHECK(same(r.report(), before));
        CHECK(f.clocks_used == clocks); CHECK(f.starts + f.setups + f.begins + f.advances + f.cancels == calls);
    }
};
[[maybe_unused]] void timing(const Timing& t, unsigned calls, unsigned measured, unsigned last, unsigned maximum, bool valid = true) {
    CHECK(t.calls == calls); CHECK(t.measured_calls == measured); CHECK(t.last_us == last);
    CHECK(t.maximum_us == maximum); CHECK(t.last_valid == valid);
}
// One independent mutation for every default Sample/CoherentMotion field category.
[[maybe_unused]] void poison(imu::Sample& s, unsigned i) {
    if (i < 3) { s.motion.accel_raw[i] = 1; return; }
    if (i < 6) { s.motion.gyro_raw[i - 3] = 1; return; }
    if (i < 9) { s.motion.accel_g[i - 6] = 1; return; }
    if (i < 12) { s.motion.gyro_dps[i - 9] = 1; return; }
    switch (i) {
    case 12: s.state = imu::SampleState::NO_NEW; break;
    case 13: s.fault = imu::SampleFault::TRANSPORT; break;
    case 14: s.bus_status = imu::BusStatus::OK; break;
    case 15: s.cleanup = imu::BusCleanup::DISABLED; break;
    case 16: s.error_flags = 1; break;
    case 17: s.sequence = 1; break;
    case 18: s.checked_us = 1; break;
    case 19: s.readiness_completed_us = 1; break;
    case 20: s.motion_started_us = 1; break;
    case 21: s.observation_gap_us = 1; break;
    case 22: s.had_previous_observation = true; break;
    case 23: s.motion.status = imu::DecodeStatus::OK; break;
    case 24: s.motion.temperature_raw = 1; break;
    case 25: s.motion.started_us = 1; break;
    case 26: s.motion.completed_us = 1; break;
    case 27: s.motion.interrupt_status = 1; break;
    case 28: s.motion.rail_mask = 1; break;
    default: s.motion.coherent = true; break;
    }
}
} // namespace

TEST_CASE("D111 passive construction disabled precedence and one attempt") {
    static_assert(!std::is_copy_constructible_v<Runner>);
    static_assert(!std::is_copy_assignable_v<Runner>);
    static_assert(std::is_same_v<decltype(std::declval<const Runner&>().checkpoint(0)), const Checkpoint*>);
    const auto allocations_before = allocations::calls;
    for (unsigned mask = 0; mask < 8; ++mask) {
        Fake f; Runner r(f.port()); CHECK(r.report().phase == Phase::NOT_STARTED);
        CHECK_FALSE(r.poll()); CHECK(f.clocks_used == 0); CHECK(r.checkpointCount() == 0);
        CHECK(r.checkpointCapacity() == config::IMU_BENCH_CHECKPOINTS); CHECK(r.checkpoint(0) == nullptr);
        CHECK(r.checkpoint(UINT32_MAX) == nullptr);
        auto g = granted(); g.enabled = false; g.exclusive_i2c = (mask & 1) != 0;
        g.power_confirmed = (mask & 2) != 0; g.at_rest_confirmed = (mask & 4) != 0;
        g.initial_bias_dps = std::numeric_limits<float>::quiet_NaN();
        { Guard guard; CHECK(r.begin(g)); }
        CHECK(r.report().phase == Phase::DISABLED); const auto before = r.report();
        CHECK_FALSE(r.poll()); CHECK_FALSE(r.begin(granted())); CHECK(same(r.report(), before));
        CHECK(f.clocks_used == 0); CHECK(f.starts == 0);
    }
    Runner empty(Port{}); CHECK(empty.begin(Grants{})); CHECK_FALSE(empty.poll());
    CHECK(empty.report().phase == Phase::DISABLED); CHECK(allocations::calls == allocations_before);
}
TEST_CASE("D111 grants and every missing callback precede native work") {
    for (unsigned mask = 0; mask < 7; ++mask) {
        auto g = granted(); g.exclusive_i2c = (mask & 1) != 0;
        g.power_confirmed = (mask & 2) != 0; g.at_rest_confirmed = (mask & 4) != 0;
        Runner r(Port{}); CHECK_FALSE(r.begin(g)); CHECK(r.report().fault == Fault::GRANT);
    }
    for (unsigned i = 0; i < 6; ++i) {
        Fake f; auto p = f.port();
        switch (i) {
        case 0: p.clockUs = nullptr; break; case 1: p.startSetup = nullptr; break;
        case 2: p.advanceSetup = nullptr; break; case 3: p.beginRead = nullptr; break;
        case 4: p.advanceRead = nullptr; break; default: p.cancelRead = nullptr; break;
        }
        Runner r(p); CHECK_FALSE(r.begin(granted())); CHECK(r.report().fault == Fault::PORT);
        CHECK(f.clocks_used == 0); CHECK(f.starts == 0);
    }
}
TEST_CASE("D111 invalid configuration is passive after grants and ports") {
#ifdef TEST_INVALID_CONFIG
    Rig x; CHECK_FALSE(x.begin()); CHECK(x.r.report().fault == Fault::CONFIG);
    CHECK(x.f.clocks_used == 0); CHECK(x.f.starts == 0); x.terminal();
#elif defined(TEST_ESTIMATOR_CONFIG)
    Rig x; CHECK_FALSE(x.begin()); CHECK(x.r.report().fault == Fault::HEADING);
    CHECK(x.r.report().estimate.fault == imu::HeadingFault::INVALID_CONFIG); CHECK(x.f.clocks_used == 0);
#else
    CHECK(config::IMU_BENCH_CHECKPOINTS > 0);
#endif
}
#if !defined(TEST_INVALID_CONFIG) && !defined(TEST_ESTIMATOR_CONFIG)
TEST_CASE("D111 valid admission copies ports allows null context and validates actual Estimator") {
    Fake f; auto p = f.port(); Runner copied(p); p = {}; f.times(50, 51, 52);
    f.start_result.state = imu::SetupState::IN_PROGRESS; f.start_result.started_us = f.start_result.observed_us = 50;
    CHECK(copied.begin(granted())); CHECK(f.starts == 1); CHECK(f.power); CHECK(f.arguments[0] == 50);
    const auto saved = copied.report(); CHECK_FALSE(copied.begin(Grants{})); CHECK(same(copied.report(), saved));
    static unsigned null_calls = 0;
    Port n; n.clockUs = [](void* context) { CHECK(context == nullptr); ++null_calls; return 0U; };
    n.startSetup = [](void*, std::uint32_t, bool) { imu::SetupReport s; s.state = imu::SetupState::IN_PROGRESS; return s; };
    n.advanceSetup = [](void*, std::uint32_t) { return imu::SetupReport{}; };
    n.beginRead = n.advanceRead = n.cancelRead = [](void*, std::uint32_t) { return imu::SampleProgress{}; };
    Runner null_context(n); CHECK(null_context.begin(granted())); CHECK(null_calls == 3);
    for (unsigned mode = 0; mode < 5; ++mode) {
        Rig x; auto g = granted();
        if (mode == 0) g.mounting.confirmed = false;
        if (mode == 1) g.mounting.body_axis[0] = -1;
        if (mode == 2) g.mounting.body_axis[1] = 1;
        if (mode == 3) g.initial_bias_dps = 1001.0F;
        if (mode == 4) g.initial_bias_dps = std::numeric_limits<float>::quiet_NaN();
        CHECK_FALSE(x.begin(0, g)); CHECK(x.r.report().fault == Fault::HEADING);
        CHECK(x.r.report().estimate.state == imu::HeadingState::FAULT); CHECK(x.f.clocks_used == 0);
    }
}
TEST_CASE("D111 setup grid begins at S and Services anchors only accepted profile C") {
    Rig x; const std::uint32_t base = 0xFFFFFE00U; REQUIRE(x.begin(base));
    CHECK(x.r.report().phase == Phase::SETUP); timing(x.r.report().start_timing, 1, 1, 1, 1);
    CHECK(same(x.r.report().calibration, countdown::ServiceResult{}));
    CHECK_FALSE(x.poll(base + config::TICK_US - 1, 0, 0)); CHECK(x.f.position == 1);
    CHECK(x.r.report().setup_not_due == 1); timing(x.r.report().poll_timing, 1, 0, 0, 0, false);
    x.f.setup_result = x.f.start_result; x.f.setup_result.advances = 1;
    x.f.setup_result.observed_us = base + config::TICK_US;
    CHECK_FALSE(x.poll(base + config::TICK_US, base + config::TICK_US + 7, base + config::TICK_US + 11));
    CHECK(x.r.report().phase == Phase::SETUP); CHECK(x.r.report().missed_setup_releases == 0);
    x.f.setup_result.state = imu::SetupState::PROFILE_READY; x.f.setup_result.bus_status = imu::BusStatus::OK;
    x.f.setup_result.advances = 2; x.f.setup_result.requests = 1;
    x.f.setup_result.observed_us = base + 4 * config::TICK_US + 3;
    CHECK_FALSE(x.poll(base + 4 * config::TICK_US, base + 4 * config::TICK_US + 4, base + 4 * config::TICK_US + 13));
    CHECK(x.r.report().phase == Phase::CALIBRATION); CHECK(x.r.report().missed_setup_releases == 2);
    CHECK(x.r.report().calibration_started_us == base + 4 * config::TICK_US + 13);
    CHECK(same(x.r.report().calibration, countdown::ServiceResult{}));
    CHECK(x.f.setups == 2); timing(x.r.report().setup_timing, 2, 2, 4, 7);
    timing(x.r.report().poll_timing, 3, 2, 13, 13); CHECK_FALSE(x.r.report().clock_fault);
}
TEST_CASE("D111 healthy setup malformed shapes are CONTRACT before A") {
    for (unsigned mutation = 0; mutation < 12; ++mutation) {
        Rig x; REQUIRE(x.begin()); auto& s = x.f.setup_result; s = x.f.start_result;
        s.observed_us = 1000; s.advances = 1;
        switch (mutation) {
        case 0: s.state = imu::SetupState::NOT_STARTED; break;
        case 1: s.state = static_cast<imu::SetupState>(99); break;
        case 2: s.fault = imu::SetupFault::RESPONSE; break;
        case 3: s.started_us = 1; break;
        case 4: s.advances = 0; break;
        case 5: s.advances = 2; break;
        case 6: s.requests = 2; break;
        case 7: s.cleanup = imu::BusCleanup::DISABLED; break;
        case 8: s.error_flags = 1; break;
        case 9: s.bus_status = imu::BusStatus::OK; break;
        case 10: s.state = imu::SetupState::PROFILE_READY; break;
        default: s.bus_status = static_cast<imu::BusStatus>(99); break;
        }
        CHECK_FALSE(x.poll(1000, 999, 1002)); CHECK(x.r.report().fault == Fault::CONTRACT);
        CHECK(x.r.report().clock_fault); CHECK(x.f.position == 2); CHECK(x.f.cancels == 0);
        CHECK(same(x.r.report().setup, s)); x.terminal();
    }
}
TEST_CASE("D111 healthy setup observed source brackets reject SOURCE_ORDER after A") {
    for (auto observed : {999U, 1002U}) {
        Rig x; REQUIRE(x.begin()); x.f.setup_result = x.f.start_result;
        x.f.setup_result.advances = 1; x.f.setup_result.observed_us = observed;
        CHECK_FALSE(x.poll(1000, 1001, 1003)); CHECK(x.r.report().fault == Fault::SOURCE_ORDER);
        CHECK(x.f.position == 3); CHECK_FALSE(x.r.report().clock_fault); CHECK(x.f.cancels == 0);
        timing(x.r.report().setup_timing, 1, 1, 1, 1); timing(x.r.report().poll_timing, 1, 1, 3, 3);
    }
}
TEST_CASE("D111 start malformed and known native setup faults preserve actual evidence") {
    for (unsigned cause = 1; cause <= static_cast<unsigned>(imu::SetupFault::STATUS); ++cause) {
        Fake f; Runner r(f.port()); f.times(5, 6, 9); auto& s = f.start_result;
        s.state = imu::SetupState::FAULT; s.fault = static_cast<imu::SetupFault>(cause);
        s.bus_status = imu::BusStatus::TIMEOUT; s.cleanup = imu::BusCleanup::UNCONFIRMED;
        s.started_us = HALF; s.observed_us = UINT32_MAX; s.requests = UINT32_MAX; s.error_flags = 0x913;
        CHECK_FALSE(r.begin(granted())); CHECK(r.report().fault == Fault::SETUP);
        CHECK(same(r.report().setup, s)); CHECK(f.position == 3); CHECK(f.cancels == 0);
        timing(r.report().start_timing, 1, 1, 1, 1);
    }
    for (unsigned i = 0; i < 10; ++i) {
        Fake f; Runner r(f.port()); f.times(5, 6, 7); auto& s = f.start_result;
        s.state = imu::SetupState::IN_PROGRESS; s.started_us = s.observed_us = 5;
        switch (i) {
        case 0: s.state = imu::SetupState::PROFILE_READY; break;
        case 1: s.started_us = 4; break; case 2: s.observed_us = 6; break;
        case 3: s.advances = 1; break; case 4: s.requests = 1; break;
        case 5: s.bus_status = imu::BusStatus::OK; break; case 6: s.cleanup = imu::BusCleanup::DISABLED; break;
        case 7: s.error_flags = 1; break; case 8: s.fault = imu::SetupFault::TIME_ORDER; break;
        default: s.state = imu::SetupState::FAULT; break;
        }
        CHECK_FALSE(r.begin(granted())); CHECK(r.report().fault == Fault::CONTRACT);
        CHECK(same(r.report().setup, s)); CHECK(f.position == 3);
    }
}
TEST_CASE("D111 release grid permits one pending advance and counts missed starts only at invocation") {
    Rig x; x.ready(); x.startRead(2000); const auto before = x.r.report().calibration;
    for (unsigned i = 0; i < 4; ++i) {
        x.f.advance_result = pending(false); CHECK_FALSE(x.poll(2003 + i * 3, 2004 + i * 3, 2005 + i * 3));
    }
    CHECK(x.f.begins == 1); CHECK(x.f.advances == 4); CHECK(x.r.report().pending_results == 5);
    CHECK(x.r.report().completions == 0); CHECK(same(x.r.report().calibration, before));
    x.f.advance_result = x.absent(2100); CHECK_FALSE(x.poll(2099, 2101, 2102));
    CHECK(x.r.report().no_new == 1); CHECK(x.r.report().observations == 0);
    CHECK_FALSE(x.poll(2999, 0, 0)); CHECK(x.f.position == 1); CHECK(x.r.report().read_not_due == 1);
    x.startRead(6000); CHECK(x.r.report().missed_read_releases == 3); CHECK(x.f.begins == 2);
    CHECK(x.r.report().estimate.gyro_observation == imu::Presence::ABSENT);
}
TEST_CASE("D111 every progress envelope pulse and default payload is enforced") {
    for (unsigned phase = 0; phase < 2; ++phase) for (unsigned state = 0; state < 5; ++state)
        for (unsigned pulses = 0; pulses < 4; ++pulses) {
            const bool valid = state == 1 && pulses == (phase == 0 ? 1U : 0U);
            if (valid) continue;
            Rig x; x.ready(); if (phase) x.startRead(2000);
            imu::SampleProgress p; p.state = static_cast<imu::AsyncState>(state);
            p.started = (pulses & 1) != 0; p.completed = (pulses & 2) != 0;
            (phase ? x.f.advance_result : x.f.begin_result) = p;
            CHECK_FALSE(x.poll(phase ? 2003 : 2000, 2010, 2020));
            CHECK(x.r.report().fault == Fault::CONTRACT); CHECK(x.f.cancels == 1);
            CHECK(same(x.r.report().progress, p)); CHECK(same(x.r.report().cancellation, x.f.cancel_result));
            CHECK(x.f.arguments[4] == 2010); timing(x.r.report().cancel_timing, 1, 1, 10, 10); x.terminal();
        }
    for (unsigned phase = 0; phase < 2; ++phase) for (unsigned field = 0; field < 30; ++field) {
        Rig x; x.ready(); if (phase) x.startRead(2000);
        auto p = pending(phase == 0); poison(p.sample, field);
        (phase ? x.f.advance_result : x.f.begin_result) = p;
        CHECK_FALSE(x.poll(phase ? 2003 : 2000, 2010, 2020));
        CHECK(x.r.report().fault == Fault::CONTRACT); CHECK(x.f.cancels == 1);
        CHECK(x.r.report().pending_results == (phase ? 1U : 0U));
    }
}
TEST_CASE("D111 terminal NO_NEW validates absent payload and shape without replay") {
    for (unsigned i = 0; i < 10; ++i) {
        Rig x; x.ready(); x.startRead(2000); auto p = x.absent(2004);
        switch (i) {
        case 0: p.sample.motion.gyro_raw[1] = 1; break; case 1: p.sample.motion.accel_g[2] = 1; break;
        case 2: p.sample.motion_started_us = 1; break; case 3: p.sample.readiness_completed_us = 2003; break;
        case 4: p.sample.had_previous_observation = true; break; case 5: p.sample.observation_gap_us = 1; break;
        case 6: p.sample.bus_status = imu::BusStatus::NACK; break; case 7: p.sample.cleanup = imu::BusCleanup::DISABLED; break;
        case 8: p.sample.error_flags = 1; break; default: p.sample.fault = imu::SampleFault::RESPONSE; break;
        }
        x.f.advance_result = p; CHECK_FALSE(x.poll(2003, 2005, 2006));
        CHECK(x.r.report().fault == Fault::CONTRACT); CHECK(x.f.cancels == 1);
        CHECK(x.r.report().completions == 0); CHECK(x.r.report().no_new == 0);
    }
}
TEST_CASE("D111 wellformed native faults delivered once with truthful first cause and cleanup") {
    for (unsigned cause = 1; cause <= static_cast<unsigned>(imu::SampleFault::SILENCE); ++cause)
        for (bool begin_fault : {false, true}) for (bool bad_a : {false, true}) {
            Rig x; x.ready(); if (!begin_fault) x.startRead(2000);
            auto p = nativeFault(static_cast<imu::SampleFault>(cause));
            (begin_fault ? x.f.begin_result : x.f.advance_result) = p;
            const auto s = x.r.report().calibration_started_us + config::CAL_START_MS * 1000U;
            CHECK_FALSE(x.poll(s, bad_a ? s - 1 : s + 1, s + 2));
            CHECK(x.r.report().fault == Fault::SOURCE); CHECK(x.r.report().clock_fault == bad_a);
            CHECK(x.r.report().completions == 1); CHECK(x.f.cancels == 0);
            CHECK(same(x.r.report().progress, p)); CHECK(x.r.report().observations == 0);
            CHECK(x.f.position == (bad_a ? 2U : 3U));
            if (!bad_a) {
                CHECK(x.r.report().estimate.fault == imu::HeadingFault::SOURCE);
                CHECK(x.r.report().estimate.acquisition_fault == static_cast<imu::SampleFault>(cause));
                CHECK(x.r.report().calibration.active); // Proves mandatory real Services delivery.
            } else CHECK(same(x.r.report().calibration, countdown::ServiceResult{}));
            x.terminal();
        }
}
TEST_CASE("D111 malformed apparent native fault cannot establish neutral cleanup") {
    for (unsigned i = 0; i < 9; ++i) {
        Rig x; x.ready(); x.startRead(2000); auto p = nativeFault();
        switch (i) {
        case 0: p.completed = false; break; case 1: p.started = true; break;
        case 2: p.sample.fault = imu::SampleFault::NONE; break;
        case 3: p.sample.fault = static_cast<imu::SampleFault>(99); break;
        case 4: p.sample.cleanup = static_cast<imu::BusCleanup>(99); break;
        case 5: p.sample.bus_status = static_cast<imu::BusStatus>(99); break;
        case 6: p.sample.motion.accel_raw[1] = 1; break; case 7: p.sample.readiness_completed_us = 1; break;
        default: p.sample.had_previous_observation = true; break;
        }
        x.f.advance_result = p; CHECK_FALSE(x.poll(2003, 2002, 2006));
        CHECK(x.r.report().fault == Fault::CONTRACT); CHECK(x.r.report().clock_fault);
        CHECK(x.f.cancels == 1); CHECK(x.f.arguments[4] == 2003);
        CHECK(x.r.report().completions == 0); timing(x.r.report().cancel_timing, 1, 0, 0, 0, false);
    }
}
TEST_CASE("D111 observation source bracket validation precedes pure consumers") {
    for (unsigned i = 0; i < 8; ++i) {
        Rig x; x.ready(); x.startRead(2000); auto p = x.observation(2004);
        switch (i) {
        case 0: p.sample.checked_us = 2002; p.sample.motion.completed_us = 2002; break;
        case 1: p.sample.checked_us = 2006; p.sample.motion.completed_us = 2006; break;
        case 2: p.sample.motion.started_us = 1999; break;
        case 3: p.sample.readiness_completed_us = 1999; break;
        case 4: p.sample.readiness_completed_us = 2003; break;
        case 5: p.sample.motion_started_us = 2005; break;
        case 6: p.sample.motion.completed_us = 2003; break;
        default: p.sample.motion.started_us = 2004 - config::IMU_I2C_TRANSFER_US; break;
        }
        x.f.advance_result = p; CHECK_FALSE(x.poll(2003, 2005, 2008));
        CHECK(x.r.report().fault == Fault::SOURCE_ORDER); CHECK(x.f.cancels == 1);
        CHECK(x.r.report().estimate.state == imu::HeadingState::WAITING);
        CHECK(x.r.report().observations == 0); CHECK(x.f.arguments[4] == 2005);
    }
}
TEST_CASE("D111 real heading payload and sequence faults occur after neutral source completion") {
    for (unsigned i = 0; i < 9; ++i) {
        Rig x; x.ready(); x.startRead(2000); auto p = x.observation(2004);
        switch (i) {
        case 0: p.sample.sequence = 2; break; case 1: p.sample.had_previous_observation = true; break;
        case 2: p.sample.motion.coherent = false; break; case 3: p.sample.motion.status = imu::DecodeStatus::RESPONSE; break;
        case 4: p.sample.motion.gyro_dps[1] = std::numeric_limits<float>::quiet_NaN(); break;
        case 5: p.sample.motion.accel_g[2] = 9; break; case 6: p.sample.motion.rail_mask = 64; break;
        case 7: p.sample.motion.interrupt_status = 2; break; default: p.sample.motion.gyro_dps[2] = 1001; break;
        }
        x.f.advance_result = p; CHECK_FALSE(x.poll(2003, 2005, 2006));
        CHECK(x.r.report().fault == Fault::HEADING); CHECK(x.f.cancels == 0);
        CHECK(x.r.report().estimate.state == imu::HeadingState::FAULT);
        CHECK(x.r.report().completions == 1); CHECK(x.r.report().observations == 0);
        CHECK_FALSE(x.r.report().observation_fresh); CHECK(x.r.report().maximum_observation_gap_us == 0);
    }
}
TEST_CASE("D111 bad S A C clocks suppress later clocks and use actual historical cancellation timestamp") {
    for (unsigned clock_index = 0; clock_index < 3; ++clock_index) for (bool half : {false, true}) {
        Rig x; x.ready(); x.startRead(2000); x.f.advance_result = pending(false);
        std::uint32_t s = 2003, a = 2004, c = 2005;
        if (clock_index == 0) s = half ? 2002 + HALF : 2001;
        if (clock_index == 1) a = half ? s + HALF : s - 1;
        if (clock_index == 2) c = half ? a + HALF : a - 1;
        CHECK_FALSE(x.poll(s, a, c)); CHECK(x.r.report().fault == Fault::CLOCK);
        CHECK(x.r.report().clock_fault); CHECK(x.f.cancels == 1); CHECK(x.f.position == clock_index + 1);
        CHECK(x.f.arguments[4] == (clock_index == 0 ? 2002 : clock_index == 1 ? s : a));
        CHECK(x.f.advances == (clock_index == 0 ? 0U : 1U));
        CHECK(x.r.report().pending_results == (clock_index == 0 ? 1U : 2U));
        CHECK_FALSE(x.r.report().poll_timing.last_valid); CHECK_FALSE(x.r.report().cancel_timing.last_valid);
        x.terminal();
    }
}
TEST_CASE("D111 saved completion visible at A and bad A cancels while bad C after neutral does not") {
    for (bool bad_a : {false, true}) {
        Rig x; x.ready(); x.startRead(2000); x.f.advance_result = x.observation(2004);
        x.f.watching = &x.r; x.f.inspect_a = true;
        CHECK_FALSE(x.poll(2003, bad_a ? 2002 : 2005, 2004));
        CHECK(x.f.saw_saved_result); CHECK(same(x.r.report().progress, x.f.advance_result));
        CHECK(x.r.report().fault == Fault::CLOCK); CHECK(x.r.report().completions == 1);
        CHECK(x.f.cancels == (bad_a ? 1U : 0U)); CHECK(x.r.report().observations == 0);
        CHECK(x.r.report().estimate.heading_updated == !bad_a); CHECK_FALSE(x.r.report().observation_fresh);
    }
}
TEST_CASE("D111 S A C deadline equality retains failed-poll timing and truthful cleanup") {
    const auto deadline = config::IMU_BENCH_DEADLINE_US;
    for (unsigned point = 0; point < 3; ++point) for (bool pending_read : {false, true}) {
        Rig x; x.ready(); if (pending_read) x.startRead(2000);
        x.f.advance_result = pending(false);
        const auto s = point == 0 ? deadline : deadline - 2;
        const auto a = point == 0 ? deadline + 3 : point == 1 ? deadline : deadline - 1;
        const auto c = point == 2 ? deadline : deadline + 4;
        CHECK_FALSE(x.poll(s, a, c)); CHECK(x.r.report().fault == Fault::DEADLINE);
        CHECK_FALSE(x.r.report().clock_fault); CHECK(x.r.report().phase == Phase::FAULT);
        const bool cancelled = pending_read || point != 0;
        CHECK(x.f.cancels == (cancelled ? 1U : 0U));
        CHECK(x.f.position == (point == 0 ? 2U : 3U));
        CHECK(x.r.report().poll_timing.last_valid);
        CHECK(x.r.report().poll_timing.last_us == (point == 0 ? a - s : c - s));
        if (cancelled) {
            CHECK(x.f.arguments[4] == (point == 0 ? s : point == 1 ? a : c));
            CHECK(x.r.report().cancel_timing.last_valid == (point != 2));
        }
        x.terminal();
    }
}
TEST_CASE("D111 A deadline still admits bounded pure terminal diagnostics without successful publication") {
    for (bool native_fault : {false, true}) {
        Rig x; x.ready(); const auto d = config::IMU_BENCH_DEADLINE_US;
        x.startRead(d - 10); x.f.advance_result = native_fault ? nativeFault() : x.observation(d - 1);
        CHECK_FALSE(x.poll(d - 2, d, d + 1));
        CHECK(x.r.report().fault == (native_fault ? Fault::SOURCE : Fault::DEADLINE));
        CHECK(x.f.cancels == 0); CHECK(x.r.report().completions == 1);
        CHECK(x.r.report().estimate.state == (native_fault ? imu::HeadingState::FAULT : imu::HeadingState::READY));
        CHECK(x.r.report().calibration.calibration_finished); CHECK(x.r.report().calibration.calibration_rejected);
        CHECK(x.r.report().observations == 0); CHECK_FALSE(x.r.report().observation_fresh);
        CHECK_FALSE(x.r.report().measurement.anchored); CHECK(x.r.checkpointCount() == 0);
    }
}
TEST_CASE("D111 accumulated lifetime half-range cannot alias before deadline diagnosis") {
    Rig x; REQUIRE(x.begin());
    CHECK_FALSE(x.poll(HALF / 2, HALF, HALF + 1));
    CHECK(x.r.report().fault == Fault::DEADLINE); CHECK(x.r.report().clock_fault);
    CHECK(x.f.position == 2); CHECK(x.f.setups == 0); CHECK_FALSE(x.r.report().poll_timing.last_valid);
}
TEST_CASE("D111 exact heading gap and completed NO_NEW retain heading without refreshing observations") {
    for (unsigned gap : {2000U, 2001U}) {
        Rig x; x.ready(); CHECK_FALSE(x.sample(2000));
        const auto before = x.r.report().estimate; x.startRead(2000 + gap);
        x.f.advance_result = x.absent(2004 + gap); CHECK_FALSE(x.poll(2003 + gap, 2005 + gap, 2006 + gap));
        CHECK(x.f.cancels == 0);
        if (gap == 2000) {
            CHECK(x.r.report().fault == Fault::NONE); CHECK(x.r.report().estimate.heading_available);
            CHECK_FALSE(x.r.report().estimate.heading_updated); CHECK(x.r.report().estimate.heading_age_us == gap);
            CHECK(x.r.report().estimate.observation_us == before.observation_us);
            CHECK(x.r.report().estimate.heading_deg == before.heading_deg); CHECK(x.r.report().no_new == 1);
            CHECK(x.r.report().estimate.gyro_observation == imu::Presence::ABSENT);
        } else { CHECK(x.r.report().fault == Fault::HEADING); CHECK(x.r.report().estimate.fault == imu::HeadingFault::GAP); }
        CHECK(x.r.report().observations == 1); CHECK_FALSE(x.r.report().observation_fresh);
    }
}
TEST_CASE("D111 calibration raw bias application retains prior corrected evidence and no yaw reset") {
    Rig x; const auto next = x.calibrate(); const auto after = x.r.report();
    CHECK(after.calibration.calibration_finished); CHECK_FALSE(after.calibration.calibration_rejected);
    CHECK(after.calibration.calibration_samples == config::CAL_END_MS - config::CAL_START_MS);
    CHECK(after.bias_applied); CHECK(after.accepted_bias_dps == 2.0F); CHECK(after.estimate.bias_dps == 2.0F);
    CHECK(after.estimate.raw_gyro_z_dps == 2.0F); CHECK(after.estimate.gyro_z_dps == 1.5F);
    CHECK(after.estimate.heading_deg == doctest::Approx((x.sequence - 1) * 0.0015).epsilon(0.00001));
    CHECK(after.estimate.heading_deg > 0); CHECK_FALSE(after.measurement.anchored); CHECK(x.r.checkpointCount() == 0);
    REQUIRE(x.sample(next, 2.0F)); CHECK(x.r.checkpointCount() == 1);
    CHECK(x.r.report().estimate.gyro_z_dps == 0); CHECK(x.r.report().estimate.heading_deg == after.estimate.heading_deg);
    CHECK(same(x.r.report().calibration, after.calibration)); CHECK(x.r.report().measurement.delta_deg == 0);
    REQUIRE(x.r.checkpoint(0)); CHECK(x.r.checkpoint(0)->sample.sequence == after.estimate.sequence + 1);
}
TEST_CASE("D111 synthetic proper mounting is passed to the same actual Estimator") {
    Rig x; auto g = granted(); g.mounting.body_axis[0] = -1; g.mounting.body_axis[2] = -3;
    g.initial_bias_dps = 0.5F; x.ready(0, g); CHECK_FALSE(x.sample(2000, 2));
    CHECK(x.r.report().estimate.raw_gyro_z_dps == -2); CHECK(x.r.report().estimate.gyro_z_dps == -2.5F);
    CHECK(x.r.report().estimate.ax_g == -0.25F); CHECK(x.r.report().estimate.ay_g == -0.5F);
    CHECK_FALSE(x.sample(3000, 4)); CHECK(x.r.report().estimate.raw_gyro_z_dps == -4);
    CHECK(x.r.report().estimate.heading_deg == doctest::Approx(-0.0035).epsilon(0.00001));
}
TEST_CASE("D111 linear rate ramp follows analytic trapezoid area and absent measurement is unchanged") {
    Rig x; const auto next = x.calibrate(); REQUIRE(x.sample(next, 2));
    for (unsigned i = 1; i <= 1000; ++i) {
        x.sample(next + i * 1000, 2 + i * 0.25F); REQUIRE(x.r.report().fault == Fault::NONE);
        CHECK(x.r.report().measurement.delta_deg == doctest::Approx(i * i * 0.000125).epsilon(0.00003));
    }
    const auto measurement = x.r.report().measurement; const auto observations = x.r.report().observations;
    CHECK_FALSE(x.sample(next + 1001000, 0, true)); CHECK(x.r.report().fault == Fault::NONE);
    CHECK(same(x.r.report().measurement, measurement)); CHECK(x.r.report().observations == observations);
    CHECK_FALSE(x.r.report().observation_fresh); CHECK(x.r.report().no_new == 1);
}
TEST_CASE("D111 rejected closing C retains actual accepted bias but publishes no successful observation") {
    Rig x; auto g = granted(); g.initial_bias_dps = 0.5F; x.ready(0, g);
    const auto anchor = x.r.report().calibration_started_us;
    for (unsigned i = 0; i < config::CAL_END_MS; ++i) {
        CHECK_FALSE(x.sample(anchor + 100 + i * 1000)); REQUIRE(x.r.report().fault == Fault::NONE);
    }
    const auto before = x.r.report(); const auto s = anchor + 100 + config::CAL_END_MS * 1000;
    x.startRead(s); x.f.advance_result = x.observation(s + 4);
    CHECK_FALSE(x.poll(s + 3, s + 5, s + 4)); CHECK(x.r.report().fault == Fault::CLOCK);
    CHECK(x.r.report().bias_applied); CHECK(x.r.report().accepted_bias_dps == 2);
    CHECK(x.r.report().estimate.bias_dps == 2); CHECK(x.r.report().estimate.gyro_z_dps == 1.5F);
    CHECK(x.r.report().calibration.calibration_finished); CHECK(x.r.report().observations == before.observations);
    CHECK_FALSE(x.r.report().observation_fresh); CHECK(x.r.checkpointCount() == 0); CHECK(x.f.cancels == 0);
}
TEST_CASE("D111 absence only closes calibration rejected without invented samples") {
    Rig x; auto g = granted(); g.initial_bias_dps = 0.75F; x.ready(0, g);
    const auto a = x.r.report().calibration_started_us;
    CHECK_FALSE(x.sample(a + config::CAL_START_MS * 1000, 0, true));
    CHECK_FALSE(x.sample(a + config::CAL_END_MS * 1000, 0, true));
    CHECK(x.r.report().fault == Fault::CALIBRATION); CHECK(x.r.report().calibration.calibration_finished);
    CHECK(x.r.report().calibration.calibration_rejected); CHECK(x.r.report().calibration.calibration_samples == 0);
    CHECK(x.r.report().calibration.bias_dps == 0.75F); CHECK_FALSE(x.r.report().bias_applied);
    CHECK(x.r.report().no_new == 1); CHECK(x.r.report().completions == 2); CHECK(x.f.cancels == 0);
}
TEST_CASE("D111 calibration source versus delivery boundary and age use real reports") {
    for (unsigned age : {0U, 1U, 2000U, 2001U}) {
        Rig x; x.ready(); const auto window = x.r.report().calibration_started_us + config::CAL_START_MS * 1000;
        const auto source = age < 2 ? window - age : window;
        x.startRead(source - 4); x.f.advance_result = x.observation(source);
        CHECK_FALSE(x.poll(source, source + age, source + age));
        CHECK(x.r.report().fault == Fault::NONE); CHECK(x.r.report().estimate.heading_updated);
        CHECK(x.r.report().calibration.calibration_samples == ((age == 0 || age == 2000) ? 1U : 0U));
    }
}
TEST_CASE("D111 sixty second analytic constant trace publishes all immutable source checkpoints") {
    const auto heap_before = allocations::calls;
    for (std::uint32_t origin : {0U, 0xFF000000U}) {
        Rig x; const auto next = x.calibrate(2, 0.5F, origin); REQUIRE(x.sample(next, 8));
        const auto first = *x.r.checkpoint(0); const auto frozen_cal = x.r.report().calibration;
        std::array<Checkpoint, config::IMU_BENCH_CHECKPOINTS> saved{}; saved[0] = first;
        unsigned stored = 1;
        for (std::uint32_t n = 1; n <= config::IMU_BENCH_TRIAL_US / 1000; ++n) {
            const bool fresh = x.sample(next + n * 1000, 8);
            REQUIRE(x.r.report().fault == Fault::NONE); CHECK(x.r.report().observation_fresh);
            CHECK(fresh == (n % (config::IMU_BENCH_CHECKPOINT_US / 1000) == 0));
            CHECK(x.r.report().measurement.delta_deg == doctest::Approx(n * 0.006).epsilon(0.00003));
            if (fresh) {
                REQUIRE(x.r.checkpoint(stored)); const auto& p = *x.r.checkpoint(stored);
                CHECK(p.elapsed_source_us == stored * config::IMU_BENCH_CHECKPOINT_US);
                CHECK(p.sample.checked_us == next + n * 1000 + 4); CHECK(p.delivered_us == p.sample.checked_us + 1);
                CHECK(p.closed_us == p.delivered_us + 1); CHECK(same(p.sample, x.f.advance_result.sample));
                CHECK(same(p.estimate, x.r.report().estimate)); saved[stored++] = p;
                for (unsigned j = 0; j < stored; ++j) CHECK(same(*x.r.checkpoint(j), saved[j]));
            }
        }
        CHECK(x.r.report().phase == Phase::COMPLETE); CHECK(stored == config::IMU_BENCH_CHECKPOINTS);
        CHECK(x.r.report().measurement.observations == config::IMU_BENCH_TRIAL_US / 1000 + 1);
        CHECK(x.r.report().measurement.elapsed_us == config::IMU_BENCH_TRIAL_US);
        CHECK(x.r.report().measurement.minimum_delta_deg == 0);
        CHECK(x.r.report().measurement.maximum_delta_deg == x.r.report().measurement.delta_deg);
        CHECK(x.r.report().measurement.maximum_absolute_excursion_deg == x.r.report().measurement.delta_deg);
        CHECK(x.r.report().maximum_observation_gap_us == 1000); CHECK(same(x.r.report().calibration, frozen_cal));
        CHECK(x.r.checkpoint(stored) == nullptr); CHECK_FALSE(x.r.report().counter_saturated); x.terminal();
        for (unsigned j = 0; j < stored; ++j) CHECK(same(*x.r.checkpoint(j), saved[j]));
    }
    CHECK(allocations::calls == heap_before);
}
TEST_CASE("D111 analytic reversing ramp exposes excursion when endpoint returns near anchor") {
    Rig x; const auto next = x.calibrate(); REQUIRE(x.sample(next, 2));
    const double start = x.r.report().estimate.heading_deg; double expected = 0, minimum = 0, maximum = 0;
    double previous = 0; const auto total = config::IMU_BENCH_TRIAL_US / 1000;
    for (std::uint32_t i = 1; i <= total; ++i) {
        const double rate = i <= total / 2 ? 6.0 : -6.0;
        expected += (previous + rate) * 0.0005; previous = rate;
        minimum = std::fmin(minimum, expected); maximum = std::fmax(maximum, expected);
        x.sample(next + i * 1000, static_cast<float>(rate + 2));
        REQUIRE(x.r.report().fault == Fault::NONE);
    }
    CHECK(x.r.report().phase == Phase::COMPLETE);
    CHECK(x.r.report().measurement.delta_deg == doctest::Approx(expected).epsilon(0.001));
    CHECK(x.r.report().measurement.maximum_delta_deg == doctest::Approx(maximum).epsilon(0.00001));
    CHECK(x.r.report().measurement.minimum_delta_deg == doctest::Approx(minimum).epsilon(0.001));
    CHECK(x.r.report().measurement.maximum_absolute_excursion_deg > 100);
    CHECK(std::fabs(x.r.report().measurement.delta_deg) < 0.01); CHECK(start > 0);
}
TEST_CASE("D111 nondivisible observation cadence retains real endpoint overshoot and first boundary samples") {
    Rig x; const auto next = x.calibrate(); REQUIRE(x.sample(next, 5));
    const auto count = (config::IMU_BENCH_TRIAL_US + 1699) / 1700;
    for (std::uint32_t i = 1; i <= count; ++i) { x.sample(next + i * 1700, 5); REQUIRE(x.r.report().fault == Fault::NONE); }
    CHECK(x.r.report().phase == Phase::COMPLETE); CHECK(x.r.checkpointCount() == config::IMU_BENCH_CHECKPOINTS);
    CHECK(x.r.report().measurement.elapsed_us == count * 1700);
    for (std::uint32_t k = 0; k < x.r.checkpointCount(); ++k) {
        const auto threshold = k * config::IMU_BENCH_CHECKPOINT_US;
        CHECK(x.r.checkpoint(k)->elapsed_source_us == ((threshold + 1699) / 1700) * 1700);
    }
}
TEST_CASE("D111 failed final closing clock hides staged slot and preserves all prior checkpoints") {
    Rig x; const auto next = x.calibrate(); REQUIRE(x.sample(next, 2));
    std::array<Checkpoint, config::IMU_BENCH_CHECKPOINTS> saved{}; saved[0] = *x.r.checkpoint(0);
    for (std::uint32_t i = 1; i < config::IMU_BENCH_TRIAL_US / 1000; ++i) {
        if (x.sample(next + i * 1000, 3)) saved[x.r.checkpointCount() - 1] = *x.r.checkpoint(x.r.checkpointCount() - 1);
        REQUIRE(x.r.report().fault == Fault::NONE);
    }
    const auto before = x.r.report(); const auto s = next + config::IMU_BENCH_TRIAL_US;
    x.startRead(s); x.f.advance_result = x.observation(s + 4, 3);
    CHECK_FALSE(x.poll(s + 3, s + 5, s + 4)); CHECK(x.r.report().fault == Fault::CLOCK);
    CHECK(x.r.checkpointCount() == config::IMU_BENCH_CHECKPOINTS - 1);
    CHECK(x.r.checkpoint(config::IMU_BENCH_CHECKPOINTS - 1) == nullptr);
    CHECK(same(x.r.report().measurement, before.measurement)); CHECK(x.r.report().observations == before.observations);
    CHECK(x.r.report().estimate.heading_updated); CHECK_FALSE(x.r.report().observation_fresh); CHECK(x.f.cancels == 0);
    x.terminal(); for (unsigned j = 0; j < x.r.checkpointCount(); ++j) CHECK(same(*x.r.checkpoint(j), saved[j]));
}
#ifdef TEST_SHORT_CAL
TEST_CASE("D111 short public calibration profile exact two minimum spread and absence") {
    for (unsigned mode = 0; mode < 4; ++mode) {
        Rig x; auto g = granted(); g.initial_bias_dps = 0.5F; x.ready(0, g);
        const auto anchor = x.r.report().calibration_started_us;
        // Source is one us before each decision. First source precedes the window.
        CHECK_FALSE(x.sample(anchor + 995, 2)); CHECK(x.r.report().calibration.calibration_samples == 0);
        CHECK_FALSE(x.sample(anchor + 1995, 2)); CHECK(x.r.report().calibration.calibration_samples == 1);
        CHECK_FALSE(x.sample(anchor + 2995, mode == 1 ? 4.0001F : 4.0F, mode == 2));
        if (mode == 3) {
            x.startRead(anchor + 3995); x.f.advance_result = nativeFault();
            CHECK_FALSE(x.poll(anchor + 3998, anchor + 4000, anchor + 4001));
            CHECK(x.r.report().fault == Fault::SOURCE); CHECK(x.r.report().calibration.calibration_finished);
            CHECK(x.r.report().calibration.bias_dps == 3); CHECK(x.f.cancels == 0); continue;
        }
        CHECK_FALSE(x.sample(anchor + 3995, 2, true));
        const bool accepted = mode == 0;
        CHECK(x.r.report().fault == (accepted ? Fault::NONE : Fault::CALIBRATION));
        CHECK(x.r.report().calibration.calibration_finished); CHECK(x.r.report().bias_applied == accepted);
        CHECK(x.r.report().calibration.calibration_samples == (mode == 2 ? 1U : 2U));
        CHECK(x.r.report().calibration.bias_dps == (accepted ? 3.0F : 0.5F));
    }
}
#endif
#ifdef TEST_LIMIT
TEST_CASE("D111 finite poll budget equality permits last poll then historical cancellation with no clock") {
    Rig x; x.ready(); x.startRead(2000);
    while (x.r.report().admitted_polls < config::IMU_BENCH_MAX_POLLS) {
        x.f.advance_result = pending(false); CHECK_FALSE(x.poll(2003, 2003, 2003));
        REQUIRE(x.r.report().fault == Fault::NONE);
    }
    const auto clock_count = x.f.clocks_used, advance_count = x.f.advances;
    CHECK_FALSE(x.r.poll()); CHECK(x.r.report().fault == Fault::LIMIT);
    CHECK(x.r.report().admitted_polls == config::IMU_BENCH_MAX_POLLS);
    CHECK(x.r.report().poll_timing.calls == config::IMU_BENCH_MAX_POLLS + 1);
    CHECK(x.f.clocks_used == clock_count); CHECK(x.f.advances == advance_count); CHECK(x.f.cancels == 1);
    CHECK(x.f.arguments[4] == 2003); CHECK_FALSE(x.r.report().poll_timing.last_valid);
    timing(x.r.report().cancel_timing, 1, 0, 0, 0, false); x.terminal();
}
#endif
#endif // valid configuration

#ifdef TEST_NATIVE_BINDING
namespace native_test {
unsigned clocks = 0, calls[5] = {}; imu::Acquirer* identity = nullptr; bool same_owner = true;
std::uint32_t args[5] = {}; bool power = false;
imu::SetupReport setup_reply;
imu::SampleProgress reply;
void called(imu::Acquirer* object, unsigned i, std::uint32_t now) {
    if (identity && identity != object) same_owner = false;
    identity = object; ++calls[i]; args[i] = now;
}
}
unsigned long micros() { ++native_test::clocks; return 0xABCDEF12UL; }
namespace imu {
SetupReport Acquirer::start(std::uint32_t now, bool confirmed) {
    native_test::called(this, 0, now); native_test::power = confirmed; return native_test::setup_reply;
}
SetupReport Acquirer::advanceSetup(std::uint32_t now) {
    native_test::called(this, 1, now); return native_test::setup_reply;
}
SampleProgress Acquirer::beginRead(std::uint32_t now) {
    native_test::called(this, 2, now); return native_test::reply;
}
SampleProgress Acquirer::advanceRead(std::uint32_t now) {
    native_test::called(this, 3, now); return native_test::reply;
}
SampleProgress Acquirer::cancelRead(std::uint32_t now) {
    native_test::called(this, 4, now); return native_test::reply;
}
} // namespace imu
TEST_CASE("D111 Native direct callbacks preserve exact results arguments and single owner") {
    static_assert(!std::is_copy_constructible_v<imu_heading_bench::Native>);
    const auto heaps = allocations::calls; const auto before = native_test::clocks;
    imu_heading_bench::Native n; const auto p = n.port(); const auto q = n.port();
    CHECK(native_test::clocks == before); CHECK(p.context == q.context);
    CHECK((p.clockUs && p.startSetup && p.advanceSetup && p.beginRead && p.advanceRead && p.cancelRead));
    native_test::setup_reply.state = imu::SetupState::FAULT; native_test::setup_reply.fault = imu::SetupFault::TRANSPORT;
    native_test::setup_reply.started_us = 0xFEDCBA98U; native_test::setup_reply.error_flags = 0x19U;
    native_test::reply = nativeFault(); native_test::identity = nullptr; native_test::same_owner = true;
    { Guard guard;
      CHECK(p.clockUs(p.context) == 0xABCDEF12U);
      CHECK(same(p.startSetup(p.context, 11, false), native_test::setup_reply));
      CHECK(same(p.advanceSetup(p.context, 22), native_test::setup_reply));
      CHECK(same(p.beginRead(p.context, 33), native_test::reply));
      CHECK(same(p.advanceRead(p.context, 44), native_test::reply));
      CHECK(same(p.cancelRead(p.context, 55), native_test::reply)); }
    CHECK_FALSE(native_test::power); CHECK(native_test::same_owner); REQUIRE(native_test::identity);
    for (unsigned i = 0; i < 5; ++i) CHECK(native_test::args[i] == 11 * (i + 1));
    CHECK(allocations::calls == heaps);
}
TEST_CASE("D111 default sketch setup and ten thousand loops remain entirely silent") {
    const auto clocks = native_test::clocks; unsigned calls[5];
    for (unsigned i = 0; i < 5; ++i) calls[i] = native_test::calls[i];
    const auto heaps = allocations::calls;
    { Guard guard; setup(); for (unsigned i = 0; i < 10000; ++i) loop(); }
    CHECK(native_test::clocks == clocks);
    for (unsigned i = 0; i < 5; ++i) CHECK(native_test::calls[i] == calls[i]);
    CHECK(allocations::calls == heaps);
}
#endif

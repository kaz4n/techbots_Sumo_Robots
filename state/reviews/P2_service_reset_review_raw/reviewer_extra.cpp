// Independently probes D103 fault transitions through the public real owners.
// No private state or synthetic reset receipt can create service authority.
// Run under ASan/UBSan in copied configured-button source, both motor modes.
#include "doctest.h"
#include "fixtures/app_service_reset/fixture.h"
#include <cstdio>

using namespace service_reset_test;
#define RV_CHECK(...) do { const bool ok = (__VA_ARGS__); CHECK_MESSAGE(ok, #__VA_ARGS__); if (!ok) return; } while (false)

namespace {
void zero(const Rig& rig, unsigned highs, unsigned pulses) {
    CHECK_FALSE(rig.fake.enabled);
    CHECK(rig.fake.highs == highs); CHECK(rig.fake.nonzero == pulses);
    for (const auto pulse : rig.fake.pulses) CHECK(pulse == 0U);
    CHECK(rig.fake.enable_setups == 1U); CHECK(rig.fake.pwm_setups == 4U);
    CHECK(rig.fake.adc_setups == 1U); CHECK(rig.fake.opp_setups == 1U);
    CHECK(rig.fake.line_setups == 1U);
}
void terminal(Rig& rig) {
    const auto calls = rig.fake.count, clocks = rig.fake.clocks;
    const auto reads = rig.sink.readies, writes = rig.sink.writes, cancels = rig.sink.cancels;
    const auto token = rig.owner.report().reset_from_token;
    for (unsigned i = 0; i < 4; ++i) {
        CHECK_FALSE(rig.owner.step()); rig.owner.abort();
        CHECK_FALSE(rig.owner.report().service_reset_fresh);
        CHECK_FALSE(rig.owner.report().service_action.fresh);
    }
    CHECK(rig.fake.count == calls); CHECK(rig.fake.clocks == clocks);
    CHECK(rig.sink.readies == reads); CHECK(rig.sink.writes == writes);
    CHECK(rig.sink.cancels == cancels); CHECK(rig.owner.report().reset_from_token == token);
}
}

TEST_CASE("B3 B14 D103 review injects each clock position across pending reset epoch") {
    unsigned faults = 0U, after_reset = 0U;
    for (unsigned position = 1U; position <= 24U; ++position) {
        CAPTURE(position); Rig rig; RV_CHECK(rig.stopped()); RV_CHECK(rig.pending());
        const auto starts = rig.fake.line_starts, advances = rig.fake.line_advances;
        const auto highs = rig.fake.highs, pulses = rig.fake.nonzero;
        const auto release_token = rig.robot().token;
        rig.fake.clock_reversal_countdown = position;
        rig.next(); zero(rig, highs, pulses);
        CHECK(rig.fake.line_starts == starts); CHECK(rig.fake.line_advances == advances);
        if (rig.owner.report().service_reset_fresh) {
            ++after_reset; CHECK(rig.owner.report().service_only);
            CHECK(rig.owner.report().reset_from_token == release_token);
        }
        if (rig.owner.report().phase == app::RuntimePhase::FAULT) {
            ++faults; CHECK_FALSE(rig.owner.report().service_reset_pending);
            terminal(rig);
        } else if (position == 1U) {
            // Returning one microsecond before the due slot is a valid early call.
            CHECK(rig.owner.report().phase == app::RuntimePhase::STOP_OBSERVING);
            CHECK(rig.owner.report().service_reset_pending);
            CHECK_FALSE(rig.owner.report().service_only);
        } else {
            CHECK(rig.owner.report().phase == app::RuntimePhase::RUNNING);
            CHECK(rig.owner.report().service_only);
        }
    }
    CHECK(faults >= 5U); CHECK(after_reset >= 5U);
    std::printf("review reset clock sweep: 24 positions, %u terminal failures, %u actual resets\n", faults, after_reset);
}

TEST_CASE("B3 B13 B14 D103 review retained service source failures are terminal and passive") {
    for (unsigned fault = 0U; fault < 8U; ++fault) {
        CAPTURE(fault); Rig rig; RV_CHECK(rig.reset()); RV_CHECK(rig.run(30U));
        const auto highs = rig.fake.highs, pulses = rig.fake.nonzero;
        const auto starts = rig.fake.line_starts, advances = rig.fake.line_advances;
        if (fault == 0U) rig.fake.buttons_failure = true;
        if (fault == 1U) rig.fake.adc_failure = true;
        if (fault >= 2U && fault <= 5U) rig.fake.opponent_error = fault - 1U;
        if (fault == 6U) rig.fake.button_raw = 16000U;
        if (fault == 7U) rig.fake.reverse_matrix = true;
        for (unsigned tick = 0; tick < 25U && rig.owner.report().phase != app::RuntimePhase::FAULT; ++tick)
            rig.next();
        CHECK(rig.owner.report().phase == app::RuntimePhase::FAULT);
        CHECK(rig.owner.report().service_only); CHECK_FALSE(rig.owner.report().service_reset_pending);
        CHECK(rig.fake.line_starts == starts); CHECK(rig.fake.line_advances == advances);
        zero(rig, highs, pulses); terminal(rig);
    }
}

TEST_CASE("B13 D103 review unavailable flag preserves every noncalibration display pixel") {
    for (unsigned state = 0U; state <= static_cast<unsigned>(core::State::DRIVE_TEST); ++state)
        for (unsigned service = 1U; service <= 4U; ++service)
            for (unsigned mask : {0U, 1U, 42U, 127U}) {
                ui::DisplaySample plain; plain.state = static_cast<core::State>(state);
                plain.service_menu = true; plain.service = static_cast<countdown::Service>(service);
                plain.faults = static_cast<std::uint8_t>(mask); plain.battery_available = true;
                plain.battery_v = 11.1F; plain.opponents_available = true; plain.opponent_mask = 0x55U;
                auto unavailable = plain; unavailable.service_unavailable = true;
                ui::Frame a, b; const auto ra = ui::render(plain, a), rb = ui::render(unavailable, b);
                CHECK(ra == rb);
                const bool selected = plain.state == core::State::IDLE &&
                    plain.service == countdown::Service::QTR_CAL;
                for (unsigned y = 0; y < 8; ++y) for (unsigned x = 0; x < 13; ++x)
                    if (!selected || !(x >= 4U && x <= 8U && y >= 1U && y <= 5U))
                        CHECK(a.pixels[y * 13U + x] == b.pixels[y * 13U + x]);
            }
}

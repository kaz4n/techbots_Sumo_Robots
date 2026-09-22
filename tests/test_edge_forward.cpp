// Checks B4.2/D-021 forward escape demands and their B6 final electrical envelope.
// Keeps the requested inner-side bias separate from capped duty and physical curvature.
// Run with tools/test_host.sh; contracts and approved equations define expectations.
#include "doctest.h"
#include "config.h"
#include "core/edge.h"
#include "core/governor.h"
#include <algorithm>
#include <cstdint>
#include <initializer_list>

namespace {
using edge::ForwardBias;

governor::Request forwardRequest(ForwardBias bias, float voltage = config::V_NOM_V) {
    const auto demand = edge::forwardDemand(bias);
    governor::Request request;
    request.duty_l = demand.duty_l;
    request.duty_r = demand.duty_r;
    request.profile = governor::Profile::EDGE_FORWARD;
    request.vbat_v = voltage;
    request.inhibited = !demand.valid;
    return request;
}

void checkZero(const governor::Result& result) {
    CHECK(result.valid);
    CHECK(result.duty_l == 0.0F);
    CHECK(result.duty_r == 0.0F);
}

governor::Result settled(governor::Request request) {
    governor::Governor governor;
    checkZero(governor.step(0U, request));
    return governor.step(100000U, request);
}
} // namespace

TEST_CASE("B4.2 forward demands are 0.80 straight and mirrored 0.56 inner-side requests") {
    const edge::ForwardDemand initial;
    CHECK_FALSE(initial.valid);
    CHECK(initial.duty_l == 0.0F);
    CHECK(initial.duty_r == 0.0F);
    CHECK(config::EDGE_BACK_DUTY == doctest::Approx(0.80F));
    CHECK(config::EDGE_FWD_INNER_RATIO == doctest::Approx(0.70F));
    const auto straight = edge::forwardDemand(ForwardBias::NONE);
    const auto left = edge::forwardDemand(ForwardBias::LEFT);
    const auto right = edge::forwardDemand(ForwardBias::RIGHT);
    CHECK(straight.valid);
    CHECK(left.valid);
    CHECK(right.valid);
    CHECK(straight.duty_l == doctest::Approx(0.80F));
    CHECK(straight.duty_r == doctest::Approx(0.80F));
    CHECK(left.duty_l == doctest::Approx(0.56F));
    CHECK(left.duty_r == doctest::Approx(0.80F));
    CHECK(right.duty_l == doctest::Approx(0.80F));
    CHECK(right.duty_r == doctest::Approx(0.56F));
    CHECK(left.duty_l == right.duty_r);
    CHECK(left.duty_r == right.duty_l);
    CHECK(left.duty_l / left.duty_r == doctest::Approx(0.70F));
}

TEST_CASE("B4.2 every unknown forward bias returns invalid zero demand") {
    for (unsigned value = 3U; value <= 255U; ++value) {
        CAPTURE(value);
        const auto demand = edge::forwardDemand(static_cast<ForwardBias>(value));
        CHECK_FALSE(demand.valid);
        CHECK(demand.duty_l == 0.0F);
        CHECK(demand.duty_r == 0.0F);
    }
}

TEST_CASE("B4.2/B6 EDGE_FORWARD final cap is 0.80 at 9 11.1 and 12.6 V") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        for (unsigned flags = 0U; flags < 4U; ++flags) {
            auto request = forwardRequest(ForwardBias::NONE, voltage);
            request.duty_l = request.duty_r = 1.0F;
            request.centered = (flags & 1U) != 0U;
            request.contact = (flags & 2U) != 0U;
            const auto result = settled(request);
            CHECK(result.valid);
            CHECK(result.duty_l == doctest::Approx(0.80F));
            CHECK(result.duty_r == doctest::Approx(0.80F));
            CHECK(result.duty_l <= config::EDGE_BACK_DUTY);
            CHECK(result.duty_r <= config::EDGE_BACK_DUTY);
        }
    }
}

TEST_CASE("B4.2/B6 compensation and per-side caps preserve mirror symmetry not a fixed ratio") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        CAPTURE(voltage);
        for (auto bias : {ForwardBias::NONE, ForwardBias::LEFT, ForwardBias::RIGHT}) {
            const auto request = forwardRequest(bias, voltage);
            const auto result = settled(request);
            const float requested_l = bias == ForwardBias::LEFT ? 0.56F : 0.80F;
            const float requested_r = bias == ForwardBias::RIGHT ? 0.56F : 0.80F;
            CHECK(result.valid);
            CHECK(result.duty_l == doctest::Approx(
                std::min(0.80F, requested_l * 11.1F / voltage)));
            CHECK(result.duty_r == doctest::Approx(
                std::min(0.80F, requested_r * 11.1F / voltage)));
        }
        const auto left = settled(forwardRequest(ForwardBias::LEFT, voltage));
        const auto right = settled(forwardRequest(ForwardBias::RIGHT, voltage));
        CHECK(left.duty_l == doctest::Approx(right.duty_r));
        CHECK(left.duty_r == doctest::Approx(right.duty_l));
        if (voltage == 9.0F) {
            CHECK(left.duty_l == doctest::Approx(0.6906666667F));
            CHECK(left.duty_r == doctest::Approx(0.80F));
            CHECK(left.duty_l / left.duty_r == doctest::Approx(0.8633333333F));
        } else {
            CHECK(left.duty_l / left.duty_r == doctest::Approx(0.70F));
        }
    }
}

TEST_CASE("B4.2/B6 forward requests use elapsed-time slew on final electrical duty") {
    for (float voltage : {9.0F, 11.1F, 12.6F}) {
        for (auto bias : {ForwardBias::NONE, ForwardBias::LEFT, ForwardBias::RIGHT}) {
            const auto request = forwardRequest(bias, voltage);
            for (auto elapsed : {999U, 1000U, 1001U}) {
                governor::Governor governor;
                checkZero(governor.step(0U, request));
                const auto result = governor.step(elapsed, request);
                const float expected = config::SLEW_DUTY_PER_MS *
                    static_cast<float>(elapsed) / 1000.0F;
                CHECK(result.duty_l == doctest::Approx(expected));
                CHECK(result.duty_r == doctest::Approx(expected));
            }
            governor::Governor governor;
            auto previous = governor.step(0U, request);
            for (std::uint32_t t = 1000U; t <= 100000U; t += 1000U) {
                const auto result = governor.step(t, request);
                CHECK(result.duty_l >= previous.duty_l);
                CHECK(result.duty_r >= previous.duty_r);
                CHECK(result.duty_l - previous.duty_l <=
                      config::SLEW_DUTY_PER_MS + 0.000001F);
                CHECK(result.duty_r - previous.duty_r <=
                      config::SLEW_DUTY_PER_MS + 0.000001F);
                CHECK(result.duty_l <= config::EDGE_BACK_DUTY);
                CHECK(result.duty_r <= config::EDGE_BACK_DUTY);
                previous = result;
            }
        }
    }
}

TEST_CASE("B4.2/B6 zero brake and inhibit stop forward duty immediately without slew") {
    for (unsigned stop_kind = 0U; stop_kind < 3U; ++stop_kind) {
        governor::Governor governor;
        const auto moving = forwardRequest(ForwardBias::LEFT);
        governor.step(0U, moving);
        const auto active = governor.step(100000U, moving);
        CHECK(active.duty_l > 0.0F);
        CHECK(active.duty_r > 0.0F);
        auto stopping = moving;
        if (stop_kind == 0U) stopping.duty_l = stopping.duty_r = 0.0F;
        if (stop_kind == 1U) stopping.brake = true;
        if (stop_kind == 2U) stopping.inhibited = true;
        checkZero(governor.step(100000U, stopping));
        checkZero(governor.step(100000U, moving));
        const auto restart = governor.step(101000U, moving);
        CHECK(restart.duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
        CHECK(restart.duty_r == doctest::Approx(config::SLEW_DUTY_PER_MS));
    }
}

TEST_CASE("B4.2/B6 changing reverse escape to forward brakes before positive slew") {
    for (auto bias : {ForwardBias::NONE, ForwardBias::LEFT, ForwardBias::RIGHT}) {
        governor::Governor governor;
        auto reverse = forwardRequest(ForwardBias::NONE);
        reverse.profile = governor::Profile::EDGE_REVERSE;
        reverse.duty_l = reverse.duty_r = -config::EDGE_BACK_DUTY;
        governor.step(0U, reverse);
        const auto backward = governor.step(100000U, reverse);
        CHECK(backward.duty_l < 0.0F);
        CHECK(backward.duty_r < 0.0F);
        const auto forward = forwardRequest(bias);
        checkZero(governor.step(101000U, forward));
        const auto restart = governor.step(102000U, forward);
        CHECK(restart.duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
        CHECK(restart.duty_r == doctest::Approx(config::SLEW_DUTY_PER_MS));
    }
}

TEST_CASE("B4.2/B6 forward escape cap immediately reduces previous full ATTACK duty") {
    governor::Governor governor;
    auto attack = forwardRequest(ForwardBias::NONE, 9.0F);
    attack.profile = governor::Profile::ATTACK;
    attack.centered = attack.contact = true;
    attack.duty_l = attack.duty_r = 1.0F;
    governor.step(0U, attack);
    const auto full = governor.step(100000U, attack);
    CHECK(full.duty_l == doctest::Approx(1.0F));
    CHECK(full.duty_r == doctest::Approx(1.0F));
    const auto escape = governor.step(100000U, forwardRequest(ForwardBias::NONE, 9.0F));
    CHECK(escape.duty_l == doctest::Approx(0.80F));
    CHECK(escape.duty_r == doctest::Approx(0.80F));
}

TEST_CASE("B2/B4.2/B6 guard inhibition overrides forward demands and retains all-white zero") {
    for (auto bias : {ForwardBias::NONE, ForwardBias::LEFT, ForwardBias::RIGHT}) {
        edge::Guard guard;
        governor::Governor governor;
        auto request = forwardRequest(bias);
        request.inhibited = guard.step(8U, false, false).inhibit_motion;
        CHECK(request.inhibited);
        checkZero(governor.step(0U, request));
        checkZero(governor.step(100000U, request));
        const auto permitted = guard.step(8U, true, false);
        CHECK(permitted.escape_required);
        CHECK_FALSE(permitted.inhibit_motion);
        request.inhibited = permitted.inhibit_motion;
        const auto moving = governor.step(200000U, request);
        CHECK(moving.duty_l > 0.0F);
        CHECK(moving.duty_r > 0.0F);
        const auto fault = guard.step(15U, true, false);
        CHECK(fault.fault_latched);
        CHECK(fault.inhibit_motion);
        request.inhibited = fault.inhibit_motion;
        checkZero(governor.step(201000U, request));
        const auto clear = guard.step(0U, true, true);
        CHECK(clear.fault_latched);
        CHECK(clear.inhibit_motion);
        request.inhibited = clear.inhibit_motion;
        checkZero(governor.step(300000U, request));
        guard.reset();
        request.inhibited = guard.step(0U, true, true).inhibit_motion;
        CHECK_FALSE(request.inhibited);
        checkZero(governor.step(300000U, request));
        const auto restart = governor.step(301000U, request);
        CHECK(restart.duty_l == doctest::Approx(config::SLEW_DUTY_PER_MS));
        CHECK(restart.duty_r == doctest::Approx(config::SLEW_DUTY_PER_MS));
    }
}

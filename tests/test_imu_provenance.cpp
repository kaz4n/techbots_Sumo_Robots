// Verifies D084 source clocks independently of current opponent and event clocks.
// Retained yaw can steer but must not manufacture measurements or refresh history.
// Literal boundaries, wrap streams and all flag bytes exercise the public APIs.
#include "doctest.h"
#include "core/fsm.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
fsm::HeadingSample heading(std::uint32_t tick, float raw, bool fresh,
                           std::uint32_t source) {
    return {tick, raw, true, fresh, source};
}
opp_fusion::FusionSample fusionSample(std::uint32_t time, std::uint8_t mask = 2U) {
    opp_fusion::FusionSample s;
    s.t_us = time; s.raw_mask = static_cast<std::uint8_t>(mask ^ config::OPP_ACTIVE_LOW_MASK);
    s.imu_ok = true; s.explicit_imu = true; s.heading_updated = true;
    s.heading_observation_us = time; s.prior_state = core::State::TRACK;
    return s;
}
void allZero(const logframe::FrameBytes& bytes) {
    for (const auto byte : bytes.data) CHECK(byte == 0U);
}
} // namespace

TEST_CASE("B3 B14 D084 heading source GO distinguishes delayed fresh retained and missing") {
    for (const unsigned mode : {0U, 1U, 2U, 3U}) {
        fsm::HeadingReference reference;
        if (mode != 3U) {
            const auto before = reference.step(heading(1000U, 37.0F, true, 900U));
            CHECK_FALSE(before.imu_ok); CHECK_FALSE(before.heading_updated);
            CHECK(before.observation_us == 900U); CHECK(before.heading_age_us == 100U);
        }
        const auto sample = mode == 0U ? heading(2000U, 40.0F, true, 1900U) :
            mode == 1U ? heading(2000U, 37.0F, false, 900U) :
            fsm::HeadingSample{2000U, std::numeric_limits<float>::quiet_NaN(), false, false, 0U};
        const auto go = reference.step(sample, true);
        CHECK_FALSE(go.fault); CHECK(go.match_started); CHECK(go.origin_changed);
        CHECK(go.heading_deg == 0.0F);
        CHECK(go.imu_ok == (mode < 2U)); CHECK(go.heading_updated == (mode == 0U));
        const auto origin = mode == 0U ? fsm::HeadingOrigin::CURRENT_GO :
            mode == 3U ? fsm::HeadingOrigin::NOMINAL_PENDING : fsm::HeadingOrigin::LAST_KNOWN;
        CHECK(go.origin == origin);
        CHECK(go.origin_t_us == (mode == 0U ? 1900U : mode == 3U ? 2000U : 900U));
        const auto recovered = reference.step(heading(2500U, 42.0F, true, 2400U));
        CHECK(recovered.imu_ok); CHECK(recovered.heading_updated);
        CHECK(recovered.origin_changed == (mode == 3U));
        CHECK(recovered.heading_deg == (mode == 0U ? 2.0F : mode == 3U ? 0.0F : 5.0F));
        CHECK(recovered.origin_t_us == (mode == 0U ? 1900U : mode == 3U ? 2400U : 900U));
    }
}

TEST_CASE("B3 B14 D084 heading duplicates clear pulses without consuming changed input") {
    fsm::HeadingReference reference;
    CHECK(reference.step(heading(100U, 30.0F, true, 90U), true).heading_updated);
    const auto repeat = reference.step({100U, std::numeric_limits<float>::infinity(), true, true, 99U}, true);
    CHECK_FALSE(repeat.fault); CHECK_FALSE(repeat.origin_changed);
    CHECK_FALSE(repeat.heading_updated); CHECK(repeat.imu_ok);
    CHECK(repeat.origin_t_us == 90U); CHECK(repeat.observation_us == 90U);
    CHECK(reference.step(heading(200U, 30.0F, false, 90U)).imu_ok);
    CHECK(reference.worldBearing(15.0F).heading_deg == 15.0F);
    CHECK(reference.projectHeading(35.0F).heading_deg == 5.0F);
}

TEST_CASE("B3 B14 D084 heading source admission exact age ordering and retained identity") {
    for (unsigned mutation = 0; mutation < 11U; ++mutation) {
        fsm::HeadingReference reference;
        CHECK_FALSE(reference.step(heading(1000U, 10.0F, true, 900U)).fault);
        auto next = heading(1100U, 11.0F, true, 1000U);
        switch (mutation) {
        case 0: next.observation_us = 900U; break;
        case 1: next.observation_us = 899U; break;
        case 2: next.observation_us = 900U + 0x80000000U; break;
        case 3: next.observation_us = 1101U; break;
        case 4: next.t_us = 3001U; next.observation_us = 1000U; break;
        case 5: next.updated = false; break;
        case 6: next.updated = false; next.observation_us = 900U; break;
        case 7: next.available = false; break;
        case 8: next.raw_heading_deg = std::numeric_limits<float>::quiet_NaN(); break;
        case 9: next.updated = false; next.observation_us = 900U; next.raw_heading_deg = 10.0F; next.t_us = 2901U; break;
        default: reference.reset(); next.updated = false; break;
        }
        const auto rejected = reference.step(next);
        CHECK(rejected.fault); CHECK_FALSE(rejected.imu_ok);
        CHECK_FALSE(reference.worldBearing(0.0F).valid);
        CHECK(reference.step(heading(4000U, 12.0F, true, 4000U)).fault);
        reference.reset();
        CHECK_FALSE(reference.step(heading(3000U, 20.0F, true, 1000U), true).fault);
    }
}

TEST_CASE("B3 B14 D084 heading wrap and accumulated history prevent source resurrection") {
    fsm::HeadingReference reference;
    CHECK(reference.step(heading(0xfffffff0U, 10.0F, true, 0xfffffff0U), true).imu_ok);
    const auto wrapped = reference.step(heading(0x10U, 11.0F, true, 0U));
    CHECK(wrapped.imu_ok); CHECK(wrapped.heading_age_us == 16U);
    CHECK(reference.step(heading(2000U, 11.0F, false, 0U)).imu_ok);
    reference.reset();
    reference.step(heading(100U, 10.0F, true, 100U), true);
    reference.step({0x80000064U, 0.0F, false, false, 0U});
    const auto absent = reference.step({99U, 0.0F, false, false, 0U});
    CHECK(absent.heading_age_us == 0xffffffffU);
    const auto resurrect = reference.step(heading(101U, 10.0F, false, 100U));
    CHECK(resurrect.fault); CHECK_FALSE(resurrect.imu_ok);
}

TEST_CASE("B5 B14 D084 fusion impact is fresh acceleration independent of retained yaw") {
    for (const bool accel : {false, true}) for (const bool fresh : {false, true}) {
        opp_fusion::Fusion fusion;
        auto s = fusionSample(1000U); s.accel_valid = accel; s.heading_updated = fresh;
        s.ax_g = 2.0F; s.heading_observation_us = 500U;
        fusion.observe(s); fusion.commit(core::State::TRACK);
        s.t_us = 2000U;
        const auto seen = fusion.observe(s);
        CHECK(seen.cue.impact_cue == accel);
        CHECK(seen.bearing.world_valid);
        CHECK(seen.bearing.heading_observation_us == 500U);
        CHECK(fusion.memory().world_heading_us == 500U);
        CHECK(fusion.memory().last_seen_us == 2000U);
        CHECK(fusion.commit(core::State::ATTACK).result.contact == accel);
    }
    opp_fusion::Fusion fusion;
    for (unsigned i = 0; i <= config::CONTACT_TICKS; ++i) {
        auto s = fusionSample(1000U + i * 1000U, 7U);
        s.imu_ok = false; s.heading_updated = false; s.ax_g = 5.0F;
        const auto observed = fusion.observe(s);
        CHECK_FALSE(observed.cue.impact_cue);
        if (i == config::CONTACT_TICKS) CHECK(observed.cue.close_cue);
        fusion.commit(core::State::ATTACK);
    }
}

TEST_CASE("B5 D084 stuck begins with fresh yaw and declares on qualified retained tick") {
    opp_fusion::StuckFilter stuck;
    CHECK(stuck.step(0U, 2U, -1000.0F, true, false).fault_mask == 0U);
    CHECK(stuck.step(5000000U, 2U, 1000.0F, true, false).fault_mask == 0U);
    CHECK(stuck.step(5001000U, 2U, 0.0F, true, true).fault_mask == 0U);
    CHECK(stuck.step(5002000U, 2U, 361.0F, true, true).fault_mask == 0U);
    CHECK(stuck.step(10000999U, 2U, 361.0F, true, false).fault_mask == 0U);
    const auto declared = stuck.step(10001000U, 2U, 361.0F, true, false);
    CHECK(declared.new_fault_mask == 2U); CHECK(declared.filtered_mask == 0U);
    CHECK(stuck.step(10002000U, 0U, 0.0F, false, false).fault_mask == 2U);
    stuck.reset();
    stuck.step(0U, 2U, 0.0F, true, true);
    stuck.step(1000U, 2U, 361.0F, true, true);
    stuck.step(4999999U, 2U, 361.0F, false, false);
    CHECK(stuck.step(5000000U, 2U, 361.0F, true, false).fault_mask == 0U);
}

TEST_CASE("B5 D084 retained yaw cannot invent stuck extrema or phantom marker") {
    opp_fusion::StuckFilter stuck;
    stuck.step(0U, 2U, 0.0F, true, true);
    CHECK(stuck.step(5000000U, 2U, 1000.0F, true, false).fault_mask == 0U);
    opp_fusion::PhantomFilter filter;
    opp_fusion::PhantomSample s;
    s.state = core::State::TRACK; s.confirmed_mask = 2U;
    s.imu_ok = true; s.heading_updated = false;
    filter.step(s); s.t_us = 1000U; s.edge_event = true;
    CHECK_FALSE(filter.step(s).phantom_set);
    s.t_us = 2000U; s.heading_updated = true;
    CHECK_FALSE(filter.step(s).phantom_set); // The unavailable edge already consumed this chase.
    s.t_us = 3000U; s.state = core::State::SEARCH; s.edge_event = false; filter.step(s);
    s.t_us = 4000U; s.state = core::State::TRACK; filter.step(s);
    s.t_us = 5000U; s.edge_event = true; s.heading_observation_us = 4500U;
    const auto marked = filter.step(s);
    CHECK(marked.phantom_set); CHECK(marked.heading_observation_us == 4500U);
    s.t_us = 6000U; s.edge_event = false; s.heading_updated = false;
    CHECK(filter.step(s).filtered_mask == 0U);
    s.t_us = 3004999U; CHECK(filter.step(s).active);
    s.t_us = 3005000U; CHECK_FALSE(filter.step(s).active);
}

TEST_CASE("B4 B8 D084 escape exit requires fresh inward evidence while retained can steer") {
    for (const bool fresh : {false, true}) {
        edge::Escape escape;
        edge::EscapeSample s;
        s.t_us = 1000U; s.line_mask = 12U; s.imu_ok = true;
        s.motion_permitted = true; s.heading_deg = 20.0F;
        CHECK(escape.step(s).entered);
        s.t_us = 200999U; s.line_mask = 0U; s.heading_updated = fresh;
        const auto moving = escape.step(s);
        CHECK_FALSE(moving.exited); CHECK_FALSE(moving.row.motion.imu_fallback);
        s.t_us = 201000U;
        const auto exit = escape.step(s);
        CHECK(exit.exited); CHECK(exit.inward_valid == fresh);
        CHECK(exit.inward_heading_deg == (fresh ? 20.0F : 0.0F));
    }
}

TEST_CASE("B15 D084 all 256 flags preserve legacy rejection and explicit self identification") {
    CHECK(logframe::FRAME_BYTES == 25U);
    for (unsigned flags = 0U; flags < 256U; ++flags) {
        logframe::FrameInput in; in.flags = static_cast<std::uint8_t>(flags);
        logframe::FrameBytes bytes;
        const auto legacy = logframe::packFrame(in, bytes);
        CHECK(legacy == (flags < 16U ? logframe::PackStatus::OK : logframe::PackStatus::INVALID));
        if (flags >= 16U) allZero(bytes);
        in.explicit_imu = true;
        const bool valid = ((flags >> 4U) & 3U) != 0U && ((flags >> 6U) & 3U) != 0U;
        CHECK(logframe::packFrame(in, bytes) == (valid ? logframe::PackStatus::OK : logframe::PackStatus::INVALID));
        if (valid) CHECK(bytes.data[22] == flags); else allZero(bytes);
    }
}

TEST_CASE("B15 D084 absent invalid sensor payload must be canonical zero and measured zero remains valid") {
    for (unsigned gyro = 1U; gyro <= 3U; ++gyro) for (unsigned accel = 1U; accel <= 3U; ++accel) {
        for (const float value : {1.0F, -1.0F, std::numeric_limits<float>::quiet_NaN(),
                                  std::numeric_limits<float>::infinity()}) {
            for (unsigned field = 0; field < 3U; ++field) {
                logframe::FrameInput in; in.explicit_imu = true;
                in.flags = static_cast<std::uint8_t>((gyro << 4U) | (accel << 6U));
                if (field == 0U) in.gyro_z_dps = value;
                if (field == 1U) in.ax_g = value;
                if (field == 2U) in.ay_g = value;
                logframe::FrameBytes out;
                const bool valid = (field == 0U ? gyro == 2U : accel == 2U) && std::isfinite(value);
                CHECK(logframe::packFrame(in, out) == (valid ? logframe::PackStatus::OK : logframe::PackStatus::INVALID));
                if (!valid) allZero(out);
            }
        }
    }
    logframe::FrameInput in; in.explicit_imu = true; in.flags = 0xa1U;
    in.heading_deg = 12.34F; in.gyro_z_dps = -12.3F; in.ax_g = 1.25F; in.ay_g = -2.5F;
    logframe::FrameBytes out;
    CHECK(logframe::packFrame(in, out) == logframe::PackStatus::OK);
    CHECK(out.data[8] == 0xd2U); CHECK(out.data[9] == 0x04U);
    CHECK(out.data[12] == 0x85U); CHECK(out.data[13] == 0xffU);
    CHECK(out.data[14] == 0xe2U); CHECK(out.data[15] == 0x04U);
    CHECK(out.data[16] == 0x3cU); CHECK(out.data[17] == 0xf6U);
    CHECK(out.data[22] == 0xa1U);
}

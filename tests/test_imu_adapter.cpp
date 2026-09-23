// Checks D084 mapping solely against the frozen report and public header contract.
// Invalid HAL evidence must stay explicit and never change unrelated Robot fields.
// Independent exhaustive mutations and actual Estimator streams run on the host.
#include "doctest.h"
#include "hal/imu_adapter.h"
#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
imu::Estimate ready(bool updated = true) {
    imu::Estimate e;
    e.state = imu::HeadingState::READY;
    e.heading_available = true;
    e.heading_updated = updated;
    e.gyro_observation = updated ? imu::Presence::VALID : imu::Presence::ABSENT;
    e.accel_observation = updated ? imu::Presence::VALID : imu::Presence::ABSENT;
    e.heading_deg = 12.5F;
    e.checked_us = 5000U;
    e.observation_us = updated ? 5000U : 4000U;
    e.heading_age_us = updated ? 0U : 1000U;
    e.sequence = 9U;
    if (updated) { e.raw_gyro_z_dps = 20.0F; e.gyro_z_dps = 18.0F; e.ax_g = 1.0F; e.ay_g = -2.0F; }
    e.bias_dps = 2.0F;
    return e;
}
fsm::RobotInput sentinel() {
    fsm::RobotInput input;
    input.t_us = 6000U;
    input.initialization_complete = true;
    input.observations_fresh = true;
    for (unsigned i = 0; i < 4U; ++i) input.line_raw_us[i] = 200U + i;
    input.opp_raw_mask = 0x2aU;
    input.button = core::ButtonLevel::BOTH;
    input.stop_requested = true;
    input.vbat_valid = true;
    input.vbat_v = 11.4F;
    input.reset_cause = fsm::ResetCause::WATCHDOG;
    input.previous = {true, 77U, 4000U, true, 0.1F, -0.2F, true, 4500U, 500U};
    return input;
}
void unchanged(const fsm::RobotInput& in) {
    CHECK(in.t_us == 6000U);
    CHECK(in.initialization_complete);
    CHECK(in.observations_fresh);
    for (unsigned i = 0; i < 4U; ++i) CHECK(in.line_raw_us[i] == 200U + i);
    CHECK(in.opp_raw_mask == 0x2aU);
    CHECK(in.button == core::ButtonLevel::BOTH);
    CHECK(in.stop_requested);
    CHECK(in.vbat_valid);
    CHECK(in.vbat_v == 11.4F);
    CHECK(in.reset_cause == fsm::ResetCause::WATCHDOG);
    CHECK(in.previous.applied_valid);
    CHECK(in.previous.token == 77U);
    CHECK(in.previous.applied_us == 4000U);
    CHECK(in.previous.motors_enabled);
    CHECK(in.previous.duty_l == 0.1F);
    CHECK(in.previous.duty_r == -0.2F);
    CHECK(in.previous.duration_valid);
    CHECK(in.previous.completed_us == 4500U);
    CHECK(in.previous.execution_us == 500U);
}
void rejected(const imu::Estimate& e) {
    auto in = sentinel();
    CHECK_FALSE(imu::applyEstimate(in, e));
    unchanged(in);
    CHECK(in.imu.explicit_values);
    CHECK_FALSE(in.imu.contract_valid);
    CHECK_FALSE(in.imu_ok);
    CHECK(in.raw_heading_deg == 0.0F);
    CHECK(in.raw_gyro_z_dps == 0.0F);
    CHECK(in.ax_g == 0.0F);
    CHECK(in.ay_g == 0.0F);
    CHECK(in.previous_bias_dps == 0.0F);
}
} // namespace

TEST_CASE("B3 B14 D084 adapter maps actual finite fresh and retained report fields") {
    for (const bool updated : {false, true}) {
        const auto e = ready(updated);
        auto in = sentinel();
        CHECK(imu::applyEstimate(in, e));
        unchanged(in);
        CHECK(in.imu.explicit_values);
        CHECK(in.imu.contract_valid);
        CHECK(in.imu.heading_available);
        CHECK(in.imu.heading_updated == updated);
        CHECK(in.imu.checked_us == e.checked_us);
        CHECK(in.imu.observation_us == e.observation_us);
        CHECK(in.imu.sequence == e.sequence);
        CHECK(in.imu.gyro == (updated ? core::ImuPresence::VALID : core::ImuPresence::ABSENT));
        CHECK(in.imu.accel == (updated ? core::ImuPresence::VALID : core::ImuPresence::ABSENT));
        CHECK(in.raw_heading_deg == e.heading_deg);
        CHECK(in.raw_gyro_z_dps == e.raw_gyro_z_dps);
        CHECK(in.ax_g == e.ax_g);
        CHECK(in.ay_g == e.ay_g);
        CHECK(in.previous_bias_dps == e.bias_dps);
    }
}

TEST_CASE("B3 B14 D084 adapter distinguishes default waiting and each terminal fault") {
    for (const auto state : {imu::HeadingState::NOT_STARTED, imu::HeadingState::WAITING}) {
        imu::Estimate e;
        e.state = state;
        if (state == imu::HeadingState::WAITING) { e.checked_us = 777U; e.bias_dps = 2.0F; }
        auto in = sentinel();
        CHECK(imu::applyEstimate(in, e));
        unchanged(in);
        CHECK(in.imu.gyro == core::ImuPresence::ABSENT);
        CHECK(in.imu.accel == core::ImuPresence::ABSENT);
        CHECK_FALSE(in.imu.heading_available);
        CHECK_FALSE(in.imu.heading_updated);
    }
    for (unsigned code = 1U; code <= static_cast<unsigned>(imu::HeadingFault::NUMERIC); ++code) {
        imu::Estimate e;
        e.state = imu::HeadingState::FAULT;
        e.fault = static_cast<imu::HeadingFault>(code);
        e.gyro_observation = e.accel_observation = imu::Presence::INVALID;
        e.sequence = 77U; e.checked_us = 888U; e.bias_dps = -3.0F;
        if (e.fault == imu::HeadingFault::SOURCE) e.acquisition_fault = imu::SampleFault::SILENCE;
        auto in = sentinel();
        CHECK(imu::applyEstimate(in, e));
        CHECK(in.imu.gyro == core::ImuPresence::INVALID);
        CHECK(in.imu.accel == core::ImuPresence::INVALID);
        CHECK_FALSE(in.imu.heading_available);
        unchanged(in);
    }
}

TEST_CASE("B3 B14 D084 adapter rejects every unknown enum and malformed presence pair") {
    for (unsigned code = 0U; code < 256U; ++code) {
        if (code > 3U) { auto e = ready(); e.state = static_cast<imu::HeadingState>(code); rejected(e); }
        if (code > 11U) { auto e = ready(); e.fault = static_cast<imu::HeadingFault>(code); rejected(e); }
        if (code > 6U) { auto e = ready(); e.acquisition_fault = static_cast<imu::SampleFault>(code); rejected(e); }
        if (code > 2U) {
            auto e = ready(); e.gyro_observation = static_cast<imu::Presence>(code); rejected(e);
            e = ready(); e.accel_observation = static_cast<imu::Presence>(code); rejected(e);
        }
    }
    for (unsigned gyro = 0; gyro < 3U; ++gyro) for (unsigned accel = 0; accel < 3U; ++accel) {
        auto e = ready(); e.gyro_observation = static_cast<imu::Presence>(gyro);
        e.accel_observation = static_cast<imu::Presence>(accel);
        if (accel == 2U) e.ax_g = e.ay_g = 0.0F;
        if (gyro == 1U && accel != 0U) { auto in = sentinel(); CHECK(imu::applyEstimate(in, e)); }
        else rejected(e);
    }
}

TEST_CASE("B3 B14 D084 adapter validates canonical inactive shapes without trusting flags") {
    for (unsigned mutation = 0U; mutation < 18U; ++mutation) {
        imu::Estimate e;
        e.state = imu::HeadingState::WAITING;
        switch (mutation) {
        case 0: e.heading_available = true; break;
        case 1: e.heading_updated = true; break;
        case 2: e.heading_deg = 1.0F; break;
        case 3: e.raw_gyro_z_dps = 1.0F; break;
        case 4: e.gyro_z_dps = 1.0F; break;
        case 5: e.ax_g = 1.0F; break;
        case 6: e.ay_g = 1.0F; break;
        case 7: e.observation_us = 1U; break;
        case 8: e.heading_age_us = 1U; break;
        case 9: e.sequence = 1U; break;
        case 10: e.fault = imu::HeadingFault::BIAS; break;
        case 11: e.acquisition_fault = imu::SampleFault::SILENCE; break;
        case 12: e.gyro_observation = imu::Presence::VALID; break;
        case 13: e.accel_observation = imu::Presence::INVALID; break;
        case 14: e.bias_dps = std::numeric_limits<float>::infinity(); break;
        case 15: e.bias_dps = 1000.01F; break;
        case 16: e.state = imu::HeadingState::NOT_STARTED; e.checked_us = 1U; break;
        default: e.state = imu::HeadingState::NOT_STARTED; e.bias_dps = 1.0F; break;
        }
        rejected(e);
    }
    imu::Estimate fault;
    fault.state = imu::HeadingState::FAULT;
    fault.gyro_observation = fault.accel_observation = imu::Presence::INVALID;
    rejected(fault);
    fault.fault = imu::HeadingFault::SOURCE; rejected(fault);
    fault.fault = imu::HeadingFault::GAP;
    fault.acquisition_fault = imu::SampleFault::SILENCE; rejected(fault);
}

TEST_CASE("B3 B14 D084 adapter checks exact bounds and permits post applyBias historical fields") {
    for (const float sign : {-1.0F, 1.0F}) {
        auto e = ready(); e.raw_gyro_z_dps = sign * 1000.0F; e.gyro_z_dps = sign * 2000.0F;
        e.ax_g = sign * 8.0F; e.ay_g = -sign * 8.0F; e.bias_dps = sign * 1000.0F;
        auto in = sentinel(); CHECK(imu::applyEstimate(in, e));
        e.raw_gyro_z_dps = sign * 1000.01F; rejected(e);
        e = ready(); e.gyro_z_dps = sign * 2000.01F; rejected(e);
        e = ready(); e.ax_g = sign * 8.001F; rejected(e);
        e = ready(); e.ay_g = sign * 8.001F; rejected(e);
    }
    for (const float invalid : {std::numeric_limits<float>::quiet_NaN(),
                               std::numeric_limits<float>::infinity(),
                               -std::numeric_limits<float>::infinity()}) {
        for (unsigned field = 0; field < 6U; ++field) {
            auto e = ready();
            if (field == 0U) e.heading_deg = invalid;
            if (field == 1U) e.raw_gyro_z_dps = invalid;
            if (field == 2U) e.gyro_z_dps = invalid;
            if (field == 3U) e.ax_g = invalid;
            if (field == 4U) e.ay_g = invalid;
            if (field == 5U) e.bias_dps = invalid;
            rejected(e);
        }
    }
    auto e = ready(); e.bias_dps = 12.0F;
    auto in = sentinel(); CHECK(imu::applyEstimate(in, e));
    e = ready(false); e.checked_us = 50U; e.observation_us = 0xfffff862U;
    e.heading_age_us = 2000U; CHECK(imu::applyEstimate(in, e));
    e.heading_age_us = 1999U; rejected(e);
    e.heading_age_us = 2001U; e.observation_us -= 1U; rejected(e);
    e = ready(); e.checked_us += 1U; e.heading_age_us = 1U; rejected(e);
    e = ready(false); e.raw_gyro_z_dps = 0.01F; rejected(e);
    e = ready(false); e.gyro_z_dps = 0.01F; rejected(e);
    e = ready(false); e.ax_g = 0.01F; rejected(e);
    e = ready(); e.accel_observation = imu::Presence::INVALID; rejected(e);
}

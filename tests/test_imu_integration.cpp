// Drives the actual D084 Robot path using independently prepared evidence and receipts.
// Source identities, fresh acceleration and retained yaw must preserve safety priority.
// Analytic cases plus seeded actual Estimator streams test public behavior only.
#include "robot_scenario.h"
#include "hal/imu_adapter.h"
#include <initializer_list>
#include <limits>

namespace {
using Presence = core::ImuPresence;
using Button = core::ButtonLevel;
using State = core::State;
class ExplicitRig : public robot_test::Rig {
public:
    ExplicitRig() { input.imu.explicit_values = true; input.imu_ok = false; }
    fsm::RobotResult fresh(std::uint32_t t, float yaw = 0.0F,
                          Button button = Button::NONE, std::uint32_t age = 0U) {
        input.imu = {true, true, Presence::VALID, acceleration, true, true, t - age, t - age, ++sequence};
        input.raw_heading_deg = yaw;
        return step(t, button);
    }
    fsm::RobotResult retained(std::uint32_t t, Button button = Button::NONE) {
        input.imu.gyro = input.imu.accel = Presence::ABSENT;
        input.imu.heading_updated = false; input.imu.checked_us = t;
        return step(t, button);
    }
    fsm::RobotResult absent(std::uint32_t t, bool invalid = false) {
        input.imu = {true, true, invalid ? Presence::INVALID : Presence::ABSENT,
            invalid ? Presence::INVALID : Presence::ABSENT, false, false, 0U, 0U, 0U};
        return step(t);
    }
    std::uint32_t release(bool direct = false) {
        fresh(0U); fresh(1000U); fresh(21000U);
        std::uint32_t base = 21000U;
        if (direct) for (unsigned i = 0; i < 2U; ++i) {
            fresh(base + 1U, 0.0F, Button::MODE);
            fresh(base + 20001U, 0.0F, Button::MODE);
            fresh(base + 20002U); fresh(base + 40002U); base += 40002U;
        }
        fresh(base + 1000U, 0.0F, Button::START);
        fresh(base + 21000U, 0.0F, Button::START);
        fresh(base + 22000U); fresh(base + 41999U);
        CHECK(fresh(base + 42000U).lifecycle.gate.start_release);
        return base + 42000U;
    }
    std::uint32_t go(bool direct = false) {
        const auto start = release(direct);
        fresh(start + 1500000U); fresh(start + 1501000U); fresh(start + 4500000U);
        robot_test::zero(fresh(start + 5099999U));
        CHECK(fresh(start + 5100000U).lifecycle.gate.go);
        CHECK(last.contract_faults == 0U);
        return start + 5100000U;
    }
    std::uint32_t sequence = 0;
    Presence acceleration = Presence::VALID;
};
void contractFault(const fsm::RobotResult& result) {
    CHECK((result.contract_faults & fsm::HEADING_CONTRACT) != 0U);
    CHECK(result.outputs.ui_state == State::STOPPED);
    robot_test::zero(result);
}
imu::Sample observation(std::uint32_t time, std::uint32_t seq, bool previous,
                        std::uint32_t gap, float gyro = 0.0F) {
    imu::Sample s;
    s.state = imu::SampleState::OBSERVATION; s.bus_status = imu::BusStatus::OK;
    s.sequence = seq; s.checked_us = time; s.had_previous_observation = previous;
    s.observation_gap_us = gap; s.motion.status = imu::DecodeStatus::OK;
    s.motion.coherent = true; s.motion.started_us = s.motion.completed_us = time;
    s.motion.gyro_dps[2] = gyro;
    return s;
}
} // namespace

TEST_CASE("B3 B14 D084 Robot admits all presence shapes without using legacy imu_ok") {
    robot_test::Rig legacy;
    legacy.input.imu.contract_valid = false;
    contractFault(legacy.step(1000U));
    for (unsigned gyro = 0; gyro < 256U; ++gyro) {
        ExplicitRig rig;
        rig.input.imu.gyro = static_cast<Presence>(gyro);
        const auto result = rig.step(1000U);
        if (gyro == 1U) CHECK(result.contract_faults == 0U); else contractFault(result);
    }
    for (unsigned accel = 0; accel < 256U; ++accel) {
        ExplicitRig rig;
        rig.acceleration = static_cast<Presence>(accel);
        const auto result = rig.fresh(1000U);
        if (accel == 2U || accel == 3U) CHECK(result.contract_faults == 0U); else contractFault(result);
    }
    for (const bool invalid : {false, true}) {
        ExplicitRig rig;
        rig.input.raw_heading_deg = rig.input.ax_g = rig.input.raw_gyro_z_dps = std::numeric_limits<float>::quiet_NaN();
        rig.input.imu_ok = true;
        CHECK(rig.absent(1000U, invalid).contract_faults == 0U);
        CHECK_FALSE(rig.last.heading.imu_ok);
    }
}

TEST_CASE("B3 B14 D084 Robot rejects malformed shape range and every time relation") {
    for (unsigned mutation = 0; mutation < 22U; ++mutation) {
        ExplicitRig rig;
        CHECK(rig.fresh(1000U, 10.0F).contract_faults == 0U);
        rig.input.imu = {true, true, Presence::VALID, Presence::VALID, true, true, 2000U, 2000U, 2U};
        auto input = rig.at(2100U); input.raw_heading_deg = 11.0F;
        switch (mutation) {
        case 0: input.imu.contract_valid = false; break;
        case 1: input.imu.heading_available = false; break;
        case 2: input.imu.heading_updated = false; break;
        case 3: input.imu.gyro = Presence::ABSENT; break;
        case 4: input.imu.accel = Presence::ABSENT; break;
        case 5: input.raw_heading_deg = std::numeric_limits<float>::infinity(); break;
        case 6: input.raw_gyro_z_dps = 1000.01F; break;
        case 7: input.raw_gyro_z_dps = -1000.01F; break;
        case 8: input.ax_g = 8.01F; break;
        case 9: input.ay_g = -8.01F; break;
        case 10: input.ax_g = std::numeric_limits<float>::quiet_NaN(); break;
        case 11: input.imu.checked_us = input.imu.observation_us = 2101U; break;
        case 12: input.imu.checked_us = 1999U; break;
        case 13: input.t_us = 4001U; break;
        case 14: input.imu.sequence = 1U; break;
        case 15: input.imu.sequence = 0U; break;
        case 16: input.imu.sequence = 1U + 0x80000000U; break;
        case 17: input.imu.checked_us = input.imu.observation_us = 999U; break;
        case 18: input.imu.checked_us = input.imu.observation_us = 1000U; break;
        case 19: input.imu.checked_us = input.imu.observation_us = 1000U + 0x80000000U; break;
        case 20: input.imu.explicit_values = false; break;
        default: input.imu.gyro = Presence::INVALID; break;
        }
        CAPTURE(mutation);
        contractFault(rig.submit(input));
        rig.input.stop_requested = true;
        contractFault(rig.fresh(5000U, 20.0F));
    }
}

TEST_CASE("B3 B14 D084 Robot exact inclusive limits and ignored invalid acceleration") {
    for (const float sign : {-1.0F, 1.0F}) {
        ExplicitRig rig;
        rig.input.raw_gyro_z_dps = sign * 1000.0F;
        rig.input.ax_g = sign * 8.0F; rig.input.ay_g = -sign * 8.0F;
        CHECK(rig.fresh(3000U, 10.0F, Button::NONE, 2000U).contract_faults == 0U);
        rig.acceleration = Presence::INVALID;
        rig.input.ax_g = rig.input.ay_g = std::numeric_limits<float>::quiet_NaN();
        CHECK(rig.fresh(4000U, 11.0F).contract_faults == 0U);
        rig.input.raw_gyro_z_dps = std::numeric_limits<float>::infinity();
        CHECK(rig.retained(5000U).contract_faults == 0U);
    }
}

TEST_CASE("B3 B14 D084 Robot identical replay suppresses sample but payload conflict latches") {
    for (unsigned field = 0; field < 7U; ++field) {
        ExplicitRig rig;
        CHECK(rig.fresh(1000U, 10.0F).contract_faults == 0U);
        auto replay = rig.at(1500U);
        if (field == 1U) replay.raw_heading_deg = 11.0F;
        if (field == 2U) replay.raw_gyro_z_dps = 1.0F;
        if (field == 3U) replay.ax_g = 1.0F;
        if (field == 4U) replay.ay_g = 1.0F;
        if (field == 5U) replay.imu.accel = Presence::INVALID;
        if (field == 6U) replay.previous_bias_dps = 7.0F;
        const auto result = rig.submit(replay);
        if (field == 0U || field == 6U) {
            CHECK(result.contract_faults == 0U);
            CHECK(result.heading.observation_us == 1000U);
            CHECK(result.heading.heading_age_us == 500U);
        } else contractFault(result);
    }
    ExplicitRig rig;
    rig.acceleration = Presence::INVALID;
    rig.fresh(1000U);
    rig.input.ax_g = std::numeric_limits<float>::infinity();
    CHECK(rig.step(1500U).contract_faults == 0U);
    rig.input.imu.checked_us = 500U;
    contractFault(rig.step(1600U));
}

TEST_CASE("B3 B14 D084 Robot retained history checks and availability cannot erase ordering") {
    for (unsigned mutation = 0; mutation < 6U; ++mutation) {
        ExplicitRig rig;
        rig.fresh(1000U, 10.0F);
        auto prior = rig.input;
        CHECK(rig.absent(1500U).contract_faults == 0U);
        rig.input = prior;
        rig.input.imu.gyro = rig.input.imu.accel = Presence::ABSENT;
        rig.input.imu.heading_updated = false; rig.input.imu.checked_us = 2000U;
        auto next = rig.at(2000U);
        if (mutation == 1U) next.imu.sequence += 1U;
        if (mutation == 2U) next.imu.observation_us += 1U;
        if (mutation == 3U) next.raw_heading_deg += 1.0F;
        if (mutation == 4U) next.t_us = 3001U;
        if (mutation == 5U) next.imu.checked_us = 999U;
        if (mutation == 0U) CHECK(rig.submit(next).contract_faults == 0U);
        else contractFault(rig.submit(next));
    }
    ExplicitRig unknown;
    unknown.input.imu.heading_available = true;
    contractFault(unknown.step(1000U));
}

TEST_CASE("B3 B14 D084 Robot wrap identities gaps duplicates reset and no resurrection") {
    ExplicitRig rig;
    rig.sequence = 0xfffffffeU;
    CHECK(rig.fresh(0xfffffff0U, 10.0F).contract_faults == 0U);
    CHECK(rig.fresh(0x10U, 11.0F).contract_faults == 0U);
    rig.sequence += 100U;
    CHECK(rig.fresh(100U, 12.0F).contract_faults == 0U);
    auto duplicate = rig.at(100U); duplicate.imu.contract_valid = false;
    duplicate.previous = {}; duplicate.stop_requested = true;
    const auto ignored = rig.submit(duplicate);
    CHECK_FALSE(ignored.fresh); CHECK(ignored.contract_faults == 0U);
    const auto saved = rig.input;
    rig.absent(0x80000064U); rig.absent(99U); rig.input = saved;
    contractFault(rig.retained(101U));
    const auto token = rig.last.token;
    rig.reset(); rig.input.imu.explicit_values = false; rig.input.imu_ok = true;
    const auto reset = rig.step(1000U);
    CHECK(reset.contract_faults == 0U); CHECK(reset.token > token);
    rig.input.imu.explicit_values = true;
    contractFault(rig.fresh(2000U));
}

TEST_CASE("B3 D084 Robot calibration counts genuine raw gyro once including valid accel loss") {
    ExplicitRig rig;
    rig.input.previous_bias_dps = 0.75F;
    const auto start = rig.release();
    rig.acceleration = Presence::INVALID; rig.input.ax_g = std::numeric_limits<float>::quiet_NaN();
    rig.input.raw_gyro_z_dps = 2.0F;
    CHECK(rig.fresh(start + 1500000U).lifecycle.services.calibration_samples == 1U);
    CHECK(rig.step(start + 1500500U).lifecycle.services.calibration_samples == 1U);
    CHECK(rig.retained(start + 1501000U).lifecycle.services.calibration_samples == 1U);
    rig.input.raw_gyro_z_dps = 3.0F;
    CHECK(rig.fresh(start + 1502000U).lifecycle.services.calibration_samples == 2U);
    CHECK(rig.absent(start + 1503000U).lifecycle.services.calibration_samples == 2U);
    const auto finish = rig.absent(start + 4500000U);
    CHECK(finish.lifecycle.services.calibration_finished);
    CHECK_FALSE(finish.lifecycle.services.calibration_rejected);
    CHECK(finish.bias_update_requested); CHECK(finish.accepted_bias_dps == 2.5F);
    robot_test::zero(finish);
}

TEST_CASE("B3 B4 B6 D084 actual Estimator adapter Robot stream preserves hold edge and STOP") {
    imu::Estimator estimator;
    CHECK(estimator.begin(imu::Mounting{{1, 2, 3}, true}, 0.0F));
    robot_test::Rig rig;
    std::uint32_t last_source = 0U, sequence = 0U;
    bool have_source = false, saw_go = false, saw_retained = false, saw_edge = false;
    std::uint32_t random = 0x812ea377U;
    for (std::uint32_t tick = 0U; tick < 5400U; ++tick) {
        const auto time = tick * 1000U;
        const bool new_data = !have_source || time - last_source >= 2000U || (robot_test::randomWord(random) & 1U) != 0U;
        imu::Sample s;
        if (new_data) {
            s = observation(time, ++sequence, have_source, have_source ? time - last_source : 0U,
                            tick < 5180U ? 1.0F : 10.0F);
            s.motion.accel_g[0] = 2.0F;
            if (tick % 17U == 0U) {
                s.motion.rail_mask = 1U; s.motion.accel_raw[0] = 32767;
            }
            last_source = time; have_source = true;
        } else {
            s.state = imu::SampleState::NO_NEW; s.checked_us = time;
            s.bus_status = imu::BusStatus::OK; s.sequence = sequence;
        }
        const auto estimate = estimator.observe(s);
        CHECK(estimate.state == imu::HeadingState::READY);
        if (new_data) {
            CHECK(estimate.gyro_observation == imu::Presence::VALID);
            CHECK(estimate.accel_observation == (tick % 17U == 0U ?
                imu::Presence::INVALID : imu::Presence::VALID));
        }
        CHECK(imu::applyEstimate(rig.input, estimate));
        const auto button = tick >= 30U && tick < 60U ? Button::START : Button::NONE;
        if (tick == 5300U) rig.lines(15U);
        if (tick == 5350U) rig.input.stop_requested = true;
        const auto result = rig.step(time, button);
        CHECK(result.contract_faults == 0U);
        robot_test::bounded(result);
        if (tick < 5180U) robot_test::zero(result);
        if (result.lifecycle.gate.go) { CHECK(tick == 5180U); saw_go = true; }
        if (saw_go && !new_data && tick < 5300U) {
            CHECK(result.heading.imu_ok); CHECK_FALSE(result.heading.heading_updated);
            CHECK(result.heading.observation_us == last_source); saw_retained = true;
        }
        if (tick >= 5300U) { robot_test::zero(result); saw_edge = true; }
        if (tick >= 5350U) CHECK(result.outputs.ui_state == State::STOPPED);
        if (result.bias_update_requested) {
            CHECK(result.accepted_bias_dps == 1.0F);
            CHECK_FALSE(result.lifecycle.services.calibration_rejected);
            CHECK(estimator.applyBias(result.accepted_bias_dps));
            const auto rebased = estimator.report();
            CHECK(rebased.heading_deg == estimate.heading_deg);
            CHECK(rebased.raw_gyro_z_dps == estimate.raw_gyro_z_dps);
            CHECK(rebased.gyro_z_dps == estimate.gyro_z_dps);
            CHECK(imu::applyEstimate(rig.input, rebased));
        }
    }
    CHECK(saw_go); CHECK(saw_retained); CHECK(saw_edge);
}

TEST_CASE("B5 B6 B9 D084 Robot acceleration presence and replay protect centered contact") {
    for (unsigned mode = 0U; mode < 4U; ++mode) {
        ExplicitRig rig; rig.opponent(2U);
        const auto go = rig.go(true);
        rig.input.ax_g = 2.0F;
        rig.fresh(go + 1000U);
        fsm::RobotResult attack;
        if (mode == 0U) attack = rig.step(go + 2000U); // Identical fresh report replay.
        if (mode == 1U) attack = rig.retained(go + 2000U);
        if (mode == 2U) { rig.acceleration = Presence::INVALID; attack = rig.fresh(go + 2000U); }
        if (mode == 3U) attack = rig.fresh(go + 2000U);
        CHECK(attack.outputs.ui_state == State::ATTACK);
        CHECK(attack.contact == (mode == 3U));
        CHECK(robot_test::count(attack, core::Event::CONTACT) == (mode == 3U ? 1U : 0U));
        CHECK(attack.contract_faults == 0U);
        if (mode != 3U) {
            rig.input.ax_g = 0.0F;
            const auto bounded = rig.fresh(go + 12000U);
            CHECK(bounded.outputs.duty_l <= 0.60F); CHECK(bounded.outputs.duty_r <= 0.60F);
        }
    }
}

TEST_CASE("B11 D084 Robot stall anchors only fresh contact and retained loss preserves timer") {
    for (const bool fresh_contact : {false, true}) {
        ExplicitRig rig;
        const auto go = rig.go(true);
        rig.opponent(7U);
        for (unsigned i = 1U; i <= 20U; ++i) {
            const auto result = rig.fresh(go + i * 1000U);
            CHECK_FALSE(result.contact);
        }
        const auto start = go + 21000U;
        const auto contact = fresh_contact ? rig.fresh(start) : rig.retained(start);
        CHECK(contact.contact); CHECK(robot_test::count(contact, core::Event::CONTACT) == 1U);
        rig.fresh(start + 50000U, 0.0F);
        const auto deflected = rig.fresh(start + 51000U, 30.0F);
        CHECK(deflected.contract_faults == 0U);
        CHECK((deflected.outputs.ui_state == State::REFLANK) == fresh_contact);
        if (!fresh_contact) {
            CHECK(deflected.outputs.ui_state == State::ATTACK);
            CHECK(rig.retained(start + 52000U).outputs.ui_state == State::ATTACK);
            CHECK(rig.fresh(start + 1050999U, 30.0F).outputs.ui_state == State::ATTACK);
            CHECK(rig.retained(start + 1051000U).outputs.ui_state == State::REFLANK);
        }
    }
}

TEST_CASE("B7 B12 B14 D084 retained GO yaw stays usable and does not latch timed fallback") {
    ExplicitRig rig;
    const auto start = rig.release();
    rig.fresh(start + 1500000U); rig.fresh(start + 1501000U); rig.fresh(start + 4500000U);
    rig.fresh(start + 5099000U, 10.0F);
    const auto go = rig.retained(start + 5100000U);
    CHECK(go.heading.origin == fsm::HeadingOrigin::LAST_KNOWN);
    CHECK(go.heading.origin_t_us == start + 5099000U);
    CHECK(go.heading.imu_ok); CHECK_FALSE(go.heading.heading_updated);
    CHECK(go.outputs.ui_state == State::OPENER);
    const auto completed_pivot = rig.fresh(start + 5101000U, 60.0F);
    CHECK(completed_pivot.heading.heading_deg == 50.0F);
    CHECK(completed_pivot.outputs.duty_l >= 0.0F);
    CHECK(completed_pivot.outputs.duty_r >= 0.0F);
    CHECK(robot_test::count(completed_pivot, core::Event::FAULT,
        static_cast<int>(logframe::FaultCode::IMU_UNAVAILABLE)) == 0U);
}

TEST_CASE("B15 D084 Robot captures presence and values before delayed receipt") {
    ExplicitRig rig;
    const auto start = rig.release();
    rig.input.raw_gyro_z_dps = 12.3F; rig.input.ax_g = 1.25F; rig.input.ay_g = -2.5F;
    const auto measured = rig.fresh(start + 40000U, 20.0F);
    const auto emitted = rig.absent(start + 41000U, true);
    CHECK(emitted.frame_ready); CHECK(emitted.frame_token == measured.token);
    CHECK(emitted.frame_status == logframe::PackStatus::OK);
    CHECK((emitted.frame.data[22] & 0xf0U) == 0xa0U);
    CHECK(emitted.frame.data[12] == 123U); CHECK(emitted.frame.data[13] == 0U);
    CHECK(emitted.frame.data[14] == 0xe2U); CHECK(emitted.frame.data[15] == 0x04U);
    CHECK(emitted.frame.data[16] == 0x3cU); CHECK(emitted.frame.data[17] == 0xf6U);
    rig.input.raw_gyro_z_dps = 9.0F; rig.input.ax_g = rig.input.ay_g = 7.0F;
    rig.fresh(start + 79000U, 22.0F);
    const auto retained = rig.retained(start + 80000U);
    const auto second = rig.fresh(start + 81000U, 23.0F);
    CHECK(second.frame_ready); CHECK(second.frame_token == retained.token);
    CHECK((second.frame.data[22] & 0xf0U) == 0x50U);
    for (unsigned i = 12U; i < 18U; ++i) CHECK(second.frame.data[i] == 0U);
}

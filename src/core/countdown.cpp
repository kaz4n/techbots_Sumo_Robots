// Implements B3 qualification, hold and approved calibration/warning/snapshot services.
// Keeps the full hold after release debounce without clocks or hardware writes.
// Verified by independent locked host boundary, wraparound and seeded stream tests.
#include "countdown.h"
#include "../config.h"
#include <algorithm>
#include <cmath>

namespace countdown {
Result Gate::step(std::uint32_t t_us, Commands commands) {
    Result result;
    if (commands.stop_requested) {
        phase_ = Phase::STOPPED;
    } else if (phase_ == Phase::HOLDING && commands.mode_press) {
        phase_ = Phase::IDLE;
    } else if (phase_ == Phase::IDLE && commands.start_release &&
               !commands.mode_press) {
        release_us_ = t_us;
        phase_ = Phase::HOLDING;
        result.start_release = true;
    }
    const std::uint32_t hold_us =
        (config::COUNTDOWN_MS + config::COUNTDOWN_MARGIN_MS) * 1000U;
    if (phase_ == Phase::HOLDING && t_us - release_us_ >= hold_us) {
        phase_ = Phase::READY;
        result.go = true;
    }
    result.phase = phase_;
    result.release_us = release_us_;
    result.motion_permitted = phase_ == Phase::READY;
    return result;
}

void Gate::reset() {
    *this = Gate{};
}

ButtonEvents Buttons::step(std::uint32_t t_us, core::ButtonLevel level) {
    ButtonEvents result;
    if (!initialized_) {
        initialized_ = true;
        candidate_ = stable_ = level;
        candidate_since_us_ = t_us;
        armed_ = level == core::ButtonLevel::NONE;
        return result;
    }
    if (level != candidate_) {
        candidate_ = level;
        candidate_since_us_ = t_us;
    }
    if (candidate_ == stable_ ||
        t_us - candidate_since_us_ < config::BTN_DEBOUNCE_MS * 1000U) {
        return result;
    }
    const bool was_mode = stable_ == core::ButtonLevel::MODE ||
                          stable_ == core::ButtonLevel::BOTH;
    stable_ = candidate_;
    result.edge_us = candidate_since_us_;
    result.qualified_us = t_us;
    if (stable_ == core::ButtonLevel::NONE) {
        result.start_release = pressed_;
        pressed_ = false;
        armed_ = true;
    } else if (stable_ == core::ButtonLevel::START) {
        pressed_ = armed_;
        armed_ = false;
    } else {
        result.mode_press = !was_mode;
        pressed_ = false;
        armed_ = false;
    }
    return result;
}

void Buttons::reset() {
    *this = Buttons{};
}

Result Controller::step(const core::Inputs& inputs, bool stop_requested) {
    const ButtonEvents events = buttons_.step(inputs.t_us, inputs.button_level);
    // A release pulse is generated at this qualifying tick. Using the same tick
    // for Gate prevents raw-edge backdating, including after delayed calls.
    return gate_.step(inputs.t_us,
                      {events.start_release, events.mode_press, stop_requested});
}

void Controller::reset() {
    buttons_.reset();
    gate_.reset();
}

bool Services::start(std::uint32_t release_us, float previous_bias_dps) {
    reset();
    if (!std::isfinite(previous_bias_dps)) {
        result_.calibration_rejected = true;
        return false;
    }
    last_us_ = release_us;
    result_.bias_dps = previous_bias_dps;
    result_.active = true;
    return true;
}

void Services::observeCalibration(const ServiceSample& sample) {
    if (!sample.imu_ok || !std::isfinite(sample.raw_gyro_z_dps)) {
        invalid_sample_ = true;
        return;
    }
    const double value = sample.raw_gyro_z_dps;
    if (result_.calibration_samples == 0U) {
        minimum_dps_ = maximum_dps_ = value;
    } else {
        minimum_dps_ = std::min(minimum_dps_, value);
        maximum_dps_ = std::max(maximum_dps_, value);
    }
    sum_dps_ += value;
    ++result_.calibration_samples;
}

void Services::finishCalibration() {
    const bool accepted = !invalid_sample_ &&
        result_.calibration_samples >= config::CAL_MIN_SAMPLES &&
        maximum_dps_ - minimum_dps_ <= config::CAL_MAX_SPREAD_DPS;
    if (accepted) {
        result_.bias_dps = static_cast<float>(sum_dps_ / result_.calibration_samples);
    }
    result_.calibration_finished = true;
    result_.calibration_rejected = !accepted;
}

ServiceResult Services::step(const ServiceSample& sample) {
    constexpr std::uint64_t hold_ms =
        static_cast<std::uint64_t>(config::COUNTDOWN_MS) + config::COUNTDOWN_MARGIN_MS;
    static_assert(config::CAL_MIN_SAMPLES >= 2U);
    static_assert(config::CAL_START_MS < config::CAL_END_MS && config::CAL_END_MS <= hold_ms);
    static_assert(config::COUNTDOWN_LINE_WARN_MS <= hold_ms && config::COUNTDOWN_SNAPSHOT_MS <= hold_ms);
    if (!result_.active) return result_;
    const std::uint32_t delta_us = sample.t_us - last_us_;
    if (delta_us == 0U) return result_; // Repeated service calls cannot fabricate samples.
    last_us_ = sample.t_us;
    elapsed_us_ += delta_us;
    const std::uint64_t calibration_end_us = static_cast<std::uint64_t>(config::CAL_END_MS) * 1000U;
    if (!result_.calibration_finished) {
        if (elapsed_us_ >= calibration_end_us) {
            finishCalibration();
        } else if (elapsed_us_ >= static_cast<std::uint64_t>(config::CAL_START_MS) * 1000U) {
            observeCalibration(sample);
        }
    }
    if (elapsed_us_ >= hold_ms * 1000U) {
        result_.active = false;
        result_.finished = true;
        return result_;
    }
    if (elapsed_us_ >= (hold_ms - config::COUNTDOWN_LINE_WARN_MS) * 1000U) {
        result_.line_warning = result_.line_warning || (sample.line_mask & 0x0FU) != 0U;
    }
    if (elapsed_us_ >= (hold_ms - config::COUNTDOWN_SNAPSHOT_MS) * 1000U) {
        result_.opponent_snapshot = sample.confirmed_opp_mask & 0x7FU;
    }
    return result_;
}

void Services::cancel() {
    const float bias_dps = result_.bias_dps;
    reset();
    result_.bias_dps = bias_dps;
}

void Services::reset() { *this = Services{}; }
} // namespace countdown

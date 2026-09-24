// Implements B3 start/services, B13 menus and D-035 logical STOP qualification.
// Keeps the full hold after release debounce without clocks or hardware writes.
// Verified by independent locked host boundary, wraparound and seeded stream tests.
#include "countdown.h"
#include "../config.h"
#include <algorithm>
#include <cmath>
#include <limits>

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
    return stepObserved(t_us, t_us, level);
}

ButtonEvents Buttons::stepObserved(std::uint32_t decision_us, std::uint32_t source_us,
                                  core::ButtonLevel level) {
    ButtonEvents result;
    if (!initialized_) {
        initialized_ = true;
        candidate_ = stable_ = level;
        candidate_since_us_ = source_us;
        armed_ = level == core::ButtonLevel::NONE;
        return result;
    }
    if (level != candidate_) {
        candidate_ = level;
        candidate_since_us_ = source_us;
    }
    if (candidate_ == stable_ ||
        source_us - candidate_since_us_ < config::BTN_DEBOUNCE_MS * 1000U) {
        return result;
    }
    const bool was_mode = stable_ == core::ButtonLevel::MODE ||
                          stable_ == core::ButtonLevel::BOTH;
    stable_ = candidate_;
    result.edge_us = candidate_since_us_;
    result.qualified_us = decision_us;
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

bool StopHold::step(std::uint32_t t_us, core::ButtonLevel level) {
    return stepObserved(t_us, t_us, level);
}

bool StopHold::stepObserved(std::uint32_t decision_us, std::uint32_t source_us,
                            core::ButtonLevel level) {
    static_assert(config::BTN_DEBOUNCE_MS > 0U && config::BTN_LONG_MS > 0U);
    static_assert(config::BTN_DEBOUNCE_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U);
    static_assert(config::BTN_LONG_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U);
    const std::uint32_t elapsed_us = source_us - last_us_;
    if (stage_ == Stage::STOPPED) return true;
    // An actual release takes priority over a deadline not yet observed.
    if (level != core::ButtonLevel::BOTH) {
        stage_ = Stage::IDLE;
        age_us_ = 0U;
        source_before_anchor_ = false;
        return false;
    }
    if (stage_ == Stage::IDLE) {
        stage_ = Stage::DEBOUNCE;
        age_us_ = 0U;
        last_us_ = source_us;
        return false;
    }
    if (source_before_anchor_ && elapsed_us >= 0x80000000U) return false;
    source_before_anchor_ = false;
    last_us_ = source_us;
    const std::uint32_t required_us = (stage_ == Stage::DEBOUNCE ?
        config::BTN_DEBOUNCE_MS : config::BTN_LONG_MS) * 1000U;
    const auto age = static_cast<std::uint64_t>(age_us_) + elapsed_us;
    if (age < required_us) {
        age_us_ = static_cast<std::uint32_t>(age);
        return false;
    }
    age_us_ = 0U;
    if (stage_ == Stage::DEBOUNCE) {
        stage_ = Stage::HOLDING;
        last_us_ = decision_us;
        source_before_anchor_ = source_us != decision_us;
        return false;
    }
    stage_ = Stage::STOPPED;
    return true;
}

void StopHold::reset() { *this = StopHold{}; }

void StopHold::interrupt() {
    if (stage_ != Stage::STOPPED) reset();
}

Result Controller::step(const core::Inputs& inputs, bool stop_requested,
                        bool allow_match_start) {
    return stepObserved(inputs, {inputs.t_us, true, false, true},
                        stop_requested, allow_match_start);
}

Result Controller::stepObserved(const core::Inputs& inputs, const ButtonTiming& timing,
                                bool stop_requested, bool allow_match_start) {
    events_ = {};
    if (timing.restart) { buttons_.reset(); stop_.interrupt(); }
    if (!timing.start_ready) buttons_.reset();
    if (timing.fresh) {
        if (timing.start_ready)
            events_ = buttons_.stepObserved(inputs.t_us, timing.observation_us, inputs.button_level);
        logical_stop_ = stop_.stepObserved(inputs.t_us, timing.observation_us, inputs.button_level);
    }
    // A release pulse is generated at this qualifying tick. Using the same tick
    // for Gate prevents raw-edge backdating, including after delayed calls.
    return gate_.step(inputs.t_us,
                      {allow_match_start && events_.start_release,
                       events_.mode_press, stop_requested || logical_stop_});
}

ButtonEvents Controller::buttonEvents() const { return events_; }

void Controller::reset() {
    stop_.reset();
    buttons_.reset();
    gate_.reset();
    events_ = {};
    logical_stop_ = false;
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

bool Services::admitGyro(const ServiceSample& sample) {
    bool explicit_mode = false;
    switch (sample.gyro_presence) {
    case GyroPresence::LEGACY: break;
    case GyroPresence::ABSENT:
    case GyroPresence::VALID:
    case GyroPresence::INVALID: explicit_mode = true; break;
    default: invalid_sample_ = true; return false;
    }
    if (gyro_mode_selected_ && explicit_gyro_mode_ != explicit_mode) {
        invalid_sample_ = true;
        return false;
    }
    gyro_mode_selected_ = true;
    explicit_gyro_mode_ = explicit_mode;
    if (!explicit_mode) {
        const bool valid = sample.imu_ok && std::isfinite(sample.raw_gyro_z_dps);
        if (!valid) invalid_sample_ = true;
        return valid;
    }
    if (sample.gyro_presence == GyroPresence::ABSENT) return false;
    if (sample.gyro_presence == GyroPresence::INVALID) {
        invalid_sample_ = true;
        return false;
    }
    return admitExplicitGyro(sample);
}

bool Services::admitExplicitGyro(const ServiceSample& sample) {
    const std::uint32_t age_us = sample.t_us - sample.gyro_observation_us;
    if (!std::isfinite(sample.raw_gyro_z_dps) || age_us > config::IMU_HEADING_MAX_GAP_US) {
        invalid_sample_ = true;
        return false;
    }
    if (have_gyro_observation_) {
        const std::uint32_t time_delta = sample.gyro_observation_us - last_gyro_observation_us_;
        const std::uint32_t sequence_delta = sample.gyro_sequence - last_gyro_sequence_;
        if (time_delta == 0U && sequence_delta == 0U) {
            if (sample.raw_gyro_z_dps != last_raw_gyro_dps_) invalid_sample_ = true;
            return false;
        }
        if (time_delta == 0U || sequence_delta == 0U ||
            time_delta >= 0x80000000U || sequence_delta >= 0x80000000U) {
            invalid_sample_ = true;
            return false;
        }
    }
    // A fresh pre-window identity stays consumed even though it contributes no value.
    have_gyro_observation_ = true;
    last_gyro_observation_us_ = sample.gyro_observation_us;
    last_gyro_sequence_ = sample.gyro_sequence;
    last_raw_gyro_dps_ = sample.raw_gyro_z_dps;
    if (elapsed_us_ < age_us) return false;
    const std::uint64_t source_elapsed_us = elapsed_us_ - age_us;
    return source_elapsed_us >= static_cast<std::uint64_t>(config::CAL_START_MS) * 1000U &&
           source_elapsed_us < static_cast<std::uint64_t>(config::CAL_END_MS) * 1000U;
}

void Services::observeCalibration(const ServiceSample& sample) {
    if (!admitGyro(sample)) return;
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
        const std::uint32_t age = sample.t_us - sample.line_source_us;
        const bool source_in_window = sample.line_updated &&
            age < config::QTR_SAMPLE_MAX_AGE_US && elapsed_us_ >= age &&
            elapsed_us_ - age >= (hold_ms - config::COUNTDOWN_LINE_WARN_MS) * 1000U;
        if (!sample.explicit_line || source_in_window)
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

LifecycleResult Lifecycle::step(const ServiceSample& sample, core::ButtonLevel button,
                                float previous_bias_dps, bool stop_requested,
                                bool allow_match_start) {
    return stepObserved(sample, button, {sample.t_us, true, false, true},
                        previous_bias_dps, stop_requested, allow_match_start);
}

LifecycleResult Lifecycle::stepObserved(const ServiceSample& sample, core::ButtonLevel button,
    const ButtonTiming& timing, float previous_bias_dps, bool stop_requested,
    bool allow_match_start) {
    core::Inputs inputs;
    inputs.t_us = sample.t_us;
    inputs.button_level = button;
    LifecycleResult result;
    result.gate = controller_.stepObserved(inputs, timing, stop_requested, allow_match_start);
    if (result.gate.start_release) {
        service_start_failed_ = !services_.start(result.gate.release_us, previous_bias_dps);
        pending_ = true;
    }
    if (pending_ && (result.gate.phase == Phase::IDLE || result.gate.phase == Phase::STOPPED)) {
        // Cancellation wins before this tick can finish calibration or alter its snapshot.
        services_.cancel();
        pending_ = false;
        service_start_failed_ = false;
    }
    result.services = services_.step(sample);
    if (result.gate.go) pending_ = false;
    result.service_start_failed = service_start_failed_;
    result.heading_reset_requested = result.gate.go;
    return result;
}

ButtonEvents Lifecycle::buttonEvents() const { return controller_.buttonEvents(); }

void Lifecycle::reset() {
    controller_.reset();
    services_.reset();
    pending_ = false;
    service_start_failed_ = false;
}

static_assert(config::MODE_DEFAULT >= 1U && config::MODE_DEFAULT <= 6U);
static_assert(config::BTN_DEBOUNCE_MS > 0U && config::BTN_LONG_MS > 0U);
static_assert(config::BTN_DEBOUNCE_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U);
static_assert(config::BTN_LONG_MS <= std::numeric_limits<std::uint32_t>::max() / 1000U);
static_assert(config::MODE_SHORT_MS > 0U && config::MODE_SHORT_MS <= config::BTN_LONG_MS);

void Menu::advanceAge(std::uint32_t delta_us, std::uint32_t limit_us) {
    const auto age = static_cast<std::uint64_t>(age_us_) + delta_us;
    age_us_ = age < limit_us ? static_cast<std::uint32_t>(age) : limit_us;
}

void Menu::disarm() {
    stage_ = Stage::DISARMED;
    age_us_ = 0U;
    short_release_ = false;
}

void Menu::cycle(MenuResult& result) {
    if (selection_.service_menu) {
        selection_.service = selection_.service == Service::LOG_DUMP ?
            Service::SENSOR_VIEW :
            static_cast<Service>(static_cast<std::uint8_t>(selection_.service) + 1U);
    } else if constexpr (config::MODE_ARC_ENABLED == 1U && config::MODE_WAIT_ENABLED == 1U) {
        selection_.mode = selection_.mode == core::Mode::WAIT ?
            core::Mode::SIDESTEP_R :
            static_cast<core::Mode>(static_cast<std::uint8_t>(selection_.mode) + 1U);
    } else {
        for (std::uint8_t probe = 0U; probe < 6U; ++probe) {
            selection_.mode = selection_.mode == core::Mode::WAIT ?
                core::Mode::SIDESTEP_R :
                static_cast<core::Mode>(static_cast<std::uint8_t>(selection_.mode) + 1U);
            if (core::modeAvailable(selection_.mode)) break;
        }
    }
    result.selection_changed = true;
}

void Menu::toggle(MenuResult& result) {
    selection_.service_menu = !selection_.service_menu;
    if (selection_.service_menu) selection_.service = Service::SENSOR_VIEW;
    result.selection_changed = true;
    result.menu_toggled = true;
}

void Menu::observeMode(std::uint32_t delta_us, MenuResult& result) {
    if (stage_ == Stage::READY) {
        stage_ = Stage::PRESS;
        age_us_ = 0U;
    } else if (stage_ == Stage::PRESS) {
        advanceAge(delta_us, config::BTN_DEBOUNCE_MS * 1000U);
        if (age_us_ == config::BTN_DEBOUNCE_MS * 1000U) {
            // A delayed qualification starts a complete hold at this call.
            stage_ = Stage::HELD;
            age_us_ = 0U;
        }
    } else if (stage_ == Stage::HELD) {
        advanceAge(delta_us, config::BTN_LONG_MS * 1000U);
        if (age_us_ == config::BTN_LONG_MS * 1000U) {
            toggle(result);
            stage_ = Stage::CONSUMED;
            age_us_ = 0U;
        }
    } else if (stage_ != Stage::CONSUMED) {
        // MODE before rearming or during release loses the whole gesture.
        disarm();
    }
}

void Menu::observeNone(std::uint32_t delta_us, MenuResult& result) {
    if (stage_ == Stage::HELD) {
        // Freeze at the first release, before considering a long deadline.
        advanceAge(delta_us, config::BTN_LONG_MS * 1000U);
        short_release_ = age_us_ < config::MODE_SHORT_MS * 1000U;
        stage_ = Stage::RELEASE;
        age_us_ = 0U;
    } else if (stage_ == Stage::RELEASE || stage_ == Stage::REARM) {
        advanceAge(delta_us, config::BTN_DEBOUNCE_MS * 1000U);
        if (age_us_ == config::BTN_DEBOUNCE_MS * 1000U) {
            if (stage_ == Stage::RELEASE && short_release_) cycle(result);
            stage_ = Stage::READY;
            age_us_ = 0U;
            short_release_ = false;
        }
    } else if (stage_ != Stage::READY) {
        stage_ = Stage::REARM;
        age_us_ = 0U;
        short_release_ = false;
    }
}

MenuResult Menu::step(const MenuSample& sample) {
    return stepObserved(sample, {sample.t_us, true, false, true});
}

MenuResult Menu::stepObserved(const MenuSample& sample, const ButtonTiming& timing) {
    MenuResult result;
    result.selection = selection_;
    if (observed_ && sample.t_us == last_us_) return result;
    observed_ = true;
    last_us_ = sample.t_us;
    if (timing.restart) { disarm(); source_observed_ = false; }
    if (sample.state_at_entry != core::State::IDLE || sample.inhibited_fault) {
        disarm();
        return result;
    }
    if (!timing.fresh) return result;
    auto delta_us = source_observed_ ? timing.observation_us - last_source_us_ : 0U;
    source_observed_ = true;
    last_source_us_ = timing.observation_us;
    if (stage_ == Stage::HELD) {
        delta_us = timing.observation_us - hold_source_us_;
        if (source_before_anchor_ && delta_us >= 0x80000000U) delta_us = 0U;
        else { source_before_anchor_ = false; hold_source_us_ = timing.observation_us; }
    }
    const auto entry = stage_;
    if (sample.button == core::ButtonLevel::NONE) {
        if (selection_.service_menu && sample.qualified_start_release) {
            result.request = selection_.service;
            result.request_unavailable = !(SUMOX_P3_DRIVE_TEST || SUMOX_P3_TURN_TRIAL || SUMOX_P3_STOP_TRIAL) &&
                selection_.service == Service::DRIVE_TEST;
            // A service START replaces any pending MODE gesture with fresh NONE.
            disarm();
            observeNone(0U, result);
        } else {
            observeNone(delta_us, result);
        }
    } else if (sample.button == core::ButtonLevel::MODE) {
        observeMode(delta_us, result);
    } else {
        disarm();
    }
    if (entry != Stage::HELD && stage_ == Stage::HELD) {
        hold_source_us_ = sample.t_us;
        source_before_anchor_ = timing.observation_us != sample.t_us;
    }
    result.selection = selection_;
    return result;
}

MenuSelection Menu::selection() const { return selection_; }

void Menu::reset() { *this = Menu{}; }
} // namespace countdown

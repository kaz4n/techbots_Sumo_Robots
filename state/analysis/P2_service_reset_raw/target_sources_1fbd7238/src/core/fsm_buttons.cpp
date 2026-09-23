// Admits D087 button evidence independently of Robot decision ticks.
// Preserves source identity, bounded continuity and neutral arming before START.
// Independent routing tests cover replay, expiry, source timing and reset faults.
#include "fsm.h"
#include <limits>

namespace fsm {
namespace {
constexpr std::uint32_t HALF_RANGE = 0x80000000U;

bool sameButtons(const core::ButtonEvidence& a, const core::ButtonEvidence& b) {
    return a.sequence == b.sequence && a.level == b.level && a.raw == b.raw &&
        a.started_us == b.started_us && a.completed_us == b.completed_us;
}

bool absentButtons(const core::ButtonEvidence& value) {
    return value.level == core::ButtonLevel::NONE && value.raw == 0U &&
        value.sequence == 0U && value.started_us == 0U && value.completed_us == 0U;
}
} // namespace

bool Robot::admitButtons(const RobotInput& input) {
    const auto& value = input.buttons;
    if (!value.contract_valid) return false;
    if (value.presence == core::ButtonPresence::ABSENT) return absentButtons(value);
    if (value.presence != core::ButtonPresence::VALID ||
        static_cast<std::uint8_t>(value.level) > 3U || value.raw > 16383U ||
        value.completed_us - value.started_us >= config::VBAT_ADC_CONVERSION_US ||
        input.t_us - value.started_us > config::BUTTON_SAMPLE_MAX_AGE_US ||
        input.t_us - value.completed_us >= HALF_RANGE) return false;
    if (button_seen_) {
        if (sameButtons(value, button_history_)) return true;
        const auto sequence = value.sequence - button_history_.sequence;
        const auto completion = value.completed_us - button_history_.completed_us;
        if (sequence == 0U || sequence >= HALF_RANGE || completion == 0U ||
            completion >= HALF_RANGE ||
            value.started_us - button_history_.completed_us >= HALF_RANGE ||
            value.started_us - button_history_.started_us > config::BUTTON_SAMPLE_MAX_AGE_US ||
            tick_.delta_us > config::BUTTON_SAMPLE_MAX_AGE_US) return false;
    }
    button_history_ = value;
    button_seen_ = true;
    button_age_us_ = input.t_us - value.started_us;
    result_.button_updated = true;
    return true;
}

void Robot::qualifyNeutral() {
    if (neutral_armed_ || !result_.button_updated) return;
    if (button_history_.level != core::ButtonLevel::NONE) {
        neutral_pending_ = false;
        return;
    }
    if (!neutral_pending_) {
        neutral_pending_ = true;
        neutral_since_us_ = button_history_.completed_us;
    } else if (button_history_.completed_us - neutral_since_us_ >=
               config::BTN_DEBOUNCE_MS * 1000U) neutral_armed_ = true;
}

void Robot::prepareButtons(RobotInput& input) {
    const bool entering = !button_mode_chosen_;
    if (entering) {
        button_mode_chosen_ = true;
        explicit_button_mode_ = input.buttons.explicit_values;
    }
    button_timing_ = {input.t_us, true, false, true};
    if (input.buttons.explicit_values != explicit_button_mode_) faults_ |= BUTTON_CONTRACT;
    if (!explicit_button_mode_ && (faults_ & BUTTON_CONTRACT) == 0U) return;
    const auto maximum = std::numeric_limits<std::uint32_t>::max();
    button_age_us_ = maximum - button_age_us_ < tick_.delta_us ? maximum :
                     button_age_us_ + tick_.delta_us;
    if (tick_.delta_us >= HALF_RANGE ||
        ((faults_ & BUTTON_CONTRACT) == 0U && !admitButtons(input))) faults_ |= BUTTON_CONTRACT;
    if ((button_seen_ && button_age_us_ > config::BUTTON_SAMPLE_MAX_AGE_US) ||
        ((initialized_ || input.initialization_complete) && !button_seen_)) faults_ |= BUTTON_CONTRACT;
    result_.button_available = button_seen_ && (faults_ & BUTTON_CONTRACT) == 0U;
    result_.button_level = button_seen_ ? button_history_.level : core::ButtonLevel::NONE;
    result_.button_source_us = button_seen_ ? button_history_.started_us : 0U;
    result_.button_sequence = button_seen_ ? button_history_.sequence : 0U;
    result_.button_age_us = button_seen_ ? button_age_us_ : 0U;
    if (!result_.button_available) result_.button_updated = false;
    qualifyNeutral();
    const bool fault = (faults_ & BUTTON_CONTRACT) != 0U;
    if (fault) neutral_pending_ = neutral_armed_ = false;
    button_timing_ = {button_history_.completed_us, result_.button_updated,
                      entering || fault, neutral_armed_};
    input.button = result_.button_level;
}
} // namespace fsm

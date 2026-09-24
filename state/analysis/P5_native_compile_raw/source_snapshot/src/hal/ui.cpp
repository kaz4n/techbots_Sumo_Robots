// Classifies explicit A1 conversion evidence without sampling or debouncing.
// Unknown and overlapping raw windows cannot manufacture a logical release.
// Independent synthetic-window and Robot routing tests cover this boundary.
#include "ui.h"
#include "../config.h"

namespace ui {
namespace {
bool validConfig() {
    if (config::BUTTON_WINDOWS_CONFIGURED > 1U ||
        config::BUTTON_SAMPLE_MAX_AGE_US < config::VBAT_ADC_CONVERSION_US ||
        config::BUTTON_SAMPLE_MAX_AGE_US >= 0x80000000U) return false;
    for (unsigned i = 0; i < 4U; ++i) {
        if (config::BUTTON_LOW_RAW[i] > config::BUTTON_HIGH_RAW[i] ||
            config::BUTTON_HIGH_RAW[i] > 16383U) return false;
    }
    return true;
}

bool absent(const power::ButtonSample& sample) {
    return sample.status == power::Status::NOT_INITIALIZED &&
        sample.shutdown == power::Shutdown::NOT_ATTEMPTED && !sample.valid &&
        sample.raw == 0U && sample.sequence == 0U && sample.started_us == 0U &&
        sample.completed_us == 0U;
}

bool validShape(const power::ButtonSample& sample) {
    if (static_cast<unsigned>(sample.status) >
            static_cast<unsigned>(power::Status::NOT_ENABLED) ||
        static_cast<unsigned>(sample.shutdown) >
            static_cast<unsigned>(power::Shutdown::UNCONFIRMED)) return false;
    if (sample.valid != (sample.status == power::Status::OK)) return false;
    if (!sample.valid) return true;
    return sample.shutdown == power::Shutdown::NOT_ATTEMPTED &&
        sample.raw <= 16383U &&
        sample.completed_us - sample.started_us < config::VBAT_ADC_CONVERSION_US;
}

void classify(const power::ButtonSample& sample, ButtonDecode& result) {
    if (config::BUTTON_WINDOWS_CONFIGURED == 0U) {
        result.qualification = ButtonQualification::UNCONFIGURED;
        return;
    }
    unsigned count = 0U;
    unsigned selected = 0U;
    for (unsigned i = 0; i < 4U; ++i) {
        if (sample.raw < config::BUTTON_LOW_RAW[i] ||
            sample.raw > config::BUTTON_HIGH_RAW[i]) continue;
        result.candidate_mask |= static_cast<std::uint8_t>(1U << i);
        selected = i;
        ++count;
    }
    result.qualification = count == 0U ? ButtonQualification::UNKNOWN :
        count == 1U ? ButtonQualification::VALID : ButtonQualification::AMBIGUOUS;
    if (count != 1U) return;
    result.evidence.presence = core::ButtonPresence::VALID;
    result.evidence.level = static_cast<core::ButtonLevel>(selected);
}
} // namespace

ButtonDecode decodeButtons(const power::ButtonSample& sample) {
    ButtonDecode result;
    result.evidence.explicit_values = true;
    if (validConfig() && absent(sample)) return result;
    result.qualification = ButtonQualification::INVALID;
    result.evidence.presence = core::ButtonPresence::INVALID;
    result.evidence.contract_valid = validConfig() && validShape(sample);
    result.evidence.raw = sample.raw;
    result.evidence.sequence = sample.sequence;
    result.evidence.started_us = sample.started_us;
    result.evidence.completed_us = sample.completed_us;
    if (!result.evidence.contract_valid || !sample.valid) return result;
    classify(sample, result);
    return result;
}

ButtonQualification applyButtons(fsm::RobotInput& input, const power::ButtonSample& sample) {
    const auto decoded = decodeButtons(sample);
    input.buttons = decoded.evidence;
    return decoded.qualification;
}
} // namespace ui

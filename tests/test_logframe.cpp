// Checks the B15 fixed frame and exact tick event representation from the header.
// Makes endian, signed, rounding and invalid-input behavior explicit in fixtures.
// Spec-only doctest cases compare literal bytes and exercise every input field.
#include "doctest.h"
#include "core/logframe.h"
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <limits>

namespace {
void checkFrameBytes(const logframe::FrameBytes& bytes, const std::uint8_t* expected) {
    for (std::size_t index = 0U; index < logframe::FRAME_BYTES; ++index) {
        CAPTURE(index);
        CHECK(bytes.data[index] == expected[index]);
    }
}

void checkEventBytes(const logframe::EventBytes& bytes, const std::uint8_t* expected) {
    for (std::size_t index = 0U; index < logframe::EVENT_BYTES; ++index) {
        CAPTURE(index);
        CHECK(bytes.data[index] == expected[index]);
    }
}

void checkInvalidFrame(const logframe::FrameInput& input) {
    logframe::FrameBytes bytes;
    for (auto& byte : bytes.data) byte = 0xA5U;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::INVALID);
    for (auto byte : bytes.data) CHECK(byte == 0U);
}

void checkInvalidEvent(const logframe::EventInput& input) {
    logframe::EventBytes bytes;
    for (auto& byte : bytes.data) byte = 0xA5U;
    CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::INVALID);
    for (auto byte : bytes.data) CHECK(byte == 0U);
}

logframe::FrameInput halfFrame() {
    logframe::FrameInput input;
    input.heading_deg = .125F;
    input.gyro_z_dps = .25F;
    input.ax_g = .0625F;
    input.ay_g = -.0625F;
    input.duty_l = .5F;
    input.duty_r = -.5F;
    input.vbat_v = .125F;
    return input;
}
} // namespace

TEST_CASE("B15 default frame bytes are exact and have no native padding") {
    CHECK(logframe::FRAME_BYTES == 25U);
    CHECK(sizeof(logframe::FrameBytes) == 25U);
    CHECK(logframe::EVENT_BYTES == 8U);
    CHECK(sizeof(logframe::EventBytes) == 8U);
    logframe::FrameBytes bytes;
    for (auto byte : bytes.data) CHECK(byte == 0U);
    const std::uint8_t expected[25] = {
        0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };
    CHECK(logframe::packFrame(logframe::FrameInput{}, bytes) == logframe::PackStatus::OK);
    checkFrameBytes(bytes, expected);
}

TEST_CASE("B15 populated frame matches literal little endian signed golden") {
    logframe::FrameInput input;
    input.t_ms = 0x12345678U;
    input.state = core::State::ATTACK;
    input.mode = core::Mode::ARC_L;
    input.line_mask = 0x09U;
    input.opp_mask = 0x45U;
    input.heading_deg = -450.25F;
    input.gyro_z_dps = -12.5F;
    input.ax_g = 1.25F;
    input.ay_g = -.5F;
    input.duty_l = .5F;
    input.duty_r = -.5F;
    input.vbat_v = 12.5F;
    input.flags = 0x0FU;
    input.tick_max_us = 0x1234U;
    const std::uint8_t expected[25] = {
        0x78, 0x56, 0x34, 0x12, 0x06, 0x05, 0x09, 0x45,
        0x1F, 0x50, 0xFF, 0xFF, 0x83, 0xFF, 0xE2, 0x04,
        0x0C, 0xFE, 0x40, 0xC0, 0xE2, 0x04, 0x0F, 0x34, 0x12
    };
    logframe::FrameBytes bytes;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    checkFrameBytes(bytes, expected);
}

TEST_CASE("B15 accumulated yaw preserves positive and negative multirevolution values") {
    logframe::FrameInput input;
    logframe::FrameBytes bytes;
    input.heading_deg = 1080.25F;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    CHECK(bytes.data[8] == 0xF9U); CHECK(bytes.data[9] == 0xA5U);
    CHECK(bytes.data[10] == 0x01U); CHECK(bytes.data[11] == 0x00U);
    input.heading_deg = -1080.25F;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    CHECK(bytes.data[8] == 0x07U); CHECK(bytes.data[9] == 0x5AU);
    CHECK(bytes.data[10] == 0xFEU); CHECK(bytes.data[11] == 0xFFU);
}

TEST_CASE("B15 exact rounding halves go away from zero in every quantized field") {
    auto input = halfFrame();
    logframe::FrameBytes bytes;
    const std::uint8_t positive[25] = {
        0, 0, 0, 0, 0, 1, 0, 0, 13, 0, 0, 0, 3, 0,
        63, 0, 0xC1, 0xFF, 64, 0xC0, 13, 0, 0, 0, 0
    };
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    checkFrameBytes(bytes, positive);
    input.heading_deg = -.125F;
    input.gyro_z_dps = -.25F;
    input.ax_g = -.0625F;
    input.ay_g = .0625F;
    input.duty_l = -.5F;
    input.duty_r = .5F;
    const std::uint8_t negative[25] = {
        0, 0, 0, 0, 0, 1, 0, 0, 0xF3, 0xFF, 0xFF, 0xFF,
        0xFD, 0xFF, 0xC1, 0xFF, 63, 0, 0xC0, 64, 13, 0, 0, 0, 0
    };
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    checkFrameBytes(bytes, negative);
}

TEST_CASE("B15 floats immediately below positive rounding ties round down") {
    auto input = halfFrame();
    input.heading_deg = std::nextafter(input.heading_deg, 0.0F);
    input.gyro_z_dps = std::nextafter(input.gyro_z_dps, 0.0F);
    input.ax_g = std::nextafter(input.ax_g, 0.0F);
    input.ay_g = std::nextafter(input.ay_g, 0.0F);
    input.duty_l = std::nextafter(input.duty_l, 0.0F);
    input.duty_r = std::nextafter(input.duty_r, 0.0F);
    input.vbat_v = std::nextafter(input.vbat_v, 0.0F);
    const std::uint8_t expected[25] = {
        0, 0, 0, 0, 0, 1, 0, 0, 12, 0, 0, 0, 2, 0,
        62, 0, 0xC2, 0xFF, 63, 0xC1, 12, 0, 0, 0, 0
    };
    logframe::FrameBytes bytes;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    checkFrameBytes(bytes, expected);
}

TEST_CASE("B15 floats immediately above magnitude rounding ties round outward") {
    auto input = halfFrame();
    const float inf = std::numeric_limits<float>::infinity();
    input.heading_deg = std::nextafter(-input.heading_deg, -inf);
    input.gyro_z_dps = std::nextafter(-input.gyro_z_dps, -inf);
    input.ax_g = std::nextafter(input.ax_g, inf);
    input.ay_g = std::nextafter(input.ay_g, -inf);
    input.duty_l = std::nextafter(input.duty_l, inf);
    input.duty_r = std::nextafter(input.duty_r, -inf);
    input.vbat_v = std::nextafter(input.vbat_v, inf);
    const std::uint8_t expected[25] = {
        0, 0, 0, 0, 0, 1, 0, 0, 0xF3, 0xFF, 0xFF, 0xFF, 0xFD, 0xFF,
        63, 0, 0xC1, 0xFF, 64, 0xC0, 13, 0, 0, 0, 0
    };
    logframe::FrameBytes bytes;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    checkFrameBytes(bytes, expected);
}

TEST_CASE("B15 finite positive overflow saturates exact signed and unsigned limits") {
    const float huge = std::numeric_limits<float>::max();
    logframe::FrameInput input;
    input.t_ms = 0xFFFFFFFFU;
    input.heading_deg = huge;
    input.gyro_z_dps = huge;
    input.ax_g = huge;
    input.ay_g = -huge;
    input.duty_l = huge;
    input.duty_r = -huge;
    input.vbat_v = huge;
    input.tick_max_us = 0xFFFFFFFFU;
    const std::uint8_t expected[25] = {
        0xFF, 0xFF, 0xFF, 0xFF, 0, 1, 0, 0, 0xFF, 0xFF, 0xFF, 0x7F,
        0xFF, 0x7F, 0xFF, 0x7F, 0, 0x80, 0x7F, 0x81, 0xFF, 0xFF, 0, 0xFF, 0xFF
    };
    logframe::FrameBytes bytes;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::CLAMPED);
    checkFrameBytes(bytes, expected);
}

TEST_CASE("B15 finite negative overflow saturates instead of wrapping") {
    const float huge = std::numeric_limits<float>::max();
    logframe::FrameInput input;
    input.heading_deg = -huge;
    input.gyro_z_dps = -huge;
    input.ax_g = -huge;
    input.ay_g = huge;
    input.duty_l = -huge;
    input.duty_r = huge;
    input.vbat_v = -huge;
    const std::uint8_t expected[25] = {
        0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0x80,
        0, 0x80, 0, 0x80, 0xFF, 0x7F, 0x81, 0x7F, 0, 0, 0, 0, 0
    };
    logframe::FrameBytes bytes;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::CLAMPED);
    checkFrameBytes(bytes, expected);
}

TEST_CASE("B15 every numeric field individually reports finite clipping") {
    float logframe::FrameInput::* const fields[] = {
        &logframe::FrameInput::heading_deg, &logframe::FrameInput::gyro_z_dps,
        &logframe::FrameInput::ax_g, &logframe::FrameInput::ay_g,
        &logframe::FrameInput::duty_l, &logframe::FrameInput::duty_r,
        &logframe::FrameInput::vbat_v
    };
    for (auto field : fields) {
        for (float sign : {-1.0F, 1.0F}) {
            logframe::FrameInput input;
            input.*field = sign * std::numeric_limits<float>::max();
            logframe::FrameBytes bytes;
            CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::CLAMPED);
        }
    }
    logframe::FrameInput input;
    logframe::FrameBytes bytes;
    input.tick_max_us = 65535U;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    CHECK(bytes.data[23] == 0xFFU); CHECK(bytes.data[24] == 0xFFU);
    input.tick_max_us = 65536U;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::CLAMPED);
    CHECK(bytes.data[23] == 0xFFU); CHECK(bytes.data[24] == 0xFFU);
}

TEST_CASE("B15 legal full duty endpoints encode 127 and minus127 never minus128") {
    logframe::FrameInput input;
    logframe::FrameBytes bytes;
    input.duty_l = 1.0F;
    input.duty_r = -1.0F;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
    CHECK(bytes.data[18] == 0x7FU); CHECK(bytes.data[19] == 0x81U);
    input.duty_l = 1.01F;
    input.duty_r = -1.01F;
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::CLAMPED);
    CHECK(bytes.data[18] == 0x7FU); CHECK(bytes.data[19] == 0x81U);
}

TEST_CASE("B15 NaN and both infinities in every float field invalidate whole frame") {
    float logframe::FrameInput::* const fields[] = {
        &logframe::FrameInput::heading_deg, &logframe::FrameInput::gyro_z_dps,
        &logframe::FrameInput::ax_g, &logframe::FrameInput::ay_g,
        &logframe::FrameInput::duty_l, &logframe::FrameInput::duty_r,
        &logframe::FrameInput::vbat_v
    };
    for (auto field : fields) {
        for (float invalid : {std::numeric_limits<float>::quiet_NaN(),
                              std::numeric_limits<float>::infinity(),
                              -std::numeric_limits<float>::infinity()}) {
            auto input = halfFrame();
            input.t_ms = 0x12345678U;
            input.*field = invalid;
            checkInvalidFrame(input);
        }
    }
}

TEST_CASE("B15 every valid State enum retains its documented code") {
    const core::State states[] = {
        core::State::BOOT, core::State::IDLE, core::State::COUNTDOWN,
        core::State::OPENER, core::State::SEARCH, core::State::TRACK,
        core::State::ATTACK, core::State::DEFEND_TURN, core::State::EDGE_ESCAPE,
        core::State::REFLANK, core::State::STOPPED, core::State::DRIVE_TEST
    };
    for (unsigned index = 0U; index < 12U; ++index) {
        logframe::FrameInput input;
        logframe::FrameBytes bytes;
        input.state = states[index];
        CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
        CHECK(bytes.data[4] == index);
    }
    for (unsigned code = 12U; code <= 255U; ++code) {
        logframe::FrameInput input;
        input.state = static_cast<core::State>(code);
        checkInvalidFrame(input);
    }
}

TEST_CASE("B15 every valid Mode enum retains its documented code") {
    const core::Mode modes[] = {
        core::Mode::SIDESTEP_R, core::Mode::SIDESTEP_L, core::Mode::DIRECT,
        core::Mode::ARC_R, core::Mode::ARC_L, core::Mode::WAIT
    };
    for (unsigned index = 0U; index < 6U; ++index) {
        logframe::FrameInput input;
        logframe::FrameBytes bytes;
        input.mode = modes[index];
        CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
        CHECK(bytes.data[5] == index + 1U);
    }
    for (unsigned code = 0U; code <= 255U; ++code) {
        if (code >= 1U && code <= 6U) continue;
        logframe::FrameInput input;
        input.mode = static_cast<core::Mode>(code);
        checkInvalidFrame(input);
    }
}

TEST_CASE("B0 B15 all line opponent and flag masks enforce their exact widths") {
    for (unsigned mask = 0U; mask <= 255U; ++mask) {
        logframe::FrameInput input;
        logframe::FrameBytes bytes;
        input.line_mask = static_cast<std::uint8_t>(mask);
        if (mask <= 15U) {
            CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
            CHECK(bytes.data[6] == mask);
        } else checkInvalidFrame(input);
        input.line_mask = 0U;
        input.opp_mask = static_cast<std::uint8_t>(mask);
        if (mask <= 127U) {
            CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
            CHECK(bytes.data[7] == mask);
        } else checkInvalidFrame(input);
        input.opp_mask = 0U;
        input.flags = static_cast<std::uint8_t>(mask);
        if (mask <= 15U) {
            CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::OK);
            CHECK(bytes.data[22] == mask);
        } else checkInvalidFrame(input);
    }
    CHECK(logframe::IMU_OK == 1U); CHECK(logframe::PHANTOM_ACTIVE == 2U);
    CHECK(logframe::STUCK == 4U); CHECK(logframe::CAL_REJECTED == 8U);
}

TEST_CASE("B15 invalid dominates simultaneous finite clipping and clears old data") {
    auto input = halfFrame();
    input.heading_deg = std::numeric_limits<float>::max();
    input.flags = 0x80U;
    checkInvalidFrame(input);
    input.flags = 0U;
    input.ay_g = std::numeric_limits<float>::quiet_NaN();
    checkInvalidFrame(input);
    logframe::FrameBytes bytes;
    CHECK(logframe::packFrame(halfFrame(), bytes) == logframe::PackStatus::OK);
    CHECK(logframe::packFrame(input, bytes) == logframe::PackStatus::INVALID);
    for (auto byte : bytes.data) CHECK(byte == 0U);
    CHECK(logframe::packFrame(halfFrame(), bytes) == logframe::PackStatus::OK);
    CHECK(bytes.data[8] == 13U);
}

TEST_CASE("B15 event populated golden preserves exact tick detail and 16 bit value") {
    logframe::EventInput input;
    input.t_us = 0x12345678U;
    input.type = core::Event::PHANTOM_SET;
    input.detail = 0xFEU;
    input.value = 0xABCDU;
    const std::uint8_t expected[8] = {0x78, 0x56, 0x34, 0x12, 8, 0xFE, 0xCD, 0xAB};
    logframe::EventBytes bytes;
    CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
    checkEventBytes(bytes, expected);
}

TEST_CASE("B15 event exact tick survives adjacent microseconds and natural wrap") {
    const std::uint32_t ticks[] = {0xFFFFFFFEU, 0xFFFFFFFFU, 0U, 1U, 999U, 1000U, 1001U};
    const std::uint8_t expected[][4] = {
        {0xFE, 0xFF, 0xFF, 0xFF}, {0xFF, 0xFF, 0xFF, 0xFF}, {0, 0, 0, 0},
        {1, 0, 0, 0}, {0xE7, 3, 0, 0}, {0xE8, 3, 0, 0}, {0xE9, 3, 0, 0}
    };
    for (unsigned index = 0U; index < 7U; ++index) {
        logframe::EventInput input;
        logframe::EventBytes bytes;
        input.t_us = ticks[index];
        CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
        for (unsigned byte = 0U; byte < 4U; ++byte) CHECK(bytes.data[byte] == expected[index][byte]);
        for (unsigned byte = 4U; byte < 8U; ++byte) CHECK(bytes.data[byte] == 0U);
    }
}

TEST_CASE("B15 every Event enum retains its code and all unknown codes invalidate") {
    const core::Event events[] = {
        core::Event::START_RELEASE, core::Event::GO, core::Event::FIRST_NONZERO_DUTY,
        core::Event::STATE_CHANGE, core::Event::EDGE, core::Event::CONTACT,
        core::Event::STALL, core::Event::REFLANK_PHASE, core::Event::PHANTOM_SET,
        core::Event::FAULT
    };
    for (unsigned index = 0U; index < 10U; ++index) {
        logframe::EventInput input;
        logframe::EventBytes bytes;
        input.type = events[index];
        input.detail = 0xFFU;
        input.value = 0xFFFFU;
        CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
        CHECK(bytes.data[4] == index); CHECK(bytes.data[5] == 0xFFU);
        CHECK(bytes.data[6] == 0xFFU); CHECK(bytes.data[7] == 0xFFU);
    }
    for (unsigned code = 10U; code <= 255U; ++code) {
        logframe::EventInput input;
        input.t_us = 0x12345678U;
        input.detail = 0xFFU;
        input.value = 0xFFFFU;
        input.type = static_cast<core::Event>(code);
        checkInvalidEvent(input);
    }
}

TEST_CASE("B15 event defaults and repeated packing overwrite every destination byte") {
    logframe::EventBytes bytes;
    for (auto byte : bytes.data) CHECK(byte == 0U);
    logframe::EventInput input;
    CHECK(input.type == core::Event::START_RELEASE);
    CHECK(input.t_us == 0U); CHECK(input.detail == 0U); CHECK(input.value == 0U);
    for (auto& byte : bytes.data) byte = 0xFFU;
    CHECK(logframe::packEvent(input, bytes) == logframe::PackStatus::OK);
    const std::uint8_t expected[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    checkEventBytes(bytes, expected);
}

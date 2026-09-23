// Checks D108's literal B0/D076 opponent identities through public projection.
// Keeps source masks unchanged while correcting only geometric presentation.
// Independent normal/sanitizer tests compare all pixels, including unknown groups.
#include "doctest.h"
#include "hal/ui_display.h"
#include <cstdint>
#include <cstring>
#include <initializer_list>

namespace {
struct Channel { std::uint8_t mask; unsigned column; unsigned row; };
// D108: FL15, FC, FR15, SL, SR, RL, RR, in unchanged B0 bit order.
constexpr Channel CHANNELS[] = {
    {0x01U, 2U, 1U}, {0x02U, 4U, 1U}, {0x04U, 6U, 1U},
    {0x08U, 0U, 3U}, {0x10U, 8U, 3U}, {0x20U, 2U, 5U}, {0x40U, 6U, 5U},
};
struct Pair {
    fsm::RobotInput input;
    fsm::RobotResult result;
    Pair() {
        input.t_us = 123456U; input.observations_fresh = true;
        input.opponent_fresh = true; input.opp_raw_mask = 0x7fU;
        result.fresh = true; result.imu_available = true;
        result.outputs.ui_state = core::State::IDLE;
        result.menu.selection.service_menu = true;
        result.menu.selection.service = countdown::Service::SENSOR_VIEW;
        result.line_available = true;
    }
};
ui::Frame expected(std::uint8_t mask, bool available) {
    ui::Frame frame;
    for (const auto& channel : CHANNELS)
        frame.pixels[channel.row * 13U + channel.column] =
            available ? ((mask & channel.mask) ? 7U : 0U) : 3U;
    // Unchanged D088 robot outline and unavailable battery indication.
    for (unsigned index : {30U, 42U, 43U, 44U, 55U, 57U}) frame.pixels[index] = 7U;
    for (unsigned column = 0U; column < 13U; column += 2U) frame.pixels[91U + column] = 7U;
    return frame;
}
void checkFrame(const ui::DisplaySample& sample, const ui::Frame& literal) {
    ui::Frame frame; std::memset(frame.pixels, 0xa5, sizeof frame.pixels);
    CHECK(ui::render(sample, frame) == ui::RenderStatus::OK);
    for (unsigned index = 0U; index < 104U; ++index) {
        CAPTURE(index); CHECK(frame.pixels[index] == literal.pixels[index]);
    }
}
} // namespace

TEST_CASE("B0 B13 D108 each single channel reaches its literal geometric pixel without mask remap") {
    for (bool explicit_line : {false, true}) for (const auto& channel : CHANNELS) {
        Pair pair; pair.input.line.explicit_values = explicit_line;
        pair.result.opponent_mask = channel.mask;
        // Deliberately unrelated electrical bits cannot replace the result mask.
        pair.input.opp_raw_mask = static_cast<std::uint8_t>(channel.mask ^ 0x7fU);
        const auto sample = ui::displaySample(pair.input, pair.result);
        CAPTURE(channel.mask); CAPTURE(explicit_line);
        CHECK(sample.opponent_mask == channel.mask); CHECK(pair.result.opponent_mask == channel.mask);
        CHECK(pair.input.opp_raw_mask == static_cast<std::uint8_t>(channel.mask ^ 0x7fU));
        CHECK(sample.opponents_available); CHECK(sample.lines_available);
        CHECK(sample.line_mask == 0U); CHECK(sample.faults == 0U);
        CHECK(sample.state == core::State::IDLE); CHECK(sample.service == countdown::Service::SENSOR_VIEW);
        checkFrame(sample, expected(channel.mask, true));
    }
}

TEST_CASE("B0 B13 D108 unavailable opponent group retains mask but shows seven unknown coordinates") {
    for (bool explicit_line : {false, true}) for (const auto& channel : CHANNELS) {
        Pair pair; pair.input.line.explicit_values = explicit_line;
        pair.input.opponent_fresh = !explicit_line;
        pair.input.observations_fresh = explicit_line;
        pair.result.opponent_mask = channel.mask;
        const auto sample = ui::displaySample(pair.input, pair.result);
        CHECK_FALSE(sample.opponents_available); CHECK(sample.opponent_mask == channel.mask);
        CHECK(sample.lines_available); CHECK(sample.faults == 0U);
        checkFrame(sample, expected(channel.mask, false));
    }
}

TEST_CASE("B0 B13 D108 simultaneous FL15 and FC stay separate from empty and FR15") {
    for (std::uint8_t mask : {0x00U, 0x03U, 0x04U, 0x07U, 0x7fU}) {
        Pair pair; pair.input.line.explicit_values = true; pair.result.opponent_mask = mask;
        const auto sample = ui::displaySample(pair.input, pair.result);
        CHECK(sample.opponents_available); CHECK(sample.opponent_mask == mask);
        checkFrame(sample, expected(mask, true));
    }
}

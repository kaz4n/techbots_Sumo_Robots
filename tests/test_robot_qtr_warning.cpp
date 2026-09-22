// Exercises the D-060 QTR warning through real Robot and explicit applied receipts.
// A sparse next observation reports held pivot settings, not measured body rotation.
// Literal1500ms strict boundaries, actual-duty qualification and rearming are checked.
#include "robot_scenario.h"
#include <initializer_list>

using namespace robot_test;

namespace {
std::uint32_t firstPivotReceipt(Rig& rig, std::uint32_t base = 0U) {
    const auto edge_time = go(rig, Mode::WAIT, base) + 1000U;
    rig.lines(5U); // Left side row: pivot right45 degrees, then forward.
    const auto entry = rig.step(edge_time);
    CHECK(entry.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(entry.outputs.duty_l > 0.0F);
    CHECK(entry.outputs.duty_r < 0.0F);
    CHECK(entry.qtr_warning_mask == 0U);
    const auto first = rig.step(edge_time + 50000U);
    CHECK(first.outputs.duty_l > 0.0F);
    CHECK(first.outputs.duty_r < 0.0F);
    CHECK(first.qtr_warning_mask == 0U);
    return edge_time + 50000U;
}
} // namespace

TEST_CASE("B14 D060 Robot QTR pivot warning is strictly beyond1500ms including wrap") {
    for (const std::uint32_t age : {1499999U, 1500000U, 1500001U}) {
        for (const std::uint32_t base : {0U, 0U - 6414010U}) {
            Rig rig;
            const auto start = firstPivotReceipt(rig, base);
            const auto result = rig.step(start + age);
            if (base != 0U) CHECK(start + age < start);
            CHECK(result.qtr_warning_mask == (age > 1500000U ? 5U : 0U));
            CHECK(count(result, core::Event::FAULT, 3) == (age > 1500000U ? 1U : 0U));
            if (age > 1500000U) {
                const auto warning = event(result, core::Event::FAULT, 3);
                CHECK(warning.t_us == start + age);
                CHECK(warning.value == 5U);
            }
            CHECK(result.line_mask == 5U);
            CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
            CHECK(result.escape_fault == edge::EscapeFault::NONE);
            CHECK(result.contract_faults == 0U);
            CHECK(result.outputs.motors_enabled);
            CHECK(result.outputs.duty_l > 0.0F);
            CHECK(result.outputs.duty_r == 0.0F); // Current pivot timed out; reversal brakes.
            CHECK(event(result, core::Event::FAULT, 8).value == 1U);
            bounded(result);
        }
    }
}

TEST_CASE("B14 D060 Robot warning clears on nonpivot actual receipt and rearms per episode") {
    Rig rig;
    const auto start = firstPivotReceipt(rig);
    const auto warned_time = start + 1500001U;
    CHECK(rig.step(warned_time).qtr_warning_mask == 5U);
    const auto broken = rig.step(warned_time + 1U);
    CHECK(broken.qtr_warning_mask == 0U);
    CHECK(count(broken, core::Event::FAULT, 3) == 0U);
    CHECK(broken.line_mask == 5U);
    const auto replacement = rig.step(warned_time + 200000U);
    CHECK((event(replacement, core::Event::EDGE).detail & 4U) != 0U);
    rig.step(warned_time + 200001U); // Reversal-zero receipt cannot qualify.
    const auto again_start = warned_time + 250001U;
    CHECK(rig.step(again_start).qtr_warning_mask == 0U);
    const auto again = rig.step(again_start + 1500001U);
    CHECK(again.qtr_warning_mask == 5U);
    CHECK(event(again, core::Event::FAULT, 3).value == 5U);
    CHECK(again.outputs.ui_state == State::EDGE_ESCAPE);
    CHECK(again.escape_fault == edge::EscapeFault::NONE);
    CHECK(again.contract_faults == 0U);
}

TEST_CASE("B14 D060 Robot QTR warning requires actual enabled strictly opposing nonzero duties") {
    for (unsigned variant = 0U; variant < 3U; ++variant) {
        Rig rig;
        const auto start = firstPivotReceipt(rig);
        auto sample = rig.at(start + 1500001U);
        if (variant == 0U) {
            sample.previous.motors_enabled = false;
            sample.previous.duty_l = 0.0F;
            sample.previous.duty_r = 0.0F;
        }
        if (variant == 1U) sample.previous.duty_l = 0.0F;
        if (variant == 2U) sample.previous.duty_r = 0.0F;
        const auto result = rig.submit(sample);
        CHECK(result.qtr_warning_mask == 0U);
        CHECK(count(result, core::Event::FAULT, 3) == 0U);
        CHECK(result.contract_faults == 0U);
        CHECK(result.outputs.ui_state == State::EDGE_ESCAPE);
    }
}

TEST_CASE("B14 D060 Robot current black breaks warning even with a held actual pivot receipt") {
    Rig rig;
    const auto start = firstPivotReceipt(rig);
    rig.lines(0U);
    const auto result = rig.step(start + 1500001U);
    CHECK(result.line_mask == 0U);
    CHECK(result.qtr_warning_mask == 0U);
    CHECK(count(result, core::Event::FAULT, 3) == 0U);
    CHECK(result.outputs.ui_state == State::EDGE_ESCAPE); // Its forward segment is not done.
    CHECK(result.contract_faults == 0U);
}

// Tests the D119 pure B4 sequence against its contract and public interface.
// Keeps literal independent expectations separate from implementation and hardware.
// Covers every row, timing boundary, cancellation priority and finite completion.
#include "doctest.h"
#include "config.h"
#include "core/stand_sequence.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <limits>

namespace {
using stand_sequence::Phase;
using stand_sequence::Reason;
using stand_sequence::Report;
using stand_sequence::Sequence;

constexpr std::uint32_t DURATION_US = 500000U;
constexpr std::uint32_t HALF_RANGE_US = 0x80000000U;
constexpr std::uint32_t BASE_US = 17003U;
struct ExpectedRow { Phase phase; float left; float right; };
constexpr std::array<ExpectedRow, 12> ROWS{{
    {Phase::DRIVE, 0.25F, 0.0F},
    {Phase::BRAKE, 0.0F, 0.0F},
    {Phase::COAST, 0.0F, 0.0F},
    {Phase::DRIVE, -0.25F, 0.0F},
    {Phase::BRAKE, 0.0F, 0.0F},
    {Phase::COAST, 0.0F, 0.0F},
    {Phase::DRIVE, 0.0F, 0.25F},
    {Phase::BRAKE, 0.0F, 0.0F},
    {Phase::COAST, 0.0F, 0.0F},
    {Phase::DRIVE, 0.0F, -0.25F},
    {Phase::BRAKE, 0.0F, 0.0F},
    {Phase::COAST, 0.0F, 0.0F}
}};

// No-exception doctest cannot abort REQUIRE; keep these prerequisites fatal.
void requireCondition(bool condition) {
    CHECK(condition);
    if (!condition) std::abort();
}

void checkBounded(const Report& report) {
    CHECK(std::isfinite(report.duty_l));
    CHECK(std::isfinite(report.duty_r));
    CHECK(std::fabs(report.duty_l) <= 0.25F);
    CHECK(std::fabs(report.duty_r) <= 0.25F);
    CHECK((report.duty_l == 0.0F || report.duty_r == 0.0F));
    CHECK(report.segment <= 12U);
}

void checkSame(const Report& actual, const Report& expected) {
    CHECK(actual.phase == expected.phase);
    CHECK(actual.reason == expected.reason);
    CHECK(actual.segment == expected.segment);
    CHECK(actual.duty_l == expected.duty_l);
    CHECK(actual.duty_r == expected.duty_r);
    CHECK(actual.fresh == expected.fresh);
    CHECK(actual.phase_changed == expected.phase_changed);
    checkBounded(actual);
}

void checkRow(const Report& report, unsigned row, bool fresh, bool changed) {
    requireCondition(row < ROWS.size());
    CHECK(report.phase == ROWS[row].phase);
    CHECK(report.reason == Reason::NONE);
    CHECK(report.segment == row);
    CHECK(report.duty_l == ROWS[row].left);
    CHECK(report.duty_r == ROWS[row].right);
    CHECK(report.fresh == fresh);
    CHECK(report.phase_changed == changed);
    checkBounded(report);
}

void checkTerminal(const Report& report, Phase phase, Reason reason,
                   unsigned row, bool fresh, bool changed) {
    CHECK(report.phase == phase);
    CHECK(report.reason == reason);
    CHECK(report.segment == row);
    CHECK(report.duty_l == 0.0F);
    CHECK(report.duty_r == 0.0F);
    CHECK(report.fresh == fresh);
    CHECK(report.phase_changed == changed);
    checkBounded(report);
}

std::uint32_t enterRow(Sequence& sequence, unsigned row,
                       std::uint32_t start = BASE_US) {
    requireCondition(row < ROWS.size());
    requireCondition(sequence.start(start));
    checkRow(sequence.report(), 0U, true, true);
    for (unsigned current = 0U; current < row; ++current) {
        const auto boundary = start + (current + 1U) * DURATION_US;
        checkRow(sequence.step(boundary - 1U), current, true, false);
        checkRow(sequence.step(boundary), current + 1U, true, true);
    }
    return start + row * DURATION_US;
}

void checkNext(const Report& report, unsigned previous) {
    if (previous == 11U) {
        checkTerminal(report, Phase::COMPLETE, Reason::NONE, 12U, true, true);
    } else {
        checkRow(report, previous + 1U, true, true);
    }
}

void checkPassiveTerminal(Sequence& sequence, const Report& terminal,
                          std::uint32_t terminal_time) {
    for (unsigned repeat = 0U; repeat < 3U; ++repeat) {
        checkSame(sequence.report(), terminal);
    }
    CHECK_FALSE(sequence.start(terminal_time + 100U));
    checkSame(sequence.report(), terminal);
    auto passive = terminal;
    passive.fresh = false;
    passive.phase_changed = false;
    for (const auto delta : {0U, 1U, DURATION_US, HALF_RANGE_US,
                             std::numeric_limits<std::uint32_t>::max()}) {
        checkSame(sequence.step(terminal_time + delta, true, true), passive);
        CHECK_FALSE(sequence.start(terminal_time - delta));
        checkSame(sequence.report(), passive);
    }
}
} // namespace

TEST_CASE("P2 B4 D119 independent defaults and finite configuration bounds") {
    CHECK(config::STAND_SEGMENT_MS == 500U);
    CHECK(config::STAND_DUTY == 0.25F);
    CHECK(config::STAND_SEGMENT_MS > 0U);
    CHECK(config::STAND_DUTY > 0.0F);
    CHECK(config::STAND_DUTY < 1.0F);
    CHECK(12ULL * 2ULL * config::STAND_SEGMENT_MS * 1000ULL < HALF_RANGE_US);
    CHECK(12U * DURATION_US == 6000000U);
}

TEST_CASE("P2 B4 D119 not started is passive for every kind of input") {
    Sequence sequence;
    const Report empty;
    checkSame(sequence.report(), empty);
    for (const auto time : {0U, 1U, HALF_RANGE_US, 0xffffffffU, BASE_US}) {
        checkSame(sequence.step(time, true, true), empty);
        checkSame(sequence.report(), empty);
    }
    requireCondition(sequence.start(0U));
    checkRow(sequence.report(), 0U, true, true);
    checkRow(sequence.step(1U), 0U, true, false);
}

TEST_CASE("P2 B4 D119 refused active start changes neither pulses nor time anchors") {
    Sequence sequence;
    requireCondition(sequence.start(BASE_US));
    const auto started = sequence.report();
    for (const auto time : {BASE_US, BASE_US - 1U, BASE_US + HALF_RANGE_US}) {
        CHECK_FALSE(sequence.start(time));
        checkSame(sequence.report(), started);
    }
    checkRow(sequence.step(BASE_US + DURATION_US - 1U), 0U, true, false);
    const auto observed = sequence.report();
    CHECK_FALSE(sequence.start(BASE_US + 42U));
    checkSame(sequence.report(), observed);
    checkRow(sequence.step(BASE_US + DURATION_US), 1U, true, true);
}

TEST_CASE("P2 B4 D119 literal twelve rows finish at exactly six nominal seconds") {
    for (const auto start : {0U, BASE_US, 0xffe00000U}) {
        Sequence sequence;
        requireCondition(sequence.start(start));
        checkRow(sequence.report(), 0U, true, true);
        for (unsigned row = 0U; row < ROWS.size(); ++row) {
            CAPTURE(start);
            CAPTURE(row);
            const auto boundary = start + (row + 1U) * DURATION_US;
            checkRow(sequence.step(boundary - 1U), row, true, false);
            checkNext(sequence.step(boundary), row);
        }
        checkTerminal(sequence.report(), Phase::COMPLETE, Reason::NONE,
                      12U, true, true);
        checkPassiveTerminal(sequence, sequence.report(), start + 6000000U);
    }
}

TEST_CASE("P2 B4 D119 every transition distinguishes duration minus one exact and plus one") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        for (const auto offset : {DURATION_US - 1U, DURATION_US, DURATION_US + 1U}) {
            CAPTURE(row);
            CAPTURE(offset);
            Sequence sequence;
            const auto entered = enterRow(sequence, row);
            checkRow(sequence.step(entered + DURATION_US - 2U), row, true, false);
            const auto report = sequence.step(entered + offset);
            if (offset < DURATION_US) {
                checkRow(report, row, true, false);
            } else {
                checkNext(report, row);
            }
        }
    }
}

TEST_CASE("P2 B4 D119 delayed observation anchors the following complete interval now") {
    Sequence sequence;
    requireCondition(sequence.start(BASE_US));
    checkRow(sequence.step(BASE_US + DURATION_US - 1U), 0U, true, false);
    const auto delayed = BASE_US + 2U * DURATION_US - 2U;
    checkRow(sequence.step(delayed), 1U, true, true);
    checkRow(sequence.step(BASE_US + 2U * DURATION_US), 1U, true, false);
    checkRow(sequence.step(delayed + DURATION_US - 1U), 1U, true, false);
    checkRow(sequence.step(delayed + DURATION_US), 2U, true, true);
    checkRow(sequence.step(delayed + 2U * DURATION_US - 1U), 2U, true, false);
    checkRow(sequence.step(delayed + 2U * DURATION_US), 3U, true, true);
}

TEST_CASE("P2 B4 D119 every row is bounded below two durations with latest legal observations") {
    for (const auto start : {BASE_US, 0xfffffff0U}) {
        Sequence sequence;
        requireCondition(sequence.start(start));
        auto entered = start;
        for (unsigned row = 0U; row < ROWS.size(); ++row) {
            CAPTURE(start);
            CAPTURE(row);
            checkRow(sequence.step(entered + DURATION_US - 1U), row, true, false);
            const auto next = entered + 2U * DURATION_US - 2U;
            checkNext(sequence.step(next), row);
            CHECK(static_cast<std::uint32_t>(next - entered) < 2U * DURATION_US);
            entered = next;
        }
        CHECK(static_cast<std::uint32_t>(entered - start) == 11999976U);
        checkTerminal(sequence.report(), Phase::COMPLETE, Reason::NONE,
                      12U, true, true);
    }
}

TEST_CASE("P2 B4 D119 distinct observation cadence gives finite bounded output without row skips") {
    for (const auto cadence : {1000U, 166667U, 499999U}) {
        Sequence sequence;
        requireCondition(sequence.start(BASE_US));
        unsigned previous_row = 0U;
        std::uint32_t elapsed = 0U;
        while (elapsed < 12000000U && sequence.report().phase != Phase::COMPLETE) {
            elapsed += cadence;
            const auto report = sequence.step(BASE_US + elapsed);
            checkBounded(report);
            CHECK(report.reason == Reason::NONE);
            CHECK(report.fresh);
            CHECK(report.segment >= previous_row);
            CHECK(report.segment <= previous_row + 1U);
            CHECK(report.phase_changed == (report.segment != previous_row));
            if (report.segment < ROWS.size()) {
                checkRow(report, report.segment, true, report.segment != previous_row);
            }
            previous_row = report.segment;
        }
        CHECK(elapsed >= 6000000U);
        CHECK(elapsed < 12000000U);
        checkTerminal(sequence.report(), Phase::COMPLETE, Reason::NONE,
                      12U, true, true);
    }
}

TEST_CASE("P2 B4 D119 gap admission is strict at every row including final coast") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        for (const auto gap : {DURATION_US - 1U, DURATION_US,
                               DURATION_US + 1U, HALF_RANGE_US - 1U}) {
            CAPTURE(row);
            CAPTURE(gap);
            Sequence sequence;
            const auto entered = enterRow(sequence, row);
            const auto report = sequence.step(entered + gap);
            if (gap < DURATION_US) {
                checkRow(report, row, true, false);
            } else {
                checkTerminal(report, Phase::FAULT, Reason::CLOCK_GAP,
                              row, true, true);
            }
        }
    }
}

TEST_CASE("P2 B4 D119 backward and half range clocks fault before stop edge or gap") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        for (const auto gap : {HALF_RANGE_US, HALF_RANGE_US + 1U, 0xffffffffU}) {
            for (unsigned flags = 0U; flags < 4U; ++flags) {
                CAPTURE(row);
                CAPTURE(gap);
                CAPTURE(flags);
                Sequence sequence;
                const auto entered = enterRow(sequence, row);
                const auto report = sequence.step(entered + gap, (flags & 1U) != 0U,
                                                   (flags & 2U) != 0U);
                checkTerminal(report, Phase::FAULT, Reason::CLOCK_ORDER,
                              row, true, true);
            }
        }
    }
}

TEST_CASE("P2 B4 D119 stop wins edge and legal or excessive clock gaps in every row") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        for (const auto delta : {1U, DURATION_US - 1U, DURATION_US,
                                 DURATION_US + 1U, HALF_RANGE_US - 1U}) {
            for (const auto edge : {false, true}) {
                CAPTURE(row);
                CAPTURE(delta);
                CAPTURE(edge);
                Sequence sequence;
                const auto entered = enterRow(sequence, row);
                checkTerminal(sequence.step(entered + delta, edge, true),
                              Phase::INTERRUPTED, Reason::STOP, row, true, true);
            }
        }
    }
}

TEST_CASE("P2 B4 D119 edge cancels before legal or excessive clock gaps in every row") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        for (const auto delta : {1U, DURATION_US - 1U, DURATION_US,
                                 DURATION_US + 1U, HALF_RANGE_US - 1U}) {
            CAPTURE(row);
            CAPTURE(delta);
            Sequence sequence;
            const auto entered = enterRow(sequence, row);
            checkTerminal(sequence.step(entered + delta, true, false),
                          Phase::INTERRUPTED, Reason::EDGE, row, true, true);
        }
    }
}

TEST_CASE("P2 B4 D119 stop and edge preempt an otherwise admitted exact row transition") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        for (unsigned flags = 1U; flags < 4U; ++flags) {
            CAPTURE(row);
            CAPTURE(flags);
            Sequence sequence;
            const auto entered = enterRow(sequence, row);
            checkRow(sequence.step(entered + DURATION_US - 1U), row, true, false);
            const auto reason = (flags & 2U) != 0U ? Reason::STOP : Reason::EDGE;
            checkTerminal(sequence.step(entered + DURATION_US, (flags & 1U) != 0U,
                                        (flags & 2U) != 0U),
                          Phase::INTERRUPTED, reason, row, true, true);
        }
    }
}

TEST_CASE("P2 B4 D119 duplicate observations suppress changed inputs and only clear pulses") {
    for (unsigned row = 0U; row < ROWS.size(); ++row) {
        Sequence sequence;
        const auto entered = enterRow(sequence, row);
        for (unsigned flags = 0U; flags < 4U; ++flags) {
            checkRow(sequence.step(entered, (flags & 1U) != 0U, (flags & 2U) != 0U),
                     row, false, false);
        }
        CHECK_FALSE(sequence.start(entered + 100U));
        checkRow(sequence.report(), row, false, false);
        checkRow(sequence.step(entered + 1U), row, true, false);
        checkRow(sequence.step(entered + DURATION_US - 1U), row, true, false);
        checkRow(sequence.step(entered + DURATION_US - 1U, true, true), row, false, false);
        checkNext(sequence.step(entered + DURATION_US), row);
    }
}

TEST_CASE("P2 B4 D119 suppressed stop is not latched but a distinct stop is admitted") {
    Sequence sequence;
    requireCondition(sequence.start(BASE_US));
    checkRow(sequence.step(BASE_US, true, true), 0U, false, false);
    checkRow(sequence.step(BASE_US + 1U), 0U, true, false);
    checkRow(sequence.step(BASE_US + 1U, false, true), 0U, false, false);
    checkTerminal(sequence.step(BASE_US + 2U, false, true),
                  Phase::INTERRUPTED, Reason::STOP, 0U, true, true);
}

TEST_CASE("P2 B4 D119 all terminal causes preserve original row reason and refuse restart") {
    for (const auto row : {0U, 3U, 7U, 11U}) {
        for (unsigned cause = 0U; cause < 4U; ++cause) {
            CAPTURE(row);
            CAPTURE(cause);
            Sequence sequence;
            const auto entered = enterRow(sequence, row);
            const std::array<std::uint32_t, 4> deltas{{1U, 1U, HALF_RANGE_US, DURATION_US}};
            const std::array<Reason, 4> reasons{{Reason::STOP, Reason::EDGE,
                                               Reason::CLOCK_ORDER, Reason::CLOCK_GAP}};
            const auto time = entered + deltas[cause];
            const auto report = sequence.step(time, cause == 1U, cause == 0U);
            checkTerminal(report, cause < 2U ? Phase::INTERRUPTED : Phase::FAULT,
                          reasons[cause], row, true, true);
            checkPassiveTerminal(sequence, report, time);
        }
    }
}

TEST_CASE("P2 B4 D119 rejected start cannot erase a previously admitted gap predecessor") {
    Sequence sequence;
    requireCondition(sequence.start(BASE_US));
    checkRow(sequence.step(BASE_US + 400000U), 0U, true, false);
    CHECK_FALSE(sequence.start(BASE_US + 899999U));
    checkTerminal(sequence.step(BASE_US + 900000U), Phase::FAULT,
                  Reason::CLOCK_GAP, 0U, true, true);
}

TEST_CASE("P2 B4 D119 wrap is admitted by unsigned delta while a true reverse clock is refused") {
    Sequence sequence;
    requireCondition(sequence.start(0xfffffff0U));
    checkRow(sequence.step(0xffffffffU), 0U, true, false);
    checkRow(sequence.step(0U), 0U, true, false);
    checkRow(sequence.step(1U), 0U, true, false);
    checkTerminal(sequence.step(0U, true, true), Phase::FAULT,
                  Reason::CLOCK_ORDER, 0U, true, true);
}

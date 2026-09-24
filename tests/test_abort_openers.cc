// Tests D135 per-call opener evidence against B12 predicates and completion rules.
// Separates current detection, saved snapshot, natural completion and internal cues.
// Isolated draft tests exhaust masks without inspecting or replaying implementation predicates.
#include "fixtures/p5_abort_fixture.h"

using namespace p5_abort;
namespace {
bool arc(unsigned mode) { return mode == 4U || mode == 5U; }
float sign(unsigned mode) { return mode == 2U || mode == 5U ? -1.0F : 1.0F; }
float pivot(unsigned mode) { return sign(mode) * (arc(mode) ? 80.0F : 50.0F); }
unsigned inner(unsigned mode) { return sign(mode) > 0.0F ? 8U : 16U; }
void prepare(openers::Flank& flank, unsigned mode, unsigned phase) {
    APP_REQUIRE(flank.start(0U, 0.0F, true, static_cast<Mode>(mode)));
    if (phase == 1U) return;
    APP_REQUIRE(flank.step(sample(1000U, 0U, pivot(mode))).phase == openers::Phase::TRAVERSE);
    if (phase == 2U) return;
    const auto r = flank.step(sample(2000U, inner(mode), pivot(mode), true, -sign(mode) * 90.0F));
    APP_REQUIRE(r.phase == openers::Phase::TURN_IN); CHECK(r.abort.cause == Cause::NONE);
}
void beginWaitFlank(openers::Wait& wait, unsigned phase) {
    APP_REQUIRE(wait.start(0U, 0.0F)); wait.step(sample(1U, 2U));
    const auto cue = wait.step(sample(2U, 3U)); APP_REQUIRE(cue.approach_cue);
    CHECK(cue.flank.abort.cause == Cause::NONE);
    if (phase == 1U) return;
    APP_REQUIRE(wait.step(sample(3U, 0U, 50.0F)).flank.phase == openers::Phase::TRAVERSE);
    if (phase == 2U) return;
    APP_REQUIRE(wait.step(sample(4U, 8U, 50.0F)).flank.phase == openers::Phase::TURN_IN);
}
void zero(const motion::Result& result) {
    CHECK(result.duty_l == 0.0F); CHECK(result.duty_r == 0.0F);
}
} // namespace

TEST_CASE("B12 D135 DIRECT all128 snapshot by128 current combinations identify actual winning cause") {
    for (unsigned snapshot = 0U; snapshot < 128U; ++snapshot) for (unsigned mask = 0U; mask < 128U; ++mask) {
        openers::Direct direct; APP_REQUIRE(direct.start(0U, 0.0F, static_cast<std::uint8_t>(snapshot)));
        const auto r = direct.step(1000U, 0.0F, true, static_cast<std::uint8_t>(mask));
        const bool saved = (snapshot & 7U) != 0U;
        const Cause cause = mask & 7U ? Cause::CURRENT_FRONT : saved ? Cause::SNAPSHOT_ONLY :
                            mask & 0x78U ? Cause::CURRENT_SIDE_OR_REAR : Cause::NONE;
        CHECK(r.abort.cause == cause);
        if (cause != Cause::NONE) {
            pulse(r.abort, Phase::DIRECT, cause, mask, saved); zero(r.motion);
            CHECK(direct.step(1000U, 0.0F, true, 127U).abort.cause == Cause::NONE);
            CHECK(direct.step(2000U, 0.0F, true, 127U).abort.cause == Cause::NONE);
        }
    }
}

TEST_CASE("B12 D135 DIRECT detection wins deadline but target-free expiry is one natural pulse") {
    for (auto elapsed : {399999U, 400000U, 400001U}) for (unsigned mask : {0U, 2U, 8U, 10U}) {
        openers::Direct direct; APP_REQUIRE(direct.start(0xffff0000U, 0.0F, 0U));
        const auto r = direct.step(0xffff0000U + elapsed, 0.0F, true, static_cast<std::uint8_t>(mask));
        const auto cause = mask & 7U ? Cause::CURRENT_FRONT : mask ? Cause::CURRENT_SIDE_OR_REAR :
                           elapsed >= 400000U ? Cause::NATURAL_END : Cause::NONE;
        CHECK(r.abort.cause == cause);
        if (cause != Cause::NONE) pulse(r.abort, Phase::DIRECT, cause, mask);
    }
    openers::Direct invalid; CHECK_FALSE(invalid.start(0U, std::numeric_limits<float>::quiet_NaN(), 2U));
    CHECK(invalid.step(1U, 0.0F, true, 127U).abort.cause == Cause::NONE);
}

TEST_CASE("B12 D033 D135 every available flank phase and mask preserves exact predicate evidence") {
    for (unsigned mode : {1U, 2U, 4U, 5U}) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        for (unsigned phase = 1U; phase <= 3U; ++phase) for (unsigned mask = 0U; mask < 128U; ++mask) {
            openers::Flank flank; prepare(flank, mode, phase);
            const auto r = flank.step(sample(3000U, mask, phase == 1U ? 0.0F : pivot(mode),
                                             true, -sign(mode) * 90.0F));
            Cause cause = Cause::NONE;
            if (permittedCue(mode, phase, 1U, mask, false)) cause = Cause::CURRENT_FRONT;
            else if (permittedCue(mode, phase, 2U, mask, false)) cause = Cause::CURRENT_SIDE_OR_REAR;
            CHECK(r.abort.cause == cause);
            if (cause != Cause::NONE) {
                pulse(r.abort, static_cast<Phase>(phase), cause, mask); zero(r.motion);
                CHECK(flank.step(sample(4000U, 127U)).abort.cause == Cause::NONE);
            }
        }
    }
}

TEST_CASE("B12 D135 same-call phase advancement records predicate phase not terminal or entry phase") {
    for (unsigned mode : {1U, 2U, 4U, 5U}) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        for (bool with_outer : {false, true}) {
            openers::Flank flank; prepare(flank, mode, 1U);
            const unsigned mask = 2U | (with_outer ? (sign(mode) > 0.0F ? 16U : 8U) : 0U);
            const auto r = flank.step(sample(1000U, mask, pivot(mode)));
            const bool old_phase_wins = with_outer && !arc(mode);
            pulse(r.abort, old_phase_wins ? Phase::PIVOT : Phase::TRAVERSE,
                  old_phase_wins ? Cause::CURRENT_SIDE_OR_REAR : Cause::CURRENT_FRONT, mask);
            CHECK(r.phase == openers::Phase::FINISHED); zero(r.motion);
        }
    }
}

TEST_CASE("B12 D135 flank inner transition and continuing timeout are not terminal aborts") {
    for (unsigned mode : {1U, 2U, 4U, 5U}) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        openers::Flank flank; prepare(flank, mode, 2U);
        auto r = flank.step(sample(2000U, inner(mode), pivot(mode), true, -sign(mode) * 90.0F));
        CHECK(r.phase == openers::Phase::TURN_IN); CHECK(r.abort.cause == Cause::NONE);
        const auto target = pivot(mode) - sign(mode) * (arc(mode) ? 90.0F : 110.0F);
        r = flank.step(sample(3000U, inner(mode), target));
        CHECK(r.exit == openers::Exit::SIDE_OR_REAR_TARGET);
        pulse(r.abort, Phase::TURN_IN, Cause::NATURAL_END, inner(mode));
        CHECK(flank.step(sample(4000U, 127U)).abort.cause == Cause::NONE);
        openers::Flank timeout; prepare(timeout, mode, 1U);
        r = timeout.step(sample(700000U)); CHECK(r.motion_timed_out);
        CHECK(r.phase == openers::Phase::TRAVERSE); CHECK(r.abort.cause == Cause::NONE);
    }
}

TEST_CASE("B12 D135 ARC natural expiry with outer target continues while no target ends naturally") {
    for (unsigned mode : {4U, 5U}) {
        if (!core::modeAvailable(static_cast<Mode>(mode))) continue;
        for (bool target : {false, true}) {
            openers::Flank flank; prepare(flank, mode, 2U);
            const auto mask = target ? (mode == 4U ? 16U : 8U) : 0U;
            const auto r = flank.step(sample(1501000U, mask, pivot(mode), true, sign(mode) * 90.0F));
            CHECK(r.motion_timed_out);
            if (target) { CHECK(r.phase == openers::Phase::TURN_IN); CHECK(r.abort.cause == Cause::NONE); }
            else pulse(r.abort, Phase::TRAVERSE, Cause::NATURAL_END, 0U);
        }
    }
}

TEST_CASE("B12 D055 D135 WAIT HOLD all128 masks separate side abort front hold and natural deadline") {
    if (!core::modeAvailable(Mode::WAIT)) return;
    for (unsigned mask = 0U; mask < 128U; ++mask) {
        openers::Wait wait; APP_REQUIRE(wait.start(0U, 0.0F));
        const auto r = wait.step(sample(1000U, mask));
        if ((mask & 0x78U) != 0U) pulse(r.flank.abort, Phase::WAIT_HOLD, Cause::CURRENT_SIDE_OR_REAR, mask);
        else {
            CHECK(r.flank.abort.cause == Cause::NONE); CHECK(r.phase == openers::WaitPhase::HOLD);
            const auto end = wait.step(sample(2000000U, mask));
            pulse(end.flank.abort, Phase::WAIT_HOLD, Cause::NATURAL_END, mask);
        }
        CHECK(wait.step(sample(2000001U, 127U)).flank.abort.cause == Cause::NONE);
    }
}

TEST_CASE("B12 D055 D135 WAIT ordered cue is not an abort and full flank preserves its own phase") {
    if (!core::modeAvailable(Mode::WAIT)) return;
    for (unsigned phase = 1U; phase <= 3U; ++phase) for (unsigned mask = 0U; mask < 128U; ++mask) {
        openers::Wait wait; beginWaitFlank(wait, phase);
        const auto r = wait.step(sample(10U, mask, phase == 1U ? 0.0F : 50.0F));
        Cause cause = Cause::NONE;
        if (permittedCue(6U, phase, 1U, mask, false)) cause = Cause::CURRENT_FRONT;
        else if (permittedCue(6U, phase, 2U, mask, false)) cause = Cause::CURRENT_SIDE_OR_REAR;
        CHECK(r.flank.abort.cause == cause); CHECK_FALSE(r.approach_cue);
        if (cause != Cause::NONE) pulse(r.flank.abort, static_cast<Phase>(phase), cause, mask);
    }
}

TEST_CASE("B12 B13 D135 inactive reset invalid and disabled scripts never publish a detection pulse") {
    openers::Direct direct; CHECK(direct.step(0U, 0.0F, true, 127U).abort.cause == Cause::NONE);
    APP_REQUIRE(direct.start(0U, 0.0F, 0U)); direct.reset();
    CHECK(direct.step(1000U, 0.0F, true, 127U).abort.cause == Cause::NONE);
    for (unsigned mode : {1U, 2U, 4U, 5U}) {
        openers::Flank flank; CHECK(flank.step(sample(0U, 127U)).abort.cause == Cause::NONE);
        const bool available = core::modeAvailable(static_cast<Mode>(mode));
        CHECK(flank.start(0U, 0.0F, true, static_cast<Mode>(mode)) == available);
        if (!available) {
            const auto r = flank.step(sample(1000U, 127U)); CHECK(r.exit == openers::Exit::INVALID);
            CHECK(r.abort.cause == Cause::NONE); zero(r.motion);
        }
        flank.reset(); CHECK(flank.step(sample(2000U, 127U)).abort.cause == Cause::NONE);
    }
    openers::Wait wait; CHECK(wait.step(sample(0U, 127U)).flank.abort.cause == Cause::NONE);
    const bool available = core::modeAvailable(Mode::WAIT); CHECK(wait.start(0U, 0.0F) == available);
    if (!available) {
        const auto r = wait.step(sample(1000U, 127U)); CHECK(r.phase == openers::WaitPhase::INVALID);
        CHECK(r.flank.abort.cause == Cause::NONE); zero(r.flank.motion);
    }
    wait.reset(); CHECK(wait.step(sample(2000U, 127U)).flank.abort.cause == Cause::NONE);
}

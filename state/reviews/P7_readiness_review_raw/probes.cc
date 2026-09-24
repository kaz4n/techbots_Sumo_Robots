// Reviews D138 current-transaction identity at the actual matrix callback.
// Keeps pre-completion observations and a frozen terminal frame distinct.
// Run with existing configured M0/M1 Runtime targets, normal and sanitizer.
#include "doctest.h"
#include "fixtures/app_runtime_fixture.h"

#ifdef APP_TEST_CONFIGURED_BUTTONS
namespace readiness_review {
bool readyGlyph(const ui::Frame& frame) {
    constexpr unsigned rows[] = {6U,5U,6U,5U,5U};
    for (unsigned y = 0U; y < 5U; ++y)
        for (unsigned x = 0U; x < 3U; ++x)
            if (frame.pixels[(y + 1U) * 13U + 10U + x] !=
                ((rows[y] & (4U >> x)) != 0U ? 7U : 0U)) return false;
    return true;
}
struct Source : runtime_test::Fake {
    app::Runtime* owner = nullptr;
    ui::Frame submitted;
    unsigned submissions = 0U, eligible_submissions = 0U, lit_submissions = 0U;
    bool reverse_after_submit = false;
    static Source& self(void* c) { return *static_cast<Source*>(c); }
    static power::Sample battery(void* c) {
        auto& f = self(c); f.note(runtime_test::Call::BATTERY); ++f.batteries;
        const auto started = f.now; f.now += f.adc_work;
        constexpr std::uint16_t raw = 11000U;
        const float voltage = float(raw) / 16383.0F *
            config::VBAT_ADC_REFERENCE_V * config::VBAT_DIVIDER_RATIO;
        return {power::Status::OK,power::Shutdown::NOT_ATTEMPTED,
            raw,started,f.now,voltage,true};
    }
    static ui::MatrixStatus matrix(void* c, std::uint32_t time, const ui::Frame& frame) {
        auto& f = self(c); f.submitted = frame; ++f.submissions;
        const auto& tx = f.owner->transaction().report();
        CHECK(tx.phase == app::Phase::DECIDED);
        CHECK(tx.decision_made); CHECK_FALSE(tx.finished); CHECK_FALSE(tx.timing_valid);
        CHECK(tx.completed_us == 0U); CHECK(tx.robot.fresh);
        CHECK(tx.robot.token != 0U); CHECK(tx.applied.consumed);
        CHECK(tx.applied.feedback.applied_valid);
        CHECK(tx.applied.feedback.token == tx.robot.token);
        CHECK_FALSE(tx.applied.feedback.duration_valid);
        CHECK(f.owner->decisionInput().t_us == tx.decision_us);
        if (tx.robot.match_start_eligible) ++f.eligible_submissions;
        if (readyGlyph(frame)) {
            ++f.lit_submissions;
            CHECK(MOTORS_ALLOWED != 0); CHECK(tx.robot.match_start_eligible);
            CHECK(tx.applied.fault == motors::Fault::NONE);
            CHECK_FALSE(tx.applied.feedback.motors_enabled);
            CHECK(tx.applied.feedback.duty_l == 0.0F);
            CHECK(tx.applied.feedback.duty_r == 0.0F);
        }
        const auto status = Fake::matrix(c,time,frame);
        if (f.reverse_after_submit) f.now = time - 1U;
        return status;
    }
    power::InputPort adcPort() { return {this,Fake::adcSetup,battery,Fake::button,Fake::clock}; }
    app::SourcePort sourcePort() {
        auto p = Fake::sourcePort(); p.submitMatrix = matrix; return p;
    }
};
struct Rig {
    Source source;
    app::Runtime runtime{source.motorPort(),source.adcPort(),source.sourcePort()};
    bool begin() {
        source.owner = &runtime;
        auto grants = runtime_test::grants(true,true);
        grants.matrix_enabled = true; grants.matrix = {true,true};
        return runtime.begin(grants);
    }
    bool next() { source.now = runtime.report().next_release_us; return runtime.step(); }
};
} // namespace readiness_review

TEST_CASE("B13 D138 private actual display callback has current receipt but no completed C") {
    readiness_review::Rig rig;
    CHECK(rig.begin());
    for (unsigned i = 0U; i < 50U; ++i) CHECK(rig.next());
    CHECK(rig.source.submissions == 50U); CHECK(rig.source.eligible_submissions > 0U);
    CHECK((rig.source.lit_submissions > 0U) == (MOTORS_ALLOWED != 0));
    CHECK(rig.runtime.transaction().report().finished);
    CHECK(rig.runtime.transaction().report().timing_valid);
    CHECK_FALSE(rig.source.enabled);
}

TEST_CASE("B13 D138 private terminal clock failure can retain last frame without new submission") {
    readiness_review::Rig rig;
    CHECK(rig.begin());
    for (unsigned i = 0U; i < 50U; ++i) CHECK(rig.next());
    CHECK(readiness_review::readyGlyph(rig.source.submitted) == (MOTORS_ALLOWED != 0));
    rig.source.reverse_after_submit = true;
    const auto before = rig.source.submissions;
    CHECK_FALSE(rig.next()); CHECK(rig.source.submissions == before + 1U);
    CHECK(rig.runtime.report().phase == app::RuntimePhase::FAULT);
    CHECK(rig.runtime.report().fault == app::RuntimeFault::CLOCK);
    CHECK_FALSE(rig.runtime.report().fresh);
    CHECK(readiness_review::readyGlyph(rig.source.submitted) == (MOTORS_ALLOWED != 0));
    for (unsigned i = 0U; i < 3U; ++i) CHECK_FALSE(rig.next());
    CHECK(rig.source.submissions == before + 1U);
    CHECK_FALSE(rig.source.enabled);
    for (const auto pulse : rig.source.pulses) CHECK(pulse == 0U);
}
#endif

// Checks whether distinct old frames can be mistaken for post-handover evidence.
// A whole decision-clock wrap must not erase the source's known earlier era.
// Reviewer-owned synthetic reproducer; no native sensor or motor operation.
#include "fixtures/qtr_cal_fixture.h"
#include <cstdio>

int main() {
    qtr_cal_test::Pipeline p;
    p.snapshot = qtr_cal_test::frame(p.now - 4000U, ++p.sequence);
    p.apply();
    const auto unseen_old = qtr_cal_test::frame(p.now - 2000U, ++p.sequence);
    p.raw = false;
    for (unsigned i = 0; i < 4; ++i) p.tick(core::ButtonLevel::NONE, 1000000000U);
    p.tick(core::ButtonLevel::NONE, 294967296U);
    p.now += 1000U;
    p.snapshot = unseen_old;
    p.apply();
    std::printf("Robot old distinct pre-handover frame: faults=%u available=%u hold=%u updated=%u age=%u\n",
        p.result.contract_faults, p.result.line_available, p.result.line_calibration_hold,
        p.result.line_updated, p.result.line_age_us);

    qtr_cal_test::Protocol owner;
    owner.step(qtr_cal_test::frame(owner.now - 4000U, 1U), true);
    owner.sequence = 1U;
    // Preserve WAITING semantics without a collecting deadline: complete stage0.
    owner.batch(197U, 200U);
    const auto next_old = qtr_cal_test::frame(owner.now - 1700U + 2000U, ++owner.sequence, 800U, 803U);
    // Let this unconsumed acquisition finish before the later stage request.
    owner.now += 3000U;
    owner.step();
    for (unsigned i = 0; i < 4; ++i) { owner.now += 1000000000U; owner.step(); }
    owner.now += 294964296U;
    owner.step({}, true);
    owner.now += 3000U;
    const auto r = owner.step(next_old);
    std::printf("Owner old distinct frame: phase=%u reason=%u samples=%u\n",
        static_cast<unsigned>(r.phase), static_cast<unsigned>(r.reason), r.samples);
    return p.result.line_available ? 1 : 0;
}

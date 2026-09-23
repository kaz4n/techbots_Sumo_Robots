// Tests D094 runtime progress from the public B3/B14 contract, not implementation.
// Links actual Setup/Acquirer/Estimator/Robot to additive independently scripted Bus methods.
// Pending never becomes sensor evidence and source clocks survive every interleave.
#include "doctest.h"
#include "support/imu_resume_fake.h"
#include "hal/imu_acquisition.h"
#include "hal/imu_adapter.h"
#include "robot_scenario.h"
#include "config.h"
#include <initializer_list>
#include <cstdint>
#include <cstdlib>

namespace {
void must(bool value) { CHECK(value); if (!value) std::abort(); }
namespace fake = imu_resume_fake;
using imu::AsyncState; using imu::SampleFault; using imu::SampleState;
void empty(const imu::Sample& s) {
    CHECK(s.state == SampleState::NOT_READY); CHECK(s.fault == SampleFault::NONE);
    CHECK(s.bus_status == imu::BusStatus::NOT_INITIALIZED);
    CHECK(s.cleanup == imu::BusCleanup::NOT_ATTEMPTED); CHECK(s.error_flags == 0U);
    CHECK(s.sequence == 0U); CHECK(s.checked_us == 0U);
    CHECK(s.readiness_completed_us == 0U); CHECK(s.motion_started_us == 0U);
    CHECK(s.observation_gap_us == 0U); CHECK_FALSE(s.had_previous_observation);
    CHECK_FALSE(s.motion.coherent); CHECK(s.motion.status == imu::DecodeStatus::RESPONSE);
    CHECK(s.motion.started_us == 0U); CHECK(s.motion.completed_us == 0U);
    CHECK(s.motion.temperature_raw == 0); CHECK(s.motion.interrupt_status == 0U);
    CHECK(s.motion.rail_mask == 0U);
    for (unsigned i = 0U; i < 3U; ++i) {
        CHECK(s.motion.accel_raw[i] == 0); CHECK(s.motion.gyro_raw[i] == 0);
        CHECK(s.motion.accel_g[i] == 0.0F); CHECK(s.motion.gyro_dps[i] == 0.0F);
    }
}
void fault(const imu::SampleProgress& p, SampleFault why) {
    CHECK(p.state == AsyncState::FAULT); CHECK_FALSE(p.started); CHECK(p.completed);
    CHECK(p.sample.state == SampleState::FAULT); CHECK(p.sample.fault == why);
    CHECK_FALSE(p.sample.motion.coherent); CHECK(p.sample.motion.started_us == 0U);
    CHECK(p.sample.motion.completed_us == 0U); CHECK(p.sample.readiness_completed_us == 0U);
    CHECK(p.sample.motion_started_us == 0U); CHECK(p.sample.observation_gap_us == 0U);
    CHECK_FALSE(p.sample.had_previous_observation);
    for (unsigned i = 0U; i < 3U; ++i) {
        CHECK(p.sample.motion.accel_raw[i] == 0); CHECK(p.sample.motion.gyro_raw[i] == 0);
        CHECK(p.sample.motion.accel_g[i] == 0.0F); CHECK(p.sample.motion.gyro_dps[i] == 0.0F);
    }
}
std::uint32_t ready(imu::Acquirer& a, std::uint32_t start = 123U) {
    fake::reset(); imu_acq_fake::seedSetup();
    must(a.start(start, true).state == imu::SetupState::IN_PROGRESS);
    auto now = start;
    for (unsigned i = 0U; i < 48U; ++i) {
        now = imu_acq_fake::setupTime(i, start, now); imu_fake::script.now_us = now;
        const auto p = a.advanceSetup(now);
        if (i == 47U) must(p.state == imu::SetupState::PROFILE_READY);
        else must(p.state == imu::SetupState::IN_PROGRESS);
    }
    return a.setupReport().observed_us;
}
void begin(imu::Acquirer& a, std::uint32_t now) {
    fake::script.begin = fake::pending(now, now, 0U, true);
    fake::script.cancel = fake::cancelled(now, now);
    const auto p = a.beginRead(now);
    must(p.state == AsyncState::PENDING); CHECK(p.started); CHECK_FALSE(p.completed); empty(p.sample);
}
imu::Sample finish(imu::Acquirer& a, std::uint32_t now, bool observation = true) {
    begin(a, now); fake::script.advance = fake::complete(now, 100U, observation);
    const auto p = a.advanceRead(now + 50U);
    must(p.state == AsyncState::COMPLETE); CHECK(p.completed); CHECK_FALSE(p.started);
    return p.sample;
}
void latched(imu::Acquirer& a, const imu::Sample& original) {
    const auto before = fake::script; const auto old = imu_acq_fake::script.calls;
    for (auto t : {0U, original.checked_us, 0x80000000U, 0xffffffffU}) {
        for (const auto& p : {a.beginRead(t), a.advanceRead(t), a.cancelRead(t), a.readProgress()}) {
            CHECK(p.state == AsyncState::FAULT); CHECK_FALSE(p.started); CHECK_FALSE(p.completed);
            CHECK(p.sample.fault == original.fault); CHECK(p.sample.checked_us == original.checked_us);
            CHECK(p.sample.sequence == original.sequence); CHECK(p.sample.bus_status == original.bus_status);
            CHECK(p.sample.cleanup == original.cleanup); CHECK(p.sample.error_flags == original.error_flags);
        }
        CHECK(a.read(t).fault == original.fault);
    }
    CHECK(fake::script.begins == before.begins); CHECK(fake::script.advances == before.advances);
    CHECK(fake::script.cancels == before.cancels); CHECK(imu_acq_fake::script.calls == old);
}
} // namespace

TEST_CASE("B3 D094 pre-profile progress constructors and idle calls are inert") {
    fake::reset(); { imu::Acquirer temporary; }
    imu::Acquirer a;
    for (auto now : {0U, 0xffffffffU, 0x80000000U}) {
        for (const auto& p : {a.beginRead(now), a.advanceRead(now), a.cancelRead(now), a.readProgress()}) {
            CHECK(p.state == AsyncState::IDLE); CHECK_FALSE(p.started); CHECK_FALSE(p.completed); empty(p.sample);
        }
    }
    CHECK(fake::script.begins == 0U); CHECK(fake::script.advances == 0U);
    CHECK(fake::script.cancels == 0U); CHECK(imu_fake::script.count == 0U);
}

TEST_CASE("B3 D094 duplicate begin reports and setup calls preserve pending lifetime") {
    imu::Acquirer a; const auto now = ready(a); begin(a, now);
    for (auto bad_time : {0U, now + 20000U, now + 0x80000000U}) {
        const auto p = a.beginRead(bad_time); CHECK(p.state == AsyncState::PENDING);
        CHECK_FALSE(p.started); CHECK_FALSE(p.completed); empty(p.sample);
        empty(a.readProgress().sample); CHECK_FALSE(a.readProgress().started);
        a.start(bad_time, false); a.advanceSetup(bad_time);
    }
    CHECK(fake::script.begins == 1U); CHECK(fake::script.advances == 0U);
    CHECK(fake::script.cancels == 0U); CHECK(imu_fake::script.count == 48U);
    fake::script.advance = fake::complete(now, 100U); const auto done = a.advanceRead(now + 50U);
    CHECK(done.state == AsyncState::COMPLETE); CHECK(done.sample.sequence == 1U);
}

TEST_CASE("B3 D094 pending is canonical after accepted observations and never updates sequence") {
    imu::Acquirer a; const auto now = ready(a); CHECK(finish(a, now).sequence == 1U);
    begin(a, now + 1000U);
    for (unsigned i = 1U; i <= 30U; ++i) {
        fake::script.advance = fake::pending(now + 1000U, now + 1000U + i, i);
        const auto p = a.advanceRead(now + 1000U + i);
        CHECK(p.state == AsyncState::PENDING); CHECK_FALSE(p.started); CHECK_FALSE(p.completed); empty(p.sample);
    }
    fake::script.advance = fake::complete(now + 1000U, 100U, true, 31U);
    const auto p = a.advanceRead(now + 1050U);
    CHECK(p.sample.sequence == 2U); CHECK(p.sample.observation_gap_us == 1000U);
    CHECK(p.sample.had_previous_observation); CHECK(p.sample.checked_us == now + 1100U);
}

TEST_CASE("B3 D094 terminal pulses occur once and success permits another operation") {
    imu::Acquirer a; const auto now = ready(a); const auto sample = finish(a, now);
    const auto calls = fake::script.advances;
    for (auto time : {0U, now + 20000U})
        for (const auto& p : {a.advanceRead(time), a.cancelRead(time), a.readProgress()}) {
            CHECK(p.state == AsyncState::COMPLETE); CHECK_FALSE(p.started); CHECK_FALSE(p.completed);
            CHECK(p.sample.sequence == 1U); CHECK(p.sample.checked_us == sample.checked_us);
        }
    CHECK(fake::script.advances == calls); CHECK(fake::script.cancels == 0U);
    CHECK(finish(a, now + 1000U).sequence == 2U);
}

TEST_CASE("B3 B14 D094 real NO_NEW preserves sequence and observed silence anchor") {
    for (bool previous : {false, true}) {
        imu::Acquirer a; auto anchor = ready(a);
        if (previous) anchor = finish(a, anchor).checked_us;
        const auto sample = finish(a, anchor + 19000U, false);
        CHECK(sample.state == SampleState::NO_NEW); CHECK_FALSE(sample.motion.coherent);
        CHECK(sample.sequence == (previous ? 1U : 0U));
        const auto begins = fake::script.begins;
        const auto expired = a.beginRead(anchor + 20000U); fault(expired, SampleFault::SILENCE);
        CHECK(expired.sample.checked_us == anchor + 20000U); CHECK(fake::script.begins == begins);
        latched(a, expired.sample);
    }
}

TEST_CASE("B14 D094 active observed silence beats overdue native budget and cancels once") {
    for (auto offset : {19999U, 20000U, 20001U}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now + 19500U);
        fake::script.advance = fake::pending(now + 19500U, now + offset, 1U);
        fake::script.cancel = fake::cancelled(now + 19500U, now + offset);
        const auto p = a.advanceRead(now + offset);
        if (offset == 19999U) { CHECK(p.state == AsyncState::PENDING); CHECK(fake::script.cancels == 0U); }
        else { fault(p, SampleFault::SILENCE); CHECK(p.sample.checked_us == now + offset);
            CHECK(p.sample.bus_status == imu::BusStatus::CANCELLED); CHECK(fake::script.advances == 0U);
            CHECK(fake::script.cancels == 1U); latched(a, p.sample); }
    }
}

TEST_CASE("B14 D094 source completion and delayed native begin obey exact silence boundary") {
    for (bool beginning : {false, true}) for (auto offset : {19999U, 20000U, 20001U}) {
        imu::Acquirer a; const auto now = ready(a); imu::SampleProgress p;
        if (beginning) {
            fake::script.begin = fake::pending(now + offset, now + offset, 0U, true);
            fake::script.cancel = fake::cancelled(now + offset, now + offset);
            p = a.beginRead(now + 19500U);
        } else {
            begin(a, now + 19500U);
            fake::script.advance = fake::complete(now + 19500U, offset - 19500U);
            fake::script.cancel = fake::cancelled(now + 19500U, now + offset, false);
            p = a.advanceRead(now + 19501U);
        }
        if (offset < 20000U) CHECK(p.state != AsyncState::FAULT);
        else { fault(p, SampleFault::SILENCE); CHECK(p.sample.checked_us == now + offset);
            CHECK(fake::script.cancels == 1U); }
    }
}

TEST_CASE("B3 D094 caller chronology rejects backward and half range while wrapping normally") {
    for (auto backwards : {1U, 0x80000000U}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        const auto p = a.advanceRead(now - backwards); fault(p, SampleFault::TIME_ORDER);
        CHECK(p.sample.checked_us == now); CHECK(fake::script.advances == 0U);
        CHECK(fake::script.cancels == 1U); latched(a, p.sample);
    }
    imu::Acquirer a; const auto now = ready(a, 0xfffffff0U - 310000U);
    CHECK(now == 0xfffffff0U);
    const auto s = finish(a, now); CHECK(s.state == SampleState::OBSERVATION);
    CHECK(s.checked_us == now + 100U);
}

TEST_CASE("B3 D094 healthy cancellation is terminal transport with actual diagnostics") {
    imu::Acquirer a; const auto now = ready(a); begin(a, now);
    fake::script.cancel = fake::cancelled(now, now + 10U);
    const auto p = a.cancelRead(now + 5U); fault(p, SampleFault::TRANSPORT);
    CHECK(p.sample.bus_status == imu::BusStatus::CANCELLED);
    CHECK(p.sample.cleanup == imu::BusCleanup::DISABLED); CHECK(p.sample.error_flags == 0x100U);
    CHECK(fake::script.cancels == 1U); latched(a, p.sample);
}

TEST_CASE("B14 D094 cancellation still validates time and silence without advancing backend") {
    for (bool late : {false, true}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        const auto p = a.cancelRead(late ? now + 20000U : now - 1U);
        fault(p, late ? SampleFault::SILENCE : SampleFault::TIME_ORDER);
        CHECK(fake::script.cancels == 1U); CHECK(fake::script.advances == 0U);
    }
}

TEST_CASE("B3 D094 active legacy read cancels immediately without accepting caller timestamp") {
    for (auto offset : {1U, 20000U, 0x80000000U}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        imu_acq_fake::script.reply = fake::cancelled(now, now + 4U).acquisition;
        const auto s = a.read(now + offset);
        CHECK(s.state == SampleState::FAULT); CHECK(s.fault == SampleFault::TRANSPORT);
        CHECK(s.bus_status == imu::BusStatus::CANCELLED); CHECK(s.checked_us == now);
        CHECK(imu_acq_fake::script.calls == 1U); CHECK(fake::script.cancels == 0U);
        latched(a, s);
    }
}

TEST_CASE("B3 D094 malformed initial progress fails before any sample is accepted") {
    for (unsigned mutation = 0U; mutation < 13U; ++mutation) {
        imu::Acquirer a; const auto now = ready(a);
        auto& p = fake::script.begin; p = fake::pending(now, now, 0U, true);
        fake::script.cancel = fake::cancelled(now, now);
        switch (mutation) {
        case 0: p.state = AsyncState::IDLE; break;
        case 1: p.state = static_cast<AsyncState>(99U); break;
        case 2: p.started = false; break;
        case 3: p.completed = true; break;
        case 4: p.polls = 1U; break;
        case 5: p.observed_us += 1U; break;
        case 6: p.started_us -= 1U; p.observed_us = p.started_us; break;
        case 7: p.acquisition.transfer.status = imu::BusStatus::OK; break;
        case 8: p.acquisition.transfer.bytes[14] = 1U; break;
        case 9: p.acquisition.readiness_completed_us = 1U; break;
        case 10: p.acquisition.motion_status = 1U; break;
        case 11: p.acquisition.transfer.cleanup = imu::BusCleanup::DISABLED; break;
        default: p.acquisition.state = imu::AcquisitionState::NO_NEW; break;
        }
        CAPTURE(mutation); const auto r = a.beginRead(now);
        fault(r, mutation == 6U ? SampleFault::TIME_ORDER : SampleFault::RESPONSE);
        CHECK(r.sample.sequence == 0U); CHECK(fake::script.cancels == 1U);
    }
}

TEST_CASE("B3 D094 all pending payload fields and progress identities remain strict") {
    for (unsigned mutation = 0U; mutation < 25U; ++mutation) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        auto& p = fake::script.advance; p = fake::pending(now, now + 20U, 1U);
        switch (mutation) {
        case 0: p.started = true; break; case 1: p.completed = true; break;
        case 2: p.started_us += 1U; break; case 3: p.polls = 0U; break;
        case 4: p.polls = config::IMU_I2C_MAX_POLLS + 1U; break;
        case 5: p.observed_us = now + 9U; break;
        case 6: p.observed_us = now + 600U; break;
        case 7: p.acquisition.state = imu::AcquisitionState::NO_NEW; break;
        case 8: p.acquisition.transfer.status = imu::BusStatus::OK; break;
        case 9: p.acquisition.transfer.cleanup = imu::BusCleanup::DISABLED; break;
        case 10: p.acquisition.transfer.bytes[0] = 1U; break;
        case 11: p.acquisition.transfer.bytes[14] = 1U; break;
        case 12: p.acquisition.transfer.count = 1U; break;
        case 13: p.acquisition.transfer.started_us = 1U; break;
        case 14: p.acquisition.transfer.completed_us = 1U; break;
        case 15: p.acquisition.transfer.error_flags = 1U; break;
        case 16: p.acquisition.transfer.complete = true; break;
        case 17: p.acquisition.readiness_status = 1U; break;
        case 18: p.acquisition.readiness_observed = true; break;
        case 19: p.acquisition.readiness_completed_us = 1U; break;
        case 20: p.acquisition.motion_attempted = true; break;
        case 21: p.acquisition.motion_started_us = 1U; break;
        case 22: p.acquisition.motion_status_observed = true; break;
        case 23: p.acquisition.motion_status = 1U; break;
        default: p.state = static_cast<AsyncState>(99U); break;
        }
        CAPTURE(mutation); const auto r = a.advanceRead(now + 10U);
        fault(r, mutation == 5U ? SampleFault::TIME_ORDER : SampleFault::RESPONSE);
        CHECK(fake::script.cancels == 1U); latched(a, r.sample);
    }
}

TEST_CASE("B3 D094 pending poll counts must strictly advance across resumptions") {
    for (auto polls : {0U, 2U, 3U}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        fake::script.advance = fake::pending(now, now + 20U, 3U);
        must(a.advanceRead(now + 10U).state == AsyncState::PENDING);
        fake::script.advance = fake::pending(now, now + 30U, polls);
        fault(a.advanceRead(now + 25U), SampleFault::RESPONSE);
        CHECK(fake::script.cancels == 1U);
    }
}

TEST_CASE("B3 D094 terminal transport status takes precedence without duplicate cleanup") {
    imu::Acquirer a; const auto now = ready(a); begin(a, now);
    auto& p = fake::script.advance; p = fake::cancelled(now, now);
    p.state = AsyncState::FAULT; p.started = true; p.completed = false;
    p.started_us = 0U; p.polls = 0U;
    p.acquisition.transfer.status = imu::BusStatus::NACK;
    const auto r = a.advanceRead(now + 10U); fault(r, SampleFault::TRANSPORT);
    CHECK(r.sample.bus_status == imu::BusStatus::NACK); CHECK(r.sample.error_flags == 0x100U);
    CHECK(fake::script.cancels == 0U); latched(a, r.sample);
}

TEST_CASE("B3 D094 unknown or idle progress cannot certify terminal transport failure") {
    for (const auto state : {AsyncState::IDLE, static_cast<AsyncState>(77U)}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        fake::script.advance = fake::cancelled(now, now);
        fake::script.advance.state = state;
        fake::script.advance.acquisition.transfer.status = imu::BusStatus::NACK;
        const auto r = a.advanceRead(now + 10U); fault(r, SampleFault::RESPONSE);
        CHECK(fake::script.cancels == 1U); latched(a, r.sample);
    }
}

TEST_CASE("B3 D094 terminal envelope and phase validation reject malformed successful replies") {
    for (unsigned mutation = 0U; mutation < 17U; ++mutation) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        auto& p = fake::script.advance; p = fake::complete(now, 100U);
        fake::script.cancel = fake::cancelled(now, now + 100U, false);
        switch (mutation) {
        case 0: p.state = AsyncState::FAULT; break; case 1: p.completed = false; break;
        case 2: p.started = true; break; case 3: p.started_us += 1U; break;
        case 4: p.polls = 0U; break; case 5: p.polls = config::IMU_I2C_MAX_POLLS + 1U; break;
        case 6: p.observed_us += 1U; break;
        case 7: p.acquisition.transfer.started_us += 1U; break;
        case 8: p.acquisition.readiness_observed = false; break;
        case 9: p.acquisition.readiness_status = 0U; break;
        case 10: p.acquisition.motion_started_us = now - 1U; break;
        case 11: p.acquisition.motion_status_observed = false; break;
        case 12: p.acquisition.motion_status = 1U; break;
        case 13: p.acquisition.transfer.count = 14U; break;
        case 14: p.acquisition.transfer.complete = false; break;
        case 15: p.acquisition.transfer.bytes[0] = 0x80U; p.acquisition.motion_status = 0x80U; break;
        default: p.acquisition.transfer.error_flags = 1U; break;
        }
        CAPTURE(mutation); const auto r = a.advanceRead(now + 50U); fault(r, SampleFault::RESPONSE);
        CHECK(fake::script.cancels == 1U); CHECK(r.sample.bus_status == imu::BusStatus::OK);
        CHECK(r.sample.cleanup == imu::BusCleanup::NOT_ATTEMPTED);
    }
}

TEST_CASE("B3 D094 original begin anchor permits late resume but final source cannot precede resume") {
    for (auto completion : {99U, 100U, 599U, 600U}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        fake::script.advance = fake::complete(now, completion);
        fake::script.cancel = fake::cancelled(now, now + completion, false);
        const auto p = a.advanceRead(now + 100U);
        if (completion == 99U) fault(p, SampleFault::TIME_ORDER);
        else if (completion == 600U) fault(p, SampleFault::RESPONSE);
        else { CHECK(p.state == AsyncState::COMPLETE); CHECK(p.sample.motion.started_us == now);
            CHECK(p.sample.checked_us == now + completion); }
    }
}

TEST_CASE("B3 D094 aborted malformed reply uses new cancellation diagnostics only") {
    for (bool newly : {false, true}) {
        imu::Acquirer a; const auto now = ready(a); begin(a, now);
        fake::script.advance = fake::complete(now, 100U); fake::script.advance.started = true;
        fake::script.cancel = fake::cancelled(now, now + 100U, newly);
        const auto p = a.advanceRead(now); fault(p, SampleFault::RESPONSE);
        CHECK(p.sample.bus_status == (newly ? imu::BusStatus::CANCELLED : imu::BusStatus::OK));
        CHECK(p.sample.error_flags == (newly ? 0x100U : 0U));
    }
}

TEST_CASE("B3 D094 synchronous and resumable successful observations share one sequence") {
    imu::Acquirer a; const auto now = ready(a);
    imu_acq_fake::script.reply = imu_acq_fake::observation(now, 100U);
    CHECK(a.read(now).sequence == 1U);
    const auto async = finish(a, now + 1000U); CHECK(async.sequence == 2U);
    CHECK(async.observation_gap_us == 1000U);
    imu_acq_fake::script.reply = imu_acq_fake::observation(now + 2000U, 100U);
    const auto legacy = a.read(now + 2000U); CHECK(legacy.sequence == 3U);
    CHECK(legacy.observation_gap_us == 1000U);
}

TEST_CASE("B3 B14 D094 actual Estimator consumes complete sources once across pending work") {
    for (auto gap : {2000U, 2001U}) {
        imu::Acquirer a; const auto now = ready(a); imu::Estimator e;
        must(e.begin({{1,2,3}, true}, 0.0F));
        auto first = finish(a, now); const auto first_estimate = e.observe(first);
        must(first_estimate.heading_available); CHECK(first_estimate.sequence == 1U);
        begin(a, now + gap);
        for (unsigned i = 1U; i < 6U; ++i) {
            fake::script.advance = fake::pending(now + gap, now + gap + i, i);
            const auto p = a.advanceRead(now + gap + i); empty(p.sample);
            CHECK(e.report().sequence == 1U); CHECK(e.report().observation_us == first.checked_us);
            CHECK(e.report().heading_deg == 0.0F);
        }
        fake::script.advance = fake::complete(now + gap, 100U);
        const auto terminal = a.advanceRead(now + gap + 50U);
        must(terminal.completed); const auto next = e.observe(terminal.sample);
        if (gap == 2000U) { CHECK(next.state == imu::HeadingState::READY); CHECK(next.sequence == 2U); }
        else { CHECK(next.state == imu::HeadingState::FAULT); CHECK(next.fault == imu::HeadingFault::GAP); }
    }
}

TEST_CASE("B3 B14 D094 actual Robot retains source age instead of promoting pending data") {
    imu::Acquirer a; const auto now = ready(a); imu::Estimator e;
    must(e.begin({{1,2,3}, true}, 0.0F)); const auto estimate = e.observe(finish(a, now));
    robot_test::Rig rig; must(imu::applyEstimate(rig.input, estimate));
    CHECK(rig.step(estimate.observation_us).contract_faults == 0U);
    begin(a, now + 200U); empty(a.readProgress().sample);
    // Present only a previously admitted provider identity. Robot suppresses replay.
    must(imu::applyEstimate(rig.input, e.report()));
    CHECK(rig.step(estimate.observation_us + 2000U).contract_faults == 0U);
    CHECK(rig.input.imu.observation_us == estimate.observation_us);
    const auto stale = rig.step(estimate.observation_us + 2001U);
    CHECK((stale.contract_faults & fsm::HEADING_CONTRACT) != 0U);
    CHECK(e.report().sequence == 1U); CHECK(e.report().checked_us == estimate.checked_us);
}

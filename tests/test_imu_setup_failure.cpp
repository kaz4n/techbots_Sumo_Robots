// Tests D097 passive setup-fault evidence from the frozen B3/B14 public contract.
// Actual Setup and Acquirer link to established independently scripted Bus fakes.
// No production CPP was read to author these expectations or the callback test.
#include "native_imu_setup_failure/check_sample.h"
#include "support/imu_resume_fake.h"
#include "config.h"
#include <initializer_list>
#include <type_traits>

namespace {
using setup_failure_test::sameSample;
namespace fake = imu_resume_fake;
using Accessor = imu::Sample (imu::Acquirer::*)() const;
static_assert(std::is_same<decltype(&imu::Acquirer::setupFailure), Accessor>::value);

// Plain CHECK is supported by the repository's no-exceptions doctest mode.
// Callers return explicitly after failed prerequisites instead of using REQUIRE.
bool checked(bool condition) { CHECK(condition); return condition; }

void sameSetup(const imu::SetupReport& a, const imu::SetupReport& b) {
    CHECK(a.state == b.state); CHECK(a.fault == b.fault);
    CHECK(a.bus_status == b.bus_status); CHECK(a.cleanup == b.cleanup);
    CHECK(a.error_flags == b.error_flags); CHECK(a.started_us == b.started_us);
    CHECK(a.observed_us == b.observed_us); CHECK(a.advances == b.advances);
    CHECK(a.requests == b.requests);
}
void sameProgress(const imu::SampleProgress& a, const imu::SampleProgress& b) {
    CHECK(a.state == b.state); CHECK(a.started == b.started);
    CHECK(a.completed == b.completed); sameSample(a.sample, b.sample);
}
void passive(const imu::Acquirer& a, const imu::Sample& expected) {
    const auto setup = a.setupReport(); const auto progress = a.readProgress();
    const auto count = imu_fake::script.count; const auto legacy = imu_acq_fake::script.calls;
    const auto async = fake::script;
    for (unsigned i = 0U; i < 3U; ++i) sameSample(a.setupFailure(), expected);
    sameSetup(a.setupReport(), setup); sameProgress(a.readProgress(), progress);
    CHECK(imu_fake::script.count == count); CHECK(imu_acq_fake::script.calls == legacy);
    CHECK(fake::script.begins == async.begins); CHECK(fake::script.advances == async.advances);
    CHECK(fake::script.cancels == async.cancels); CHECK(fake::script.reports == async.reports);
}
imu::Sample setupFault(const imu::SetupReport& report) {
    imu::Sample expected;
    expected.state = imu::SampleState::FAULT; expected.fault = imu::SampleFault::SETUP;
    expected.checked_us = report.observed_us; expected.bus_status = report.bus_status;
    expected.cleanup = report.cleanup; expected.error_flags = report.error_flags;
    return expected;
}
std::uint32_t ready(imu::Acquirer& a) {
    fake::reset(); imu_acq_fake::seedSetup(); const std::uint32_t start = 123U;
    if (!checked(a.start(start, true).state == imu::SetupState::IN_PROGRESS)) return 0U;
    auto now = start;
    for (unsigned i = 0U; i < 48U; ++i) {
        now = imu_acq_fake::setupTime(i, start, now); imu_fake::script.now_us = now;
        const auto report = a.advanceSetup(now);
        if (!checked(report.state == (i == 47U ? imu::SetupState::PROFILE_READY :
                                                imu::SetupState::IN_PROGRESS))) return 0U;
        passive(a, {});
    }
    CHECK(imu_fake::script.count == 48U); return a.setupReport().observed_us;
}
bool begin(imu::Acquirer& a, std::uint32_t now) {
    fake::script.begin = fake::pending(now, now, 0U, true);
    fake::script.cancel = fake::cancelled(now, now + 10U);
    const auto progress = a.beginRead(now);
    if (!checked(progress.state == imu::AsyncState::PENDING)) return false;
    CHECK(progress.started); CHECK_FALSE(progress.completed);
    return true;
}
} // namespace

TEST_CASE("B3 D097 const retrieval is canonical before setup through all 48 setup operations") {
    fake::reset(); imu::Acquirer a; passive(a, {});
    CHECK(a.read(0xffffffffU).state == imu::SampleState::NOT_READY);
    passive(a, {}); if (!checked(ready(a) != 0U)) return; passive(a, {});
    CHECK(imu_acq_fake::script.calls == 0U);
    CHECK(fake::script.begins == 0U); CHECK(fake::script.cancels == 0U);
}

TEST_CASE("B3 D097 start failure keeps every latched field and returned copies cannot mutate it") {
    for (auto start : {17U, 0xfffffff0U}) {
        fake::reset(); imu::Acquirer a; const auto report = a.start(start, false);
        if (!checked(report.state == imu::SetupState::FAULT)) return;
        CHECK(report.fault == imu::SetupFault::POWER_UNCONFIRMED);
        CHECK(report.observed_us == start); CHECK(imu_fake::script.count == 0U);
        const auto expected = setupFault(report); passive(a, expected);
        auto copy = a.setupFailure(); copy.state = imu::SampleState::OBSERVATION;
        copy.checked_us = 0U; copy.motion.accel_g[0] = 22.0F; copy.sequence = 99U;
        passive(a, expected); CHECK(copy.sequence == 99U);
        for (auto time : {0U, start, 0x80000000U, 0xffffffffU}) {
            sameSample(a.read(time), expected);
            sameSetup(a.start(time, true), report); sameSetup(a.advanceSetup(time), report);
            passive(a, expected);
        }
    }
}

TEST_CASE("B3 D097 advanceSetup transport failures retain diagnostic statuses and timestamps") {
    for (bool init : {false, true}) {
        fake::reset(); imu_acq_fake::seedSetup(); imu::Acquirer a;
        if (!checked(a.start(79U, true).state == imu::SetupState::IN_PROGRESS)) return;
        if (init) imu_fake::script.replies[0].init =
            {imu::BusStatus::OWNERSHIP, imu::BusCleanup::UNCONFIRMED, false};
        auto now = 79U + config::IMU_POWER_WAIT_US; imu_fake::script.now_us = now;
        auto report = a.advanceSetup(now);
        if (!init) {
            if (!checked(report.state == imu::SetupState::IN_PROGRESS)) return;
            auto& reply = imu_fake::script.replies[1];
            reply.start_offset_us = 7U; reply.duration_us = 31U;
            reply.transfer.status = imu::BusStatus::NACK;
            reply.transfer.cleanup = imu::BusCleanup::DISABLED;
            reply.transfer.error_flags = 0xa5a50011U;
            now += 23U; imu_fake::script.now_us = now; report = a.advanceSetup(now);
        }
        if (!checked(report.state == imu::SetupState::FAULT)) return;
        CHECK(report.fault == imu::SetupFault::TRANSPORT);
        CHECK(report.bus_status == (init ? imu::BusStatus::OWNERSHIP : imu::BusStatus::NACK));
        CHECK(report.cleanup == (init ? imu::BusCleanup::UNCONFIRMED : imu::BusCleanup::DISABLED));
        CHECK(report.error_flags == (init ? 0U : 0xa5a50011U));
        const auto expected = setupFault(report); passive(a, expected);
        sameSample(a.read(0U), expected); passive(a, expected);
        CHECK(imu_fake::script.count == (init ? 1U : 2U));
    }
}

TEST_CASE("B3 D097 setup time-order failure is evidence without a replacement time or bus request") {
    fake::reset(); imu::Acquirer a;
    if (!checked(a.start(1000U, true).state == imu::SetupState::IN_PROGRESS)) return;
    passive(a, {}); const auto report = a.advanceSetup(999U);
    if (!checked(report.state == imu::SetupState::FAULT)) return;
    CHECK(report.fault == imu::SetupFault::TIME_ORDER); CHECK(report.observed_us == 1000U);
    passive(a, setupFault(report)); sameSample(a.read(0xffffffffU), setupFault(report));
    CHECK(imu_fake::script.count == 0U); CHECK(imu_acq_fake::script.calls == 0U);
}

TEST_CASE("B3 B14 D097 successful runtime and NO_NEW never masquerade as setup failure") {
    imu::Acquirer a; const auto now = ready(a); if (!checked(now != 0U)) return;
    imu_acq_fake::script.reply = imu_acq_fake::observation(now);
    const auto first = a.read(now); if (!checked(first.state == imu::SampleState::OBSERVATION)) return;
    CHECK(first.sequence == 1U); CHECK(first.motion.coherent); passive(a, {});
    imu_acq_fake::script.reply = imu_acq_fake::noNew(now + 1000U);
    CHECK(a.read(now + 1000U).state == imu::SampleState::NO_NEW); passive(a, {});
    if (!checked(begin(a, now + 2000U))) return;
    passive(a, {});
    fake::script.advance = fake::complete(now + 2000U, 100U);
    const auto completed = a.advanceRead(now + 2050U);
    if (!checked(completed.completed)) return;
    CHECK(completed.sample.sequence == 2U);
    CHECK(completed.sample.observation_gap_us == 2000U);
    CHECK(completed.sample.had_previous_observation); passive(a, {});
    const auto retained = a.readProgress(); CHECK_FALSE(retained.completed);
    sameSample(retained.sample, completed.sample); CHECK(fake::script.cancels == 0U);
}

TEST_CASE("B3 B14 D097 runtime-only failure stays distinct and legacy fault reads remain latched") {
    imu::Acquirer a; const auto now = ready(a); if (!checked(now != 0U)) return;
    imu_acq_fake::script.reply = imu_acq_fake::observation(now);
    const auto observation = a.read(now); passive(a, {});
    const auto fault = a.read(observation.checked_us - 1U);
    if (!checked(fault.state == imu::SampleState::FAULT)) return;
    CHECK(fault.fault == imu::SampleFault::TIME_ORDER); CHECK(fault.sequence == 1U);
    CHECK(a.setupReport().state == imu::SetupState::PROFILE_READY); passive(a, {});
    sameSample(a.read(0xffffffffU), fault); passive(a, {});
    CHECK(imu_acq_fake::script.calls == 1U);
}

TEST_CASE("B3 D097 passive retrieval leaves mixed-API pending cancellation to legacy read") {
    imu::Acquirer a; const auto now = ready(a); if (!checked(now != 0U)) return;
    if (!checked(begin(a, now))) return;
    passive(a, {});
    CHECK(fake::script.cancels == 0U); CHECK(a.readProgress().state == imu::AsyncState::PENDING);
    // The established Bus seam returns collision cleanup from acquireMotion itself.
    imu_acq_fake::script.reply = fake::cancelled(now, now + 10U).acquisition;
    const auto fault = a.read(now + 10U);
    if (!checked(fault.state == imu::SampleState::FAULT)) return;
    CHECK(fault.fault == imu::SampleFault::TRANSPORT);
    CHECK(fault.bus_status == imu::BusStatus::CANCELLED);
    CHECK(fault.cleanup == imu::BusCleanup::DISABLED); CHECK(fault.error_flags == 0x100U);
    CHECK(fake::script.cancels == 0U); CHECK(imu_acq_fake::script.calls == 1U);
    passive(a, {}); sameSample(a.read(now + 11U), fault);
    CHECK(fake::script.cancels == 0U); CHECK(imu_acq_fake::script.calls == 1U);
    CHECK_FALSE(a.readProgress().completed);
}

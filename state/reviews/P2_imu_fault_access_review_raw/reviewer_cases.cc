// Independently stress the D097 passive setup-failure getter at lifecycle boundaries.
// Uses actual Setup/Acquirer and established scripted Bus transports without private access.
// Compiled under ASan/UBSan in an isolated reviewer executable; never firmware.
#include "doctest.h"
#include "hal/imu_acquisition.h"
#include "support/imu_resume_fake.h"
#include "config.h"
#include <array>
#include <cstring>
#include <type_traits>
#include <utility>

namespace {
static_assert(std::is_same<decltype(std::declval<const imu::Acquirer&>().setupFailure()),
                           imu::Sample>::value, "public getter is const and returns a value");
void same(const imu::Sample& a, const imu::Sample& b) {
    CHECK(a.state == b.state); CHECK(a.fault == b.fault);
    CHECK(a.bus_status == b.bus_status); CHECK(a.cleanup == b.cleanup);
    CHECK(a.error_flags == b.error_flags); CHECK(a.sequence == b.sequence);
    CHECK(a.checked_us == b.checked_us);
    CHECK(a.readiness_completed_us == b.readiness_completed_us);
    CHECK(a.motion_started_us == b.motion_started_us);
    CHECK(a.observation_gap_us == b.observation_gap_us);
    CHECK(a.had_previous_observation == b.had_previous_observation);
    CHECK(a.motion.status == b.motion.status);
    CHECK(a.motion.temperature_raw == b.motion.temperature_raw);
    CHECK(a.motion.started_us == b.motion.started_us);
    CHECK(a.motion.completed_us == b.motion.completed_us);
    CHECK(a.motion.interrupt_status == b.motion.interrupt_status);
    CHECK(a.motion.rail_mask == b.motion.rail_mask);
    CHECK(a.motion.coherent == b.motion.coherent);
    for (unsigned i = 0U; i < 3U; ++i) {
        CHECK(a.motion.accel_raw[i] == b.motion.accel_raw[i]);
        CHECK(a.motion.gyro_raw[i] == b.motion.gyro_raw[i]);
        CHECK(a.motion.accel_g[i] == b.motion.accel_g[i]);
        CHECK(a.motion.gyro_dps[i] == b.motion.gyro_dps[i]);
    }
}
void passive(const imu::Acquirer& a, const imu::Sample& expected = {}) {
    std::array<unsigned char, sizeof(a)> bytes{};
    std::memcpy(bytes.data(), &a, sizeof(a));
    const auto setup_count = imu_fake::script.count;
    const auto legacy_count = imu_acq_fake::script.calls;
    const auto before = imu_resume_fake::script;
    for (unsigned i = 0U; i < 8U; ++i) {
        same(a.setupFailure(), expected);
        auto local = a.setupFailure();
        local.sequence = 0xFFFFFFFFU; local.checked_us = 0x80000000U;
        local.motion.gyro_dps[2] = 999.0F;
        CHECK(local.sequence == 0xFFFFFFFFU);
        same(a.setupFailure(), expected);
    }
    CHECK(std::memcmp(bytes.data(), &a, sizeof(a)) == 0);
    CHECK(imu_fake::script.count == setup_count);
    CHECK(imu_acq_fake::script.calls == legacy_count);
    CHECK(imu_resume_fake::script.begins == before.begins);
    CHECK(imu_resume_fake::script.advances == before.advances);
    CHECK(imu_resume_fake::script.cancels == before.cancels);
    CHECK(imu_resume_fake::script.reports == before.reports);
}
std::uint32_t ready(imu::Acquirer& a, std::uint32_t start) {
    imu_resume_fake::reset(); imu_acq_fake::seedSetup();
    REQUIRE(a.start(start, true).state == imu::SetupState::IN_PROGRESS);
    auto now = start;
    for (unsigned i = 0U; i < 48U; ++i) {
        passive(a);
        now = imu_acq_fake::setupTime(i, start, now);
        imu_fake::script.now_us = now;
        const auto r = a.advanceSetup(now);
        REQUIRE(r.state == (i == 47U ? imu::SetupState::PROFILE_READY : imu::SetupState::IN_PROGRESS));
    }
    passive(a);
    return a.setupReport().observed_us;
}
}

TEST_CASE("B3 D097 reviewer all setup request faults retain exact diagnostics and passive storage") {
    for (unsigned failed = 0U; failed < 48U; ++failed) {
        imu_resume_fake::reset(); imu_acq_fake::seedSetup(); imu::Acquirer a;
        passive(a);
        const std::uint32_t start = 0xFFFF0000U;
        auto r = a.start(start, true); auto now = start;
        if (failed == 0U) imu_fake::script.replies[0].init =
            {imu::BusStatus::OWNERSHIP, imu::BusCleanup::DISABLED, false};
        else {
            auto& t = imu_fake::script.replies[failed].transfer;
            t.status = imu::BusStatus::NACK; t.cleanup = imu::BusCleanup::DISABLED;
            t.error_flags = 0xA55A0000U | failed;
        }
        for (unsigned i = 0U; i <= failed; ++i) {
            passive(a);
            now = imu_acq_fake::setupTime(i, start, now); imu_fake::script.now_us = now;
            r = a.advanceSetup(now);
        }
        REQUIRE(r.state == imu::SetupState::FAULT);
        imu::Sample expected{}; expected.state = imu::SampleState::FAULT;
        expected.fault = imu::SampleFault::SETUP; expected.bus_status = r.bus_status;
        expected.cleanup = r.cleanup; expected.error_flags = r.error_flags;
        expected.checked_us = r.observed_us;
        passive(a, expected);
        same(a.read(0U), expected); same(a.read(0x80000000U), expected);
        a.start(0U, true); a.advanceSetup(0U);
        same(a.beginRead(0U).sample, expected);
        passive(a, expected);
    }
}

TEST_CASE("B3 D097 reviewer start failure survives mixed APIs without time admission") {
    imu_resume_fake::reset(); imu::Acquirer a;
    const auto r = a.start(0xFFFFFFFFU, false);
    REQUIRE(r.state == imu::SetupState::FAULT);
    imu::Sample expected{}; expected.state = imu::SampleState::FAULT;
    expected.fault = imu::SampleFault::SETUP; expected.checked_us = 0xFFFFFFFFU;
    passive(a, expected);
    same(a.read(0U), expected);
    a.beginRead(0U); a.cancelRead(0U); a.advanceRead(0U);
    passive(a, expected);
}

TEST_CASE("B3 D097 reviewer absence does not cancel pending or steal completion and excludes runtime faults") {
    imu::Acquirer a; const auto now = ready(a, 123U);
    imu_acq_fake::script.reply = imu_acq_fake::observation(now);
    REQUIRE(a.read(now).state == imu::SampleState::OBSERVATION);
    passive(a);
    const auto next = now + 1000U;
    imu_resume_fake::script.begin = imu_resume_fake::pending(next, next, 0U, true);
    REQUIRE(a.beginRead(next).state == imu::AsyncState::PENDING);
    passive(a);
    imu_resume_fake::script.advance = imu_resume_fake::complete(next, 100U);
    const auto done = a.advanceRead(next + 50U);
    REQUIRE(done.completed); REQUIRE(done.sample.sequence == 2U);
    CHECK(done.sample.observation_gap_us == 1000U);
    passive(a);
    CHECK_FALSE(a.readProgress().completed);
    const auto failed = a.read(next + 100U + config::IMU_SILENCE_US);
    REQUIRE(failed.fault == imu::SampleFault::SILENCE);
    REQUIRE(a.setupReport().state == imu::SetupState::PROFILE_READY);
    passive(a);
    same(a.read(0U), failed);
}

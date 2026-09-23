// Checks the review finding with malformed nonterminal progress replies.
// Unknown and IDLE envelopes cannot certify that native ownership has ended.
// Actual Acquirer and Setup run against independently scripted Bus replies.
#include "doctest.h"
#include "support/imu_resume_fake.h"
#include "hal/imu_acquisition.h"
#include <initializer_list>

namespace {
std::uint32_t ready(imu::Acquirer& a) {
    imu_resume_fake::reset(); imu_acq_fake::seedSetup();
    const std::uint32_t started = 123U;
    REQUIRE(a.start(started, true).state == imu::SetupState::IN_PROGRESS);
    auto now = started;
    for (unsigned i = 0U; i < 48U; ++i) {
        now = imu_acq_fake::setupTime(i, started, now); imu_fake::script.now_us = now;
        a.advanceSetup(now);
    }
    REQUIRE(a.setupReport().state == imu::SetupState::PROFILE_READY);
    return a.setupReport().observed_us;
}
}

TEST_CASE("B3 D094 reviewer malformed nonterminal begin and advance cancel regardless status") {
    for (bool beginning : {false, true}) for (auto state : {imu::AsyncState::IDLE, static_cast<imu::AsyncState>(99U)})
        for (auto status : {imu::BusStatus::NOT_INITIALIZED, imu::BusStatus::OK, imu::BusStatus::NACK}) {
            imu::Acquirer a; const auto now = ready(a);
            imu_resume_fake::script.begin = imu_resume_fake::pending(now, now, 0U, true);
            if (!beginning) REQUIRE(a.beginRead(now).state == imu::AsyncState::PENDING);
            auto p = imu_resume_fake::pending(now, now + 1U, 1U);
            p.state = state; p.acquisition.transfer.status = status;
            if (beginning) imu_resume_fake::script.begin = p; else imu_resume_fake::script.advance = p;
            imu_resume_fake::script.cancel = imu_resume_fake::cancelled(now, now + 1U);
            const auto result = beginning ? a.beginRead(now) : a.advanceRead(now + 1U);
            CHECK(result.state == imu::AsyncState::FAULT); CHECK(result.completed);
            CHECK(result.sample.fault == imu::SampleFault::RESPONSE);
            CHECK(result.sample.bus_status == imu::BusStatus::CANCELLED);
            CHECK(imu_resume_fake::script.cancels == 1U);
            CHECK_FALSE(a.advanceRead(now + 2U).completed);
            CHECK_FALSE(a.cancelRead(now + 3U).completed);
            CHECK(imu_resume_fake::script.cancels == 1U);
        }
}

TEST_CASE("B3 D094 reviewer genuine terminal transport still wins malformed remaining envelope") {
    for (bool beginning : {false, true}) for (auto state : {imu::AsyncState::COMPLETE, imu::AsyncState::FAULT}) {
        imu::Acquirer a; const auto now = ready(a);
        imu_resume_fake::script.begin = imu_resume_fake::pending(now, now, 0U, true);
        if (!beginning) REQUIRE(a.beginRead(now).state == imu::AsyncState::PENDING);
        imu::BusProgress p{}; p.state = state; p.started = true; p.completed = false;
        p.acquisition.transfer.status = imu::BusStatus::NACK;
        if (beginning) imu_resume_fake::script.begin = p; else imu_resume_fake::script.advance = p;
        const auto result = beginning ? a.beginRead(now) : a.advanceRead(now + 1U);
        CHECK(result.state == imu::AsyncState::FAULT); CHECK(result.completed);
        CHECK(result.sample.fault == imu::SampleFault::TRANSPORT);
        CHECK(result.sample.bus_status == imu::BusStatus::NACK);
        CHECK(imu_resume_fake::script.cancels == 0U);
    }
}

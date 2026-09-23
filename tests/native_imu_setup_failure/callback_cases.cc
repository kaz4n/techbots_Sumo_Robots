// Compiles the actual NativeSources callbacks against named provider substitutes.
// Makes setupFailure and legacy read observably different without private access.
// Checks every value field and forbids unrelated providers or clock observations.
#include "check_sample.h"
#include "app/native_sources_unoq.h"
#include <initializer_list>

namespace {
imu::Sample evidence;
unsigned passive_calls = 0U, legacy_calls = 0U, other_calls = 0U, clock_calls = 0U;
imu::Sample distinctEvidence() {
    imu::Sample s;
    s.state = imu::SampleState::FAULT; s.fault = imu::SampleFault::SETUP;
    s.bus_status = imu::BusStatus::BUS_ERROR; s.cleanup = imu::BusCleanup::UNCONFIRMED;
    s.error_flags = 0xf00df00dU; s.sequence = 72U; s.checked_us = 0xfffffffaU;
    s.readiness_completed_us = 24U; s.motion_started_us = 27U;
    s.observation_gap_us = 1234U; s.had_previous_observation = true;
    s.motion.status = imu::DecodeStatus::STATUS; s.motion.temperature_raw = -128;
    s.motion.started_us = 31U; s.motion.completed_us = 32U;
    s.motion.interrupt_status = 0x23U; s.motion.rail_mask = 0x45U; s.motion.coherent = true;
    for (unsigned i = 0U; i < 3U; ++i) {
        s.motion.accel_raw[i] = -21 - static_cast<int>(i);
        s.motion.gyro_raw[i] = 42 + static_cast<int>(i);
        s.motion.accel_g[i] = 0.5F + static_cast<float>(i);
        s.motion.gyro_dps[i] = -0.75F - static_cast<float>(i);
    }
    return s;
}
} // namespace

unsigned long micros() { ++clock_calls; return 0x80000000UL; }
namespace imu {
Sample Acquirer::setupFailure() const { ++passive_calls; return evidence; }
Sample Acquirer::read(std::uint32_t) { ++legacy_calls; return {}; }
SetupReport Acquirer::start(std::uint32_t, bool) { ++other_calls; return {}; }
SetupReport Acquirer::advanceSetup(std::uint32_t) { ++other_calls; return {}; }
SampleProgress Acquirer::beginRead(std::uint32_t) { ++other_calls; return {}; }
SampleProgress Acquirer::advanceRead(std::uint32_t) { ++other_calls; return {}; }
SampleProgress Acquirer::cancelRead(std::uint32_t) { ++other_calls; return {}; }
} // namespace imu
namespace opp_sensors {
InitResult Sensors::begin() { ++other_calls; return {}; }
Snapshot Sensors::read() const { ++other_calls; return {}; }
} // namespace opp_sensors
namespace line_qtr {
Status Reader::begin(bool) { ++other_calls; return Status::OK; }
Status Reader::start() { ++other_calls; return Status::OK; }
Snapshot Reader::advance() { ++other_calls; return {}; }
Snapshot Reader::cancel() { ++other_calls; return {}; }
} // namespace line_qtr
namespace power {
InputPort readerInputPort(Reader&) { ++other_calls; return {}; }
} // namespace power
namespace ui {
MatrixStatus UnoQMatrix::begin(MatrixGrant) { ++other_calls; return MatrixStatus::NOT_INITIALIZED; }
MatrixStatus UnoQMatrix::submit(std::uint32_t, const Frame&) {
    ++other_calls; return MatrixStatus::NOT_INITIALIZED;
}
} // namespace ui

TEST_CASE("B3 D097 actual NativeSources setup callback uses passive accessor and ignores caller time") {
    passive_calls = legacy_calls = other_calls = clock_calls = 0U;
    app::NativeSources native; const auto port = native.port();
    CHECK(port.context != nullptr); CHECK(port.imuSetupFailure != nullptr);
    if (port.context == nullptr || port.imuSetupFailure == nullptr) return;
    CHECK(passive_calls == 0U); CHECK(other_calls == 0U); evidence = distinctEvidence();
    unsigned expected_calls = 0U;
    for (auto time : {0U, 17U, 0x80000000U, 0xffffffffU}) {
        auto value = port.imuSetupFailure(port.context, time);
        setup_failure_test::sameSample(value, evidence); ++expected_calls;
        CHECK(passive_calls == expected_calls); CHECK(legacy_calls == 0U);
        CHECK(other_calls == 0U); CHECK(clock_calls == 0U);
        value.sequence = 0U; CHECK(evidence.sequence == 72U);
    }
    evidence = {}; setup_failure_test::sameSample(port.imuSetupFailure(port.context, 0U), {});
    CHECK(passive_calls == expected_calls + 1U); CHECK(legacy_calls == 0U);
    CHECK(other_calls == 0U); CHECK(clock_calls == 0U);
}

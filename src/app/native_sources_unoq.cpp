// Forwards application source operations directly to fixed UNO Q HAL objects.
// Adds no sensor interpretation, bus ownership, timestamps or hidden retries.
// D096 binding tests and the actual target app verify retained native calls.
#include "native_sources_unoq.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
namespace app {
NativeSources& NativeSources::self(void* context) {
    return *static_cast<NativeSources*>(context);
}
SourcePort NativeSources::port() {
    return {this, beginOpponents, readOpponents, beginLines, startLines,
        advanceLines, cancelLines, lines, startImu, advanceImuSetup, beginImu,
        advanceImu, cancelImu, imuSetupFailure, beginMatrix, submitMatrix};
}
power::InputPort NativeSources::adcPort() { return power::readerInputPort(adc_); }
opp_sensors::InitResult NativeSources::beginOpponents(void* p) {
    return self(p).opponents_.begin();
}
opp_sensors::Snapshot NativeSources::readOpponents(void* p) {
    return self(p).opponents_.read();
}
line_qtr::Status NativeSources::beginLines(void* p, bool exclusive) {
    return self(p).lines_.begin(exclusive);
}
line_qtr::Status NativeSources::startLines(void* p) { return self(p).lines_.start(); }
line_qtr::Snapshot NativeSources::advanceLines(void* p) { return self(p).lines_.advance(); }
line_qtr::Snapshot NativeSources::cancelLines(void* p) { return self(p).lines_.cancel(); }
line_qtr::Snapshot NativeSources::lines(void* p) { return self(p).lines_.report(); }
imu::SetupReport NativeSources::startImu(void* p, std::uint32_t t, bool power) {
    return self(p).imu_.start(t, power);
}
imu::SetupReport NativeSources::advanceImuSetup(void* p, std::uint32_t t) {
    return self(p).imu_.advanceSetup(t);
}
imu::SampleProgress NativeSources::beginImu(void* p, std::uint32_t t) {
    return self(p).imu_.beginRead(t);
}
imu::SampleProgress NativeSources::advanceImu(void* p, std::uint32_t t) {
    return self(p).imu_.advanceRead(t);
}
imu::SampleProgress NativeSources::cancelImu(void* p, std::uint32_t t) {
    return self(p).imu_.cancelRead(t);
}
imu::Sample NativeSources::imuSetupFailure(void* p, std::uint32_t t) {
    return self(p).imu_.read(t);
}
ui::MatrixStatus NativeSources::beginMatrix(void* p, ui::MatrixGrant grant) {
    return self(p).matrix_.begin(grant);
}
ui::MatrixStatus NativeSources::submitMatrix(void* p, std::uint32_t t, const ui::Frame& f) {
    return self(p).matrix_.submit(t, f);
}
} // namespace app
#endif

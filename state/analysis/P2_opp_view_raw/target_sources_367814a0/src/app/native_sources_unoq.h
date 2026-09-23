// Binds each application source callback to one existing native HAL owner.
// Keeps pad, ADC and I2C lifetimes fixed without another resource router.
// D096 native binding substitutes and target app compilation verify this wiring.
#pragma once
#include "runtime.h"

namespace app {
class NativeSources {
public:
    NativeSources() = default;
    NativeSources(const NativeSources&) = delete;
    NativeSources& operator=(const NativeSources&) = delete;
    SourcePort port();
    power::InputPort adcPort();
private:
    static NativeSources& self(void* context);
    static opp_sensors::InitResult beginOpponents(void* context);
    static opp_sensors::Snapshot readOpponents(void* context);
    static line_qtr::Status beginLines(void* context, bool exclusive);
    static line_qtr::Status startLines(void* context);
    static line_qtr::Snapshot advanceLines(void* context);
    static line_qtr::Snapshot cancelLines(void* context);
    static line_qtr::Snapshot lines(void* context);
    static imu::SetupReport startImu(void*, std::uint32_t, bool);
    static imu::SetupReport advanceImuSetup(void*, std::uint32_t);
    static imu::SampleProgress beginImu(void*, std::uint32_t);
    static imu::SampleProgress advanceImu(void*, std::uint32_t);
    static imu::SampleProgress cancelImu(void*, std::uint32_t);
    static imu::Sample imuSetupFailure(void*, std::uint32_t);
    static ui::MatrixStatus beginMatrix(void*, ui::MatrixGrant);
    static ui::MatrixStatus submitMatrix(void*, std::uint32_t, const ui::Frame&);
    opp_sensors::Sensors opponents_;
    line_qtr::Reader lines_;
    power::Reader adc_;
    imu::Acquirer imu_;
    ui::UnoQMatrix matrix_;
};
} // namespace app

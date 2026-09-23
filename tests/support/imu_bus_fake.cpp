// Defines host-only concrete Bus methods returning independently scripted replies.
// Exercises production Setup without native registers, Arduino or real time.
// D080 recipe, fault injection and variant tests check every recorded request.
#include "imu_bus_fake.h"

namespace imu_fake {
Script script{};
void reset() { script = Script{}; }

std::size_t record(Kind kind, imu::Register reg, std::uint8_t value) {
    const auto index = script.count++;
    if (index >= CAPACITY) {
        script.overflow = true;
        return CAPACITY - 1U;
    }
    script.calls[index] = {kind, reg, value};
    script.call_us[index] = script.now_us;
    return index;
}

imu::BusTransfer transfer(Kind kind, imu::Register reg, std::uint8_t value) {
    const auto index = record(kind, reg, value);
    const auto& reply = script.replies[index];
    auto result = reply.transfer;
    result.started_us = script.now_us + reply.start_offset_us;
    result.completed_us = result.started_us + reply.duration_us;
    script.completed_us[index] = result.completed_us;
    return result;
}
} // namespace imu_fake

namespace imu {
BusInit Bus::begin() {
    const auto index = imu_fake::record(imu_fake::Kind::BEGIN, Register::IDENTITY, 0U);
    return imu_fake::script.replies[index].init;
}
BusTransfer Bus::readRegister(Register reg) {
    return imu_fake::transfer(imu_fake::Kind::READ, reg, 0U);
}
BusTransfer Bus::writeRegister(Register reg, std::uint8_t value) {
    return imu_fake::transfer(imu_fake::Kind::WRITE, reg, value);
}
BusTransfer Bus::readMotion() {
    return imu_fake::transfer(imu_fake::Kind::MOTION, Register::INTERRUPT_STATUS, 0U);
}
} // namespace imu

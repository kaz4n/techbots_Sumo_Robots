// Retains the concrete setup lifecycle, native transport and pure decoder.
// The sketch stores this address but never invokes it during startup or loop.
// Independent startup tests and target disassembly check the unused call path.
#include "imu_setup_probe.h"

namespace imu_setup_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result{};
    result.started = setup_driver.start(0U, true);
    result.advanced = setup_driver.advance(0U);
    const auto transfer = bus.readMotion();
    result.decoded = imu::decodeMotion(transfer);
    return result;
}
} // namespace imu_setup_probe

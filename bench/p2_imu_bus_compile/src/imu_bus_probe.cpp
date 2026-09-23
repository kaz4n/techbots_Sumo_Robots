// Retains concrete native admission, register, burst and fault paths.
// Neither static initialization nor sketch startup calls this function.
// Independent startup tests and target ELF inspection verify retention only.
#include "imu_bus_probe.h"

namespace imu_bus_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result;
    result.init = bus.begin();
    result.identity = bus.readRegister(imu::Register::IDENTITY);
    result.configuration = bus.writeRegister(imu::Register::POWER_1, 0U);
    result.motion = bus.readMotion();
    return result;
}
} // namespace imu_bus_probe

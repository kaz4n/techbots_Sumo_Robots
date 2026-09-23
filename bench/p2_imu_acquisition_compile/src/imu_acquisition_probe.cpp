// Retains actual Acquirer, Setup, decoder and native shared-budget Bus methods.
// The sketch stores this address but never invokes it during startup or loop.
// Independent startup tests and target disassembly check the unused call path.
#include "imu_acquisition_probe.h"

namespace imu_acquisition_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result{};
    result.started = acquirer.start(0U, true);
    result.advanced = acquirer.advanceSetup(0U);
    result.sample = acquirer.read(0U);
    return result;
}
} // namespace imu_acquisition_probe

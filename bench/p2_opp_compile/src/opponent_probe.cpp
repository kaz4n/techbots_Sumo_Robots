// Retains real native opponent initialization and raw-read paths for compilation.
// The function is never invoked by setup or loop, so no pad is configured or read.
// Independent host startup and target ELF review distinguish retention from a run.
#include "opponent_probe.h"

namespace opponent_probe {
__attribute__((noinline, used)) Result exercise() {
    Result result;
    result.initialization = sensors.begin();
    result.sample = sensors.read();
    return result;
}
} // namespace opponent_probe

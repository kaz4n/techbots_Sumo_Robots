// Exercises the real synthetic runner locally without MCU or substituted core.
// Provides a deterministic host clock solely for an implementation smoke check.
// Independent tests remain owned by the separate author.
#include "recorder_bench.h"
#include <cstdio>
static std::uint32_t now_us = 0;
std::uint32_t clockNow(void*) { return now_us; }
int main() {
    static recorder_bench::Runner runner({nullptr, clockNow});
    if (!runner.begin()) return 1;
    for (unsigned i = 0; i < 201100; ++i) {
        now_us += 1000;
        runner.poll();
    }
    for (unsigned i = 0; i < 10000; ++i) { ++now_us; runner.poll(); }
    const auto& r = runner.report();
    std::printf("{\"phase\":%u,\"failure\":%u,\"ticks\":%u,\"release_us\":%u,\"stop_us\":%u,\"elapsed_us\":%u,\"frames\":%u,\"events\":%u,\"rows\":%u,\"crc\":%u,\"incomplete\":%u,\"go\":%u,\"robot_faults\":%u,\"gate_fault\":%u,\"nonzero_pwm\":%u,\"enabled_en\":%u}\n",r.phase,r.failure,r.ticks,r.release_us,r.stop_us,r.elapsed_us,r.frame_count,r.event_count,r.checksum_rows,r.crc32,r.incomplete,r.go_seen,r.robot_faults,r.gate_fault,r.nonzero_pwm,r.enabled_en);
    return r.phase == static_cast<unsigned>(recorder_bench::Phase::FROZEN) && r.failure == 0 &&
           r.go_seen == 1 && r.nonzero_pwm == 0 && r.enabled_en == 0 ? 0 : 2;
}

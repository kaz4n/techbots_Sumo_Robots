// Emits an actual synthetic Robot/MotorGate/recorder/Transfer byte stream.
// Lets the independent Python receiver test real C++ output and retained losses.
// Host-only executable; stdout is wire bytes, stderr is fixture failure only.
#include "dump_fixture.h"
#include <iostream>
int main() {
    dump_test::Pipeline pipeline;
    pipeline.startAttempt();
    pipeline.sealByStop();
    if (pipeline.source.phase() != recorder::AttemptPhase::SEALED) return 2;
    pipeline.resetPreserving();
    pipeline.selectDump();
    pipeline.requestDump();
    if (!pipeline.finish() || pipeline.writes.enabled != 0U || pipeline.writes.nonzero != 0U) return 3;
    std::cout << pipeline.sink.bytes;
    return 0;
}

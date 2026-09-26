// Runs the fixed native acquisition, decision, MotorGate, recorder and dump pipeline.
// Keeps unconfirmed setup grants absent and all physical acceptance explicit.
// D096/D101 runtime tests and D180 configured-entry tests verify this binding.
#pragma push_macro("EMPTY")
#undef EMPTY
#include "src/app/native_sources_unoq.h"
#include "src/app/configured_setup.h"
#include "src/hal/motor_port_unoq.h"
#pragma pop_macro("EMPTY")
#if SUMOX_TIMING_EVIDENCE
#include "src/app/outer_loop_timing.h"
// External identity plus the loop's compiler escape retain observable target data.
app::outer_loop_timing::Observer outer_loop_timing __attribute__((used));
#endif

namespace {
app::NativeSources sources;
motors::UnoQPort motor_port;
recorder::dump::UnoQDumpPort dump_port{recorder::dump::Buffering::FIFO8};
app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port(),
    app::unoQDumpPort(dump_port)};
#if SUMOX_TIMING_EVIDENCE
const auto timing_port = motor_port.port();
#endif
}

void setup() {
    // Every checked-in grant remains unconfirmed; build mode grants nothing.
    runtime.begin(app::configuredSetupGrants());
}

void loop() {
#if SUMOX_TIMING_EVIDENCE
    if (!outer_loop_timing.terminal()) {
        outer_loop_timing.entry(timing_port.clockUs(timing_port.context));
        const auto before = app::outer_loop_timing::Context::read(runtime.report());
        const bool completed = runtime.step();
        outer_loop_timing.result(before,
            app::outer_loop_timing::Context::read(runtime.report()), completed);
        // Publication survives optimization; this work belongs to the wall interval.
        // The final drain's store/freeze/escape tail is explicitly outside population.
        __asm__ volatile("" : : "g"(&outer_loop_timing) : "memory");
        return;
    }
#endif
    runtime.step();
}

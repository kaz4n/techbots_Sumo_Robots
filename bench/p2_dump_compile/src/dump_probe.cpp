// Retains real recorder storage, authority checks and native transport for linking.
// Does not run: the sketch only stores this function pointer for ELF inspection.
// Actual host pipeline tests establish behavior; this source proves target coverage.
#include "dump_probe.h"
namespace dump_probe {
fsm::Robot robot;
recorder::AttemptRecorder source;
recorder::dump::UnoQDumpPort native;
recorder::dump::Transfer transfer{native.port()};
__attribute__((noinline, used)) Result exercise(fsm::RobotInput input,
        const recorder::dump::SetupGrant& grant, bool reset) {
    Result result;
    result.native = native.begin(grant);
    result.robot = robot.step(input);
    source.consume(result.robot);
    result.transfer = transfer.step({input.t_us, input.t_us, native.ready(),
        recorder::dump::Origin::SYNTHETIC}, result.robot, source);
    if (reset) {
        transfer.onRobotReset();
        source.onRobotReset();
        robot.reset();
    }
    return result;
}
}

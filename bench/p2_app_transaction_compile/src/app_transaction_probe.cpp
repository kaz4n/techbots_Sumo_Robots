// Links the sole application transaction owner to the actual native motor port.
// Does not run; real source acquisition and scheduling remain future integration.
// D095 independent tests verify behavior and ELF inspection verifies retained code.
#include "app_transaction_probe.h"
namespace app_transaction_probe {
motors::UnoQPort native_motors;
app::Transaction transaction{native_motors.port()};
__attribute__((noinline, used)) bool exercise(Action action, fsm::RobotInput input) {
    switch (action) {
    case Action::INITIALIZE: return transaction.initialize();
    case Action::OPEN: return transaction.open();
    case Action::DECIDE: return transaction.decide(input);
    case Action::FINISH: return transaction.finish();
    case Action::ABORT: transaction.abort(); return false;
    }
    return false;
}
} // namespace app_transaction_probe

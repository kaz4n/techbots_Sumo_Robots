// Retains the actual D095 app transaction owner and native MotorGate boundary.
// Setup stores a pointer only; no control or peripheral method executes.
// Host startup substitutes and target ELF inspection verify compile-only scope.
#include "src/app_transaction_probe.h"
namespace app_transaction_probe { Probe volatile entry = nullptr; }
void setup() { app_transaction_probe::entry = &app_transaction_probe::exercise; }
void loop() {}

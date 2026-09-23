// Runs the actual Runtime with absent sources on the bare UNO Q.
// Initializes no external pin, motor backend, bus, ADC, UART or Bridge.
// Independent host contracts, ELF review and RAM capture provide scoped evidence.
#include "src/runtime_native.h"
void setup() { runtime_native::begin(); }
void loop() { runtime_native::poll(); }

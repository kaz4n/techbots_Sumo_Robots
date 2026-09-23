// Runs the D091 synthetic recorder experiment on the bare UNO Q.
// No sensor, header output, UART or motor backend is initialized.
// Host contracts, exact ELF review and read-only RAM capture are separate evidence.
#include "src/recorder_native.h"
void setup() { recorder_native::begin(); }
void loop() { recorder_native::poll(); }

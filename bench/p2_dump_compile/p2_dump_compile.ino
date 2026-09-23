// Retains the complete D090 recorder/owner/native path for target linking.
// Neither setup nor loop initializes peripherals or invokes the retained probe.
// Actual board compilation and ELF inspection are distinct from runtime tests.
#include "src/dump_probe.h"
namespace dump_probe { Probe volatile entry = nullptr; }
void setup() { dump_probe::entry = &dump_probe::exercise; }
void loop() {}

// Exposes only the native clock required by the frozen dump contract.
// Missing stock Bridge, Serial and Monitor declarations prevent accidental use.
// The independent harness counts and controls every clock observation.
#pragma once
unsigned long micros();

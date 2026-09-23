// Provides a counted clock and only the native API used by the QTR contract.
// No analogRead, delay, heap, serial or Bridge substitution is available.
// The independent B2 executable supplies deterministic micros observations.
#pragma once
unsigned long micros();

// Arduino API Common.h preserves this global macro in the actual target build.
#define bit(b) (1UL << (b))

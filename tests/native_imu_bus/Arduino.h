// Provides a counted clock and only the native API used by the IMU transport contract.
// No analogRead, delay, heap, serial or Bridge substitution is available.
// The independent B3 executable supplies deterministic micros observations.
#pragma once
unsigned long micros();

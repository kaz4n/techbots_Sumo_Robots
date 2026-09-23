// Supplies only the clock API admitted by the native motor contract.
// Missing delay, Arduino output, serial and Bridge APIs reject accidental use.
// Counted host definitions exercise actual backend callbacks without hardware.
#pragma once
unsigned long micros();

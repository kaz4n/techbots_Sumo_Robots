// Declares the bare-board recorder experiment entry points.
// Keeps Arduino macros outside the pure runner's public interface.
// Target compilation and fixed diagnostic capture check this wrapper.
#pragma once
namespace recorder_native {
void begin();
void poll();
}

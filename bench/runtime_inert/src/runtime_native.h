// Declares the actual Runtime bare-board probe entry points.
// Keeps Arduino macros outside the pure checked runner interface.
// Exact target review and immutable diagnostic capture verify this wrapper.
#pragma once
namespace runtime_native {
void begin();
void poll();
}

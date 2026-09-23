// Models the installed public Zephyr device surface used by the adapter.
// Readiness stays independently observable and cannot imply pin or output state.
// Host native cases inject loss and error status without changing production code.
#pragma once
struct device { const void* config; unsigned index; };
bool device_is_ready(const device*);

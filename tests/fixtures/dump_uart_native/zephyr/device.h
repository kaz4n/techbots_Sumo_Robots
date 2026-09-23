// Supplies installed-shaped device metadata under independent host control.
// Device initialization and readiness remain separately observable conditions.
// Tests inject missing metadata and init/readiness failure before UART use.
#pragma once
struct device_state { unsigned init_res; bool initialized; };
struct device { const void* config; void* data; const void* api; device_state* state; };
extern device dump_devices[4];
bool device_is_ready(const device*);
int device_init(const device*);

// Models source-verified native device metadata and readiness.
// Config, data, API and state can independently become unavailable.
// Whole-bank admission must fail before a native configuration request.
#pragma once
#include <cstdint>
struct device_state { std::uint8_t init_res; bool initialized : 1; };
struct device { const void* config; void* data; const void* api; device_state* state; unsigned index; };
extern device fixture_devices[3];
extern device fixture_unknown_device;
bool device_is_ready(const device*);

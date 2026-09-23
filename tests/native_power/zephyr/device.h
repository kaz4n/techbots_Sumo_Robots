// Models installed Zephyr device readiness and deferred-initialization state.
// Never-initialized is distinct from a failed stock ADC initialization.
// Admission cases mutate state independently of all hardware register flags.
#pragma once
#include <cstdint>
struct device_state { std::uint8_t init_res; bool initialized : 1; };
struct device { const void* config; const void* api; device_state* state; unsigned index; };
bool device_is_ready(const device*);
extern device fixture_devices[5];

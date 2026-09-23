// Declares a controlled native matrix counter readiness interface.
// Tests distinguish null pointers, unready devices and readiness itself.
// The actual adapter includes this header only in isolated host builds.
#pragma once
struct device { bool ready; };
extern const device* fixture_matrix_device;
bool device_is_ready(const device* value);
#define DEVICE_DT_GET(node) ((node) == 233 ? fixture_matrix_device : nullptr)

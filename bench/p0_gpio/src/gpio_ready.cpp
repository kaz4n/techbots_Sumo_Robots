// Queries the installed GPIOH device readiness without configuring a pin.
// Prevents a GPIO timing run from claiming success on an uninitialized device.
// Installed export and candidate relocation audits supplement host substitutes.
#include "gpio_capture.h"
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

namespace p0 {
bool gpioReady() {
    return device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpioh)));
}
} // namespace p0

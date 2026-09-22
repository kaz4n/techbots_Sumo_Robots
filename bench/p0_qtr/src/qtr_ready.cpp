// Checks the two installed GPIO controllers without changing their registers.
// Prevents diagnostic pad operations before both loader-owned devices are ready.
// Exact target binary/export review verifies these installed DT bindings.
#include "qtr_capture.h"
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

namespace p0 {
std::uint32_t qtrReadyMask() {
    const bool a = device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpioa)));
    const bool b = device_is_ready(DEVICE_DT_GET(DT_NODELABEL(gpiob)));
    return (a ? 1U : 0U) | (b ? 2U : 0U);
}
} // namespace p0

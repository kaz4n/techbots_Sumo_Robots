// Forwards bench callbacks to one existing opponent sensor and matrix owner.
// Leaves construction and port discovery passive and every setup grant explicit.
// Counted owner substitutes and target inspection verify the direct D107 binding.
#include "opp_view_native.h"
#include <Arduino.h>

namespace opp_view {
Port Native::port() {
    return {this, clockUs, beginOpponents, readOpponents, beginMatrix, submitMatrix};
}

std::uint32_t Native::clockUs(void*) {
    return static_cast<std::uint32_t>(micros());
}

opp_sensors::InitResult Native::beginOpponents(void* context) {
    return static_cast<Native*>(context)->opponents_.begin();
}

opp_sensors::Snapshot Native::readOpponents(void* context) {
    return static_cast<Native*>(context)->opponents_.read();
}

ui::MatrixStatus Native::beginMatrix(void* context, ui::MatrixGrant grant) {
    return static_cast<Native*>(context)->matrix_.begin(grant);
}

ui::MatrixStatus Native::submitMatrix(void* context, std::uint32_t t_us,
                                    const ui::Frame& frame) {
    return static_cast<Native*>(context)->matrix_.submit(t_us, frame);
}
} // namespace opp_view

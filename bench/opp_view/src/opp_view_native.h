// Binds the opponent-view bench to exactly one existing sensor and matrix owner.
// Keeps all setup grants explicit and performs no constructor or motor I/O.
// Counted owner substitutes and target startup inspection verify the real binding.
#pragma once
#include "opp_view.h"

namespace opp_view {
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    Port port();
private:
    static std::uint32_t clockUs(void* context);
    static opp_sensors::InitResult beginOpponents(void* context);
    static opp_sensors::Snapshot readOpponents(void* context);
    static ui::MatrixStatus beginMatrix(void* context, ui::MatrixGrant grant);
    static ui::MatrixStatus submitMatrix(void* context, std::uint32_t t_us,
                                         const ui::Frame& frame);
    opp_sensors::Sensors opponents_;
    ui::UnoQMatrix matrix_;
};
} // namespace opp_view

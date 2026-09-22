// Implements the B12 O2 DIRECT opener using the approved B7 straight primitive.
// Reports transition intents so global arbitration retains all safety authority.
// Independent host tests check snapshots, priority, timing and bounded demands.
#include "core/openers.h"
#include "config.h"

namespace openers {
namespace {
Result terminal(Exit exit) {
    Result result;
    result.exit = exit;
    result.motion.status = exit == Exit::INVALID ? motion::Status::INVALID :
                           exit == Exit::NONE ? motion::Status::IDLE : motion::Status::DONE;
    return result;
}
} // namespace

bool Direct::start(std::uint32_t t_us, float heading_deg,
                   std::uint8_t countdown_snapshot) {
    active_ = straight_.start(t_us, heading_deg, config::OPENER_DUTY_MAX, config::DIRECT_MS);
    exit_ = active_ ? Exit::NONE : Exit::INVALID;
    snapshot_ = static_cast<std::uint8_t>(countdown_snapshot & 0x7FU);
    return active_;
}

Result Direct::step(std::uint32_t t_us, float heading_deg, bool imu_ok,
                    std::uint8_t confirmed_opp_mask) {
    if (!active_) return terminal(exit_);
    if (((confirmed_opp_mask | snapshot_) & 0x07U) != 0U) {
        exit_ = Exit::FRONT_TARGET;
    } else if ((confirmed_opp_mask & 0x78U) != 0U) {
        exit_ = Exit::SIDE_OR_REAR_TARGET;
    }
    snapshot_ = 0U;
    if (exit_ != Exit::NONE) {
        active_ = false;
        return terminal(exit_);
    }
    Result result;
    result.motion = straight_.step(t_us, heading_deg, imu_ok);
    if (result.motion.status == motion::Status::DONE) exit_ = Exit::SEARCH;
    if (result.motion.status == motion::Status::INVALID) exit_ = Exit::INVALID;
    result.exit = exit_;
    active_ = exit_ == Exit::NONE;
    return result;
}

void Direct::reset() { *this = Direct{}; }
} // namespace openers

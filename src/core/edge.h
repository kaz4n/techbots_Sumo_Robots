// Defines B4.1 classification and the D-020 persistent-edge safety guard.
// Keeps acquisition, escape motion scripts and hardware writes outside this module.
// Locked host tests cover thresholds, persistent masks and latched all-white faults.
#pragma once
#include <cstdint>

namespace edge {
class Classifier {
public:
    // Each call represents one NEW complete observation. Repeated/stale samples
    // must not be passed as fresh. This API does not implement or validate a HAL.
    // Returns confirmed white levels (not rising edges), so white persists.
    std::uint8_t observe(const std::uint32_t (&raw_us)[4]);
    void reset();
private:
    std::uint32_t consecutive_[4] = {};
};

struct GuardResult {
    bool escape_required = false;
    bool fault_latched = false;
    bool inhibit_motion = true; // A veto; false does not itself authorize motion.
};
class Guard {
public:
    // One confirmed fresh line mask per tick; only the low four bits are used.
    // This implements the default zero push-through window only; compilation
    // rejects a positive configured window until that bounded exception exists.
    // Before motion permission, do not enter escape/latch a new line fault.
    // Afterwards any persistent white requires escape. Once entered, all black
    // AND script_finished are both required to leave. All-white latches a motion
    // veto until reset, even if later black or permission is revoked. When the
    // permission gate is closed, escape_required is false and inhibition wins.
    // This does not choose a motion direction or execute a script/MotorGate.
    GuardResult step(std::uint8_t line_mask, bool motion_permitted,
                     bool script_finished);
    void reset();
private:
    bool escaping_ = false;
    bool fault_latched_ = false;
};
} // namespace edge

// Declares one-shot native setup and inhibition evidence using the existing Gate.
// Keeps permission default-false and preserves setup failure separately from halt.
// Independent D115 callback traces and terminal-passivity checks verify this owner.
#pragma once
#include "config.h"
#include "hal/motors.h"
#include <cstdint>

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Motor inhibition bench requires inert flags");

namespace motor_stand {
enum class Phase : std::uint8_t {
    NOT_STARTED, DISABLED, ACTIVE, COMPLETE, FAULT
};
struct Grants {
    bool exclusive_motor_outputs = false;
};
struct Report {
    Phase phase = Phase::NOT_STARTED;
    bool begin_called = false;
    bool begin_ok = false;
    motors::Fault begin_fault = motors::Fault::NONE;
    bool halt_called = false;
    motors::HaltResult halt;
};
class Runner {
public:
    explicit Runner(const motors::Port& port);
    Runner(const Runner&) = delete;
    Runner& operator=(const Runner&) = delete;
    bool begin(const Grants& grants);
    void poll();
    const Report& report() const;
private:
    motors::MotorGate gate_;
    Report report_;
    bool attempted_ = false;
};
} // namespace motor_stand

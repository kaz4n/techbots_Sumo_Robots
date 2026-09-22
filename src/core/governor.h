// Defines the B6 final electrical duty envelope approved in D-017.
// Separates duty shaping from state arbitration and hardware MotorGate writes.
// Independent host tests exercise low-voltage caps, slew, braking and finite values.
#pragma once
#include <cstdint>

namespace governor {
// Profiles name the specified B6 cap rows. The future FSM selects its phase's
// profile; choosing an escape forward-motion cap is still an unresolved contract.
enum class Profile : std::uint8_t {
    SEARCH_FORWARD, PIVOT, OPENER, ATTACK, EDGE_REVERSE, REFLANK_BACK, REFLANK_TURN
};
struct Request {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    float vbat_v = 0.0F;
    Profile profile = Profile::SEARCH_FORWARD;
    bool centered = false;
    bool contact = false;
    bool inhibited = true;
    bool brake = false;
};
struct Result {
    float duty_l = 0.0F;
    float duty_r = 0.0F;
    float filtered_vbat_v = 0.0F;
    bool valid = true; // Nonfinite request/voltage or unknown profile returns zeros.
};
class Governor {
public:
    // Called each tick, including inhibited ticks. First call establishes time
    // and battery state, with zero elapsed acceleration budget. No I/O or clock.
    // Filter: one-second first-order lag, backward-Euler discretization.
    // Compensation precedes caps and slew; cap decreases and all braking are
    // immediate. A sign reversal returns zero before accelerating the other way.
    // ATTACK_DUTY is eligible only with BOTH centered and contact; otherwise use
    // ATTACK_APPROACH_DUTY. Inhibit always clears the remembered output duty.
    Result step(std::uint32_t t_us, const Request& request);
    void reset();
private:
    std::uint32_t last_us_ = 0;
    float filtered_vbat_v_ = 0.0F;
    float last_l_ = 0.0F;
    float last_r_ = 0.0F;
    bool initialized_ = false;
    bool battery_initialized_ = false;
};
} // namespace governor

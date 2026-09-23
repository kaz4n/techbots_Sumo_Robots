// Applies Robot-governed commands through the sole checked motor write boundary.
// Keeps failed writes, countdown permission and unverified hardware fail-closed.
// Independent port-trace tests cover R1/R6; target probes never execute motor I/O.
#pragma once
#include "../core/fsm.h"
#include <cstdint>

namespace motors {
enum class Channel : std::uint8_t { LEFT_FORWARD, LEFT_REVERSE, RIGHT_FORWARD, RIGHT_REVERSE };
enum class Fault : std::uint8_t { NONE, NOT_INITIALIZED, PORT, IO, COMMAND, TOKEN, STOPPED };
struct Port {
    void* context = nullptr;
    bool (*configureEnableLow)(void*) = nullptr;
    bool (*configurePwm)(void*, Channel) = nullptr;
    bool (*writeEnable)(void*, bool) = nullptr;
    bool (*writePwm)(void*, Channel, std::uint32_t, std::uint32_t) = nullptr;
    bool (*settle)(void*) = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
    std::uint32_t period_cycles[4] = {};
};
struct Result {
    fsm::PreviousTick feedback;
    Fault fault = Fault::NONE;
    bool consumed = false;
};
class MotorGate {
public:
    // Exact callback, lifecycle, failure and receipt rules: P2_motor_gate_contract.md.
    explicit MotorGate(const Port& port);
    bool begin();
    Result apply(std::uint32_t decision_us, const fsm::RobotResult& command);
    bool reset();
    Fault fault() const;
private:
    bool validPort() const;
    bool zeroPwm();
    bool inhibit();
    bool validCommand(std::uint32_t now, const fsm::RobotResult& command);
    bool transact(const core::Outputs& output, fsm::PreviousTick& feedback);
    void disarm();
    Port port_;
    Fault fault_ = Fault::NONE;
    bool initialized_ = false;
    bool began_ = false;
    bool armed_ = false;
    bool hold_complete_ = false;
    std::uint32_t release_us_ = 0;
    std::uint64_t last_token_ = 0;
};
} // namespace motors

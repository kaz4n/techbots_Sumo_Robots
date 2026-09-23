// Owns fixed A0/A1 acquisition calls and bounded battery evidence for the app.
// Retains truthful source time while shared ADC faults invalidate both outputs.
// Independent port/native/Robot/MotorGate tests verify the D093 contract.
#pragma once
#include "power.h"
#include "ui.h"
#include <cstdint>

namespace power {
struct InputPort {
    void* context = nullptr;
    InitResult (*beginWithButtons)(void*) = nullptr;
    Sample (*readA0)(void*) = nullptr;
    ButtonSample (*readA1)(void*) = nullptr;
    std::uint32_t (*clockUs)(void*) = nullptr;
};
enum class InputFault : std::uint8_t { NONE, PORT, CONFIG, SETUP, ADC, CLOCK, SOURCE };
enum class InputOperation : std::uint8_t { NONE, SETUP, BATTERY, BUTTONS, OBSERVE };
struct BatteryRead { bool attempted = false; bool accepted = false; Sample sample; };
struct ButtonRead { bool attempted = false; bool accepted = false; ButtonSample sample; };
struct InputReport {
    bool attempted = false;
    bool ready = false;
    bool battery_available = false;
    bool battery_due = false;
    InputFault fault = InputFault::NONE;
    InputOperation fault_operation = InputOperation::NONE;
    Status first_status = Status::NOT_INITIALIZED;
    Shutdown first_shutdown = Shutdown::NOT_ATTEMPTED;
    InitResult setup;
    Sample battery; // Last accepted source even after expiry; availability is separate.
    std::uint32_t observed_us = 0;
    std::uint32_t battery_age_us = 0;
    std::uint64_t battery_generation = 0; // Accepted callback identity, not ADC hardware sequence.
    std::uint32_t battery_attempts = 0;
    std::uint32_t button_attempts = 0;
    std::uint32_t battery_refused = 0;
    std::uint32_t button_refused = 0;
};
class InputOwner {
public:
    explicit InputOwner(const InputPort& port);
    InputOwner(const InputOwner&) = delete;
    InputOwner& operator=(const InputOwner&) = delete;
    // Exactly one setup attempt; no constructor/destructor I/O and no reset API.
    bool begin();
    // Caller supplies a scheduler grant covering the actual bounded native call.
    // No catch-up, delay or hidden second conversion. Faults prevent future callbacks.
    BatteryRead readBatteryIfDue(bool slot_granted);
    ButtonRead readButtons(bool slot_granted);
    // Same clock domain as port; successive observations must be less than half-range.
    // Pure snapshot updates accumulated age; expired evidence never revives unaided.
    InputReport observe(std::uint32_t decision_us);
    const InputReport& report() const;
    // Mutate only the named input fields; preserve initialization/time/other sensors.
    bool applyBattery(fsm::RobotInput& input);
    ui::ButtonQualification applyButtons(fsm::RobotInput& input, const ButtonRead& read);
private:
    bool validPort() const;
    bool validConfig() const;
    bool advance(std::uint32_t now, InputOperation operation);
    bool interval(std::uint32_t before, std::uint32_t started,
                  std::uint32_t completed, std::uint32_t after) const;
    void fail(InputFault fault, InputOperation operation, Status status, Shutdown shutdown);
    void updateAvailability();
    InputPort port_;
    InputReport report_;
    bool observed_ = false;
    bool battery_seen_ = false;
    bool button_seen_ = false;
    std::uint32_t button_sequence_ = 0;
};
// Thin target binding: same Reader lifetime, exact pair setup/read methods, micros.
// Factory does not initialize or sample. Native definition is target-only.
InputPort readerInputPort(Reader& reader);
} // namespace power

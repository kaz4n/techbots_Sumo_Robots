// Declares the sole existing UNO Q motor port for this inhibition diagnostic.
// Keeps construction and port retrieval passive with no new native callbacks.
// Independent counted-owner substitutions and target audits verify this binding.
#pragma once
#include "motor_stand.h"
#include "hal/motor_port_unoq.h"

namespace motor_stand {
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    motors::Port port();
private:
    motors::UnoQPort native_;
};
} // namespace motor_stand

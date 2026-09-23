// Owns bounded native UNO Q matrix submissions after an explicit setup grant.
// Void hardware APIs report unconfirmed submission, never optical success.
// Independent native seam and retained target disassembly verify D088 guards.
#pragma once
#include "ui_display.h"

namespace ui {
enum class MatrixStatus : std::uint8_t {
    NOT_INITIALIZED, INIT_UNCONFIRMED, SUBMITTED_UNCONFIRMED, THROTTLED,
    INVALID_GRANT, CONTEXT_REJECTED, DEVICE_UNAVAILABLE, INVALID_FRAME,
    ALREADY_OWNED, FAULTED
};
struct MatrixGrant {
    bool normal_startup = false;
    bool exclusive_boot_owner = false;
};
class UnoQMatrix {
public:
    UnoQMatrix() = default;
    UnoQMatrix(const UnoQMatrix&) = delete;
    UnoQMatrix& operator=(const UnoQMatrix&) = delete;
    // Setup only. One lifetime grant per boot. No destructor/release/reset I/O.
    MatrixStatus begin(MatrixGrant grant);
    // First submit immediately, later >=UI_FRAME_PERIOD_US. Validate every call,
    // including throttled ones. Distinct times must be <half a uint32 wrap apart.
    // Wrong frame/context latches local fault; never submit again until reset.
    MatrixStatus submit(std::uint32_t t_us, const Frame& frame);
private:
    bool initialized_ = false;
    bool faulted_ = false;
    bool submitted_ = false;
    std::uint32_t last_submit_us_ = 0U;
};
} // namespace ui

// Submits bounded grayscale frames through the installed UNO Q matrix C API.
// A boot owner and exact PRIMASK restoration protect the shared ISR framebuffer.
// Independent native substitutes and retained target disassembly test D088.
#include "ui_matrix_unoq.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include "../config.h"
#include <cmsis_core.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

// Exact declarations from the installed Arduino_LED_Matrix 0.1.3 header.
// Avoid its optional graphics and animation wrapper paths.
extern "C" {
void matrixBegin(void);
void matrixSetGrayscaleBits(std::uint8_t bits);
void matrixGrayscaleWrite(const std::uint8_t* buffer);
}

namespace ui {
namespace {
static_assert(FRAME_BYTES == 104U, "Native matrix copies exactly 104 bytes");
static_assert(config::UI_FRAME_PERIOD_US > 0U &&
              config::UI_FRAME_PERIOD_US < 0x80000000U,
              "Matrix cadence must fit the forward timestamp interval");

// The exclusive boot grant includes serialized setup and every other writer.
// Destruction and local faults never release the lifetime claim.
bool matrix_claimed = false;

bool contextValid() {
    return (__get_CONTROL() & 1U) == 0U && __get_IPSR() == 0U;
}

bool frameValid(const Frame& frame) {
    bool valid = true;
    for (unsigned i = 0U; i < FRAME_BYTES; ++i) {
        valid &= frame.pixels[i] <= 7U;
    }
    return valid;
}

void writeFrame(const Frame& frame) {
    const std::uint32_t saved_primask = __get_PRIMASK();
    __disable_irq();
    matrixGrayscaleWrite(frame.pixels);
    __DMB();
    __set_PRIMASK(saved_primask);
}
} // namespace

MatrixStatus UnoQMatrix::begin(MatrixGrant grant) {
    if (faulted_) return MatrixStatus::FAULTED;
    if (matrix_claimed) {
        faulted_ = true;
        return MatrixStatus::ALREADY_OWNED;
    }
    if (!grant.normal_startup || !grant.exclusive_boot_owner) {
        faulted_ = true;
        return MatrixStatus::INVALID_GRANT;
    }
    if (!contextValid()) {
        faulted_ = true;
        return MatrixStatus::CONTEXT_REJECTED;
    }
    const device* const matrix_device = DEVICE_DT_GET(DT_NODELABEL(counter_matrix));
    if (matrix_device == nullptr || !device_is_ready(matrix_device)) {
        faulted_ = true;
        return MatrixStatus::DEVICE_UNAVAILABLE;
    }
    matrix_claimed = true;
    matrixSetGrayscaleBits(3U);
    const Frame blank{};
    writeFrame(blank);
    matrixBegin();
    initialized_ = true;
    return MatrixStatus::INIT_UNCONFIRMED;
}

MatrixStatus UnoQMatrix::submit(std::uint32_t t_us, const Frame& frame) {
    if (faulted_) return MatrixStatus::FAULTED;
    if (!initialized_) return MatrixStatus::NOT_INITIALIZED;
    if (!contextValid()) {
        faulted_ = true;
        return MatrixStatus::CONTEXT_REJECTED;
    }
    if (!frameValid(frame)) {
        faulted_ = true;
        return MatrixStatus::INVALID_FRAME;
    }
    if (submitted_ &&
        static_cast<std::uint32_t>(t_us - last_submit_us_) < config::UI_FRAME_PERIOD_US) {
        return MatrixStatus::THROTTLED;
    }
    writeFrame(frame);
    last_submit_us_ = t_us;
    submitted_ = true;
    return MatrixStatus::SUBMITTED_UNCONFIRMED;
}
} // namespace ui
#endif

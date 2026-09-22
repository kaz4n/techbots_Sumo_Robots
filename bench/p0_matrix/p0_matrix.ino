// Displays SUMO and submits a fixed counter notification on the internal UART.
// Exercises an inert P0 sketch without blocking Bridge calls or motor writes.
// Packet/adapter tests, target compile and physical receipt are separate evidence.
#include "src/config.h"
#include "src/counter_uart.h"
#include <Arduino_LED_Matrix.h>

static_assert(MOTORS_ALLOWED == 0, "This P0 diagnostic must remain inert");
Arduino_LED_Matrix matrix;
volatile std::uint32_t p0Seconds = 0;
std::uint32_t lastScrollMs = 0;
std::uint32_t lastCounterMs = 0;
std::uint8_t scrollColumn = 0;
std::uint8_t frame[104] = {};
// Four five-row glyphs stored as columns; zeros provide spacing.
constexpr std::uint8_t GLYPHS[] = {
    0x17, 0x15, 0x1d, 0,  // S
    0x1f, 0x10, 0x1f, 0,  // U
    0x1f, 0x02, 0x04, 0x02, 0x1f, 0,  // M
    0x1f, 0x11, 0x1f, 0   // O
};

void drawScroll() {
    for (std::uint8_t row = 0; row < 8; ++row) {
        for (std::uint8_t col = 0; col < 13; ++col) {
            const int glyph = static_cast<int>(scrollColumn) + col - 13;
            const bool lit = row >= 1 && row <= 5 && glyph >= 0 &&
                glyph < static_cast<int>(sizeof(GLYPHS)) &&
                (GLYPHS[glyph] & (1U << (row - 1)));
            frame[row * 13 + col] = lit ? 1 : 0;
        }
    }
    matrix.draw(frame);
    scrollColumn = (scrollColumn + 1) % (sizeof(GLYPHS) + 13);
}

void setup() {
    matrix.begin();
    matrix.setGrayscaleBits(3);
    p0::beginCounterTransport();
    lastCounterMs = lastScrollMs = millis();
}

void loop() {
    p0::serviceCounter(micros());
    const std::uint32_t now = millis();
    if (now - lastScrollMs >= config::P0_SCROLL_MS) {
        lastScrollMs = now;
        drawScroll();
    }
    const std::uint32_t periods = (now - lastCounterMs) / config::P0_COUNTER_MS;
    if (periods != 0) {
        lastCounterMs += periods * config::P0_COUNTER_MS;
        p0Seconds += periods;
        p0::submitCounter(p0Seconds, micros());
    }
}

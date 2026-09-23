// Exercises actual D088 rendering and native submission on the built-in matrix.
// Synthetic display scenes require no sensors, header writes, Bridge or motors.
// Host fixtures and exact target/runtime counter evidence are separate checks.
#include "src/config.h"
#include "src/hal/ui_display.h"
#include "src/hal/ui_matrix_unoq.h"

static_assert(MOTORS_ALLOWED == 0, "This display diagnostic must remain inert");
static_assert(MATCH == 0, "The synthetic display diagnostic is not match firmware");
static_assert(config::UI_BENCH_SCENE_MS > 0U);
// Fixed uint32 layout lets the reviewed read-only capture identify actual progress.
struct UiBenchCounters {
    std::uint32_t magic, version, initialized, submissions, failures, scene;
    std::uint32_t last_status, last_render, last_us, max_call_us;
};
volatile UiBenchCounters uiBench;
ui::UnoQMatrix matrix;
ui::Frame frame;
std::uint32_t lastFrameUs = 0U;
bool firstFrame = true;

ui::DisplaySample scene(std::uint32_t now) {
    ui::DisplaySample sample;
    sample.t_us = now;
    sample.state = core::State::IDLE;
    const auto page = (now / 1000U / config::UI_BENCH_SCENE_MS) % 12U;
    uiBench.scene = page;
    if (page < 6U) sample.mode = static_cast<core::Mode>(page + 1U);
    else if (page == 6U) {
        sample.state = core::State::COUNTDOWN;
        sample.release_us = now; // Synthetic fixed5, never a real START or gate.
    } else if (page == 7U) {
        sample.state = core::State::STOPPED;
    } else {
        sample.service_menu = true;
        sample.service = static_cast<countdown::Service>(page - 7U);
    }
    // Deliberately unavailable: no fake battery or sensor measurement on a bare board.
    sample.faults = ui::IMU_UNAVAILABLE;
    return sample;
}

void setup() {
    uiBench.magic = 0x55494D58U;
    uiBench.version = 1U;
    const auto status = matrix.begin({true, true});
    uiBench.last_status = static_cast<std::uint32_t>(status);
    uiBench.initialized = status == ui::MatrixStatus::INIT_UNCONFIRMED ? 1U : 0U;
}

void loop() {
    const std::uint32_t now = micros();
    if (!firstFrame && now - lastFrameUs < config::UI_FRAME_PERIOD_US) return;
    firstFrame = false;
    lastFrameUs = now;
    uiBench.last_render = static_cast<std::uint32_t>(ui::render(scene(now), frame));
    const auto status = matrix.submit(now, frame);
    uiBench.last_status = static_cast<std::uint32_t>(status);
    if (status == ui::MatrixStatus::SUBMITTED_UNCONFIRMED) ++uiBench.submissions;
    else ++uiBench.failures;
    uiBench.last_us = now;
    const std::uint32_t duration = micros() - now;
    if (duration > uiBench.max_call_us) uiBench.max_call_us = duration;
}

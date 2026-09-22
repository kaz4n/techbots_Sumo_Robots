// Tests the P0 UART adapter against its published transport contract.
// Keeps production source opaque while controlling installed API outcomes.
// Run each named case in a fresh process through test_counter_uart.py.
#include "counter_uart.h"
#include "config.h"
#include <Arduino.h>
#include <zephyr/irq.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

const device p0_test_router_device = {78};

namespace probe {
[[noreturn]] void fail(const char* expression, int line) {
    std::fprintf(stderr, "FAIL line %d: %s\n", line, expression);
    std::exit(1);
}
#define CHECK(expression) \
    do { if (!(expression)) probe::fail(#expression, __LINE__); } while (false)

int init_result = 0;
bool device_ready = true;
int config_result = 0;
int callback_result = 0;
int update_result = 1;
int ready_result = 1;
int complete_result = 1;
int fill_result = 1;
uart_config installed = {115200U, UART_CFG_PARITY_NONE, UART_CFG_STOP_BITS_1,
                         UART_CFG_DATA_BITS_8, UART_CFG_FLOW_CTRL_NONE};
uart_irq_callback_user_data_t callback = nullptr;
void* callback_data = nullptr;
bool tx_enabled = false;
bool rx_disabled = false;
bool error_disabled = false;
bool in_callback = false;
unsigned int mask = 0U;
std::vector<unsigned int> keys;
std::vector<std::uint8_t> emitted;
unsigned init_calls = 0U;
unsigned config_calls = 0U;
unsigned callback_calls = 0U;
unsigned tx_enables = 0U;
unsigned tx_disables = 0U;
unsigned rx_disables = 0U;
unsigned error_disables = 0U;
unsigned updates = 0U;
unsigned readiness_reads = 0U;
unsigned completion_reads = 0U;
unsigned fills = 0U;
unsigned locks = 0U;
unsigned unlocks = 0U;
unsigned checks = 0U;

void checkDevice(const device* dev) { CHECK(dev == &p0_test_router_device); }
void checkLocked(const device* dev) {
    checkDevice(dev);
    CHECK(!keys.empty());
}
void beforeCall() {
    CHECK(keys.empty());
    CHECK(locks == unlocks);
    // Exercise both an unmasked caller and an already masked caller.
    mask = (++checks % 2U == 0U) ? 0xA5U : 0U;
}
void afterCall(unsigned int saved) {
    CHECK(keys.empty());
    CHECK(locks == unlocks);
    CHECK(mask == saved);
}
p0::CounterDiagnostics diagnostics() {
    beforeCall();
    const unsigned int saved = mask;
    const auto result = p0::counterDiagnostics();
    afterCall(saved);
    return result;
}
bool begin() {
    beforeCall();
    const unsigned int saved = mask;
    const bool result = p0::beginCounterTransport();
    afterCall(saved);
    return result;
}
bool submit(std::uint32_t counter, std::uint32_t now) {
    beforeCall();
    const unsigned int saved = mask;
    const bool result = p0::submitCounter(counter, now);
    afterCall(saved);
    return result;
}
void service(std::uint32_t now) {
    beforeCall();
    const unsigned int saved = mask;
    p0::serviceCounter(now);
    afterCall(saved);
}
void irq(bool forced = false) {
    CHECK(callback != nullptr);
    CHECK(forced || tx_enabled);
    beforeCall();
    const unsigned int saved = mask;
    const unsigned old_fills = fills;
    const unsigned old_updates = updates;
    const unsigned old_ready = readiness_reads;
    const unsigned old_complete = completion_reads;
    in_callback = true;
    callback(&p0_test_router_device, callback_data);
    in_callback = false;
    afterCall(saved);
    CHECK(fills - old_fills <= 1U);
    CHECK(updates - old_updates <= 1U);
    CHECK(readiness_reads - old_ready <= 1U);
    CHECK(completion_reads - old_complete <= 1U);
}
void stats(std::uint32_t submitted, std::uint32_t completed,
           std::uint32_t refused, bool ready, bool faulted) {
    const auto value = diagnostics();
    CHECK(value.submitted == submitted);
    CHECK(value.completed == completed);
    CHECK(value.refused == refused);
    CHECK(value.ready == ready);
    CHECK(value.faulted == faulted);
}
std::vector<std::uint8_t> expected(std::uint32_t counter) {
    std::array<char, 11U> digits{};
    CHECK(std::snprintf(digits.data(), digits.size(), "%010u",
                        static_cast<unsigned>(counter)) == 10);
    std::vector<std::uint8_t> value = {0x93U, 0x02U, 0xA9U};
    const std::string method = "mon/write";
    value.insert(value.end(), method.begin(), method.end());
    value.push_back(0x91U);
    value.push_back(0xB6U);
    const std::string message = std::string("P0 counter=") + digits.data() + "\n";
    value.insert(value.end(), message.begin(), message.end());
    CHECK(value.size() == 36U);
    return value;
}
void setupSuccess() {
    stats(0U, 0U, 0U, false, false);
    CHECK(begin());
    CHECK(init_calls == 1U);
    CHECK(config_calls == 1U);
    CHECK(callback_calls == 1U);
    CHECK(callback != nullptr);
    CHECK(!tx_enabled);
    CHECK(rx_disabled && error_disabled);
    CHECK(rx_disables == 1U && error_disables == 1U);
    CHECK(emitted.empty());
    stats(0U, 0U, 0U, true, false);
}
void repeatedBeginUnchanged() {
    const auto old = diagnostics();
    const auto calls = std::array<unsigned, 7U>{init_calls, config_calls,
        callback_calls, tx_enables, tx_disables, rx_disables, error_disables};
    CHECK(!begin());
    stats(old.submitted, old.completed, old.refused, old.ready, old.faulted);
    CHECK((calls == std::array<unsigned, 7U>{init_calls, config_calls,
        callback_calls, tx_enables, tx_disables, rx_disables, error_disables}));
}
void permanentFault(std::uint32_t submitted, std::uint32_t completed,
                    std::uint32_t refused) {
    CHECK(!tx_enabled);
    stats(submitted, completed, refused, false, true);
    const auto old_bytes = emitted;
    const unsigned old_fills = fills;
    const unsigned old_enables = tx_enables;
    repeatedBeginUnchanged();
    CHECK(!submit(123U, 0U));
    CHECK(!submit(456U, 999999U));
    service(0U);
    service(UINT32_MAX);
    if (callback != nullptr) { irq(true); irq(true); }
    CHECK(!tx_enabled);
    CHECK(emitted == old_bytes);
    CHECK(fills == old_fills);
    CHECK(tx_enables == old_enables);
    stats(submitted, completed, refused + 2U, false, true);
}
void bytes(unsigned count) {
    for (unsigned i = 0; i < count; ++i) {
        const auto old = diagnostics();
        const auto old_size = emitted.size();
        const auto old_fills = fills;
        const auto old_updates = updates;
        irq();
        CHECK(emitted.size() == old_size + 1U);
        CHECK(fills == old_fills + 1U);
        CHECK(updates == old_updates + 1U);
        CHECK(tx_enabled);
        stats(old.submitted, old.completed, old.refused, true, false);
    }
}
void finalCompletion(std::uint32_t submitted, std::uint32_t completed,
                     std::uint32_t refused) {
    const unsigned old_fills = fills;
    const unsigned old_updates = updates;
    const unsigned old_completion = completion_reads;
    irq();
    CHECK(fills == old_fills);
    CHECK(updates == old_updates + 1U);
    CHECK(completion_reads == old_completion + 1U);
    CHECK(!tx_enabled);
    stats(submitted, completed, refused, true, false);
}
void caseSetupSuccess() {
    setupSuccess();
    repeatedBeginUnchanged();
    service(100000U);
    service(UINT32_MAX);
    stats(0U, 0U, 0U, true, false);
}
void caseSetupFailure(const std::string& name) {
    if (name == "setup_init_negative") init_result = -5;
    else if (name == "setup_init_positive") init_result = 1;
    else if (name == "setup_nonready") device_ready = false;
    else if (name == "setup_config_failure") config_result = -38;
    else if (name == "setup_baud") installed.baudrate = 9600U;
    else if (name == "setup_parity") installed.parity = UART_CFG_PARITY_EVEN;
    else if (name == "setup_stop") installed.stop_bits = UART_CFG_STOP_BITS_2;
    else if (name == "setup_data") installed.data_bits = UART_CFG_DATA_BITS_7;
    else if (name == "setup_flow") installed.flow_ctrl = UART_CFG_FLOW_CTRL_RTS_CTS;
    else if (name == "setup_callback_negative") callback_result = -16;
    else if (name == "setup_callback_positive") callback_result = 1;
    else CHECK(false);
    CHECK(!begin());
    CHECK(init_calls == 1U);
    CHECK(emitted.empty());
    permanentFault(0U, 0U, 0U);
}
void casePackets() {
    setupSuccess();
    const std::array<std::uint32_t, 12U> counters = {
        0U, 1U, 9U, 10U, 99U, 100U, 999U, 1000U, 999999999U,
        1000000000U, 4294967294U, UINT32_MAX};
    std::uint32_t sent = 0U;
    for (const auto counter : counters) {
        emitted.clear();
        CHECK(submit(counter, sent * 100000U));
        ++sent;
        CHECK(tx_enabled);
        stats(sent, sent - 1U, 0U, true, false);
        bytes(36U);
        CHECK(emitted == expected(counter));
        stats(sent, sent - 1U, 0U, true, false);
        finalCompletion(sent, sent, 0U);
    }
}
void caseBusyRetention() {
    setupSuccess();
    CHECK(submit(1234567890U, 70U));
    CHECK(!submit(0U, 80U));
    stats(1U, 0U, 1U, true, false);
    bytes(13U);
    repeatedBeginUnchanged();
    CHECK(!submit(UINT32_MAX, 50070U));
    stats(1U, 0U, 2U, true, false);
    service(100069U);
    bytes(23U);
    CHECK(emitted == expected(1234567890U));
    CHECK(!submit(123U, 100069U));
    stats(1U, 0U, 3U, true, false);
    finalCompletion(1U, 1U, 3U);
    CHECK(submit(42U, 100070U));
    stats(2U, 1U, 3U, true, false);
}
void caseTimeout(const std::string& name) {
    setupSuccess();
    const bool wrap = name == "timeout_wrap";
    const std::uint32_t anchor = wrap ? UINT32_MAX - 50000U : 1234U;
    CHECK(submit(1U, anchor));
    if (name == "timeout_partial" || wrap) bytes(12U);
    if (name == "timeout_final_tc") bytes(36U);
    service(anchor + 99999U);
    stats(1U, 0U, 0U, true, false);
    CHECK(tx_enabled);
    CHECK(!submit(2U, anchor + 99999U));
    service(anchor + (name == "timeout_after" ? 100001U : 100000U));
    permanentFault(1U, 0U, 1U);
}
void caseDriverFailure(const std::string& name) {
    setupSuccess();
    CHECK(submit(17U, 100U));
    const bool final = name.find("_final") != std::string::npos;
    if (final) bytes(36U);
    else bytes(7U);
    if (name.find("update_zero") == 0U) update_result = 0;
    else if (name.find("update_negative") == 0U) update_result = -38;
    else if (name.find("update_positive") == 0U) update_result = 2;
    else if (name.find("ready_zero") == 0U) ready_result = 0;
    else if (name.find("ready_negative") == 0U) ready_result = -38;
    else if (name.find("ready_positive") == 0U) ready_result = 3;
    else if (name == "fill_zero") fill_result = 0;
    else if (name == "fill_negative") fill_result = -5;
    else if (name == "fill_oversized") fill_result = 2;
    else if (name == "complete_zero_final") complete_result = 0;
    else if (name == "complete_negative_final") complete_result = -38;
    else if (name == "complete_positive_final") complete_result = 4;
    else CHECK(false);
    const auto old_bytes = emitted;
    irq();
    CHECK(emitted == old_bytes);
    update_result = ready_result = complete_result = fill_result = 1;
    permanentFault(1U, 0U, 0U);
}
void caseIdleIrq(bool after_completion) {
    setupSuccess();
    if (after_completion) {
        CHECK(submit(0U, 0U));
        bytes(36U);
        finalCompletion(1U, 1U, 0U);
    }
    const auto old_bytes = emitted;
    const unsigned old_fills = fills;
    const unsigned old_updates = updates;
    const unsigned count = after_completion ? 1U : 0U;
    irq(true);
    CHECK(!tx_enabled);
    CHECK(emitted == old_bytes && fills == old_fills);
    CHECK(updates == old_updates);
    stats(count, count, 0U, true, false);
    CHECK(submit(42U, 100U));
    bytes(36U);
    finalCompletion(count + 1U, count + 1U, 0U);
}
} // namespace probe

unsigned int irq_lock() {
    const auto old = probe::mask;
    probe::keys.push_back(old);
    probe::mask = 0x10U;
    ++probe::locks;
    return old;
}
void irq_unlock(unsigned int key) {
    CHECK(!probe::keys.empty());
    CHECK(probe::keys.back() == key);
    probe::keys.pop_back();
    probe::mask = key;
    ++probe::unlocks;
}
namespace zephyr { namespace arduino {
int init_dev_apply_pinctrl(const device* dev) {
    probe::checkDevice(dev);
    CHECK(probe::keys.empty());
    CHECK(!probe::in_callback);
    CHECK(++probe::init_calls == 1U);
    return probe::init_result;
}
} }
bool device_is_ready(const device* dev) {
    probe::checkDevice(dev);
    return probe::device_ready;
}
int uart_config_get(const device* dev, uart_config* cfg) {
    probe::checkDevice(dev);
    CHECK(cfg != nullptr);
    CHECK(!probe::in_callback);
    ++probe::config_calls;
    *cfg = probe::installed;
    return probe::config_result;
}
int uart_irq_callback_user_data_set(const device* dev,
                                   uart_irq_callback_user_data_t callback,
                                   void* user_data) {
    probe::checkLocked(dev);
    CHECK(!probe::tx_enabled && probe::rx_disabled && probe::error_disabled);
    CHECK(!probe::in_callback);
    CHECK(callback != nullptr);
    ++probe::callback_calls;
    if (probe::callback_result == 0) {
        probe::callback = callback;
        probe::callback_data = user_data;
    }
    return probe::callback_result;
}
void uart_irq_tx_enable(const device* dev) {
    probe::checkLocked(dev);
    CHECK(probe::callback != nullptr);
    CHECK(probe::rx_disabled && probe::error_disabled);
    probe::tx_enabled = true;
    ++probe::tx_enables;
}
void uart_irq_tx_disable(const device* dev) {
    probe::checkLocked(dev);
    probe::tx_enabled = false;
    ++probe::tx_disables;
}
void uart_irq_rx_disable(const device* dev) {
    probe::checkLocked(dev);
    probe::rx_disabled = true;
    ++probe::rx_disables;
}
void uart_irq_err_disable(const device* dev) {
    probe::checkLocked(dev);
    probe::error_disabled = true;
    ++probe::error_disables;
}
int uart_irq_update(const device* dev) {
    probe::checkLocked(dev);
    CHECK(probe::in_callback);
    ++probe::updates;
    return probe::update_result;
}
int uart_irq_tx_ready(const device* dev) {
    probe::checkLocked(dev);
    CHECK(probe::in_callback);
    ++probe::readiness_reads;
    return probe::ready_result;
}
int uart_irq_tx_complete(const device* dev) {
    probe::checkLocked(dev);
    CHECK(probe::in_callback);
    ++probe::completion_reads;
    return probe::complete_result;
}
int uart_fifo_fill(const device* dev, const std::uint8_t* bytes, int size) {
    probe::checkLocked(dev);
    CHECK(probe::in_callback && probe::tx_enabled);
    CHECK(bytes != nullptr && size == 1);
    ++probe::fills;
    if (probe::fill_result == 1) probe::emitted.push_back(*bytes);
    return probe::fill_result;
}
void uart_irq_rx_enable(const device*) { CHECK(false); }
void uart_irq_err_enable(const device*) { CHECK(false); }
int uart_fifo_read(const device*, std::uint8_t*, int) { CHECK(false); return -1; }
int uart_configure(const device*, const uart_config*) { CHECK(false); return -1; }

int main(int argc, char** argv) {
    static_assert(MOTORS_ALLOWED == 0, "tests must remain inert");
    CHECK(config::P0_MONITOR_TIMEOUT_US == 100000U);
    CHECK(argc == 2);
    const std::string name = argv[1];
    if (name == "setup_success") probe::caseSetupSuccess();
    else if (name.find("setup_") == 0U) probe::caseSetupFailure(name);
    else if (name == "packets") probe::casePackets();
    else if (name == "busy_retention") probe::caseBusyRetention();
    else if (name.find("timeout_") == 0U) probe::caseTimeout(name);
    else if (name == "idle_irq") probe::caseIdleIrq(false);
    else if (name == "completed_idle_irq") probe::caseIdleIrq(true);
    else probe::caseDriverFailure(name);
    CHECK(probe::keys.empty());
    CHECK(probe::locks == probe::unlocks);
    std::printf("PASS %s\n", name.c_str());
    return 0;
}

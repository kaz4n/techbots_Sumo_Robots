// Sends the fixed P0 counter through the installed internal router UART.
// Owns TX alone and bounds runtime work without Bridge, receives or wait loops.
// Tested with API substitutes; target binary and physical evidence are separate.
#include "config.h"
#include "counter_packet.h"
#include "counter_uart.h"
#include <Arduino.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/irq.h>

static_assert(MOTORS_ALLOWED == 0, "P0 counter transport must remain inert");

namespace p0 {
namespace {
const device* const uart = DEVICE_DT_GET(ARDUINO_ROUTER_PHANDLE);
CounterPacket packet(config::P0_MONITOR_TIMEOUT_US);
CounterDiagnostics diagnostics;
bool attempted = false;

void increment(std::uint32_t& count) {
    if (count != UINT32_MAX) {
        ++count;
    }
}

// Caller holds irq_lock: this also contains the installed CR1 exclusive retries.
void faultLocked() {
    packet.fail();
    diagnostics.ready = false;
    diagnostics.faulted = true;
    uart_irq_tx_disable(uart);
}

void onTransmit(const device* source, void*) {
    const unsigned int key = irq_lock();
    if (!diagnostics.ready || packet.status() != PacketStatus::BUSY) {
        uart_irq_tx_disable(uart);
    } else if (source != uart || uart_irq_update(uart) != 1 ||
               uart_irq_tx_ready(uart) != 1) {
        faultLocked();
    } else {
        std::uint8_t byte = 0;
        if (packet.nextByte(byte)) {
            packet.accepted(uart_fifo_fill(uart, &byte, 1));
            if (packet.status() == PacketStatus::FAULT) {
                faultLocked();
            }
        } else if (uart_irq_tx_complete(uart) == 1 && packet.complete()) {
            increment(diagnostics.completed);
            uart_irq_tx_disable(uart);
        } else {
            faultLocked();
        }
    }
    irq_unlock(key);
}

bool expectedConfig(const uart_config& value) {
    return value.baudrate == config::P0_MONITOR_BAUD_BPS &&
           value.parity == UART_CFG_PARITY_NONE &&
           value.stop_bits == UART_CFG_STOP_BITS_1 &&
           value.data_bits == UART_CFG_DATA_BITS_8 &&
           value.flow_ctrl == UART_CFG_FLOW_CTRL_NONE;
}
} // namespace

bool beginCounterTransport() {
    if (attempted) {
        return false;
    }
    attempted = true;
    uart_config value{};
    // Deferred initialization can wait on MCU hardware; it is setup-only.
    if (zephyr::arduino::init_dev_apply_pinctrl(uart) != 0 ||
        !device_is_ready(uart) || uart_config_get(uart, &value) != 0 ||
        !expectedConfig(value)) {
        packet.fail();
        diagnostics.faulted = true;
        return false;
    }
    const unsigned int key = irq_lock();
    uart_irq_tx_disable(uart);
    uart_irq_rx_disable(uart);
    uart_irq_err_disable(uart);
    if (uart_irq_callback_user_data_set(uart, onTransmit, nullptr) == 0) {
        diagnostics.ready = true;
    } else {
        faultLocked();
    }
    irq_unlock(key);
    return diagnostics.ready;
}

bool submitCounter(std::uint32_t counter, std::uint32_t now_us) {
    const unsigned int key = irq_lock();
    const bool accepted = diagnostics.ready && packet.submit(counter, now_us);
    if (accepted) {
        increment(diagnostics.submitted);
        uart_irq_tx_enable(uart);
    } else {
        increment(diagnostics.refused);
    }
    irq_unlock(key);
    return accepted;
}

void serviceCounter(std::uint32_t now_us) {
    const unsigned int key = irq_lock();
    if (diagnostics.ready) {
        packet.service(now_us);
        if (packet.status() == PacketStatus::FAULT) {
            faultLocked();
        }
    }
    irq_unlock(key);
}

CounterDiagnostics counterDiagnostics() {
    const unsigned int key = irq_lock();
    const CounterDiagnostics copy = diagnostics;
    irq_unlock(key);
    return copy;
}
} // namespace p0

// Declares the controlled UART surface for the independent P0 adapter tests.
// Makes every operation observable without substituting adapter implementation.
// Compiled by test_counter_uart.py with the real opaque production sources.
#pragma once
#include <cstdint>

struct device { int identity; };
extern const device p0_test_router_device;
#define ARDUINO_ROUTER_PHANDLE p0_test_router
#define P0_TEST_DEVICE_DT_GET(node) (&node##_device)
#define DEVICE_DT_GET(node) P0_TEST_DEVICE_DT_GET(node)

enum uart_config_parity { UART_CFG_PARITY_NONE, UART_CFG_PARITY_ODD,
                          UART_CFG_PARITY_EVEN };
enum uart_config_stop_bits { UART_CFG_STOP_BITS_1, UART_CFG_STOP_BITS_2 };
enum uart_config_data_bits { UART_CFG_DATA_BITS_7, UART_CFG_DATA_BITS_8,
                             UART_CFG_DATA_BITS_9 };
enum uart_config_flow_control { UART_CFG_FLOW_CTRL_NONE,
                               UART_CFG_FLOW_CTRL_RTS_CTS };
struct uart_config {
    std::uint32_t baudrate;
    uart_config_parity parity;
    uart_config_stop_bits stop_bits;
    uart_config_data_bits data_bits;
    uart_config_flow_control flow_ctrl;
};
using uart_irq_callback_user_data_t = void (*)(const device*, void*);

bool device_is_ready(const device* dev);
int uart_config_get(const device* dev, uart_config* cfg);
int uart_irq_callback_user_data_set(const device* dev,
                                   uart_irq_callback_user_data_t callback,
                                   void* user_data);
void uart_irq_tx_enable(const device* dev);
void uart_irq_tx_disable(const device* dev);
void uart_irq_rx_disable(const device* dev);
void uart_irq_err_disable(const device* dev);
int uart_irq_update(const device* dev);
int uart_irq_tx_ready(const device* dev);
int uart_irq_tx_complete(const device* dev);
int uart_fifo_fill(const device* dev, const std::uint8_t* bytes, int size);

// Forbidden receive/reconfiguration paths fail immediately if introduced.
void uart_irq_rx_enable(const device* dev);
void uart_irq_err_enable(const device* dev);
int uart_fifo_read(const device* dev, std::uint8_t* bytes, int size);
int uart_configure(const device* dev, const uart_config* cfg);

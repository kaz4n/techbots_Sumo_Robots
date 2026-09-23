// Mirrors fields from the retained installed uart_stm32.h and offline config dump.
// Exposes metadata only; no stock transmit, receive or interrupt-loop API exists.
// The independent native harness mutates each field at controlled boundaries.
#pragma once
#include <cstddef>
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/drivers/clock_control/stm32_clock_control.h>
#include <stm32_ll_usart.h>
struct reset_dt_spec { const device* dev; std::uint32_t id; };
struct pinctrl_dev_config { unsigned state_cnt; };
using uart_irq_config_func_t = void (*)(const device*);
using uart_irq_callback_user_data_t = void (*)(const device*, void*);
struct uart_config { std::uint32_t baudrate; std::uint8_t parity, stop_bits, data_bits, flow_ctrl; };
inline constexpr unsigned UART_CFG_PARITY_NONE = 0U;
inline constexpr unsigned UART_CFG_STOP_BITS_1 = 1U;
inline constexpr unsigned UART_CFG_DATA_BITS_8 = 3U;
inline constexpr unsigned UART_CFG_FLOW_CTRL_NONE = 0U;
struct uart_stm32_config {
    USART_TypeDef* usart; const device* clock; reset_dt_spec reset;
    const stm32_pclken* pclken; std::size_t pclk_len;
    bool single_wire, tx_rx_swap, rx_invert, tx_invert, de_enable;
    std::uint8_t de_assert_time, de_deassert_time;
    bool de_invert, fifo_enable;
    const pinctrl_dev_config* pcfg;
    uart_irq_config_func_t irq_config_func;
};
struct uart_stm32_data { uart_config* uart_cfg; uart_irq_callback_user_data_t user_cb; void* user_data; };

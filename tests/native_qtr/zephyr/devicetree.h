// Reproduces saved source-verified GPIO device-tree binding macros.
// Address and index variants test rejection without remapping arbitrary devices.
// These are host-controlled declarations, never claims about live MCU state.
#pragma once
#include <cstdint>
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define DT_NODELABEL(n) n
#define DT_REG_ADDR(n) DT_REG_IMPL(n)
#define DT_REG_IMPL(n) FIX_REG_##n
#ifndef NATIVE_GPIOA_ADDRESS
#define NATIVE_GPIOA_ADDRESS 0x42020000UL
#endif
#define FIX_REG_gpioa NATIVE_GPIOA_ADDRESS
#define FIX_REG_gpiob 0x42020400UL
#define DEVICE_DT_GET(n) DEVICE_DT_IMPL(n)
#define DEVICE_DT_IMPL(n) FIX_DEVICE_##n
#define FIX_DEVICE_gpioa (&fixture_devices[0])
#define FIX_DEVICE_gpiob (&fixture_devices[1])

#define FIX_DEVICE_gpioc (&fixture_devices[2])

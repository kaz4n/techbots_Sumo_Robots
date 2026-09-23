// Maps the installed UNO Q GPIO/PWM metadata into controllable native fixtures.
// Malformed variants test validation before any native configuration or write.
// Expectations use the installed source report, never the backend implementation.
#pragma once
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/pwm.h>
#ifndef NATIVE_BAD_MAP
#define NATIVE_BAD_MAP 0
#endif
#ifndef NATIVE_BAD_SLOT
#define NATIVE_BAD_SLOT 0
#endif
#ifndef NATIVE_TABLE_SIZE
#define NATIVE_TABLE_SIZE 70
#endif
extern gpio_driver_config fixture_gpio_configs[4];
extern const device fixture_gpio_ports[4];
extern const device fixture_pwm_devices[7];
constexpr unsigned selected_pins[5] = {3,5,6,9,10};
constexpr unsigned selected_pwm_indices[4] = {1,2,3,6};
constexpr gpio_dt_spec gpioBase(unsigned index) {
    switch(index) {
    case 2: return {&fixture_gpio_ports[1],3,0};
    case 3: return {&fixture_gpio_ports[1],0,0};
    case 4: return {&fixture_gpio_ports[1],5,0};
    case 5: return {&fixture_gpio_ports[0],11,0};
    case 6: return {&fixture_gpio_ports[1],1,0};
    case 7: return {&fixture_gpio_ports[1],2,0};
    case 8: return {&fixture_gpio_ports[1],4,0};
    case 9: return {&fixture_gpio_ports[1],8,0};
    case 10: return {&fixture_gpio_ports[1],9,0};
    case 11: return {&fixture_gpio_ports[1],15,0};
    case 12: return {&fixture_gpio_ports[1],14,0};
    case 13: return {&fixture_gpio_ports[1],13,0};
    case 16: return {&fixture_gpio_ports[0],6,0};
    case 17: return {&fixture_gpio_ports[0],7,0};
    case 18: return {&fixture_gpio_ports[2],1,0};
    case 19: return {&fixture_gpio_ports[2],0,0};
    case 20: return {&fixture_gpio_ports[1],11,0};
    case 21: return {&fixture_gpio_ports[1],10,0};
    case 50: return {&fixture_gpio_ports[3],10,0};
    case 51: return {&fixture_gpio_ports[3],11,0};
    case 52: return {&fixture_gpio_ports[3],12,0};
    default: return {nullptr,0,0};
    }
}
constexpr gpio_dt_spec gpioSpec(unsigned index) {
    auto s=gpioBase(index);
    if (NATIVE_BAD_MAP==11 && index==11) return gpioBase(selected_pins[NATIVE_BAD_SLOT]);
    if (NATIVE_BAD_MAP==12 && index==2) return gpioBase(selected_pins[NATIVE_BAD_SLOT]);
    if (index!=selected_pins[NATIVE_BAD_SLOT]) return s;
    if (NATIVE_BAD_MAP==1) s.port=nullptr;
    if (NATIVE_BAD_MAP==2) s.pin=32;
    if (NATIVE_BAD_MAP==3) s.dt_flags=1;
    if (NATIVE_BAD_MAP==4) s=gpioBase(selected_pins[(NATIVE_BAD_SLOT+1)%5]);
    if (NATIVE_BAD_MAP==5) s.pin=12;
    return s;
}
constexpr unsigned pwm_pins[16]={2,3,5,6,7,8,9,10,11,12,13,20,21,50,51,52};
constexpr gpio_dt_spec pwmPad(unsigned index) {
    if (NATIVE_BAD_MAP==6 && index==15) return gpioBase(selected_pins[NATIVE_BAD_SLOT]);
    return gpioBase(pwm_pins[index]);
}
constexpr pwm_dt_spec pwmSpec(unsigned index) {
    constexpr unsigned devices[16]={3,1,0,1,4,1,2,2,0,0,0,3,3,5,5,5};
    constexpr unsigned channels[16]={2,3,4,4,4,1,3,4,3,2,1,4,3,1,2,3};
    constexpr unsigned flags[16]={0,0,0,0,256,0,0,0,256,256,256,0,0,1,1,1};
    pwm_dt_spec s={&fixture_pwm_devices[devices[index]],channels[index],2000000,static_cast<pwm_flags_t>(flags[index])};
    if (NATIVE_BAD_SLOT<4 && index==selected_pwm_indices[NATIVE_BAD_SLOT]) {
        if (NATIVE_BAD_MAP==7) s.dev=nullptr;
        if (NATIVE_BAD_MAP==8) s.dev=&fixture_pwm_devices[3];
        if (NATIVE_BAD_MAP==9) s.channel=2;
        if (NATIVE_BAD_MAP==10) s.flags=1;
    }
    return s;
}

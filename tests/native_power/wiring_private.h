// Supplies public Arduino pad metadata with independent malformed-map variants.
// A0 is PA4; aliases against each existing proposal must fail admission.
// All mappings come from the installed source audits, not the implementation.
#pragma once
#include <zephyr/drivers/gpio.h>
#ifndef NATIVE_TABLE_SIZE
#define NATIVE_TABLE_SIZE 70
#endif
#ifndef NATIVE_BAD_MAP
#define NATIVE_BAD_MAP 0
#endif
#ifndef NATIVE_ALIAS_INDEX
#define NATIVE_ALIAS_INDEX 2
#endif
extern device fixture_other_ports[2];
constexpr gpio_dt_spec fixturePad(unsigned index) {
    if (NATIVE_BAD_MAP==5 && index==NATIVE_ALIAS_INDEX) return {&fixture_devices[1],4,0};
    if(index==14) {
        if(NATIVE_BAD_MAP==1)return {nullptr,4,0};
        if(NATIVE_BAD_MAP==2)return {&fixture_devices[1],32,0};
        if(NATIVE_BAD_MAP==3)return {&fixture_devices[1],4,1};
        if(NATIVE_BAD_MAP==4)return {&fixture_other_ports[0],4,0};
        return {&fixture_devices[1],4,0};
    }
    switch(index) {
    case 2:return {&fixture_other_ports[0],3,0};
    case 3:return {&fixture_other_ports[0],0,0};
    case 4:return {&fixture_other_ports[0],5,0};
    case 5:return {&fixture_devices[1],11,0};
    case 6:return {&fixture_other_ports[0],1,0};
    case 7:return {&fixture_other_ports[0],2,0};
    case 8:return {&fixture_other_ports[0],4,0};
    case 9:return {&fixture_other_ports[0],8,0};
    case 10:return {&fixture_other_ports[0],9,0};
    case 11:return {&fixture_other_ports[0],15,0};
    case 12:return {&fixture_other_ports[0],14,0};
    case 13:return {&fixture_other_ports[0],13,0};
    case 16:return {&fixture_devices[1],6,0};
    case 17:return {&fixture_devices[1],7,0};
    case 18:return {&fixture_other_ports[1],1,0};
    case 19:return {&fixture_other_ports[1],0,0};
    default:return {nullptr,0,0};
    }
}
namespace zephyr { namespace arduino {
constexpr gpio_dt_spec arduino_pins[] = {
#if NATIVE_TABLE_SIZE > 0
fixturePad(0),
#endif
#if NATIVE_TABLE_SIZE > 1
fixturePad(1),
#endif
#if NATIVE_TABLE_SIZE > 2
fixturePad(2),
#endif
#if NATIVE_TABLE_SIZE > 3
fixturePad(3),
#endif
#if NATIVE_TABLE_SIZE > 4
fixturePad(4),
#endif
#if NATIVE_TABLE_SIZE > 5
fixturePad(5),
#endif
#if NATIVE_TABLE_SIZE > 6
fixturePad(6),
#endif
#if NATIVE_TABLE_SIZE > 7
fixturePad(7),
#endif
#if NATIVE_TABLE_SIZE > 8
fixturePad(8),
#endif
#if NATIVE_TABLE_SIZE > 9
fixturePad(9),
#endif
#if NATIVE_TABLE_SIZE > 10
fixturePad(10),
#endif
#if NATIVE_TABLE_SIZE > 11
fixturePad(11),
#endif
#if NATIVE_TABLE_SIZE > 12
fixturePad(12),
#endif
#if NATIVE_TABLE_SIZE > 13
fixturePad(13),
#endif
#if NATIVE_TABLE_SIZE > 14
fixturePad(14),
#endif
#if NATIVE_TABLE_SIZE > 15
fixturePad(15),
#endif
#if NATIVE_TABLE_SIZE > 16
fixturePad(16),
#endif
#if NATIVE_TABLE_SIZE > 17
fixturePad(17),
#endif
#if NATIVE_TABLE_SIZE > 18
fixturePad(18),
#endif
#if NATIVE_TABLE_SIZE > 19
fixturePad(19),
#endif
#if NATIVE_TABLE_SIZE > 20
fixturePad(20),
#endif
#if NATIVE_TABLE_SIZE > 21
fixturePad(21),
#endif
#if NATIVE_TABLE_SIZE > 22
fixturePad(22),
#endif
#if NATIVE_TABLE_SIZE > 23
fixturePad(23),
#endif
#if NATIVE_TABLE_SIZE > 24
fixturePad(24),
#endif
#if NATIVE_TABLE_SIZE > 25
fixturePad(25),
#endif
#if NATIVE_TABLE_SIZE > 26
fixturePad(26),
#endif
#if NATIVE_TABLE_SIZE > 27
fixturePad(27),
#endif
#if NATIVE_TABLE_SIZE > 28
fixturePad(28),
#endif
#if NATIVE_TABLE_SIZE > 29
fixturePad(29),
#endif
#if NATIVE_TABLE_SIZE > 30
fixturePad(30),
#endif
#if NATIVE_TABLE_SIZE > 31
fixturePad(31),
#endif
#if NATIVE_TABLE_SIZE > 32
fixturePad(32),
#endif
#if NATIVE_TABLE_SIZE > 33
fixturePad(33),
#endif
#if NATIVE_TABLE_SIZE > 34
fixturePad(34),
#endif
#if NATIVE_TABLE_SIZE > 35
fixturePad(35),
#endif
#if NATIVE_TABLE_SIZE > 36
fixturePad(36),
#endif
#if NATIVE_TABLE_SIZE > 37
fixturePad(37),
#endif
#if NATIVE_TABLE_SIZE > 38
fixturePad(38),
#endif
#if NATIVE_TABLE_SIZE > 39
fixturePad(39),
#endif
#if NATIVE_TABLE_SIZE > 40
fixturePad(40),
#endif
#if NATIVE_TABLE_SIZE > 41
fixturePad(41),
#endif
#if NATIVE_TABLE_SIZE > 42
fixturePad(42),
#endif
#if NATIVE_TABLE_SIZE > 43
fixturePad(43),
#endif
#if NATIVE_TABLE_SIZE > 44
fixturePad(44),
#endif
#if NATIVE_TABLE_SIZE > 45
fixturePad(45),
#endif
#if NATIVE_TABLE_SIZE > 46
fixturePad(46),
#endif
#if NATIVE_TABLE_SIZE > 47
fixturePad(47),
#endif
#if NATIVE_TABLE_SIZE > 48
fixturePad(48),
#endif
#if NATIVE_TABLE_SIZE > 49
fixturePad(49),
#endif
#if NATIVE_TABLE_SIZE > 50
fixturePad(50),
#endif
#if NATIVE_TABLE_SIZE > 51
fixturePad(51),
#endif
#if NATIVE_TABLE_SIZE > 52
fixturePad(52),
#endif
#if NATIVE_TABLE_SIZE > 53
fixturePad(53),
#endif
#if NATIVE_TABLE_SIZE > 54
fixturePad(54),
#endif
#if NATIVE_TABLE_SIZE > 55
fixturePad(55),
#endif
#if NATIVE_TABLE_SIZE > 56
fixturePad(56),
#endif
#if NATIVE_TABLE_SIZE > 57
fixturePad(57),
#endif
#if NATIVE_TABLE_SIZE > 58
fixturePad(58),
#endif
#if NATIVE_TABLE_SIZE > 59
fixturePad(59),
#endif
#if NATIVE_TABLE_SIZE > 60
fixturePad(60),
#endif
#if NATIVE_TABLE_SIZE > 61
fixturePad(61),
#endif
#if NATIVE_TABLE_SIZE > 62
fixturePad(62),
#endif
#if NATIVE_TABLE_SIZE > 63
fixturePad(63),
#endif
#if NATIVE_TABLE_SIZE > 64
fixturePad(64),
#endif
#if NATIVE_TABLE_SIZE > 65
fixturePad(65),
#endif
#if NATIVE_TABLE_SIZE > 66
fixturePad(66),
#endif
#if NATIVE_TABLE_SIZE > 67
fixturePad(67),
#endif
#if NATIVE_TABLE_SIZE > 68
fixturePad(68),
#endif
#if NATIVE_TABLE_SIZE > 69
fixturePad(69),
#endif
}; }}

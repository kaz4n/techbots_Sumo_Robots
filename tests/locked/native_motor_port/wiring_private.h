// Declares installed-shaped Arduino GPIO metadata without production I/O.
// Compile variants exercise selected index bounds and mapping validation.
// The native harness owns every referenced device and permission flag.
#pragma once
#include "mapping.h"
namespace zephyr { namespace arduino {
constexpr gpio_dt_spec arduino_pins[]={
#if NATIVE_TABLE_SIZE > 0
gpioSpec(0),
#endif
#if NATIVE_TABLE_SIZE > 1
gpioSpec(1),
#endif
#if NATIVE_TABLE_SIZE > 2
gpioSpec(2),
#endif
#if NATIVE_TABLE_SIZE > 3
gpioSpec(3),
#endif
#if NATIVE_TABLE_SIZE > 4
gpioSpec(4),
#endif
#if NATIVE_TABLE_SIZE > 5
gpioSpec(5),
#endif
#if NATIVE_TABLE_SIZE > 6
gpioSpec(6),
#endif
#if NATIVE_TABLE_SIZE > 7
gpioSpec(7),
#endif
#if NATIVE_TABLE_SIZE > 8
gpioSpec(8),
#endif
#if NATIVE_TABLE_SIZE > 9
gpioSpec(9),
#endif
#if NATIVE_TABLE_SIZE > 10
gpioSpec(10),
#endif
#if NATIVE_TABLE_SIZE > 11
gpioSpec(11),
#endif
#if NATIVE_TABLE_SIZE > 12
gpioSpec(12),
#endif
#if NATIVE_TABLE_SIZE > 13
gpioSpec(13),
#endif
#if NATIVE_TABLE_SIZE > 14
gpioSpec(14),
#endif
#if NATIVE_TABLE_SIZE > 15
gpioSpec(15),
#endif
#if NATIVE_TABLE_SIZE > 16
gpioSpec(16),
#endif
#if NATIVE_TABLE_SIZE > 17
gpioSpec(17),
#endif
#if NATIVE_TABLE_SIZE > 18
gpioSpec(18),
#endif
#if NATIVE_TABLE_SIZE > 19
gpioSpec(19),
#endif
#if NATIVE_TABLE_SIZE > 20
gpioSpec(20),
#endif
#if NATIVE_TABLE_SIZE > 21
gpioSpec(21),
#endif
#if NATIVE_TABLE_SIZE > 22
gpioSpec(22),
#endif
#if NATIVE_TABLE_SIZE > 23
gpioSpec(23),
#endif
#if NATIVE_TABLE_SIZE > 24
gpioSpec(24),
#endif
#if NATIVE_TABLE_SIZE > 25
gpioSpec(25),
#endif
#if NATIVE_TABLE_SIZE > 26
gpioSpec(26),
#endif
#if NATIVE_TABLE_SIZE > 27
gpioSpec(27),
#endif
#if NATIVE_TABLE_SIZE > 28
gpioSpec(28),
#endif
#if NATIVE_TABLE_SIZE > 29
gpioSpec(29),
#endif
#if NATIVE_TABLE_SIZE > 30
gpioSpec(30),
#endif
#if NATIVE_TABLE_SIZE > 31
gpioSpec(31),
#endif
#if NATIVE_TABLE_SIZE > 32
gpioSpec(32),
#endif
#if NATIVE_TABLE_SIZE > 33
gpioSpec(33),
#endif
#if NATIVE_TABLE_SIZE > 34
gpioSpec(34),
#endif
#if NATIVE_TABLE_SIZE > 35
gpioSpec(35),
#endif
#if NATIVE_TABLE_SIZE > 36
gpioSpec(36),
#endif
#if NATIVE_TABLE_SIZE > 37
gpioSpec(37),
#endif
#if NATIVE_TABLE_SIZE > 38
gpioSpec(38),
#endif
#if NATIVE_TABLE_SIZE > 39
gpioSpec(39),
#endif
#if NATIVE_TABLE_SIZE > 40
gpioSpec(40),
#endif
#if NATIVE_TABLE_SIZE > 41
gpioSpec(41),
#endif
#if NATIVE_TABLE_SIZE > 42
gpioSpec(42),
#endif
#if NATIVE_TABLE_SIZE > 43
gpioSpec(43),
#endif
#if NATIVE_TABLE_SIZE > 44
gpioSpec(44),
#endif
#if NATIVE_TABLE_SIZE > 45
gpioSpec(45),
#endif
#if NATIVE_TABLE_SIZE > 46
gpioSpec(46),
#endif
#if NATIVE_TABLE_SIZE > 47
gpioSpec(47),
#endif
#if NATIVE_TABLE_SIZE > 48
gpioSpec(48),
#endif
#if NATIVE_TABLE_SIZE > 49
gpioSpec(49),
#endif
#if NATIVE_TABLE_SIZE > 50
gpioSpec(50),
#endif
#if NATIVE_TABLE_SIZE > 51
gpioSpec(51),
#endif
#if NATIVE_TABLE_SIZE > 52
gpioSpec(52),
#endif
#if NATIVE_TABLE_SIZE > 53
gpioSpec(53),
#endif
#if NATIVE_TABLE_SIZE > 54
gpioSpec(54),
#endif
#if NATIVE_TABLE_SIZE > 55
gpioSpec(55),
#endif
#if NATIVE_TABLE_SIZE > 56
gpioSpec(56),
#endif
#if NATIVE_TABLE_SIZE > 57
gpioSpec(57),
#endif
#if NATIVE_TABLE_SIZE > 58
gpioSpec(58),
#endif
#if NATIVE_TABLE_SIZE > 59
gpioSpec(59),
#endif
#if NATIVE_TABLE_SIZE > 60
gpioSpec(60),
#endif
#if NATIVE_TABLE_SIZE > 61
gpioSpec(61),
#endif
#if NATIVE_TABLE_SIZE > 62
gpioSpec(62),
#endif
#if NATIVE_TABLE_SIZE > 63
gpioSpec(63),
#endif
#if NATIVE_TABLE_SIZE > 64
gpioSpec(64),
#endif
#if NATIVE_TABLE_SIZE > 65
gpioSpec(65),
#endif
#if NATIVE_TABLE_SIZE > 66
gpioSpec(66),
#endif
#if NATIVE_TABLE_SIZE > 67
gpioSpec(67),
#endif
#if NATIVE_TABLE_SIZE > 68
gpioSpec(68),
#endif
#if NATIVE_TABLE_SIZE > 69
gpioSpec(69),
#endif
};
}}

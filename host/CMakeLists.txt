# Builds the pure C++17 host test scaffold.
# Keeps hardware dependencies out of specification tests.
# Validated by tools/test_host.sh; P0 proves only the scaffold.
cmake_minimum_required(VERSION 3.20)
project(sumox26_host LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
enable_testing()
file(GLOB CORE_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/../src/core/*.cpp")
file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/../tests/*.cpp")
# B8 storage/formatting and D075 MotorGate use host-safe code; pin backends stay out.
add_executable(sumox26_tests ${CORE_SOURCES} ${TEST_SOURCES}
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_frames.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_csv.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/motors.cpp")
target_include_directories(sumox26_tests PRIVATE ../src)
target_include_directories(sumox26_tests SYSTEM PRIVATE third_party)
target_compile_definitions(sumox26_tests PRIVATE DOCTEST_CONFIG_NO_EXCEPTIONS)
if(MSVC)
  target_compile_options(sumox26_tests PRIVATE /W4 /GR-)
else()
  target_compile_options(sumox26_tests PRIVATE -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
endif()
add_test(NAME sumox26_host COMMAND sumox26_tests)

# Host-only active-path test build: never staged, uploaded or used as firmware.
add_executable(motor_gate_enabled_tests ${CORE_SOURCES}
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/motors.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_motor_gate.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/motor_gate_main.cpp")
target_include_directories(motor_gate_enabled_tests PRIVATE ../src)
target_include_directories(motor_gate_enabled_tests SYSTEM PRIVATE third_party)
target_compile_definitions(motor_gate_enabled_tests PRIVATE
  DOCTEST_CONFIG_NO_EXCEPTIONS MOTORS_ALLOWED=1)
if(MSVC)
  target_compile_options(motor_gate_enabled_tests PRIVATE /W4 /GR-)
else()
  target_compile_options(motor_gate_enabled_tests PRIVATE
    -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
endif()
add_test(NAME motor_gate_enabled_host COMMAND motor_gate_enabled_tests)

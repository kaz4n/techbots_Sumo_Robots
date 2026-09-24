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
file(GLOB APP_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/../src/app/*.cpp")
file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/../tests/*.cpp")
# B8 storage/formatting and D075 MotorGate use host-safe code; pin backends stay out.
add_executable(sumox26_tests ${CORE_SOURCES} ${APP_SOURCES} ${TEST_SOURCES}
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_frames.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_csv.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_dump.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/motors.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../bench/motor_stand/src/motor_stand.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../bench/recorder/src/recorder_transport.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../bench/recorder/src/recorder_transport_scenario.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../bench/recorder/src/recorder_transport_io.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu_acquisition.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu_acquisition_async.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu_heading.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu_adapter.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/line_qtr_adapter.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/ui.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/power_inputs.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/ui_display.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/qtr_cal.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/qtr_cal_format.cpp")
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
add_executable(motor_gate_enabled_tests ${CORE_SOURCES} ${APP_SOURCES}
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_app_projection.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_app_runtime.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_app_dump.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_app_service_reset.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_motor_halt.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_app_transaction.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/ui.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/power_inputs.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu_heading.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/imu_adapter.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/ui_display.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/motors.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_motor_gate.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_button_motor_gate.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_qtr_cal_motor_gate.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_recorder_dump.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_tick_timing.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_power_inputs.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_frames.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_csv.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_dump.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/line_qtr_adapter.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/qtr_cal.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/qtr_cal_format.cpp"
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

# D120 has an immutable bench profile in every translation unit. Keep existing
# targets/locked cases at profile0; dedicated .cc cases exercise the real Gate.
get_target_property(B4_HOST_SOURCES motor_gate_enabled_tests SOURCES)
list(FILTER B4_HOST_SOURCES EXCLUDE REGEX "/tests/")
foreach(motors 0 1)
  set(b4_target stand_integration_m${motors}_tests)
  add_executable(${b4_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_stand_integration.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_stand_integration_safety.cc")
  target_include_directories(${b4_target} PRIVATE ../src)
  target_include_directories(${b4_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${b4_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_B4_STAND=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${b4_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${b4_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME stand_integration_m${motors}_host COMMAND ${b4_target})
endforeach()

# D134 copied configs select availability; every target keeps real Gate semantics.
foreach(motors 0 1)
  set(mode_target mode_availability_m${motors}_tests)
  add_executable(${mode_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_mode_availability.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_mode_availability_safety.cc")
  target_include_directories(${mode_target} PRIVATE ../src ../tests)
  target_include_directories(${mode_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${mode_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${mode_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${mode_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME mode_availability_m${motors}_host COMMAND ${mode_target})
endforeach()

# D131 uses copied-source positive duration fixtures; normal targets retain zero.
get_target_property(PUSH_HOST_SOURCES motor_gate_enabled_tests SOURCES)
list(FILTER PUSH_HOST_SOURCES EXCLUDE REGEX "/tests/")
foreach(motors 0 1)
  set(push_target push_through_m${motors}_tests)
  add_executable(${push_target} ${PUSH_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_push_through.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_push_through_safety.cc")
  target_include_directories(${push_target} PRIVATE ../src)
  target_include_directories(${push_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${push_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P4_REACTIVE=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${push_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${push_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME push_through_m${motors}_host COMMAND ${push_target})
endforeach()

# P3 is opt-in in every translation unit; legacy and B4 locked targets stay intact.
foreach(motors 0 1)
  set(p3_target drive_test_m${motors}_tests)
  add_executable(${p3_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_drive_test.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_drive_test_safety.cc")
  target_include_directories(${p3_target} PRIVATE ../src)
  target_include_directories(${p3_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${p3_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P3_DRIVE_TEST=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${p3_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${p3_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME drive_test_m${motors}_host COMMAND ${p3_target})
endforeach()

# D125 one finite turn uses separate profile targets and separate safety oracles.
foreach(motors 0 1)
  set(turn_target turn_integration_m${motors}_tests)
  add_executable(${turn_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_turn_integration.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_turn_integration_safety.cc")
  target_include_directories(${turn_target} PRIVATE ../src)
  target_include_directories(${turn_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${turn_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P3_TURN_TRIAL=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${turn_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${turn_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME turn_integration_m${motors}_host COMMAND ${turn_target})
endforeach()

# D126 stopping-duty preparation cannot replace any established profile oracle.
foreach(motors 0 1)
  set(stop_target stop_trial_m${motors}_tests)
  add_executable(${stop_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_stop_trial.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_stop_trial_safety.cc")
  target_include_directories(${stop_target} PRIVATE ../src)
  target_include_directories(${stop_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${stop_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P3_STOP_TRIAL=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${stop_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${stop_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME stop_trial_m${motors}_host COMMAND ${stop_target})
endforeach()

# D128 reactive profile reuses actual executors with a separate GO-routing oracle.
foreach(motors 0 1)
  set(reactive_target reactive_profile_m${motors}_tests)
  add_executable(${reactive_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_reactive_profile.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_reactive_profile_safety.cc")
  target_include_directories(${reactive_target} PRIVATE ../src)
  target_include_directories(${reactive_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${reactive_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P4_REACTIVE=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${reactive_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${reactive_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME reactive_profile_m${motors}_host COMMAND ${reactive_target})
endforeach()

# D129 conditional acquisition/application evidence keeps accepted profiles unchanged.
foreach(motors 0 1)
  set(timing_target timing_evidence_m${motors}_tests)
  add_executable(${timing_target} ${B4_HOST_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_timing_evidence.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_push_through_timing.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/../tests/locked/test_timing_evidence_safety.cc")
  target_include_directories(${timing_target} PRIVATE ../src)
  target_include_directories(${timing_target} SYSTEM PRIVATE third_party)
  target_compile_definitions(${timing_target} PRIVATE
    DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P4_REACTIVE=1 SUMOX_TIMING_EVIDENCE=1 MOTORS_ALLOWED=${motors})
  if(MSVC)
    target_compile_options(${timing_target} PRIVATE /W4 /GR-)
  else()
    target_compile_options(${timing_target} PRIVATE
      -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
  endif()
  add_test(NAME timing_evidence_m${motors}_host COMMAND ${timing_target})
endforeach()

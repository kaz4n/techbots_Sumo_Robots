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
# D-068 admits this I/O-free B8 owner only; hardware HAL stays outside host tests.
add_executable(sumox26_tests ${CORE_SOURCES} ${TEST_SOURCES}
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder_frames.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../src/hal/recorder.cpp")
target_include_directories(sumox26_tests PRIVATE ../src)
target_include_directories(sumox26_tests SYSTEM PRIVATE third_party)
target_compile_definitions(sumox26_tests PRIVATE DOCTEST_CONFIG_NO_EXCEPTIONS)
if(MSVC)
  target_compile_options(sumox26_tests PRIVATE /W4 /GR-)
else()
  target_compile_options(sumox26_tests PRIVATE -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)
endif()
add_test(NAME sumox26_host COMMAND sumox26_tests)

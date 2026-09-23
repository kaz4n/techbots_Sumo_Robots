// Exercises B1 electrical snapshots and B5 polarity through public contracts.
// Test authors do not read the native implementation or replace its algorithm.
// Strict UBSan builds link this harness to the same production HAL and core.
#include <cassert>
#include <cerrno>
#include <climits>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include "mapping.h"
#include "config.h"
#include "hal/opp_sensors.h"
#include "core/opp_fusion.h"
#ifdef OPP_PROBE
#include "opponent_probe.h"
void setup();
void loop();
#endif

gpio_driver_config fixture_configs[3] = {{0xffffffffU}, {0xffffffffU}, {0xffffffffU}};
extern const device fixture_ports[3] = {
    {&fixture_configs[0]}, {&fixture_configs[1]}, {&fixture_configs[2]}
};

namespace {
bool allocation_guard = false;
unsigned allocation_calls = 0;
unsigned ready_calls = 0, configure_calls = 0, read_calls = 0, clock_calls = 0;
unsigned configured_slots = 0, read_slots = 0;
unsigned ready_mask = 127;
int configure_status[7] = {}, read_status[7] = {};
std::uint32_t clock_values[2] = {100, 107};
bool reading = false;
opp_sensors::Sensors global_sensors;

void resetCalls() {
    ready_calls = configure_calls = read_calls = clock_calls = 0;
    configured_slots = read_slots = 0;
    reading = false;
}

unsigned slotFor(const device* port, gpio_pin_t pin) {
    for (unsigned slot = 0; slot < 7; ++slot) {
        const auto expected = fixtureSpec(fixture_indices[slot]);
        if (expected.port == port && expected.pin == pin) return slot;
    }
    assert(false && "Native operation used an unowned pad");
    return 7;
}

void noCalls() {
    assert(ready_calls == 0 && configure_calls == 0);
    assert(read_calls == 0 && clock_calls == 0);
}

void checkDenied(const opp_sensors::Sensors& sensors) {
    resetCalls();
    const auto sample = sensors.read();
    assert(!sample.valid && sample.raw_mask == 0 && sample.valid_mask == 0);
    assert(sample.started_us == 0 && sample.completed_us == 0);
    for (const auto status : sample.status) assert(status == -EACCES);
    noCalls();
}

void checkInit(opp_sensors::Sensors& sensors) {
    resetCalls();
    const auto result = sensors.begin();
    unsigned mask = 0, attempted = 0;
    for (unsigned slot = 0; slot < 7; ++slot) {
        const bool ready = (ready_mask & (1U << slot)) != 0;
        const auto expected = ready ? configure_status[slot] : -ENODEV;
        assert(result.status[slot] == expected);
        if (ready) attempted |= 1U << slot;
        if (expected == 0) mask |= 1U << slot;
    }
    assert(result.configured_mask == mask && result.ready == (mask == 127));
    assert(ready_calls == 7 && configured_slots == attempted);
    assert(configure_calls == static_cast<unsigned>(__builtin_popcount(attempted)));
    assert(read_calls == 0 && clock_calls == 0);
}

opp_sensors::Snapshot checkRead(const opp_sensors::Sensors& sensors) {
    resetCalls();
    const auto sample = sensors.read();
    unsigned valid = 0, raw = 0, attempted = 0;
    for (unsigned slot = 0; slot < 7; ++slot) {
        const bool ready = (ready_mask & (1U << slot)) != 0;
        const auto expected = ready ? read_status[slot] : -ENODEV;
        assert(sample.status[slot] == expected);
        if (ready) attempted |= 1U << slot;
        if (expected == 0 || expected == 1) valid |= 1U << slot;
        if (expected == 1) raw |= 1U << slot;
    }
    assert(sample.valid_mask == valid && sample.raw_mask == raw);
    assert(sample.valid == (valid == 127));
    assert(sample.started_us == clock_values[0] && sample.completed_us == clock_values[1]);
    assert(sample.completed_us - sample.started_us == clock_values[1] - clock_values[0]);
    assert(ready_calls == 7 && read_slots == attempted && configure_calls == 0);
    assert(read_calls == static_cast<unsigned>(__builtin_popcount(attempted)));
    assert(clock_calls == 2 && !reading);
    return sample;
}

void setLevels(unsigned mask) {
    for (unsigned slot = 0; slot < 7; ++slot) read_status[slot] = (mask >> slot) & 1;
}

void allMasks(bool compose) {
    opp_sensors::Sensors sensors;
    checkInit(sensors);
    for (unsigned mask = 0; mask < 128; ++mask) {
        setLevels(mask);
        const auto first = checkRead(sensors);
        assert(first.raw_mask == mask);
        if (!compose) continue;
        opp_fusion::Debouncer debouncer;
        const auto logical = static_cast<std::uint8_t>(mask ^ 0x78U);
        for (unsigned tick = 0; tick < config::OPP_SET_TICKS; ++tick) {
            const auto sample = checkRead(sensors);
            const auto actual = debouncer.step(1000U + tick * 1000U, sample.raw_mask);
            assert(actual == (tick + 1 == config::OPP_SET_TICKS ? logical : 0));
        }
        setLevels(0x78U);
        const auto empty = checkRead(sensors);
        assert(debouncer.step(100000U, empty.raw_mask) == logical);
        assert(debouncer.step(100000U + config::OPP_CLEAR_MS * 1000U - 1U,
                              empty.raw_mask) == logical);
        assert(debouncer.step(100000U + config::OPP_CLEAR_MS * 1000U,
                              empty.raw_mask) == 0);
    }
}

void initFailure(unsigned slot, int status, bool unavailable) {
    opp_sensors::Sensors sensors;
    checkInit(sensors);
    if (unavailable) ready_mask &= ~(1U << slot);
    else configure_status[slot] = status;
    checkInit(sensors);
    checkDenied(sensors);
    ready_mask = 127;
    configure_status[slot] = 0;
    // Recovery of the environment alone must not undo the failed begin.
    checkDenied(sensors);
    checkInit(sensors);
    checkRead(sensors);
}

void readFailure(unsigned slot, int status, bool unavailable) {
    opp_sensors::Sensors sensors;
    checkInit(sensors);
    setLevels(127);
    checkRead(sensors);
    if (unavailable) ready_mask &= ~(1U << slot);
    else read_status[slot] = status;
    checkRead(sensors);
    // No reinitialization is permitted or needed for transient read recovery.
    ready_mask = 127;
    read_status[slot] = 0;
    checkRead(sensors);
    read_status[slot] = 1;
    checkRead(sensors);
}

void malformed(unsigned slot, bool invalid_mask) {
    opp_sensors::Sensors sensors;
    if (invalid_mask) {
        checkInit(sensors);
        const auto spec = expected_specs[slot];
        const auto port = static_cast<unsigned>(spec.port - fixture_ports);
        fixture_configs[port].port_pin_mask &= ~(1U << spec.pin);
    }
    resetCalls();
    const auto result = sensors.begin();
    assert(!result.ready && result.configured_mask == 0);
    for (const auto status : result.status) assert(status == -EINVAL);
    // Reject the whole mapping before readiness, configure or timing.
    noCalls();
    checkDenied(sensors);
    if (invalid_mask) {
        for (auto& config : fixture_configs) config.port_pin_mask = 0xffffffffU;
        checkDenied(sensors);
        checkInit(sensors);
        checkRead(sensors);
    }
}

void mixed() {
    opp_sensors::Sensors sensors;
    ready_mask = 0;
    checkInit(sensors);
    checkDenied(sensors);
    ready_mask = 0x35;
    for (unsigned slot = 0; slot < 7; ++slot) configure_status[slot] = -7 - int(slot);
    configure_status[2] = 0;
    checkInit(sensors);
    checkDenied(sensors);
    ready_mask = 127;
    for (auto& status : configure_status) status = 0;
    checkInit(sensors);
    ready_mask = 0;
    checkRead(sensors);
    ready_mask = 0x6f;
    const int values[7] = {1, -1, 0, 2, 1, INT_MIN, INT_MAX};
    for (unsigned slot = 0; slot < 7; ++slot) read_status[slot] = values[slot];
    checkRead(sensors);
    ready_mask = 127;
    setLevels(0);
    checkRead(sensors);
}

void timestamps() {
    opp_sensors::Sensors sensors;
    checkInit(sensors);
    const std::uint32_t starts[] = {0, 1, 0x7fffffffU, 0xfffffff9U, 0xffffffffU};
    const std::uint32_t elapsed[] = {0, 1, 7, 113, 0x80000001U};
    for (const auto start : starts) {
        for (const auto duration : elapsed) {
            clock_values[0] = start;
            clock_values[1] = start + duration;
            checkRead(sensors);
        }
    }
}

void separateInstances() {
    opp_sensors::Sensors first, second;
    checkInit(first);
    checkDenied(second);
    configure_status[2] = -EIO;
    checkInit(second);
    checkRead(first);
    checkDenied(second);
    configure_status[2] = 0;
    checkInit(second);
    checkRead(second);
}

void longRun() {
    opp_sensors::Sensors sensors;
    checkInit(sensors);
    for (unsigned tick = 0; tick < 10000; ++tick) {
        setLevels((tick * 37U) & 127U);
        clock_values[0] = 0xffff0000U + tick * 1000U;
        clock_values[1] = clock_values[0] + (tick % 31U);
        if (tick % 41U == 0) read_status[tick % 7U] = -EIO;
        checkRead(sensors);
    }
}

#ifdef OPP_PROBE
void probeInert() {
    assert(opponent_probe::address == nullptr);
    setup();
    assert(opponent_probe::address == &opponent_probe::exercise);
    for (unsigned tick = 0; tick < 10000; ++tick) loop();
    noCalls();
    checkDenied(opponent_probe::sensors);
}
#endif
} // namespace

extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t, std::size_t);
extern "C" void* __real_realloc(void*, std::size_t);
extern "C" void __real_free(void*);
extern "C" void* __wrap_malloc(std::size_t size) {
    if (allocation_guard) ++allocation_calls;
    return __real_malloc(size);
}
extern "C" void* __wrap_calloc(std::size_t count, std::size_t size) {
    if (allocation_guard) ++allocation_calls;
    return __real_calloc(count, size);
}
extern "C" void* __wrap_realloc(void* ptr, std::size_t size) {
    if (allocation_guard) ++allocation_calls;
    return __real_realloc(ptr, size);
}
extern "C" void __wrap_free(void* ptr) {
    if (allocation_guard) ++allocation_calls;
    __real_free(ptr);
}
void* operator new(std::size_t size) { return __wrap_malloc(size); }
void* operator new[](std::size_t size) { return __wrap_malloc(size); }
void operator delete(void* ptr) noexcept { __wrap_free(ptr); }
void operator delete[](void* ptr) noexcept { __wrap_free(ptr); }
void operator delete(void* ptr, std::size_t) noexcept { __wrap_free(ptr); }
void operator delete[](void* ptr, std::size_t) noexcept { __wrap_free(ptr); }

bool device_is_ready(const device* port) {
    assert(ready_calls < 7);
    assert(port == fixtureSpec(fixture_indices[ready_calls]).port);
    if (reading) assert(clock_calls == 1);
    return (ready_mask & (1U << ready_calls++)) != 0;
}

int gpio_pin_configure_dt(const gpio_dt_spec* spec, gpio_flags_t flags) {
    assert(spec != nullptr && flags == GPIO_INPUT && spec->dt_flags == 0);
    const auto slot = slotFor(spec->port, spec->pin);
    assert(ready_calls == slot + 1 && !reading && configure_calls < 7);
    assert((ready_mask & (1U << slot)) != 0);
    assert((configured_slots & (1U << slot)) == 0);
    configured_slots |= 1U << slot;
    ++configure_calls;
    return configure_status[slot];
}

int gpio_pin_get_raw(const device* port, gpio_pin_t pin) {
    const auto slot = slotFor(port, pin);
    assert(ready_calls == slot + 1 && reading && read_calls < 7);
    assert((ready_mask & (1U << slot)) != 0 && (read_slots & (1U << slot)) == 0);
    read_slots |= 1U << slot;
    ++read_calls;
    return read_status[slot];
}

unsigned long micros() {
    assert(clock_calls < 2);
    if (clock_calls == 0) {
        assert(ready_calls == 0 && configure_calls == 0 && read_calls == 0);
        reading = true;
    } else {
        assert(ready_calls == 7);
        reading = false;
    }
    return clock_values[clock_calls++];
}

int main(int argc, char** argv) {
    assert(argc >= 2);
    noCalls(); // Includes the global Sensors construction before main.
    allocation_guard = true;
    opp_sensors::Sensors local;
    noCalls();
    checkDenied(global_sensors);
    checkDenied(local);
    static_assert(config::OPP_ACTIVE_LOW_MASK == 0x78U);
    for (unsigned slot = 0; slot < 7; ++slot) assert(config::OPP_INPUT_PINS[slot] == fixture_indices[slot]);
    const unsigned slot = argc > 2 ? unsigned(std::atoi(argv[2])) : 0;
    const int value = argc > 3 ? int(std::strtol(argv[3], nullptr, 10)) : -EIO;
    if (std::strcmp(argv[1], "masks") == 0) allMasks(false);
    else if (std::strcmp(argv[1], "composition") == 0) allMasks(true);
    else if (std::strcmp(argv[1], "init-failure") == 0) initFailure(slot, value, false);
    else if (std::strcmp(argv[1], "init-ready") == 0) initFailure(slot, value, true);
    else if (std::strcmp(argv[1], "read-failure") == 0) readFailure(slot, value, false);
    else if (std::strcmp(argv[1], "read-ready") == 0) readFailure(slot, value, true);
    else if (std::strcmp(argv[1], "malformed") == 0) malformed(slot, false);
    else if (std::strcmp(argv[1], "mask-invalid") == 0) malformed(slot, true);
    else if (std::strcmp(argv[1], "mixed") == 0) mixed();
    else if (std::strcmp(argv[1], "timestamps") == 0) timestamps();
    else if (std::strcmp(argv[1], "instances") == 0) separateInstances();
    else if (std::strcmp(argv[1], "long-run") == 0) longRun();
    else if (std::strcmp(argv[1], "valid-high-pin") == 0) { checkInit(local); checkRead(local); }
#ifdef OPP_PROBE
    else if (std::strcmp(argv[1], "probe") == 0) probeInert();
#endif
    else assert(false && "Unknown independent scenario");
    allocation_guard = false;
    assert(allocation_calls == 0);
    std::printf("PASS %s\n", argv[1]);
}

// Counts heap operations around actual Runtime construction and whole epochs.
// Keeps the test framework outside the measurement while real owners run inside.
// D096 tooling executes this public-fixture probe in both button and motor modes.
#include "doctest.h"
#include "fixtures/app_runtime_fixture.h"
#include <cstddef>
#include <cstdlib>
#include <new>

namespace {
bool counting = false;
unsigned allocations = 0U;
unsigned deallocations = 0U;
}
extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t, std::size_t);
extern "C" void* __real_realloc(void*, std::size_t);
extern "C" void __real_free(void*);
extern "C" void* __wrap_malloc(std::size_t bytes) {
    if (counting) ++allocations;
    return __real_malloc(bytes);
}
extern "C" void* __wrap_calloc(std::size_t count, std::size_t bytes) {
    if (counting) ++allocations;
    return __real_calloc(count, bytes);
}
extern "C" void* __wrap_realloc(void* memory, std::size_t bytes) {
    if (counting) ++allocations;
    return __real_realloc(memory, bytes);
}
extern "C" void __wrap_free(void* memory) {
    if (counting) ++deallocations;
    __real_free(memory);
}
void* operator new(std::size_t bytes) {
    void* result = __wrap_malloc(bytes);
    if (result == nullptr) std::abort();
    return result;
}
void* operator new[](std::size_t bytes) { return operator new(bytes); }
void operator delete(void* memory) noexcept { __wrap_free(memory); }
void operator delete[](void* memory) noexcept { __wrap_free(memory); }
void operator delete(void* memory, std::size_t) noexcept { __wrap_free(memory); }
void operator delete[](void* memory, std::size_t) noexcept { __wrap_free(memory); }

TEST_CASE("B14 D096 allocation counters detect actual malloc calloc realloc and free") {
    allocations = deallocations = 0U;
    counting = true;
    void* first = __wrap_malloc(8U);
    void* second = __wrap_calloc(2U, 8U);
    first = __wrap_realloc(first, 16U);
    __wrap_free(first);
    __wrap_free(second);
    counting = false;
    CHECK(allocations == 3U);
    CHECK(deallocations == 2U);
}

TEST_CASE("B0 B14 D096 actual Runtime whole epochs and terminal cleanup allocate nothing") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        bool good = true, terminal_passive = false;
        unsigned completed = 0U, violations = 0U, robot_faults = 0U, runtime_fault = 0U;
        allocations = deallocations = 0U;
        counting = true;
        {
            runtime_test::Rig rig;
            good = rig.begin(scenario != 0U, scenario == 2U);
            for (unsigned tick = 0U; tick < 1000U; ++tick) {
                const bool progressed = rig.next();
                good = progressed && good;
                completed += progressed ? 1U : 0U;
            }
            robot_faults = rig.owner.transaction().report().robot.contract_faults;
            runtime_fault = static_cast<unsigned>(rig.owner.report().fault);
            rig.owner.abort();
            const auto callbacks = rig.fake.count;
            rig.owner.abort();
            const bool stepped = rig.owner.step();
            const bool restarted = rig.begin();
            terminal_passive = !stepped && !restarted && callbacks == rig.fake.count;
            violations = rig.fake.violations;
        }
        counting = false;
        CAPTURE(scenario);
        CAPTURE(robot_faults); CAPTURE(runtime_fault);
        CHECK(good);
        CHECK(completed == 1000U);
        CHECK(violations == 0U);
        CHECK(terminal_passive);
        CHECK(allocations == 0U);
        CHECK(deallocations == 0U);
    }
}

TEST_CASE("B14 D096 actual Runtime finite service fault and cancellation allocate nothing") {
    bool began = false, completed = true, terminal = false;
    unsigned cancellations = 0U;
    allocations = deallocations = 0U;
    counting = true;
    {
        runtime_test::Rig rig;
        rig.fake.line_work = 0U;
        rig.fake.qtr_never_release = true;
        began = rig.begin();
        completed = rig.next();
        terminal = rig.owner.report().phase == app::RuntimePhase::FAULT;
        cancellations = rig.fake.line_cancels;
        rig.owner.abort();
    }
    counting = false;
    CHECK(began);
    CHECK_FALSE(completed);
    CHECK(terminal);
    CHECK(cancellations == 1U);
    CHECK(allocations == 0U);
    CHECK(deallocations == 0U);
}

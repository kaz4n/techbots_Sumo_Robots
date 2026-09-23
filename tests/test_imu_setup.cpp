// Verifies B3 D080 checked setup and sensor-coordinate coherent decoding.
// Derives order, timing and rejected bytes from the frozen contract, not imu.cpp.
// Runs actual Setup/decodeMotion with a scripted concrete Bus in host and sanitizer builds.
#include "doctest.h"
#include "config.h"
#include "hal/imu.h"
#include "support/imu_bus_fake.h"
#include <array>
#include <cstdint>
#include <cstdlib>
// Fatal fixture guards keep a broken sequence finite with the host no-exceptions policy.
#define IMU_REQUIRE(condition) do { CHECK(condition); if (!(condition)) std::abort(); } while (false)

namespace {
using imu::Register;
using imu_fake::Kind;
struct Expected { Kind kind; Register reg; std::uint8_t byte; };
// Literal independent D080 recipe: the register byte is read data or write data.
constexpr Expected RECIPE[] = {
    {Kind::BEGIN, Register::IDENTITY, 0},
    {Kind::READ, Register::IDENTITY, 0x68},
    {Kind::WRITE, Register::POWER_1, 0x80},
    {Kind::READ, Register::POWER_1, 0x40},
    {Kind::READ, Register::IDENTITY, 0x68},
    {Kind::READ, Register::POWER_2, 0},
    {Kind::READ, Register::USER_CONTROL, 0},
    {Kind::READ, Register::FIFO_ENABLE, 0},
    {Kind::READ, Register::FILTER, 0},
    {Kind::READ, Register::SAMPLE_DIVIDER, 0},
    {Kind::READ, Register::GYRO_RANGE, 0},
    {Kind::READ, Register::ACCEL_RANGE, 0},
    {Kind::READ, Register::INTERRUPT_CONFIG, 0},
    {Kind::READ, Register::INTERRUPT_ENABLE, 0},
    {Kind::WRITE, Register::POWER_2, 0},
    {Kind::READ, Register::POWER_2, 0},
    {Kind::WRITE, Register::POWER_1, 0},
    {Kind::READ, Register::POWER_1, 0},
    {Kind::WRITE, Register::POWER_1, 1},
    {Kind::READ, Register::POWER_1, 1},
    {Kind::WRITE, Register::USER_CONTROL, 0},
    {Kind::READ, Register::USER_CONTROL, 0},
    {Kind::WRITE, Register::FIFO_ENABLE, 0},
    {Kind::READ, Register::FIFO_ENABLE, 0},
    {Kind::WRITE, Register::INTERRUPT_CONFIG, 0},
    {Kind::READ, Register::INTERRUPT_CONFIG, 0},
    {Kind::WRITE, Register::FILTER, 1},
    {Kind::READ, Register::FILTER, 1},
    {Kind::WRITE, Register::SAMPLE_DIVIDER, 0},
    {Kind::READ, Register::SAMPLE_DIVIDER, 0},
    {Kind::WRITE, Register::GYRO_RANGE, 0x10},
    {Kind::READ, Register::GYRO_RANGE, 0x10},
    {Kind::WRITE, Register::ACCEL_RANGE, 0x10},
    {Kind::READ, Register::ACCEL_RANGE, 0x10},
    {Kind::WRITE, Register::INTERRUPT_ENABLE, 1},
    {Kind::READ, Register::INTERRUPT_ENABLE, 1},
    {Kind::READ, Register::IDENTITY, 0x68},
    {Kind::READ, Register::POWER_1, 1},
    {Kind::READ, Register::POWER_2, 0},
    {Kind::READ, Register::USER_CONTROL, 0},
    {Kind::READ, Register::FIFO_ENABLE, 0},
    {Kind::READ, Register::FILTER, 1},
    {Kind::READ, Register::SAMPLE_DIVIDER, 0},
    {Kind::READ, Register::GYRO_RANGE, 0x10},
    {Kind::READ, Register::ACCEL_RANGE, 0x10},
    {Kind::READ, Register::INTERRUPT_CONFIG, 0},
    {Kind::READ, Register::INTERRUPT_ENABLE, 1},
    {Kind::MOTION, Register::INTERRUPT_STATUS, 1}
};
static_assert(sizeof(RECIPE) / sizeof(RECIPE[0]) == 48U);
constexpr imu::BusStatus FAULTS[] = {
    imu::BusStatus::NOT_INITIALIZED, imu::BusStatus::ALREADY_STARTED,
    imu::BusStatus::INVALID_CONFIG, imu::BusStatus::INVALID_REQUEST,
    imu::BusStatus::OWNERSHIP, imu::BusStatus::READBACK,
    imu::BusStatus::BUS_NOT_IDLE, imu::BusStatus::NACK,
    imu::BusStatus::ARBITRATION_LOST, imu::BusStatus::BUS_ERROR,
    imu::BusStatus::OVERRUN, imu::BusStatus::PROTOCOL,
    imu::BusStatus::TIMEOUT, imu::BusStatus::POLL_LIMIT,
    imu::BusStatus::FAULT_LATCHED
};

void sameReport(const imu::SetupReport& actual, const imu::SetupReport& expected) {
    CHECK(actual.state == expected.state);
    CHECK(actual.fault == expected.fault);
    CHECK(actual.bus_status == expected.bus_status);
    CHECK(actual.cleanup == expected.cleanup);
    CHECK(actual.error_flags == expected.error_flags);
    CHECK(actual.started_us == expected.started_us);
    CHECK(actual.observed_us == expected.observed_us);
    CHECK(actual.advances == expected.advances);
    CHECK(actual.requests == expected.requests);
}

struct Fixture {
    imu::Bus bus;
    imu::Setup setup{bus};
    std::uint32_t origin;
    std::uint32_t now;
    explicit Fixture(std::uint32_t start = 1234U) : origin(start), now(start) {
        imu_fake::reset();
        for (std::size_t i = 0; i < 48U; ++i) {
            auto& transfer = imu_fake::script.replies[i].transfer;
            transfer.status = imu::BusStatus::OK;
            transfer.complete = true;
            transfer.count = RECIPE[i].kind == Kind::WRITE ? 0U :
                (RECIPE[i].kind == Kind::MOTION ? 15U : 1U);
            transfer.bytes[0] = RECIPE[i].byte;
        }
        CHECK(setup.start(origin, true).state == imu::SetupState::IN_PROGRESS);
        CHECK(imu_fake::script.count == 0U);
    }
    std::uint32_t nextTime() const {
        const auto& script = imu_fake::script;
        switch (script.count) {
        case 0: return origin + config::IMU_POWER_WAIT_US;
        case 3: return script.completed_us[2] + config::IMU_RESET_WAIT_US;
        case 18: return script.completed_us[16] + config::IMU_GYRO_WAIT_US;
        case 20: return script.completed_us[18] + config::IMU_PLL_WAIT_US;
        case 36: return script.completed_us[34] + config::IMU_FILTER_WAIT_US;
        default: return now;
        }
    }
    imu::SetupReport at(std::uint32_t time) {
        imu_fake::script.now_us = time;
        now = time;
        const auto before = imu_fake::script.count;
        const auto result = setup.advance(time);
        CHECK(imu_fake::script.count <= before + 1U);
        CHECK_FALSE(imu_fake::script.overflow);
        if (imu_fake::script.count != before && before != 0U)
            now = imu_fake::script.completed_us[before];
        return result;
    }
    imu::SetupReport next() {
        const auto index = imu_fake::script.count;
        IMU_REQUIRE(index < 48U);
        const auto result = at(nextTime());
        IMU_REQUIRE(imu_fake::script.count == index + 1U);
        const auto& actual = imu_fake::script.calls[index];
        CHECK(actual.kind == RECIPE[index].kind);
        CHECK(actual.reg == RECIPE[index].reg);
        CHECK(actual.value == (RECIPE[index].kind == Kind::WRITE ? RECIPE[index].byte : 0U));
        CHECK(result.requests == index + 1U);
        return result;
    }
    void before(std::size_t target) {
        while (imu_fake::script.count < target) {
            const auto report = next();
            IMU_REQUIRE(report.state == imu::SetupState::IN_PROGRESS);
        }
    }
    void terminal(imu::SetupFault fault) {
        const auto report = setup.report();
        IMU_REQUIRE(report.state == imu::SetupState::FAULT);
        CHECK(report.fault == fault);
        const auto calls = imu_fake::script.count;
        sameReport(setup.advance(now), report);
        sameReport(setup.advance(now + config::IMU_SETUP_DEADLINE_US), report);
        sameReport(setup.start(now + 1U, true), report);
        sameReport(setup.start(now + 2U, false), report);
        CHECK(imu_fake::script.count == calls);
    }
};

imu::BusTransfer motion() {
    imu::BusTransfer result{};
    result.status = imu::BusStatus::OK;
    result.complete = true;
    result.count = 15U;
    result.started_us = 700U;
    result.completed_us = 1299U;
    result.bytes[0] = 1U;
    for (std::size_t i = 1; i < 15U; ++i) result.bytes[i] = 0xFFU;
    return result;
}

void zeroFailure(const imu::CoherentMotion& result, imu::DecodeStatus expected) {
    CHECK(result.status == expected);
    CHECK_FALSE(result.coherent);
    CHECK(result.started_us == 0U);
    CHECK(result.completed_us == 0U);
    CHECK(result.interrupt_status == 0U);
    CHECK(result.rail_mask == 0U);
    CHECK(result.temperature_raw == 0);
    for (std::size_t axis = 0; axis < 3U; ++axis) {
        CHECK(result.accel_raw[axis] == 0);
        CHECK(result.gyro_raw[axis] == 0);
        CHECK(result.accel_g[axis] == 0.0F);
        CHECK(result.gyro_dps[axis] == 0.0F);
    }
}

void word(imu::BusTransfer& transfer, std::size_t slot, std::int32_t value) {
    const auto encoded = static_cast<std::uint32_t>(value < 0 ? value + 65536 : value);
    transfer.bytes[1U + slot * 2U] = static_cast<std::uint8_t>(encoded / 256U);
    transfer.bytes[2U + slot * 2U] = static_cast<std::uint8_t>(encoded % 256U);
}
} // namespace

TEST_CASE("B3 D080 setup lifecycle has no constructor destructor start or prestart IO") {
    imu_fake::reset();
    {
        imu::Bus bus;
        imu::Setup setup{bus};
        const auto initial = setup.report();
        CHECK(initial.state == imu::SetupState::NOT_STARTED);
        sameReport(setup.advance(0xFFFFFFFFU), initial);
        const auto started = setup.start(123U, true);
        CHECK(started.started_us == 123U);
        CHECK(started.advances == 0U);
        CHECK(started.requests == 0U);
        sameReport(setup.start(999U, false), started);
        CHECK(imu_fake::script.count == 0U);
    }
    CHECK(imu_fake::script.count == 0U);
}

TEST_CASE("B3 D080 unconfirmed power is terminal without Bus begin") {
    imu_fake::reset();
    imu::Bus bus;
    imu::Setup setup{bus};
    const auto report = setup.start(123U, false);
    CHECK(report.state == imu::SetupState::FAULT);
    CHECK(report.fault == imu::SetupFault::POWER_UNCONFIRMED);
    sameReport(setup.start(200U, true), report);
    sameReport(setup.advance(999999U), report);
    CHECK(imu_fake::script.count == 0U);
}

TEST_CASE("B3 D080 exactly 48 operations verify the complete profile across clock wrap") {
    for (const auto origin : {1234U, 0xFFFF0000U}) {
        Fixture fixture(origin);
        fixture.before(47U);
        const auto ready = fixture.next();
        IMU_REQUIRE(ready.state == imu::SetupState::PROFILE_READY);
        CHECK(ready.fault == imu::SetupFault::NONE);
        CHECK(ready.requests == 48U);
        CHECK(ready.advances == 48U);
        CHECK(ready.observed_us == fixture.now);
        CHECK(ready.bus_status == imu::BusStatus::OK);
        sameReport(fixture.setup.advance(fixture.now + 1000000U), ready);
        sameReport(fixture.setup.start(0U, false), ready);
        CHECK(imu_fake::script.count == 48U);
    }
}

TEST_CASE("B3 D080 every wait starts at its named successful write completion") {
    for (const auto target : {0U, 3U, 18U, 20U, 36U}) {
        Fixture fixture(0xFFFF0000U);
        fixture.before(target);
        const auto due = fixture.nextTime();
        const auto count = fixture.setup.report().advances;
        CHECK(fixture.at(due - 1U).state == imu::SetupState::IN_PROGRESS);
        CHECK(imu_fake::script.count == target);
        CHECK(fixture.setup.report().advances == count + 1U);
        CHECK(fixture.next().state == imu::SetupState::IN_PROGRESS);
        CHECK(imu_fake::script.call_us[target] == due);
    }
}

TEST_CASE("B3 D080 every nonOK Bus begin result retains status and cleanup and latches") {
    for (const auto status : FAULTS) for (const auto cleanup : {
            imu::BusCleanup::NOT_ATTEMPTED, imu::BusCleanup::DISABLED, imu::BusCleanup::UNCONFIRMED}) {
        Fixture fixture;
        imu_fake::script.replies[0].init = {status, cleanup, false};
        const auto report = fixture.next();
        CHECK(report.bus_status == status);
        CHECK(report.cleanup == cleanup);
        fixture.terminal(imu::SetupFault::TRANSPORT);
    }
}

TEST_CASE("B3 D080 successful begin must be ready with no cleanup") {
    for (const bool ready : {false, true}) for (const auto cleanup : {
            imu::BusCleanup::NOT_ATTEMPTED, imu::BusCleanup::DISABLED, imu::BusCleanup::UNCONFIRMED}) {
        if (ready && cleanup == imu::BusCleanup::NOT_ATTEMPTED) continue;
        Fixture fixture;
        imu_fake::script.replies[0].init = {imu::BusStatus::OK, cleanup, ready};
        fixture.next();
        fixture.terminal(imu::SetupFault::RESPONSE);
    }
}

TEST_CASE("B3 D080 every transfer stage preserves every nonOK fault and diagnostic") {
    for (std::size_t index = 1U; index < 48U; ++index) for (const auto status : FAULTS) {
        CAPTURE(index);
        Fixture fixture;
        fixture.before(index);
        auto& reply = imu_fake::script.replies[index];
        reply.transfer.status = status;
        reply.transfer.cleanup = imu::BusCleanup::UNCONFIRMED;
        reply.transfer.error_flags = 0xA5120080U;
        reply.transfer.complete = false;
        reply.transfer.count = 255U;
        reply.start_offset_us = 0x80000000U;
        const auto report = fixture.next();
        CHECK(report.bus_status == status);
        CHECK(report.cleanup == imu::BusCleanup::UNCONFIRMED);
        CHECK(report.error_flags == 0xA5120080U);
        fixture.terminal(imu::SetupFault::TRANSPORT);
    }
}

TEST_CASE("B3 D080 every transfer rejects malformed success without accepting data") {
    for (std::size_t index = 1U; index < 48U; ++index) for (unsigned fault = 0; fault < 9U; ++fault) {
        CAPTURE(index);
        CAPTURE(fault);
        Fixture fixture;
        fixture.before(index);
        auto& reply = imu_fake::script.replies[index];
        switch (fault) {
        case 0: reply.transfer.complete = false; break;
        case 1: ++reply.transfer.count; break;
        case 2: reply.transfer.count = static_cast<std::uint8_t>(reply.transfer.count - 1U); break;
        case 3: reply.transfer.error_flags = 1U; break;
        case 4: reply.transfer.cleanup = imu::BusCleanup::DISABLED; break;
        case 5: reply.transfer.cleanup = imu::BusCleanup::UNCONFIRMED; break;
        case 6: reply.duration_us = config::IMU_I2C_TRANSFER_US; break;
        case 7: reply.duration_us = config::IMU_I2C_TRANSFER_US + 1U; break;
        default: reply.transfer.count = 255U; break;
        }
        const auto report = fixture.next();
        CHECK(report.cleanup == reply.transfer.cleanup);
        CHECK(report.error_flags == reply.transfer.error_flags);
        fixture.terminal(imu::SetupFault::RESPONSE);
    }
}

TEST_CASE("B3 D080 every readback compares all eight bits including reserved zeros") {
    for (std::size_t index = 1U; index < 47U; ++index) {
        if (RECIPE[index].kind != Kind::READ) continue;
        for (unsigned bit = 0; bit < 8U; ++bit) {
            CAPTURE(index);
            CAPTURE(bit);
            Fixture fixture;
            fixture.before(index);
            imu_fake::script.replies[index].transfer.bytes[0] ^= static_cast<std::uint8_t>(1U << bit);
            fixture.next();
            fixture.terminal(RECIPE[index].reg == Register::IDENTITY ?
                imu::SetupFault::IDENTITY : imu::SetupFault::READBACK);
        }
    }
}

TEST_CASE("B3 D080 final discarded burst accepts bit0 either way but no other status") {
    for (unsigned status = 0; status < 256U; ++status) {
        Fixture fixture;
        fixture.before(47U);
        auto& transfer = imu_fake::script.replies[47].transfer;
        transfer.bytes[0] = static_cast<std::uint8_t>(status);
        for (std::size_t i = 1U; i < 15U; ++i) transfer.bytes[i] = 0x80U;
        const auto report = fixture.next();
        if (status < 2U) CHECK(report.state == imu::SetupState::PROFILE_READY);
        else fixture.terminal(imu::SetupFault::STATUS);
    }
}

TEST_CASE("B3 D080 caller time must follow start and every accepted completion") {
    for (const auto offset : {0xFFFFFFFFU, 0x80000000U, 0x80000001U}) {
        Fixture initial;
        initial.at(initial.origin + offset);
        CHECK(imu_fake::script.count == 0U);
        initial.terminal(imu::SetupFault::TIME_ORDER);
        Fixture after;
        after.before(2U);
        const auto calls = imu_fake::script.count;
        after.at(after.now + offset);
        CHECK(imu_fake::script.count == calls);
        after.terminal(imu::SetupFault::TIME_ORDER);
    }
}

TEST_CASE("B3 D080 successful transfer timestamps reject reversal and half-range ambiguity") {
    for (std::size_t index = 1U; index < 48U; ++index) for (unsigned mode = 0; mode < 4U; ++mode) {
        Fixture fixture;
        fixture.before(index);
        auto& reply = imu_fake::script.replies[index];
        if (mode < 2U) reply.start_offset_us = mode == 0U ? 0xFFFFFFFFU : 0x80000000U;
        else reply.duration_us = mode == 2U ? 0xFFFFFFFFU : 0x80000000U;
        fixture.next();
        fixture.terminal(imu::SetupFault::TIME_ORDER);
    }
}

TEST_CASE("B3 D080 time equality and zero transfer interval are allowed") {
    Fixture fixture;
    for (auto& reply : imu_fake::script.replies) {
        reply.start_offset_us = 0U;
        reply.duration_us = 0U;
    }
    fixture.before(47U);
    CHECK(fixture.next().state == imu::SetupState::PROFILE_READY);
}

TEST_CASE("B3 D080 every successful transfer may consume exactly 599us") {
    Fixture fixture(0xFFFF0000U);
    for (auto& reply : imu_fake::script.replies) reply.duration_us = 599U;
    fixture.before(47U);
    CHECK(fixture.next().state == imu::SetupState::PROFILE_READY);
}

TEST_CASE("B3 D080 malformed success precedes timestamp and absolute deadline checks") {
    Fixture fixture;
    fixture.before(1U);
    auto& reply = imu_fake::script.replies[1];
    reply.transfer.error_flags = 1U;
    reply.start_offset_us = 0x80000000U;
    fixture.next();
    fixture.terminal(imu::SetupFault::RESPONSE);
}

TEST_CASE("B3 D080 every stage checks exact absolute deadline before further Bus work") {
    for (std::size_t index = 0U; index < 48U; ++index) {
        Fixture fixture;
        fixture.before(index);
        const auto report = fixture.at(fixture.origin + config::IMU_SETUP_DEADLINE_US);
        CHECK(imu_fake::script.count == index);
        CHECK(report.requests == index);
        fixture.terminal(imu::SetupFault::DEADLINE);
    }
}

TEST_CASE("B3 D080 absolute deadline is exclusive before begin and at transfer completion") {
    for (const auto origin : {10U, 0xFFFF0000U}) {
        Fixture noBegin(origin);
        noBegin.at(origin + config::IMU_SETUP_DEADLINE_US);
        CHECK(imu_fake::script.count == 0U);
        noBegin.terminal(imu::SetupFault::DEADLINE);
        for (const auto lateness : {0U, 1U}) {
            Fixture fixture(origin);
            fixture.before(1U);
            const auto due = origin + config::IMU_SETUP_DEADLINE_US;
            fixture.at(due - 38U + lateness);
            CHECK(imu_fake::script.count == 2U);
            fixture.terminal(imu::SetupFault::DEADLINE);
        }
    }
}

TEST_CASE("B3 D080 only final completion strictly before deadline can publish ready") {
    for (const auto late : {0U, 1U, 2U}) {
        Fixture fixture(0xFFFF0000U);
        fixture.before(47U);
        const auto deadline = fixture.origin + config::IMU_SETUP_DEADLINE_US;
        const auto report = fixture.at(deadline - 39U + late);
        CHECK(imu_fake::script.count == 48U);
        if (late == 0U) {
            CHECK(report.state == imu::SetupState::PROFILE_READY);
            CHECK(report.observed_us == deadline - 1U);
        } else fixture.terminal(imu::SetupFault::DEADLINE);
    }
}

TEST_CASE("B3 D080 frozen time exhausts exactly the finite advance allowance") {
    Fixture fixture;
    for (std::uint32_t count = 1U; count <= config::IMU_SETUP_MAX_ADVANCES; ++count) {
        const auto report = fixture.at(fixture.origin);
        IMU_REQUIRE(report.state == imu::SetupState::IN_PROGRESS);
        CHECK(report.advances == count);
        CHECK(report.requests == 0U);
    }
    const auto report = fixture.at(fixture.origin);
    CHECK(report.advances == config::IMU_SETUP_MAX_ADVANCES);
    CHECK(imu_fake::script.count == 0U);
    fixture.terminal(imu::SetupFault::ADVANCE_LIMIT);
}

TEST_CASE("B3 D080 decoder axis placement and scale use the documented high byte first layout") {
    auto transfer = motion();
    const std::int32_t values[] = {4096, -8192, 12288, -12345, 3280, -6560, 9840};
    for (std::size_t i = 0; i < 7U; ++i) word(transfer, i, values[i]);
    const auto result = imu::decodeMotion(transfer);
    IMU_REQUIRE(result.coherent);
    CHECK(result.status == imu::DecodeStatus::OK);
    for (std::size_t i = 0; i < 3U; ++i) {
        CHECK(result.accel_raw[i] == values[i]);
        CHECK(result.gyro_raw[i] == values[i + 4U]);
    }
    CHECK(result.temperature_raw == -12345);
    CHECK(result.accel_g[0] == doctest::Approx(1.0));
    CHECK(result.accel_g[1] == doctest::Approx(-2.0));
    CHECK(result.accel_g[2] == doctest::Approx(3.0));
    CHECK(result.gyro_dps[0] == doctest::Approx(100.0));
    CHECK(result.gyro_dps[1] == doctest::Approx(-200.0));
    CHECK(result.gyro_dps[2] == doctest::Approx(300.0));
    CHECK(result.started_us == 700U);
    CHECK(result.completed_us == 1299U);
    CHECK(result.interrupt_status == 1U);
    CHECK(result.rail_mask == 0U);
}

TEST_CASE("B3 D080 all 65536 signed word patterns decode at every sensor position") {
    auto transfer = motion();
    for (std::int32_t value = -32768; value <= 32767; ++value) {
        for (std::size_t slot = 0; slot < 7U; ++slot) word(transfer, slot, value);
        const auto result = imu::decodeMotion(transfer);
        IMU_REQUIRE(result.coherent);
        CHECK(result.temperature_raw == value);
        CHECK(result.rail_mask == (value == -32768 || value == 32767 ? 0x7FU : 0U));
        for (std::size_t axis = 0; axis < 3U; ++axis) {
            CHECK(result.accel_raw[axis] == value);
            CHECK(result.gyro_raw[axis] == value);
            CHECK(result.accel_g[axis] == doctest::Approx(static_cast<double>(value) / 4096.0));
            CHECK(result.gyro_dps[axis] == doctest::Approx(static_cast<double>(value) / 32.8));
        }
    }
}

TEST_CASE("B3 D080 each independent rail bit marks both limits without rejecting coherent data") {
    for (std::size_t slot = 0; slot < 7U; ++slot) for (const auto value : {-32768, 32767, -32767, 32766}) {
        auto transfer = motion();
        word(transfer, slot, value);
        const auto result = imu::decodeMotion(transfer);
        IMU_REQUIRE(result.coherent);
        CHECK(result.rail_mask == (value == -32768 || value == 32767 ? 1U << slot : 0U));
    }
}

TEST_CASE("B3 D080 decoder status bit0 is diagnostic and every other bit rejects all payload") {
    for (unsigned status = 0; status < 256U; ++status) {
        auto transfer = motion();
        transfer.bytes[0] = static_cast<std::uint8_t>(status);
        const auto result = imu::decodeMotion(transfer);
        if (status < 2U) {
            CHECK(result.coherent);
            CHECK(result.interrupt_status == status);
        } else zeroFailure(result, imu::DecodeStatus::STATUS);
    }
}

TEST_CASE("B3 D080 decoder every transport fault precedes malformed payload validation") {
    for (const auto status : FAULTS) {
        auto transfer = motion();
        transfer.status = status;
        transfer.complete = false;
        transfer.count = 0U;
        transfer.cleanup = imu::BusCleanup::UNCONFIRMED;
        transfer.error_flags = 0xFFFFFFFFU;
        transfer.bytes[0] = 0xFFU;
        transfer.completed_us = transfer.started_us - 1U;
        zeroFailure(imu::decodeMotion(transfer), imu::DecodeStatus::TRANSPORT);
    }
}

TEST_CASE("B3 D080 decoder rejects every incomplete count and malformed successful result") {
    for (unsigned count = 0U; count <= 255U; ++count) {
        if (count == 15U) continue;
        auto transfer = motion();
        transfer.count = static_cast<std::uint8_t>(count);
        zeroFailure(imu::decodeMotion(transfer), imu::DecodeStatus::RESPONSE);
    }
    for (unsigned mode = 0; mode < 8U; ++mode) {
        auto transfer = motion();
        switch (mode) {
        case 0: transfer.complete = false; break;
        case 1: transfer.cleanup = imu::BusCleanup::DISABLED; break;
        case 2: transfer.cleanup = imu::BusCleanup::UNCONFIRMED; break;
        case 3: transfer.error_flags = 1U; break;
        case 4: transfer.completed_us = transfer.started_us + config::IMU_I2C_TRANSFER_US; break;
        case 5: transfer.completed_us = transfer.started_us + config::IMU_I2C_TRANSFER_US + 1U; break;
        case 6: transfer.completed_us = transfer.started_us - 1U; break;
        default: transfer.completed_us = transfer.started_us + 0x80000000U; break;
        }
        zeroFailure(imu::decodeMotion(transfer), imu::DecodeStatus::RESPONSE);
    }
}

TEST_CASE("B3 D080 decoder accepts zero and 599us intervals including unsigned wrap") {
    for (const auto origin : {0U, 0xFFFFFF00U}) for (const auto duration : {0U, 1U, 599U}) {
        auto transfer = motion();
        transfer.started_us = origin;
        transfer.completed_us = origin + duration;
        const auto result = imu::decodeMotion(transfer);
        CHECK(result.coherent);
        CHECK(result.started_us == origin);
        CHECK(result.completed_us == origin + duration);
    }
}

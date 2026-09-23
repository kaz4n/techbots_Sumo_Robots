// Tests the D081 two-transaction native acquisition through unchanged MMIO models.
// Derives phase order, shared budget and zero-data failure from the public contract.
// The model proves software progression only, never physical shadow synchronization.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"
#include <cstdlib>

namespace {
unsigned clears = 0U;
std::uint8_t burst_status = 0U;
bool ordered = true;
unsigned phase = 0U;
std::uint32_t flags = 0U, deadline = 0U;
fixture::Point inject_point = fixture::Point::LAST_RX;
void begin(imu::Bus& bus) {
    const auto result = bus.begin(); CHECK(result.ready);
    if (!result.ready) std::abort();
    fixture::hw.bytes[0] = 1U;
}
void empty(const imu::BusAcquisition& result) {
    CHECK(result.state == imu::AcquisitionState::FAULT);
    CHECK_FALSE(result.transfer.complete); CHECK(result.transfer.count == 0U);
    for (auto byte : result.transfer.bytes) CHECK(byte == 0U);
}
void protocol(fixture::Point point, std::uintptr_t) {
    if (point == fixture::Point::STOP_CLEAR) ++clears;
    if (point == fixture::Point::START && fixture::hw.start_count == 3U) {
        ordered = clears == 1U && !(fixture::peek(I2C4->ISR) &
                  (I2C_ISR_BUSY | I2C_ISR_STOPF | I2C_ISR_RXNE));
    }
    if (point == fixture::Point::START && fixture::hw.start_count == 4U)
        fixture::hw.bytes[0] = burst_status;
}
void latched(imu::Bus& bus, imu::BusCleanup cleanup) {
    fixture::clearTrace(); fixture::hw.irq_reads = 0U;
    auto result = bus.acquireMotion(); empty(result);
    CHECK(result.transfer.status == imu::BusStatus::FAULT_LATCHED);
    CHECK(result.transfer.cleanup == cleanup); CHECK(result.transfer.error_flags == 0U);
    CHECK_FALSE(result.readiness_observed); CHECK_FALSE(result.motion_attempted);
    CHECK_FALSE(result.motion_status_observed);
    CHECK(result.readiness_status == 0U); CHECK(result.motion_status == 0U);
    CHECK(result.readiness_completed_us == 0U); CHECK(result.motion_started_us == 0U);
    CHECK(bus.readMotion().status == imu::BusStatus::FAULT_LATCHED);
    CHECK(bus.readRegister(imu::Register::IDENTITY).status == imu::BusStatus::FAULT_LATCHED);
    CHECK(bus.writeRegister(imu::Register::POWER_1, 0U).status == imu::BusStatus::FAULT_LATCHED);
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.ready_reads == 0U); CHECK(fixture::hw.irq_reads == 0U);
}
void accepted(const imu::BusAcquisition& r, std::uint32_t start) {
    CHECK(r.state == imu::AcquisitionState::OBSERVATION); CHECK(r.transfer.complete);
    CHECK(r.transfer.status == imu::BusStatus::OK); CHECK(r.transfer.count == 15U);
    CHECK(r.transfer.cleanup == imu::BusCleanup::NOT_ATTEMPTED); CHECK(r.transfer.error_flags == 0U);
    CHECK(r.readiness_observed); CHECK(r.readiness_status == 1U); CHECK(r.motion_attempted);
    CHECK(r.motion_status_observed); CHECK(r.motion_status == burst_status);
    CHECK(r.transfer.started_us == start); CHECK(r.transfer.bytes[0] == burst_status);
    const auto duration = r.transfer.completed_us - start;
    CHECK(duration < config::IMU_I2C_TRANSFER_US);
    CHECK(r.readiness_completed_us - start <= r.motion_started_us - start);
    CHECK(r.motion_started_us - start <= duration);
    for (unsigned i = 1U; i < 15U; ++i) CHECK(r.transfer.bytes[i] == fixture::hw.bytes[i]);
    CHECK(fixture::hw.command_errors == 0U); CHECK(fixture::hw.gated_reads == 0U);
}
} // namespace

TEST_CASE("B3 D081 acquisition before begin has default fault and no native activity") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; const auto r = bus.acquireMotion(); empty(r);
        CHECK(r.transfer.status == imu::BusStatus::NOT_INITIALIZED);
        CHECK_FALSE(r.readiness_observed); CHECK_FALSE(r.motion_attempted);
        CHECK_FALSE(r.motion_status_observed); CHECK(r.transfer.started_us == 0U);
        CHECK(r.transfer.completed_us == 0U); CHECK(fixture::hw.accesses == 0U);
        CHECK(fixture::hw.micros_calls == 0U); CHECK(fixture::hw.ready_reads == 0U);
    });
}

TEST_CASE("B3 D081 exact one-byte status STOP idle then fifteen-byte status and motion") {
    for (unsigned status : {0U, 1U}) fixture::isolated([status] {
        fixture::reset(); imu::Bus bus; begin(bus); burst_status = status;
        fixture::hw.now = 1000U; fixture::hw.hook = protocol;
        const auto r = bus.acquireMotion(); accepted(r, 1000U);
        CHECK(ordered); CHECK(clears == 2U); CHECK(fixture::hw.start_count == 4U);
        CHECK(fixture::hw.tx_count == 2U); CHECK(fixture::hw.rx_count == 16U);
        CHECK(fixture::hw.transmitted[0] == 0x3aU); CHECK(fixture::hw.transmitted[1] == 0x3aU);
        for (unsigned index = 0U; index < 4U; ++index) {
            const auto command = fixture::hw.starts[index].cr2;
            const bool read = index % 2U != 0U;
            CHECK(((command & I2C_CR2_NBYTES) >> I2C_CR2_NBYTES_Pos) == (index == 3U ? 15U : 1U));
            CHECK((command & I2C_CR2_RD_WRN) == (read ? I2C_CR2_RD_WRN : 0U));
            CHECK((command & I2C_CR2_AUTOEND) == (read ? I2C_CR2_AUTOEND : 0U));
            CHECK((command & I2C_CR2_SADD) == config::IMU_I2C_ADDRESS << 1U);
            CHECK((command & (I2C_CR2_STOP | I2C_CR2_RELOAD | I2C_CR2_ADD10)) == 0U);
        }
        CHECK(fixture::hw.stop_count == 0U); CHECK(fixture::hw.disable_count == 0U);
    });
}

TEST_CASE("B3 D081 readiness zero completes once with no motion and all bytes zero") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.bytes[0] = 0U;
        fixture::hw.now = 99U; fixture::hw.hook = protocol;
        const auto r = bus.acquireMotion(); CHECK(r.state == imu::AcquisitionState::NO_NEW);
        CHECK(r.transfer.status == imu::BusStatus::OK); CHECK(r.transfer.complete);
        CHECK(r.transfer.count == 0U); for (auto byte : r.transfer.bytes) CHECK(byte == 0U);
        CHECK(r.readiness_observed); CHECK(r.readiness_status == 0U);
        CHECK(r.readiness_completed_us == r.transfer.completed_us);
        CHECK_FALSE(r.motion_attempted); CHECK(r.motion_started_us == 0U);
        CHECK_FALSE(r.motion_status_observed); CHECK(r.motion_status == 0U);
        CHECK(r.transfer.started_us == 99U); CHECK(r.transfer.completed_us > 99U);
        CHECK(r.transfer.error_flags == 0U); CHECK(r.transfer.cleanup == imu::BusCleanup::NOT_ATTEMPTED);
        CHECK(fixture::hw.start_count == 2U); CHECK(fixture::hw.rx_count == 1U); CHECK(clears == 1U);
    });
}

TEST_CASE("B3 D081 repeated changed and numerically equal payloads are independent observations") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.hook = protocol;
        for (unsigned index = 0U; index < 4U; ++index) {
            fixture::hw.start_count = fixture::hw.tx_count = fixture::hw.rx_count = 0U;
            clears = 0U; fixture::hw.bytes[0] = 1U;
            fixture::hw.bytes[1] = index < 2U ? 9U : 23U;
            const auto r = bus.acquireMotion(); CHECK(r.state == imu::AcquisitionState::OBSERVATION);
            CHECK(r.transfer.bytes[1] == (index < 2U ? 9U : 23U));
            CHECK(fixture::hw.start_count == 4U); CHECK(fixture::hw.rx_count == 16U);
        }
        fixture::hw.bytes[0] = 0U; const auto empty_read = bus.acquireMotion();
        CHECK(empty_read.state == imu::AcquisitionState::NO_NEW);
        for (auto byte : empty_read.transfer.bytes) CHECK(byte == 0U);
    });
}

TEST_CASE("B3 D081 every unexpected readiness or burst status bit terminally rejects payload") {
    for (bool second : {false, true}) for (unsigned bit = 1U; bit < 8U; ++bit)
        for (unsigned ready_bit : {0U, 1U}) fixture::isolated([second, bit, ready_bit] {
            fixture::reset(); imu::Bus bus; begin(bus);
            const auto invalid = static_cast<std::uint8_t>((1U << bit) | ready_bit);
            if (second) burst_status = invalid; else fixture::hw.bytes[0] = invalid;
            fixture::hw.hook = protocol; const auto r = bus.acquireMotion(); empty(r);
            CHECK(r.transfer.status == imu::BusStatus::PROTOCOL);
            CHECK(r.transfer.error_flags == 0U); CHECK(r.readiness_observed);
            CHECK(r.readiness_status == (second ? 1U : invalid));
            CHECK(r.motion_attempted == second); CHECK(r.motion_status_observed == second);
            CHECK(r.motion_status == (second ? invalid : 0U));
            CHECK(fixture::hw.start_count == (second ? 4U : 2U));
            CHECK(fixture::hw.disable_count == 1U); CHECK(fixture::hw.stop_count == 0U);
            CHECK(r.transfer.cleanup == imu::BusCleanup::DISABLED); latched(bus, r.transfer.cleanup);
        });
}

TEST_CASE("B3 D081 native error in either transaction retains flags and cleans once") {
    const std::uint32_t errors[] = {I2C_ISR_NACKF, I2C_ISR_ARLO, I2C_ISR_BERR, I2C_ISR_OVR,
                                   I2C_ISR_PECERR, I2C_ISR_TIMEOUT, I2C_ISR_ALERT};
    const imu::BusStatus statuses[] = {imu::BusStatus::NACK, imu::BusStatus::ARBITRATION_LOST,
        imu::BusStatus::BUS_ERROR, imu::BusStatus::OVERRUN, imu::BusStatus::PROTOCOL,
        imu::BusStatus::PROTOCOL, imu::BusStatus::PROTOCOL};
    for (unsigned which = 0U; which < 7U; ++which) for (unsigned transaction : {1U, 2U})
        fixture::isolated([=] {
            fixture::reset(); imu::Bus bus; begin(bus); phase = transaction; flags = errors[which];
            fixture::hw.hook = [](fixture::Point point, std::uintptr_t address) {
                protocol(point, address);
                if (point == fixture::Point::RX && fixture::hw.start_count == phase * 2U)
                    I2C4->ISR.value |= flags;
            };
            const auto r = bus.acquireMotion(); empty(r); CHECK(r.transfer.status == statuses[which]);
            CHECK((r.transfer.error_flags & errors[which]) == errors[which]);
            CHECK(r.readiness_observed == (transaction == 2U));
            CHECK(r.motion_attempted == (transaction == 2U)); CHECK_FALSE(r.motion_status_observed);
            CHECK(fixture::hw.disable_count == 1U); CHECK(fixture::hw.stop_count == 0U);
            CHECK(r.transfer.cleanup == imu::BusCleanup::DISABLED); latched(bus, r.transfer.cleanup);
        });
}

TEST_CASE("B3 D081 ownership lost after either STOP prevents more commands and blind cleanup") {
    for (unsigned transaction : {1U, 2U}) fixture::isolated([transaction] {
        fixture::reset(); imu::Bus bus; begin(bus); phase = transaction;
        fixture::hw.hook = [](fixture::Point point, std::uintptr_t address) {
            protocol(point, address);
            if (point == fixture::Point::STOP_CLEAR && clears == phase)
                GPIOD->AFR[1].value ^= 1U << 16U;
        };
        const auto r = bus.acquireMotion(); empty(r); CHECK(r.transfer.status == imu::BusStatus::OWNERSHIP);
        CHECK(r.transfer.cleanup == imu::BusCleanup::NOT_ATTEMPTED);
        CHECK(fixture::hw.start_count == transaction * 2U); CHECK(fixture::hw.disable_count == 0U);
        CHECK(r.readiness_observed == (transaction == 2U)); CHECK_FALSE(r.motion_status_observed);
        latched(bus, r.transfer.cleanup);
    });
}

TEST_CASE("B3 D081 shared deadline starts at readiness and rejects final equality including wrap") {
    for (auto point : {fixture::Point::LAST_RX, fixture::Point::STOP_CLEAR})
        for (auto start : {1000U, 0xfffffe00U}) for (unsigned late : {0U, 1U})
            fixture::isolated([=] {
                fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.tick = 0U;
                fixture::hw.now = start; deadline = start + 599U + late; inject_point = point;
                fixture::hw.hook = [](fixture::Point p, std::uintptr_t address) {
                    protocol(p, address);
                    if (p == fixture::Point::STOP_CLEAR && clears == 1U) fixture::hw.now += 350U;
                    if (p == inject_point && fixture::hw.start_count == 4U) fixture::hw.now = deadline;
                };
                const auto r = bus.acquireMotion();
                if (late) { empty(r); CHECK(r.transfer.status == imu::BusStatus::TIMEOUT);
                    CHECK(r.readiness_observed); CHECK(r.motion_attempted); latched(bus, r.transfer.cleanup); }
                else { accepted(r, start); CHECK(r.transfer.completed_us == deadline); }
            });
}

TEST_CASE("B3 D081 intertransaction admission cannot borrow a second 600us budget") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.now = 10U; fixture::hw.tick = 0U;
        fixture::hw.hook = [](fixture::Point point, std::uintptr_t address) {
            protocol(point, address);
            if (point == fixture::Point::STOP_CLEAR && clears == 1U) fixture::hw.now = 609U;
            if (point == fixture::Point::START && fixture::hw.start_count == 3U) fixture::hw.now = 610U;
        };
        const auto r = bus.acquireMotion(); empty(r); CHECK(r.transfer.status == imu::BusStatus::TIMEOUT);
        CHECK(r.readiness_observed); CHECK(r.motion_attempted); CHECK(fixture::hw.rx_count == 1U);
        CHECK(fixture::hw.tx_count == 1U); CHECK(fixture::hw.disable_count == 1U);
        latched(bus, r.transfer.cleanup);
    });
}

TEST_CASE("B3 D081 poll control workloads fit each standalone transaction") {
    for (bool motion : {false, true}) fixture::isolated([motion] {
        fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.tick = 0U;
        fixture::hw.byte_after = motion ? 500 : 3500;
        const auto r = motion ? bus.readMotion() : bus.readRegister(imu::Register::INTERRUPT_STATUS);
        CHECK(r.status == imu::BusStatus::OK); CHECK(r.complete);
        CHECK(r.count == (motion ? 15U : 1U)); CHECK(fixture::hw.disable_count == 0U);
    });
}

TEST_CASE("B3 D081 frozen shared poll budget includes the completed first transaction") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.tick = 0U;
        fixture::hw.byte_after = 3500;
        fixture::hw.hook = [](fixture::Point point, std::uintptr_t address) {
            protocol(point, address);
            if (point == fixture::Point::STOP_CLEAR && clears == 1U) fixture::hw.byte_after = 500;
        };
        const auto r = bus.acquireMotion(); empty(r); CHECK(r.transfer.status == imu::BusStatus::POLL_LIMIT);
        CHECK(r.readiness_observed); CHECK(r.motion_attempted); CHECK(fixture::hw.start_count == 4U);
        CHECK(fixture::hw.rx_count > 1U); CHECK(fixture::hw.rx_count < 16U);
        CHECK(fixture::hw.accesses < 1000000U); CHECK(fixture::hw.disable_count == 1U);
        latched(bus, r.transfer.cleanup);
    });
}

TEST_CASE("B3 D081 terminal cleanup remains one independent 50us allowance") {
    for (unsigned late : {0U, 1U}) fixture::isolated([late] {
        fixture::reset(); imu::Bus bus; begin(bus); fixture::hw.tick = 0U; fixture::hw.now = 1000U;
        deadline = 1000U + 49U + late;
        fixture::hw.hook = [](fixture::Point point, std::uintptr_t address) {
            protocol(point, address);
            if (point == fixture::Point::RX && fixture::hw.start_count == 4U) I2C4->ISR.value |= I2C_ISR_NACKF;
            if (point == fixture::Point::DISABLE) fixture::hw.now = deadline;
        };
        const auto r = bus.acquireMotion(); empty(r); CHECK(r.transfer.status == imu::BusStatus::NACK);
        CHECK(r.transfer.cleanup == (late ? imu::BusCleanup::UNCONFIRMED : imu::BusCleanup::DISABLED));
        CHECK(fixture::hw.disable_count == 1U); CHECK(fixture::hw.stop_count == 0U);
        latched(bus, r.transfer.cleanup);
    });
}

TEST_CASE("B3 D081 missing second STOP cannot publish consumed readiness or partial motion") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; begin(bus);
        fixture::hw.hook = [](fixture::Point point, std::uintptr_t address) {
            protocol(point, address);
            if (point == fixture::Point::START && fixture::hw.start_count == 4U) {
                fixture::hw.with_final_stop = false; fixture::hw.stop_after = -1;
            }
        };
        const auto r = bus.acquireMotion(); empty(r); CHECK(r.transfer.status == imu::BusStatus::TIMEOUT);
        CHECK(r.readiness_observed); CHECK(r.motion_attempted); CHECK_FALSE(r.motion_status_observed);
        CHECK(fixture::hw.rx_count == 16U); latched(bus, r.transfer.cleanup);
    });
}

TEST_CASE("B3 D081 setup successful acquisition and fault cleanup allocate no heap") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus; imu::BusInit init; imu::BusAcquisition first, second;
        { fixture::AllocationGuard guard;
            init = bus.begin(); fixture::hw.bytes[0] = 1U; fixture::hw.hook = protocol;
            first = bus.acquireMotion(); fixture::hw.bytes[0] = 0x80U; second = bus.acquireMotion(); }
        CHECK(init.ready); CHECK(first.state == imu::AcquisitionState::OBSERVATION);
        empty(second); CHECK(fixture::hw.allocations == 0U);
    });
}

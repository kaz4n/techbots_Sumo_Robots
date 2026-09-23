// Tests the frozen D094 protocol by calling the actual opaque native Bus sources.
// Independent yields and register faults expose per-call work and lifetime budgets.
// Process isolation preserves the production irreversible claim without reset hooks.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"
#include <initializer_list>
#include <cstdint>

namespace {
unsigned clears = 0U;
bool ordered = true, immediate_byte = false;
std::uint8_t burst_status = 0U;
void hook(fixture::Point p, std::uintptr_t) {
    if (p == fixture::Point::STOP_CLEAR) ++clears;
    if (p == fixture::Point::START && fixture::hw.start_count == 3U)
        ordered = clears == 1U && !(I2C4->ISR.value & (I2C_ISR_STOPF | I2C_ISR_BUSY | I2C_ISR_RXNE));
    if (p == fixture::Point::START && fixture::hw.start_count == 4U)
        fixture::hw.bytes[0] = burst_status;
    if (p == fixture::Point::RX && immediate_byte && fixture::hw.remaining) {
        I2C4->RXDR.value = fixture::hw.bytes[fixture::hw.byte_index];
        I2C4->ISR.value |= I2C_ISR_RXNE;
        if (fixture::hw.remaining == 1U) {
            I2C4->ISR.value |= I2C_ISR_STOPF; I2C4->ISR.value &= ~I2C_ISR_BUSY;
        }
    }
}
void boot(imu::Bus& bus, std::uint32_t now = 1000U) {
    fixture::reset(); clears = 0U; ordered = true; immediate_byte = false; burst_status = 0U;
    REQUIRE(bus.begin().ready); fixture::hw.tick = 0U; fixture::hw.now = now;
    fixture::hw.bytes[0] = 1U; fixture::hw.hook = hook;
}
void emptyAcquisition(const imu::BusAcquisition& a) {
    CHECK(a.state == imu::AcquisitionState::FAULT);
    CHECK(a.transfer.status == imu::BusStatus::NOT_INITIALIZED);
    CHECK(a.transfer.cleanup == imu::BusCleanup::NOT_ATTEMPTED);
    CHECK_FALSE(a.transfer.complete); CHECK(a.transfer.count == 0U);
    CHECK(a.transfer.started_us == 0U); CHECK(a.transfer.completed_us == 0U);
    CHECK(a.transfer.error_flags == 0U);
    for (auto b : a.transfer.bytes) CHECK(b == 0U);
    CHECK(a.readiness_status == 0U); CHECK_FALSE(a.readiness_observed);
    CHECK(a.readiness_completed_us == 0U); CHECK_FALSE(a.motion_attempted);
    CHECK(a.motion_started_us == 0U); CHECK_FALSE(a.motion_status_observed); CHECK(a.motion_status == 0U);
}
unsigned actions() { return fixture::hw.start_count + fixture::hw.tx_count + fixture::hw.rx_count + clears; }
imu::BusProgress step(imu::Bus& bus) {
    const auto prior = bus.motionReport(); const auto before = actions();
    const auto p = bus.advanceMotion(); CHECK_FALSE(p.started);
    CHECK(actions() - before <= 1U);
    if (prior.state == imu::AsyncState::PENDING) {
        CHECK(p.polls >= prior.polls); CHECK(p.polls - prior.polls <= 3U);
        if (p.state != imu::AsyncState::FAULT) CHECK(p.polls > prior.polls);
    }
    if (p.state == imu::AsyncState::PENDING) {
        CHECK_FALSE(p.completed); emptyAcquisition(p.acquisition);
    }
    return p;
}
imu::BusProgress drain(imu::Bus& bus, unsigned limit = 100U) {
    auto p = bus.motionReport();
    for (unsigned i = 0U; i < limit && p.state == imu::AsyncState::PENDING; ++i) p = step(bus);
    CHECK(p.state != imu::AsyncState::PENDING); return p;
}
void failed(const imu::BusProgress& p, imu::BusStatus status) {
    CHECK(p.state == imu::AsyncState::FAULT); CHECK(p.completed); CHECK_FALSE(p.started);
    CHECK(p.acquisition.state == imu::AcquisitionState::FAULT);
    CHECK(p.acquisition.transfer.status == status); CHECK_FALSE(p.acquisition.transfer.complete);
    CHECK(p.acquisition.transfer.count == 0U); for (auto b : p.acquisition.transfer.bytes) CHECK(b == 0U);
}
void passive(imu::Bus& bus, const imu::BusProgress& terminal) {
    fixture::clearTrace(); fixture::hw.ready_reads = fixture::hw.irq_reads = 0U;
    for (const auto& p : {bus.motionReport(), bus.advanceMotion(), bus.cancelMotion()}) {
        CHECK(p.state == terminal.state); CHECK_FALSE(p.started); CHECK_FALSE(p.completed);
        CHECK(p.started_us == terminal.started_us); CHECK(p.observed_us == terminal.observed_us);
        CHECK(p.polls == terminal.polls);
        CHECK(p.acquisition.transfer.status == terminal.acquisition.transfer.status);
        CHECK(p.acquisition.transfer.cleanup == terminal.acquisition.transfer.cleanup);
    }
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.ready_reads == 0U); CHECK(fixture::hw.irq_reads == 0U);
}
// Progress a byte while the CPU is outside Bus. Register effects do not count as CPU accesses.
void wireDuringYield() {
    auto& h = fixture::hw;
    if (h.start_pending) {
        h.start_pending = false; h.transfer_pending = true; h.phase_polls = 0U;
        I2C4->CR2.value &= ~I2C_CR2_START; I2C4->ISR.value |= I2C_ISR_BUSY;
    }
    if (!h.transfer_pending) return;
    if (h.remaining && h.read_phase && !(I2C4->ISR.value & I2C_ISR_RXNE)) {
        I2C4->RXDR.value = h.bytes[h.byte_index]; I2C4->ISR.value |= I2C_ISR_RXNE;
        if (h.remaining == 1U && h.autoend) {
            I2C4->ISR.value |= I2C_ISR_STOPF; I2C4->ISR.value &= ~I2C_ISR_BUSY;
        }
    } else if (h.remaining && !h.read_phase) I2C4->ISR.value |= I2C_ISR_TXIS;
    else if (!h.remaining && !h.autoend) I2C4->ISR.value |= I2C_ISR_TC;
}
} // namespace

TEST_CASE("B3 D094 before initialization idle methods and failed begin are inert and recoverable") {
    fixture::isolated([] {
        fixture::reset(); imu::Bus bus;
        for (const auto& p : {bus.motionReport(), bus.advanceMotion(), bus.cancelMotion()}) {
            CHECK(p.state == imu::AsyncState::IDLE); CHECK_FALSE(p.started); CHECK_FALSE(p.completed);
            emptyAcquisition(p.acquisition);
        }
        failed(bus.beginMotion(), imu::BusStatus::NOT_INITIALIZED);
        CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
        REQUIRE(bus.begin().ready); const auto p = bus.beginMotion();
        CHECK(p.state == imu::AsyncState::PENDING); CHECK(p.started); CHECK_FALSE(p.completed);
    });
}

TEST_CASE("B3 D094 begin anchors one clock and duplicate begin never alters budget") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); fixture::clearTrace();
        const auto first = bus.beginMotion(); CHECK(first.started); CHECK_FALSE(first.completed);
        CHECK(first.started_us == 1000U); CHECK(first.observed_us == 1000U); CHECK(first.polls == 0U);
        CHECK(fixture::hw.micros_calls == 1U); CHECK(fixture::hw.accesses == 0U);
        fixture::hw.now = 1599U; fixture::clearTrace();
        const auto second = bus.beginMotion(); CHECK_FALSE(second.started); CHECK_FALSE(second.completed);
        CHECK(second.started_us == 1000U); CHECK(second.observed_us == 1000U); CHECK(second.polls == 0U);
        CHECK(fixture::hw.micros_calls == 0U); CHECK(fixture::hw.accesses == 0U);
        fixture::hw.now = 1600U; failed(bus.advanceMotion(), imu::BusStatus::TIMEOUT);
        CHECK(fixture::hw.start_count == 0U); CHECK(fixture::hw.disable_count == 1U);
    });
}

TEST_CASE("B3 D094 all protocol actions yield with exact readiness STOP and burst ordering") {
    for (auto status : {0U, 1U}) fixture::isolated([status] {
        imu::Bus bus; boot(bus); burst_status = static_cast<std::uint8_t>(status);
        bus.beginMotion(); const auto p = drain(bus);
        REQUIRE(p.state == imu::AsyncState::COMPLETE); CHECK(p.completed);
        const auto& a = p.acquisition; CHECK(a.state == imu::AcquisitionState::OBSERVATION);
        CHECK(a.transfer.complete); CHECK(a.transfer.count == 15U); CHECK(a.transfer.status == imu::BusStatus::OK);
        CHECK(a.transfer.started_us == 1000U); CHECK(a.transfer.completed_us == p.observed_us);
        CHECK(a.readiness_observed); CHECK(a.readiness_status == 1U); CHECK(a.motion_attempted);
        CHECK(a.motion_status_observed); CHECK(a.motion_status == status); CHECK(ordered);
        CHECK(fixture::hw.start_count == 4U); CHECK(fixture::hw.tx_count == 2U);
        CHECK(fixture::hw.rx_count == 16U); CHECK(clears == 2U);
        for (unsigned i = 0U; i < 4U; ++i) {
            const auto cr2 = fixture::hw.starts[i].cr2;
            CHECK(((cr2 & I2C_CR2_NBYTES) >> I2C_CR2_NBYTES_Pos) == (i == 3U ? 15U : 1U));
            CHECK(bool(cr2 & I2C_CR2_RD_WRN) == bool(i & 1U));
            CHECK(bool(cr2 & I2C_CR2_AUTOEND) == bool(i & 1U));
            CHECK((cr2 & (I2C_CR2_RELOAD | I2C_CR2_STOP | I2C_CR2_ADD10)) == 0U);
        }
        CHECK(fixture::hw.transmitted[0] == 0x3aU); CHECK(fixture::hw.transmitted[1] == 0x3aU);
        for (unsigned i = 0U; i < 15U; ++i) CHECK(a.transfer.bytes[i] == fixture::hw.bytes[i]);
        CHECK(fixture::hw.stop_count == 0U); CHECK(fixture::hw.disable_count == 0U);
        CHECK(fixture::hw.command_errors == 0U); passive(bus, p);
    });
}

TEST_CASE("B3 D094 NO_NEW completes only the readiness transaction and permits next begin") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); fixture::hw.bytes[0] = 0U; bus.beginMotion();
        const auto p = drain(bus); CHECK(p.state == imu::AsyncState::COMPLETE);
        CHECK(p.acquisition.state == imu::AcquisitionState::NO_NEW);
        CHECK(p.acquisition.transfer.count == 0U); CHECK(p.acquisition.transfer.complete);
        for (auto b : p.acquisition.transfer.bytes) CHECK(b == 0U);
        CHECK(p.acquisition.readiness_completed_us == p.acquisition.transfer.completed_us);
        CHECK_FALSE(p.acquisition.motion_attempted); CHECK_FALSE(p.acquisition.motion_status_observed);
        CHECK(fixture::hw.start_count == 2U); CHECK(fixture::hw.rx_count == 1U); passive(bus, p);
        const auto next = bus.beginMotion(); CHECK(next.started); CHECK(next.polls == 0U);
        emptyAcquisition(next.acquisition);
    });
}

TEST_CASE("B3 D094 missing events return after one pass and hardware may progress during yields") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); fixture::hw.start_after = fixture::hw.byte_after = -1;
        bus.beginMotion(); auto p = step(bus); REQUIRE(p.state == imu::AsyncState::PENDING);
        const auto prior = p.polls; p = step(bus); CHECK(p.state == imu::AsyncState::PENDING);
        CHECK(p.polls == prior + 1U); CHECK(fixture::hw.tx_count == 0U);
        for (unsigned i = 0U; i < 60U && p.state == imu::AsyncState::PENDING; ++i) {
            wireDuringYield(); fixture::hw.now += 5U; p = step(bus);
        }
        CHECK(p.state == imu::AsyncState::COMPLETE); CHECK(fixture::hw.rx_count == 16U);
        CHECK(p.acquisition.transfer.completed_us - p.started_us < 600U); CHECK(ordered);
    });
}

TEST_CASE("B3 D094 immediate shifter byte reassertion does not require a false RXNE gap") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); immediate_byte = true; bus.beginMotion();
        const auto p = drain(bus); CHECK(p.state == imu::AsyncState::COMPLETE);
        CHECK(fixture::hw.rx_count == 16U); CHECK(fixture::hw.command_errors == 0U);
    });
}

TEST_CASE("B3 D094 deadline includes every caller interleave and final equality including wrap") {
    for (auto start : {1000U, 0xffffff00U}) for (auto duration : {599U, 600U, 601U})
        fixture::isolated([=] {
            imu::Bus bus; boot(bus, start); bus.beginMotion();
            while (clears < 2U && bus.motionReport().state == imu::AsyncState::PENDING) step(bus);
            REQUIRE(clears == 2U); fixture::hw.now = start + duration;
            const auto p = step(bus);
            if (duration == 599U) { CHECK(p.state == imu::AsyncState::COMPLETE);
                CHECK(p.acquisition.transfer.completed_us == start + duration); }
            else { failed(p, imu::BusStatus::TIMEOUT); CHECK(fixture::hw.disable_count == 1U); }
        });
}

TEST_CASE("B3 D094 first STOP and second admission share the original deadline") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); bus.beginMotion();
        while (clears < 1U && bus.motionReport().state == imu::AsyncState::PENDING) step(bus);
        REQUIRE(clears == 1U); fixture::hw.now = 1599U;
        REQUIRE(step(bus).state == imu::AsyncState::PENDING);
        fixture::hw.now = 1600U; const auto p = step(bus); failed(p, imu::BusStatus::TIMEOUT);
        CHECK(fixture::hw.start_count == 2U); CHECK(p.acquisition.readiness_observed);
    });
}

TEST_CASE("B3 D094 frozen clock exhausts one cumulative poll budget across both transactions") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); fixture::hw.start_after = -1; bus.beginMotion(); step(bus);
        for (unsigned i = 0U; i < 4000U; ++i) REQUIRE(step(bus).state == imu::AsyncState::PENDING);
        fixture::hw.start_after = 1;
        while (fixture::hw.start_count < 4U && bus.motionReport().state == imu::AsyncState::PENDING) step(bus);
        REQUIRE(fixture::hw.start_count == 4U); fixture::hw.byte_after = -1;
        I2C4->ISR.value &= ~I2C_ISR_RXNE;
        auto p = bus.motionReport(); unsigned calls = 0U;
        while (p.state == imu::AsyncState::PENDING && calls++ < 8193U) p = step(bus);
        failed(p, imu::BusStatus::POLL_LIMIT); CHECK(p.polls == config::IMU_I2C_MAX_POLLS);
        CHECK(calls < 4200U); CHECK(fixture::hw.disable_count == 1U); CHECK(fixture::hw.start_count == 4U);
    });
}

TEST_CASE("B3 D094 every pause can be cancelled once without publication or retry") {
    for (unsigned pause = 0U; pause < 26U; ++pause) fixture::isolated([pause] {
        imu::Bus bus; boot(bus); bus.beginMotion();
        for (unsigned i = 0U; i < pause; ++i) REQUIRE(step(bus).state == imu::AsyncState::PENDING);
        const auto starts = fixture::hw.start_count; const auto p = bus.cancelMotion();
        failed(p, imu::BusStatus::CANCELLED); CHECK(fixture::hw.disable_count == 1U);
        CHECK((p.acquisition.transfer.error_flags & (I2C_ISR_TXIS | I2C_ISR_TC | I2C_ISR_RXNE | I2C_ISR_STOPF)) == 0U);
        CHECK(fixture::hw.start_count == starts); CHECK(fixture::hw.stop_count == 0U); passive(bus, p);
        CHECK(bus.beginMotion().acquisition.transfer.status == imu::BusStatus::CANCELLED);
        CHECK(bus.readMotion().status == imu::BusStatus::FAULT_LATCHED);
        CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.disable_count == 1U);
    });
}

TEST_CASE("B3 D094 cancellation cause wins simultaneous deadline and captured native errors") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); bus.beginMotion(); step(bus);
        fixture::hw.now = 5000U; I2C4->ISR.value |= I2C_ISR_ARLO | I2C_ISR_NACKF;
        const auto p = bus.cancelMotion(); failed(p, imu::BusStatus::CANCELLED);
        CHECK((p.acquisition.transfer.error_flags & I2C_ISR_ARLO) != 0U);
        CHECK((p.acquisition.transfer.error_flags & I2C_ISR_NACKF) != 0U);
        CHECK(fixture::hw.disable_count == 1U); CHECK(fixture::hw.stop_count == 0U);
    });
}

TEST_CASE("B3 D094 cancelled unexpected protocol events are diagnostic without replacing cause") {
    for (const auto flags : {I2C_ISR_ADDR, I2C_ISR_TCR, I2C_ISR_DIR, I2C_ISR_ADDR | I2C_ISR_ARLO})
        fixture::isolated([flags] {
            imu::Bus bus; boot(bus); bus.beginMotion(); step(bus);
            I2C4->ISR.value |= flags; const auto p = bus.cancelMotion();
            failed(p, imu::BusStatus::CANCELLED);
            CHECK((p.acquisition.transfer.error_flags & flags) == flags);
            CHECK(fixture::hw.disable_count == 1U);
        });
}

TEST_CASE("B3 D094 cancel with lost ownership cannot capture unsafe flags or disable") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); bus.beginMotion(); step(bus);
        GPIOD->AFR[1].value ^= 1U << 16U; I2C4->ISR.value |= I2C_ISR_NACKF;
        const auto p = bus.cancelMotion(); failed(p, imu::BusStatus::CANCELLED);
        CHECK(p.acquisition.transfer.cleanup == imu::BusCleanup::NOT_ATTEMPTED);
        CHECK(fixture::hw.disable_count == 0U);
        GPIOD->AFR[1].value ^= 1U << 16U; passive(bus, p);
    });
}

TEST_CASE("B3 D094 event vanished before mutation returns pending without stale TXDR write") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); bus.beginMotion(); step(bus);
        fixture::hw.byte_after = -1; fixture::hw.start_pending = false;
        I2C4->CR2.value &= ~I2C_CR2_START;
        I2C4->ISR.value = I2C_ISR_TXE | I2C_ISR_BUSY | I2C_ISR_TXIS;
        fixture::hw.stop_polls = 0U;
        fixture::hw.hook = [](fixture::Point p, std::uintptr_t address) {
            if (p == fixture::Point::ACCESS && address == reinterpret_cast<std::uintptr_t>(&I2C4->ISR))
                fixture::hw.stop_polls = 1U;
            if (p == fixture::Point::CLOCK && fixture::hw.stop_polls)
                I2C4->ISR.value &= ~I2C_ISR_TXIS;
        };
        const auto p = step(bus); CHECK(p.state == imu::AsyncState::PENDING);
        CHECK(fixture::hw.tx_count == 0U); CHECK(fixture::hw.disable_count == 0U);
    });
}

TEST_CASE("B3 D094 supported legacy collisions cancel and malformed requests stay passive") {
    for (unsigned method = 0U; method < 4U; ++method) fixture::isolated([method] {
        imu::Bus bus; boot(bus); bus.beginMotion(); step(bus); fixture::clearTrace();
        CHECK(bus.readRegister(static_cast<imu::Register>(0xffU)).status == imu::BusStatus::INVALID_REQUEST);
        CHECK(bus.writeRegister(imu::Register::IDENTITY, 0U).status == imu::BusStatus::INVALID_REQUEST);
        CHECK(bus.begin().status == imu::BusStatus::ALREADY_STARTED);
        CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
        imu::BusTransfer t;
        if (method == 0U) t = bus.readRegister(imu::Register::IDENTITY);
        else if (method == 1U) t = bus.writeRegister(imu::Register::POWER_1, 0U);
        else if (method == 2U) t = bus.readMotion(); else t = bus.acquireMotion().transfer;
        CHECK(t.status == imu::BusStatus::CANCELLED); CHECK_FALSE(t.complete); CHECK(t.count == 0U);
        for (auto b : t.bytes) CHECK(b == 0U);
        CHECK(fixture::hw.start_count == 1U); CHECK(fixture::hw.disable_count == 1U);
        CHECK(bus.motionReport().state == imu::AsyncState::FAULT); CHECK_FALSE(bus.motionReport().completed);
    });
}

TEST_CASE("B3 D094 error injected at every yield prevents another protocol action") {
    const std::uint32_t bits[] = {I2C_ISR_ARLO, I2C_ISR_BERR, I2C_ISR_NACKF, I2C_ISR_OVR};
    const imu::BusStatus statuses[] = {imu::BusStatus::ARBITRATION_LOST, imu::BusStatus::BUS_ERROR,
        imu::BusStatus::NACK, imu::BusStatus::OVERRUN};
    for (unsigned pause = 0U; pause < 26U; ++pause) for (unsigned which = 0U; which < 4U; ++which)
        fixture::isolated([=] {
            imu::Bus bus; boot(bus); bus.beginMotion();
            for (unsigned i = 0U; i < pause; ++i) REQUIRE(step(bus).state == imu::AsyncState::PENDING);
            const auto before = actions(); I2C4->ISR.value |= bits[which];
            const auto p = step(bus); failed(p, statuses[which]); CHECK(actions() == before);
            CHECK((p.acquisition.transfer.error_flags & bits[which]) != 0U);
            CHECK(fixture::hw.disable_count == 1U); passive(bus, p);
        });
}

TEST_CASE("B3 D094 ownership lost during yield forbids commands and blind cleanup") {
    for (unsigned pause : {0U, 3U, 6U, 10U, 25U}) fixture::isolated([pause] {
        imu::Bus bus; boot(bus); bus.beginMotion();
        for (unsigned i = 0U; i < pause; ++i) REQUIRE(step(bus).state == imu::AsyncState::PENDING);
        const auto before = actions(); GPIOD->AFR[1].value ^= 1U << 16U;
        const auto p = step(bus); failed(p, imu::BusStatus::OWNERSHIP);
        CHECK(p.acquisition.transfer.cleanup == imu::BusCleanup::NOT_ATTEMPTED);
        CHECK(actions() == before); CHECK(fixture::hw.disable_count == 0U);
        GPIOD->AFR[1].value ^= 1U << 16U; passive(bus, p); CHECK(fixture::hw.disable_count == 0U);
    });
}

TEST_CASE("B3 D094 early STOP extra data and vanished RXNE cannot publish staged bytes") {
    for (unsigned mode = 0U; mode < 3U; ++mode) fixture::isolated([mode] {
        imu::Bus bus; boot(bus); bus.beginMotion();
        while (fixture::hw.start_count < 4U && bus.motionReport().state == imu::AsyncState::PENDING) step(bus);
        REQUIRE(fixture::hw.start_count == 4U);
        if (mode == 0U) {
            fixture::hw.start_after = fixture::hw.byte_after = -1;
            fixture::hw.start_pending = false; I2C4->CR2.value &= ~I2C_CR2_START;
            I2C4->ISR.value = I2C_ISR_TXE | I2C_ISR_STOPF;
            failed(step(bus), imu::BusStatus::PROTOCOL);
        } else if (mode == 1U) {
            while (fixture::hw.rx_count < 16U && bus.motionReport().state == imu::AsyncState::PENDING) step(bus);
            I2C4->ISR.value |= I2C_ISR_RXNE; failed(step(bus), imu::BusStatus::PROTOCOL);
        } else {
            fixture::hw.start_after = fixture::hw.byte_after = -1; wireDuringYield();
            I2C4->ISR.value &= ~I2C_ISR_RXNE;
            const auto before = fixture::hw.rx_count; const auto p = step(bus);
            CHECK(p.state == imu::AsyncState::PENDING); CHECK(fixture::hw.rx_count == before);
        }
    });
}

TEST_CASE("B3 D094 each unexpected MPU status bit faults with preserved diagnostics") {
    for (bool second : {false, true}) for (unsigned bit = 1U; bit < 8U; ++bit)
        fixture::isolated([=] {
            imu::Bus bus; boot(bus); const auto invalid = static_cast<std::uint8_t>(1U << bit);
            if (second) burst_status = invalid; else fixture::hw.bytes[0] = invalid;
            bus.beginMotion(); const auto p = drain(bus); failed(p, imu::BusStatus::PROTOCOL);
            CHECK(p.acquisition.readiness_observed);
            CHECK(p.acquisition.readiness_status == (second ? 1U : invalid));
            CHECK(p.acquisition.motion_status_observed == second);
            CHECK(p.acquisition.motion_status == (second ? invalid : 0U));
            CHECK(fixture::hw.disable_count == 1U);
        });
}

TEST_CASE("B3 D094 cleanup keeps separate 49 versus 50us boundary and frozen poll cap") {
    for (unsigned mode = 0U; mode < 3U; ++mode) fixture::isolated([mode] {
        imu::Bus bus; boot(bus); bus.beginMotion();
        fixture::hw.stop_after = static_cast<int>(mode);
        fixture::hw.hook = [](fixture::Point point, std::uintptr_t) {
            if (point == fixture::Point::DISABLE)
                fixture::hw.now += fixture::hw.stop_after == 0 ? 49U : 50U;
        };
        if (mode == 2U) { fixture::hw.ignore_disable = true; fixture::hw.hook = nullptr; }
        const auto p = bus.cancelMotion(); failed(p, imu::BusStatus::CANCELLED);
        CHECK(p.acquisition.transfer.cleanup == (mode == 0U ? imu::BusCleanup::DISABLED : imu::BusCleanup::UNCONFIRMED));
        CHECK(fixture::hw.disable_count == 1U); CHECK(fixture::hw.accesses < 1000000U); passive(bus, p);
    });
}

TEST_CASE("B3 D094 successful and failed resumptions allocate no heap") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); imu::BusProgress success, failure;
        {
            fixture::AllocationGuard guard;
            bus.beginMotion();
            for (unsigned i = 0U; i < 40U; ++i) {
                success = bus.advanceMotion(); if (success.state != imu::AsyncState::PENDING) break;
            }
            bus.beginMotion(); failure = bus.cancelMotion();
        }
        CHECK(success.state == imu::AsyncState::COMPLETE); CHECK(failure.state == imu::AsyncState::FAULT);
        CHECK(fixture::hw.allocations == 0U);
    });
}

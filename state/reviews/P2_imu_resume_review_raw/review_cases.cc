// Reviews guarded resumption and exact retained poll boundaries independently.
// Makes readiness disappear between guards instead of only between public calls.
// Links the actual native sources to the established process-isolated fixture.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/imu_bus_unoq.h"
#include "config.h"

namespace {
unsigned isr_reads = 0U, vanish_at = 0U;
std::uint32_t wanted = 0U;
void vanish(fixture::Point point, std::uintptr_t address) {
    if (point == fixture::Point::ACCESS && address == reinterpret_cast<std::uintptr_t>(&I2C4->ISR)) {
        if (++isr_reads == vanish_at) I2C4->ISR.value &= ~wanted;
    }
}
unsigned actions() { return fixture::hw.start_count + fixture::hw.tx_count + fixture::hw.rx_count; }
void boot(imu::Bus& bus) {
    fixture::reset(); REQUIRE(bus.begin().ready);
    fixture::hw.tick = 0U; fixture::hw.now = 1000U; fixture::hw.bytes[0] = 0U;
    REQUIRE(bus.beginMotion().state == imu::AsyncState::PENDING);
}
}

TEST_CASE("B3 D094 reviewer vanished expected events do not authorize a later action") {
    for (unsigned phase = 1U; phase <= 4U; ++phase) for (unsigned guard : {3U, 4U}) fixture::isolated([=] {
        imu::Bus bus; boot(bus);
        for (unsigned i = 0U; i < phase; ++i) REQUIRE(bus.advanceMotion().state == imu::AsyncState::PENDING);
        fixture::hw.start_after = fixture::hw.byte_after = fixture::hw.stop_after = -1;
        fixture::hw.start_pending = fixture::hw.transfer_pending = fixture::hw.stop_pending = false;
        I2C4->CR2.value &= ~I2C_CR2_START;
        wanted = phase == 1U ? I2C_ISR_TXIS : phase == 2U ? I2C_ISR_TC : phase == 3U ? I2C_ISR_RXNE : I2C_ISR_STOPF;
        I2C4->ISR.value = I2C_ISR_TXE | wanted;
        isr_reads = 0U; vanish_at = guard; fixture::hw.hook = vanish;
        const auto before = actions(); const auto writes = fixture::hw.writes;
        const auto p = bus.advanceMotion();
        CHECK(p.state == imu::AsyncState::PENDING); CHECK_FALSE(p.completed);
        CHECK(actions() == before); CHECK(fixture::hw.writes == writes);
        CHECK(fixture::hw.disable_count == 0U);
    });
}

TEST_CASE("B3 D094 reviewer repeated START rechecks TC at its third guard") {
    for (unsigned guard : {5U, 6U}) fixture::isolated([=] {
        imu::Bus bus; boot(bus); bus.advanceMotion(); bus.advanceMotion();
        fixture::hw.start_after = fixture::hw.byte_after = -1;
        fixture::hw.transfer_pending = fixture::hw.start_pending = false;
        I2C4->CR2.value &= ~I2C_CR2_START; I2C4->ISR.value = I2C_ISR_TXE | I2C_ISR_TC;
        wanted = I2C_ISR_TC; vanish_at = guard; isr_reads = 0U; fixture::hw.hook = vanish;
        const auto p = bus.advanceMotion();
        CHECK(p.state == imu::AsyncState::PENDING); CHECK(fixture::hw.start_count == 1U);
        CHECK(fixture::hw.disable_count == 0U);
    });
}

TEST_CASE("B3 D094 reviewer permits observation8192 and rejects the next request") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus); bus.advanceMotion();
        fixture::hw.start_after = fixture::hw.byte_after = -1;
        fixture::hw.start_pending = fixture::hw.transfer_pending = false;
        I2C4->CR2.value &= ~I2C_CR2_START; I2C4->ISR.value = I2C_ISR_TXE;
        for (unsigned i = 3U; i < config::IMU_I2C_MAX_POLLS; ++i)
            REQUIRE(bus.advanceMotion().state == imu::AsyncState::PENDING);
        CHECK(bus.motionReport().polls == 8192U);
        const auto p = bus.advanceMotion();
        CHECK(p.state == imu::AsyncState::FAULT); CHECK(p.acquisition.transfer.status == imu::BusStatus::POLL_LIMIT);
        CHECK(p.polls == 8192U); CHECK(fixture::hw.disable_count == 1U);
    });
}

TEST_CASE("B3 D094 reviewer final acceptance may consume observation8192") {
    fixture::isolated([] {
        imu::Bus bus; boot(bus);
        for (unsigned i = 0U; i < 4U; ++i) REQUIRE(bus.advanceMotion().state == imu::AsyncState::PENDING);
        fixture::hw.start_after = fixture::hw.byte_after = fixture::hw.stop_after = -1;
        fixture::hw.start_pending = fixture::hw.transfer_pending = fixture::hw.stop_pending = false;
        I2C4->CR2.value &= ~I2C_CR2_START; I2C4->ISR.value = I2C_ISR_TXE;
        while (bus.motionReport().polls < 8189U) REQUIRE(bus.advanceMotion().state == imu::AsyncState::PENDING);
        I2C4->ISR.value = I2C_ISR_TXE | I2C_ISR_STOPF;
        REQUIRE(bus.advanceMotion().state == imu::AsyncState::PENDING);
        REQUIRE(bus.motionReport().polls == 8191U);
        const auto p = bus.advanceMotion();
        CHECK(p.state == imu::AsyncState::COMPLETE); CHECK(p.completed); CHECK(p.polls == 8192U);
        CHECK(p.acquisition.state == imu::AcquisitionState::NO_NEW); CHECK(p.acquisition.transfer.complete);
        CHECK(fixture::hw.disable_count == 0U);
    });
}

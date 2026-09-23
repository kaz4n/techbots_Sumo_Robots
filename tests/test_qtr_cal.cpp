// Verifies D089 B13 calibration from public lifecycle and interval contracts.
// Exercises atomicity, ordering, deadlines and exact export independently.
// Host cases use synthetic evidence; no production implementation was inspected.
#include "doctest.h"
#include "fixtures/qtr_cal_fixture.h"
#include <cstring>
#include <limits>

using namespace qtr_cal_test;

TEST_CASE("B13 D089 raw qualification and threshold boundaries preserve identity") {
    auto s = frame(1000U, 9U, 297U, 300U);
    CHECK(line_qtr::validateRaw(s) == line_qtr::RawQualification::VALID);
    fsm::RobotInput input;
    input.t_us = 123456U;
    input.opp_raw_mask = 73U;
    input.vbat_v = 12.3F;
    line_qtr::Thresholds bank;
    for (auto& value : bank.white_us) value = 300U;
    bank.version = 18U;
    CHECK(line_qtr::applySnapshot(input, s, bank) == line_qtr::Qualification::VALID);
    CHECK(input.line.white_candidates == 15U);
    CHECK(input.line.threshold_version == 18U);
    CHECK(input.line.sequence == 9U);
    CHECK(input.t_us == 123456U);
    CHECK(input.opp_raw_mask == 73U);
    CHECK(input.vbat_v == 12.3F);
    s = frame(1000U, 9U, 300U, 303U);
    CHECK(line_qtr::applySnapshot(input, s, bank) == line_qtr::Qualification::VALID);
    CHECK(input.line.white_candidates == 0U);
    s = frame(1000U, 9U, 299U, 302U);
    CHECK(line_qtr::applySnapshot(input, s, bank) == line_qtr::Qualification::AMBIGUOUS);
    CHECK(line_qtr::applyRawSnapshot(input, s) == line_qtr::RawQualification::VALID);
    CHECK(input.line.use == core::LineUse::CALIBRATION);
    CHECK(input.line.white_candidates == 0U);
    CHECK(input.line.threshold_version == 0U);
    bank.white_us[2] = 0U;
    CHECK_FALSE(line_qtr::validThresholds(bank));
    CHECK(line_qtr::applySnapshot(input, {}, bank) == line_qtr::Qualification::INVALID);
    CHECK_FALSE(input.line.contract_valid);
}

TEST_CASE("B13 D089 eight complete batches atomically publish four literal thresholds") {
    Protocol p;
    for (unsigned stage = 0U; stage < 8U; ++stage) {
        ++p.now;
        CHECK(p.step({}, true).phase == qtr_cal::Phase::COLLECTING);
        CHECK(p.report.stage == stage);
        for (std::uint32_t n = 0U; n < config::QTR_CAL_SAMPLES; ++n) {
            p.sample((stage & 1U) == 0U ? 197U : 800U, (stage & 1U) == 0U ? 200U : 803U);
            if (stage != 7U || n + 1U != config::QTR_CAL_SAMPLES) {
                CHECK(p.owner.thresholds().version == 0U);
                for (unsigned i = 0U; i < 4U; ++i)
                    CHECK(p.owner.thresholds().white_us[i] == config::QTR_WHITE_US[i]);
                CHECK_FALSE(p.report.committed);
            }
        }
        CHECK(p.report.phase == (stage == 7U ? qtr_cal::Phase::SUCCESS : qtr_cal::Phase::WAITING));
    }
    CHECK(p.report.committed);
    CHECK(p.report.thresholds.version == 1U);
    for (unsigned i = 0U; i < 4U; ++i) {
        CHECK(p.report.thresholds.white_us[i] == 500U);
        CHECK(p.report.sensors[i].white_upper_us == 200U);
        CHECK(p.report.sensors[i].black_lower_us == 800U);
        CHECK(p.report.sensors[i].white_count == config::QTR_CAL_SAMPLES);
        CHECK(p.report.sensors[i].black_count == config::QTR_CAL_SAMPLES);
        CHECK(p.report.sensors[i].black_censored == 0U);
    }
    CHECK_FALSE(p.owner.step(p.now, eligible(p.token), {}).committed);
}

TEST_CASE("B13 D089 one-unit separation and censored black retain literal evidence") {
    Protocol narrow;
    QTR_REQUIRE(narrow.complete(200U, 201U).phase == qtr_cal::Phase::SUCCESS);
    for (const auto value : narrow.report.thresholds.white_us) CHECK(value == 200U);
    Protocol censored;
    QTR_REQUIRE(censored.complete(200U, 1600U, true).phase == qtr_cal::Phase::SUCCESS);
    for (unsigned i = 0U; i < 4U; ++i) {
        CHECK(censored.report.thresholds.white_us[i] == 850U);
        CHECK(censored.report.sensors[i].black_lower_us == 1600U);
        CHECK(censored.report.sensors[i].black_censored == config::QTR_CAL_SAMPLES);
    }
}

TEST_CASE("B13 D089 selected sensor extrema and distinct exported bank retain stage order") {
    Protocol p;
    for (unsigned stage = 0U; stage < 8U; ++stage) {
        ++p.now;
        p.step({}, true);
        for (std::uint32_t n = 0U; n < config::QTR_CAL_SAMPLES; ++n) {
            if ((stage & 1U) == 0U) {
                const auto upper = 100U + 20U * (stage / 2U) + n;
                p.sample(upper - 3U, upper);
            } else p.sample(1000U - n, 1003U - n);
        }
    }
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::SUCCESS);
    for (unsigned sensor = 0U; sensor < 4U; ++sensor) {
        CHECK(p.report.sensors[sensor].white_upper_us == 99U + 20U * sensor + config::QTR_CAL_SAMPLES);
        CHECK(p.report.sensors[sensor].black_lower_us == 1001U - config::QTR_CAL_SAMPLES);
        CHECK(p.report.thresholds.white_us[sensor] == 550U + 10U * sensor);
    }
    char buffer[128];
    std::size_t written = 0U;
    CHECK(qtr_cal::formatConfig(p.report, buffer, sizeof(buffer), written) == qtr_cal::FormatStatus::OK);
    CHECK(std::strcmp(buffer, "QTR_WHITE_US[4] = {550U, 560U, 570U, 580U}; // us\n") == 0);
}

TEST_CASE("B13 D089 invalid white and separation never mutate the complete bank") {
    Protocol p;
    QTR_REQUIRE(p.complete().phase == qtr_cal::Phase::SUCCESS);
    const auto bank = p.owner.thresholds();
    ++p.now;
    p.step({}, true);
    CHECK(p.sample(1500U, 0U, 15U).reason == qtr_cal::Reason::CENSORED_WHITE);
    CHECK(p.report.phase == qtr_cal::Phase::REJECTED);
    CHECK(p.owner.thresholds().version == bank.version);
    ++p.now;
    p.step({}, true);
    p.batch(197U, 200U);
    ++p.now;
    p.step({}, true);
    CHECK(p.batch(200U, 203U).reason == qtr_cal::Reason::NO_SEPARATION);
    for (unsigned i = 0U; i < 4U; ++i) CHECK(p.owner.thresholds().white_us[i] == bank.white_us[i]);
}

TEST_CASE("B13 D089 deadline equality wins and duplicates cannot renew capture") {
    Protocol p;
    const auto began = p.now;
    p.step({}, true);
    p.now += config::QTR_CAL_CAPTURE_MS * 1000U - 1U;
    CHECK(p.step().phase == qtr_cal::Phase::COLLECTING);
    auto duplicate = eligible(p.token, true);
    CHECK(p.owner.step(p.now + 100U, duplicate, frame(p.now, 1U)).phase == qtr_cal::Phase::COLLECTING);
    p.now = began + config::QTR_CAL_CAPTURE_MS * 1000U;
    const auto valid = frame(p.now - 1700U, 2U, 197U, 200U);
    CHECK(p.step(valid).reason == qtr_cal::Reason::DEADLINE);
    CHECK(p.report.samples == 0U);
}

TEST_CASE("B13 D089 waiting has no capture deadline but replay age remains bounded") {
    Protocol p;
    p.step({}, true);
    p.batch(197U, 200U);
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::WAITING);
    const auto old = frame(p.now - 1700U, p.sequence, 197U, 200U);
    p.now += config::QTR_CAL_CAPTURE_MS * 1000U + 17U;
    CHECK(p.step().phase == qtr_cal::Phase::WAITING);
    ++p.now;
    CHECK(p.step(old).phase == qtr_cal::Phase::REJECTED);
    CHECK(p.report.reason == qtr_cal::Reason::STALE);
}

TEST_CASE("B13 D089 pre-request acquisition is remembered but never collected") {
    Protocol p;
    const auto before = frame(p.now - 1700U, 10U, 197U, 200U);
    CHECK(p.step(before, true).phase == qtr_cal::Phase::COLLECTING);
    CHECK(p.report.samples == 0U);
    p.now += 1000U;
    CHECK(p.step(before).samples == 0U);
    p.sequence = 10U;
    CHECK(p.sample(197U, 200U).samples == (config::QTR_CAL_SAMPLES == 1U ? 0U : 1U));
}

TEST_CASE("B13 D089 exact semantic replay differs from conflicting source identity") {
    Protocol p;
    p.step({}, true);
    p.sample(197U, 200U);
    auto same = frame(p.now - 1700U, p.sequence, 197U, 200U);
    const auto count = p.report.samples;
    ++p.now;
    CHECK(p.step(same).samples == count);
    auto changed = frame(same.started_us, same.sequence, 196U, 199U);
    ++p.now;
    CHECK(p.step(changed).reason == qtr_cal::Reason::CONFLICTING_REPLAY);
}

TEST_CASE("B13 D089 source spacing sequence and modular wrap are checked") {
    Protocol wrapped;
    wrapped.now = 0xFFFFEFFFU;
    wrapped.sequence = 0xFFFFFFFDU;
    CHECK(wrapped.complete().phase == qtr_cal::Phase::SUCCESS);
    for (unsigned fault = 0U; fault < 3U; ++fault) {
        Protocol p;
        p.step({}, true);
        p.sample(197U, 200U);
        const auto start = p.now - 1700U;
        p.now += 2000U;
        auto bad = frame(start + (fault == 0U ? 1999U : 2000U),
                         p.sequence + (fault == 1U ? 0U : (fault == 2U ? 0x80000000U : 1U)),197U,200U);
        CHECK(p.step(bad).phase == qtr_cal::Phase::REJECTED);
    }
}

TEST_CASE("B13 D089 context and owner token-time high-water reject before collection") {
    for (unsigned fault = 0U; fault < 5U; ++fault) {
        Protocol p;
        p.step({}, true);
        auto result = eligible(++p.token);
        if (fault == 0U) result.outputs.motors_enabled = true;
        if (fault == 1U) result.outputs.duty_l = 0.01F;
        if (fault == 2U) result.outputs.ui_state = core::State::STOPPED;
        if (fault == 3U) result.contract_faults = fsm::LINE_CONTRACT;
        if (fault == 4U) result.line_raw_mode = false;
        CHECK(p.owner.step(p.now + 2000U, result, frame(p.now + 300U, 1U,197U,200U)).phase == qtr_cal::Phase::CANCELLED);
    }
    Protocol p;
    p.token = 50U;
    p.step({}, true);
    CHECK(p.owner.step(p.now + 1U, eligible(49U), {}).reason == qtr_cal::Reason::TOKEN_ORDER);
    CHECK(p.owner.step(p.now + 2U, eligible(50U, true), {}).phase == qtr_cal::Phase::REJECTED);
    Protocol time;
    time.step({}, true);
    CHECK(time.owner.step(time.now + 0x80000000U, eligible(2U), {}).reason == qtr_cal::Reason::TIME_ORDER);
}

TEST_CASE("B13 D089 provider and malformed records reject while pending never counts") {
    for (bool malformed : {false, true}) {
        Protocol p;
        p.step({}, true);
        auto bad = frame(p.now + 300U, 1U,197U,200U);
        if (malformed) ++bad.pad[0].upper_us;
        else { bad = {}; bad.phase = line_qtr::Phase::FAULT; bad.status = line_qtr::Status::NATIVE_ERROR; }
        p.now += 2000U;
        CHECK(p.step(bad).reason == (malformed ? qtr_cal::Reason::INVALID_RAW : qtr_cal::Reason::PROVIDER_FAULT));
    }
    Protocol pending;
    pending.step({}, true);
    pending.now += 100U;
    CHECK(pending.step().samples == 0U);
}

TEST_CASE("B13 D089 exact config export is atomic at every buffer boundary") {
    Protocol p;
    QTR_REQUIRE(p.complete().phase == qtr_cal::Phase::SUCCESS);
    const char expected[] = "QTR_WHITE_US[4] = {500U, 500U, 500U, 500U}; // us\n";
    char buffer[128];
    std::size_t written = 999U;
    CHECK(qtr_cal::formatConfig(p.report, buffer, sizeof(expected), written) == qtr_cal::FormatStatus::OK);
    CHECK(written == sizeof(expected) - 1U);
    CHECK(std::strcmp(buffer, expected) == 0);
    for (std::size_t capacity = 0U; capacity < sizeof(expected); ++capacity) {
        std::memset(buffer, 'X', sizeof(buffer));
        written = 999U;
        CHECK(qtr_cal::formatConfig(p.report, buffer, capacity, written) == qtr_cal::FormatStatus::BUFFER_TOO_SMALL);
        CHECK(written == 0U);
        CHECK(buffer[0] == (capacity == 0U ? 'X' : '\0'));
        CHECK(buffer[capacity] == 'X');
    }
    CHECK(qtr_cal::formatConfig(p.report, nullptr, 100U, written) == qtr_cal::FormatStatus::INVALID);
    auto invalid = p.report;
    invalid.thresholds.version = 0U;
    CHECK(qtr_cal::formatConfig(invalid, buffer, sizeof(buffer), written) == qtr_cal::FormatStatus::INVALID);
    CHECK(buffer[0] == '\0');
    p.owner.reset();
    CHECK(p.owner.thresholds().version == 0U);
    invalid.phase = qtr_cal::Phase::INACTIVE;
    CHECK(qtr_cal::formatConfig(invalid, buffer, sizeof(buffer), written) == qtr_cal::FormatStatus::UNAVAILABLE);
}

TEST_CASE("B13 D089 request during capture is not queued and age equality expires") {
    Protocol p;
    p.step({}, true);
    ++p.now;
    CHECK(p.step({}, true).stage == 0U);
    p.batch(197U, 200U);
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::WAITING);
    ++p.now;
    CHECK(p.step().phase == qtr_cal::Phase::WAITING);
    for (std::uint32_t age : {5999U, 6000U}) {
        Protocol boundary;
        boundary.step({}, true);
        boundary.now += age;
        const auto s = frame(boundary.now - age, 1U,197U,200U);
        const auto result = boundary.step(s);
        CHECK((result.phase == qtr_cal::Phase::REJECTED) == (age == 6000U));
        if (age == 6000U) CHECK(result.reason == qtr_cal::Reason::STALE);
    }
}

TEST_CASE("B13 D089 injected maximum bank version rejects atomically without wrapping") {
    Protocol p;
    // Authorized boundary injection on a nonconst owner; not a reachable-history proof.
    auto& bank = const_cast<line_qtr::Thresholds&>(p.owner.thresholds());
    bank.version = std::numeric_limits<std::uint32_t>::max();
    for (auto& threshold : bank.white_us) threshold = 321U;
    CHECK(p.complete().reason == qtr_cal::Reason::VERSION_EXHAUSTED);
    CHECK(p.report.phase == qtr_cal::Phase::REJECTED);
    CHECK_FALSE(p.report.committed);
    CHECK(p.owner.thresholds().version == std::numeric_limits<std::uint32_t>::max());
    for (const auto value : p.owner.thresholds().white_us) CHECK(value == 321U);
}

TEST_CASE("B13 D089 owner source era rejects unseen old frames after full wrap") {
    Protocol p;
    p.step({}, true);
    p.batch(197U, 200U);
    QTR_REQUIRE(p.report.phase == qtr_cal::Phase::WAITING);
    const auto old_start = p.now - 1700U;
    for (unsigned i = 0U; i < 4U; ++i) {
        p.now += 1000000000U;
        CHECK(p.step().phase == qtr_cal::Phase::WAITING);
    }
    p.now = old_start + 4000U + 1700U;
    CHECK(p.step(frame(old_start + 4000U, ++p.sequence,197U,200U)).reason == qtr_cal::Reason::SOURCE_ORDER);
    CHECK(p.owner.thresholds().version == 0U);
}

TEST_CASE("B13 D089 owner source era half-range adjacent boundary is exact") {
    for (std::uint32_t age : {0x7FFFFFFFU, 0x80000000U}) {
        Protocol p;
        p.step({}, true);
        p.batch(197U, 200U);
        QTR_REQUIRE(p.report.phase == qtr_cal::Phase::WAITING);
        p.now += age - 1701U;
        CHECK(p.step().phase == qtr_cal::Phase::WAITING);
        ++p.now;
        const auto report = p.step(frame(p.now - 1700U, ++p.sequence,197U,200U));
        CHECK((report.phase == qtr_cal::Phase::REJECTED) == (age == 0x80000000U));
        if (age == 0x80000000U) CHECK(report.reason == qtr_cal::Reason::SOURCE_ORDER);
        CHECK(p.owner.thresholds().version == 0U);
    }
}

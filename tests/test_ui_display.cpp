// Tests literal B3/B13/B14 matrix pixels and actual Robot diagnostic mapping.
// Expected glyphs and boundaries come only from the frozen D088 public contract.
// Independent host and sanitizer suites run this file without native hardware.
#include "doctest.h"
#include "hal/ui_display.h"
#include "robot_scenario.h"
#include <array>
#include <cmath>
#include <cstring>
#include <limits>

namespace {
using Rows = std::array<unsigned, 5>;
constexpr Rows DIGITS[] = {{7,5,7,5,7},{2,6,2,2,7},{7,1,7,4,7},
    {7,1,7,1,7},{5,5,7,1,1},{7,4,7,1,7},{7,4,7,5,7},
    {7,1,1,1,1},{7,5,7,5,7},{7,5,7,1,7}};
constexpr Rows ICONS[] = {{4,2,31,2,4},{4,8,31,8,4},{4,14,21,4,4},
    {0,14,17,2,7},{0,14,17,8,28},{10,10,10,10,10}};
constexpr Rows FAULTS[] = {{7,2,2,2,7},{7,4,7,1,7},{7,5,7,3,1},
    {4,4,4,4,7},{7,4,4,4,7},{5,5,5,7,5},{7,4,6,4,7}};
constexpr Rows HOURGLASS = {31,17,10,4,31};
constexpr Rows CROSS = {17,10,4,10,17};
constexpr Rows ERROR = {7,4,6,4,7};

ui::Frame glyphFrame(const Rows& glyph, const Rows& icon) {
    ui::Frame expected;
    for (unsigned y = 0U; y < 5U; ++y) {
        for (unsigned x = 0U; x < 3U; ++x)
            expected.pixels[(y+1U)*13U+x] = (glyph[y] & (4U >> x)) ? 7U : 0U;
        for (unsigned x = 0U; x < 5U; ++x)
            expected.pixels[(y+1U)*13U+x+4U] = (icon[y] & (16U >> x)) ? 7U : 0U;
    }
    for (unsigned x = 0U; x < 13U; x += 2U) expected.pixels[91U+x] = 7U;
    return expected;
}
void faultPixels(ui::Frame& expected, unsigned mask, unsigned selected) {
    for (unsigned bit = 0U; bit < 7U; ++bit)
        expected.pixels[bit*2U] = (mask & (1U << bit)) ? 7U : 0U;
    for (unsigned y = 0U; y < 5U; ++y)
        for (unsigned x = 0U; x < 3U; ++x)
            expected.pixels[(y+1U)*13U+10U+x] = (FAULTS[selected][y] & (4U >> x)) ? 7U : 0U;
}
void exact(const ui::DisplaySample& sample, const ui::Frame& expected,
           ui::RenderStatus status = ui::RenderStatus::OK) {
    struct Guard { std::uint8_t before[17]; ui::Frame frame; std::uint8_t after[19]; } guard;
    std::memset(guard.before, 0xa5, sizeof guard.before);
    std::memset(guard.frame.pixels, 0xa5, sizeof guard.frame.pixels);
    std::memset(guard.after, 0xa5, sizeof guard.after);
    CHECK(ui::render(sample, guard.frame) == status);
    for (unsigned i = 0U; i < 104U; ++i) {
        CAPTURE(i); CHECK(guard.frame.pixels[i] == expected.pixels[i]);
    }
    for (auto byte : guard.before) CHECK(byte == 0xa5U);
    for (auto byte : guard.after) CHECK(byte == 0xa5U);
}
ui::DisplaySample idle() {
    ui::DisplaySample sample; sample.state = core::State::IDLE; return sample;
}
void invalid(const ui::DisplaySample& sample) {
    auto expected = glyphFrame(ERROR, CROSS);
    for (unsigned bit=0U;bit<7U;++bit) expected.pixels[bit*2U]=7U;
    exact(sample, expected, ui::RenderStatus::INVALID);
}
ui::Frame sensors(unsigned opponents, unsigned lines, bool opp_valid, bool line_valid) {
    ui::Frame expected;
    // D108 corrects FL15/FC positions; all other D088 pixels and assertions stay.
    constexpr unsigned OPP[] = {15,17,19,39,47,67,71};
    constexpr unsigned LINE[] = {13,21,65,73};
    for (unsigned bit = 0U; bit < 7U; ++bit)
        expected.pixels[OPP[bit]] = opp_valid ? ((opponents & (1U << bit)) ? 7U : 0U) : 3U;
    for (unsigned bit = 0U; bit < 4U; ++bit)
        expected.pixels[LINE[bit]] = line_valid ? ((lines & (1U << bit)) ? 7U : 0U) : 3U;
    for (unsigned index : {30U,42U,43U,44U,55U,57U}) expected.pixels[index] = 7U;
    for (unsigned x = 0U; x < 13U; x += 2U) expected.pixels[91U+x] = 7U;
    return expected;
}
} // namespace

TEST_CASE("B13 D088 all six modes and every normal state have literal complete frames") {
    for (unsigned state = 1U; state <= 9U; ++state) {
        if (state == 2U) continue;
        for (unsigned mode = 1U; mode <= 6U; ++mode) {
            auto sample = idle(); sample.state = static_cast<core::State>(state);
            sample.mode = static_cast<core::Mode>(mode);
            CAPTURE(state); CAPTURE(mode); exact(sample, glyphFrame(DIGITS[mode], ICONS[mode-1U]));
        }
    }
}
TEST_CASE("B13 B14 D088 BOOT STOPPED DRIVE_TEST have distinct literal frames") {
    auto sample = idle(); sample.state = core::State::BOOT;
    exact(sample, glyphFrame({6,5,6,5,6}, HOURGLASS));
    sample.state = core::State::STOPPED; exact(sample, glyphFrame({7,4,7,1,7}, CROSS));
    sample.state = core::State::DRIVE_TEST; exact(sample, glyphFrame({6,5,5,5,6}, CROSS));
}
TEST_CASE("B13 D088 service selection never replaces a non-IDLE state") {
    constexpr Rows SERVICE_GLYPH[] = {{7,4,4,4,7},{6,5,5,5,6},{4,4,4,4,7}};
    constexpr Rows SERVICE_ICON[] = {{21,10,21,10,21},CROSS,{4,4,21,14,4}};
    for (unsigned service = 2U; service <= 4U; ++service) {
        auto sample = idle(); sample.service_menu = true;
        sample.service = static_cast<countdown::Service>(service);
        exact(sample, glyphFrame(SERVICE_GLYPH[service-2U], SERVICE_ICON[service-2U]));
        sample.state = core::State::ATTACK; exact(sample, glyphFrame(DIGITS[1], ICONS[0]));
        sample.state = core::State::STOPPED; exact(sample, glyphFrame({7,4,7,1,7}, CROSS));
        sample.state = core::State::IDLE; sample.service_menu = false;
        exact(sample, glyphFrame(DIGITS[1], ICONS[0]));
    }
}
TEST_CASE("B13 D088 SENSOR_VIEW exhaustive literal group bits and unavailable markers") {
    auto sample = idle(); sample.service_menu = true;
    sample.service = countdown::Service::SENSOR_VIEW;
    for (unsigned avail = 0U; avail < 4U; ++avail) {
        sample.opponents_available = (avail & 1U) != 0U;
        sample.lines_available = (avail & 2U) != 0U;
        for (unsigned opp = 0U; opp < 128U; ++opp) for (unsigned line = 0U; line < 16U; ++line) {
            sample.opponent_mask = static_cast<std::uint8_t>(opp);
            sample.line_mask = static_cast<std::uint8_t>(line);
            exact(sample, sensors(opp,line,sample.opponents_available,sample.lines_available));
        }
    }
}
TEST_CASE("B14 D088 each fault marker and glyph plus sparse and dense page boundaries") {
    for (unsigned mask = 1U; mask < 128U; ++mask) {
        unsigned bits[7] = {}; unsigned count = 0U;
        for (unsigned bit = 0U; bit < 7U; ++bit) if (mask & (1U << bit)) bits[count++] = bit;
        for (unsigned page = 0U; page <= count; ++page) for (unsigned delta : {0U,499999U}) {
            auto sample = idle(); sample.faults = static_cast<std::uint8_t>(mask);
            sample.t_us = page*500000U+delta;
            auto expected = glyphFrame(DIGITS[1], ICONS[0]); faultPixels(expected,mask,bits[page%count]);
            exact(sample,expected);
        }
    }
    auto sample = idle(); sample.faults = 65U;
    for (const std::uint32_t time : {0xffffffffU,0U,499999U,500000U}) {
        sample.t_us = time; auto expected = glyphFrame(DIGITS[1],ICONS[0]);
        faultPixels(expected,65U,((time/1000U/500U)%2U) ? 6U : 0U); exact(sample,expected);
    }
}
TEST_CASE("B3 D088 countdown exact seconds margin future anchor and uint32 wrap") {
    for (const std::uint32_t anchor : {0U,1234567U,0xfffffff0U}) {
        auto sample = idle(); sample.state = core::State::COUNTDOWN; sample.release_us = anchor;
        for (unsigned second = 0U; second < 5U; ++second) for (unsigned offset : {0U,1U,999999U}) {
            sample.t_us = anchor + second*1000000U + offset;
            exact(sample,glyphFrame(DIGITS[5U-second],HOURGLASS));
        }
        for (unsigned elapsed : {5000000U,5000001U,5099999U}) {
            sample.t_us = anchor+elapsed; exact(sample,glyphFrame(DIGITS[1],HOURGLASS));
        }
        for (unsigned elapsed : {5100000U,5100001U,0x7fffffffU,0x80000000U,0xffffffffU}) {
            sample.t_us = anchor+elapsed; invalid(sample);
        }
    }
}
TEST_CASE("B13 B14 D088 battery all threshold adjacent floats and ignored unavailable payload") {
    auto sample = idle(); sample.battery_available = true;
    for (unsigned level = 0U; level <= 13U; ++level) {
        const double threshold = double(config::UI_BATTERY_EMPTY_V) +
            (double(config::UI_BATTERY_FULL_V)-double(config::UI_BATTERY_EMPTY_V))*double(level)/13.0;
        const float center = static_cast<float>(threshold);
        for (float value : {std::nextafter(center,-INFINITY),center,std::nextafter(center,INFINITY)}) {
            sample.battery_v = value; auto expected = glyphFrame(DIGITS[1],ICONS[0]);
            for (unsigned x=0U;x<13U;++x) expected.pixels[91U+x]=0U;
            const unsigned count = value < threshold ? (level == 0U ? 0U : level-1U) : level;
            for (unsigned x=0U;x<count;++x) expected.pixels[91U+x]=7U;
            exact(sample,expected);
        }
    }
    for (float value : {0.0F,1.0F,100.0F,std::numeric_limits<float>::max()}) {
        sample.battery_v=value; auto expected=glyphFrame(DIGITS[1],ICONS[0]);
        for(unsigned x=0U;x<13U;++x) expected.pixels[91U+x]=value<9.5F?0U:7U;
        exact(sample,expected);
    }
    sample.battery_available=false;
    for (float value : {-1.0F,INFINITY,-INFINITY,NAN}) {
        sample.battery_v=value; exact(sample,glyphFrame(DIGITS[1],ICONS[0]));
    }
}
TEST_CASE("B13 B14 D088 invalid enums masks service and finite battery use full error frame") {
    for(unsigned value=0U;value<256U;++value) {
        if(value>11U) { auto s=idle();s.state=static_cast<core::State>(value);invalid(s); }
        if(value<1U || value>6U) { auto s=idle();s.mode=static_cast<core::Mode>(value);invalid(s); }
        if(value>4U) { auto s=idle();s.service=static_cast<countdown::Service>(value);invalid(s); }
        if(value>127U) { auto s=idle();s.opponent_mask=static_cast<std::uint8_t>(value);invalid(s); }
        if(value>15U) { auto s=idle();s.line_mask=static_cast<std::uint8_t>(value);invalid(s); }
        if(value>127U) { auto s=idle();s.faults=static_cast<std::uint8_t>(value);invalid(s); }
    }
    for(unsigned state=0U;state<12U;++state) {
        auto s=idle();s.state=static_cast<core::State>(state);s.service_menu=true;
        s.service=countdown::Service::NONE;invalid(s);
    }
    auto s=idle();s.service=countdown::Service::NONE;exact(s,glyphFrame(DIGITS[1],ICONS[0]));
    s.battery_available=true;
    for(float value:{-0.01F,INFINITY,-INFINITY,NAN}) {s.battery_v=value;invalid(s);}
}
TEST_CASE("B13 B14 D088 mapping forwards only current result fields and explicit availability") {
    fsm::RobotInput input; input.t_us=123U; input.vbat_v=11.7F;input.vbat_valid=true;
    input.observations_fresh=true; fsm::RobotResult result;result.fresh=true;result.imu_available=true;
    result.outputs.ui_state=core::State::IDLE; result.menu.selection.mode=core::Mode::ARC_L;
    result.running_mode=core::Mode::WAIT;result.menu.selection.service_menu=true;
    result.menu.selection.service=countdown::Service::LOG_DUMP;result.line_available=true;
    result.line_mask=9U;result.opponent_mask=85U;result.lifecycle.gate.release_us=99U;
    auto sample=ui::displaySample(input,result);
    CHECK(sample.t_us==123U);CHECK(sample.mode==core::Mode::ARC_L);CHECK(sample.state==core::State::IDLE);
    CHECK(sample.service_menu);CHECK(sample.service==countdown::Service::LOG_DUMP);CHECK(sample.release_us==99U);
    CHECK(sample.battery_available);CHECK(sample.battery_v==11.7F);CHECK(sample.opponents_available);
    CHECK(sample.lines_available);CHECK(sample.line_mask==9U);CHECK(sample.opponent_mask==85U);CHECK(sample.faults==0U);
    result.outputs.ui_state=core::State::ATTACK;CHECK(ui::displaySample(input,result).mode==core::Mode::WAIT);
    for(unsigned bits=0U;bits<32U;++bits) {
        result.fresh=(bits&1U)!=0U;input.line.explicit_values=(bits&2U)!=0U;
        input.opponent_fresh=(bits&4U)!=0U;input.observations_fresh=(bits&8U)!=0U;
        result.contract_faults=(bits&16U)?static_cast<unsigned>(fsm::STALE_SENSORS):0U;
        sample=ui::displaySample(input,result);
        CHECK(sample.opponents_available==(result.fresh && !(bits&16U) &&
            (input.line.explicit_values?input.opponent_fresh:input.observations_fresh)));
        CHECK(sample.lines_available==result.fresh);CHECK(sample.battery_available==result.fresh);
    }
    result.fresh=true;result.contract_faults=0U;result.line_available=false;input.vbat_valid=false;
    sample=ui::displaySample(input,result);CHECK_FALSE(sample.lines_available);CHECK_FALSE(sample.battery_available);
}
TEST_CASE("B14 D088 every direct fault source independently maps to its declared bit") {
    for(unsigned fault=0U;fault<9U;++fault) {
        fsm::RobotInput input;fsm::RobotResult result;result.fresh=true;result.imu_available=true;
        if(fault==0U)result.imu_available=false;
        if(fault==1U)result.opponent_fault_mask=64U;
        if(fault==2U)result.qtr_warning_mask=8U;
        if(fault==3U)result.low_battery=true;
        if(fault==4U)result.lifecycle.services.calibration_rejected=true;
        if(fault==5U)result.lifecycle.services.line_warning=true;
        if(fault==6U)result.contract_faults=fsm::BUTTON_CONTRACT;
        if(fault==7U)result.escape_fault=edge::EscapeFault::REPLAN_LIMIT;
        if(fault==8U)result.fresh=false;
        CHECK(ui::displaySample(input,result).faults==(1U<<(fault<7U?fault:6U)));
    }
}
TEST_CASE("B3 B14 D088 actual Robot preGO healthy IMU differs from match heading availability") {
    robot_test::Rig rig;const auto time=robot_test::select(rig,core::Mode::ARC_L);
    const auto observation=rig.at(time+1000U);const auto result=rig.submit(observation);
    CHECK(result.imu_available);CHECK_FALSE(result.heading.imu_ok);
    const auto display=ui::displaySample(observation,result);
    CHECK(display.mode==core::Mode::ARC_L);CHECK((display.faults&ui::IMU_UNAVAILABLE)==0U);
    CHECK(display.lines_available);CHECK(display.opponents_available);CHECK(display.battery_available);
    const auto duplicate=rig.submit(observation);const auto cached=ui::displaySample(observation,duplicate);
    CHECK_FALSE(cached.lines_available);CHECK_FALSE(cached.opponents_available);CHECK_FALSE(cached.battery_available);
    CHECK((cached.faults&ui::CONTRACT_FAULT)!=0U);
}
TEST_CASE("B3 B14 D088 actual Robot countdown mapping preserves anchor and margin no motion") {
    robot_test::Rig rig;const auto anchor=robot_test::release(rig,robot_test::select(rig,core::Mode::WAIT));
    for(unsigned elapsed:{0U,999999U,1000000U,4999999U,5000000U,5099999U}) {
        auto input=rig.at(anchor+elapsed);const auto result=elapsed==0U?rig.last:rig.submit(input);
        const auto sample=ui::displaySample(input,result);
        CHECK(sample.release_us==anchor);CHECK(sample.state==core::State::COUNTDOWN);
        CHECK(sample.mode==core::Mode::WAIT);CHECK(result.imu_available);robot_test::zero(result);
    }
}
TEST_CASE("B14 D088 actual Robot missing malformed and explicit validated preGO IMU") {
    for(unsigned scenario=0U;scenario<5U;++scenario) {
        robot_test::Rig rig;rig.input.imu_ok=scenario!=0U;
        if(scenario==1U)rig.input.initialization_complete=false;
        if(scenario==2U)rig.input.raw_heading_deg=NAN;
        if(scenario>=3U) {
            rig.input.imu_ok=false;
            rig.input.imu={true,true,core::ImuPresence::VALID,core::ImuPresence::VALID,true,true,1000U,1000U,1U};
            if(scenario==4U)rig.input.imu.contract_valid=false;
        }
        const auto input=rig.at(1000U);const auto result=rig.submit(input);
        CHECK(result.imu_available==(scenario==3U));CHECK_FALSE(result.heading.imu_ok);
        CHECK(((ui::displaySample(input,result).faults&ui::IMU_UNAVAILABLE)==0U)==(scenario==3U));
        if(scenario==2U||scenario==4U) CHECK((result.contract_faults&fsm::HEADING_CONTRACT)!=0U);
    }
}
TEST_CASE("B13 D088 actual Robot service menu routes all four display selections without execution") {
    robot_test::Rig rig;auto time=robot_test::longMode(rig,robot_test::idle(rig)+1U);
    for(unsigned service=1U;service<=4U;++service) {
        if(service>1U)time=robot_test::shortMode(rig,time+1U);
        const auto input=rig.at(time+1U);const auto result=rig.submit(input);++time;
        const auto sample=ui::displaySample(input,result);
        CHECK(result.menu.selection.service_menu);CHECK(sample.service_menu);
        CHECK(static_cast<unsigned>(sample.service)==service);
        CHECK(sample.state==core::State::IDLE);CHECK(result.menu.request==countdown::Service::NONE);
        CHECK_FALSE(result.lifecycle.gate.start_release);robot_test::zero(result);
        ui::Frame frame;CHECK(ui::render(sample,frame)==ui::RenderStatus::OK);
    }
}
TEST_CASE("B3 B14 D088 actual Robot retained preGO IMU availability expires at exact source age") {
    robot_test::Rig rig;rig.input.imu_ok=false;
    rig.input.imu={true,true,core::ImuPresence::VALID,core::ImuPresence::VALID,true,true,1000U,1000U,1U};
    rig.input.raw_heading_deg=12.0F;
    CHECK(rig.step(1000U).imu_available);
    rig.input.imu.gyro=rig.input.imu.accel=core::ImuPresence::ABSENT;
    rig.input.imu.heading_updated=false;
    rig.input.imu.checked_us=2000U;
    auto input=rig.at(2000U);auto result=rig.submit(input);
    CHECK(result.imu_available);CHECK_FALSE(result.heading.imu_ok);
    CHECK((ui::displaySample(input,result).faults&ui::IMU_UNAVAILABLE)==0U);
    rig.input.imu.checked_us=3000U;
    input=rig.at(3000U);result=rig.submit(input);
    CHECK(result.imu_available);
    rig.input.imu.checked_us=3001U;
    input=rig.at(3001U);result=rig.submit(input);
    CHECK_FALSE(result.imu_available);
    CHECK((ui::displaySample(input,result).faults&ui::IMU_UNAVAILABLE)!=0U);
}

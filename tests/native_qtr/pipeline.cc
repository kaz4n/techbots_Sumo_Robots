// Connects the actual native driver, qualifier and Robot with controlled GPIO data.
// Raw intervals pass unchanged through the real adapter into distinct source history.
// All sixteen patterns and a later provider fault exercise the complete software path.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/line_qtr_adapter.h"
using namespace fixture;
TEST_CASE("B2 B4 D085 actual native intervals qualify and reach Robot for all sixteen patterns") {
 for(unsigned white=0;white<16;++white)isolated([=]{reset();line_qtr::Reader reader;fsm::Robot robot;fsm::RobotInput input;input.initialization_complete=true;input.opponent_fresh=true;input.opp_raw_mask=0x78;input.vbat_v=11.1F;input.vbat_valid=true;
  REQUIRE(reader.begin(true)==line_qtr::Status::OK);REQUIRE(reader.start()==line_qtr::Status::OK);
  for(unsigned p=0;p<4;++p)hw.values[p]=(white&(1U<<p))?0:1;
  hw.now=reader.report().drive_completed_us+11;auto raw=reader.advance();
  if(!raw.valid){hw.now=1400;for(auto& v:hw.values)v=1;for(unsigned p=0;p<4;++p)if(white&(1U<<p))hw.values[p]=0;reader.advance();hw.now=1410;for(auto& v:hw.values)v=0;raw=reader.advance();}
  REQUIRE(raw.valid);input.t_us=1500;CHECK(line_qtr::applySnapshot(input,raw)==line_qtr::Qualification::VALID);CHECK(input.line.white_candidates==white);
  const auto first=robot.step(input);CHECK(first.contract_faults==0);CHECK(first.line_updated);CHECK(first.line_mask==white);CHECK(first.line_source_us==1000);CHECK(first.line_age_us==500);
  input.opp_raw_mask=0x79;input.t_us=2500;input.previous={true,first.token,1500,false,0,0,true,1500,0};CHECK(line_qtr::applySnapshot(input,reader.report())==line_qtr::Qualification::VALID);const auto retained=robot.step(input);CHECK(retained.contract_faults==0);CHECK_FALSE(retained.line_updated);CHECK(retained.line_mask==white);CHECK(retained.line_age_us==1500);
  hw.now=3000;REQUIRE(reader.start()==line_qtr::Status::OK);hw.now+=11;for(auto& v:hw.values)v=0;const auto second_raw=reader.advance();REQUIRE(second_raw.valid);input.t_us=3500;input.previous={true,retained.token,2500,false,0,0,true,2500,0};CHECK(line_qtr::applySnapshot(input,second_raw)==line_qtr::Qualification::VALID);const auto second=robot.step(input);CHECK(second.contract_faults==0);CHECK(second.line_updated);CHECK(second.line_sequence==2);CHECK(second.line_source_us==3000);CHECK(second.line_mask==15);CHECK(second.opponent_mask==1);
  hw.now=5000;REQUIRE(reader.start()==line_qtr::Status::OK);reader.cancel();CHECK(line_qtr::applySnapshot(input,reader.report())==line_qtr::Qualification::INVALID);input.t_us=5500;input.previous={true,second.token,3500,false,0,0,true,3500,0};const auto bad=robot.step(input);CHECK((bad.contract_faults&fsm::LINE_CONTRACT)!=0);CHECK_FALSE(bad.outputs.motors_enabled);CHECK(bad.outputs.duty_l==0);CHECK(bad.outputs.duty_r==0);
 });
}
TEST_CASE("B2 B4 D085 actual six-hundred-us observation gap is ambiguous rather than black") {
 isolated([]{reset();line_qtr::Reader reader;REQUIRE(reader.begin(true)==line_qtr::Status::OK);REQUIRE(reader.start()==line_qtr::Status::OK);for(auto& v:hw.values)v=1;hw.now+=11;reader.advance();hw.now+=600;for(auto& v:hw.values)v=0;const auto raw=reader.advance();REQUIRE(raw.valid);for(const auto& p:raw.pad){CHECK(p.lower_us==0);CHECK(p.upper_us==601);}fsm::RobotInput input;input.initialization_complete=true;input.opponent_fresh=true;input.opp_raw_mask=0x78;input.vbat_v=11.1F;input.vbat_valid=true;input.t_us=1700;CHECK(line_qtr::applySnapshot(input,raw)==line_qtr::Qualification::AMBIGUOUS);CHECK(input.line.contract_valid);fsm::Robot robot;const auto result=robot.step(input);CHECK((result.contract_faults&fsm::LINE_CONTRACT)!=0);CHECK_FALSE(result.outputs.motors_enabled);});
}
TEST_CASE("B2 B4 D085 actual native adapter Robot runtime uses no dynamic allocation") {
 isolated([]{reset();bool good=true;unsigned count=0;{AllocationGuard guard;line_qtr::Reader reader;fsm::Robot robot;fsm::RobotInput input;input.initialization_complete=true;input.opponent_fresh=true;input.opp_raw_mask=0x78;input.vbat_v=11.1F;input.vbat_valid=true;good&=reader.begin(true)==line_qtr::Status::OK;fsm::RobotResult previous;
  for(unsigned frame=0;frame<3;++frame){hw.now=1000+frame*2000;good&=reader.start()==line_qtr::Status::OK;hw.now+=11;const auto raw=reader.advance();good&=raw.valid;input.t_us=1500+frame*2000;if(frame)input.previous={true,previous.token,input.t_us-2000,false,0,0,true,input.t_us-2000,0};good&=line_qtr::applySnapshot(input,raw)==line_qtr::Qualification::VALID;previous=robot.step(input);good&=previous.contract_faults==0&&previous.line_updated;}
  for(unsigned replay=0;replay<10000;++replay){good&=line_qtr::applySnapshot(input,reader.report())==line_qtr::Qualification::VALID;good&=!robot.step(input).fresh;}
  count=hw.allocations;}CHECK(good);CHECK(count==0);});
}

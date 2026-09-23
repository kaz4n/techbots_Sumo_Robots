// Exercises actual Robot and Escape consumers with explicit D085 source evidence.
// Distinct QTR frames and fresh opponent observations have independent lifetimes.
// Public contract-derived cases preserve the established application receipt path.
#include "robot_scenario.h"
#include "config.h"
#include <cstdint>
#include <initializer_list>
namespace {
using Presence=core::LinePresence;
using Button=core::ButtonLevel;
class LineRig:public robot_test::Rig {
public:
 LineRig(){input.line.explicit_values=true;input.opponent_fresh=true;input.observations_fresh=false;}
 fsm::RobotResult fresh(std::uint32_t t,std::uint8_t white=0,Button button=Button::NONE,std::uint32_t age=100){
  input.line={true,true,Presence::VALID,++sequence,t-age,t-age+50U,white};return step(t,button);
 }
 fsm::RobotResult absent(std::uint32_t t,Button button=Button::NONE){input.line.presence=Presence::ABSENT;return step(t,button);}
 fsm::RobotResult sample(std::uint32_t t,std::uint8_t white=0,Button button=Button::NONE){
  if(sequence==0||static_cast<std::uint32_t>(t-input.line.started_us)>=2100)return fresh(t,white,button);
  return absent(t,button);
 }
 std::uint32_t release(){sample(1000);sample(22000);sample(24000,0,Button::START);sample(44000,0,Button::START);sample(46000);auto r=sample(66000);CHECK(r.lifecycle.gate.start_release);return 66000;}
 std::uint32_t sequence=0;
};
void fault(const fsm::RobotResult& r){CHECK((r.contract_faults&fsm::LINE_CONTRACT)!=0U);robot_test::zero(r);CHECK(r.outputs.ui_state==core::State::STOPPED);}
}
TEST_CASE("B2 B4 D085 explicit fresh line updates are independent from opponent freshness") {
 LineRig rig;auto r=rig.fresh(1000,1);CHECK(r.contract_faults==0);CHECK(r.line_available);CHECK(r.line_updated);CHECK(r.line_mask==1);CHECK(r.line_source_us==900);CHECK(r.line_age_us==100);
 rig.opponent(1);r=rig.absent(2000);CHECK(r.contract_faults==0);CHECK(r.line_mask==1);CHECK(r.line_available);CHECK_FALSE(r.line_updated);CHECK(r.line_age_us==1100);
 r=rig.absent(3000);CHECK(r.contract_faults==0);CHECK(r.opponent_mask==1);CHECK(r.line_sequence==1);
 rig.input.opponent_fresh=false;const auto stale=rig.fresh(4000);CHECK(stale.contract_faults!=0);robot_test::zero(stale);
}
TEST_CASE("B2 D085 source age expires at equality and cannot resurrect through timestamp wrap") {
 for(unsigned age:{5999U,6000U}){LineRig rig;rig.fresh(1000);const auto r=rig.absent(900+age);CHECK(r.line_available==(age<6000));if(age==6000)fault(r);else CHECK(r.contract_faults==0);}
 LineRig rig;rig.fresh(1000);fault(rig.absent(0x400003e8U));fault(rig.absent(0x800003e8U));fault(rig.absent(0xc00003e8U));fault(rig.absent(1001U));
}
TEST_CASE("B2 D085 preinitialization may wait without a line while initialized absence inhibits") {
 LineRig rig;rig.input.initialization_complete=false;auto r=rig.absent(1000);CHECK(r.contract_faults==0);CHECK(r.outputs.ui_state==core::State::BOOT);CHECK_FALSE(r.line_available);rig.input.initialization_complete=true;fault(rig.absent(2000));
 LineRig invalid;invalid.input.initialization_complete=false;invalid.input.line.presence=Presence::INVALID;fault(invalid.step(1000));
}
TEST_CASE("B2 D085 replay is retained and duplicate decisions ignore conflicting input without pulses") {
 LineRig rig;auto first=rig.fresh(1000,3);const auto evidence=rig.input.line;auto repeated=rig.step(2000);CHECK(repeated.contract_faults==0);CHECK(repeated.line_available);CHECK_FALSE(repeated.line_updated);CHECK(repeated.line_sequence==first.line_sequence);CHECK(repeated.line_age_us==1100);
 rig.input.line.white_candidates=0;auto duplicate=rig.step(2000);CHECK_FALSE(duplicate.fresh);CHECK_FALSE(duplicate.line_updated);CHECK(duplicate.line_mask==3);CHECK(duplicate.contract_faults==0);CHECK_FALSE(duplicate.frame_ready);CHECK(duplicate.events.count==0);
 rig.input.line=evidence;rig.input.line.white_candidates=2;fault(rig.step(3000));
}
TEST_CASE("B2 D085 mode is immutable until reset and unknown shapes latch a line contract fault") {
 for(unsigned p=0;p<256;++p){if(p==1||p==2)continue;LineRig r;r.input.line.presence=static_cast<Presence>(p);r.input.initialization_complete=false;fault(r.step(1000));}
 LineRig explicit_mode;explicit_mode.fresh(1000);explicit_mode.input.line.explicit_values=false;fault(explicit_mode.step(2000));
 robot_test::Rig legacy;legacy.step(1000);legacy.input.line.explicit_values=true;legacy.input.opponent_fresh=true;fault(legacy.step(2000));
 explicit_mode.reset();explicit_mode.input.observations_fresh=true;CHECK(explicit_mode.step(3000).contract_faults==0);
}
TEST_CASE("B2 D085 source identity order span spacing age and mask validate before replacing history") {
 for(unsigned kind=0;kind<16;++kind){LineRig r;r.fresh(1000,1);r.input.line={true,true,Presence::VALID,2,2900,2950,2};switch(kind){case 0:r.input.line.sequence=1;break;case 1:r.input.line.sequence=0;break;case 2:r.input.line.sequence=0x80000001U;break;case 3:r.input.line.started_us=900;break;case 4:r.input.line.started_us=899;break;case 5:r.input.line.started_us=2899;break;case 6:r.input.line.completed_us=2899;break;case 7:r.input.line.completed_us=5400;break;case 8:r.input.line.completed_us=3001;break;case 9:r.input.line.white_candidates=16;break;case 10:r.input.line.contract_valid=false;break;case 11:r.input.line.presence=Presence::INVALID;break;case 12:r.input.line.started_us=0x80000384U;break;case 13:r.input.line.started_us=950;r.input.line.completed_us=960;break;case 14:r.input.line.started_us=900;r.input.line.completed_us=950;r.input.line.sequence=2;break;case 15:r.input.line.started_us=900;r.input.line.completed_us=951;r.input.line.sequence=1;break;}auto result=r.step(3000);fault(result);CHECK(result.line_source_us==900);}
 for(unsigned age:{5999U,6000U}){LineRig r;const auto result=r.fresh(10000,0,Button::NONE,age);if(age==6000)fault(result);else CHECK(result.line_available);}
}
TEST_CASE("B2 D085 first arbitrary sequence and ordinary source sequence wrap remain admitted") {
 LineRig r;r.input.line={true,true,Presence::VALID,0xffffffffU,0xfffffff0U,0x22U,1};auto a=r.step(0x54U);CHECK(a.contract_faults==0);CHECK(a.line_age_us==100);r.input.line={true,true,Presence::VALID,0U,0x7c0U,0x7f2U,0};auto b=r.step(0x824U);CHECK(b.contract_faults==0);CHECK(b.line_updated);CHECK(b.line_sequence==0);CHECK(b.line_mask==0);
}
TEST_CASE("B3 B4 D085 countdown holds and GO uses qualified retained white") {
 LineRig rig;const auto anchor=rig.release();for(std::uint32_t elapsed=2000;elapsed<5098000;elapsed+=2000){const auto r=rig.fresh(anchor+elapsed);CHECK(r.contract_faults==0);robot_test::zero(r);}
 auto white=rig.fresh(anchor+5098000U,1);CHECK(white.contract_faults==0);robot_test::zero(white);const auto go=rig.absent(anchor+5100000U);CHECK(go.lifecycle.gate.go);CHECK(go.outputs.ui_state==core::State::EDGE_ESCAPE);CHECK(go.line_available);CHECK_FALSE(go.line_updated);CHECK(go.line_mask==1);
}
TEST_CASE("B4 D085 retained entry seeds baseline and identical next white cannot replan") {
 edge::Escape e;edge::EscapeSample s;s.t_us=1000;s.line_mask=1;s.motion_permitted=true;s.line_updated=false;const auto first=e.step(s);CHECK(first.entered);CHECK(first.replans==0);s.t_us=2000;s.line_updated=true;const auto next=e.step(s);CHECK_FALSE(next.replanned);CHECK(next.replans==0);CHECK(next.row.phase==edge::ScriptPhase::BACK);
}
TEST_CASE("B4 D085 retained levels advance phases without consuming replan or all-black exit") {
 edge::Escape e;edge::EscapeSample s;s.t_us=0;s.line_mask=4;s.motion_permitted=true;CHECK(e.step(s).entered);s.line_updated=false;s.t_us=200000;auto done=e.step(s);CHECK(done.row.phase==edge::ScriptPhase::DONE);CHECK_FALSE(done.replanned);CHECK(done.replans==0);CHECK(done.escape_required);
 s.t_us=201000;s.line_mask=0;auto retained=e.step(s);CHECK_FALSE(retained.exited);CHECK(retained.escape_required);s.t_us=202000;s.line_updated=true;auto fresh=e.step(s);CHECK(fresh.exited);CHECK_FALSE(fresh.escape_required);
}
TEST_CASE("B4 D085 fresh black on the exact DONE decision exits without an extra frame") {
 edge::Escape e;edge::EscapeSample s;s.line_mask=4;s.motion_permitted=true;e.step(s);s.t_us=200000;s.line_mask=0;s.line_updated=true;const auto exit=e.step(s);CHECK(exit.exited);CHECK_FALSE(exit.escape_required);
}
TEST_CASE("B4 D085 retained fault masks preserve priority and cached clear never replaces baseline") {
 edge::Escape e;edge::EscapeSample s;s.line_mask=1;s.motion_permitted=true;e.step(s);s.t_us=1;s.line_mask=0;s.line_updated=false;CHECK_FALSE(e.step(s).replanned);s.t_us=2;s.line_mask=1;s.line_updated=true;CHECK_FALSE(e.step(s).replanned);s.t_us=3;s.line_mask=15;s.line_updated=false;const auto bad=e.step(s);CHECK(bad.fault==edge::EscapeFault::WHITE_PATTERN);CHECK(bad.inhibit_motion);
}
TEST_CASE("B3 D085 countdown warning requires fresh source and delivery inside final window") {
 for(unsigned kind=0;kind<4;++kind){LineRig rig;const auto anchor=rig.release();rig.fresh(anchor+4096000U);const auto decision=anchor+4101000U;const auto age=kind==0?2000U:100U;rig.input.line={true,true,Presence::VALID,++rig.sequence,decision-age,decision-age+50,1};if(kind==2)rig.input.line.presence=Presence::ABSENT;if(kind==3)rig.input.line.white_candidates=0;const auto result=rig.step(decision);CHECK(result.contract_faults==0);CHECK(result.lifecycle.services.line_warning==(kind==1));robot_test::zero(result);}
 countdown::Services service;const bool started=service.start(1000,0);CHECK(started);if(!started)return;countdown::ServiceSample sample;sample.explicit_line=true;sample.line_updated=true;sample.line_mask=1;sample.t_us=5101000;sample.line_source_us=5100999;CHECK_FALSE(service.step(sample).line_warning);
}
TEST_CASE("B4 D085 configurable confirmation consumes distinct frames and resets across BOOT expiry") {
 for(bool silent_gap:{false,true}){LineRig rig;rig.input.initialization_complete=false;rig.opponent(1);std::uint32_t t=1000;
  for(unsigned count=1;count<config::QTR_CONFIRM_TICKS;++count){const auto fresh=rig.fresh(t,1);CHECK(fresh.line_mask==0);const auto replay=rig.step(t+500);CHECK_FALSE(replay.line_updated);CHECK(replay.line_mask==0);CHECK(rig.absent(t+1000).line_mask==0);t+=2000;}
  if(config::QTR_CONFIRM_TICKS>1){t+=6000;if(!silent_gap){const auto absent=rig.absent(t-1000);CHECK(absent.contract_faults==0);CHECK_FALSE(absent.line_available);}}
  for(unsigned count=1;count<=config::QTR_CONFIRM_TICKS;++count){const auto fresh=rig.fresh(t,1);CHECK(fresh.contract_faults==0);CHECK(fresh.line_mask==(count==config::QTR_CONFIRM_TICKS?1:0));t+=2000;}
 }
}
TEST_CASE("B14 D085 expired or invalid line evidence cannot sustain pivot stuck qualification") {
 for(bool fresh_after_gap:{false,true}){LineRig rig;const auto anchor=rig.release();rig.fresh(anchor+5098000U,5);const auto go=rig.absent(anchor+5100000U);CHECK(go.lifecycle.gate.go);CHECK(go.outputs.ui_state==core::State::EDGE_ESCAPE);if(!go.lifecycle.gate.go||go.outputs.ui_state!=core::State::EDGE_ESCAPE)return;const auto pivot=anchor+5150000U;const auto first=rig.fresh(pivot,5);CHECK(first.outputs.duty_l>0);CHECK(first.outputs.duty_r<0);if(first.outputs.duty_l<=0||first.outputs.duty_r>=0)return;CHECK(first.qtr_warning_mask==0);const auto result=fresh_after_gap?rig.fresh(pivot+1500001U,5):rig.absent(pivot+1500001U);CHECK(result.qtr_warning_mask==0);CHECK(robot_test::count(result,core::Event::FAULT,3)==0);if(!fresh_after_gap)fault(result);}
}

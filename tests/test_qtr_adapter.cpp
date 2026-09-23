// Validates native interval qualification against D085's frozen evidence contract.
// Ambiguity and malformed timing cannot silently become measured black.
// Independent synthetic public records test each endpoint and structural boundary.
#include "doctest.h"
#include "hal/line_qtr_adapter.h"
#include <cstdint>
#include <initializer_list>
namespace {
line_qtr::Snapshot complete(std::uint8_t white=15U,std::uint32_t base=1000U) {
 line_qtr::Snapshot s;s.phase=line_qtr::Phase::COMPLETE;s.status=line_qtr::Status::OK;s.valid=true;
 s.sequence=7;s.started_us=base;s.drive_completed_us=base+3;s.advances=2;s.released_mask=15;s.low_mask=15;
 for(unsigned p=0;p<4;++p){auto& a=s.pad[p];a.release_before_us=base+14+p*2;a.release_after_us=a.release_before_us+1;
  if(white&(1U<<p)){a.first_low_after_us=a.release_before_us+299;a.upper_us=300;}
  else {s.high_mask|=1U<<p;a.last_high_before_us=a.release_after_us+301;a.lower_us=300;a.first_low_after_us=a.last_high_before_us+2;a.upper_us=a.first_low_after_us-a.release_before_us+1;}
 }
 s.cleanup.attempted_mask=15;s.cleanup.started_us=base+400;s.cleanup.completed_us=base+404;
 s.completed_us=s.checked_us=base+404;return s;
}
fsm::RobotInput sentinel(){fsm::RobotInput in;in.t_us=7777;in.initialization_complete=true;in.observations_fresh=true;in.opponent_fresh=true;in.opp_raw_mask=0x65;in.raw_heading_deg=42;in.raw_gyro_z_dps=7;in.imu_ok=true;in.ax_g=2;in.ay_g=-1;in.vbat_v=11.1F;in.vbat_valid=true;in.stop_requested=true;in.button=core::ButtonLevel::BOTH;in.previous.token=99;in.previous.applied_us=500;for(unsigned p=0;p<4;++p)in.line_raw_us[p]=123+p;return in;}
void unchanged(const fsm::RobotInput& in){CHECK(in.t_us==7777);CHECK(in.initialization_complete);CHECK(in.observations_fresh);CHECK(in.opponent_fresh);CHECK(in.opp_raw_mask==0x65);CHECK(in.raw_heading_deg==42);CHECK(in.raw_gyro_z_dps==7);CHECK(in.imu_ok);CHECK(in.ax_g==2);CHECK(in.ay_g==-1);CHECK(in.vbat_v==11.1F);CHECK(in.vbat_valid);CHECK(in.stop_requested);CHECK(in.button==core::ButtonLevel::BOTH);CHECK(in.previous.token==99);CHECK(in.previous.applied_us==500);for(unsigned p=0;p<4;++p)CHECK(in.line_raw_us[p]==123+p);}
void invalid(const line_qtr::Snapshot& s){auto in=sentinel();CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::INVALID);CHECK(in.line.explicit_values);CHECK_FALSE(in.line.contract_valid);CHECK(in.line.presence==core::LinePresence::INVALID);unchanged(in);}
}
TEST_CASE("B2 B4 D085 adapter all sixteen qualified patterns preserve unrelated controller inputs") {
 for(unsigned mask=0;mask<16;++mask){auto in=sentinel();const auto s=complete(mask);CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::VALID);CHECK(in.line.explicit_values);CHECK(in.line.contract_valid);CHECK(in.line.presence==core::LinePresence::VALID);CHECK(in.line.white_candidates==mask);CHECK(in.line.sequence==s.sequence);CHECK(in.line.started_us==s.started_us);CHECK(in.line.completed_us==s.completed_us);unchanged(in);}
}
TEST_CASE("B2 B4 D085 adapter closed lower exclusive upper threshold endpoints and ambiguity") {
 for(unsigned p=0;p<4;++p){auto s=complete();++s.pad[p].first_low_after_us;++s.pad[p].upper_us;auto in=sentinel();CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::AMBIGUOUS);CHECK(in.line.contract_valid);CHECK(in.line.presence==core::LinePresence::INVALID);unchanged(in);
  s=complete(0);--s.pad[p].last_high_before_us;--s.pad[p].lower_us;CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::AMBIGUOUS);CHECK(in.line.contract_valid);
 }
}
TEST_CASE("B2 D085 adapter censored timeouts preserve actual qualified lower bounds") {
 auto s=complete(0);s.low_mask=0;s.timeout_mask=s.high_mask=15;
 for(auto& a:s.pad){a.last_high_before_us=a.release_after_us+1501;a.lower_us=1500;a.first_low_after_us=0;a.upper_us=0;}
 s.cleanup.started_us=s.started_us+1600;s.completed_us=s.checked_us=s.cleanup.completed_us=s.started_us+1604;
 fsm::RobotInput in;CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::VALID);CHECK(in.line.white_candidates==0);
 for(unsigned p=0;p<4;++p){auto bad=s;--bad.pad[p].lower_us;--bad.pad[p].last_high_before_us;invalid(bad);bad=s;bad.pad[p].upper_us=1501;invalid(bad);bad=s;bad.pad[p].first_low_after_us=42;invalid(bad);}
}
TEST_CASE("B2 D085 adapter rejects unknown phases statuses masks and inconsistent complete metadata") {
 for(unsigned code=6;code<256;++code){auto s=complete();s.phase=static_cast<line_qtr::Phase>(code);invalid(s);}
 for(unsigned code=1;code<256;++code){auto s=complete();s.status=static_cast<line_qtr::Status>(code);invalid(s);}
 for(unsigned kind=0;kind<21;++kind){auto s=complete();switch(kind){case 0:s.valid=false;break;case 1:s.released_mask=7;break;case 2:s.released_mask=31;break;case 3:s.high_mask=16;break;case 4:s.low_mask=31;break;case 5:s.timeout_mask=1;break;case 6:s.low_mask=14;break;case 7:s.cleanup.attempted_mask=14;break;case 8:s.cleanup.failed_mask=1;break;case 9:s.cleanup.skipped_mask=2;break;case 10:s.cleanup.nonneutral_mask=4;break;case 11:s.cleanup.deadline_exceeded=true;break;case 12:s.cleanup.status[3]=-1;break;case 13:s.advances=0;break;case 14:s.advances=8193;break;case 15:--s.checked_us;break;case 16:--s.cleanup.completed_us;break;case 17:s.cleanup.started_us=s.completed_us-100;break;case 18:s.completed_us=s.checked_us=s.cleanup.completed_us=s.started_us+2500;break;case 19:s.drive_completed_us=s.started_us-1;break;case 20:s.cleanup.started_us=s.started_us+100;break;}invalid(s);}
}
TEST_CASE("B2 D085 adapter validates every release observation ordering and bound derivation") {
 for(unsigned p=0;p<4;++p)for(unsigned kind=0;kind<12;++kind){auto s=complete();auto& a=s.pad[p];switch(kind){case 0:a.release_before_us=s.drive_completed_us+10;break;case 1:a.release_before_us=s.drive_completed_us+100;break;case 2:a.release_after_us=a.release_before_us-1;break;case 3:a.release_after_us=s.completed_us+1;break;case 4:a.first_low_after_us=a.release_before_us-1;break;case 5:a.first_low_after_us=s.completed_us+1;break;case 6:++a.lower_us;break;case 7:++a.upper_us;break;case 8:a.last_high_before_us=1;break;case 9:s.status_by_pad[p]=-2;break;case 10:s.status_by_pad[p]=2;break;case 11:a.upper_us=0;break;}invalid(s);}
 for(unsigned p=0;p<4;++p){auto s=complete(0);s.pad[p].last_high_before_us=s.pad[p].first_low_after_us+1;invalid(s);}
}
TEST_CASE("B2 D085 adapter accepts modulo wrap and rejects half-range time inversions") {
 auto s=complete(5,0xfffffff0U);fsm::RobotInput in;CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::VALID);CHECK(in.line.started_us==0xfffffff0U);CHECK(in.line.white_candidates==5);
 s=complete();s.pad[0].first_low_after_us+=0x80000000U;invalid(s);
}
TEST_CASE("B2 D085 adapter pending is absent only for structurally valid records") {
 for(auto phase:{line_qtr::Phase::NOT_STARTED,line_qtr::Phase::IDLE,line_qtr::Phase::CHARGING,line_qtr::Phase::DISCHARGING}){line_qtr::Snapshot s;s.phase=phase;if(phase!=line_qtr::Phase::NOT_STARTED)s.status=line_qtr::Status::OK;if(phase==line_qtr::Phase::CHARGING||phase==line_qtr::Phase::DISCHARGING){s.sequence=1;s.started_us=1000;s.drive_completed_us=1003;s.checked_us=1004;if(phase==line_qtr::Phase::DISCHARGING){s.released_mask=s.high_mask=15;s.advances=1;s.checked_us=1024;for(unsigned p=0;p<4;++p){s.pad[p].release_before_us=1014+p*2;s.pad[p].release_after_us=1015+p*2;s.pad[p].last_high_before_us=1023;s.pad[p].lower_us=1023-s.pad[p].release_after_us-1;s.status_by_pad[p]=1;}}}auto in=sentinel();CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::ABSENT);CHECK(in.line.presence==core::LinePresence::ABSENT);CHECK(in.line.contract_valid);unchanged(in);auto bad=s;bad.valid=true;invalid(bad);bad=s;bad.cleanup.attempted_mask=1;invalid(bad);bad=s;bad.completed_us=1;invalid(bad);}
 line_qtr::Snapshot s;s.phase=line_qtr::Phase::FAULT;s.status=line_qtr::Status::CANCELLED;fsm::RobotInput in;CHECK(line_qtr::applySnapshot(in,s)==line_qtr::Qualification::INVALID);CHECK(in.line.contract_valid);CHECK(in.line.presence==core::LinePresence::INVALID);s.status=line_qtr::Status::BUSY;invalid(s);
}

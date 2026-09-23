// Worker smoke uses actual production Robot, MotorGate and recorder.
// Scripted native callbacks expose timing and single-pass terminal inhibition.
// Independent contract suites provide the broader acceptance matrix.
#include "app/transaction.h"
#include <cassert>
#include <cstdio>
struct Fake {
 unsigned writes=0,clocks=0,settles=0;std::uint32_t now=0;bool fail_write=false;
 static bool configure(void* c){++static_cast<Fake*>(c)->writes;return true;}
 static bool pwmConfigure(void* c,motors::Channel){return configure(c);}
 static bool enable(void* c,bool high){auto& f=*static_cast<Fake*>(c);++f.writes;assert(!high);return !f.fail_write;}
 static bool pwm(void* c,motors::Channel,std::uint32_t,std::uint32_t pulse){assert(pulse==0);return configure(c);}
 static bool settle(void* c){++static_cast<Fake*>(c)->settles;return true;}
 static std::uint32_t clock(void* c){auto& f=*static_cast<Fake*>(c);++f.clocks;return f.now;}
 motors::Port port(){return {this,configure,pwmConfigure,enable,pwm,settle,clock,{1000,1000,1000,1000}};}
};
static void closedAndAbort(){
 Fake f;app::Transaction tx(f.port());assert(f.writes==0&&f.clocks==0);assert(tx.initialize());auto writes=f.writes;assert(tx.initialize()&&f.writes==writes&&f.clocks==0);
 f.now=100;assert(tx.open());fsm::RobotInput input;input.t_us=0xdeadbeef;input.previous.applied_valid=true;input.previous.token=555;input.timing={false,false,77};
 f.now=200;assert(tx.decide(input));assert(tx.report().robot.token==1&&tx.report().decision_us==200&&tx.report().applied.feedback.applied_us==200);f.now=250;assert(tx.finish());assert(tx.previous().duration_valid&&tx.previous().execution_us==150&&tx.previous().completed_us==250);
 f.now=300;assert(tx.open());f.now=400;assert(tx.decide(input));assert(tx.report().robot.token==2&&tx.report().robot.contract_faults==0);f.now=450;assert(tx.finish());
 auto saved=tx.previous();writes=f.writes;auto settles=f.settles;tx.abort();assert(tx.report().fault==app::Fault::ABORTED&&tx.report().halt.attempted);assert(f.writes==writes+5&&f.settles==settles+1);assert(!tx.previous().applied_valid&&!tx.previous().duration_valid);assert(tx.previous().token==saved.token&&tx.previous().applied_us==saved.applied_us);
 writes=f.writes;auto clocks=f.clocks;tx.abort();assert(!tx.initialize()&&!tx.open()&&!tx.decide(input)&&!tx.finish());assert(f.writes==writes&&f.clocks==clocks);
}
static void duplicateDecision(){
 Fake f;app::Transaction tx(f.port());assert(tx.initialize());assert(tx.open()&&tx.decide({})&&tx.finish());assert(tx.open());auto writes=f.writes;assert(!tx.decide({}));assert(tx.report().fault==app::Fault::CLOCK&&f.writes==writes+5);assert(!tx.report().decision_made);
}
static void receiptAndClock(){
 for(unsigned k=0;k<4;++k){Fake f;app::Transaction tx(f.port());assert(tx.initialize());f.now=k==3?0xfffffff0U:100;assert(tx.open());f.now=k==3?0xfffffff8U:110;assert(tx.decide({}));
  if(k==0){f.now=0x80000064U;assert(!tx.finish()&&tx.report().fault==app::Fault::CLOCK);}
  if(k==1){f.now=109;assert(!tx.finish()&&tx.report().fault==app::Fault::CLOCK);}
  if(k==2){f.now=120;assert(tx.finish());f.now=119;assert(!tx.open()&&tx.report().fault==app::Fault::CLOCK);}
  if(k==3){f.now=10;assert(tx.finish()&&tx.previous().execution_us==26);}
 }
}
static void beforeSetup(){
 Fake f;app::Transaction tx(f.port());assert(!tx.open());assert(tx.report().fault==app::Fault::ORDER&&tx.report().halt.fault==motors::Fault::NOT_INITIALIZED);assert(f.clocks==0&&f.writes==0&&!tx.initialize());
 Fake bad;auto p=bad.port();p.clockUs=nullptr;app::Transaction failed(p);assert(!failed.initialize()&&failed.report().fault==app::Fault::SETUP);assert(bad.writes==0&&bad.clocks==0);failed.abort();assert(bad.writes==0);
}
int main(){closedAndAbort();duplicateDecision();receiptAndClock();beforeSetup();std::puts("actual transaction worker smoke PASS");}

// Tests adopted D117 public setup, cleanup and bounded transmit oracles.
// Controlled hardware faults occur at observed external boundaries, without owner seeding.
// Each named subprocess has a fresh actual native singleton and immutable constructor mode.
#include "fixture.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <type_traits>

namespace fifo_test {
SetupGrant grants(){return {true,true,true,true};}
bool start(UnoQDumpPort& owner) {
    const auto status=owner.begin(grants());VERIFY(status==NativeStatus::OK);
    VERIFY(owner.status()==status);hw.setup=false;return status==NativeStatus::OK;
}
std::vector<unsigned char> packet(const std::string& data) {
    std::vector<unsigned char> result{0x93,0x02,0xa9,'m','o','n','/','w','r','i','t','e',0x91,0xd9};
    result.push_back(static_cast<unsigned char>(data.size()));result.insert(result.end(),data.begin(),data.end());return result;
}
WriteResult send(UnoQDumpPort& owner,const std::string& data) {
    const auto p=owner.port();const auto before=hw.submitted.size();const auto mask=hw.mask;
    const auto clocks=hw.clocks;hw.call_started=static_cast<std::uint32_t>(hw.now);hw.enforce_budget=true;
    const auto result=p.write(p.context,data.data(),data.size());hw.enforce_budget=false;
    VERIFY(hw.submitted.size()-before<=8);VERIFY(hw.mask==mask);VERIFY(hw.clocks-clocks<=64);
    VERIFY(hw.overflow==0);VERIFY(hw.rdr_reads==0);VERIFY(hw.forbidden_writes==0);
    if(result.status!=WriteStatus::PROGRESS)VERIFY(result.count==0);
    return result;
}
void terminal(UnoQDumpPort& owner) {
    const auto init=hw.init,configure=hw.configure;const auto before=hw.submitted.size();
    for(unsigned i=0;i<3;++i) {
        VERIFY(!owner.ready());VERIFY(send(owner,"x").status==WriteStatus::ERROR);
        VERIFY(owner.begin(grants())!=NativeStatus::OK);
    }
    VERIFY(hw.init==init&&hw.configure==configure);VERIFY(hw.submitted.size()==before);
}
void passive() {
    static_assert(static_cast<unsigned>(Buffering::LEGACY_SINGLE)==0);
    static_assert(static_cast<unsigned>(Buffering::FIFO8)==1);
    UnoQDumpPort a,b(Buffering::FIFO8),c(static_cast<Buffering>(255));
    for(auto* p:{&a,&b,&c}) {
        VERIFY(p->status()==NativeStatus::NOT_INITIALIZED);
        const auto port=p->port();const auto wrapped=app::unoQDumpPort(*p);
        VERIFY(port.context==p&&wrapped.context==p&&wrapped.output.context==p);
        VERIFY(port.write&&port.cancel&&wrapped.begin&&wrapped.ready&&wrapped.output.write&&wrapped.output.cancel);
    }
    VERIFY(hw.clocks==0&&hw.init==0&&hw.configure==0&&hw.ready_calls==0);
    VERIFY(hw.reads==0&&hw.writes==0&&hw.context_queries==0);
}
void admission(unsigned mode,unsigned bits,unsigned context) {
    UnoQDumpPort owner(static_cast<Buffering>(mode));
    SetupGrant g{bool(bits&1),bool(bits&2),bool(bits&4),bool(bits&8)};
    if(context==1)hw.control=1;
    if(context==2)hw.ipsr=16;
    const auto status=owner.begin(g);
    const auto expected=mode>1?NativeStatus::INVALID_ARGUMENT:bits!=15?NativeStatus::OWNERSHIP:NativeStatus::CONTEXT;
    VERIFY(status==expected);VERIFY(owner.status()==status);VERIFY(hw.writes==0&&hw.init==0&&hw.configure==0);
    if(mode>1||bits!=15)VERIFY(hw.context_queries==0&&hw.reads==0&&hw.clocks==0);
    terminal(owner);
}
void setup(unsigned mask,unsigned low) {
    hw.mask=mask;hw.ready=low?0:1;UnoQDumpPort owner(Buffering::FIFO8);
    if(!start(owner))return;
    const std::array<std::uint32_t,3> values{{0,USART_CR1_TE|USART_CR1_FIFOEN,
        USART_CR1_UE|USART_CR1_TE|USART_CR1_FIFOEN}};
    VERIFY(hw.trace.size()==9);VERIFY(hw.cr1_writes==3);
    for(unsigned i=0;i<3&&hw.trace.size()>=9;++i) {
        VERIFY(hw.trace[3*i].kind=='W'&&hw.trace[3*i].value==values[i]);
        VERIFY(hw.trace[3*i+1].kind=='B');VERIFY(hw.trace[3*i+2].kind=='R'&&hw.trace[3*i+2].value==values[i]);
    }
    VERIFY(hw.mask==mask);VERIFY(hw.disabled==1&&hw.cleared==1);VERIFY(hw.init==1);
    VERIFY(!metadata.fifo_enable);VERIFY(hw.submitted.empty());VERIFY(hw.forbidden_writes==0);
    VERIFY(owner.ready()==!bool(low));VERIFY(hw.mask==mask);
    UnoQDumpPort other(Buffering::FIFO8);const auto writes=hw.writes;
    VERIFY(other.begin(grants())==NativeStatus::OWNERSHIP);VERIFY(hw.writes==writes&&hw.init==1);
}
void initial(unsigned kind) {
    UnoQDumpPort owner(Buffering::FIFO8);NativeStatus expected=NativeStatus::REGISTER;
    if(kind==0){metadata.fifo_enable=true;expected=NativeStatus::DEVICE;}
    if(kind==1){hw.post_init_fault=1;expected=NativeStatus::OWNERSHIP;}
    if(kind==2)LPUART1->AUTOCR.value=1;
    if(kind==3)LPUART1->AUTOCR.value=1U<<31;
    if(kind==4)LPUART1->CR1.value|=USART_CR1_FIFOEN;
    if(kind==5)LPUART1->BRR.value=355555;
    if(kind==6)LPUART1->PRESC.value=1;
    const auto status=owner.begin(grants());
    if(kind<4)VERIFY(status==expected);else VERIFY(status!=NativeStatus::OK);
    VERIFY(owner.status()==status);VERIFY(hw.cr1_writes==0&&hw.submitted.empty());
    VERIFY(hw.forbidden_writes==0);terminal(owner);
}
void legacyAutocr(unsigned value) {
    LPUART1->AUTOCR.value=value;UnoQDumpPort owner;if(!start(owner))return;
    VERIFY(LPUART1->CR1.value==(USART_CR1_UE|USART_CR1_TE));
    VERIFY(LPUART1->AUTOCR.value==value);VERIFY(owner.ready());
    WriteResult result;
    for(unsigned i=0;i<25;++i) {
        moveTime(hw.now+1000);result=send(owner,"x");
        if(result.status!=WriteStatus::PENDING)break;
    }
    VERIFY(result.status==WriteStatus::PROGRESS&&result.count==1);
    VERIFY(hw.emitted==packet("x"));VERIFY(LPUART1->AUTOCR.value==value);
}
void partial(unsigned stage,unsigned fault,bool cleanup_failure,unsigned mask) {
    hw.target_stage=stage;hw.fault_kind=fault;hw.cleanup_corrupt=cleanup_failure;hw.mask=mask;
    UnoQDumpPort owner(Buffering::FIFO8);const auto status=owner.begin(grants());
    const auto expected=fault==4?NativeStatus::CONTEXT:fault==5?NativeStatus::DEVICE:
        (fault==6||fault==7)?NativeStatus::OWNERSHIP:fault==9?NativeStatus::READY_ERROR:NativeStatus::REGISTER;
    VERIFY(status==expected);VERIFY(owner.status()==status);VERIFY(hw.fault_fired);VERIFY(hw.mask==mask);
    const bool cleanup=fault==0||fault==2||fault==9;
    VERIFY(hw.cr1_writes==stage+(cleanup?1:0));VERIFY(hw.submitted.empty());
    VERIFY(hw.forbidden_writes==0);VERIFY(hw.trace.size()==3*hw.cr1_writes);
    if(cleanup)VERIFY(hw.trace[3*stage].kind=='W'&&hw.trace[3*stage].value==0);
    if(cleanup&&!cleanup_failure)VERIFY(LPUART1->CR1.value==0);
    if(cleanup_failure)VERIFY(LPUART1->CR1.value==0x40000000U);
    const auto writes=hw.cr1_writes;terminal(owner);VERIFY(hw.cr1_writes==writes);
}
void model(unsigned size,bool wrap) {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    if(wrap)moveTime(0xfffffff0ULL);
    std::string data(size,'A');data.back()='\n';WriteResult result;unsigned calls=0;
    do {moveTime(hw.now+1000);result=send(owner,data);++calls;}while(result.status==WriteStatus::PENDING&&calls<20);
    VERIFY(result.status==WriteStatus::PROGRESS&&result.count==size);
    VERIFY(hw.submitted==packet(data));VERIFY(hw.emitted==packet(data));VERIFY(!hw.shifting&&hw.count==0);
    VERIFY(calls==(size+15+7)/8+1);VERIFY(hw.max_queue<=8);VERIFY(hw.overflow==0);
}
void fullFifo() {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    hw.frozen_serial=true;std::string data(64,'x');VERIFY(send(owner,data).status==WriteStatus::PENDING);
    VERIFY(hw.submitted.size()==8&&hw.count==7&&hw.shifting);
    VERIFY(send(owner,data).status==WriteStatus::PENDING);VERIFY(hw.submitted.size()==9&&hw.count==8);
    const auto before=hw.submitted.size();VERIFY(send(owner,data).status==WriteStatus::PENDING);
    VERIFY(hw.submitted.size()==before);VERIFY(!(LPUART1->ISR.value&USART_ISR_TXE));
    VERIFY(hw.emitted.empty());hw.frozen_serial=false;WriteResult result;
    for(unsigned i=0;i<20;++i){moveTime(hw.now+1000);result=send(owner,data);if(result.status!=WriteStatus::PENDING)break;}
    VERIFY(result.status==WriteStatus::PROGRESS);VERIFY(hw.emitted==packet(data));
}
void tcOnly() {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    const std::string data="x";VERIFY(send(owner,data).status==WriteStatus::PENDING);
    moveTime(hw.now+1000);VERIFY(send(owner,data).status==WriteStatus::PENDING);
    VERIFY(hw.submitted.size()==16);VERIFY(hw.emitted.size()==8);VERIFY(!hw.count?hw.shifting:true);
    moveTime(hw.now+694);VERIFY(send(owner,data).status==WriteStatus::PENDING);
    VERIFY(hw.emitted.size()==15);VERIFY(hw.count==0&&hw.shifting);
    moveTime(hw.now+1);const auto result=send(owner,data);
    VERIFY(result.status==WriteStatus::PROGRESS&&result.count==1);VERIFY(hw.emitted==packet(data));
}
void timeout(unsigned age,bool wrap) {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    if(wrap)moveTime(0xfffffff0ULL);
    hw.frozen_serial=true;const auto start_time=hw.now;VERIFY(send(owner,"abc").status==WriteStatus::PENDING);
    moveTime(start_time+age);const auto result=send(owner,"abc");
    VERIFY(result.status==(age<100000?WriteStatus::PENDING:WriteStatus::ERROR));
    if(age>=100000){VERIFY(owner.status()==NativeStatus::TIMEOUT);terminal(owner);}
}
void budget(unsigned cost) {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    hw.step=cost;const auto result=send(owner,std::string(64,'a'));
    VERIFY(result.count==0);VERIFY(hw.submitted.size()<=8);
    if(cost>=80)VERIFY(hw.submitted.empty());
}
void live(unsigned kind,unsigned after) {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    if(after){hw.live_kind=kind;hw.live_after_tdr=after;}else corrupt(kind);
    const auto writes=hw.cr1_writes;const auto result=send(owner,std::string(64,'a'));
    VERIFY(result.status==WriteStatus::ERROR&&result.count==0);VERIFY(hw.submitted.size()==after);
    if(kind==5||kind==6)VERIFY(owner.status()==NativeStatus::REGISTER);
    if(kind!=9&&kind!=10)VERIFY(hw.cr1_writes==writes);
    VERIFY(hw.forbidden_writes==0);terminal(owner);
}
void cancel(unsigned foreign) {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    VERIFY(send(owner,std::string(64,'x')).status==WriteStatus::PENDING);
    moveTime(hw.now+100);VERIFY(hw.emitted.size()==1);const auto prior=hw.emitted;
    if(foreign)corrupt(foreign==1?0:5);
    const auto count=hw.cr1_writes;const auto p=owner.port();p.cancel(p.context);
    VERIFY(owner.status()==NativeStatus::POISONED);VERIFY(hw.cr1_writes==count+(foreign?0:1));
    if(!foreign){VERIFY(LPUART1->CR1.value==0);VERIFY(!hw.shifting&&!hw.count);moveTime(hw.now+10000);VERIFY(hw.emitted==prior);}
    terminal(owner);
}
void identity(unsigned kind) {
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    const std::string original="abc\n";VERIFY(send(owner,original).status==WriteStatus::PENDING);
    const auto before=hw.submitted.size();const auto p=owner.port();WriteResult result;
    if(kind==0)result=send(owner,"abd\n");
    else if(kind==1)result=send(owner,"abc");
    else if(kind==2)result=p.write(p.context,nullptr,1);
    else if(kind==3)result=send(owner,std::string(65,'x'));
    else result=send(owner,std::string("a\0b",3));
    VERIFY(result.status==WriteStatus::ERROR&&result.count==0);VERIFY(hw.submitted.size()==before);terminal(owner);
}
}
int main(int argc,char** argv) {
    using namespace fifo_test;initialize();const std::string name=argc>1?argv[1]:"passive";
    const auto arg=[&](int n){return argc>n?unsigned(std::strtoul(argv[n],nullptr,10)):0U;};
    if(name=="passive")passive();
    else if(name=="admission")admission(arg(2),arg(3),arg(4));
    else if(name=="setup")setup(arg(2),arg(3));
    else if(name=="initial")initial(arg(2));
    else if(name=="legacy_autocr")legacyAutocr(arg(2));
    else if(name=="partial")partial(arg(2),arg(3),arg(4),arg(5));
    else if(name=="model")model(arg(2),arg(3));
    else if(name=="full")fullFifo();
    else if(name=="tc")tcOnly();
    else if(name=="timeout")timeout(arg(2),arg(3));
    else if(name=="budget")budget(arg(2));
    else if(name=="live")live(arg(2),arg(3));
    else if(name=="cancel")cancel(arg(2));
    else if(name=="identity")identity(arg(2));
    else if(name=="replay"&&argc==4)replay(argv[2],argv[3]);
    else if(name=="capacity"&&argc==3)capacity(argv[2]);
    else return 2;
    std::printf("checks=%u failures=%u submitted=%zu emitted=%zu queue_max=%u\n",checks,failures,
                hw.submitted.size(),hw.emitted.size(),hw.max_queue);
    return failures?1:0;
}

// Replays full D116 bytes and stress-tests every raw formatter capacity slot.
// Real native FIFO execution is separate from the conservative effective-call model.
// Arbitrary raw stress rows never claim valid Robot semantics or receiver acceptance.
#include "fixture.h"
#include "hal/recorder_csv.h"
#include <algorithm>
#include <cstring>
#include <fstream>
#include <iterator>

namespace fifo_test {
std::uint32_t crc(const std::string& text) {
    std::uint32_t value=0xffffffffU;
    for(unsigned char c:text){value^=c;for(unsigned i=0;i<8;++i)value=(value>>1)^((value&1)?0xedb88320U:0U);}
    return value^0xffffffffU;
}
void writeFile(const std::string& path,const void* data,std::size_t size) {
    std::ofstream output(path,std::ios::binary);output.write(static_cast<const char*>(data),size);VERIFY(output.good());
}
unsigned sendStream(UnoQDumpPort& owner,const std::string& text) {
    unsigned calls=0,expected_calls=0;std::vector<unsigned char> expected;expected.reserve(2097152);
    std::size_t start=0;
    while(start<text.size()) {
        const auto end=text.find('\n',start);VERIFY(end!=std::string::npos);if(end==std::string::npos)break;
        for(auto offset=start;offset<=end;) {
            const auto size=std::min<std::size_t>(64,end-offset+1);const auto data=text.substr(offset,size);
            const auto framed=packet(data);expected.insert(expected.end(),framed.begin(),framed.end());
            expected_calls+=static_cast<unsigned>((size+15+7)/8+1);WriteResult result;
            for(unsigned i=0;i<20;++i) {
                moveTime(hw.now+1000);result=send(owner,data);++calls;
                if(result.status!=WriteStatus::PENDING)break;
            }
            VERIFY(result.status==WriteStatus::PROGRESS&&result.count==size);
            if(result.status!=WriteStatus::PROGRESS)return calls;
            offset+=size;
        }
        start=end+1;
    }
    VERIFY(calls==expected_calls);VERIFY(hw.submitted==expected);VERIFY(hw.emitted==expected);
    VERIFY(hw.overflow==0&&hw.max_queue<=8);return calls;
}
void replay(const std::string& input,const std::string& output) {
    std::ifstream file(input,std::ios::binary);
    const std::string bytes{std::istreambuf_iterator<char>(file),std::istreambuf_iterator<char>()};
    VERIFY(bytes.size()==532562);UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    const auto calls=sendStream(owner,bytes);VERIFY(calls<300000);VERIFY(hw.emitted.size()==682967);
    writeFile(output,hw.emitted.data(),hw.emitted.size());
    std::printf("D116 payload=%zu wire=%zu calls=%u\n",bytes.size(),hw.emitted.size(),calls);
}
std::string formatted(const char* bytes,recorder::csv::FormatResult result) {
    VERIFY(result.status==recorder::csv::FormatStatus::OK);VERIFY(result.size<1024);
    VERIFY(bytes[result.size]=='\0');return std::string(bytes,result.size);
}
std::string capacityWire() {
    namespace csv=recorder::csv;
    const std::string session="18446744073709551615",prefix=","+session+",";
    std::string wire="SUMOX26_DUMP,1,"+session+","+session+",1,25,5001,4096,5001,4096\n";
    char line[1024]{};csv::SummarySnapshot summary;
    summary.phase=recorder::AttemptPhase::SEALED;summary.frame_count=5001;summary.event_count=4096;
    summary.attempt.epoch_token=~std::uint64_t(0);summary.attempt.last_frame_token=~std::uint64_t(0);
    wire+="SH"+prefix+formatted(line,csv::summaryHeader(line,sizeof line));
    wire+="SR"+prefix+formatted(line,csv::summaryRow(summary,line,sizeof line));
    wire+="FH"+prefix+formatted(line,csv::frameHeader(line,sizeof line));
    recorder::StoredFrame frame;frame.status=logframe::PackStatus::INVALID;
    std::memset(frame.bytes.data,0xff,25);
    for(unsigned i=8;i<11;++i)frame.bytes.data[i]=0;
    frame.bytes.data[11]=0x80;
    for(unsigned i=12;i<18;i+=2){frame.bytes.data[i]=0;frame.bytes.data[i+1]=0x80;}
    frame.bytes.data[18]=frame.bytes.data[19]=0x80;
    for(unsigned i=0;i<5001;++i) {
        auto row=formatted(line,csv::frameRow(frame,i,line,sizeof line));
        VERIFY(row.size()+24<=170);if(i==5000)VERIFY(row.size()+24==170);
        wire+="FR"+prefix+row;
    }
    wire+="EH"+prefix+formatted(line,csv::eventHeader(line,sizeof line));
    logframe::EventBytes event;std::memset(event.data,0xff,8);
    for(unsigned i=0;i<4096;++i) {
        const auto row=formatted(line,csv::eventRow(event,i,line,sizeof line));
        VERIFY(row.size()+24<=73);if(i==4095)VERIFY(row.size()+24==73);
        wire+="ER"+prefix+row;
    }
    wire+="END,"+session+",5001,4096,"+std::to_string(crc(wire))+"\n";return wire;
}
void capacity(const std::string& output) {
    const auto bytes=capacityWire();VERIFY(bytes.size()<=1156084);
    UnoQDumpPort owner(Buffering::FIFO8);if(!start(owner))return;
    const auto calls=sendStream(owner,bytes);VERIFY(calls<=217659);VERIFY(hw.emitted.size()<=1505629);
    writeFile(output+".wire",bytes.data(),bytes.size());writeFile(output+".mp",hw.emitted.data(),hw.emitted.size());
    std::printf("RAW_STRESS payload=%zu wire=%zu calls=%u frames=5001 events=4096\n",
                bytes.size(),hw.emitted.size(),calls);
}
}

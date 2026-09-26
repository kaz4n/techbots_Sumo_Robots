// Exercises opt-in receive admission against the independent eight-byte UART model.
// Removing trusted framing cannot bypass setup, ownership, ready, FIFO or poisoning.
// One fresh subprocess per case isolates the native singleton and register model.
#include "fixture.h"
#include <cstdio>
#include <cstdlib>

using namespace fifo_test;
namespace {
SetupGrant optIn() { return {true,true,true,false,ReceiveStream::UNTRUSTED_RECEIVE_STREAM,0xF123456789ABCDEFULL}; }
WriteResult offer(UnoQDumpPort& owner, const std::string& data) {
    const auto before = hw.submitted.size();
    hw.call_started = static_cast<std::uint32_t>(hw.now);
    hw.enforce_budget = true;
    const auto port = owner.port();
    const auto result = port.write(port.context, data.data(), data.size());
    hw.enforce_budget = false;
    VERIFY(hw.submitted.size() - before <= 8U);
    VERIFY(hw.rdr_reads == 0U && hw.forbidden_writes == 0U && hw.overflow == 0U);
    return result;
}
void admission(unsigned bits, unsigned mode, bool supplied) {
    SetupGrant grant{bool(bits&1),bool(bits&2),bool(bits&4),bool(bits&8),
                     static_cast<ReceiveStream>(mode),supplied?1ULL:0ULL};
    const bool expected = (bits & 7) == 7 && ((mode == 0 && bool(bits&8)) || (mode == 1 && supplied));
    UnoQDumpPort owner(Buffering::FIFO8);
    VERIFY((owner.begin(grant) == NativeStatus::OK) == expected);
    if (!expected) VERIFY(hw.init == 0U && hw.configure == 0U && hw.writes == 0U && hw.reads == 0U);
    VERIFY(hw.submitted.empty());
}
void retainedGuards(unsigned fault) {
    UnoQDumpPort owner(Buffering::FIFO8);
    if (fault == 0) hw.ipsr = 1U;
    if (fault == 1) hw.control = 1U;
    if (fault == 2) metadata.fifo_enable = true;
    if (fault <= 2) {
        VERIFY(owner.begin(optIn()) != NativeStatus::OK);
        VERIFY(hw.submitted.empty());
        return;
    }
    VERIFY(owner.begin(optIn()) == NativeStatus::OK);
    hw.setup = false;
    if (fault == 3) {
        UnoQDumpPort other(Buffering::FIFO8);
        const auto writes = hw.writes;
        VERIFY(other.begin(optIn()) == NativeStatus::OWNERSHIP);
        VERIFY(hw.writes == writes);
    } else if (fault == 4) {
        hw.ready = 0;
        VERIFY(!owner.ready());
        VERIFY(offer(owner,"abc").status == WriteStatus::ERROR);
        VERIFY(hw.submitted.empty());
    } else if (fault == 5) {
        VERIFY(offer(owner,std::string(64,'x')).status == WriteStatus::PENDING);
        const auto before = hw.submitted.size();
        const auto port = owner.port();
        port.cancel(port.context);
        VERIFY(owner.status() == NativeStatus::POISONED);
        VERIFY(offer(owner,"abc").status == WriteStatus::ERROR);
        VERIFY(owner.begin(optIn()) != NativeStatus::OK);
        VERIFY(hw.submitted.size() == before);
    } else if (fault == 6) {
        hw.frozen_serial = true;
        VERIFY(offer(owner,"abc").status == WriteStatus::PENDING);
        moveTime(hw.now + 100000U);
        VERIFY(offer(owner,"abc").status == WriteStatus::ERROR);
        VERIFY(owner.status() == NativeStatus::TIMEOUT);
    } else {
        const std::string data(64,'x');
        WriteResult result;
        for (unsigned i=0;i<1000U;++i) {
            result=offer(owner,data);
            if(result.status!=WriteStatus::PENDING) break;
            moveTime(hw.now+100U);
        }
        VERIFY(result.status==WriteStatus::PROGRESS && result.count==64U);
        VERIFY(hw.emitted.size()==79U && hw.max_queue<=8U && hw.max_queue>1U);
        VERIFY(hw.submitted==hw.emitted);
    }
}
}
int main(int argc,char** argv) {
    initialize();
    if(argc==5) admission(unsigned(std::strtoul(argv[2],nullptr,10)),
                         unsigned(std::strtoul(argv[3],nullptr,10)),std::strtoul(argv[4],nullptr,10)!=0);
    else if(argc==3) retainedGuards(unsigned(std::strtoul(argv[2],nullptr,10)));
    else return 2;
    std::printf("checks=%u failures=%u submitted=%zu emitted=%zu queue_max=%u\n",checks,failures,
                hw.submitted.size(),hw.emitted.size(),hw.max_queue);
    return failures?1:0;
}

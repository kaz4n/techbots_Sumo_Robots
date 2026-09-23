// Drives actual D088 native CPP with controlled CMSIS, device and C symbols.
// Contract-derived assertions distinguish submission from optical confirmation.
// Each command-line scenario starts a new process and boot owner lifetime.
#include "hal/ui_matrix_unoq.h"
#include "cmsis_core.h"
#include "zephyr/device.h"
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>
#include <type_traits>

namespace {
enum Call : unsigned { CONTROL=1U,IPSR,MASK,DISABLE,WRITE,BARRIER,RESTORE,READY,GRAY,BEGIN };
unsigned calls[10000] = {};unsigned used=0U;unsigned writes=0U;
unsigned begins=0U;unsigned gray=0U;unsigned ready_reads=0U;
std::uint32_t control=0U;std::uint32_t ipsr=0U;std::uint32_t primask=0U;
std::uint8_t copied[104] = {};const std::uint8_t* last_pointer=nullptr;
device matrix_device{true};
void record(Call call){assert(used<10000U);calls[used++]=call;}
void noWrites(unsigned from) {
    for(unsigned i=from;i<used;++i) assert(calls[i]!=GRAY&&calls[i]!=BEGIN&&calls[i]!=WRITE&&
        calls[i]!=MASK&&calls[i]!=DISABLE&&calls[i]!=BARRIER&&calls[i]!=RESTORE);
}
void maskedCopy(unsigned from,std::uint32_t saved) {
    unsigned at=from;while(at<used&&calls[at]!=MASK)++at;
    assert(at+4U<used);assert(calls[at+1U]==DISABLE);assert(calls[at+2U]==WRITE);
    assert(calls[at+3U]==BARRIER);assert(calls[at+4U]==RESTORE);assert(primask==saved);
    for(unsigned i=at;i<at+5U;++i)assert(calls[i]!=CONTROL&&calls[i]!=IPSR);
}
void beginGood(ui::UnoQMatrix& driver,std::uint32_t mask=0U) {
    primask=mask;const unsigned from=used;
    assert(driver.begin({true,true})==ui::MatrixStatus::INIT_UNCONFIRMED);
    assert(begins==1U);assert(gray==3U);assert(writes==1U);assert(ready_reads==1U);
    maskedCopy(from,mask);
    unsigned g=0U,w=0U,b=0U;
    for(unsigned i=from;i<used;++i){if(calls[i]==GRAY)g=i;if(calls[i]==WRITE)w=i;if(calls[i]==BEGIN)b=i;}
    assert(g<w&&w<b);for(auto byte:copied)assert(byte==0U);
}
ui::Frame pattern() {
    ui::Frame frame;for(unsigned i=0U;i<104U;++i)frame.pixels[i]=static_cast<std::uint8_t>(i%8U);
    return frame;
}
void assertPattern() {for(unsigned i=0U;i<104U;++i)assert(copied[i]==i%8U);}
void initRejected(unsigned scenario) {
    ui::UnoQMatrix driver;ui::MatrixGrant grant{true,true};auto expected=ui::MatrixStatus::INVALID_GRANT;
    if(scenario<3U){grant.normal_startup=(scenario&1U)!=0U;grant.exclusive_boot_owner=(scenario&2U)!=0U;}
    if(scenario==3U){control=1U;expected=ui::MatrixStatus::CONTEXT_REJECTED;}
    if(scenario==4U){ipsr=17U;expected=ui::MatrixStatus::CONTEXT_REJECTED;}
    if(scenario==5U){fixture_matrix_device=nullptr;expected=ui::MatrixStatus::DEVICE_UNAVAILABLE;}
    if(scenario==6U){matrix_device.ready=false;expected=ui::MatrixStatus::DEVICE_UNAVAILABLE;}
    assert(driver.begin(grant)==expected);noWrites(0U);
    if(scenario==5U)assert(ready_reads==0U);
    const unsigned from=used;
    assert(driver.begin({true,true})==ui::MatrixStatus::FAULTED);
    assert(driver.submit(0U,pattern())==ui::MatrixStatus::FAULTED);noWrites(from);
    control=ipsr=0U;fixture_matrix_device=&matrix_device;matrix_device.ready=true;
    ready_reads=0U;ui::UnoQMatrix replacement;beginGood(replacement);
}
void ownership(bool repeated) {
    ui::UnoQMatrix first;beginGood(first);const unsigned from=used;
    ui::UnoQMatrix second;auto& attempted=repeated?first:second;
    assert(attempted.begin({true,true})==ui::MatrixStatus::ALREADY_OWNED);
    assert(attempted.submit(0U,pattern())==ui::MatrixStatus::FAULTED);noWrites(from);
    if(!repeated)assert(first.submit(0U,pattern())==ui::MatrixStatus::SUBMITTED_UNCONFIRMED);
}
void lifetime() {
    {ui::UnoQMatrix first;beginGood(first);}
    const unsigned from=used;ui::UnoQMatrix second;
    assert(second.begin({true,true})==ui::MatrixStatus::ALREADY_OWNED);noWrites(from);
}
void submitContext(unsigned kind) {
    ui::UnoQMatrix driver;beginGood(driver);const unsigned from=used;
    if(kind==0U)control=1U;else ipsr=15U;
    assert(driver.submit(0U,pattern())==ui::MatrixStatus::CONTEXT_REJECTED);noWrites(from);
    control=ipsr=0U;assert(driver.submit(40000U,pattern())==ui::MatrixStatus::FAULTED);noWrites(from);
}
void invalidFrame(unsigned index,unsigned value,bool throttled) {
    ui::UnoQMatrix driver;beginGood(driver);auto frame=pattern();
    if(throttled)assert(driver.submit(999U,frame)==ui::MatrixStatus::SUBMITTED_UNCONFIRMED);
    frame.pixels[index]=static_cast<std::uint8_t>(value);const unsigned from=used;
    assert(driver.submit(1000U,frame)==ui::MatrixStatus::INVALID_FRAME);noWrites(from);
    frame.pixels[index]=0U;assert(driver.submit(1000000U,frame)==ui::MatrixStatus::FAULTED);noWrites(from);
}
void throttle(std::uint32_t anchor,std::uint32_t mask) {
    ui::UnoQMatrix driver;beginGood(driver,mask);auto frame=pattern();unsigned from=used;
    assert(driver.submit(anchor,frame)==ui::MatrixStatus::SUBMITTED_UNCONFIRMED);
    maskedCopy(from,mask);assert(writes==2U);assertPattern();assert(last_pointer!=nullptr);
    std::memset(frame.pixels,0U,sizeof frame.pixels);assertPattern();frame=pattern();from=used;
    for(unsigned delta:{0U,1U,39999U}) {
        assert(driver.submit(anchor+delta,frame)==ui::MatrixStatus::THROTTLED);noWrites(from);
    }
    assert(driver.submit(anchor+40000U,frame)==ui::MatrixStatus::SUBMITTED_UNCONFIRMED);
    maskedCopy(from,mask);assert(writes==3U);from=used;
    assert(driver.submit(anchor+79999U,frame)==ui::MatrixStatus::THROTTLED);noWrites(from);
    assert(driver.submit(anchor+4000000U,frame)==ui::MatrixStatus::SUBMITTED_UNCONFIRMED);
    assert(writes==4U);maskedCopy(from,mask);from=used;
    assert(driver.submit(anchor+4000001U,frame)==ui::MatrixStatus::THROTTLED);noWrites(from);
    assert(begins==1U);
}
} // namespace

const device* fixture_matrix_device=&matrix_device;
bool device_is_ready(const device* value){record(READY);++ready_reads;return value&&value->ready;}
std::uint32_t __get_CONTROL(){record(CONTROL);return control;}
std::uint32_t __get_IPSR(){record(IPSR);return ipsr;}
std::uint32_t __get_PRIMASK(){record(MASK);return primask;}
void __disable_irq(){record(DISABLE);primask=1U;}
void __DMB(){record(BARRIER);assert(primask==1U);}
void __set_PRIMASK(std::uint32_t value){record(RESTORE);primask=value;}
extern "C" void matrixSetGrayscaleBits(std::uint8_t value){record(GRAY);gray=value;}
extern "C" void matrixBegin(){record(BEGIN);++begins;}
extern "C" void matrixGrayscaleWrite(const std::uint8_t* value){
    record(WRITE);assert(primask==1U);assert(value);++writes;last_pointer=value;
    std::memcpy(copied,value,sizeof copied);
}
int main(int argc,char** argv) {
    static_assert(!std::is_copy_constructible<ui::UnoQMatrix>::value,"one native owner");
    static_assert(!std::is_copy_assignable<ui::UnoQMatrix>::value,"one native owner");
    assert(argc>=2);const unsigned scenario=static_cast<unsigned>(std::strtoul(argv[1],nullptr,0));
    if(scenario==0U){ {ui::UnoQMatrix driver;assert(used==0U);
        assert(driver.submit(0U,pattern())==ui::MatrixStatus::NOT_INITIALIZED);assert(used==0U);}
        assert(used==0U); }
    if(scenario==1U){assert(argc==3);initRejected(static_cast<unsigned>(std::strtoul(argv[2],nullptr,0)));}
    if(scenario==2U)ownership(false);
    if(scenario==3U)ownership(true);
    if(scenario==4U)lifetime();
    if(scenario==5U){assert(argc==3);submitContext(static_cast<unsigned>(std::strtoul(argv[2],nullptr,0)));}
    if(scenario==6U){assert(argc==5);invalidFrame(static_cast<unsigned>(std::strtoul(argv[2],nullptr,0)),
        static_cast<unsigned>(std::strtoul(argv[3],nullptr,0)),std::strtoul(argv[4],nullptr,0)!=0U);}
    if(scenario==7U){assert(argc==4);throttle(static_cast<std::uint32_t>(std::strtoul(argv[2],nullptr,0)),
        static_cast<std::uint32_t>(std::strtoul(argv[3],nullptr,0)));}
    if(scenario==8U){control=2U;ui::UnoQMatrix driver;beginGood(driver);
        assert(driver.submit(0U,pattern())==ui::MatrixStatus::SUBMITTED_UNCONFIRMED);}
    assert(scenario<=8U);std::printf("PASS scenario=%u native_writes=%u calls=%u\n",scenario,writes,used);
}

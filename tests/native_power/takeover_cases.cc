// Tests reset-only ADC ownership after an unacknowledged first claim write.
// A fresh Reader must not recover the same boot's partially claimed resource.
// One executable is one fresh process; no production reset hook is available.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "hal/power.h"
namespace {
void loseDividerWrite(fixture::Point p,std::uintptr_t address) {
 if(p==fixture::Point::ACCESS&&address==reinterpret_cast<std::uintptr_t>(&ADC12_COMMON->CCR))
  ADC12_COMMON->CCR.value=0;
}
}
TEST_CASE("B5 ignored first divider write cannot be recovered by a second Reader") {fixture::isolated([&] {
 fixture::reset();fixture::hw.hook=loseDividerWrite;
 {power::Reader first;auto a=first.begin();CHECK_FALSE(a.ready);CHECK(a.status!=power::Status::OK);}
 fixture::hw.hook=nullptr;fixture::clearTrace();power::Reader second;auto b=second.begin();
 CHECK_FALSE(b.ready);CHECK(b.status==power::Status::OWNERSHIP);CHECK(fixture::hw.writes==0);

});}

// Retains actual calibration, raw Robot admission, formatter and renderer APIs.
// Compile-only: setup installs a function pointer; neither setup nor loop calls it.
// Host behavior tests and actual target ELF inspection qualify software separately.
#include "src/qtr_cal_probe.h"
namespace qtr_cal_probe {
fsm::Robot robot;
qtr_cal::Calibration calibration;
Probe volatile entry = nullptr;
}
void setup() { qtr_cal_probe::entry = &qtr_cal_probe::exercise; }
void loop() {}

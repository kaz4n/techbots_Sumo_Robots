// Retains a finite calibration and heading trial when IMU permissions are explicit.
// Ships disabled and constructs no motor, transport or unrelated sensor owner.
// Independent default-sketch tests and checked target startup audits verify this boundary.
#include "src/config.h"
#include "src/imu_heading_bench_native.h"

static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Heading bench requires inert flags");
namespace {
imu_heading_bench::Native native;
imu_heading_bench::Runner runner(native.port());
}
void setup() { runner.begin(imu_heading_bench::Grants{}); }
void loop() { runner.poll(); }

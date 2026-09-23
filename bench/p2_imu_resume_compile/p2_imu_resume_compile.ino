// Retains the D094 resumable IMU source and complete downstream link path.
// Setup stores a pointer only; no peripheral operation or sensor sample executes.
// Controlled startup tests and offline target ELF inspection verify inertness.
#include "src/imu_resume_probe.h"
namespace imu_resume_probe { Probe volatile entry = nullptr; }
void setup() { imu_resume_probe::entry = &imu_resume_probe::exercise; }
void loop() {}

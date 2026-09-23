// Emits the actual D101 Runtime stream and an independently retained CSV snapshot.
// Lets the strict receiver compare every row and loss field across serialization.
// Scoped host runner tests both motor settings with synthetic button windows.
#include "fixture.h"
#include <fstream>
#include <iostream>

namespace {
bool writeExpected(const std::string& base, const recorder::AttemptRecorder& source) {
    char line[recorder::csv::MAX_LINE_BYTES];
    std::ofstream summary(base + "/expected_summary.csv", std::ios::binary);
    auto result = recorder::csv::summaryHeader(line, sizeof(line)); summary.write(line, result.size);
    result = recorder::csv::summaryRow(recorder::csv::captureSummary(source), line, sizeof(line));
    summary.write(line, result.size);
    std::ofstream frames(base + "/expected_frames.csv", std::ios::binary);
    result = recorder::csv::frameHeader(line, sizeof(line)); frames.write(line, result.size);
    for (std::uint32_t i = 0U; i < source.frames().size(); ++i) {
        const auto* frame = source.frames().at(i); if (frame == nullptr) return false;
        result = recorder::csv::frameRow(*frame, i, line, sizeof(line)); frames.write(line, result.size);
    }
    std::ofstream events(base + "/expected_events.csv", std::ios::binary);
    result = recorder::csv::eventHeader(line, sizeof(line)); events.write(line, result.size);
    for (std::uint32_t i = 0U; i < source.events().size(); ++i) {
        const auto* event = source.events().at(i); if (event == nullptr) return false;
        result = recorder::csv::eventRow(*event, i, line, sizeof(line)); events.write(line, result.size);
    }
    return summary.good() && frames.good() && events.good();
}
}
int main(int argc, char** argv) {
    if (argc != 2) return 1;
    app_dump_test::Rig rig;
    if (!rig.active()) { std::cerr << "actual Runtime intent failed\n"; return 2; }
    if (!writeExpected(argv[1], rig.owner.transaction().recording())) return 3;
    if (!rig.finish() || rig.sink.cancels != 0U || rig.fake.enabled) return 4;
    for (auto pulse : rig.fake.pulses) if (pulse != 0U) return 5;
    std::cout << rig.sink.bytes;
    return 0;
}

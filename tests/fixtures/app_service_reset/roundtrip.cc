// Exports actual D103 GO/STOP/tail/reset/local LOG_DUMP bytes from Runtime.
// Saves retained pre-reset CSV independently for strict receiver comparison.
// The author runner verifies both motor builds and every wire byte boundary.
#include "fixture.h"
#include <fstream>
#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) return 1;
    service_reset_test::Rig rig;
    if (!rig.stopped(true) || !rig.owner.transaction().recording().summary().go_seen) return 2;
    std::string frames, events, summary;
    if (!service_reset_test::csv(rig.owner.transaction().recording(), frames, events, summary)) return 3;
    const std::string base = argv[1];
    for (const auto& item : {std::make_pair("frames", frames), std::make_pair("events", events),
                             std::make_pair("summary", summary)}) {
        std::ofstream file(base + "/expected_" + item.first + ".csv", std::ios::binary);
        file.write(item.second.data(), static_cast<std::streamsize>(item.second.size()));
        if (!file.good()) return 4;
    }
    if (!rig.pending() || !rig.next() || !rig.owner.report().service_only || !rig.select(3U) ||
        !rig.request(countdown::Service::LOG_DUMP) || !rig.finishDump()) return 5;
    if (rig.fake.enabled || rig.sink.cancels != 0U) return 6;
    for (auto pulse : rig.fake.pulses) if (pulse != 0U) return 7;
    std::string f, e, s;
    if (!service_reset_test::csv(rig.owner.transaction().recording(), f, e, s) ||
        f != frames || e != events || s != summary) return 8;
    std::cout << rig.sink.bytes;
    return 0;
}

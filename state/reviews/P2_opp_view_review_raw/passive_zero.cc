// Verifies public passive states under the contract's invalid zero-period profile.
// Guards must not turn a never-started or deliberately disabled bench into a fault.
// Compiled against preserved interim and corrected production sources, without seeding.
#include "opp_view.h"
#include <cstdio>

int failures = 0;
#define CHECK(expression) do { if (!(expression)) { ++failures; \
    std::printf("FAIL line %d: %s\n", __LINE__, #expression); } } while (false)

int main() {
    using namespace opp_view;
    Runner unopened({});
    CHECK(unopened.report().phase == Phase::NOT_STARTED);
    CHECK(!unopened.poll());
    CHECK(unopened.report().phase == Phase::NOT_STARTED);
    CHECK(unopened.report().fault == Fault::NONE);
    CHECK(unopened.report().completed_polls == 0U);
    for (bool unused : {false, true}) {
        Runner disabled({});
        Grants grants;
        grants.matrix_grant = {unused, unused};
        CHECK(disabled.begin(grants));
        CHECK(disabled.report().phase == Phase::DISABLED);
        for (unsigned i = 0U; i < 3U; ++i) CHECK(!disabled.poll());
        CHECK(disabled.report().phase == Phase::DISABLED);
        CHECK(disabled.report().fault == Fault::NONE);
        CHECK(!disabled.report().fresh);
        CHECK(!disabled.report().current_available);
        CHECK(disabled.report().completed_polls == 0U);
        CHECK(disabled.report().read_attempts == 0U);
        CHECK(disabled.report().display_attempts == 0U);
        CHECK(!disabled.begin({true, true, {true, true}}));
        CHECK(disabled.report().phase == Phase::DISABLED);
    }
    std::printf("Passive zero-period failures: %d\n", failures);
    return failures != 0;
}

// Reviewer-only public-owner regressions; appended solely to an isolated test copy.
#if MATCH == 0
TEST_CASE("B14 D105 reviewer motor inhibition precedes transport cancellation on abort and clock failure") {
    for (unsigned scenario = 0U; scenario < 3U; ++scenario) {
        Rig rig; CO_REQUIRE(rig.active());
        const auto before = rig.sink.calls.size();
        if (scenario == 0U) rig.owner.abort();
        else {
            rig.sink.reverse_ready = scenario == 1U;
            rig.sink.reverse_write = scenario == 2U;
            CHECK_FALSE(rig.next());
        }
        unsigned cancellations = 0U;
        for (std::size_t i = before; i < rig.sink.calls.size(); ++i) {
            const auto& call = rig.sink.calls[i];
            if (call.kind == Kind::CANCEL) {
                ++cancellations;
                CHECK_MESSAGE(call.halted, "scenario=", scenario,
                    ": actual Transaction motor halt must precede cancellation");
                CHECK(call.transaction == app::Phase::FAULT);
            }
        }
        CHECK(cancellations == 1U);
        inhibited(rig);
    }
}
#endif

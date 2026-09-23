from pathlib import Path
p=Path('tests/native_power/cases.cc');s=p.read_text();start=s.index('TEST_CASE("B5 second live owner');end=s.index('TEST_CASE("B5 admission excludes',start)
new='''TEST_CASE("B5 second live owner cannot gain admission") {
    fixture::isolated([&] {
        fixture::reset();power::Reader first;ready(first);fixture::clearTrace();power::Reader second;
        auto b=second.begin();CHECK(b.status==Status::OWNERSHIP);CHECK_FALSE(b.ready);
        CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);noMoreIo(second,b.shutdown);
    });
}
TEST_CASE("B5 initialized and failed stock ADC owner state rejects a fresh boot") {
    for(auto res:{0,5})fixture::isolated([&] {
        fixture::reset();fixture_devices[0].state->initialized=true;fixture_devices[0].state->init_res=res;
        power::Reader r;auto b=r.begin();CHECK(b.status==Status::OWNERSHIP);
        CHECK(b.shutdown==Shutdown::NOT_ATTEMPTED);CHECK(fixture::hw.writes==0);
        CHECK(fixture::hw.clock_on==0);noMoreIo(r,b.shutdown);
    });
}
'''
s=s[:start]+new+s[end:];s=s.replace('CHECK(fixture::hw.accesses==0);','CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);')
p.write_text(s)
p=Path('tests/native_power/probe_cases.cc');s=p.read_text(encoding='utf-8-sig').replace('CHECK(fixture::hw.accesses==0);','CHECK(fixture::hw.accesses==0);CHECK(fixture::hw.reads==0);');p.write_text(s)

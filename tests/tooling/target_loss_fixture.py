# Builds synthetic D130 traces from the independent D073 byte-format fixtures.
# Keeps target-loss expectations independent of analyzer and firmware implementations.
# Public API/CLI tests use these files only as declared synthetic host evidence.
from countdown_analysis_fixture import BoundedReader, Bundle as CsvBundle, ROOT, U32, wire


BOUND = 35000
GO = 5100000
SOURCE = GO + 100000


class Bundle(CsvBundle):
    def __init__(self, directory, index=0, lower=34950, upper=35000,
                 release=None, mode=1, motors=True):
        super().__init__(directory, index, release=release, mode=mode)
        self.motors = motors
        start = SOURCE
        end = start + upper - lower
        applied = start + upper
        decision = max(end, start + min(30000, upper))
        self.times = {0: self.summary['release_us'], 1: self.absolute(start),
                      2: self.absolute(end), 3: self.absolute(decision),
                      4: self.absolute(applied)}
        self.set_trace([0, 1, 2, 3, 4])
        self.write()

    def absolute(self, offset):
        return (self.summary['release_us'] + offset) & U32

    def timing_record(self, detail, time=None, value=None):
        if time is None:
            time = self.times.get(detail, self.absolute(SOURCE + 31000))
        if value is None:
            value = (0x0105 if self.motors else 0x0101) if detail == 0 else 1
        return dict(t_us=time, ordinal=0, kind=10, detail=detail, value=value)

    def set_trace(self, details):
        mode = self.summary['mode']
        self.events = [dict(t_us=self.summary['release_us'], ordinal=0,
                            kind=0, detail=mode, value=0)]
        remaining = list(details)
        if remaining and remaining[0] == 0:
            self.events.append(self.timing_record(remaining.pop(0)))
        self.events.append(dict(t_us=self.absolute(GO), ordinal=0,
                                kind=1, detail=mode, value=0))
        self.events.extend(self.timing_record(detail) for detail in remaining)
        return self.renumber()

    def renumber(self):
        for ordinal, event in enumerate(self.events):
            event['ordinal'] = ordinal
        return self

    def marker(self, detail):
        return next(event for event in self.events if event['kind'] == 10 and event['detail'] == detail)

    def ordinary(self, kind):
        return next(event for event in self.events if event['kind'] == kind)


def cohort(bundles):
    return dict(schema_version=1, opp_clear_ms=30, extra_margin_ms=5,
                attempts=[bundle.entry() for bundle in bundles])

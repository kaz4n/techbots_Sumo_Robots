# Builds synthetic D127 attempts from the independent frozen D073 wire fixtures.
# Keeps recorder bytes and expected timestamps independent of analyzer implementation.
# Used only by public API and CLI countdown-analysis contract tests.
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'd127_independent_wire', ROOT / 'tests/tooling/test_csv_bundle.py')
wire = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wire)
U32 = (1 << 32) - 1
HOLD = 5100000
CLEAN_FRAME = [0, 10, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1110, 0, 100]


class BoundedReader(wire.CheckedReader):
    def __init__(self, stream, observations, limit):
        super().__init__(stream, observations)
        self.limit = limit

    def read(self, size=-1):
        if not 0 <= size <= self.limit + 1:
            raise AssertionError('Read must fit the role-specific bound plus lookahead')
        return super().read(size)

    def readline(self, size=-1):
        if not 0 < size <= self.limit + 1:
            raise AssertionError('Line read must have a finite role-specific bound')
        self.observations.append(('readline', size))
        return self.stream.readline(size)

    def readinto(self, buffer):
        if len(buffer) > self.limit + 1:
            raise AssertionError('Input buffer exceeds the role-specific file bound')
        return super().readinto(buffer)


class Bundle:
    def __init__(self, directory, index=0, delay=HOLD, release=None, mode=1):
        self.directory = Path(directory)
        self.id = 'synthetic-' + str(index)
        self.paths = {role: self.directory / (self.id + '-' + role + '.csv')
                      for role in ('frames', 'events', 'summary')}
        self.manifest_path = self.directory / (self.id + '-manifest.json')
        release = index * 7000000 + 123 if release is None else release
        go_delay = min(HOLD, delay)
        self.events = [dict(t_us=release, ordinal=0, kind=0, detail=mode, value=0),
                       dict(t_us=(release + go_delay) & U32, ordinal=1,
                            kind=1, detail=mode, value=0),
                       dict(t_us=(release + delay) & U32, ordinal=2,
                            kind=2, detail=3, value=0x0101)]
        self.frames = []
        self.summary = dict(epoch_token=index + 1, last_frame_token=index + 10,
                            release_us=release, mode=mode, phase=3, go_seen=1)
        self.declarations = {}
        self.manifest_present = True
        self.write()

    def manifest(self):
        files = {}
        for role, path in self.paths.items():
            raw = path.read_bytes()
            files[role] = dict(sha256=hashlib.sha256(raw).hexdigest(),
                               rows=raw.count(b'\n') - 1)
        value = dict(schema_version=1, session_id=self.id, origin='synthetic',
                     firmware_revision='a' * 40, source_sha256='b' * 64,
                     config_sha256='c' * 64, log_hz=25, frame_capacity=5001,
                     event_capacity=4096, target='HOST SYNTHETIC ONLY',
                     closure='closed', files=files)
        value.update(self.declarations)
        return value

    def write(self):
        counts = dict(frame_count=len(self.frames), event_count=len(self.events))
        counts.update(self.summary)
        self.paths['frames'].write_bytes(wire.header('frames') + b''.join(self.frames))
        self.paths['events'].write_bytes(wire.header('events') +
                                        b''.join(wire.event(**event) for event in self.events))
        self.paths['summary'].write_bytes(wire.header('summary') + wire.summary(**counts))
        self.manifest_path.write_text(json.dumps(self.manifest()), encoding='ascii')
        return self

    def entry(self):
        value = dict(id=self.id, **{role: path.name for role, path in self.paths.items()})
        value['manifest'] = self.manifest_path.name if self.manifest_present else None
        return value


def cohort(bundles):
    return dict(schema_version=1, countdown_ms=5000, countdown_margin_ms=100,
                attempts=[bundle.entry() for bundle in bundles])

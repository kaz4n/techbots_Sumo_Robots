# Tests the D087 decoder and inert probe from public contracts and literal profiles.
# Production source bodies are copied and hashed opaquely, never read for expectations.
# WSL/Linux compiler and subprocess receipts retain every status and output stream.
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P2_button_routing_raw/author'

DECODER = r'''
#include "hal/ui.h"
#include <cassert>
#include <cstdint>
#include <cstdio>
using Q = ui::ButtonQualification;
using P = core::ButtonPresence;
using B = core::ButtonLevel;
power::ButtonSample good(std::uint16_t raw = 100U) {
    power::ButtonSample s;
    s.status = power::Status::OK; s.valid = true; s.raw = raw;
    s.started_us = 0xfffffff0U; s.completed_us = 19U; s.sequence = 42U;
    return s;
}
void same(const core::ButtonEvidence& a, const core::ButtonEvidence& b) {
    assert(a.explicit_values == b.explicit_values && a.contract_valid == b.contract_valid);
    assert(a.presence == b.presence && a.level == b.level && a.raw == b.raw);
    assert(a.started_us == b.started_us && a.completed_us == b.completed_us);
    assert(a.sequence == b.sequence);
}
void invalid(const power::ButtonSample& s, bool contract) {
    const auto d = ui::decodeButtons(s);
    assert(d.qualification == Q::INVALID);
    assert(d.evidence.explicit_values && d.evidence.contract_valid == contract);
    assert(d.evidence.presence == P::INVALID && d.evidence.level == B::NONE);
}
void statuses() {
    const auto empty = ui::decodeButtons({});
    assert(empty.qualification == Q::ABSENT && empty.evidence.presence == P::ABSENT);
    assert(empty.evidence.explicit_values && empty.evidence.contract_valid);
    assert(empty.evidence.raw == 0U && empty.evidence.sequence == 0U);
    assert(empty.evidence.started_us == 0U && empty.evidence.completed_us == 0U);
    for (unsigned status = 1U; status <= 14U; ++status) {
        for (unsigned shutdown = 0U; shutdown <= 2U; ++shutdown) {
            auto s = good(); s.valid = false;
            s.status = static_cast<power::Status>(status);
            s.shutdown = static_cast<power::Shutdown>(shutdown);
            invalid(s, true);
        }
    }
    for (unsigned change = 0U; change < 9U; ++change) {
        auto s = good();
        if (change == 0U) s.status = static_cast<power::Status>(255U);
        if (change == 1U) s.shutdown = static_cast<power::Shutdown>(3U);
        if (change == 2U) s.valid = false;
        if (change == 3U) s.status = power::Status::NOT_ENABLED;
        if (change == 4U) s.shutdown = power::Shutdown::DISABLED;
        if (change == 5U) s.shutdown = power::Shutdown::UNCONFIRMED;
        if (change == 6U) s.raw = 16384U;
        if (change == 7U) s.completed_us = s.started_us + 100U;
        if (change == 8U) s.completed_us = s.started_us - 1U;
        invalid(s, false);
    }
}
void adapter() {
    fsm::RobotInput before;
    before.t_us = 901U; before.initialization_complete = true;
    before.observations_fresh = true; before.opponent_fresh = true;
    before.opp_raw_mask = 31U; before.line_raw_us[2] = 937U;
    before.raw_heading_deg = 11.0F; before.raw_gyro_z_dps = 12.0F;
    before.ax_g = 13.0F; before.ay_g = 14.0F; before.imu_ok = true;
    before.previous_bias_dps = 15.0F; before.vbat_v = 16.0F; before.vbat_valid = true;
    before.button = B::BOTH; before.stop_requested = true;
    before.reset_cause = fsm::ResetCause::WATCHDOG; before.previous.token = 777U;
    before.previous.applied_valid = true; before.previous.applied_us = 123U;
    before.imu.explicit_values = true; before.imu.sequence = 444U;
    before.line.explicit_values = true; before.line.sequence = 555U;
    auto after = before;
    const auto s = good(); const auto decoded = ui::decodeButtons(s);
    assert(ui::applyButtons(after, s) == decoded.qualification);
    same(after.buttons, decoded.evidence);
    assert(after.t_us == before.t_us && after.initialization_complete == before.initialization_complete);
    assert(after.observations_fresh == before.observations_fresh && after.opponent_fresh == before.opponent_fresh);
    assert(after.opp_raw_mask == before.opp_raw_mask && after.line_raw_us[2] == before.line_raw_us[2]);
    assert(after.raw_heading_deg == before.raw_heading_deg && after.raw_gyro_z_dps == before.raw_gyro_z_dps);
    assert(after.ax_g == before.ax_g && after.ay_g == before.ay_g && after.imu_ok == before.imu_ok);
    assert(after.previous_bias_dps == before.previous_bias_dps && after.vbat_v == before.vbat_v);
    assert(after.vbat_valid == before.vbat_valid && after.button == before.button);
    assert(after.stop_requested == before.stop_requested && after.reset_cause == before.reset_cause);
    assert(after.previous.token == before.previous.token && after.previous.applied_valid == before.previous.applied_valid);
    assert(after.previous.applied_us == before.previous.applied_us);
    assert(after.imu.explicit_values == before.imu.explicit_values && after.imu.sequence == before.imu.sequence);
    assert(after.line.explicit_values == before.line.explicit_values && after.line.sequence == before.line.sequence);
}
int main() {
    if (PROFILE == 4) { invalid(good(), false); std::puts("malformed configuration rejected"); return 0; }
    statuses(); adapter();
    for (std::uint32_t raw = 0U; raw <= 16383U; ++raw) {
        const auto s = good(static_cast<std::uint16_t>(raw));
        const auto d = ui::decodeButtons(s);
        if (PROFILE == 0) {
            assert(d.qualification == Q::UNCONFIGURED);
            assert(d.evidence.presence == P::INVALID && d.evidence.level == B::NONE);
        } else if (PROFILE == 1) {
            const unsigned level = raw < 100U ? 0U : raw < 200U ? 1U : raw < 300U ? 2U : 3U;
            assert(d.qualification == Q::VALID && d.evidence.presence == P::VALID);
            assert(static_cast<unsigned>(d.evidence.level) == level);
            assert(d.candidate_mask == (1U << level));
            assert(d.evidence.raw == raw && d.evidence.sequence == 42U);
            assert(d.evidence.started_us == s.started_us && d.evidence.completed_us == s.completed_us);
        } else if (PROFILE == 2) {
            unsigned mask = 0U;
            if (raw <= 100U) mask |= 1U;
            if (raw >= 100U && raw <= 200U) mask |= 2U;
            if (raw >= 100U && raw <= 300U) mask |= 4U;
            if (raw >= 100U) mask |= 8U;
            assert(d.candidate_mask == mask);
            const bool overlap = (mask & (mask - 1U)) != 0U;
            assert(d.qualification == (overlap ? Q::AMBIGUOUS : Q::VALID));
            if (overlap) assert(d.evidence.presence == P::INVALID && d.evidence.level == B::NONE);
        } else {
            unsigned mask = 0U;
            if (raw >= 10U && raw <= 20U) mask |= 1U;
            if (raw >= 30U && raw <= 40U) mask |= 2U;
            if (raw >= 50U && raw <= 60U) mask |= 4U;
            if (raw >= 70U && raw <= 80U) mask |= 8U;
            assert(d.candidate_mask == mask);
            assert(d.qualification == (mask == 0U ? Q::UNKNOWN : Q::VALID));
            if (mask == 0U) assert(d.evidence.presence == P::INVALID && d.evidence.level == B::NONE);
        }
        assert(d.evidence.explicit_values && d.evidence.contract_valid);
    }
    auto instant = good(15U); instant.completed_us = instant.started_us;
    assert(ui::decodeButtons(instant).qualification != Q::INVALID);
    instant.completed_us = instant.started_us + 99U;
    assert(ui::decodeButtons(instant).qualification != Q::INVALID);
    std::puts("16384 raw values plus status, timing and adapter assertions PASS");
}
'''

PROBE = r'''
#include "doctest.h"
#include "native_fixture.h"
#include "button_probe.h"
void setup(); void loop();
TEST_CASE("B6 D087 actual button probe setup and10000loops never run retained path") {
    CHECK(fixture::hw.accesses == 0U); CHECK(fixture::hw.micros_calls == 0U);
    CHECK(fixture::hw.reads == 0U); CHECK(fixture::hw.ready_reads == 0U);
    CHECK(fixture::hw.clock_on == 0U); CHECK(fixture::hw.clock_rate == 0U);
    CHECK(button_probe::entry == nullptr);
    fixture::hw.count_allocations = true;
    setup(); for (unsigned i = 0U; i < 10000U; ++i) loop();
    fixture::hw.count_allocations = false;
    CHECK(button_probe::entry == &button_probe::exercise);
    CHECK(fixture::hw.allocations == 0U); CHECK(fixture::hw.accesses == 0U);
    CHECK(fixture::hw.micros_calls == 0U); CHECK(fixture::hw.reads == 0U);
    CHECK(fixture::hw.ready_reads == 0U); CHECK(fixture::hw.clock_on == 0U);
    CHECK(fixture::hw.clock_rate == 0U);
}
'''


class ButtonDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RAW.mkdir(parents=True, exist_ok=True)
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('Run under Linux/WSL with g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-button-d087-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.base = [cls.compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all']
        frozen = [Path(__file__), ROOT/'state/analysis/P2_button_routing_contract.md',
                  ROOT/'src/hal/ui.h', ROOT/'src/hal/power.h', ROOT/'src/config.h']
        frozen += list((ROOT/'tests').glob('test_button_*.cpp'))
        cls.save('freeze', {'purpose': 'Independent contract/public API assertions before first execution',
                           'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen}})

    @classmethod
    def save(cls, kind, payload):
        (RAW/f'{kind}_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')

    @classmethod
    def command(cls, argv, manifest=None, timeout=180):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        cls.save('command', {'argv': list(map(str, argv)), 'returncode': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr,
                            'capture': 'subprocess text=True; normalized newline', 'source_manifest': manifest})
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result

    def profile(self, number, edits=None):
        slot = self.stage/f'profile-{time.time_ns()}'
        source = slot/'src'
        shutil.copytree(ROOT/'src', source)
        if edits:
            text = (source/'config.h').read_text()
            for name, value in edits.items():
                text, count = re.subn(r'(\b'+re.escape(name)+r'\s*=\s*)[^;]+;',
                                     lambda m: m.group(1)+value+';', text)
                self.assertEqual(count, 1, name)
            (source/'config.h').write_text(text)
        case = slot/'case.cpp'; case.write_text(DECODER)
        binary = slot/'decoder'
        manifest = {str(p.relative_to(slot)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in slot.rglob('*') if p.is_file()}
        self.command([*self.base, f'-DPROFILE={number}', '-I', str(source),
                      str(case), str(source/'hal/ui.cpp'), '-o', str(binary)], manifest)
        self.command([str(binary)], manifest)

    def test_b6_unconfigured_profile_never_implies_none(self):
        self.profile(0)

    def test_b6_synthetic_inclusive_windows_preserve_all_14bit_values(self):
        self.profile(1, {'BUTTON_WINDOWS_CONFIGURED':'1U',
                        'BUTTON_LOW_RAW[4]':'{0U,100U,200U,300U}',
                        'BUTTON_HIGH_RAW[4]':'{99U,199U,299U,16383U}'})

    def test_b6_overlapping_windows_report_every_candidate_without_priority(self):
        self.profile(2, {'BUTTON_WINDOWS_CONFIGURED':'1U',
                        'BUTTON_LOW_RAW[4]':'{0U,100U,100U,100U}',
                        'BUTTON_HIGH_RAW[4]':'{100U,200U,300U,16383U}'})

    def test_b6_unmatched_counts_are_unknown_not_release(self):
        self.profile(3, {'BUTTON_WINDOWS_CONFIGURED':'1U',
                        'BUTTON_LOW_RAW[4]':'{10U,30U,50U,70U}',
                        'BUTTON_HIGH_RAW[4]':'{20U,40U,60U,80U}'})

    def test_b6_malformed_config_rejects_before_logical_mapping(self):
        for edits in ({'BUTTON_WINDOWS_CONFIGURED':'2U'},
                      {'BUTTON_LOW_RAW[4]':'{1U,0U,0U,0U}'},
                      {'BUTTON_HIGH_RAW[4]':'{16384U,0U,0U,0U}'},
                      {'BUTTON_SAMPLE_MAX_AGE_US':'0U'},
                      {'BUTTON_SAMPLE_MAX_AGE_US':'99U'},
                      {'BUTTON_SAMPLE_MAX_AGE_US':'2147483648U'}):
            with self.subTest(edits=edits):
                self.profile(4, edits)

    def test_b6_actual_probe_is_inert_in_both_macro_modes(self):
        fixture = ROOT/'tests/native_power'
        for allowed in (0, 1):
            slot = self.stage/f'probe-{allowed}'
            shutil.copytree(ROOT/'src', slot/'src')
            shutil.copytree(ROOT/'bench/p2_button_compile', slot/'probe')
            shutil.copyfile(slot/'probe/p2_button_compile.ino', slot/'sketch.cpp')
            case = slot/'case.cpp'; case.write_text(PROBE)
            binary = slot/'probe_test'
            manifest = {str(p.relative_to(slot)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in slot.rglob('*') if p.is_file()}
            self.command([*self.base, '-DARDUINO_ARCH_ZEPHYR',
                          '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                          f'-DMATCH={allowed}', f'-DMOTORS_ALLOWED={allowed}',
                          '-I', str(slot/'src'), '-I', str(slot/'probe'), '-I', str(slot/'probe/src'),
                          '-I', str(fixture), '-isystem', str(ROOT/'host/third_party'),
                          str(case), str(fixture/'native_fixture.cc'), str(fixture/'test_main.cc'),
                          str(slot/'src/hal/power.cpp'), str(slot/'src/hal/native_pins.cpp'), str(slot/'src/hal/ui.cpp'),
                          *map(str, (slot/'src/core').glob('*.cpp')),
                          str(slot/'probe/src/button_probe.cpp'), str(slot/'sketch.cpp'),
                          '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free',
                          '-o', str(binary)], manifest)
            self.assertIn('Status: SUCCESS!', self.command([str(binary), '--no-colors'], manifest).stdout)

    def test_b6_upload_refuses_all_eight_modes_before_transport(self):
        spec = importlib.util.spec_from_file_location('button_board_tool', ROOT/'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT':transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        with self.assertRaises(ValueError) as caught:
                            board.flash(SimpleNamespace(sketch='bench/p2_button_compile', match=match,
                                                        startup=startup, compile_only=False))
                        self.save('upload_refusal', {'transport':transport, 'match':match, 'startup':startup,
                                  'error':str(caught.exception), 'target_calls':target.call_count,
                                  'remote_calls':remote.call_count, 'require_calls':require.call_count,
                                  'board_tool_sha256':hashlib.sha256((ROOT/'tools/board_tool.py').read_bytes()).hexdigest()})
                        target.assert_not_called(); remote.assert_not_called(); require.assert_not_called()

    def test_b15_csv_validator_retains_new_detail11_with_existing_schema(self):
        from . import test_csv_bundle as fixtures
        slot = self.stage/'csv'; slot.mkdir()
        files = {kind:slot/f'{kind}.csv' for kind in ('frames', 'events', 'summary')}
        files['frames'].write_bytes(fixtures.header('frames') + fixtures.FRAME_LITERAL)
        files['events'].write_bytes(fixtures.header('events') +
                                    fixtures.event(ordinal=0, kind=9, detail=11, value=256) +
                                    fixtures.event(ordinal=1, kind=9, detail=11, value=512))
        files['summary'].write_bytes(fixtures.header('summary') + fixtures.summary(event_count=2))
        validator = fixtures.load_validator()
        report = validator.validate_bundle(files['frames'], files['events'], files['summary'])
        self.save('csv_compatibility', {'report':report,
                  'files':{kind:p.read_text() for kind,p in files.items()},
                  'validator_sha256':hashlib.sha256((ROOT/'tools/validate_csv_bundle.py').read_bytes()).hexdigest()})
        self.assertEqual(report['format_integrity'], 'PASS')
        self.assertFalse(report['hardware_acceptance'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

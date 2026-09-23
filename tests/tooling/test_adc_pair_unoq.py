# Extends the established native battery runner with independent D086 assertions.
# Production bodies are copied and hashed opaquely, never read for expectations.
# All inherited battery methods and original assertions remain unchanged and run here.
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import time
from types import SimpleNamespace
import unittest
from unittest import mock
from . import test_power_unoq as _battery

ROOT = _battery.ROOT
FIXTURE = _battery.FIXTURE
RECEIPTS = ROOT / 'state/analysis/P2_adc_pair_raw/author'


class NativeAdcPairTests(_battery.NativePowerTests):
    @classmethod
    def setUpClass(cls):
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        paths = [Path(__file__), ROOT/'src/hal/power.h', ROOT/'src/config.h',
                 ROOT/'state/analysis/P2_adc_pair_contract.md']
        paths += [p for p in FIXTURE.rglob('*') if p.is_file()]
        payload = {'purpose': 'Contract/header-derived tests frozen before first production execution',
                   'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
        (RECEIPTS/f'freeze_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')
        super().setUpClass()

    @classmethod
    def receipt(cls, argv, result):
        old = os.environ.get('SUMO_NATIVE_RECEIPT_DIR')
        os.environ['SUMO_NATIVE_RECEIPT_DIR'] = str(RECEIPTS)
        try:
            super().receipt(argv, result)
        finally:
            if old is None:
                os.environ.pop('SUMO_NATIVE_RECEIPT_DIR', None)
            else:
                os.environ['SUMO_NATIVE_RECEIPT_DIR'] = old

    @classmethod
    def variant(cls, definitions=(), case='cases.cc', edits=None, probe=False):
        if not probe or not case.startswith('pair'):
            return super().variant(definitions, case, edits, probe)
        slot = cls.stage/f'pair-probe-{len(list(cls.stage.glob("pair-probe-*")))}'
        source = slot/'src'; (source/'hal').mkdir(parents=True)
        for name in ('power.cpp', 'power.h'):
            shutil.copyfile(ROOT/'src/hal'/name, source/'hal'/name)
        shutil.copyfile(ROOT/'src/config.h', source/'config.h')
        shutil.copytree(ROOT/'bench/p2_adc_pair_compile', slot/'probe')
        sketch = slot/'pair_sketch.cpp'
        shutil.copyfile(slot/'probe/p2_adc_pair_compile.ino', sketch)
        binary = slot/'native-adc-pair'
        cls.command([*cls.base, *definitions, '-I', str(source), '-I', str(slot/'probe'),
                     '-I', str(slot/'probe/src'), str(FIXTURE/case),
                     str(FIXTURE/'native_fixture.cc'), str(FIXTURE/'isolation.cc'),
                     str(source/'hal/power.cpp'), str(slot/'probe/src/adc_pair_probe.cpp'),
                     str(sketch), str(cls.main),
                     '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free', '-o', str(binary)])
        cls.binary_manifests[str(binary)] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                           for p in slot.rglob('*') if p.is_file() and p != binary}
        return binary

    def test_b6_pair_public_contract_and_backward_compatibility(self):
        self.execute(self.variant(case='pair_cases.cc'))

    def test_b6_pair_guards_and_tracked_partial_transitions(self):
        self.execute(self.variant(case='pair_guards.cc'))

    def test_b6_pair_exact_timing_flags_and_sequence(self):
        self.execute(self.variant(case='pair_timing.cc'))

    def test_b6_pair_metadata_and_proposal_exclusions(self):
        for kind in range(1, 6):
            with self.subTest(kind=kind):
                self.execute(self.variant(definitions=(f'-DNATIVE_PAIR_BAD_MAP={kind}',), case='pair_metadata_cases.cc'))
        for kind in (6, 7):
            for index in (2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19):
                with self.subTest(kind=kind,index=index):
                    self.execute(self.variant(definitions=(f'-DNATIVE_PAIR_BAD_MAP={kind}',f'-DNATIVE_ALIAS_INDEX={index}'),case='pair_metadata_cases.cc'))
        for channel in (9, 11):
            self.execute(self.variant(definitions=(f'-DNATIVE_BUTTON_CHANNEL={channel}',),case='pair_metadata_cases.cc'))
        self.execute(self.variant(definitions=('-DNATIVE_TABLE_SIZE=15',),case='pair_metadata_cases.cc'))
        for pin in ('14U', '16U', '999U'):
            self.execute(self.variant(case='pair_metadata_cases.cc',edits={'BUTTON_INPUT_PIN':pin}))

        for pins in ('{2U,4U,7U,14U}','{2U,4U,7U,15U}','{2U,4U,7U,999U}'):
            self.execute(self.variant(case='pair_metadata_cases.cc',edits={'QTR_INPUT_PINS[4]':pins}))

    def test_b6_pair_probe_is_inert_in_both_macro_modes(self):
        for allowed in (0, 1):
            with self.subTest(allowed=allowed):
                self.execute(self.variant(definitions=(f'-DMATCH={allowed}',f'-DMOTORS_ALLOWED={allowed}'),case='pair_probe_cases.cc',probe=True))

    def test_b6_pair_upload_refusals_precede_every_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('adc_pair_board_tool',ROOT/'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        for transport in ('adb','ssh'):
            for match in (False,True):
                for startup in ('default','immediate'):
                    with self.subTest(transport=transport,match=match,startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ,{'SUMO_TRANSPORT':transport}))
                        target=stack.enter_context(mock.patch.object(board,'target'))
                        remote=stack.enter_context(mock.patch.object(board,'remote'))
                        require=stack.enter_context(mock.patch.object(board,'require_transport'))
                        with self.assertRaises(ValueError) as caught:
                            board.flash(SimpleNamespace(sketch='bench/p2_adc_pair_compile',match=match,startup=startup,compile_only=False))
                        payload={'transport':transport,'match':match,'startup':startup,'error':str(caught.exception),
                                 'target_calls':target.call_count,'remote_calls':remote.call_count,'require_transport_calls':require.call_count,
                                 'board_tool_sha256':hashlib.sha256((ROOT/'tools/board_tool.py').read_bytes()).hexdigest()}
                        (RECEIPTS/f'upload_refusal_{time.time_ns()}.json').write_text(json.dumps(payload,indent=2)+'\n')
                        target.assert_not_called();remote.assert_not_called();require.assert_not_called()


if __name__=='__main__':
    unittest.main(verbosity=2)

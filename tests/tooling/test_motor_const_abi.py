# Preserves all D199 ABI methods through exact checked fixture metadata only.
# Adds D204 recipe, current artifact/source binding and consumed-owner coverage.
# Freeze before new reader inspection; every process/transport endpoint is controlled.
import ast
import builtins
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_motor_const_compile_raw'
SUBJECT = RAW + '/inspect_static_abi.py'
SUBJECT_PIN = (16087, 'f360a52d6e8c29227b8a59481f37f5e8a30b207d7b66fbffaa8e8785a4dedf3c')
PRIOR = 'tests/tooling/test_motor_settle_abi.py'
PRIOR_PIN = (30983, '96763b42d61b80654503f4093d32ac3b174ab2152fdfb795b3801304e4e2b252')
BASELINE = 'state/analysis/P7_motor_settle_compile_raw/inspect_static_abi.py'
BASELINE_PIN = (16106, '0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea')
CONTRACT = 'state/analysis/P7_motor_const_abi_contract.md'
SOURCE = '4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2'
OLD_SOURCE = '117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da'
OWNER = '/home/arduino/sumox26_codex_build/app-motor-const-static01'
SCOPE = '/home/arduino/sumox26_codex_build/app-motor-const-abi-static01'
PRIOR_PROJECTED = (30948, '635ad352851111ec9af6d4696240ff75111bd84fac1d386c1840c46ac5d54652')
PRIOR_REPLACEMENTS = (
    (b'D199', b'D204', 7),
    (b'P7_motor_settle_compile_raw', b'P7_motor_const_compile_raw', 2),
    (b'tools/compile_motor_settle_probe.py', b'tools/compile_motor_const.py', 4),
    (b'P7_motor_settle_abi_contract.md', b'P7_motor_const_abi_contract.md', 1),
    (b'dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956', b'55a9f10dec0a7a148fc6fab3cc80ae131ae2e9a82ac74ce14c7aeb1c484ce3d1', 1),
    (b'7570', b'7557', 1),
    (b'13432', b'13559', 1),
    (b'1608', b'1605', 1),
    (b'9648', b'9645', 1),
    (b'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62', b'957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247', 1),
    (b'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282', b'1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95', 1),
    (b'9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5', b'323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7', 1),
    (b'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10', b'fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd', 1),
    (b'app-motor-settle-abi-static01', b'app-motor-const-abi-static01', 2),
    (b'app-motor-settle-static01', b'app-motor-const-static01', 2),
    (b'117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da', b'4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2', 1),
    (b'17061', b'17051', 1),
    (b'67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6', b'938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6', 1),
    (b'a7f77d9b640988fcd2fd891abdc4d4b2ac449058d23ce7b9e794fdd13fe7f358', b'9acd23ba6cddac9c23be6a01812939043a9bba5095f467165b6d15a1bb320cba', 1),
)
WRAPPER_REPLACEMENTS = (
    (b'D199', b'D204', 2),
    (b'P7_motor_settle_compile_raw', b'P7_motor_const_compile_raw', 2),
    (b'tools/compile_motor_settle_probe.py', b'tools/compile_motor_const.py', 2),
    (b'P7_motor_settle_abi_contract.md', b'P7_motor_const_abi_contract.md', 1),
    (b'dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956', b'55a9f10dec0a7a148fc6fab3cc80ae131ae2e9a82ac74ce14c7aeb1c484ce3d1', 1),
    (b'7570', b'7557', 1),
    (b'13432', b'13559', 1),
    (b'1608', b'1605', 1),
    (b'9648', b'9645', 1),
    (b'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62', b'957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247', 2),
    (b'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282', b'1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95', 2),
    (b'9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5', b'323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7', 2),
    (b'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10', b'fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd', 2),
    (b'app-motor-settle-abi-static01', b'app-motor-const-abi-static01', 1),
    (b'app-motor-settle-static01', b'app-motor-const-static01', 1),
    (b'117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da', b'4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2', 1),
    (b'17061', b'17051', 1),
    (b'67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6', b'938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6', 1),
    (b'_sumox_d199_abi02_original', b'_sumox_d204_abi02_original', 1),
)
CURRENT_INPUTS = {
    'state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py': (8219, 'a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421'),
    'state/analysis/P7_motor_const_abi_contract.md': (15192, '55a9f10dec0a7a148fc6fab3cc80ae131ae2e9a82ac74ce14c7aeb1c484ce3d1'),
    'state/analysis/P7_motor_const_compile_raw/inputs_static.json': (13559, '1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95'),
    'state/analysis/P7_motor_const_compile_raw/native_static01/artifacts.json': (9645, 'fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd'),
    'state/analysis/P7_motor_const_compile_raw/native_static01/result.json': (1605, '323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7'),
    'tools/compile_motor_const.py': (7557, '957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247'),
}
CURRENT_ARTIFACTS = {
    'artifacts/app_motor_observe.ino.bin-zsk.bin': (95368, 'f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7'),
    'build/app_motor_observe.ino.bin': (95352, '76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3'),
    'build/app_motor_observe.ino.bin-zsk.bin': (95368, 'f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7'),
    'build/app_motor_observe.ino.elf': (172600, '390b69c1f35dd85a56462e562561e16b4659c0e31aa44d99aaf5b87e4ccd7e13'),
    'build/app_motor_observe.ino.elf-zsk.bin': (172600, '5416c121deb8ff3cb0a27a3d8d150981fe945c5ab818fe3da788744f4980db7f'),
    'build/app_motor_observe.ino.map': (449499, '23416a129a832bbbc4738814a7a1326a62f5e5f9e879d925ab7620e3ab1b88a3'),
    'build/app_motor_observe.ino_debug.elf': (1838360, 'b3520cacc96ccd3d410b011dd6b4e65761c503b940fa13f1fddfe59db3666066'),
    'build/app_motor_observe.ino_temp.elf': (1838360, 'b3520cacc96ccd3d410b011dd6b4e65761c503b940fa13f1fddfe59db3666066'),
}
STALE_INPUTS = {
    'tools/compile_motor_const.py': ('tools/compile_motor_settle_probe.py', 7570, 'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62'),
    'state/analysis/P7_motor_const_compile_raw/inputs_static.json': ('state/analysis/P7_motor_settle_compile_raw/inputs_static.json', 13432, 'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282'),
    'state/analysis/P7_motor_const_compile_raw/native_static01/result.json': ('state/analysis/P7_motor_settle_compile_raw/native_static01/result.json', 1608, '9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5'),
    'state/analysis/P7_motor_const_compile_raw/native_static01/artifacts.json': ('state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json', 9648, 'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10'),
    'state/analysis/P7_motor_const_abi_contract.md': ('state/analysis/P7_motor_settle_abi_contract.md', 22405, 'dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956'),
}
NEW_METHODS = (
    'test_exact_nineteen_step_wrapper_and_all_function_bodies',
    'test_current_six_pins_reject_stale_d199_bytes_before_private_execution',
    'test_current_source_manifest_and_artifact_admission_refuse_d199_substitutes',
    'test_consumed_d199_local_owner_and_transport_scope_are_not_current',
    'test_current_artifact_pins_require_all_thirteen_closures_and_preserve_raw',
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(name, pin):
    raw = (ROOT / name).read_bytes()
    if (len(raw), sha(raw)) != pin:
        raise AssertionError('D204 frozen input differs: ' + name)
    return raw


def project(raw, substitutions):
    for old, new, count in substitutions:
        if raw.count(old) != count:
            raise AssertionError('Independent metadata occurrence differs: ' + repr(old))
        raw = raw.replace(old, new)
    return raw


def historical():
    raw = project(checked(PRIOR, PRIOR_PIN), PRIOR_REPLACEMENTS)
    if (len(raw), sha(raw)) != PRIOR_PROJECTED:
        raise AssertionError('Private complete D199 oracle projection differs')
    module = types.ModuleType('_d204_private_d199_oracle')
    module.__file__ = str(ROOT / PRIOR)
    module.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def functions(raw):
    lines = raw.splitlines(keepends=True)
    return {item.name: b''.join(lines[item.lineno-1:item.end_lineno])
            for item in ast.parse(raw).body if isinstance(item, ast.FunctionDef)}


def additional_cases(prior):
    class CurrentAbiContract(prior.SettleAbiContract):
        def test_exact_nineteen_step_wrapper_and_all_function_bodies(self):
            old = checked(BASELINE, BASELINE_PIN)
            actual = checked(SUBJECT, SUBJECT_PIN)
            self.assertEqual(actual, project(old, WRAPPER_REPLACEMENTS))
            self.assertEqual(len(WRAPPER_REPLACEMENTS), 19)
            self.assertEqual(sum(count for _, _, count in WRAPPER_REPLACEMENTS), 26)
            before, after = functions(old), functions(actual)
            self.assertEqual(set(before), set(after)); self.assertEqual(len(after), 17)
            for name, raw in before.items():
                if name == 'load_reader':
                    self.assertEqual(raw.count(b'_sumox_d199_abi02_original'), 1)
                    raw = raw.replace(b'_sumox_d199_abi02_original', b'_sumox_d204_abi02_original')
                self.assertEqual(after[name], raw, name)
            self.assertEqual(self.subject.INPUT, (16937, 'b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981'))
            self.assertEqual(self.subject.PROJECTED, (17051, '938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6'))

        def test_current_six_pins_reject_stale_d199_bytes_before_private_execution(self):
            expected = {name: pin for name, pin in CURRENT_INPUTS.items() if name != CONTRACT}
            self.assertEqual(self.subject.ORIGINALS, expected)
            self.assertEqual(self.subject.CONTRACT, CONTRACT)
            self.assertEqual(self.subject.CONTRACT_SHA, CURRENT_INPUTS[CONTRACT][1])
            self.assertEqual(set(self.inputs) | {CONTRACT}, set(CURRENT_INPUTS))
            current = {name: checked(name, pin) for name, pin in CURRENT_INPUTS.items()}
            for target, (old_name, size, digest) in STALE_INPUTS.items():
                root = self.scratch()
                for name, raw in current.items():
                    path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
                (root / target).write_bytes(checked(old_name, (size, digest)))
                execute = mock.Mock(side_effect=AssertionError('Stale input reached private execution'))
                self.subject.__dict__['__builtins__']['exec'] = execute
                with self.subTest(target=target):
                    self.reject(lambda: self.subject.load_reader(root=root))
                    execute.assert_not_called()

        def test_current_source_manifest_and_artifact_admission_refuse_d199_substitutes(self):
            reader, owner = self.base.LifecycleContract.prepared_owner(self)
            self.assertEqual(owner.source_sha256, SOURCE)
            self.assertEqual(owner.inputs_path, ROOT / RAW / 'inputs_static.json')
            self.assertEqual(sha(owner.code['src/hal/motor_port_unoq.cpp']), 'fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b')
            current_manifest = owner.inputs_path
            old_name, size, digest = STALE_INPUTS[RAW + '/inputs_static.json']
            path = self.scratch() / 'stale-inputs.json'; path.write_bytes(checked(old_name, (size, digest)))
            stale_owner = reader.StaticAbi(prior.HEAD); stale_owner.inputs_path = path
            self.reject(lambda: stale_owner.compiler.CompileDiagnostic.admission(stale_owner))
            self.assertEqual(owner.inputs_path, current_manifest)
            report = owner.prepare()
            self.assertEqual(report['source_sha256'], SOURCE)
            self.assertEqual(owner.packet['schema'], 'app-motor-const-static-artifacts-v1')
            old_name, size, digest = STALE_INPUTS[RAW + '/native_static01/artifacts.json']
            old_packet = checked(old_name, (size, digest))
            self.reject(lambda: owner.compiler.CompileDiagnostic.validate_artifact_reply(owner, old_packet.decode()))
            old_name, size, digest = STALE_INPUTS[RAW + '/native_static01/result.json']
            old_outcome = checked(old_name, (size, digest)); original = reader.pinned
            def stale_outcome(path, expected, *args):
                return old_outcome if Path(path) == ROOT / reader.OUTCOME else original(path, expected, *args)
            with mock.patch.object(reader, 'pinned', stale_outcome):
                self.reject(owner.prepare)
            self.assertFalse(owner.output.exists()); self.assertFalse(owner.claimed)

        def test_consumed_d199_local_owner_and_transport_scope_are_not_current(self):
            reader = self.loaded(); owner = reader.StaticAbi(prior.HEAD)
            self.assertEqual(reader.SELF, SUBJECT); self.assertEqual(reader.SOURCE, SOURCE)
            self.assertEqual(reader.OWNER, OWNER); self.assertEqual(owner.remote, SCOPE)
            self.assertEqual(owner.output, ROOT / RAW / 'native_abi_static01')
            owner.source_sha256, owner.boot = SOURCE, self.base.BOOT
            owner.claimed = True
            old_path = 'state/analysis/P7_motor_settle_compile_raw/native_abi_static01/result.json'
            owner.git_state = mock.Mock(return_value=(prior.HEAD, [('??', old_path)]))
            with mock.patch.object(reader, 'pinned', return_value=b'controlled local identity'), mock.patch.object(
                    owner.compiler.CompileDiagnostic, 'admission', return_value=None):
                self.reject(owner.local)
                owner.git_state.return_value = (prior.HEAD, [])
                owner.source_sha256 = OLD_SOURCE; self.reject(owner.local)
            _, attempt, result, writes = self.base.LifecycleContract.executing_owner(self)
            result['scope'] = 'D199_STATIC_FILE_ONLY_ABI'
            attempt.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
            self.reject(attempt.execute)
            self.assertEqual(writes[1], ('result.json', result))
            self.assertNotIn('abi.json', [name for name, _ in writes])
            self.assertEqual(writes[-1][1]['status'], 'FAILED'); attempt.local.assert_called_once_with()

        def test_current_artifact_pins_require_all_thirteen_closures_and_preserve_raw(self):
            _, prepared = self.base.LifecycleContract.prepared_owner(self); prepared.prepare()
            observed = {name: (row['identity']['bytes'], row['sha256']) for name, row in prepared.packet['files'].items()}
            self.assertEqual(observed, CURRENT_ARTIFACTS)
            prefix = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
            core = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
            expected = {OWNER + '/' + name: pin[1] for name, pin in CURRENT_ARTIFACTS.items()}
            expected.update({prefix + 'readelf': 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e',
                prefix + 'gdb': '8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778',
                core + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf': '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',
                core + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S': '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'})
            self.assertEqual(prepared.remote_pins, expected); self.assertEqual(len(expected), 12)
            paths = [*prepared.remote_pins, 'board_identity']; self.assertEqual(len(paths), 13)
            self.assertEqual(len(prepared.commands), 4)
            for failed in [None, *paths]:
                _, owner, result, writes = self.base.LifecycleContract.executing_owner(self)
                owner.remote_pins = dict(prepared.remote_pins)
                result['final_checks'] = [dict(path=name, status='FAILED' if name == failed else 'PASS') for name in paths]
                before = copy.deepcopy(result)
                owner.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
                with self.subTest(failed=failed):
                    if failed is None:
                        self.assertEqual(owner.execute()['status'], 'STATIC_ABI_OBSERVED')
                        self.assertIn('abi.json', [name for name, _ in writes])
                    else:
                        self.reject(owner.execute)
                        self.assertNotIn('abi.json', [name for name, _ in writes])
                        self.assertEqual(writes[-1][1]['status'], 'FAILED')
                    self.assertEqual(writes[1], ('result.json', before)); self.assertEqual(result, before)
                    owner.local.assert_called_once_with()
    return CurrentAbiContract


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D204 independent tests require Python -B')
    prior = historical()
    retained = prior.load_tests(loader, loader.loadTestsFromTestCase(prior.SettleAbiContract), pattern)
    if retained.countTestCases() != 66:
        raise AssertionError('All 66 D199 methods must be retained')
    case = additional_cases(prior)
    suite = unittest.TestSuite([standard, retained])
    suite.addTests(case(name) for name in NEW_METHODS)
    if suite.countTestCases() != 71:
        raise AssertionError('Expected 66 inherited and five new D204 methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)

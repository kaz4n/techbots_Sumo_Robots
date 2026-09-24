# Tests D114's literal shared-source probe, true grant, and checked compile boundary.
# Uses the public contract and existing synthetic policy fixtures, with opaque bodies.
# Runs in isolated Linux copies; no transport, ADC hardware, or upload is performed.
import contextlib
import copy
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from . import test_opp_view_policy as fixture

ROOT = Path(__file__).resolve().parents[2]
SKETCH = 'bench/ui_adc_probe'
PROJECT = 'ui_adc_probe.ino'
SHARED = ('ui_bench.h', 'ui_bench.cpp', 'ui_bench_native.h', 'ui_bench_native.cpp')
OLD_SKETCH_SHA = 'be6dd812eac69d4d1df49a4bbc04378d799604a065ef27abdf22212b03a09139'
BASELINES = {
    'ui_bench.h': '881eceb27b8eb54654777529b50c8df49597a2303352f11f9b34695310e7094e',
    'ui_bench.cpp': 'bc2def36d611f534112288dfca538ab36d51aff58d73c7e5e09eb1f0d9a7e70d',
    'ui_bench_native.h': '74d66c0ff294ce09ff1a1eaa387c686b3726557cac19e2027e1f6e1c1144fee4',
    'ui_bench_native.cpp': 'a9bd1c4d71cb167a94953194435857c88823ffd755db89d80ed9dccb6a2381d0',
}


class UiAdcProbeStageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d114-stage-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.board = fixture.board
        self.patch = mock.patch.object(self.board, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.write('src/config.h', b'// literal config\n')
        for directory in ('core', 'hal', 'app'):
            self.write('src/'+directory+'/shared.h', ('// '+directory+'\n').encode())
        self.write(SKETCH+'/'+PROJECT, b'// literal probe\nvoid setup() {}\nvoid loop() {}\n')
        for index, name in enumerate(SHARED):
            self.write('bench/ui/src/'+name, ('// independently named shared file '+str(index)+'\r\n').encode())
        self.write('bench/ui/src/not_selected.cpp', b'// must not be copied\n')
        self.write('bench/ui/ui.ino', b'// must not replace probe\n')

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def stage(self):
        with mock.patch.object(self.board, 'remote', side_effect=AssertionError('staging used transport')):
            return self.board.stage(SKETCH)

    def test_exact_four_sources_bytes_layout_and_existing_project_modules(self):
        output = self.stage()
        self.assertEqual(output, self.root / 'build/stage/ui_adc_probe')
        self.assertEqual((output / PROJECT).read_bytes(), (self.root / SKETCH / PROJECT).read_bytes())
        for name in SHARED:
            self.assertEqual((output/'src'/name).read_bytes(), (self.root/'bench/ui/src'/name).read_bytes())
        for relative in ('config.h', 'core/shared.h', 'hal/shared.h', 'app/shared.h'):
            self.assertEqual((output/'src'/relative).read_bytes(), (self.root/'src'/relative).read_bytes())
        self.assertFalse((output/'src/not_selected.cpp').exists())
        self.assertFalse((output/'ui.ino').exists())
        self.assertEqual({p.name for p in output.glob('*.ino')}, {PROJECT})

    def test_every_shared_file_participates_in_source_hash_and_restage(self):
        initial = self.board.source_hash(self.stage())
        for name in SHARED:
            path = self.root/'bench/ui/src'/name
            original = path.read_bytes()
            path.write_bytes(original+b'// changed fixture\n')
            self.assertNotEqual(self.board.source_hash(self.stage()), initial)
            path.write_bytes(original)
            self.assertEqual(self.board.source_hash(self.stage()), initial)
        stale = self.root/'build/stage/ui_adc_probe/stale.cpp'
        stale.write_bytes(b'// previous staging output\n')
        self.stage()
        self.assertFalse(stale.exists())

    def test_missing_each_shared_file_is_refused(self):
        for name in SHARED:
            with self.subTest(name=name):
                path = self.root/'bench/ui/src'/name
                original = path.read_bytes()
                path.unlink()
                with self.assertRaises(ValueError):
                    self.stage()
                path.write_bytes(original)

    def test_shared_file_symlinks_and_each_ancestry_symlink_are_refused(self):
        for relative in ('bench/ui/src/ui_bench.h', 'bench/ui/src', 'bench/ui', 'bench'):
            with self.subTest(relative=relative):
                path = self.root/relative
                moved = self.root/'saved-source'
                path.rename(moved)
                path.symlink_to(moved, target_is_directory=moved.is_dir())
                with self.assertRaises(ValueError):
                    self.stage()
                path.unlink()
                moved.rename(path)

    def test_every_destination_collision_including_dangling_link_is_refused(self):
        for name in SHARED:
            for kind in ('file', 'directory', 'dangling'):
                with self.subTest(name=name, kind=kind):
                    destination = self.root/'destination'
                    destination.mkdir(exist_ok=True)
                    conflict = destination/name
                    if kind == 'file': conflict.write_bytes(b'preserve existing')
                    elif kind == 'directory': conflict.mkdir()
                    else: conflict.symlink_to(self.root/'does-not-exist')
                    with self.assertRaises(ValueError):
                        self.board.stage_ui_probe_sources(SKETCH, destination)
                    if kind == 'file': self.assertEqual(conflict.read_bytes(), b'preserve existing')
                    elif kind == 'directory': self.assertTrue(conflict.is_dir())
                    else: self.assertTrue(conflict.is_symlink())
                    if kind == 'directory': conflict.rmdir()
                    else: conflict.unlink()
                    for created in destination.iterdir():
                        created.unlink()

    def test_real_stage_local_source_collision_cannot_shadow_shared_owner(self):
        for name in SHARED:
            with self.subTest(name=name):
                collision = self.write(SKETCH+'/src/'+name, b'// shadow shared owner\n')
                with self.assertRaises(ValueError):
                    self.stage()
                self.assertEqual(collision.read_bytes(), b'// shadow shared owner\n')
                collision.unlink()

    def test_helper_only_selects_exact_probe_and_never_arbitrary_source_paths(self):
        destination = self.root/'destination'
        destination.mkdir()
        for sketch in ('bench/ui', 'bench/ui_adc_probe_copy', '../bench/ui_adc_probe',
                       'bench/ui_adc_probe/../ui_adc_probe', str(self.root/SKETCH)):
            with self.subTest(sketch=sketch):
                self.board.stage_ui_probe_sources(sketch, destination)
                self.assertEqual(list(destination.iterdir()), [])

    def test_original_sketch_and_all_four_existing_implementations_remain_exact(self):
        self.assertEqual(hashlib.sha256((ROOT/'bench/ui/ui.ino').read_bytes()).hexdigest(), OLD_SKETCH_SHA)
        for name, expected in BASELINES.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT/'bench/ui/src'/name).read_bytes()).hexdigest(), expected)


class UiAdcProbePolicyTests(unittest.TestCase):
    def validate(self, doc, immediate=False, flags=fixture.FLAGS):
        fqbn = fixture.IMMEDIATE if immediate else fixture.FQBN
        return fixture.policy.validate_result(json.dumps(doc), fqbn, flags, fixture.BUILD, project=PROJECT)

    def test_default_result_preflight_and_exact_selected_artifact_names(self):
        document = fixture.document(project=PROJECT)
        result = self.validate(document)
        before = fixture.policy.validate_preflight(json.dumps(document), fixture.FQBN,
            fixture.FLAGS, fixture.BUILD, fixture.DATA, project=PROJECT)
        self.assertEqual(result, before)
        self.assertEqual(result['build.project_name'], PROJECT)
        pins = fixture.policy.installed_pins(fixture.DATA)
        names = [fixture.BUILD+'/'+PROJECT+suffix for suffix in ('.elf', '_debug.elf', '_temp.elf')]
        names += [fixture.ARTIFACTS+'/'+PROJECT+'.elf-zsk.bin']
        def remote(target, command, capture):
            self.assertEqual(command, ['sha256sum', '--', *pins, *names])
            return fixture.SimpleNamespace(stdout=''.join(pins.get(name, '1'*64)+'  '+name+'\n' for name in command[2:]))
        self.assertEqual(set(fixture.policy.verify_files(remote, 'fixture', result, fixture.BUILD, fixture.ARTIFACTS)), set([*pins,*names]))

    def test_immediate_and_every_conflicting_macro_profile_are_refused(self):
        for immediate in (False, True):
            for flags in ('-DMATCH=1 -DMOTORS_ALLOWED=1', '-DMATCH=0 -DMOTORS_ALLOWED=1',
                          '-DMATCH=1 -DMOTORS_ALLOWED=0', '', fixture.FLAGS+' -DOTHER=1'):
                with self.subTest(immediate=immediate, flags=flags), self.assertRaises(ValueError):
                    fixture.policy.selected_project(PROJECT, fixture.IMMEDIATE if immediate else fixture.FQBN, flags)
            if immediate:
                with self.assertRaises(ValueError):
                    self.validate(fixture.document(True, PROJECT), True)
        self.assertEqual(fixture.policy.selected_project(PROJECT, fixture.FQBN, fixture.FLAGS), PROJECT)

    def test_mixed_project_references_external_libraries_and_success_claims_refuse(self):
        original = fixture.document(project=PROJECT)
        for index, entry in enumerate(fixture.entries(original)):
            if PROJECT not in entry:
                continue
            for other in ('ui.ino', 'app.ino', 'ui_adc_probe_other.ino'):
                bad = copy.deepcopy(original)
                fixture.entries(bad)[index] = entry.replace(PROJECT, other)
                with self.subTest(index=index, other=other), self.assertRaises(ValueError):
                    self.validate(bad)
        for key, value in (('success', False), ('upload_result', {'success':True})):
            bad = copy.deepcopy(original)
            bad[key] = value
            with self.assertRaises(ValueError): self.validate(bad)
        bad = copy.deepcopy(original)
        bad['builder_result']['used_libraries'] = [{'name':'Arduino_RouterBridge'}]
        with self.assertRaises(ValueError): self.validate(bad)

    def test_default_only_compile_routes_to_checked_project(self):
        for startup in (None, 'default'):
            with fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH, startup))
                source = '/fixture/root/'+'a'*64+'/ui_adc_probe'
                calls['compile_app'].assert_called_once_with('fixture-board', 'a'*64,
                    source, '/fixture/root', fixture.FQBN, fixture.FLAGS, 'default', project=PROJECT)
                self.assertEqual(calls['remote'].call_args_list,
                                 [mock.call('fixture-board', ['mkdir', '-p', source])])
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_upload_match_and_immediate_refuse_before_all_transport_or_staging(self):
        for startup in (None, 'default', 'immediate'):
            for match, compile_only in ((False, False), (True, False), (True, True), (False, True)):
                if not match and compile_only and startup != 'immediate':
                    continue
                with self.subTest(startup=startup, match=match, compile_only=compile_only):
                    with fixture.isolated_flash(SKETCH) as calls:
                        with self.assertRaises(ValueError):
                            fixture.board.flash(fixture.args(SKETCH, startup, match, compile_only))
                        for name in ('target', 'require_transport', 'stage', 'remote', 'compile_app'):
                            calls[name].assert_not_called()

    def test_profile_overrides_and_checked_failure_never_fall_back(self):
        for name in ('sketch.yaml', 'sketch.yml'):
            for link in (False, True):
                with fixture.isolated_flash(SKETCH) as calls:
                    folder = fixture.board.ROOT/SKETCH
                    folder.mkdir(parents=True)
                    path = folder/name
                    if link: path.symlink_to(folder/'missing')
                    else: path.write_text('profile: unreviewed')
                    with self.assertRaises(ValueError): fixture.board.flash(fixture.args(SKETCH))
                    calls['target'].assert_not_called()
                    calls['compile_app'].assert_not_called()
        with fixture.isolated_flash(SKETCH) as calls:
            calls['compile_app'].side_effect = ValueError('checked build refusal')
            with self.assertRaises(ValueError): fixture.board.flash(fixture.args(SKETCH))
            self.assertEqual(len(calls['remote'].call_args_list), 1)
            self.assertEqual(calls['remote'].call_args.args[1][0], 'mkdir')

    def test_old_ui_profiles_and_upload_refusal_remain_unchanged(self):
        for startup, fqbn, mode in ((None,fixture.FQBN,'default'),
                                   ('immediate',fixture.IMMEDIATE,'immediate')):
            with fixture.isolated_flash('bench/ui') as calls:
                fixture.board.flash(fixture.args('bench/ui', startup))
                calls['compile_app'].assert_called_once_with('fixture-board','a'*64,
                    '/fixture/root/'+'a'*64+'/ui','/fixture/root',fqbn,fixture.FLAGS,mode,project='ui.ino')
            with fixture.isolated_flash('bench/ui') as calls:
                with self.assertRaises(ValueError):
                    fixture.board.flash(fixture.args('bench/ui', startup, compile_only=False))
                calls['target'].assert_not_called()
                calls['remote'].assert_not_called()


STUB = r'''#pragma once
#include <cstdint>
#include <cstdlib>
namespace ui_bench {
inline unsigned natives=0, runners=0, ports=0, begins=0, polls=0;
inline void* owner=nullptr;
inline void* runner_owner=nullptr;
inline void require(bool value) { if (!value) std::abort(); }
struct Port { void* context=nullptr; };
struct Grants { bool exclusive_adc=false; };
class Native {
public:
    Native() { require(++natives==1); owner=this; }
    Port port() { require(this==owner); ++ports; return {this}; }
};
class Runner {
public:
    explicit Runner(const Port& port) {
        require(++runners==1 && port.context==owner); runner_owner=this;
    }
    bool begin(const Grants& grants) {
        require(this==runner_owner && ++begins==1 && polls==0);
        require(grants.exclusive_adc==bool(EXPECT_EXCLUSIVE)); return BEGIN_RESULT;
    }
    bool poll() { require(this==runner_owner && begins==1); ++polls; return false; }
};
}
'''
MAIN = r'''#include "src/ui_bench_native.h"
#include <cstddef>
void setup();
void loop();
void* operator new(std::size_t) { std::abort(); }
void* operator new[](std::size_t) { std::abort(); }
void operator delete(void*) noexcept { std::abort(); }
void operator delete[](void*) noexcept { std::abort(); }
void operator delete(void*, std::size_t) noexcept { std::abort(); }
void operator delete[](void*, std::size_t) noexcept { std::abort(); }
int main() {
    using namespace ui_bench;
    require(natives==1 && runners==1 && ports==1 && begins==0 && polls==0);
    setup();
    require(begins==1 && polls==0);
    for (unsigned index=0; index<10000; ++index) loop();
    require(natives==1 && runners==1 && ports==1 && begins==1 && polls==10000);
}
'''


@unittest.skipUnless(sys.platform.startswith('linux'), 'Host wrapper substitution requires g++ under Linux')
class UiAdcProbeWrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d114-wrapper-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'src').mkdir()
        (self.root/'src/ui_bench_native.h').write_text(STUB)
        (self.root/'src/ui_bench.h').write_text('#pragma once\n#include "ui_bench_native.h"\n')
        (self.root/'src/config.h').write_text('#pragma once\n')
        (self.root/'Arduino.h').write_text('#pragma once\n')
        (self.root/'main.cc').write_text(MAIN)
        self.compiler = shutil.which('g++')
        self.assertIsNotNone(self.compiler)

    def compile(self, sketch, grant, result, flags=(), syntax=False):
        path = ROOT/'bench'/sketch/(sketch+'.ino')
        shutil.copyfile(path,self.root/'wrapper.cc')
        command = [self.compiler,'-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror',
                   '-fno-exceptions','-fno-rtti','-I',str(self.root),'-include','Arduino.h',
                   '-DEXPECT_EXCLUSIVE='+str(int(grant)),'-DBEGIN_RESULT='+str(int(result)),*flags]
        if syntax:
            command += ['-fsyntax-only',str(self.root/'wrapper.cc')]
        else:
            command += [str(self.root/'wrapper.cc'),str(self.root/'main.cc'),'-o',str(self.root/'probe')]
        return subprocess.run(command,capture_output=True,text=True,timeout=60)

    def test_actual_new_and_unchanged_old_wrappers_have_one_owner_exact_grant_and_no_heap(self):
        for sketch, grant in (('ui_adc_probe', True), ('ui', False)):
            for begin_result in (False, True):
                for sanitizer in (False, True):
                    flags = ['-DMATCH=0','-DMOTORS_ALLOWED=0']
                    if sanitizer:
                        flags += ['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
                    with self.subTest(sketch=sketch, begin=begin_result, sanitizer=sanitizer):
                        built = self.compile(sketch,grant,begin_result,flags)
                        self.assertEqual(built.returncode,0,built.stderr)
                        ran = subprocess.run([str(self.root/'probe')],capture_output=True,text=True,timeout=10)
                        self.assertEqual(ran.returncode,0,ran.stderr)
                        self.assertEqual(ran.stdout,'')
                        self.assertEqual(ran.stderr,'')

    def test_actual_probe_compile_guards_refuse_each_nonzero_match_motor_profile(self):
        for match, motors in ((1,0),(0,1),(1,1)):
            with self.subTest(match=match,motors=motors):
                result = self.compile('ui_adc_probe',True,True,
                                      ['-DMATCH='+str(match),'-DMOTORS_ALLOWED='+str(motors)],True)
                self.assertNotEqual(result.returncode,0)
                self.assertTrue(result.stderr.strip())


if __name__ == '__main__':
    unittest.main(verbosity=2)

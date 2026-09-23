# Checks D-071/D-072 frozen contracts and public header without reading probe code.
# Keeps candidate preparation, inert startup and compile-only authority independently tested.
# Runs with unittest under WSL using strict C++17 counted substitutes and no board access.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
BENCH = 'bench/p2_recorder_memory'
LITERAL = b'LOG_HZ = 50U'


def load_tool():
    # Import executes the tool but does not disclose its source to the test author.
    with mock.patch.object(sys, 'path', [str(ROOT / 'tools'), *sys.path]):
        spec = importlib.util.spec_from_file_location(
            'independent_recorder_memory_build', ROOT / 'tools/recorder_memory_build.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


def input_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for base in (root / 'src', root / BENCH)
            for path in base.rglob('*') if path.is_file()}


class RecorderMemoryPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='sumo-memory-sources-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'project'
        self.root.mkdir()
        self.module = load_tool()
        self.module.ROOT = self.root
        self.board_root = self.module.board_tool.ROOT
        self.addCleanup(setattr, self.module.board_tool, 'ROOT', self.board_root)
        fixture = {
            'src/config.h': b'// fixture\r\ninline constexpr unsigned LOG_HZ = 50U; // Hz\r\n',
            'src/core/fsm.h': b'// public fixture\n',
            'src/core/fsm.cpp': b'// opaque core fixture\n',
            'src/hal/recorder.h': b'// public fixture\n',
            'src/hal/recorder.cpp': b'// opaque owner fixture\n',
            BENCH + '/p2_recorder_memory.ino': b'// inert sketch fixture\n',
            BENCH + '/src/memory_probe.h': b'// public fixture\n',
            BENCH + '/src/memory_probe.cpp': b'// opaque probe fixture\n',
        }
        for relative, data in fixture.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.before = input_bytes(self.root)
        self.flash = mock.patch.object(self.module.board_tool, 'flash',
                                       side_effect=AssertionError('transport forbidden'))
        self.flash_mock = self.flash.start()
        self.addCleanup(self.flash.stop)

    def prepare(self, rate):
        with redirect_stdout(io.StringIO()):
            return self.module.prepare_source(rate)

    def check_candidate(self, candidate, rate, source_rate=50, expected_config=None):
        self.assertIsInstance(candidate, Path)
        self.assertTrue(candidate.resolve().is_relative_to(
            (self.root / 'build/memory_sources').resolve()))
        self.assertNotEqual(candidate.resolve(), self.root.resolve())
        expected = dict(self.before)
        if expected_config is not None:
            expected['src/config.h'] = expected_config
        else:
            declaration = f'inline constexpr unsigned LOG_HZ = {source_rate}U;'.encode()
            expected['src/config.h'] = expected['src/config.h'].replace(
                declaration, f'inline constexpr unsigned LOG_HZ = {rate}U;'.encode())
        self.assertEqual(expected, input_bytes(candidate))
        self.assertEqual(self.before, input_bytes(self.root))
        provenance = json.loads((candidate / 'provenance.json').read_text())
        self.assertEqual(rate, provenance['rate_hz'])
        self.assertEqual(source_rate, provenance['source_rate_hz'])
        self.assertEqual(hash_bytes(self.before['src/config.h']),
                         provenance['original_config_sha256'])
        self.assertEqual(hash_bytes(expected['src/config.h']),
                         provenance['candidate_config_sha256'])
        self.assertEqual({name: hash_bytes(data) for name, data in self.before.items()},
                         provenance['source_files'])
        self.assertEqual({name: hash_bytes(data) for name, data in expected.items()},
                         provenance['candidate_files'])
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)
        self.flash_mock.assert_not_called()

    def test_d071_50hz_copy_is_byte_identical_and_manifest_exact(self):
        self.check_candidate(self.prepare(50), 50)

    def test_d071_25hz_changes_only_the_one_config_literal(self):
        self.check_candidate(self.prepare(25), 25)

    def test_d072_both_source_rates_support_both_destination_rates_with_exact_provenance(self):
        for source_rate in (25, 50):
            config = (b'// fixture\r\ninline constexpr unsigned LOG_HZ = ' +
                      str(source_rate).encode() + b'U; // Hz\r\n')
            (self.root / 'src/config.h').write_bytes(config)
            self.before = input_bytes(self.root)
            for rate in (25, 50):
                with self.subTest(source=source_rate, destination=rate):
                    self.check_candidate(self.prepare(rate), rate, source_rate)

    def test_d072_changes_only_active_digits_and_preserves_comments_adjacent_values_and_crlf(self):
        prefix = (b'// Original inline constexpr std::uint32_t LOG_HZ = 50U;\r\n'
                  b'/* inline constexpr unsigned LOG_HZ = 25U; */\r\n'
                  b'namespace config {\r\ninline constexpr unsigned NEIGHBOR_HZ = 50U;\r\n'
                  b'inline constexpr std::uint32_t LOG_HZ = ')
        suffix = (b'U; // fallback25Hz from original50; LOG_HZ = 50U\r\n'
                  b'inline constexpr unsigned NEXT_HZ = 25U;\r\n}\r\n')
        for source_rate in (25, 50):
            config = prefix + str(source_rate).encode() + suffix
            (self.root / 'src/config.h').write_bytes(config)
            self.before = input_bytes(self.root)
            for rate in (25, 50):
                with self.subTest(source=source_rate, destination=rate):
                    expected = prefix + str(rate).encode() + suffix
                    self.check_candidate(self.prepare(rate), rate, source_rate, expected)

    def test_d072_unsupported_nonliteral_and_ambiguous_declarations_reject_before_copy(self):
        declaration = b'inline constexpr std::uint32_t LOG_HZ = 25U;\n'
        invalid = (
            b'// ' + declaration,
            b'/* ' + declaration + b' */\n',
            b'#define LOG_HZ 25U\n',
            declaration.replace(b'25U', b'49U'),
            declaration.replace(b'25U', b'0U'),
            declaration.replace(b'25U', b'(25U)'),
            declaration.replace(b'25U', b'25U + 0U'),
            declaration.replace(b'25U', b'OTHER_HZ'),
            declaration + declaration,
            declaration + declaration.replace(b'25U', b'50U'),
            declaration + declaration.replace(b'25U', b'49U'),
            declaration + b'#define LOG_HZ 50U\n',
            b'struct Fixture { ' + declaration + b'};\n',
        )
        with mock.patch.object(shutil, 'copy2') as copy_file, \
                mock.patch.object(shutil, 'copytree') as copy_tree:
            for config in invalid:
                (self.root / 'src/config.h').write_bytes(config)
                for rate in (25, 50):
                    with self.subTest(config=config, rate=rate), self.assertRaises(ValueError):
                        self.prepare(rate)
                    self.assertEqual(config, (self.root / 'src/config.h').read_bytes())
                    self.assertEqual(self.board_root, self.module.board_tool.ROOT)
            copy_file.assert_not_called()
            copy_tree.assert_not_called()
        self.flash_mock.assert_not_called()

    def test_d072_conditionals_continuations_and_array_duplicates_reject_before_copy(self):
        declaration = b'inline constexpr unsigned LOG_HZ = 25U;\n'
        invalid = (
            b'#if 0\n' + declaration + b'#endif\n',
            b'#if 1\n' + declaration + b'#endif\n',
            b'#define FAKE \\\n' + declaration,
            b'// continued comment \\\n' + declaration,
            declaration + b'inline constexpr unsigned LOG_HZ[1] = {50U};\n',
        )
        with mock.patch.object(shutil, 'copy2', side_effect=AssertionError('copy forbidden')) as copy_file, \
                mock.patch.object(shutil, 'copytree', side_effect=AssertionError('copy forbidden')) as copy_tree:
            for config in invalid:
                (self.root / 'src/config.h').write_bytes(config)
                for rate in (25, 50):
                    with self.subTest(config=config, rate=rate), self.assertRaises(ValueError):
                        self.prepare(rate)
                    self.assertEqual(config, (self.root / 'src/config.h').read_bytes())
                    self.assertEqual(self.board_root, self.module.board_tool.ROOT)
            copy_file.assert_not_called()
            copy_tree.assert_not_called()
        self.flash_mock.assert_not_called()

    def test_d072_closed_unrelated_preprocessor_guards_preserve_valid_top_level_rate(self):
        prefix = (b'#ifndef MATCH\n#define MATCH 0\n#endif\n'
                  b'#ifndef MOTORS_ALLOWED\n#define MOTORS_ALLOWED 0\n#endif\n'
                  b'namespace config {\ninline constexpr std::uint32_t LOG_HZ = ')
        suffix = b'U; // Hz\n}\n'
        for source_rate in (25, 50):
            config = prefix + str(source_rate).encode() + suffix
            (self.root / 'src/config.h').write_bytes(config)
            self.before = input_bytes(self.root)
            for rate in (25, 50):
                with self.subTest(source=source_rate, destination=rate):
                    expected = prefix + str(rate).encode() + suffix
                    self.check_candidate(self.prepare(rate), rate, source_rate, expected)

    def test_d071_each_preparation_is_fresh_and_preserves_previous_candidate(self):
        first = self.prepare(25)
        (first / 'retention-sentinel').write_bytes(b'keep previous candidate')
        first_files = {p.relative_to(first): p.read_bytes() for p in first.rglob('*') if p.is_file()}
        second, third = self.prepare(25), self.prepare(50)
        self.assertEqual(3, len({first.resolve(), second.resolve(), third.resolve()}))
        self.assertEqual(first_files, {p.relative_to(first): p.read_bytes()
                                      for p in first.rglob('*') if p.is_file()})
        self.check_candidate(second, 25)
        self.check_candidate(third, 50)

    def test_d071_rejects_every_noninteger_or_unsupported_rate_before_work(self):
        for rate in (True, False, None, '25', '50', 25.0, 50.0, -25, 0, 24, 26, 49, 51):
            with self.subTest(rate=repr(rate)), self.assertRaises(ValueError):
                self.prepare(rate)
        self.assertFalse((self.root / 'build').exists())
        self.assertEqual(self.before, input_bytes(self.root))
        self.flash_mock.assert_not_called()

    def test_d071_missing_config_or_required_sketch_fails_explicitly(self):
        for relative in ('src/config.h', BENCH + '/p2_recorder_memory.ino'):
            path = self.root / relative
            saved = path.read_bytes()
            path.unlink()
            try:
                with self.subTest(path=relative), self.assertRaises((ValueError, OSError)):
                    self.prepare(25)
            finally:
                path.write_bytes(saved)
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)

    def test_d071_missing_or_duplicated_expected_literal_rejects_both_rates(self):
        path = self.root / 'src/config.h'
        for data in (b'LOG_HZ = 49U;', LITERAL + b';\n' + LITERAL + b';\n', b''):
            path.write_bytes(data)
            for rate in (25, 50):
                with self.subTest(data=data, rate=rate), self.assertRaises(ValueError):
                    self.prepare(rate)
                self.assertEqual(data, path.read_bytes())
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)

    def test_d071_copy_failure_propagates_without_original_change_or_board_call(self):
        with mock.patch.object(shutil, 'copy2', side_effect=OSError('copy denied')), \
                mock.patch.object(shutil, 'copytree', side_effect=OSError('copy denied')):
            with self.assertRaises(OSError):
                self.prepare(25)
        self.assertEqual(self.before, input_bytes(self.root))
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)
        self.flash_mock.assert_not_called()

    def test_d071_symlink_source_files_and_dangling_links_are_rejected(self):
        target = Path(self.temporary.name) / 'outside'
        target.write_bytes(b'outside unchanged')
        for destination in (target, target.with_name('missing')):
            link = self.root / 'src/core/unsafe.cpp'
            link.symlink_to(destination)
            try:
                with self.subTest(destination=str(destination)), self.assertRaises(ValueError):
                    self.prepare(25)
            finally:
                link.unlink()
        self.assertEqual(b'outside unchanged', target.read_bytes())

    def test_d071_source_bench_and_build_ancestry_symlinks_are_rejected(self):
        for relative in ('src', 'bench', 'build', 'build/memory_sources'):
            with self.subTest(relative=relative):
                path = self.root / relative
                saved = path.with_name(path.name + '_saved')
                existed = path.exists()
                if existed:
                    path.rename(saved)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    saved.mkdir()
                path.symlink_to(saved, target_is_directory=True)
                try:
                    with self.assertRaises(ValueError):
                        self.prepare(50)
                finally:
                    path.unlink()
                    if existed:
                        saved.rename(path)
        self.assertEqual(self.before, input_bytes(self.root))
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)

    def test_d071_compile_uses_only_safe_flags_and_prints_provenance_before_flash(self):
        output = io.StringIO()
        observed = []
        def fake_flash(args):
            candidate = self.module.board_tool.ROOT
            self.assertNotEqual(candidate, self.board_root)
            self.assertEqual(dict(sketch=BENCH, match=False, compile_only=True,
                                  startup='default'), vars(args))
            self.assertTrue((candidate / 'provenance.json').is_file())
            self.assertIn(str(candidate), output.getvalue())
            self.assertIn('provenance', output.getvalue().lower())
            observed.append(candidate)
        self.flash_mock.side_effect = fake_flash
        with redirect_stdout(output):
            self.module.compile_candidate(25)
        self.assertEqual(1, self.flash_mock.call_count)
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)
        self.assertEqual(self.before, input_bytes(self.root))
        self.assertTrue(observed[0].is_dir())

    def test_d071_transport_failure_propagates_restores_root_and_retains_candidate(self):
        observed = []
        def broken_flash(args):
            observed.append(self.module.board_tool.ROOT)
            raise subprocess.CalledProcessError(23, ['synthetic-compile'])
        self.flash_mock.side_effect = broken_flash
        with redirect_stdout(io.StringIO()), self.assertRaises(subprocess.CalledProcessError) as failure:
            self.module.compile_candidate(50)
        self.assertEqual(23, failure.exception.returncode)
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)
        self.assertTrue((observed[0] / 'provenance.json').is_file())
        self.assertEqual(self.before, input_bytes(self.root))

    def test_d071_compile_propagates_nonzero_integer_return(self):
        self.flash_mock.side_effect = None
        self.flash_mock.return_value = 19
        with redirect_stdout(io.StringIO()):
            self.assertEqual(19, self.module.compile_candidate(25))
        self.assertEqual(self.board_root, self.module.board_tool.ROOT)

    def test_d071_cli_rejects_missing_invalid_and_unknown_arguments_before_work(self):
        invalid = ([], ['--compile-only'], ['--log-hz', '25'],
                   ['--log-hz', '26', '--compile-only'],
                   ['--log-hz', '25.0', '--compile-only'],
                   ['--log-hz', '25', '--compile-only', '--match'],
                   ['--log-hz', '25', '--compile-only', '--upload'],
                   ['--log-hz', '25', '--compile-only', '--startup', 'default'])
        with mock.patch.object(self.module, 'prepare_source') as prepare, \
                mock.patch.object(self.module, 'compile_candidate') as compile_candidate:
            for args in invalid:
                with self.subTest(args=args), redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit) as failure:
                    self.module.main(args)
                self.assertNotEqual(0, failure.exception.code)
            prepare.assert_not_called()
            compile_candidate.assert_not_called()
        self.assertFalse((self.root / 'build').exists())
        self.flash_mock.assert_not_called()

    def test_d071_cli_valid_rates_and_nonzero_failure_status(self):
        for rate in (25, 50):
            with mock.patch.object(self.module, 'compile_candidate', return_value=None) as compile_candidate:
                self.assertEqual(0, self.module.main(['--log-hz', str(rate), '--compile-only']))
                compile_candidate.assert_called_once_with(rate)
        errors = ((ValueError('bad input'), 1), (OSError('missing file'), 1),
                  (subprocess.CalledProcessError(31, ['fake']), 31))
        for error, expected in errors:
            with self.subTest(error=type(error).__name__), \
                    mock.patch.object(self.module, 'compile_candidate', side_effect=error), \
                    redirect_stderr(io.StringIO()):
                result = self.module.main(['--log-hz', '25', '--compile-only'])
                self.assertEqual(expected, result)


ALLOCATORS = r'''
static unsigned allocations = 0;
extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t, std::size_t);
extern "C" void* __real_realloc(void*, std::size_t);
extern "C" void* __real_aligned_alloc(std::size_t, std::size_t);
extern "C" void* __wrap_malloc(std::size_t n) { ++allocations; return __real_malloc(n); }
extern "C" void* __wrap_calloc(std::size_t n, std::size_t s) {
    ++allocations; return __real_calloc(n, s);
}
extern "C" void* __wrap_realloc(void* p, std::size_t n) {
    ++allocations; return __real_realloc(p, n);
}
extern "C" void* __wrap_aligned_alloc(std::size_t a, std::size_t n) {
    ++allocations; return __real_aligned_alloc(a, n);
}
void* operator new(std::size_t n) {
    ++allocations;
    auto* result = __real_malloc(n ? n : 1);
    if (!result) std::abort();
    return result;
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void* operator new(std::size_t n, const std::nothrow_t&) noexcept { return ::operator new(n); }
void* operator new[](std::size_t n, const std::nothrow_t&) noexcept { return ::operator new(n); }
void* operator new(std::size_t n, std::align_val_t alignment) {
    ++allocations;
    const auto a = static_cast<std::size_t>(alignment);
    auto* result = __real_aligned_alloc(a, ((n ? n : 1) + a - 1) / a * a);
    if (!result) std::abort();
    return result;
}
void* operator new[](std::size_t n, std::align_val_t a) { return ::operator new(n, a); }
void* operator new(std::size_t n, std::align_val_t a, const std::nothrow_t&) noexcept {
    return ::operator new(n, a);
}
void* operator new[](std::size_t n, std::align_val_t a, const std::nothrow_t&) noexcept {
    return ::operator new(n, a);
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }
void operator delete(void* p, std::align_val_t) noexcept { std::free(p); }
void operator delete[](void* p, std::align_val_t) noexcept { std::free(p); }
void operator delete(void* p, std::size_t, std::align_val_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t, std::align_val_t) noexcept { std::free(p); }
'''

HARNESS = r'''#include "src/memory_probe.h"
#include <cassert>
#include <cstdlib>
#include <new>
#include <type_traits>
''' + ALLOCATORS + r'''
static unsigned api_calls = 0, probe_calls = 0;
[[noreturn]] static void forbidden() { ++api_calls; std::abort(); }
namespace fsm {
RobotResult Robot::step(const RobotInput&) { forbidden(); }
void Robot::reset() { forbidden(); }
}
namespace recorder {
ConsumeStatus AttemptRecorder::consume(const fsm::RobotResult&) { forbidden(); }
void AttemptRecorder::onRobotReset() { forbidden(); }
AttemptPhase AttemptRecorder::phase() const { forbidden(); }
const FrameBuffer& AttemptRecorder::frames() const { forbidden(); }
const logframe::EventBuffer& AttemptRecorder::events() const { forbidden(); }
const AttemptSummary& AttemptRecorder::summary() const { forbidden(); }
bool AttemptRecorder::incomplete() const { forbidden(); }
std::size_t FrameBuffer::size() const { forbidden(); }
const StoredFrame* FrameBuffer::at(std::size_t) const { forbidden(); }
}
namespace logframe {
std::size_t EventBuffer::size() const { forbidden(); }
const EventBytes* EventBuffer::at(std::size_t) const { forbidden(); }
}
extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_enter(void* fn, void*) {
    if (fn == reinterpret_cast<void*>(&memory_probe::probeStep) ||
        fn == reinterpret_cast<void*>(&memory_probe::probeConsume) ||
        fn == reinterpret_cast<void*>(&memory_probe::probeQuery) ||
        fn == reinterpret_cast<void*>(&memory_probe::probeReset)) ++probe_calls;
}
extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_exit(void*, void*) {}
void setup();
void loop();
static void checkAnchors() {
    using namespace memory_probe;
    assert(robot_address == &robot_owner && recorder_address == &recorder_owner);
    assert(abi_address == &abi);
    assert(step_address == &probeStep && consume_address == &probeConsume);
    assert(query_address == &probeQuery && reset_address == &probeReset);
    assert(allocations == 0 && api_calls == 0 && probe_calls == 0);
}
int main() {
    using namespace memory_probe;
    static_assert(std::is_same_v<decltype(robot_address), fsm::Robot* volatile>);
    static_assert(std::is_same_v<decltype(recorder_address), recorder::AttemptRecorder* volatile>);
    static_assert(std::is_same_v<decltype(abi_address), const Abi* volatile>);
    static_assert(std::is_same_v<decltype(step_address), StepProbe volatile>);
    static_assert(std::is_same_v<decltype(consume_address), ConsumeProbe volatile>);
    static_assert(std::is_same_v<decltype(query_address), QueryProbe volatile>);
    static_assert(std::is_same_v<decltype(reset_address), ResetProbe volatile>);
    assert(robot_address == nullptr && recorder_address == nullptr && abi_address == nullptr);
    assert(step_address == nullptr && consume_address == nullptr);
    assert(query_address == nullptr && reset_address == nullptr);
    assert(allocations == 0 && api_calls == 0 && probe_calls == 0);
    assert(abi.version == 1 && abi.record_bytes == 96 && abi.log_hz == 25);
    assert(abi.window_ms == 200000 && abi.frame_capacity == 5001 && abi.event_capacity == 4096);
    assert(abi.pointer_bytes == sizeof(void*) && abi.size_t_bytes == sizeof(std::size_t));
    const std::uint32_t sizes[] = {sizeof(fsm::Robot), sizeof(recorder::AttemptRecorder),
        sizeof(recorder::FrameBuffer), sizeof(recorder::StoredFrame), sizeof(logframe::EventBuffer),
        sizeof(recorder::AttemptSummary), sizeof(fsm::RobotInput), sizeof(fsm::RobotResult)};
    const std::uint32_t aligns[] = {alignof(fsm::Robot), alignof(recorder::AttemptRecorder),
        alignof(recorder::FrameBuffer), alignof(recorder::StoredFrame), alignof(logframe::EventBuffer),
        alignof(recorder::AttemptSummary), alignof(fsm::RobotInput), alignof(fsm::RobotResult)};
    for (unsigned i = 0; i < 8; ++i) {
        assert(abi.sizes[i] == sizes[i] && abi.alignments[i] == aligns[i]);
    }
    setup();
    checkAnchors();
    for (unsigned i = 0; i < 10000; ++i) { loop(); checkAnchors(); }
}
'''


class RecorderMemoryInertProbeTests(unittest.TestCase):
    def build(self, match=0, motors=0, empty_macro=False):
        temporary = tempfile.TemporaryDirectory(prefix='sumo-memory-probe-')
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        sketch = folder / 'probe'
        shutil.copytree(ROOT / BENCH, sketch)
        shutil.copy2(ROOT / 'src/config.h', sketch / 'src/config.h')
        for relative in ('core', 'hal'):
            # Header copies preserve real owner types; no production implementation is linked.
            for header in (ROOT / 'src' / relative).rglob('*.h'):
                destination = sketch / 'src' / header.relative_to(ROOT / 'src')
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(header, destination)
        (sketch / 'Arduino.h').write_text(
            '#pragma once\n' + ('#define EMPTY\n' if empty_macro else ''))
        macro_check = ('#ifndef EMPTY\n#error "EMPTY was not restored"\n#endif\n'
                       '#define TEST_STRINGIFY_INNER(value) #value\n'
                       '#define TEST_STRINGIFY(value) TEST_STRINGIFY_INNER(value)\n'
                       'static_assert(sizeof(TEST_STRINGIFY(EMPTY)) == 1U, '
                       '"EMPTY replacement text changed");\n'
                       if empty_macro else
                       '#ifdef EMPTY\n#error "undefined EMPTY became defined"\n#endif\n')
        public_include = '#include "src/memory_probe.h"\n'
        (sketch / 'harness.cpp').write_text(HARNESS.replace(
            public_include, public_include + macro_check, 1))
        sources = [sketch / 'p2_recorder_memory.ino',
                   *sorted((sketch / 'src').rglob('*.cpp')), sketch / 'harness.cpp']
        command = ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                   '-fno-exceptions', '-fno-rtti', '-finstrument-functions',
                   '-fsanitize=undefined', '-fno-sanitize-recover=all',
                   f'-DMATCH={match}', f'-DMOTORS_ALLOWED={motors}',
                   '-include', str(sketch / 'Arduino.h'),
                   '-I', str(sketch), '-I', str(sketch / 'src'), '-x', 'c++',
                   *map(str, sources),
                   '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=aligned_alloc',
                   '-o', str(folder / 'probe-test')]
        return folder, subprocess.run(command, text=True, capture_output=True, timeout=40)

    def test_d071_setup_and_10000_loops_publish_abi_and_exact_addresses_without_work(self):
        folder, result = self.build()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        run = subprocess.run([str(folder / 'probe-test')], text=True,
                             capture_output=True, timeout=10)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)

    def test_d071_arduino_empty_macro_is_restored_and_inert_probe_still_compiles(self):
        folder, result = self.build(empty_macro=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        run = subprocess.run([str(folder / 'probe-test')], text=True,
                             capture_output=True, timeout=10)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)

    def test_d071_positive_match_and_motor_definitions_reject_build(self):
        for match, motors in ((1, 0), (0, 1), (1, 1), (2, 0), (0, 2)):
            with self.subTest(match=match, motors=motors):
                _, result = self.build(match, motors)
                self.assertNotEqual(0, result.returncode)
                self.assertIn('static assertion', result.stderr)

    def test_d071_all_upload_startup_match_combinations_refuse_before_transport(self):
        board = load_tool().board_tool
        for match in (False, True):
            for startup in (None, 'default', 'immediate'):
                args = SimpleNamespace(sketch=BENCH, match=match,
                                       compile_only=False, startup=startup)
                with self.subTest(match=match, startup=startup), ExitStack() as stack:
                    blocked = [stack.enter_context(mock.patch.object(
                        board, name, side_effect=AssertionError(name + ' forbidden')))
                        for name in ('target', 'setting', 'require_transport', 'stage',
                                     'remote', 'sync_sources', 'verify_core', 'verify_inert_source')]
                    blocked.append(stack.enter_context(mock.patch.object(
                        board.subprocess, 'run', side_effect=AssertionError('subprocess forbidden'))))
                    with self.assertRaises(ValueError):
                        board.flash(args)
                    for call in blocked:
                        call.assert_not_called()


if __name__ == '__main__':
    unittest.main()

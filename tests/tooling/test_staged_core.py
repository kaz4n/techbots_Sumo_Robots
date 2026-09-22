# Checks that the actual staged pure core resolves its own Arduino source includes.
# Prevents host-only root include flags from hiding target staging failures.
# Run with unittest and g++; production sources are copied and compiled opaquely.
from pathlib import Path
import shutil
import subprocess
import unittest

import test_tools as tooling_fixture


class StagedCoreTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tooling_fixture.ToolContractTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.use_reviewed_sources()
        result = self.fixture.run_tool('bench/p0_timing', '--compile-only')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.fixture.assert_no_motion_command()
        self.stage = self.fixture.root / 'build/stage/p0_timing'
        self.core = self.stage / 'src/core'
        self.compiler = shutil.which('g++')
        self.assertIsNotNone(self.compiler, 'g++ is required; run this suite under WSL')

    def check_translation_unit(self, source):
        # Deliberately omit -I/-iquote and CPATH-style environment search paths.
        env = dict(self.fixture.env)
        for variable in ('CPATH', 'CPLUS_INCLUDE_PATH', 'C_INCLUDE_PATH', 'OBJC_INCLUDE_PATH'):
            env.pop(variable, None)
        result = subprocess.run([self.compiler, '-std=c++17', '-Wall', '-Wextra',
            '-Werror', '-fno-exceptions', '-fno-rtti', '-fsyntax-only', str(source)],
            cwd=self.fixture.root, env=env, text=True, capture_output=True,
            timeout=30, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_every_staged_core_cpp_compiles_without_a_project_root_include_flag(self):
        sources = sorted(self.core.rglob('*.cpp'))
        self.assertTrue(sources, 'The fixture must contain actual production core sources')
        for source in sources:
            with self.subTest(source=source.relative_to(self.stage).as_posix()):
                self.check_translation_unit(source)

    def test_every_staged_public_core_header_compiles_standalone_without_root_include_flags(self):
        headers = sorted(self.core.rglob('*.h'))
        self.assertTrue(headers, 'The fixture must contain actual production public headers')
        probe = self.fixture.root / 'standalone_header.cpp'
        for header in headers:
            with self.subTest(header=header.relative_to(self.stage).as_posix()):
                probe.write_text('#include "' + header.as_posix() + '"\n', encoding='utf-8')
                self.check_translation_unit(probe)


if __name__ == '__main__':
    unittest.main()

"""D235 historical-eight profile and current-six config registry checks.

The inherited native/FIFO cases retain their public guard and byte oracles.
Only copied historical config changes back to eight; production stays at six.
"""
from contextlib import ExitStack
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from . import test_configured_setup as setup
from . import test_dump_uart_fifo as fifo
from . import test_runtime_config_registry as registry

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P7_dump_six_store_raw/config'


class HistoricalEightTests(fifo.DumpUartFifoTests):
    STEP_BYTES = 8


class ConfigTests(unittest.TestCase):
    def run_registry(self, wrong=False):
        additions = {name: 0 for name, _ in setup.FLAGS}
        additions.update(APP_DUMP_ORIGIN=0, APP_DUMP_RECEIVE_STREAM_ID=0,
                         TICK_DISTRIBUTION_LIMIT_US=800, APP_MOTOR_OBSERVE_EPOCHS=10000,
                         APP_MOTOR_OBSERVE_MAX_POLLS=10000000)
        with tempfile.TemporaryDirectory(prefix='d235-config-') as directory:
            project = ROOT
            if wrong:
                project = Path(directory)
                (project / 'src').mkdir()
                (project / 'docs').mkdir()
                shutil.copyfile(ROOT / 'docs/BEHAVIOR.md', project / 'docs/BEHAVIOR.md')
                source = (ROOT / 'src/config.h').read_bytes()
                self.assertEqual(source.count(b'DUMP_UART_STEP_BYTES = 6U;'), 1)
                (project / 'src/config.h').write_bytes(source.replace(
                    b'DUMP_UART_STEP_BYTES = 6U;', b'DUMP_UART_STEP_BYTES = 8U;'))
            with ExitStack() as patches:
                patches.enter_context(mock.patch.dict(registry.legacy.BEHAVIOR_EXTRA_DEFAULTS, additions))
                patches.enter_context(mock.patch.dict(registry.legacy.BEHAVIOR_DERIVED_TYPES,
                    {'APP_IMU_BODY_AXIS[3]': 'std::int32_t', 'APP_DUMP_SESSION_ID': 'std::uint64_t'}))
                patches.enter_context(mock.patch.object(registry, 'RAW', RAW))
                case = registry.RuntimeConfigRegistryTests('runTest')
                case.run_registry('D235-wrong-eight' if wrong else 'D235-current-six',
                                  project, expected_failure=wrong)

    def test_current_six_runs_all_18_legacy_config_checks(self):
        self.run_registry()

    def test_old_eight_is_refused_by_current_value_assertion(self):
        self.run_registry(wrong=True)

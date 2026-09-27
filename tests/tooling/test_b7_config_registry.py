"""Register approved D243/D244 literals without weakening the legacy registry.

The existing eighteen checks still reject extra declarations and value drift.
The inherited wrong-UART-width fixture remains a required negative control.
"""
from contextlib import ExitStack
from decimal import Decimal
import unittest
from unittest import mock

from . import test_dump_six_store as previous


class ConfigTests(previous.ConfigTests):
    def run_registry(self, wrong=False):
        expected = dict(OUTER_LOOP_WINDOW_US=300000000, BROWNOUT_CYCLES=20,
                        BROWNOUT_DWELL_MS=500, BROWNOUT_REACH_MS=1000,
                        BROWNOUT_RECEIPT_MAX_GAP_US=2000)
        with ExitStack() as patches:
            patches.enter_context(mock.patch.dict(
                previous.registry.legacy.BEHAVIOR_EXTRA_DEFAULTS, expected))
            patches.enter_context(mock.patch.dict(
                previous.registry.legacy.BEHAVIOR_EXTRA_FLOAT_DEFAULTS,
                {'BROWNOUT_FULL_DUTY': Decimal('1.0')}))
            patches.enter_context(mock.patch.object(previous, 'RAW',
                previous.ROOT / 'state/analysis/P2_b7_brownout_raw/config01'))
            super().run_registry(wrong)


if __name__ == '__main__':
    unittest.main(verbosity=2)

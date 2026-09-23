"""Recheck only changed failure/clock paths against final opaque D104 sources."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from tests.tooling.test_runtime_bench_runner import RuntimeBenchRunnerTests

class FinalFailureRecheck(RuntimeBenchRunnerTests):
    def command(self, argv, expected=0):
        values = list(map(str, argv))
        if len(values) == 2 and values[1] == "--no-colors":
            values += ["--test-case=*regression*,*stall*"]
        return super().command(values, expected)

FinalFailureRecheck().test_actual_runtime_contract_normal_sanitizer_and_compile_refusals()


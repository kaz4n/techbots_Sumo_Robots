# D170 first-run fixture failure

Preserved commit: 0160d1a6. Original independent test be241bb7 and all nine
frozen inputs remain exact. Raw: P7_motor_fault_raw/fresh_stage_first.json.
WSL Python3.12: 25 pass, one Windows-only junction skip. Windows Python3.13.11:
16 pass, one failure, nine symlink-privilege skips. Actual Windows junction passes.

The failure is `test_copy_failure_retains_partial_bytes_and_consumes_attempt`:
the expected injected OSError did not occur. The fixture patched stdlib
`shutil.copyfile`. Read-only inspection of the installed Windows Python3.13.11
`shutil.copy2` shows its `_winapi.CopyFile2` fast path returns without calling
copyfile. The fixture therefore did not inject a failure on that host. This is
not evidence that production discards a failed copy; production is unchanged.

Correction assigned to the independent author: inject at the cross-platform
copy2 boundary, perform the real copy first, then raise. Preserve the same
assertions for the exception, actual copied bytes, exclusive owner consumption,
legacy sentinel and no retry. Freeze corrected fixture before rerunning both
platforms and legacy staging regressions. No locked test or assertion is relaxed.

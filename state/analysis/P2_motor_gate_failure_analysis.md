# D075 retained failures and repairs

- C: free0 prevented WSL swap creation. Automatic approval review rejected
  recursive generated-build cleanup. Narrow removal of two independently verified
  untracked generated executables succeeded; exact paths/hashes/bytes retained in
  P2_motor_gate_environment.md. No source/evidence deleted. RAM builds used next.
- First build: `P2_motor_gate_host_build.txt` retains compiler diagnostics;
  `P2_motor_gate_test_first.cpp.txt` retains original independent draft. The
  doctest exception-disabled mode disallows REQUIRE; one && expression also
  needed parentheses. Test author replaced prerequisites with CHECK_MESSAGE plus
  abort-on-failure and parenthesized the predicate, retaining every expectation.
  Added stronger cases before establishment. No existing locked test touched.
- Initial shell receipt trailer failed to preserve its shell exit variable;
  compiler errors still clearly show failure. A subsequent host_build.json records
  exact exit1 because the RAM directory was absent on a later WSL invocation.
  A sanitizer command separately failed PowerShell parsing of unquoted comma.
  No second production/test repair was needed: use argv-based Python receipts
  and one continuous WSL configure/build/test process. All final steps exit0.
- First target symbol extraction succeeded but its output filename collided with
  the command receipt. Renamed to target_elf_symbols.json, repeated only read-only
  extraction. Original/retry command receipts retained; no new compilation/run.
- Reviewer noted C-linkage setup/loop absent from initial disassembly selector.
  Preserve target_elf_symbols_initial.json, extend selector to exact plain symbols,
  capture target_symbols_complete.json/target_elf_symbols.json, exit0. No firmware
  or test change. Final source/static and normal/sanitizer runtime tests pass.

No assertion weakened, no skipped failure, no fabricated hardware success.

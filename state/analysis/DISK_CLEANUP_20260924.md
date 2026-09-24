# Disk cleanup, 24 September 2026

User-authorized cleanup completed during P4 D129 validation. Free space on C:
rose from approximately 90 MiB to 3.33 GiB. Readings can move as Windows writes.

- Removed inspected, closed old RDP traces (1,335,373,824 bytes), six old Python
  crash dumps (135,489,953 bytes), and fourteen previous motor-analysis temporary
  artifacts (87,954,144 bytes). Exact paths and observations are in
  `P4_timing_evidence_raw/temp_inventory.json`.
- Removed only the two generated host executables and their compiler-object
  directories in each of `build/host` and `build/host-sanitize`. CMake caches,
  test logs and dependency downloads remain; these outputs can be rebuilt.
- Applied transparent NTFS compression to `state/` only. `compact.exe` exited 0,
  reporting 2,495,793,787 logical bytes stored in 819,448,297 bytes. Future files
  in these directories inherit compression; paths and file contents are intact.
- Verified every one of the 21,145 preexisting evidence files against its saved
  size and SHA-256: zero missing files or mismatches.

Preserved source, tests, Git history, evidence, current diagnostic information,
active Word diagnostics and all persistent WSL/Docker virtual disks. A subsequent
inventory found three RDP paths had reappeared; no newly created trace was deleted.
No pre-development disk inventory exists, so this does not identify the entire
reported 9 GB decrease. No global service or WSL settings were changed.

Evidence: `P4_timing_evidence_raw/disk_cleanup.json`,
`evidence_before_compression.json`, `evidence_after_compression.json`, and
`temp_inventory.json` in the same raw directory.

The concurrent D129 jobs were interrupted by a recorded WSL service termination,
not a completed test failure. Partial logs are preserved separately. Retry host
validation serially, using the existing RAM-backed `/dev/shm` build directories.
Hardware and human phase gates remain pending.

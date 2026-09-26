# D223 actual UART holder observation review

Date: 2026-09-26. Independent read-only review of saved local evidence. No board
commands, authentication, observer execution or test suite was run by this
reviewer. The sealed source review remains unchanged.

## Findings and reconciliation

No open finding in this bounded observation. The reviewer independently
reconciled all five intent pins against current bytes, reconstructed the full
compressed-source argv without executing it, and verified the fixed ADB binary
hash. The argv is exactly the admitted read-only observer, serial `2629958581`,
5890 Windows command units. The saved invocation and transport records reference
the same 7382-byte intent, SHA-256
`ffbed823d46dcc6b900bfcd0d2e82e7319d66b34c6870a0f0d02711ac8375cc0`.

`state/analysis/P7_uart_holder_raw/observation_transport01.json` records one
completion with return code 0, no first error, no closing errors, all five inputs
unchanged and 14.380782 seconds elapsed. The 5459-byte stdout independently
matches SHA-256
`8380134796ac20aeab649e52ba4feacc22a75bc6dccd020ee7b69df8bc5c1be5`;
stderr is empty with the expected empty-file hash. The existing invocation owner
is consumed; this review creates no retry or new admission.

## Observed visibility

The saved report is `sumox-uart-holders-v1`, UTC
`2026-09-26T18:36:05.811832+00:00`, and reports `SAMPLED_COMPLETE`:

- Both sweeps examined 165 processes, 275 tasks and 3082 logical FD-stat attempts.
  They took 0.234668 and 0.202351 seconds. Each records zero problems and no
  detail truncation; both are complete. No error, cap or detected race is recorded.
- Logical FD-stat attempts total 6164; actual budgeted FD stats total 6180,
  including the observer's own FD-directory validation. Overall observer elapsed
  time is 0.554964 seconds. These are Linux observation durations, not MCU timing.
- Before/after boundary objects are exactly equal, as are both holder lists and
  holder-process identity maps. Root UID/GID triples `[0,0,0]`, supplementary
  groups `[0]` and capabilities are recorded at both boundaries.
- The observed boot is `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, kernel
  `6.16.7-g0dd6551ae96b`. `/dev/ttyHS1` is character device 239:1,
  filesystem device 6, inode 148.
- The only observed holder process is PID 568, `arduino-router`, process start
  1514. Descriptor 7 is exposed in task tables 568, 581, 582, 583, 584, 585, 592,
  597, 599 and 600 in both sweeps. These ten task-table rows do not establish ten
  separate opens or distinct open-file descriptions.
- The router executable is `/usr/bin/arduino-router`, 6095032 bytes, SHA-256
  `3eacd38a9c813209f6985951869105600824e4f7c54a1111a8d48ef094cc1a19`.
  Its recorded path/stat/hash and process identity match at both boundaries;
  holder executable metadata matches that boundary identity.

## Verdict and limits

FINAL PASS for the saved, bounded holder-visibility evidence. The previously
uninspected protected descriptors were visible in these two complete sweeps;
the router was an observed holder, so this is not evidence of an unused UART.

No transient activity between metadata reads or continuous exclusivity is proved.
`continuous_exclusivity`, `framing_clean` and `receiver_ready` all remain
`UNKNOWN`. This observation supplies no UART-open/setup grant, last-close or DMA
completion proof, positive reopen/delivery result, service/RPC change, MCU
operation, motor-run permission, physical acceptance or human phase gate.
Mandatory motor inhibition is unchanged. Stop this one-time operation; retain
the receipt and carry these limitations into any separately scoped next step.

# D076 opponent GPIO scoped review — 2026-09-23

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed D076 software scope.

## Verdict

**PASS** for the checked native opponent driver, independent host contracts,
compile-only probe and exact five inert guard updates. This is not a P2 gate,
physical B1 acceptance, pin approval or permission to upload/run the probe.

Separate newly spawned same-model reviewer; no production implementation,
contract-test or board changes by this reviewer. Review compared the working
tree with `a806e05`, including contract commits `98adcda` and `3c39bc4`.
Only this report and `P2_opponent_review_*` receipts were written by the reviewer.
Actual local date was Wednesday 23 September, before PLAN section 3's scope-cut
and freeze dates. D075 changes software eligibility, not human acceptance.

## Source and contract checks

- `src/hal/opp_sensors.cpp` SHA256
  `68ce44dad67ec3264fba927d8ccf0eebc7d3199ceed2e9b0ace81ad840b53bc1`
  implements the actual Arduino-conditioned native path. All mappings are checked
  before configuration: bounds, nonnull port/config, zero DT flags, representable
  and supported pin bits, and duplicate physical port/pin pairs. A malformed bank
  invalidates earlier readiness and returns seven `-EINVAL` statuses without
  native configuration. There is no alternative host-success implementation.
- Valid setup attempts all seven channels independently, checks readiness before
  configuration, passes only GPIO_INPUT and preserves every signed configure
  result. Only seven successes establish readiness. An explicit later begin is
  the sole recovery from failed initialization; there is no retry loop.
- Uninitialized reads perform no readiness, GPIO or clock operation. Initialized
  reads make at most seven readiness checks and seven native reads, bracketed by
  two micros observations. Native failures and unexpected positive results remain
  explicit; valid_mask/raw_mask contain only valid readings. Each snapshot is
  newly initialized, so stale bits do not survive. Read failure permits a later
  explicit read to recover without inventing a successful sample.
- HAL preserves electrical levels. Core `opp_fusion::Debouncer` still owns the
  single OPP_ACTIVE_LOW_MASK conversion and debounce. No behavior, motor write,
  output/pull flag, heap allocation, wait, Bridge operation or unbounded loop is
  introduced into the driver. Setup bank comparison is bounded by 21 pairs.
- `src/config.h` adds only the seven existing proposed HARDWARE section 3 pins,
  in FL15/FC/FR15/SL/SR/RL/RR order: 11/12/13/16/17/18/19. Installed mapping is
  PB15/PB14/PB13/PA6/PA7/PC1/PC0, all flags zero. All 76 B16 values are unchanged.
  The config test amendment explicitly validates the proposal's type, extent and
  values while retaining the original default checks.
- Existing locked tests, core, app entry and board upload tool are unchanged
  against the review base. No rule R1–R6 behavior or motor-write authority changes.

## Independent test evidence

Reviewed `tests/tooling/test_opp_sensors.py` and its independent native fixtures.
The fixtures compile the same production cpp with strict C++17, warnings as
errors, no exceptions/RTTI and UBSan. They exercise every electrical mask, all
seven failure positions and signed/positive statuses, retries/recovery, mixed
failures, malformed maps, highest representable bit, same-number pins on distinct
ports, timestamp wrap, allocation guards and exact native-call bounds. Real core
composition confirms polarity is applied once. Probe startup and 10,000 loop
calls perform no native I/O; a motor-enabled probe fails its static assertion.
The retained `../analysis/P2_opponent_raw/installed_typedefs.json` confirms the
fixture widths against the same installed gpio.h hash: pin uint8_t, DT flags
uint16_t, GPIO flags and port mask uint32_t. Installed zephyrCommon.cpp:17 also
confirms micros returns unsigned long. These substitutes model API arguments
and outcomes, not a physical GPIO-fault experiment.

Reviewer reproduced:

- 18 native unittest methods, **PASS**, 46.168 seconds, exit 0:
  `P2_opponent_review_native_tests.txt`.
- The subsequent strengthened device-mask test, which first establishes ready
  state then invalidates the map and retries begin: **PASS**, all seven slots,
  1.080 seconds, exit 0: `P2_opponent_review_mask_retry.txt`.
- Nine config checks, **PASS**, 0.083 seconds, exit 0:
  `P2_opponent_review_config_tests.txt`.
- Eight independent default/Immediate, MATCH0/1, ADB/SSH upload rejections,
  all before target lookup or transport: `P2_opponent_review_upload_rejections.json`.

Initial independent-author probe failures were fixture staging errors: temporary
`src/config.h` was missing. The failure predicates were preserved and the fixture
copies the actual config now; no production repair or weakened assertion followed.
The reviewer's separate first upload-check harness caught the wrong exception
class; the tool already rejected correctly. Its ValueError-only harness repair
and initial error are retained in the rejection receipt.

The coordinator's normal host receipt also passes both existing CTest targets.
Aggregate final tooling/sanitizer jobs were still running at review completion;
this verdict does not claim their later results. The focused UBSan replay above
is this reviewer's independently reproduced evidence.

## Actual target and startup evidence

Successful target compile receipt reports source
`ef44ace309afc50dfdd85c583e22a74c76ddbe6e06108809a878b3555416c9f8`,
MATCH0/MOTORS_ALLOWED0/default startup, exit 0, 76308 bytes program and 31032
bytes compiler-accounted memory. Reviewer independently matched all 36 staged
files to current source and that aggregate hash; see
`P2_opponent_review_target_source.json`. These size figures are not free-RAM or
loader/runtime acceptance measurements.

Reviewed all three ELF records in `../analysis/P2_opponent_raw/target_elf.json`.
The upload-format ELF SHA256 is
`1cb841b0d2a146d06f4c09bdf95b538ab34f943df5c365c6265cb373f49fbe71`.
Actual retained begin/read/exercise bodies use inline device-API dispatch for
configure/raw read; no undefined named z_impl_gpio_* wrapper is used. Every one
of the 31 collected native device/clock exports resolves nonzero. Selected
GPIOA/B/C callbacks and masks agree with installed audit/raw evidence; the raw
audit SHA256 independently matches `cfc9e52a8d1a7ed7e56180c4bad8d469224d3001e0f5229cbff5cbe1618cbca1`.

Target setup at 0x6c only stores the exercise address; loop at 0x7c returns.
Exercise is referenced by that retained pointer and invokes actual begin/read;
startup does not invoke it. All five init-array entries were traced. The two
new translation-unit initializers only establish inherited RouterBridge HCI
metadata, with no GPIO calls. initVariant immediately returns. Sketch and base
static-thread start/end symbols are equal. Inherited __loopHook still includes
K_FOREVER mutex acquisition and conditional Bridge.update_safe: F091's runtime
limitation remains open. This is GPIO-inert compile-only preparation, not a claim
that the complete inherited platform runtime is bounded or allocation-free.

## Exact inert guards

`P2_opponent_review_manifest.json` independently recomputes the original five
source maps. Relative to their reviewed D075 maps, each has exactly one changed
file (config.h), two additions (opp_sensors.cpp/h) and no removal. Existing
sketches instantiate no Sensors object. The final `tools/p0_inert_sources.json`
was checked after refresh and exactly matches these approved five hashes; no
new upload allowlist entry exists. The board tool's earlier rejection remains
unchanged and was independently exercised without board access.

## Limits and next action

The installed source/binary audit supports bounded instruction paths, not measured
WCET or injected MCU faults. Native success cannot detect wrong voltage, broken
wires, stuck/floating signals or another peripheral reclaiming a pad. Preserve
SPI2/Wire2 and direct same-pad API exclusions, and serialize GPIO configuration
including register/metadata sharing on the same ports. Per-channel PWM/ADC pinctrl
behavior must not be confused with remuxing every listed pin.

Future app integration must require Snapshot.valid before forwarding raw_mask
as fresh input and must define/test its fault policy. This change supplies no
app integration, live matrix/range/60-second false-hit evidence, physical polarity
or ownership proof, full-loop WCET, PINMAP OK, human phase gate, upload/reset or
motor-run authorization. Continue P2 software under D075 while retaining those
explicit acceptance dependencies.

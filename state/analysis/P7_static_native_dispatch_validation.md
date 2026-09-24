# P7 direct native driver boundary: file evidence

25 September 2026, Asia/Dubai. The selected current application/native GPIO,
PWM, RCC and device-init call boundary is now identified from actual files.
This is not firmware execution or a complete native operating-system audit.
Source remains `fcddbd8e`; static final ELF `5cc2dfde`, debug ELF `0f7f2825`,
packaged loader `39d4a4fd`. No source/config/test change, compiler, upload,
reset, motor run, physical result or phase gate occurred.

## Evidence and preserved failure

- [GPIO audit](P7_static_gpio_dispatch_audit.md): actual MotorGate, QTR and
  opponent calls, selected application DWARF, pinned installed GPIO header.
- [PWM audit](P7_static_pwm_dispatch_audit.md): actual set/get calls, M0 nonzero
  rejection, expanded application callback types, retained clock selection.
- [RCC/UART audit](P7_static_rcc_dispatch_audit.md): actual direct RCC calls,
  optional UART initialization, retained native helper and setup limitations.
- [D150 result](P7_static_link_probe_raw/native_api/result.json) remains
  **NATIVE_API_READ_FAILED**. All five commands returned0 and all postchecks
  passed, but GDB emitted `No function contains specified address.` for the
  by-name initialization disassembly. Its `whatis` found a const void pointer;
  49 other query sections are useful partial observations. The original error,
  empty section and failed result are unchanged. D150 was not retried.
- [Partial comparison](P7_static_link_probe_raw/native_api_partial_comparison.json)
  records coordinator interpretation of those sections. No whole-collection
  pass is substituted. [D150 review](../reviews/P7_static_native_api_review.md)
  separately confirms this distinction.
- D151 GO `a60ef466` scoped only the missing18-byte numeric address range.
  [Actual result](P7_static_link_probe_raw/native_init/result.json) is
  **NATIVE_INIT_QUERIES_COLLECTED**: five read-only commands returned0, no
  stderr/postcheck errors, no compiler/property queries. Exact captured source
  `4c39fafc` stayed unchanged; original source/stage/installed/file identities
  remained bound. The sole new body is in [0003.json](P7_static_link_probe_raw/native_init/0003.json).

## Direct boundary conclusions

The two ELF files agree on device size36, api+8, ops.init+20, device_ops size8,
PWM API size8 and its set/get slots0/4, clock API size28 and on slot0,
stm32_pclken size8 with bus12/div20/enr at+4, and PWM flags unsigned short.
GPIO layout40 and the used configure/read/set/clear slots0/4/12/16 agree.
GPIO scalar widths are int4, pin1, flags4, port value4 and mask4. The unused
manage_callback prints C++ bool versus native C _Bool; this report does not
claim every callback was compared or exercised. The GPIO native prototypes
match the used application/header signatures. PWM typedef chains are separately
expanded in the PWM supplement; the RCC call sites pass device/subsystem
pointers and inspect the integer return, matching the observed native on routine.

D150 repeats all nine selected native device values and the three driver
vectors. Those offsets/targets match the actual application instruction chains
in the companion reports. M0 rejects EN-high and nonzero PWM requests before
their driver dispatches. It still performs GPIO/PWM initialization; optional
ADC/IMU/QTR/opponent/UART services remain disabled by current SetupGrants{}.

The missing wrapper is now observed at `[0x08019e5c,0x08019e6e)`:
it reads device.state at+12, tests initialized bit0 in state byte1, returns
integer -120 if set, or tail-branches at0x08019e64 to do_device_init0x08019e2c
with the device argument unchanged. The retained helper loads ops.init at+20,
calls it if non-null, stores a bounded error magnitude and marks initialized.
This closes the wrapper-to-helper-to-selected-PWM/UART-initializer edge that
the earlier RCC/PWM notes correctly left pending. No additional native read is
needed for this particular edge; their historical pending text remains provenance.

## What remains

These observations close the selected direct driver dispatch evidence gap.
Packaged internal reset/pinctrl/clock/kernel behavior is inherited dependency,
not recursively proven by these checks. Optional UART setup's known TEACK/
REACK/exclusive-access waits remain explicit and its grants remain false.
Native loading/startup, ownership in the running image, stack/heap/WCET,
matrix behavior and physical acceptance still need actual qualification.
Production admission is still dynamic-only, and its modeled592B deficit remains.
No static deployment path is adopted by this report.

Next original-scope task: prepare the smallest reviewed, source-bound bare-board
M0 static startup qualification using the existing checked packet and a verified
upload/observation path; establish the precise allowed run and observations
before any upload. Reuse current artifacts and retained tooling evidence.
Do not rebuild, add another source snapshot, request more hardware, or infer a
motor-run grant from the file audit. Existing human gates stay pending.

Storage: no new compiler tree or binary copy was created. Retain compact actual
receipts and these scoped reports. Repeated full disassembly/DWARF stayed in RAM.
This turn's separate cleanup saved about49.9MiB through content-preserving
compression and Git internal packing; see [STORAGE_LOG](../STORAGE_LOG.md).

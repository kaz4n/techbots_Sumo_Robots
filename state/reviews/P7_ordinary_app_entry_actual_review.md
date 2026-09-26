# D210 ordinary application actual entry review

FINAL ACTUAL PASS, 2026-09-26. This accepts the single saved file-only observation and the selected emitted instructions, within the limits below. No material discrepancy remains. The native owner is consumed; this review does not authorize a retry, expanded query, upload or runtime operation.

This is a separate same-model review with reused project context, not human or cross-model review. The lead reviewer independently reconciled provenance, the complete transported program, all group geometry and symbols, and groups44-63. Separate same-model reviewers inspected groups0-28 and29-43 against the actual saved instructions and source, and supplied scoped PASS reports incorporated below. The oracle author contributed the latter actual-evidence review after oracle/source barriers had closed; these semantic conclusions do not come from synthetic fixtures. No reviewer imported/executed a subject, ran a test, or made a device call. Only this review was written.

## Exact accepted evidence

Paths abbreviated RAW are under `state/analysis/P7_ordinary_app_static_compile_raw/`; NATIVE is its `native_entry_static01/` directory.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| RAW/entry_binding01.json | 106946 | 36cafffcfebc647b5019b438705fa42a8be94edfb5d8b67deac2508878c6ae89 |
| RAW/entry_native_scope01.json | 4398 | 87e79080f327910690477a53950e17b8ea335bce4605e235e91844b374039842 |
| RAW/entry_native_invocation01.json | 1363 | 18a0a68974d8c0fac3b9868cb47e3bbe7158a8324d6908d471635134aef8af69 |
| NATIVE/inputs.json | 25170 | e8857e738f91702ba0eab787a4eafc2869b0cc70a7463b6422646d5374a97832 |
| NATIVE/result.json | 708200 | 0daff4f15d41142f5d381fff227d2252cb9cf255c0e3b30891ca834df85f84eb |
| NATIVE/entry.json | 21583 | 8cb90c514ffc6a9e1f04c8ea601ec3f70e5c49c45017e6da88a9753026298f85 |
| NATIVE/local_result.json | 277 | c922d19e429f219befb37a3f7d48b1b5051dab39526a4176d1c6216f1e89b8ce |
| NATIVE/0001-file-entry/intent.json | 5567 | 46071580d2db6ca9b7ea76a1eb09c57afde12645532ac64f6a90519dbd90af6d |
| NATIVE/0001-file-entry/result.json | 5586 | a3593c9f76fa65000a47fb34a848956f06eed86a38d4deccc03b78fb79a5c4bb |
| NATIVE/0001-file-entry/stdout | 705201 | 054425f130efef3e1844920c52b66b530fd7f899ef1752d3cce9bd32f1d0c4c1 |
| RAW/entry_native_closing01.json | 6157 | 66477a387ef406dfac768769202bbbc66d55331cf6575e99ca8d70b9c2574a32 |

Transport stderr is empty, SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855. Eight native files total1471584 logical bytes; invocation/closing are additional compact receipts. Source/host review10497B/ca0104db53338a3148f0fb5c080ed5944893786858499ee4d026818df71d0ae9 and admission6561B/3a1aa879d6184aba5f9b76aaa99a75f278fb6cec507510b75e70293188bc4b32 remain immutable prerequisites.

## Provenance, exact command and closure reconciliation

The saved invocation binds clean reviewed commit `f14ff870779987b9552bb14782b97cea11c7457a`: check-only returned0 in0.5631879s and execute returned0 in2.6265711s. Its printed check object agrees with inputs.json and its printed execution object equals local_result.json. Local attempt timestamps are2026-09-26T13:33:20.656499Z through13:33:22.640292Z. Local closure records one transport, PASS, no first error. The retained caller enforces the reviewed commit and permits only its newly claimed untracked owner during closure.

Independently hashed all171 coordinator,15 scope and141 runtime-local pin roles:174 unique files match both current working bytes and blobs at the native commit. This includes the125-file ordinary manifest and accepted D208/D209 artifacts/evidence. Source remains9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a, ordinary app.ino/default static/MATCH0/MOTORS_ALLOWED0/probe0, with all17 setup grants absent. The D210 wrapper remains18546B/5bcb6e12424237cb2701d271e2704281dedca76688d786eac1076daf8f9b3e0b. No source, oracle, manifest or scope change is needed for acceptance.

Strict JSON parsing rejected duplicate keys/nonfinite constants; raw transport stdout parses to the saved result exactly. Checked result/command schemas, canonical base64 and exact decoded stream lengths, all four argv arrays, serial child order, execution returncode0/timed_out=false/reaped=true, empty errors/stderr,60s child deadlines and5s reap bounds. The transport result is its exact saved intent plus returncode0: serial2629958581, one `adb shell -T`, sanitized environment, Python-I-B,400s transport limit and5457 UTF-16 units including NUL, below30000.

Decompressed the saved bootstrap as data and independently reconstructed the entire program from pinned historical identity/wait/read literal bodies, current eight artifact pins, two tools, loader/TLS pins and binding-derived commands. It matches byte-for-byte:13818B/SHA2564021bf0754d1ae35d3e041967c4ca55852de104819cc97740c8bb3dbe048dca9. This was AST/literal reconstruction, not subject execution. Exact four children are readelf--version, gdb--version, readelf-hSWs-x.init_array on ordinary app.ino.elf, and fixed GDB disassembly of ordinary app.ino_debug.elf with -nx/-nh/-batch, auto-load disabled and may-call-functions off. The latter requests64 fixed ranges plus65 markers,129 range/marker expressions. No target connection, compiler, upload, reset, MCU read, privilege operation, remote owner creation or dynamic expansion appears in the transported program.

| Child | stdout bytes | stdout SHA256 | Elapsed seconds |
|---|---:|---|---:|
| readelf version | 283 | fb0fb06d29e07100d474b8370bcc7cc304258189feab180bc678c9c0abdff851 | 0.011451005935668945 |
| GDB version | 281 | a2ba24fa1b25ad3c6b26e5fcf0e715f1eeb4a8480434761ed9f4c7682bb12438 | 0.07256317138671875 |
| ELF/symbols/init array | 153891 | c97bc4ccb6f12f831b3238799b6a83f2bf412cbfc21bffdbe07a12e76f4d8ab2 | 0.0320124626159668 |
| Selected disassembly | 367877 | dd8717cd5363c014b38edb6114448a1ef5b3a803b61d514cfabc424ba11c480b | 0.44327259063720703 |

All child streams stay within1MiB; the transport reply stays within8MiB. Opening identity is arduino/UID1000, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, pinned CLIb878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433, conflicts[], and free13892366336B. Remote ancestry, inherited resource limit and absence of the entry scope were checked by the exact program before children. All12 opening hashes and their final dev/inode/size/mtime/ctime comparisons passed; final UID/boot check passed. The saved13 closing rows exactly follow program insertion order: eight artifacts, gdb, readelf, loader, TLS, board identity. JSON-sorted inputs are not a different execution order. The remote absence check is an opening condition; no separate post-use absence or whole-filesystem inventory is claimed.

Root closure is independently reconciled to every native file, four decoded stream pairs, timings, counts and local closure. Its reported C:free5906980864B is a saved resource observation, not reclaimed space. Root's first purely local audit wrongly expected globally sorted closing paths and refused before receipt write; the corrected ordered-pin audit is recorded. This reviewer also corrected three local data-audit assumptions before final passing reconciliation: composed TOOLS expressions require bounded AST string resolution, a constructed GDB marker had an extra backslash, and binding startup bounds are rows rather than the summary dictionary. None was a subject/native failure, changed evidence or caused a subject/test/device retry.

## Complete selected geometry and symbol evidence

Independently parsed every raw group, exact header/end, address row and opcode width:64 groups,77 aliases,10420 selected bytes,3688 contiguous dump rows and65 ordered markers. Every recomputed raw block hash, byte count, row count, name, address and alias list equals entry.json and the binding. These rows include literal-pool words displayed as misleading ARM mnemonics; they are not an executed instruction count. All2234 fresh symbol rows, indices0..2233 including unnamed row0, equal the accepted D209 table. Every selected alias tuple and all six initializer-bound tuples reconcile. The actual .init_array bytes at0x081158f0 are01011008, little-endian Thumb pointer0x08100101; its end is0x081158f4. All other five startup bounds are0x081158f0.

The following covers every selected group. Source/member names qualify interpretation where the selected instruction bytes alone do not name the member. Calls to unselected bodies are identified as calls, not acceptance of their interiors.

### Groups0-28: startup, binding and all constructor aliases

| Groups | Actual selected behavior |
|---|---|
| 0 entry_point | Copies208B from0x08116a40 to0x20013890 and zeros[0x20013960,0x2003c6c8),167272B. Empty preinit list; one initializer call through the observed word. Earlier calls to external0x080173d5 are unselected, so whole-entry silence/no-I/O is not established. Zeroing does not extend to .bss end0x2003c800. |
| 1 setup;2 loop | setup forms21 zero grant bytes, calls Runtime::begin for0x20013960 and discards its bool. loop tail-calls Runtime::step; it has no diagnostic freeze or forced terminal abort. |
| 3 global_initializer | Emits sources defaults and a source-consistent Bus/Setup reference binding, then calls motor_port, sources.adcPort, sources.port, app::unoQDumpPort and Runtime constructor. Contexts are motor0x2003c348, sources0x2003c370, dump0x20013890 and runtime0x20013960. Exact NativeSources submember interpretation remains source-derived because its complete layout was not selected. |
| 4 app_dump_port;5 sources_port;6 sources_adc_port | Construct callback tables; sources_port stores15 callbacks without calling them. ADC factory forwards sources+288 to readerInputPort. app_dump_port calls the output-port factory only. |
| 7 dump_port;8 motor_port;9 power_reader_port | Store respective context/callback pointers. motor_port computes four candidate periods and zeros the bank if any is unsupported; it calls no bound configure/write/settle callback. No dump or ADC action follows from constructing their tables. |
| 10 loop_hook;13 init_variant | Each is bx lr. |
| 11 memcpy;12 memset | Veneers to external Thumb0x0801b2d3/0x0801b31f; underlying implementation is unselected. |
| 14 main;15 start_static_threads | main calls initVariant, static-thread startup and setup, then loops over loop/hook indefinitely. The actual static-thread start=end=0x081158f0 skips thread creation. |
| 16 Runtime constructor | Copies Motor/ADC/Source/Dump ports at0/44/64/128; calls Transaction at+152 and InputOwner at+164104. Inline dump Transfer state includes output-port copy+162696 and CRC0xffffffff at+164092. Selected helper constructors and default stores establish zero grants+164640, report+164664 with raw_lines=true, and attempted=false at+166218. This is emitted initialization, not observed completion. |
| 17 Transaction constructor | Copies44-byte Port; constructs Gate+48, Robot+136 and report RobotResult. Recorder/default storage includes32768-byte event clear. Report and PreviousTick defaults align with accepted offsets; recorded=2/OUTSIDE_ATTEMPT is explicitly nonzero. |
| 18 MotorGate constructor;19 InputOwner constructor | Gate copies44-byte Port and clears fault/lifecycle/token/halt defaults with no callback. InputOwner copies20-byte InputPort and emits zero plus NOT_INITIALIZED/status defaults, also without callbacks. Neither is a physical inhibition or acquisition result. |
| 20 Robot constructor | Emits aggregate defaults and selected Turn/Straight/FusionObservation/Flank/RobotResult constructor calls plus memset; no Robot::step or motor/native callback. Nonzero defaults are not actions. |
| 21 FusionObservation;22 Flank;23 Turn;24 Straight constructors | Direct default stores; Flank calls Turn/Straight and stores mirror1.0 at+140. These are not all-zero objects. |
| 25 Thresholds;26 qtr Report;27 Snapshot;28 RobotResult constructors | Thresholds copies four words from0x081158f8 and zeros version; those pointee bytes were not queried. qtr Report clears/defaults and calls Thresholds. Snapshot stores NOT_STARTED/NOT_INITIALIZED and clears arrays. RobotResult defaults token/fresh/duties/enable/BOOT and packed mode/menu fields without deciding or applying a command. |

All13 constructor groups16-28 have their exact paired C1/C2 aliases, four GLOBAL and nine WEAK. Absence of separate constructor symbols for NativeSources/Acquirer/Setup/Bus/AttemptRecorder/Transfer/UnoQPort/UnoQDumpPort does not prove absent construction. Selected callers show inline stores/copies/reference binding and startup BSS initialization. FIFO8 is source-defined copied .data; the sole init-array hex query did not observe its contents. Threshold and FIFO pointee values therefore retain their source-only boundary.

### Groups29-43: setup, ordinary dispatch and completion

| Groups | Actual selected behavior |
|---|---|
| 29 runtime_begin | attempted/FAULT guard; marks attempted and copies grants before transaction initialization. Then validPorts, confirmed/raw-lines, initializeSources, initializeDump and clock anchor; next_release store precedes RUNNING. Failure paths remain. |
| 30 runtime_valid_ports;31 runtime_initialize_sources;32 runtime_initialize_dump | Callback checks and matrix/ADC/opponent/QTR/IMU actions are conditional on stored grants. All-zero grants still leave five clock checkpoints. Dump setup requires its grant and complete callback table. This does not authorize any grant or prove any peripheral initialized. |
| 33 transaction_initialize;34 gate_begin | First attempt is marked before setup. gate_begin checks port, configureEnableLow, writeEnable(false), configurePwm0..3, zeroPwm and settle; only success sets initialized. Callback-chain failure records IO and invokes inhibit. Transaction success is IDLE; setup failure is FAULT/SETUP. |
| 35 runtime_step | Clears freshness fields, admits RUNNING/STOP_OBSERVING, checks release/clock ordering and65536 equal-clock poll limit, uses1000us release divisor and saturating missed count. Then open, acceptClock, service-reset, line selection/acquisition, decideFrom, projection checks, application/postdecision and completeEpoch. No diagnostic epoch limit or terminal capture abort. |
| 36 transaction_open | FAULT/IDLE/order and clock checks, new report construction. Actual ACQUIRING store0x081033f8 precedes started_us0x081033fc. |
| 37 transaction_decide_from | beginDecision, nonnull projection, phase recheck after callback, optional clockAccepted, then applyDecision; interruptions/refusals persist. |
| 38 transaction_apply_decision | Supplies current time/timing/prior receipt to Robot.step; validates fresh, nonzero strictly increasing64-bit token; calls gate.apply and checks consumed/matching token before recorder.consume and DECIDED publication. Strategy and recorder interiors are unselected. |
| 39 gate_apply | Token consumption/feedback precedes application. Invalid and STOP paths inhibit; STOP disarms. Normal path calls transact. Applied time is clocked afterward. consumed alone proves neither applied_valid nor faultNONE. validCommand target0x08111241 resolves but its body is unselected; internal hold/governor policy remains source/host evidence here. |
| 40 gate_transact | The emitted M0 path requests writeEnable(false), four writePwm calls with pulse0, then settle; it contains no enable-high call. Success sets applied_valid and zero enabled/duties. Failure records IO then calls inhibit. These are callback requests, not measured output levels. |
| 41 runtime_complete_epoch | finishAfter and acceptClock precede saturating epoch count, maximum execution, fresh and skipBefore, then stop-tail/recorder-state processing. Counter/fresh can precede later tail failure. |
| 42 transaction_complete;43 transaction_finish_after | Complete retains phase, clock/half-range and decision/application/outer-observation ordering checks. Stores completed at0x08103678, timing_valid0x0810367c and finished0x08103680 before execution_us0x08103684, then multiword PreviousTick, duration/completion and stopped bookkeeping, finally IDLE0x081036b4. finishAfter tail-forwards complete(true,last_observed). |

The29-43 contributor reconciled all15 raw blocks:2548B/989 dump rows. These actual store orders prevent treating one phase/finished/fresh/token/counter read as an atomic publication barrier. Multiword copies/tokens can tear and fields may describe different epoch stages. Repeated/bracketed reads can provide diagnostic consistency observations without proving coherence.

### Groups44-63: fault cleanup and native motor callbacks

The lead reviewed every raw row in these20 groups,2828B/1140 dump rows, against current source and resolved literal targets in the actual symbol table.

| Group | Actual selected behavior and boundary |
|---|---|
| 44 runtime_fail | Existing FAULT/STOPPED returns. Calls Transaction::abort, then the unselected endCalibrationOutput target0x08101589 with CLOCK/TIME_ORDER versus RESET reason. Stores runtime FAULT/fault/fresh/reset fields, calls dump abort0x08114ae1, copies its report and tail-calls cancelSources. Runtime FAULT does not prove all later dump/source cleanup completed. |
| 45 runtime_cancel_sources | Idempotent sources_cancelled guard is set before callbacks. QTR cancel requires its grant and charging/discharging state; IMU cancel requires its grant and pending state and receives a clock reading. Reports are copied after calls. Waiting/collecting calibration marks interruption. Underlying cancel bodies are unselected. |
| 46 transaction_fail | Existing FAULT returns. Stores fault and phaseFAULT at0x0810332c/30 before Gate::halt0x0810333c. Then copies HaltResult, clears previous/applied validity and duration acknowledgements, and calls unselected recorder reset0x081136bf. Fault alone cannot acknowledge completed halt or recorder cleanup. |
| 47 transaction_abort | Tail-forwards fail with Fault::ABORTED6. |
| 48 gate_halt | Repeated halt copies prior result with fresh=false. First call marks halted and disarms before work. If never began, sets NOT_INITIALIZED as needed without a claimed attempt. Otherwise preserves existing fault or sets STOPPED, marks attempted, optionally clocks, always invokes inhibit, records its boolean, optionally clocks completion and checks unsigned half-range timing. Missing/invalid timing cannot suppress the inhibit call. A concurrent observation before return is not a completed HaltResult. |
| 49 gate_inhibit | Calls enablefalse if present; visits all four eligible PWM callbacks even after an earlier failure; then settle if present. Tracks callback IO failure separately from absent/invalid port, updates fault and returns combined success. This cleanup loop does not short-circuit remaining channels. |
| 50 gate_zero_pwm | Ordinary setup zero loop does stop on a failed write; this differs deliberately from inhibit cleanup. |
| 51 configure_enable_low | Null/reentry guards, clears cached acknowledgement, checks map/separation/duplicates and device readiness, requests GPIO_OUTPUT_LOW, then verifies ownership/readback before acknowledging. GPIO driver bodies and physical voltage are outside this file query. |
| 52 configure_pwm | Bounds/repeated-channel/enable-low guards, exact mapped channel, owned-timer validation or refusal of an already-ready unowned device, pinctrl initialization, postvalidation, and configured-mask publication. Newly claimed timer bit is withdrawn on failed postvalidation. Pinctrl body0x081157d5 is unselected. |
| 53 write_enable | M0 high request branches to false before a GPIO write. Low request clears settled/written/low acknowledgement, requires ownership, requests low via driver, rechecks ownership/readback, then acknowledges low. No high capability is inferred from the source's generic signature. |
| 54 write_pwm | Clears settled/current-written acknowledgement, bounds/configuration/enable checks, exact candidate period and explicit pulse==0 rejection for M0, map/timer checks, driver request and postchecks, then written-mask update. Nonzero pulse is rejected before the driver call. |
| 55 motor_settle | Probe0 body, no publishSettle/report stores. Requires configured/written masks15 and enableLow, clock anchor and valid bank; clears update flags on three timer-register pointers. At most4096 polls; each rejects elapsed>=150us, accumulates fresh mask7, validates the bank, then rechecks elapsed<150us before setting settled. These are retained bounds, not proof any real call succeeds or fits an overall WCET budget. |
| 56 motor_clock | Tail-call to micros0x081157b9; micros body is unselected. |
| 57 candidate_period | Emits250 for timer0,3200 for timers1/2, zero otherwise. This is a computed expectation, not observed live timing. |
| 58 map_channel | Checks configured pin/table metadata, pad and input separation, unique pad match, device-state index (channel2 versus others), expected timer device/native channel/flags and supported period. The emitted helper relies on its bounded callers for channel admission; no extra independent entry guard is invented. Pad/input-separation/device helpers and pointed tables are unselected interiors/data. |
| 59 enable_owned | Requires configured state, valid expected pad/device/readiness and register mode=output, push-pull and no pull. These conditional register reads are instructions in the file, not measurements made by this review. |
| 60 enable_low | Requires cached low acknowledgement plus ownership and exact zero raw GPIO readback. |
| 61 timer_valid | Timer<3 and ownership, device/readiness and driver rate query, nonzero rate equal to emitted2.5MHz(timer0) or32MHz(others), active compare/pulse/period consistency, expected PSC/ARR, exact mode/control/channel-enable checks. Only timer0 checks RCR0 and BDTR0x8000; other timers branch around those slots. Active ARR expectations249/3199 remain. |
| 62 bank_valid | Requires configured15, initialized7 and active15, enableLow, then all three timer validations. |
| 63 gate_valid_port | Requires six nonnull callbacks and all four periods in1..16777216. It validates software prerequisites, not wiring or clock behavior. |

## Acceptance boundaries and handoff

All64 selected groups are covered; none required a new query. Current raw instructions support ordinary startup/constructor bindings, grant-conditioned setup and continuous dispatch, inhibited M0 callback sequences, fault cleanup ordering and retained timer guards. They do not form a closed call graph. Unselected loader, memory-veneer targets, micros, pad/separation/timer helpers, pinctrl/device drivers, strategy, recorder, calibration-output, service, cancellation and peripheral interiors remain outside instruction acceptance even where call addresses are resolved. Literal pointers do not supply unqueried pointee contents.

No ordinary application instruction was executed by this observation. Startup zeroing is not initialization completion; absent grants do not establish full hardware initialization. Software callback acknowledgements are not pin measurements. A finite future host observation cannot imply firmware termination, final inhibition, atomic/coherent state, live RAM headroom, WCET or repair of the earlier intermittent diagnostic behavior. The ordinary probe0 image has no diagnostic Runner/SETTLE publication to interpret. D207 remains the latest verified flash; this operation changed no firmware, configuration, motor permission, physical acceptance or human gate.

Reviewed root actual-validation wording is consistent. Its pending-review status may be replaced with this acceptance reference without a circular validation-file hash prerequisite; source and native evidence above remain immutable. Further ABI/entry use, cleanup or ordinary-runtime preparation requires its own scope/admission. Preserve this consumed native owner and the unique audit/failure history. All review writes stop after sealing this file.

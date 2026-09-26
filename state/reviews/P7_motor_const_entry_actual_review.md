# D205 actual file-only entry and motor instruction review

Date: 2026-09-26. Reviewer: separate review-only agent. Outcome: **PASS within
the adopted fixed file-observation scope; no open blocker in this scope.**

This review closes the actual single observation and its emitted semantics.
It does not extend the source/host review or admission into a runtime approval.
The reviewer read local files, decoded retained streams and reconstructed data;
the reviewer did not import or execute a subject, run a test, compiler or native
tool, contact the board, change firmware, or operate motors. Only this new
review file was written. Earlier source/host and admission reviews remain intact.

## Bound evidence and actual operation

`RAW` below means `state/analysis/P7_motor_const_compile_raw`. The adopted
contract remains `state/analysis/P7_motor_const_entry_contract.md`, 22163 bytes,
SHA256 `6663d1ea7309c809d8f727fc5bf68291128e54c83ca64b7d1ce53b9ff1cea9d9`.
The immutable source/host review is 16398 bytes,
`0c2e5fac514767619d1434a5f415ddbd00bed58d6d23f8eb7b325fd6ad821ddd`;
the admission review is 5863 bytes,
`2e187d66647e6d9a8b9330d5b86fc1a6d3c61b2d29c44719bc0bca0b080e6971`.
The admitted scope is `RAW/entry_native_scope01.json`, 3815 bytes,
`4b2f9f5f3bd7eeecd7d8aea29f982fadc33c7e0c797ecc7eed2ae8e74d5d0360`.

Actual check-only and execute receipts bind clean reviewed HEAD
`0a3f2b9ef755fde08086fc01c728a96c339e8e19`, source
`4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2`,
the static/default app_motor_observe build with MATCH=0, MOTORS_ALLOWED=0 and
SUMOX_MOTOR_FAULT_PROBE=1, and compiled owner
`/home/arduino/sumox26_codex_build/app-motor-const-static01`.
The separate absent scope pathname is
`/home/arduino/sumox26_codex_build/app-motor-const-entry-static01`; this reader
checks it without creating it. The local native_entry_static01 owner is now
consumed. No retry is represented or admitted.

| File relative to RAW | Bytes | SHA256 |
|---|---:|---|
| native_entry_static01/inputs.json | 23279 | a420e45658fc292599e85bd6624348f5cf880999cc82d1bd1cfe52e733d247af |
| native_entry_static01/result.json | 423604 | 6700e974d75a99d3b82d044bb026cb43c060730b4f94fad16c007d4702d944e2 |
| native_entry_static01/entry.json | 10875 | b80c8ce88d199de4538c465ab9c858ca69f2c635a5630a9b731297d9aa7cf2d5 |
| native_entry_static01/local_result.json | 277 | 495c501ded117bb53e09e6e64eba56403b66469a41bc7b8c376a5d7aa90600e9 |
| native_entry_static01_invocation.json | 1266 | ce9851499ca60f67d865440e782dc8f35d8f2034c3ed7f9d70e97c9b9c102afd |
| entry_native_closing01.json | 4089 | 82abafa93d94356450b165f444541769bb7bca29c4de693f246cc82f8eb79484 |

Root's actual validation is
`state/analysis/P7_motor_const_entry_actual_validation.md`, 3293 bytes,
SHA256 `c40de91ee0ebb893e6680d3186650f6bad2e5a859e0a00a4f83abc9fdad82823`.
Its bounded findings agree with the independent observations below.

The reviewer independently rehashed all 268 coordinator pins, 13 admission
bindings and 151 runtime local pins. The eight files inside the native owner
have exactly the closing inventory and all stated sizes/digests, totaling
889913 bytes. The transport stdout is the durable result as JSON; its stderr
is empty. The separate invocation receipt agrees with the saved inputs and
local result. The root closing stream hashes, counts, initializer, invocation
pin and local closure were independently recomputed. Root recorded C: free
space 8238292992 bytes at closure; this is a local storage observation.

## Submitted program, commands and closure

The actual compressed remote program was decoded as data, without execution.
An independent reconstruction from admitted constant values, original IDENTITY
and REMOTE_READ string literals and unchanged stop_child/wait_child source
segments equals every submitted byte: 11431 bytes, SHA256
`fb95f3b13d97ea321ea0e7e8dad3cbf499c4e0a7e8eb1d7256035c01426e01bb`.
The reconstruction preserved ordered artifact/tool pins and the fixed queries.
The complete Windows command length was independently recomputed as 5005
UTF-16 units including the terminator, below 30000.

The sole transport is the fixed ADB serial 2629958581, shell -T, admitted minimal
environment and python3 -I -B -c bootstrap. Its argv and 400-second bound match
the transport intent/result. The embedded identity observes uid 1000/user
arduino, boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, the pinned CLI and no
conflicting process. The program and actual packet contain exactly four
ordered file children:

1. Pinned readelf --version.
2. Pinned GDB --version.
3. Pinned readelf -hSWs -x .init_array on the current raw ELF.
4. Pinned batch GDB on the current debug ELF with -nx/-nh, auto-load disabled,
   C++ language and may-call-functions off, followed by the fixed 65 expressions.

The 65 expressions are exactly 32 marker/disassemble pairs and the final marker.
No inferior, connection, function call, MCU memory query or additional command
appears. All four child argv lists were independently rebuilt from the frozen
binding and compared with the actual packet. Each child returned zero, was
reaped, did not time out, and retained the 60-second/5-second deadline/reap
bounds. Child intervals are ordered and nonoverlapping within the remote clock.
Decoded stdout lengths are 283, 281, 158510 and 152370 bytes; all stderr lengths
are zero. Canonical base64 and every declared stream length/hash close, below
the 1 MiB stream limit. These elapsed child intervals concern file tools only.

All 12 opening remote file pins are the admitted eight artifacts and four
tools/loader/TLS files. All 13 closing rows are present in the exact expected
order and pass. The raw result is OBSERVED for D205_STATIC_FILE_ONLY_ENTRY,
with first_error null. Local closure independently records PASS,
STATIC_ENTRY_OBSERVED, one transport call and first_error null, from
09:47:18.834412 to 09:47:20.418917 UTC. Host and target clock values are not
treated as a common measured runtime clock.

## Raw symbol, byte and initializer closure

The reviewer parsed all 2299 indexed .symtab rows from the actual readelf
stream, without discarding ABS, undefined, local or non-function rows. Every
raw symbol row equals the accepted D204 ABI observation. All 34 selected
aliases and six initialization bounds match the frozen full tuples and raw
rows. The selected ranges are inside the accepted .text span. The exact and
token/clone candidateRate absence and sole 20-byte candidatePeriod symbol
remain true; these symbol facts alone are not the optimization conclusion.

Independent decoding of all 32 raw marker-delimited blocks verified each
header/end marker, monotonically contiguous opcode address/width coverage,
name/aliases, byte count and raw-block SHA256 against entry.json. There are
3834 selected file bytes and 1429 decoded rows. Literal-pool words sometimes
display as ARM mnemonics in GDB; they were interpreted as data where loaded
by PC-relative instructions. Neither count is a count of executed instructions.

The new .init_array observation at 0x08116258 is exactly `05011008`, hence
little-endian Thumb pointer 0x08100105 to _GLOBAL__sub_I_setup. Its end is
0x0811625c. The preinit and static-thread start/end pairs are each 0x08116258.
Thus the selected entry path has no preinit entries, one sketch initializer
and no sketch static-thread entries. This says nothing about loader threads.

## Complete selected-group semantic coverage

The reviewer inspected the raw instructions and literal targets for every
group, comparing the relevant current source only as intent. The table lists
all 32 groups; detailed motor and publication conclusions follow it.

| Group | Observed emitted behavior |
|---|---|
| entry_point | Loader logging, initialized-data copy, zero-BSS, bounded initializer iteration, then main. |
| setup | Supplies the probe's exclusive-motor-output boolean and calls Runner::begin on the bound diagnostic object. |
| loop | Checks RUNNING before calling Runner::poll; other phases return. |
| global_initializer | Initializes NativeSources and builds the four ports before constructing the Runner; selected construction does not invoke native motor callbacks. |
| app_dump_port | Builds the application dump callback port through the lower dump port builder. |
| sources_port | Copies the source context and fixed callback addresses into the returned port. |
| sources_adc_port | Forwards the contained Reader to power::readerInputPort. |
| runner_constructor | Constructs Trace, gets its wrapped port, constructs Runtime, and initializes reports/snapshots and attempted state. |
| runner_application_valid | Validates consumed/applied-valid feedback, matching 64-bit token, motors disabled and both floating duties zero when a decision exists. |
| runner_stop_reason | Preserves callback-failure, trace-invalid, application-invalid, runtime-terminal, epoch-limit and poll-limit priority. |
| runner_freeze | RUNNING guard, FINALIZING/reason, before-abort field copies and valid flag, HALT context, abort call/return flags, FROZEN. |
| runner_begin | One-attempt guard, ownership refusal/DISABLED path, SETUP context, zeroed application grants, Runtime begin, ordered freeze checks. |
| runner_poll | RUNNING guard, poll increment, APPLY/next-epoch context, Runtime step, stored return and stop/freeze check. |
| dump_port | Copies context plus two fixed callback pointers; does not invoke them. |
| loop_hook | Immediate return. |
| candidate_period | Timer 0 selects 250, timers 1/2 select 3200, other values select zero. |
| motor_port | Copies six callbacks/context, computes four periods through candidatePeriod, and zeros all periods if any unsupported value occurs. |
| power_reader_port | Copies Reader context and fixed callbacks; does not invoke them. |
| trace_constructor | Copies its underlying port and initializes bounded trace/report/state storage; no native callback invocation. |
| trace_port | Copies the port and preserves periods, substituting Trace wrappers for non-null callbacks. |
| memcpy | Tail dispatch to loader target 0x0801b2d3. |
| memset | Tail dispatch to loader target 0x0801b31f. |
| unsigned_divide | Retained tail dispatch to loader __real___aeabi_uldivmod at 0x08001365. |
| init_variant | Immediate return. |
| main | initVariant, start_static_threads, setup, then loop and hook repeatedly. |
| start_static_threads | Equal current start/end bounds bypass thread-create/name calls for the empty sketch list. |
| publish_settle | Current scalar publication followed by presence flag, and first-failure publication guarded by its lifetime flag. |
| motor_settle | Retains preconditions, fresh update flags, repeated bank checks, 150-us deadline, 4096-poll bound and eight outcomes. |
| timer_valid | Retains the live rate getter and hardware register checks while selecting constant expected metadata. |
| bank_valid | Retains configured/initialized/active masks, enableLow and all three timerValid calls. |
| write_pwm | Retains channel/mapping/period checks, zero-pulse inhibition, driver call, pre/post live checks and final written-bit admission. |
| map_channel | Retains bounded pad/spec matching, uniqueness and device/channel/flags checks with candidatePeriod support selection. |

The entry data-copy literals are [0x20013890,0x20013960), sourced at 0x081173b8;
the zero-BSS interval is [0x20013960,0x2003d408). This includes the diagnostic
Runner at 0x20013960 and separate 28-byte settle report at 0x2003d3e8. The
initializer pointer agrees with the constructor's observed entry. The global
initializer's selected builders initialize software state and callback tables;
Runtime constructor and loader helper interiors outside the selected ranges
are not newly disassembled by this review.

The setup ownership grant is deliberately true for probe1. It is distinct
from app::SetupGrants: Runner::begin emits a zero-filled 21-byte grants value
before calling Runtime::begin, preserving the inert peripheral grant boundary.
The attempted flag is set before the grant branch, so repeated begin cannot
rearm it. applicationValid rejects nonzero duties and failed/unordered float
comparisons, with exact token and inhibition checks. stopReason retains the
10000-epoch and 10000000-poll constants. freeze captures semantic report fields
before abort and marks FROZEN only after abort returns; the copies are not a
claim that every structure padding byte is copied. Later loop/poll calls return
without rearming in terminal phases. These are emitted control-flow properties,
not proof that begin, step or abort completes on the MCU.

## Expected metadata and retained live validation

The historical comparison used the retained D199 raw entry result, 378557
bytes, SHA256 `10d8a184598b587ff820cb3342586a61a22106a087788a7be756486e22a824ad`.
Its relevant raw blocks also match their historical summary hashes. Old
candidateRate at 0x08110c90..0x08110cf8 loaded prescaler/clock-selection
metadata and dispatched twice through literal 0x081160ed to the unsigned
64-bit divide helper. Old candidatePeriod at 0x08110cf8..0x08110d30 called that
rate helper and then the divide helper with 10000. Old motor_port called this
period helper for its four channels.

Current candidatePeriod at 0x08110c90..0x08110ca4 is direct conditional
selection of 250/3200/0. Current motor_port, mapChannel, writePwm and timerValid
resolve their period calls to Thumb address 0x08110c91. The selected bodies
contain no replacement expected-period division dispatch.

timerValid at 0x081111a4..0x08111324 first bounds the timer and checks its
initialized bit, device/configuration and readiness. At 0x081111f6 it retains
the indirect live PWM API rate getter through device->api + 4, for channel 4
on timer0 or channel 3 otherwise. Its return status and nonzero rate checks
remain. Literal values 0x002625a0 and 0x01e84800 select expected rates 2500000
and 32000000; the returned 64-bit rate must have zero high word and matching
low word. Selection follows the actual getter, not a substituted cached rate.

The rest of timerValid walks four channels, checks active CCR3/CCR4 against
stored pulse and pulse against period, and constructs expected mode/enables.
It retains PSC, ARR, CR1, CR2, SMCR, DIER, CCMR1, CCMR2 and CCER comparisons.
For active outputs ARR is 249 or 3199, and otherwise zero. Timer0 additionally
requires RCR zero and BDTR 32768; timers1/2 bypass those advanced-only slots.
bankValid retains configured=15, initialized=7, active=15, enableLow and the
three ordered timerValid checks, with immediate failure propagation.

writePwm clears settled and the selected written bit before admission. It
retains bounded channel, configured bit, enableLow, exact candidate period,
mapChannel/saved-index match and pre-driver timerValid checks. The emitted
nonzero pulse rejection at 0x08111460/62 reflects MOTORS_ALLOWED=0; with pulse
zero the source pulse<=period condition is redundant. The indirect native
PWM driver call remains at 0x081114b0. Only its success updates stored pulse
and active mask; post-call enableLow/timerValid must pass before the written
bit is restored. No nonzero duty path was admitted by this change.

mapChannel retains native pin bounds, pad/input separation validation, the
bounded sixteen-entry PWM-spec scan, exactly one matching pad, and the required
prior device-alias count (one only for the shared channel). Device identity,
configuration, native channel, zero flags and nonzero candidate period remain.
Port builders still assemble callbacks rather than execute them.

These actual selected instructions establish replacement of the former
immutable expected-rate/period arithmetic by constant selection. They do not
establish absence of division throughout the image or in the retained live
getter/loader functions. The global divider stub remains present, but it does
not imply these selected expected-metadata paths still call it. No cycle
saving, measured timer rate, successful SETTLE or runtime remedy follows.

## SETTLE and publication

The current settle body at 0x08111538..0x0811165c preserves the following
observed order. Null context publishes NULL_CONTEXT(2) with zero payload.
Otherwise settled is cleared; configured/written masks must both be 15 and
enableLow must pass, else PRECONDITION(3). A start micros sample precedes
initial bankValid; failure publishes INITIAL_BANK(4). The three UPDATE flags
are then cleared before fresh-mask accumulation begins.

Each of at most 4096 iterations samples elapsed time by unsigned 32-bit
subtraction. The emitted comparison against 149 rejects elapsed >=150 before
reading fresh flags, publishing POLL_DEADLINE(5). Each timer contributes its
UPDATE bit to the persistent three-bit fresh mask. bankValid is called again
after those reads; failure publishes POLL_BANK(6). Only fresh==7 reaches the
final micros sample. Success requires that final elapsed value also be <150;
otherwise FINAL_DEADLINE(7) is published and settled remains false. The common
publisher receives SUCCESS(1) only for the admitted path. Exhaustion compares
the incremented counter with 4096 and publishes POLL_LIMIT(8), with last poll
index 4095. All eight distinct outcomes are retained.

The initial failure outcomes publish zero elapsed/poll/fresh/valid values;
poll/final outcomes retain elapsed, poll and accumulated fresh with valid=7.
That validity mask denotes populated observation fields, not a successful bank
validation or accepted hardware state. SETTLE's return reads the actual settled
flag after publication on the final path. No deadline or poll limit was relaxed.

publishSettle at 0x08110cd4..0x08110d10 targets 0x2003d3e8, matching the accepted
report layout. Current elapsed/poll/reason/fresh/valid/reserved stores land at
offsets 0/4/8/9/10/11 before has_current at 24. SUCCESS bypasses first-failure
publication. Other reasons test has_failure at 25 and only when it is unset
store first-failure fields at 12/16/20/21/22/23, then set has_failure. Reserved
bytes are explicitly zero. The selected publisher never replaces a captured
first failure or resets its lifetime flag. Startup zero-BSS initializes the
separate report; construction does not introduce a report reset.

This establishes emitted store ordering and lifetime guarding only. Separate
scalar stores and presence flags do not prove atomicity or a coherent remote
multi-field capture. Repeated calls can update current fields while retaining
the first failure. MCU runtime, interrupt behavior and any later observation
protocol need their own admitted evidence.

## Review disposition and limits

Actual collection, byte coverage and selected semantics conform to the fixed
D205 contract. The parser's unchanged semantic-review-pending text is an honest
generic parser limitation; this separate review supplies the bounded manual
semantic inspection without rewriting raw evidence. Read-only audit helpers
required correction of a JSON field spelling and recognition of eight-hex
literal rows during analysis; these were reviewer parsing corrections, not
subject/native failures, and caused no new invocation or query.

D201 remains the latest flashed image. This inspection did not compile,
upload, reset, attach to an inferior or execute the candidate firmware. It
does not prove setup succeeds, that prior failure is repaired, timing benefit,
live RAM/stack/WCET, coherent report capture, physical acceptance, motor-run
permission or a human phase gate. Preserve these consumed owners and original
streams. Any inhibited runtime attempt must be separately specified, reviewed
and bound to the current artifacts and ABI; historical runtime owners cannot
be reused. Reviewer writes stop after this file's final size/hash is reported.

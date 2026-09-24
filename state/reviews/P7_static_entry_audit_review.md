# P7 static entry and constructor audit review

25 September2026, Asia/Dubai. Separate same-model read-only review, reusing the
D148 review context, with a bounded second same-model constructor/factory
inspection. This is not fresh-context, cross-model or human review. Reviewer
owns only this file, changed no implementation/test, ran no board commands,
compiler, upload/reset or target execution, and made no commit. Local JSON,
hash and ELF-byte comparisons supplemented source and receipt inspection.

## Scope, hashes and verdict

**PASS for the corrected focused FILE-AUDITED entry/constructor note; no open
BLOCKER, MAJOR or MINOR findings.** This does not qualify complete native bindings,
public ABI layouts, runtime behavior, live memory, timing or any human gate.

- Corrected `state/analysis/P7_static_entry_audit.md`:
  `704bff9b96e130e6c1d3c4bcd1d4c93bbf55141a65ff19d779642ebb26339892`.
- Unchanged `state/analysis/P7_static_link_probe_raw/entry_audit.json`,101536B:
  `92b72069900fc761deb0e4cdfba43a0058d0bc771dabdb1c41fff1557bad8eeb`.
- Original note, preserved by coordinator in6ecb8ab6:
  `4e9065d20f29f07e8c3032bad8a867e3fea343a4b7d8510ccfb1570e067a8150`.
- Actual debug ELF,1764708B:
  `0f7f2825329466e06f15144f07a5188435ac309aa1a3aff71a1a9f1be87a27bd`.
- Actual map:
  `15da1417d5a7f781195d86ba1554dd449e4e14548dde1ea8052e8da78cd16806`.
- Frozen103-file manifest:
  `c106c0fb8baaf0a6f2536558da0084bd7d236c4ee8e77a4110b60107ad073391`.

## Finding and correction

Resolved MINOR: original note`:16-17` and receipt `stdout_format` overstated
literal completeness. Objdump preserved `...` rather than rendering zero data
in Runtime[0x08100908,0x08100910) and Robot[0x08102f10,0x08102f24).
The initial reviewer continuity assertion identified this omission. Refined
comparison against the original ELF verified all5194 displayed instruction/
literal bytes and the28 omitted zero bytes across32 complete symbol ranges.
The Runtime branch at0x08100900 targets0x08100930; the Robot branch at0x08102f0a
targets0x08102f40, skipping their respective literal pools.

Corrected note`:16-22` explicitly states both omissions and supersedes the raw
receipt's inaccurate description. Preserving the original receipt makes this
correction auditable. No instruction/call-path finding arose from the omission.

## Evidence checks

The receipt contains32 nonempty function disassemblies, one init-array dump and
one separately stored symbol query:34 commands, all recorded returncode0. Each
function request uses the symbol's even Thumb start and start+size end. All
captured function starts and extents match their symbol-query rows. Therefore
the requested C1 names with C2 aliases yielded actual bytes rather than empty
symbol-name disassembly. No extra disassembly or native code was executed during
this review; opcode/literal encodings were compared directly with ELF sections.

All six retained inputs (ELF/map/main.cpp and three static linker scripts) were
rehash-checked against before/after records. The current manifest itself and all
103 current project source hashes match. Installed-source hashes agree with
the D140 provenance note. Receipt tool hashes agree before/after; this review
does not independently rerun the tools or requalify their implementations.

Entry literals and register flow support the note's ordering: three native
printk calls precede208B data copy and167272B BSS clear; empty preinit range;
one init word0x08100101 selecting `_GLOBAL__sub_I_setup`; then image main.
The map places `_ebss` before312B alignment fill ending at0x2003c800. Its
linker wildcard includes `.noinit`; no reset-persistence claim follows.

Main calls the captured empty weak initVariant, the static-thread iterator,
setup, then loop and the strong project hook. Identical thread-list bounds
0x08115970 skip the thread-creation body. The hook symbol is GLOBAL and its body
is `bx lr`, matching `src/hal/loop_hook.cpp:4`; compiled main has no SerialUSB
initialization call. Setup passes21 zeroed bytes and runtime0x20013960 to begin;
loop passes the same runtime to step. This agrees with `app.ino` and the default
SetupGrants/member definitions, not a claim about all begin/step native effects.

The captured constructor/factory closure includes Runtime, Transaction,
MotorGate, Robot and their named subordinate value constructors. Cross-checks
against current source and map support the stated static object placement and
factory call order. Peripheral callback pointers are stored, not invoked, by
these factories. Candidate PWM arithmetic reads retained constants; no live
register access, explicit heap allocation, Bridge call or serial initialization
was found in the inspected project constructor/factory paths.

## Boundaries retained

The early native printk path is a startup dependency. Image memcpy, memset and
__aeabi_uldivmod tail-branch to packaged functions at0x0801b2d3,0x0801b31f and
0x08001365; their complete behavior is outside this inspection. The note does
not turn absence of explicit allocation in this constructor closure into a
whole-app allocation or Linux-independence proof. Full external callback/device
binding, ABI size/alignment/member offsets, runtime stack/RAM, startup timing,
WCET, physical acceptance and specific motor-run authorization remain separate.

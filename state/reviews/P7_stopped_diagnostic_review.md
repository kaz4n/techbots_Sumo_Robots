# Fixed stopped-state diagnostic: pre-action review

25 September 2026, Asia/Dubai. Same-model review reusing D149/D153/D160 context;
local source/evidence inspection only, no native command or reviewer execution.
Reviewed read_stopped_remote.py SHA256
`71507fd8c815eab148eb83684dfb9cbc766582635a9505908b96e28700c5d0d3`
and P7_stopped_diagnostic_plan.md SHA256
`bf992388e1d6c0a1d5c42281b959acfb0b30f12fa3af5a1535b2b41ab76baa55`.
Its final addendum accurately records the repair and explicit clean-HEAD/pin,
exclusive-intent,60s outer-timeout and independent local-postcheck boundary;
it preserves parsed-data failure and consumed scopes. Source71507fd8 is unchanged.

**Scoped source/plan PASS; no open material finding.** This is a separate fixed
observation after consumed D160, not a retry or firmware remedy. The coordinator
must record D161, pin the final source/payload/ADB and reviewed current HEAD,
verify the existing local stage/packet, and persist the exclusive local intent
before one bounded transport invocation. No launch was reviewed or performed here.

Only one OpenOCD child is possible: four literal echo-labelled mdw phys commands
at0x2003bc98/7,0x2003b2b0/126,0x2003bef0/48,0x2003bc98/7, then END/shutdown.
All extents are word-aligned:28+504+192+28=752B. D149 receipt a7c0c479 retains
TransactionReport504B, RobotInput192B and the quoted nested fault/consumed offsets.
The original capture bindings select five fixed files and the prior exact boot;
their complete bytes, helper8ba9b190 and supportab0bb320 are hash-bound before
loading. Payload framing is bounded; no caller address or command is accepted.

The pinned694B MEM-AP config89d16a28 selects only sumox.mem, reset_config none,
disabled servers and no Cortex/flash/event hooks. The [official command guide](https://openocd.org/doc/html/General-Commands.html#Memory-access-commands)
defines mdw counts as32-bit words. Versioned [target.c:1469-1479](https://github.com/openocd-org/openocd/blob/v0.12.0/src/target/target.c#L1469-L1479)
maps no-MMU physical reads to read_memory; [mem_ap.c:222-233](https://github.com/openocd-org/openocd/blob/v0.12.0/src/target/mem_ap.c#L222-L233)
routes those reads through the AP. This supports phys without a separate CPU
target. Actual success of this command spelling on the pinned installed build
remains to be observed; unsupported/error output ends the attempt without retry.

Fresh remote mkdir is exclusive; held no-follow descriptors own intent, raw
stdout/stderr and result. Intent is fsynced before spawn. The child uses fixed
argv/env/cwd, DEVNULL stdin, no shell, a new session and inherited D1531MiB
regular-file limit. wait_child bounds30s plus5s owned-group termination/reap;
unknown outcomes remain unknown. Accepted streams must each be below1MiB.
Admission checks identity and all five pins; final checks attempt each independently.

Initial source2d2ff1bb had two material preservation defects: stream.close at
:119-128 could bypass final checks/result and mask the process error; postcheck
check at:47-54 stopped after the first drift. Fixed before native execution:
current:131-141 captures every close error without replacing first_error or
subprocess outcome, and:47-66 independently attempts all six final checks.
Coordinator host-check receipt for71507fd8 reports PASS under controlled stubs:
injected wait/unreaped outcome survives two close errors, every aftercheck and
final-result attempt still occurs. This is bounded host evidence, not a fresh
independent oracle or native qualification. No broad test/framework is required.

COLLECTED denotes successful child/stream/postcheck completion; reads_bytes752
is the requested extent. Interpretation still requires all exact ordered labels,
addresses and word counts from the retained raw output, reconstructed little-endian
against D149. Unknown fields remain raw. Equal runtime brackets show sampled
prefix stability only, not atomic nested data or uninterrupted MCU continuity.
D160 flash identity is inherited provenance, explicitly not freshly reverified.
No upload/halt/reset/resume/write/recovery, motor/sensor acceptance, timing or
memory qualification, production static admission or human gate follows.

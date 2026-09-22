# P0: what the team needs to check manually

**Current update,2026-09-22:** the human has connected the bare UNO Q and asks for
no additional hardware now. USB ADB inventory, actual board-side builds and inert
uploads work. The frozen60000-sample timing diagnostic measured max/p99 lateness3us;
the default matrix demo is uploaded. See state/FACTS.md F-062 onward and the current
handoff for precise evidence/limits. The checklist below is retained for later
physical acceptance; its old pending connection statements are superseded by these
receipts. No new connection or measurement is requested from the human this session.

Prepared 2026-09-22, Asia/Dubai. **Checklist only: no hardware result or approval.**
P0 is active; no phase gates have passed. Today is the planned board/SSH setup
day; PLAN section 3 targets P0 completion on 23 September. Complete the checks
in order, recording `unknown` or `not available` when necessary.

The immediate task is a bare-board inventory and connection. Motor operation,
sensor calibration and ring trials come later. Existing `[P]` wiring in
[HARDWARE.md](HARDWARE.md) remains a proposal; this checklist does not authorize
building or changing a disputed circuit.

## 1. Do these first: no instruments needed

- [ ] With power off, photograph/record the existing connections before touching
  them. List every attached header wire, shield, Qwiic cable and power source.
  If nothing is connected, write `bare board`.
- [ ] Prepare the UNO Q alone on the desk. Motor battery, motors and both driver
  boards must be physically isolated from it, including driver control leads.
  Keep sensor/battery/button wiring disconnected for the first board check.
  A main switch being off or wheels being raised is not the bare-board setup.
  If you cannot establish this, report the actual connections and stop here.
- [ ] Record the UNO Q board label/revision and its intended approved power
  source/cable. Once isolated, use the board's normal documented power setup.
  Record whether Linux starts and whether the board is reachable; LEDs alone
  do not prove the toolchain or firmware works.
- [ ] Identify the **MPU6050 breakout**, not only the chip name: manufacturer,
  board printing/revision, connector labels, front/back photographs and vendor
  link if available. Do not assume it is a GY-521 or Adafruit board. The actual
  regulator, pull-up rail, AD0 connection and cable pinout still need review
  before connection. See [G6](../state/analysis/P0_G6.md).
- [ ] List the parts on hand and any already assembled wiring: three JS200XF
  revisions (rear button or pads), four MZ80 wire-color variants, four exact
  QTR boards, and the markings on both IBT-2 boards and their input-buffer ICs.
  Record available multimeter, oscilloscope and logic analyser, including `none`.

## 2. Give the agent a verified SSH connection

The human sets up the board's network/account; the agent can perform the
read-only inventory after that. Use the same WSL Ubuntu SSH environment that
the repository scripts use. Windows-only SSH configuration is not automatically
the WSL configuration.

1. Obtain the board's actual hostname/IP and login username from its trusted
   local console or existing setup. On a board terminal, `whoami` and
   `hostname -I` can report the account and addresses. Do not guess a default
   password, username or target.
2. Set up public-key login for that account using an existing suitable WSL key
   or a newly created key without overwriting an existing one. Keep passwords,
   private keys and Wi-Fi credentials out of chat and out of this repository.
3. Verify the SSH host-key fingerprint against a trusted board console/setup
   record before accepting it in WSL. For an Ed25519 host key, the board-side
   read-only command is `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`.
   Compare the same algorithm/fingerprint with the connection prompt. If the
   file is absent or the fingerprints differ, report the result; do not disable
   host-key checking or erase an existing host record to bypass the mismatch.
4. Confirm WSL can run `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes
   USER@HOST true` with your verified target substituted. Expected result:
   exit code 0, no password prompt. An SSH alias is also acceptable. The agent
   needs only the alias or `user@host`, setup status, and a dedicated absolute
   board build-directory path; it does not need credentials in a message.

The scripts use `SUMO_SSH_TARGET` and, for staged builds, `SUMO_REMOTE_ROOT`;
see [tools/README.md](../tools/README.md). These values must describe your board.

**Agent task after setup:** run the read-only inventory, retain its JSON and
each command's result, then review installed CLI/core/libraries, startup options,
kernel, listener list and required utilities. The prospective command is
`bash tools/preflight.sh > state/analysis/P0_board_inventory_YYYYMMDD_HHMMSS.json`,
from the repository root in WSL, substituting a fresh timestamp; never overwrite
earlier evidence. `INVENTORY-COLLECTED` means the initial commands completed;
`INCOMPLETE` needs follow-up. Neither status is a hardware pass. Loader
configuration and exact router identity still need separate read-only inspection.
No upload, reset or package installation belongs to that inventory. Missing
fields remain unknown. These commands have not been run on the board by this
checklist.

## 3. Observe the inert matrix demonstration and both boot modes

Only after isolation and the installed-tool inventory are checked:

**Immediate matrix execution is still blocked.** The official UNO Q manual
(section 5, printed page 15) warns that matrix access before Linux startup
completes can interfere with MCU operation. The agent must inspect the installed
loader and matrix ownership before using it as an early-start indicator. The
script rejects Immediate matrix uploads; compile-only remains allowed. A revised
indicator or delayed display requires review and must not be mistaken for the
actual sketch-entry instant. See FACTS F-061; no header pin is assigned here.

- [ ] Agent compiles the reviewed inert matrix sketch against the actual core;
  record compile output separately from upload output. Prospective compile-only
  commands are `bash tools/flash.sh bench/p0_matrix --compile-only --startup
  default` and the same command with `--startup immediate`. Compile success
  does not prove a display, a boot time or a Monitor connection.
- [ ] Agent verifies the complete staged source against the reviewed inert
  allowlist before any upload. Human observes the actual matrix scrolling
  `SUMO` and records the result/video. A different installed program's display
  is not evidence for this sketch.
- [ ] After the indicator/ownership issue is resolved, repeat cold-start timing
  in each verified startup mode, using the same
  sketch and supply. Record individual runs from **power application to first
  identifiable sketch `SUMO` frame, excluding the loader boot logo**, the
  method/resolution (video or stopwatch), and failures. Identify the marker
  precisely and account for its known software/display delay: the current first
  draw is blank and the glyph scrolls in later. This observation measures display
  readiness and is not an exact timestamp of sketch entry.
  Use a normal orderly Linux shutdown before removing power for the next cold
  boot; do not substitute a sketch reset or SSH reconnection timestamp. Several
  runs per mode let the agent report observed min/max without inventing a
  universal startup deadline. The old roughly 35-second number is not a target
  or a measurement on this board.

**Printed counter remains blocked by SC-I.** The current sketch keeps its
counter in RAM; it does not print it. P0 also requires once-per-second counter
lines received by `tools/logs.sh`. Inspected Monitor/Bridge code can allocate or
wait, conflicting with R3/R4. The coordinator must present the scoped diagnostic
exception versus bounded-transport options, obtain the protected decision and
record it before implementing that path. Neither a matrix video nor a RAM
counter closes the log round trip. See [SC-I](../state/analysis/spec_conflicts.md)
and [G3](../state/analysis/P0_G3.md). The internal readiness index 67 is not a
header pin to connect to; high readiness alone does not prove bounded RPC.

After that issue is resolved and the source reviewed, human confirms the display
while the agent receives and saves the real sequential counter through the
receive-only log script. Keep default and Immediate observations separate.

## 4. Electrical checks before any external signal reaches the UNO Q

The team owns these measurements. Review the exact part/interface and test
setup with the coordinator first. These are evidence requirements, **not a
wiring recipe**. Do not populate proposed dividers, change supplies, solder range
pads or connect an unidentified output simply to complete this table.

The project treats all MCU interfaces as 3.3 V only. Keep ADC signals within
their permitted operating range; an absolute-maximum rating is not an operating
target. The official [UNO Q manual](https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf)
describes 3.3 V headers/Qwiic and ADC input range 0 V to VREF+. A measurement
must also establish valid logic levels, loading and startup/power-off behavior,
not merely a steady voltage below a damage limit.

| Item | Human records, MCU disconnected from the signal | What stays unresolved until review |
|---|---|---|
| Existing power/interface harness | Exact schematic/as-built connections, component markings/values, actual rail readings and reference ground; powered-off continuity results where appropriate | No new power or ground arrangement is approved by this checklist |
| Each JS200XF | Purchased revision, both detection states, isolated OUT and proposed interface-node readings under a reviewed load, including power on/off behavior | Output stage/drive limits; the vendor's rear learning button differs from D-005's soldered pads. Do not alter the range mechanism until reconciled |
| Each MZ80 | Actual wire variant, both detection states, unloaded and reviewed loaded readings, power-off/on behavior | An unloaded meter reading does not prove the internal pull-up, leakage or safe divider/pull-up choice |
| Each QTR-1RC | Exact PCB; scope captures of isolated OUT during a reviewed test of both power sequences and supply transients; maxima/minima and probe/setup details | **VIN=5 V with 3.3 V charging has no established safe OUT maximum.** A DMM can miss transients. Do not connect direct OUT or silently switch its supply |
| Both IBT-2 boards | Buffer markings, unpowered continuity/pull-up findings, reviewed loaded logic-level and EN off/boot observations with motor power/motors isolated | D-013 logic-supply decision; working once does not prove guaranteed input thresholds. No forward/reverse/brake run now |
| Battery sense / buttons, if already assembled | As-built circuit and isolated node readings; buttons recorded separately for none, START, MODE and both | **SC-A: the documented ladder makes START and both indistinguishable.** Do not claim both-held STOP works or approve thresholds from this circuit |
| MPU6050 breakout | Regulator/level shifter/pull-up identification, connector mapping and measured bus/interface levels in an approved isolated setup | Correct chip name alone does not establish the breakout supply, address or Qwiic compatibility |

The QTR transient concern is an inference from the VIN-connected capacitor in
the [exact QTR-1RC circuit](https://www.pololu.com/product/2459), not a measured
failure. The vendor describes charging for at least 10 us and then timing decay;
that description does not certify the proposed mixed-voltage power sequencing.
The [JS200XF vendor description](https://www.jsumo.com/js200xf-infrared-long-range-sensor)
currently describes a rear range-learning button. Detailed source conditions
and proposed tests are in [G5](../state/analysis/P0_G5.md). If equipment or a
safe approved setup is unavailable, record `not measured` and keep that interface
disconnected; the agent cannot replace the measurement with research.

## 5. Help collect P0 timing and pin evidence

The agent prepares/reviews inert diagnostics, captures available data, computes
statistics and records evidence. The human supplies the isolated board,
instruments and physical observations. Check the source and setup before any
diagnostic that drives a header pin. Present sketches do not implement all the
remaining GPIO/QTR/ADC/I2C tests.

- [ ] Run the bare 1 kHz scheduler capture: P0 asks for 60 s, max and p99 jitter.
  Save the raw histogram, sample count, maximum, over-period count and actual
  elapsed duration. The current sketch collects 60,000 samples and can take
  longer than 60 s when periods are missed. Its last bin is `>=1000 us`; if p99
  falls there, report a bound, not an exact percentile. RAM extraction needs a
  verified debugger or approved bounded transport. Record the matrix-active
  case separately; [bench/README.md](../bench/README.md) defines present limits.
- [ ] With no external circuit on the selected verified pins, measure pinMode,
  digitalWrite/digitalRead, four-pin QTR-style timeout acquisition and analogRead
  duration. Record timing overhead, count, max/p99, errors, interrupts and build
  conditions. A 1500 us QTR timeout already exceeds the 1 ms tick; SC-B requires
  a decision, not a smaller silently substituted timeout.
- [ ] Once the breakout/interface is approved, collect MPU6050 identity and
  configuration readback, actual unique-sample intervals and successful/fault
  I2C times. P0 asks for gyro range at least 1000 dps and new samples at least
  800 Hz; neither a 1 kHz loop nor a library default proves those. Fault injection
  requires a reviewed isolated setup, not shorting a live bus. Use [G6](../state/analysis/P0_G6.md).
- [ ] Check installed source/devicetree against the proposed pin map, then scope
  intended PWM pins with driver leads disconnected. Retain measured waveforms,
  API error results and boot/off EN evidence from the approved electrical setup.
  Installed source, observations and any human-approved changes must agree.

Only after these dependencies are reviewed does the coordinator present the
verified map for a separate `PINMAP OK`. Only after P0 criteria and the full
fresh review are satisfied can the human write `GATE P0 PASS`. Neither reply is
being requested now. Filled checkboxes or the template below grant neither.

## 6. Later checks, not today's request

P2 covers integrated sensor calibration, motor direction/brake tests, battery
ADC calibration, IMU drift, brownout behavior and the complete five-minute
worst-case tick measurement under 800 us. P3 and later cover countdown proof,
stopping distances, edge escapes and ring behavior. They require their preceding
phase gates; motor-capable uploads/runs require the exact run's human `STAND OK`
or `RING OK`. No motor-run approval is requested for this bare-board checklist.

## Reply with this first batch

```text
UNO Q available / label:
Bare board; drivers, motors and motor battery physically isolated: yes / no / unknown
Current connections / power source:
SSH alias or user@host (no credentials):
WSL key login / trusted host-key check: ready / not ready / unknown
Dedicated absolute board build directory:
MPU6050 breakout brand / board markings / vendor link:
Other parts/revisions present and wiring already built:
Multimeter / oscilloscope / logic analyser available:
Anything unclear or unavailable:
```

Use [P0_MEASUREMENTS_TEMPLATE.md](../state/analysis/P0_MEASUREMENTS_TEMPLATE.md)
for later raw observations. The agent transfers reviewed results into FACTS,
PROGRESS and TUNING_LOG; human decisions go into DECISIONS. Leave missing values
blank or `not measured` rather than entering vendor or expected values.

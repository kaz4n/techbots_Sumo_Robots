# D088 B3/B13/B14 display contract

**D108 correction:** the historical SENSOR_VIEW order below incorrectly puts
bit0 at FC and bit1 at FL. P2_display_channel_contract.md supersedes only that
mapping: bit0 FL15 at (2,1), bit1 FC at (4,1). The original clause remains below
as provenance; all other clauses remain in force.

2026-09-23, selected under D051/D075. Pure renderer plus actual native submission;
no service execution, sensor acquisition, motion permission or hardware acceptance.
User explicitly permits testing the bare UNO Q with no external sensors. One
reviewed MOTORS_ALLOWED=0 built-in-matrix bench may be deployed with recorded exact
source/artifact/target identity. No request to connect other hardware is needed.

## Renderer and actual Robot mapping

Public ui_display.h is the fixed interface. Every render completely overwrites
104 bytes, row-major8x13. Pixels0/7 mean off/full,3 means unavailable sensor marker.
No heap, clock, I/O, recursion or motion mutation. Loops have fixed small bounds.
State must be BOOT..DRIVE_TEST, mode1..6, serviceNONE..LOG_DUMP; service_menu requires
non-NONE even outside IDLE. Masks must fit opponent7/line4/fault7 bits. Available
battery must be finite and nonnegative; unavailable payload is ignored. Invalid
input returns INVALID and renders E + cross, all fault markers and unknown battery.
The invalid-frame right glyph region is blank; malformed data never selects a fault page.

Top row marks each active fault bit at columns0,2,4,6,8,10,12. Rows1..5 contain
left3x5 glyph at x0, center5x5 icon at x4 and right3x5 fault glyph at x10. Row6 is
blank. For multiple faults, select ascending set-bit index using
(t_us/1000/UI_FAULT_PAGE_MS)%number_active. Time-wrap may change the visual page;
this is never a behavioral timer. Fault order/glyphs: IMU I, opponent stuck S,
QTR stuck Q, low battery L, rejected calibration C, line warning W, contract E.

3-bit glyph rows, highest bit left: digits0..9 =
75757,26227,71747,71717,55711,74717,74757,71111,75757,75717.
Letters: B=65656, S=74717, E=74647, I=72227, Q=75731, L=44447,
C=74447, W=55575, D=65556. Each string is five decimal row masks.
5-bit icon rows (decimal, bit4 left): RIGHT=[4,2,31,2,4], LEFT horizontal mirror;
UP=[4,14,21,4,4]; ARC_R=[0,14,17,2,7], ARC_L mirror;
PAUSE=[10,10,10,10,10]; HOURGLASS=[31,17,10,4,31]; CROSS=[17,10,4,10,17];
CHECKER=[21,10,21,10,21]; DOWN=[4,4,21,14,4].

BOOT uses B/hourglass; STOPPED S/cross; DRIVE_TEST D/cross. COUNTDOWN uses
ceil(max(0,COUNTDOWN_MS*1000-elapsed)/1000000), clamped to at least1, and hourglass.
Elapsed is uint32(t_us-release_us); elapsed >= full hold is INVALID (including
future anchors outside the small forward interval). Thus full5seconds show5..1
and the100ms margin remains1; renderer never announces GO. Compile-time countdown
range1..9000ms, total hold<half uint32 wrap; no existing timing defaults change.
Other states show mode digit and its B13 icon. Services show only in IDLE with
service_menu=true: QTR_CAL C/checker, DRIVE_TEST D/cross, LOG_DUMP L/down; selection
does not claim execution/progress. SENSOR_VIEW replaces left+center region with
geometry: opponentFC,FL,FR,L,R,RL,RR at (4,1),(2,1),(6,1),(0,3),(8,3),(2,5),(6,5);
lineFL,FR,RL,RR at (0,1),(8,1),(0,5),(8,5). Available group bits0/7, unavailable
all3. Robot outline at x3..5,y2..4 has3-bit rows[2,7,5]. Fault/battery remain.

Bottom battery row: for i=1..13, light pixel i-1 if available V >=
EMPTY+(FULL-EMPTY)*i/13, evaluating thresholds in double from configured floats.
Below EMPTY alloff, at FULL all13. Unavailable: even columns7, odd0. Display range
9.5..12.6V is a development visual scale, never calibrated battery evidence or a
new power-control threshold. Frame period40000us, fault page500ms, bench scenes
2000ms live in config.h; representation dimensions/bit depths are not tunables.

displaySample accepts the actual paired current RobotInput/RobotResult. State from
outputs, IDLE mode from menu else running_mode, selection/release from result.
Battery from input; masks from result. Opponent availability requires fresh result,
no STALE_SENSORS and input.opponent_fresh in explicit-line mode else observations_fresh.
Line availability requires fresh result and result.line_available. Fresh result
battery availability requires input.vbat_valid. Nonfresh result makes all three
unavailable and sets CONTRACT. New RobotResult.imu_available reflects initialized,
validated resolved input.imu_ok, no heading fault/HEADING_CONTRACT (including preGO);
it is diagnostic only and not a match-heading validity flag. Faults map directly
from that availability, opponent_fault_mask, qtr_warning_mask, low_battery,
lifecycle.services.calibration_rejected, lifecycle.services.line_warning and
nonzero contract_faults/escape_fault. No revalidation of IMU source or inferred data.

## Actual native adapter

Read P2_matrix_native_audit.md for exact installed source/export/context evidence.
UnoQMatrix constructor/destructor have no I/O; noncopyable. begin requires normal
startup AND exclusive boot ownership, privileged Thread mode, nonnull matrix
device and device_is_ready true. Reject before any matrix/mask write otherwise.
One global lifetime owner; after successful begin another instance or repeated
begin returns ALREADY_OWNED, no writes. Failed begin latches local fault; further
operations FAULTED. Failed begin does not consume global owner. The exclusive
grant prohibits every other writer including NMI/HardFault and inherited animation.

Setup sets grayscale3, submits a zero104-byte frame, calls matrixBegin once; returns
INIT_UNCONFIRMED since void native APIs cannot certify running/optical output.
The blank write and every submit save PRIMASK, disable IRQ, native fixed write,
DMB, restore exact PRIMASK. No unconditional IRQ enable. Validate context outside
mask. ISR may see old/new slots in one scan, but cannot read a partially copied
buffer. No matrixEnd, scrolling/playing, Bridge, waiting, heap or generic fallback.

submit before begin returns NOT_INITIALIZED. After init, context rejects latch
CONTEXT_REJECTED; any pixel>7 latches INVALID_FRAME. Validate all104 even when
throttled. First valid submit immediate; subsequent uint32(t-last_submit) below
period returns THROTTLED with no write; >=period one write (never catch-up loop).
Caller supplies forward time, gaps<half wrap. Submit only after validation and
return SUBMITTED_UNCONFIRMED. Rendering/frame validation stay outside critical
section. No stored caller pointer. Local fault is reset-only, no optical-off claim.

Host tests must execute actual native CPP against controlled symbol/CMSIS/device
substitutes, not a replacement adapter. Target artifact must retain real matrix
calls and privilege/PRIMASK instructions. Full control tick WCET, IRQ interference,
optical orientation/brightness, SC-AJ clock, F091 deployment identity and all
external-hardware/human gates are separate. A bench scene is synthetic UI input,
never an actual sensor/competition measurement.

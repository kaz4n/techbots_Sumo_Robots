# D076: P2 B1 checked native opponent inputs

Scope: D075 software preparation, actual UNO Q GPIO driver and compile-only bench
probe. No physical sensor/range/false-hit evidence, pin approval, upload or gate.
Use the proposed HARDWARE3 order FL15,FC,FR15,SL,SR,RL,RR at unchanged Arduino
indices11,12,13,16,17,18,19, now named OPP_INPUT_PINS in config.h. These remain
development proposals; copying their values is not PINMAP OK or a wiring change.

## Production API

opp_sensors::Sensors has no constructor I/O. begin() is a setup-only explicit
initialization attempt, returning InitResult {ready, configured_mask, status[7]}.
It first invalidates the previous ready state, then validates all mappings before
configuration: indices within installed zephyr::arduino::arduino_pins, nonnull
ports, pins representable in gpio_port_pins_t and in device's port_pin_mask,
flags==0 and no duplicate physical port/pin pairs. Any mapping failure rejects
the whole bank without configure calls, reports status -EINVAL for all7.
No pin may alias a motor/output through a bad config without rejection of that
config: exact approved development list checked at coordinator/source review;
future config changes retain R8 review. This generic duplicate check is not a
complete pin-ownership manager.

For a valid map, check device_is_ready before each gpio_pin_configure_dt(spec,
GPIO_INPUT). No pull/output/interrupt flags, pinMode, digitalRead or analog API.
Preserve every native signed status; not-ready=>-ENODEV. Attempt all7 independently
even if one fails. configured_mask marks exactly statuses==0; ready only if0x7f.
Calling begin again is an explicit bounded setup retry, not a retry loop. It may
recover after a failed attempt but never invent a successful configuration.

read() returns Snapshot {valid,raw_mask,valid_mask,status[7],started_us,completed_us}.
If not fully initialized: no device/read/clock calls, validfalse,masks0,times0,
all statuses -EACCES. Otherwise record micros before and after the bounded seven
channel pass. Recheck readiness; not-ready=>-ENODEV. For ready channels call
gpio_pin_get_raw(port,pin) once. Preserve returned signed values exactly. Only0/1
is a valid reading; negative OR unexpected positive values are invalid. valid_mask
marks those0/1 channels; raw_mask sets only actual successful1 bits. valid is true
only for0x7f. Read failure does not clear initialization or silently retry; next
explicit read can recover, while Robot still applies its own fault policy.

This is an electrical-level snapshot: no OPP_ACTIVE_LOW_MASK XOR, debounce,
contact, bearing, stale cached reading or fake fallback detection in HAL. Partial
data is diagnostic only. Application must require Snapshot.valid before declaring
the opponent observation fresh; it passes raw_mask to Robot unchanged. Host
composition tests prove the existing core applies its configured polarity once.
Timestamps are actual read-window observations, not proof of simultaneous pins
or whole-tick WCET. Unsigned completed-started supports normal micros wrap.

Implementation lives in src/hal/opp_sensors.*; actual platform cpp guarded by
ARDUINO_ARCH_ZEPHYR so ordinary pure host builds need no Arduino headers. Native
tests compile this SAME implementation with controlled Arduino/wiring_private/
GPIO headers and ARDUINO_ARCH_ZEPHYR. No alternate success implementation.
No heap, waits, retries, dynamic ownership manager or Bridge/serial operation.
Exclusive ownership of these input pads is an application prerequisite; configure
and read do not themselves protect against another peripheral remuxing a pad.

## Tests and evidence

Separate author derives tests from this contract/header and installed API audit,
not implementation cpp. Cover no constructor I/O; all128 electrical masks; native
error and unexpected positive values on every channel; setup failures/readiness
at every position; masks/status/timing/wrap; invalid/duplicate/malformed maps;
setup retry/read recovery; fixed maximum7 reads/configurations; no pulls/output;
raw polarity through real core debounce; no allocation. Preserve existing locked
tests and B16 values. Actual target probe has one Sensors instance, retains
never-called begin/read wrapper, setup only stores its address, loop empty.
Upload remains refused. Retain installed API/link/ELF and staged source evidence.

Update only the five existing inert guards after independent additions/config-
proposal review. Existing sketches never instantiate Sensors. Fresh separate
read-only review checks code, mocks, target retention and guarded upload behavior.
Physical B1 matrix display/ranges/60s empty-ring false hits remain pending.

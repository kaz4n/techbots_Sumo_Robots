# Countdown production composition — 2026-09-22

Read-only audit by p1_timed_arc_worker; recorded by coordinator. No implementation
or protected policy approval is implied. D-018/D-019/D-024/D-035 and B3 already
authorize composing Controller with Services before applying the motor gate.
The established tests/locked/test_countdown_services.cpp LogicalHarness demonstrates
the active-countdown ordering; future production tests must call the new wrapper,
not weaken or replace the established cases.

Proposed minimal wrapper inside countdown owns Controller, Services and pending
attempt state. Use ServiceSample as the sole timestamp/raw-gyro/confirmed-mask
input, plus logical button, previous finite bias and external stop. Return Gate's
Result, ServiceResult, service_start_failed and heading_reset_requested=gate.go.

Order: Controller first; on accepted release start Services at release_us; on
IDLE/STOP cancellation during pending attempt cancel before sampling; step Services;
return combined result before output gate. Explicit reset clears both components.
Do not derive GO from Services.finished, introduce a new motor veto, or reset the
physical board. Controller remains the GO authority. Raw gyro must precede bias
subtraction; previous bias is sampled at accepted release only. Caller supplies
confirmed masks and applies accepted bias/heading-reset request through HAL/app.

Header details to resolve before tests:
- Post-GO STOP lifetime: the harness retains pending after GO and would cancel
  completed evidence. A lifecycle can end pending at GO and retain completed
  service outputs, but document this diagnostic lifetime explicitly before coding.
- Expose existing nonfinite-previous-bias start failure; never report its default
  output as an accepted calibration. Do not invent a new fault/motor policy.
- Services accumulate elapsed intervals; Gate's release-relative subtraction can
  defer GO for unusually sparse calls spanning a full counter cycle. Preserve
  the existing Gate authority instead of using service completion as permission.

Full Robot/actuator ordering and actual sample freshness remain integration work.

# P0 counter adapter initial test discrepancies — 2026-09-23

The independent adapter author compiled the real opaque source through strict
host API substitutes without reading its .cpp. Initial result31/34 cases pass.
This is a new diagnostic test suite, not an established locked safety test.

1. Two forced IDLE callback cases expected terminal fault from the feasibility
   audit's recommendation. The committed public packet/adapter contract instead
   required TX disabled while idle. Actual code disables TX without FIFO work or
   counter changes; keeping it ready tolerates a settled stale pending interrupt.
   The installed-source auditor corrected that recommendation, and the fresh
   reviewer agreed this was an audit wording mismatch, not unsafe behavior.
2. A `positive_statuses` case expected update=2,ready=3,complete=4 to succeed from
   the audit's word "positive". Actual code accepts exactly1. The pinned binary
   returns1 for update and Boolean0/1 for ready/complete; the independent reviewer
   recommends retaining exact1 and treating all other values as unexpected.

Under D-051/D-062, the coordinator explicitly retains these source behaviors and
clarifies P0_counter_transport_contract.md before the author amends only those
three new cases. Retain all byte-count, no-TX-on-idle, terminal active-fault,
timeout, critical-section, refusal and completion assertions. No locked test,
motor rule, B16 default, driver source or phase gate changes. This is a documented
expectation-policy reconciliation, not a claim that the initial run passed.
The amended tests must still be independently authored and reviewed. No board
runtime test occurred during this discrepancy; compile-only succeeded separately.

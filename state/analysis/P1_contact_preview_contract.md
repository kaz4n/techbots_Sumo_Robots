# Read-only contact candidate — 2026-09-23 Asia/Dubai

D-056 resolves the upcoming Robot's current-contact/stall/final-state ordering
without committing twice or running Governor speculatively. Public contracts in
opp_fusion.h add Contact::previewLatch and Fusion::preview; existing observe and
commit contracts are unchanged. These queries never mutate pending observations,
cue counts, latch or event state. Only final commit authorizes downstream contact.

Acceptance: independent tests from D-027/D-056 and public headers, covering
repeated/different-state previews, pending/no-pending, visual/impact cues, ineligible
clear versus preview-only nonclear, skipped commits, cached observations and reset.
Implementation can factor existing commit arithmetic through its const preview,
then mutate the latch once. Full Robot/stall/governor/application integration is
not claimed by this component addition. No board operation is required.

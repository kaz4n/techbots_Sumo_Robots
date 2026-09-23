# D112 draft source/API preflight

**PASS, draft scope only.** Reused separate same-model reviewer; existing source bodies were inspected to check the proposed API contract. No implementation, test, configuration or hardware changes were made.

- One `power::Reader` with `beginWithButtons()` and `readButtons()` matches the existing fixed A0/A1 profile and A1/channel10 raw acquisition. It preserves the shared fault/ownership latch and does not introduce a second ADC owner or battery read.
- `readButtons()` publishes raw/timestamps unchanged, increments its sequence only for successful conversions and leaves invalid sequence/raw zero. Proposed success-only brackets and contiguous sequence admission agree with the native owner; failure timestamps/cleanup remain diagnostic.
- Actual `ui::decodeButtons()` accepts the proposed single-input delivery. Its default, unconfigured, unknown, ambiguous and invalid qualifications remain distinct from raw-source acceptance. The proposed `decode_matches_sample` flag correctly distinguishes an older retained decode after rejected A.
- Caller-granted ADC access, passive defaults, admitted S/A/C timing, immutable capture prefix and absence of a shutdown API are explicit. The contract does not infer NONE as a release or decoder qualification from COMPLETE.
- The five-public-record saturation example is reachable under its labelled temporary timing profile. Native sequence wrap is correctly excluded for a new finite128-record owner.
- Remaining prerequisites before any implementation verdict: adopted exact contract/public interfaces, independently frozen executable cases, source review, checked default/Immediate targets and startup/import/loader audit. B6 gesture, electrical-window and physical display acceptance remain separate.

No material draft contradiction found. Exact document/API/source hashes are in `d112_preflight.json`; this is no approval of future source, artifacts, pin access or a physical run.

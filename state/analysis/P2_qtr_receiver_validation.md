# D105 calibration receiver validation

2026-09-23 Asia/Dubai. IMPLEMENTED / HOST-TESTED / REVIEWED, parser scope only.

`tools/qtr_config.py` validates one canonical received threshold line with an
explicit firmware timeout and writes original bytes plus a five-field receipt
to a new directory. It never edits config.h or sends commands. The receipt says
`UNATTRIBUTED_BARE_LINE`: no board, firmware or physical-calibration provenance
can be inferred from these bytes alone.

The independent spec/public-interface-derived test file froze at
`5d8b66a1d1059d99e6d663fa5ca9ecd8b63d68f295d1ddbb3d230b8af4574d49`
before implementation. Its ten cases passed unchanged on Windows and WSL/Linux;
the latter exercised symlink/FIFO rejection without skips. Evidence:
`P2_app_build_raw/d105_parser_initial.{json,txt}` and
`P2_calibration_delivery_raw/author/parser_{freeze,run1}.json` / `parser_run1.txt`.

Separate same-model reviewer `/root/runtime_inert_review` approved source
`cf09e26903417ba8f15a05cf1acf221eb2fd42239c24d0129eea209600c07562`
after inspecting the exact grammar, bounded80-byte read, filesystem rejection,
exclusive publication and lack of config/network/process operations. Its own
ten-case Linux run passed in
`reviews/P2_calibration_delivery_review_raw/host_1790191368160591863.json`.
This is separate-context review, not cross-model review or a human gate.

Example for an already received file:
`python tools/qtr_config.py received.txt --timeout-us 1500 --output-dir new-receipt`
The timeout must match the intended firmware. Successful parsing does not apply
thresholds or establish that they were measured. Runtime delivery, target memory
fit, native UART and physical calibration remain separately tracked in D105.

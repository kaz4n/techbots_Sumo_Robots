# D114 independent guard test result

PASS: 22 methods, zero failures/errors/skips in isolated WSL on the unchanged first guard/board source freeze. Final test SHA `4cd63920370c23f6ec4b538a353c6f7dc2277bc2e032ad3fdc7eeee342e3e130`; final harness `af6d21d49b6df4d34f0be599ca5a34879d67ec5a7ad137030c5f6f26f64a11a3`.

First frozen run retained one fixture failure: mocked stage returned a directory named `stage`, whereas the public staging contract and unchanged expected upload path require `ui_adc_probe`. Root approved the exact one-value correction before re-freeze. All assertions and expected paths remain unchanged; original test/freeze/run and byte diff remain in this directory. The separate amended harness differs only in selecting the amended freeze receipt.

`validation.json` binds both copied source identities and `run_1790201759093568814.json`; full stdout/stderr accompany every run. Original first test SHA `7e5c6efb916bec1558a11d16bc0b26cdd6959cbb7000e4e55ec0e312e8b60831` is preserved.

Independence: this reused reviewer context previously read old board_tool, but did not read the new guard body or pending board diff. Expected behavior comes from the public contract; the implementation was copied and executed opaquely. A separate context owns actual guard source review. Existing tests were not edited. No board command, live approval/run record, manifest key or upload was created.

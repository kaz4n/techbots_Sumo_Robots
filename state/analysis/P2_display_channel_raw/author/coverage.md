# D108 independent author scope

The author derived expectations from P2_display_channel_contract.md, the public
ui_display/types/fsm interfaces, D088's preserved rules and existing test
fixtures. No ui_display.cpp body was read. Source bytes were copied and hashed
opaquely for isolated runs and retained red/green evidence. Prior D104 and
D105-D107 context was retained, so this is independence from the D108 renderer
implementation, not a fresh whole-repository or cross-model review.

The authorized amendment to tests/test_ui_display.cpp changes only its first
two opponent oracle offsets from 17,15 to 15,17 and adds a D108 comment. The
before copy and oracle_amendment.json prove all other non-comment tokens are
identical. All 15 prior cases and their 47 CHECK, 10 CHECK_FALSE and 3 CAPTURE
macro sites remain. The exhaustive 128 opponent masks, 16 line masks and four
availability combinations remain intact, as do guards and all pixel assertions.

The additive tests/test_display_channels.cpp uses literal channel masks and
(column,row) coordinates in B0/D076 order. Each one-hot result passes through
the actual public displaySample and render functions in both legacy and explicit
source-freshness modes. Deliberately unrelated input electrical bits cannot
replace the result mask; masks remain unchanged. Every output byte is checked
after poisoning the output frame. Other checks cover the seven unknown-group
positions while retaining the original mask, plus empty, combined front and
all-channel masks. Unchanged robot outline, line-off and unknown-battery pixels
are included in these literal frames. These are public projection/render tests,
not tests that construct actual sensor hardware or claim new Robot behavior.

Targeted normal/sanitizer runs include both the full preserved 15-case display
suite and the three additive cases. The red characterizations use an opaque
copy of the old renderer, and green runs use the coordinator's frozen corrected
source. The full-host snapshot includes all current source/tests and the
unchanged CMake configuration, and runs both ordinary and motor-enabled host
test targets. No shared build, source tuning, locked-test change, firmware
upload, board access or network operation is used.

All measured durations here are host test execution only. Pixel-array success
does not prove physical optical orientation, electrical wiring, sensor polarity,
loaded target RAM, motor safety, complete-app WCET or any human phase gate.

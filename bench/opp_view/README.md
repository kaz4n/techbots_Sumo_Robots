# Opponent input bench (P2 B1)

This bench uses the existing seven-input driver and matrix owner. Its checked-in
grants are all false: setup and loop do not configure or read pads or write the
matrix. It has no motor owner. Build-only commands are:

```
python tools/board_tool.py flash bench/opp_view --compile-only
python tools/board_tool.py flash bench/opp_view --compile-only --startup immediate
```

The board connection settings are the same as other project builds. Uploads and
MATCH are refused. Actual sensor operation needs a separately reviewed revision
with the existing electrical/pad ownership and normal-startup matrix grants.
Immediate compilation does not authorize matrix operation. The current bare-board
test uses the separate runtime_inert sketch; do not replace it with this bench.

When explicitly enabled in a future reviewed revision, columns0,2,4,6,8,10,12
on rows2 and3 show channels0..6: FL15,FC,FR15,SL,SR,RL,RR under D076's proposed
map. Bright means current detection, off means current clear, dim means unknown.
The top row latches a sensor setup/read error. A terminal fault can leave an old
image displayed; check the retained report before treating an image as live.

Runner's report retains original signed statuses/raw bits/timestamps, current
availability, first failed snapshot, read/invalid/missed counters, matrix status
and actual inner poll timing. Reports have no serial/Bridge command or export
path. Host test fixtures are synthetic. Software tests and target compilation
do not establish sensor polarity, range, sixty seconds without false hits,
optical orientation or the full application's800us worst-case tick requirement.
See state/analysis/P2_opp_view_contract.md and the validation/review evidence.

# D102 local Git staging correction

Windows Git refused the long nested receiver evidence paths during the first
add. The shell continued, so commit412f85f contains only the18command/status
receipts, despite its broader message. No source work was lost. History is
preserved; the next commit records the actual implementation and remaining
review/evidence. Per-command git -c core.longpaths=true handles the existing
paths without changing global Git configuration or captured evidence names.
All subsequent commands are checked before committing.

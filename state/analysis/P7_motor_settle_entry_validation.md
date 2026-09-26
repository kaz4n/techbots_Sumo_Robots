# D199 SETTLE entry reader host validation

The fixed reader sourcec9e8f023 implements adopted contractaf8ce726 and binding62346762.
It preserves the D199/D194 file-only lifecycle through original-first private
composition, nine reader metadata substitutions and36 parser substitutions. The
new entry query/summary functions replace their ABI counterparts directly.
All five descriptor/bootstrap source bodies are unchanged. The fixed scope has
29 instruction ranges,31 required function aliases and59 GDB expressions.

The independent oracle4e6e1cae was frozen before its author inspected the new
implementation. Its19 historical methods retain77 assertion call sites through
explicit fixture adaptations, plus four focused current binding/range/summary
checks. Both first serial runs passed23/23 methods with no skips; raw receipts
6caf4bde (Linux) and1d229c81 (Windows) are preserved. All204 coordinator input pins
remain exact, with no new bytecode; closing receipt1d798f24 is PASS. No failed
run, test repair or retry occurred.

Separate fresh-context same-model source/host reviewdcf1a079 reports no open
findings and independently verifies projections, alias fixtures and raw results.
A fresh fixed entry scope is prepared for one check-only followed by one
file-only execution at a clean reviewed HEAD. The existing attempt guards check
board boot, exact installed/source/artifact pins, owner absence, command bounds,
first errors and closing evidence. Actual file instructions have not yet been
observed by this new owner.

Successful parsing will still require separate semantic review of the actual
initializer and publication/SETTLE blocks. Source/host checks prove no report
contents, target execution, failure cause, repair, live RAM/WCET, motor permission
or physical/human gate. D195 remains flashed.

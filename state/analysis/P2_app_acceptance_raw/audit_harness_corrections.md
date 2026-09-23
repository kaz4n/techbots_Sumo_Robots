# Local analysis helper corrections

No board collection or firmware acceptance failed in this audit. Two local
inspection helpers required correction, with no source/test/build change:

1. An ad-hoc disassembly snippet extractor called splitlines()[0] on the empty
   leading chunk created by re.split. It raised IndexError. Filtering empty
   chunks produced the saved default/MATCH motor_macro_disassembly.txt excerpts.
2. After observing MATCH's376-byte text growth, a new local analyzer assertion
   incorrectly assumed its newly retained __aeabi_d2uiz veneer was4bytes. The
   ELF symbol table proves10bytes, hex40f2000cc0f2000c6047, with relocations to
   the existing __real___aeabi_d2uiz import. Its size and net layout delta are
   distinct quantities. Corrected assertion requires10; final analyzer passes.
   A dependent attempted read of the not-yet-written result key then raised
   KeyError; it did not overwrite the prior successful comparison.json.

The final comparison records the complete veneer, changed function sizes,
relocations and actual section sizes. No expectation about motor safety or a
production test was relaxed. The compiler statuses and raw captures are intact.

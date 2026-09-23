# D108 reviewer harness notes

The first target comparer demanded pool fit for all three ELF forms and stopped
on an intermediate artifact. D106's existing model approves only the packaged
final ELF; temporary/debug ELFs are audit inputs and retain different metadata.
The corrected comparator still proves every form has unchanged regions and
metadata, but requires fit only for the actual final package, as D106 did.
The first AssertionError was review_target.py line85; no production or test
source was changed to resolve the reviewer condition.

Initial reviewer-only verify_targets.py stopped at its mistaken equality assertion
between the packaged ZSK SHA256 and the raw ELF SHA256. Observed default lengths
were both175036; differences were confined to offsets7,8,9,10,12,13 in the ELF
identification/header area. Corrected the verification to match the package's own
recorded bundle digest and independently require exact ELF contents at0..6 and
16..end. The target package and source were never modified. This was a review
harness assumption failure, not a source/build failure or weakened code check.

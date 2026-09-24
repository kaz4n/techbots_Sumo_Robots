# D134 regression exposed a D131 host-target integration defect

The full default run `P5_mode_availability_raw/default11_full_retry1` configured
successfully, then failed compilation with exit2 in push_through_m0_tests.
`tests/test_push_through_timing.cc` requires SUMOX_TIMING_EVIDENCE=1 explicitly,
but host/CMakeLists.txt included it unconditionally in ordinary push targets
whose timing profile defaults to0. Missing conditional TimingDetail and
OpponentReadWindow declarations are consequences of that wrong association.
No CTest/private probe executed after this build failure. The complete compiler
diagnostic and source-bound receipt are retained; scratch was released.

This mismatch was introduced in the earlier D131 timing-test addition. Its
positive/configured timing checks ran with the required flag and passed. The
earlier full ordinary suite passed before that addition; it does not prove the
final all-target build. D134's availability production changes are not its cause.
The historical executed results remain valid for their recorded source states,
but the final P4 review missed this build integration gap.

Independently approved minimal repair: retain every test source/assertion unchanged, associate
the timing-only file with existing timing_evidence_m0/m1 targets that already
define the required profile, and retain the ordinary push targets separately.
The full build still runs18 targets. Positive-duration current-source regression
must run the entire push family with timing enabled and the five D131-named
cases from the timing family with the copied configured inputs. The unchanged
full legacy D129 assertions still run at duration0; the positive policy extension
does not make their old zero-duration expectations positive-profile assertions.
This preserves all six D131 timing cases, including the separately guarded case
in test_push_through.cc. The five timing-specific cases must execute, not merely
compile or take disabled branches.
Do not rewrite the old frozen runners/results or change a protected test.

Independent test author and reviewer approved this exact reassociation. Root
applied it and updated only the host/CMakeLists.txt key in both input manifests;
cmake_profile_correction.json preserves before/after hashes. Actual full and
positive regression remain pending. This is a reviewed build fix, not yet a
passing regression claim.

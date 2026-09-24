# Validation when optional modes are removed

D134 software-scope clarification under D051, 2026-09-24. Independent review
found no blocker for the present shipped1/1 configuration. Existing all-six
opener/menu assertions deliberately assume those capabilities are available;
running them unchanged against a future0/0 source is not expected to pass.
Do not skip assertions, modify locked tests or label that source full-suite green.

For a later reduced release, bind two explicitly identified configurations:

1. Run the unchanged legacy/capability suite on an otherwise identical temporary
   source with both availability flags1 and the baseline default1. Record the
   exact substitutions and hashes; this is baseline capability coverage.
2. Run the additive owner/MotorGate/menu/admission/sanitizer checks on the actual
   reduced flags and selected enabled default, using that exact source identity.
   This is actual reduced-configuration coverage. Preserve the four-pair matrix
   and all original safety requirements; no unavailable opener is invoked as a
   substitute for a mandatory one.

Report these separately. Compilation/fit and physical trials must use the actual
release configuration and its own evidence. Existing frozen task runners bind
their recorded inputs; they are not permission to relabel a future modified tree.
A reviewed release recipe may orchestrate both checks with the existing CMake
targets. A generic new runner is not necessary to establish today's D134 default
software result. No config value, production behavior or gate changes here.

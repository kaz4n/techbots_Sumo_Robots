The first local verifier invocation stopped at `assert audit['native_names'] == baseline['native_names']`.
The inert image intentionally removes seven unused device imports from the full-app baseline.
Corrected the review oracle to require an exact subset and identical installed export addresses for each retained native name.
This changes only the reviewer verifier; production source, target ELF and established tests are unchanged.

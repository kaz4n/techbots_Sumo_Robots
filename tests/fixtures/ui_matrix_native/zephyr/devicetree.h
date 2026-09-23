// Provides only the audited counter_matrix devicetree symbol.
// The fixture must not mask a production request for any other device node.
// The compile-only native seam consumes this exact macro name.
#pragma once
#define DT_NODELABEL_counter_matrix 233
#define DT_NODELABEL(label) DT_NODELABEL_##label

// Provides the installed UART register declarations without polling helpers.
// Direct finite register operations are the only permitted native TX surface.
// Missing blocking helpers make accidental stock operations a compile failure.
#pragma once
#include "cmsis_core.h"

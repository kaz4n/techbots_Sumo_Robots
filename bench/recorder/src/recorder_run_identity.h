// Defines the recorder delivery attempt; the checked-in profile stays disabled.
// A reviewed caller stages a fresh positive identity without changing this file.
// Session tests verify default-off grants and exact generated identity admission.
#pragma once
#include "hal/dump_uart_unoq.h"

namespace recorder_run_identity {
inline constexpr bool ENABLED = false;
inline constexpr std::uint64_t SESSION = 0U;
inline constexpr recorder::dump::SetupGrant GRANTS{};
static_assert(!ENABLED || (SESSION != 0U && GRANTS.session == SESSION),
              "Enabled recorder delivery needs an identified session");
} // namespace recorder_run_identity

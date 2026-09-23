// Declares bounded offline B15 CSV formatting in exact encoded integer units.
// Preserves raw evidence and loss metadata without transport or dump permission.
// Independent D-073 tests cover literal bytes, limits, capacity and snapshots.
#pragma once
#include "recorder.h"
#include <cstddef>
#include <cstdint>

namespace recorder::csv {
// Representation bounds, not tuning values. Includes LF and terminating NUL.
inline constexpr std::size_t MAX_LINE_BYTES = 1024U;
inline constexpr std::uint32_t SCHEMA_VERSION = 1U;
enum class FormatStatus : std::uint8_t { OK, INVALID_ARGUMENT, INSUFFICIENT_CAPACITY };
struct FormatResult {
    FormatStatus status = FormatStatus::INVALID_ARGUMENT;
    std::size_t size = 0U; // Successful bytes including LF, excluding NUL; failure0.
};
struct SummarySnapshot {
    AttemptSummary attempt;
    AttemptPhase phase = AttemptPhase::EMPTY;
    std::uint32_t frame_count = 0;
    std::uint32_t frame_overwritten = 0;
    std::uint32_t frame_rejected_status = 0;
    std::uint32_t frame_clamped = 0;
    std::uint32_t frame_invalid = 0;
    std::uint32_t event_count = 0;
    bool event_overflow = false;
    std::uint32_t event_rejected = 0;
    bool incomplete = false;
};
// Caller provides exclusive read access; no concurrent owner mutation. Copies
// only bounded metadata, never payload arrays. Phase/loss is not dump authority.
SummarySnapshot captureSummary(const AttemptRecorder& source);
// D-073 exact schemas/semantics: state/analysis/P2_csv_contract.md. Buffers must
// not overlap input objects. Null destination invalid; capacity0 insufficient.
// Failure writes NUL only at destination[0] when nonnull/capacity>0, size0.
// Success is complete ASCII CSV with one LF then NUL; no partial valid line.
FormatResult frameHeader(char* destination, std::size_t capacity);
FormatResult frameRow(const StoredFrame& frame, std::uint64_t ordinal,
                      char* destination, std::size_t capacity);
FormatResult eventHeader(char* destination, std::size_t capacity);
FormatResult eventRow(const logframe::EventBytes& event, std::uint64_t ordinal,
                      char* destination, std::size_t capacity);
FormatResult summaryHeader(char* destination, std::size_t capacity);
FormatResult summaryRow(const SummarySnapshot& summary,
                        char* destination, std::size_t capacity);
} // namespace recorder::csv

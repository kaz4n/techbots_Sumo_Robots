// Produces the exact B13 config threshold snippet in caller-owned fixed storage.
// All validation and capacity checks precede publication of any output bytes.
// Independent exact-format and capacity-boundary tests exercise this producer.
#include "qtr_cal.h"

namespace qtr_cal {
namespace {
void appendText(char* buffer, std::size_t& size, const char* text, std::size_t count) {
    for (std::size_t i = 0U; i < count; ++i) buffer[size++] = text[i];
}
void appendNumber(char* buffer, std::size_t& size, std::uint32_t value) {
    char reverse[10];
    std::size_t digits = 0U;
    for (unsigned i = 0U; i < 10U; ++i) {
        reverse[digits++] = static_cast<char>('0' + value % 10U);
        value /= 10U;
        if (value == 0U) break;
    }
    for (std::size_t i = 0U; i < digits; ++i) buffer[size++] = reverse[digits - i - 1U];
}
} // namespace

FormatStatus formatConfig(const Report& report, char* output, std::size_t capacity,
                          std::size_t& written) {
    written = 0U;
    if (output != nullptr && capacity != 0U) output[0] = '\0';
    if (report.phase != Phase::SUCCESS) return FormatStatus::UNAVAILABLE;
    if (report.thresholds.version == 0U || !line_qtr::validThresholds(report.thresholds) ||
        output == nullptr) return FormatStatus::INVALID;
    char buffer[CONFIG_SNIPPET_CAPACITY];
    std::size_t size = 0U;
    constexpr char prefix[] = "QTR_WHITE_US[4] = {";
    constexpr char suffix[] = "}; // us\n";
    appendText(buffer, size, prefix, sizeof(prefix) - 1U);
    for (unsigned i = 0U; i < 4U; ++i) {
        if (i != 0U) appendText(buffer, size, ", ", 2U);
        appendNumber(buffer, size, report.thresholds.white_us[i]);
        buffer[size++] = 'U';
    }
    appendText(buffer, size, suffix, sizeof(suffix) - 1U);
    if (capacity <= size) return FormatStatus::BUFFER_TOO_SMALL;
    for (std::size_t i = 0U; i < size; ++i) output[i] = buffer[i];
    output[size] = '\0';
    written = size;
    return FormatStatus::OK;
}
} // namespace qtr_cal

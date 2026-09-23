// Declares the QTR capture bench binding to exactly one existing native Reader.
// Preserves passive construction, explicit ownership grant and direct callback delegation.
// Counted Reader substitutes and exact target startup inspection test this binding.
#pragma once
#include "qtr_raw.h"

namespace qtr_raw {
class Native {
public:
    Native() = default;
    Native(const Native&) = delete;
    Native& operator=(const Native&) = delete;
    Port port();
private:
    static std::uint32_t clockUs(void* context);
    static line_qtr::Status beginReader(void* context, bool exclusive_pads);
    static line_qtr::Status startReader(void* context);
    static line_qtr::Snapshot readerReport(void* context);
    static line_qtr::Snapshot advanceReader(void* context);
    static line_qtr::Snapshot cancelReader(void* context);
    line_qtr::Reader reader_;
};
} // namespace qtr_raw

// Binds the finite QTR capture runner directly to one existing native Reader.
// Keeps construction passive and preserves explicit grant, status and snapshot values.
// Independent counted Reader substitutes and target startup inspection test this binding.
#include "qtr_raw_native.h"
#include <Arduino.h>

namespace qtr_raw {
Port Native::port() {
    return {this, &clockUs, &beginReader, &startReader, &readerReport,
            &advanceReader, &cancelReader};
}
std::uint32_t Native::clockUs(void*) { return static_cast<std::uint32_t>(micros()); }
line_qtr::Status Native::beginReader(void* context, bool exclusive_pads) {
    return static_cast<Native*>(context)->reader_.begin(exclusive_pads);
}
line_qtr::Status Native::startReader(void* context) {
    return static_cast<Native*>(context)->reader_.start();
}
line_qtr::Snapshot Native::readerReport(void* context) {
    return static_cast<Native*>(context)->reader_.report();
}
line_qtr::Snapshot Native::advanceReader(void* context) {
    return static_cast<Native*>(context)->reader_.advance();
}
line_qtr::Snapshot Native::cancelReader(void* context) {
    return static_cast<Native*>(context)->reader_.cancel();
}
} // namespace qtr_raw

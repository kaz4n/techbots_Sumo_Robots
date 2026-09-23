// Supplies the existing NativeSources public signatures for the opaque app sketch.
// Actual Runtime remains linked, while established counted source callbacks supply no hardware.
// This substitute does not change the native-dump API or its grant semantics.
#pragma once
#include "runtime.h"
namespace app {
class NativeSources {
public:
    SourcePort port();
    power::InputPort adcPort();
};
}

// Includes an unconditional external library for the D099 dependency experiment.
// Gives both discovery settings the same library requirement without peripheral I/O.
// Compile-only evidence must show SumoPolicyFixture in used_libraries for both modes.
#include <SumoPolicyFixture.h>
volatile unsigned sumoPolicyFixtureObserved = 0U;
void setup() { sumoPolicyFixtureObserved = sumoPolicyFixtureValue(); }
void loop() {}

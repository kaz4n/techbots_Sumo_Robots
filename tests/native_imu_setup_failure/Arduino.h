// Declares only the counted native clock for the D097 callback substitute.
// Any unprovided hardware API prevents a host link rather than touching a board.
// Native callback tests require zero clock calls during passive fault retrieval.
#pragma once
unsigned long micros();

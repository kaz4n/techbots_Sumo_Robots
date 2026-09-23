// Declares only the clock surface needed by the native opponent adapter.
// Any accidental Arduino GPIO, wait, serial or Bridge use fails to compile.
// Independent host cases link the real adapter against these counted functions.
#pragma once
unsigned long micros();

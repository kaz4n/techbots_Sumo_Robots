#include "src/app/runtime.h"
#include <cstdio>
int main(){std::printf("RobotResult=%zu Runtime=%zu Transaction=%zu Transfer=%zu Input=%zu\n",sizeof(fsm::RobotResult),sizeof(app::Runtime),sizeof(app::Transaction),sizeof(recorder::dump::Transfer),sizeof(fsm::RobotInput));}

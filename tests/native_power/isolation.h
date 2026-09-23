// Gives each modeled boot a separate operating-system process.
// Driver static ownership survives within a boot and has no test reset backdoor.
// Child assertions and crashes must propagate as a failing parent assertion.
#pragma once
#include "doctest.h"
#include <cstdio>
#include <sys/wait.h>
#include <unistd.h>
namespace fixture {
extern bool child_assertion_failed;
template<class F> void isolated(F&& body) {
    std::fflush(nullptr);const auto pid=fork();REQUIRE(pid>=0);
    if(pid==0){child_assertion_failed=false;body();std::fflush(nullptr);_exit(child_assertion_failed?1:0);}
    int status=0;REQUIRE(waitpid(pid,&status,0)==pid);
    CHECK(WIFEXITED(status));CHECK((WIFEXITED(status)?WEXITSTATUS(status):-1)==0);
}
}

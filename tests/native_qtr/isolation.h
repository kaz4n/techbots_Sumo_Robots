// Gives each modeled boot a separate operating-system process.
// Driver static ownership survives within a boot and has no test reset backdoor.
// Child assertions and crashes must propagate as a failing parent assertion.
#pragma once
#include "doctest.h"
#include <cstdio>
#include <cstdint>
#include <sys/wait.h>
#include <unistd.h>
namespace fixture {
extern bool child_assertion_failed;
extern std::uint64_t child_assertion_count,total_child_assertions;
template<class F> void isolated(F&& body) {
    int counts[2];REQUIRE(pipe(counts)==0);
    std::fflush(nullptr);const auto pid=fork();REQUIRE(pid>=0);
    if(pid==0){close(counts[0]);child_assertion_failed=false;child_assertion_count=0;body();
        const auto written=write(counts[1],&child_assertion_count,sizeof(child_assertion_count));
        close(counts[1]);std::fflush(nullptr);_exit(child_assertion_failed||written!=sizeof(child_assertion_count)?1:0);}
    close(counts[1]);std::uint64_t observed=0;
    const auto received=read(counts[0],&observed,sizeof(observed));close(counts[0]);
    int status=0;REQUIRE(waitpid(pid,&status,0)==pid);
    CHECK(WIFEXITED(status));CHECK((WIFEXITED(status)?WEXITSTATUS(status):-1)==0);
    CHECK(received==sizeof(observed));total_child_assertions+=observed;
}
}

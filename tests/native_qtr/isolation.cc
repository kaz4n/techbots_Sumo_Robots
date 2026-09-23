// Forwards doctest assertion failures to the native child process exit status.
// Without this listener nonfatal CHECK failures could vanish at a fork boundary.
// Parent assertions independently check normal child termination and exit zero.
#include "isolation.h"
namespace fixture { bool child_assertion_failed=false;std::uint64_t child_assertion_count=0,total_child_assertions=0; }
struct ChildFailureListener:doctest::IReporter {
 explicit ChildFailureListener(const doctest::ContextOptions&){}
 void report_query(const doctest::QueryData&) override{}
 void test_run_start() override{}
 void test_run_end(const doctest::TestRunStats&) override{std::printf("Native isolated child assertions: %llu\n",static_cast<unsigned long long>(fixture::total_child_assertions));}
 void test_case_start(const doctest::TestCaseData&) override{}
 void test_case_reenter(const doctest::TestCaseData&) override{}
 void test_case_end(const doctest::CurrentTestCaseStats&) override{}
 void test_case_exception(const doctest::TestCaseException&) override{fixture::child_assertion_failed=true;}
 void subcase_start(const doctest::SubcaseSignature&) override{}
 void subcase_end() override{}
 void log_assert(const doctest::AssertData& a) override{++fixture::child_assertion_count;if(a.m_failed)fixture::child_assertion_failed=true;}
 void log_message(const doctest::MessageData&) override{}
 void test_case_skipped(const doctest::TestCaseData&) override{}
};
REGISTER_LISTENER("child-failure-exit",0,ChildFailureListener);

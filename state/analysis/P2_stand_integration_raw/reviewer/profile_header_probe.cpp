
#include "core/fsm.h"
#include "app/runtime.h"
#include <type_traits>
#include <utility>
template<class T, class = void> struct HasStand : std::false_type {};
template<class T> struct HasStand<T, std::void_t<decltype(std::declval<T>().stand)>> : std::true_type {};
static_assert(fsm::RobotResult::STAND_PROFILE == (SUMOX_B4_STAND != 0));
static_assert(HasStand<fsm::RobotResult>::value == (SUMOX_B4_STAND != 0));
static_assert(static_cast<unsigned>(governor::Profile::SEARCH_FORWARD) == 0);
static_assert(static_cast<unsigned>(governor::Profile::PIVOT) == 1);
static_assert(static_cast<unsigned>(governor::Profile::OPENER) == 2);
static_assert(static_cast<unsigned>(governor::Profile::ATTACK) == 3);
static_assert(static_cast<unsigned>(governor::Profile::EDGE_REVERSE) == 4);
static_assert(static_cast<unsigned>(governor::Profile::REFLANK_BACK) == 5);
static_assert(static_cast<unsigned>(governor::Profile::REFLANK_TURN) == 6);
static_assert(static_cast<unsigned>(governor::Profile::EDGE_FORWARD) == 7);
#if SUMOX_B4_STAND == 1
static_assert(static_cast<unsigned>(governor::Profile::STAND) == 8);
static_assert(std::is_same_v<decltype(fsm::RobotResult{}.stand_stopping), bool>);
#endif
int main() { return 0; }

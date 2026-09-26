// Retains one bounded population of consecutive application loop-entry intervals.
// Includes delayed observer work without claiming calibrated CPU execution time.
// D243 host fixtures check windows, chronology, classification and frozen closure.
#pragma once
#include "runtime.h"
#include <cstdint>
#include <limits>

namespace app::outer_loop_timing {
static_assert(config::OUTER_LOOP_WINDOW_US > 0U &&
              config::OUTER_LOOP_WINDOW_US < 0x80000000U);
static_assert(config::APP_CLOCK_STALL_MAX_POLLS > 0U);
enum class Status : std::uint8_t {
    NOT_STARTED, SAMPLING, DRAINING, SEALED, CLOCK_ERROR, CLOCK_STALLED,
    MISSING_CONTEXT, SATURATED
};
struct Context {
    RuntimePhase phase = RuntimePhase::NOT_STARTED;
    RuntimeFault fault = RuntimeFault::NONE;
    std::uint32_t epochs = 0U;
    bool initialized = false; // A readiness latch, not continuous sensor liveness.
    static Context read(const RuntimeReport& report) {
        return {report.phase, report.fault, report.epochs, report.initialization_complete};
    }
};
struct Poll {
    Context before;
    Context after;
    bool returned = false;
};
struct Count {
    std::uint32_t polls = 0U;
    std::uint32_t maximum_us = 0U;
};
struct Data {
    epoch_timing::Distribution all;
    epoch_timing::Distribution completed;
    Status status = Status::NOT_STARTED;
    Count idle, failed, terminal, uncertain;
    Poll pending, last_population, first_failure, first_uncertain;
    std::uint32_t anchor_us = 0U, pending_entry_us = 0U, last_entry_us = 0U;
    std::uint32_t last_population_entry_us = 0U;
    std::uint32_t close_entry_us = 0U, drain_end_us = 0U, drain_us = 0U;
    std::uint32_t bad_entry_us = 0U, equal_entries = 0U;
    std::uint64_t elapsed_us = 0U, close_elapsed_us = 0U, overshoot_us = 0U;
    bool pending_context = false, population_closed = false;
};
struct Summary {
    Status status = Status::NOT_STARTED;
    epoch_timing::Summary all;
    epoch_timing::Summary completed;
    bool population_closed = false;
    bool classification_certain = false;
};
class Observer {
public:
    bool terminal() const {
        return data_.status != Status::NOT_STARTED && data_.status != Status::SAMPLING &&
               data_.status != Status::DRAINING;
    }
    // Call once at loop entry, before taking Runtime's before-context.
    void entry(std::uint32_t now_us) {
        if (terminal()) return;
        if (data_.status == Status::NOT_STARTED) {
            data_.anchor_us = data_.last_entry_us = data_.pending_entry_us = now_us;
            data_.status = Status::SAMPLING;
            return;
        }
        if (!data_.pending_context) { fail(Status::MISSING_CONTEXT, now_us); return; }
        const auto delta = now_us - data_.last_entry_us;
        if (!accept(delta, now_us)) return;
        data_.elapsed_us += delta;
        data_.last_entry_us = now_us;
        if (data_.status == Status::DRAINING) {
            data_.drain_end_us = now_us;
            data_.drain_us = delta;
            data_.status = Status::SEALED;
            return;
        }
        observe(delta, now_us);
        if (terminal()) return;
        if (data_.elapsed_us >= config::OUTER_LOOP_WINDOW_US) {
            data_.close_entry_us = now_us;
            data_.close_elapsed_us = data_.elapsed_us;
            data_.overshoot_us = data_.elapsed_us - config::OUTER_LOOP_WINDOW_US;
            data_.population_closed = true;
            data_.status = Status::DRAINING;
        }
        data_.pending_entry_us = now_us;
        data_.pending_context = false;
    }
    // Post-step stores are inside this interval, before the next entry timestamp.
    void result(const Context& before, const Context& after, bool returned) {
        if (terminal() || data_.status == Status::NOT_STARTED) return;
        if (data_.pending_context) { fail(Status::MISSING_CONTEXT, data_.last_entry_us); return; }
        data_.pending = {before, after, returned};
        data_.pending_context = true;
    }
    const Data& data() const { return data_; }
    // Never invoked by the application loop; live reads require separate coherence.
    Summary summary() const {
        return {data_.status, data_.all.summary(), data_.completed.summary(),
            data_.population_closed,
            data_.uncertain.polls == 0U};
    }
private:
    void fail(Status reason, std::uint32_t entry_us) {
        data_.bad_entry_us = entry_us;
        data_.status = reason;
    }
    bool accept(std::uint32_t delta, std::uint32_t now_us) {
        if (delta >= 0x80000000U) { fail(Status::CLOCK_ERROR, now_us); return false; }
        if (delta != 0U) data_.equal_entries = 0U;
        else if (++data_.equal_entries >= config::APP_CLOCK_STALL_MAX_POLLS) {
            fail(Status::CLOCK_STALLED, now_us);
            return false;
        }
        return true;
    }
    static void count(Count& category, std::uint32_t duration) {
        if (category.polls != std::numeric_limits<std::uint32_t>::max()) ++category.polls;
        if (duration > category.maximum_us) category.maximum_us = duration;
    }
    static bool contextValid(const Context& value) {
        return value.phase <= RuntimePhase::STOP_OBSERVING &&
            value.fault <= RuntimeFault::PROJECTION &&
            ((value.phase == RuntimePhase::FAULT) == (value.fault != RuntimeFault::NONE));
    }
    static bool coherent(const Poll& poll) {
        if (!contextValid(poll.before) || !contextValid(poll.after)) return false;
        const bool active = poll.before.phase == RuntimePhase::RUNNING ||
            poll.before.phase == RuntimePhase::STOP_OBSERVING;
        if (!active) return !poll.returned && poll.before.phase == poll.after.phase &&
            poll.before.fault == poll.after.fault && poll.before.epochs == poll.after.epochs &&
            poll.before.initialized == poll.after.initialized;
        if (poll.after.phase == RuntimePhase::NOT_STARTED) return false;
        if (poll.returned) return poll.after.phase != RuntimePhase::FAULT;
        if (poll.after.phase == RuntimePhase::FAULT) return true;
        return poll.before.phase == poll.after.phase && poll.before.epochs == poll.after.epochs;
    }
    void observe(std::uint32_t duration, std::uint32_t now_us) {
        const auto& poll = data_.pending;
        const auto limit = std::numeric_limits<std::uint32_t>::max();
        const bool advanced = poll.before.epochs != limit &&
            poll.after.epochs == poll.before.epochs + 1U;
        const bool completed = poll.returned || advanced;
        const bool uncertain = !coherent(poll) || (poll.before.epochs == limit) ||
            (poll.after.epochs != poll.before.epochs && !advanced) ||
            (poll.returned && !advanced && poll.before.epochs != limit);
        const bool failed = poll.after.phase == RuntimePhase::FAULT &&
            (poll.before.phase != RuntimePhase::FAULT || poll.before.fault != poll.after.fault);
        data_.all.observe(duration, data_.pending_entry_us, now_us);
        if (data_.all.data().saturated) { fail(Status::SATURATED, now_us); return; }
        data_.last_population = poll;
        data_.last_population_entry_us = data_.pending_entry_us;
        if (completed) data_.completed.observe(duration, data_.pending_entry_us, now_us);
        if (uncertain) {
            if (data_.uncertain.polls == 0U) data_.first_uncertain = poll;
            count(data_.uncertain, duration);
        }
        if (failed) {
            if (data_.failed.polls == 0U) data_.first_failure = poll;
            count(data_.failed, duration);
        } else if (!completed && !poll.returned) {
            if (poll.after.phase == RuntimePhase::RUNNING ||
                poll.after.phase == RuntimePhase::STOP_OBSERVING) count(data_.idle, duration);
            else count(data_.terminal, duration);
        }
        if (data_.all.data().saturated || data_.completed.data().saturated)
            fail(Status::SATURATED, now_us);
    }
    Data data_;
};
} // namespace app::outer_loop_timing

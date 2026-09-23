# Checks consequences of a deliberately weak model allowed by the register text.
# Demonstrates why coherent payload bytes alone do not bind INT_STATUS generation.
# This is an epistemic counterexample and protocol check, not MPU silicon simulation.
from itertools import product
from pathlib import Path
import json

class Model:
    def __init__(self, internal=0, visible=0, flag=0):
        self.internal, self.visible, self.flag = internal, visible, flag
        self.idle = True
    def update(self, count):
        self.internal += count
        if count:
            self.flag = 1
        if self.idle:
            self.visible = self.internal
    def start(self):
        self.idle = False
    def status(self):
        result = self.flag
        self.flag = 0
        return result
    def stop(self):
        self.idle = True
        self.visible = self.internal

def acquire(m, events):
    m.update(events[0]); m.start(); m.update(events[1])
    probe = m.status()
    m.update(events[2]); m.stop(); m.update(events[3])
    if not probe:
        return None
    m.start(); m.update(events[4]); delivery_status = m.status()
    m.update(events[5]); payload = m.visible
    m.update(events[6]); m.stop(); m.update(events[7])
    return payload, delivery_status

m = Model()
m.start(); m.update(1)
single = {'status':m.status(), 'motion_generation':m.visible,
          'previous_motion_generation':0, 'internal_generation':m.internal}
assert single['status'] == 1 and single['motion_generation'] == 0

# A status probe may itself see an update while its motion shadow is frozen.
# Its STOP creates idle before the following payload transaction.
one_cases = 0
for initial in (0,1):
    for events in product(range(3), repeat=8):
        m = Model(initial, initial, 0)
        result = acquire(m, events)
        if result is not None:
            assert result[0] > 0
        one_cases += 1

# Two consecutive accepted acquisitions must strictly increase generation,
# including events during either payload/status window and after its STOP.
two_cases = accepted_pairs = 0
binary = list(product(range(2), repeat=8))
for events1 in binary:
    for events2 in binary:
        m = Model()
        first = acquire(m, events1)
        second = acquire(m, events2)
        if first is not None and second is not None:
            assert second[0] > first[0]
            accepted_pairs += 1
        two_cases += 1

out = {'scope':'Model counterexample, not measured or vendor-guaranteed silicon timing',
       'assumptions':['Internal conversion can set DRDY while interface is busy; source does not explicitly exclude this ordering',
                      'Motion shadow copies internal generation when interface is idle',
                      'Reading INT_STATUS clears its event flag; no other owner/read/reset',
                      'Complete STOP creates an idle shadow-copy opportunity before next START'],
       'single_burst_counterexample':single,
       'one_acquisition_cases':one_cases, 'two_acquisition_cases':two_cases,
       'accepted_pairs_checked':accepted_pairs,
       'result':'PASS: two-transaction inference strictly newer under stated model; single-burst status not sufficient',
       'does_not_prove':['physical sample timestamp','number of skipped generations','actual silicon event ordering','whole-tick WCET','all-temperature settling']}
Path(__file__).with_name('freshness_model.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

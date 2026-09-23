# Evaluates the proposed I2C4 timing against explicit conditional envelopes.
# Uses exact rational arithmetic and exhausts independent timing corners.
# This verifies arithmetic, not clocks, pad waveforms, stretch or target WCET.
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
root=Path(__file__).parent
PRESC,SCLDEL,SDADEL,SCLH,SCLL=4,14,11,32,44
DNF=0
fields={'PRESC':PRESC,'SCLDEL':SCLDEL,'SDADEL':SDADEL,'SCLH':SCLH,'SCLL':SCLL}
timing=(PRESC<<28)|(SCLDEL<<20)|(SDADEL<<16)|(SCLH<<8)|SCLL
assert timing==0x40EB202C and (timing & 0x0F000000)==0
freqs=[158_400_000,161_600_000]
af=[50,115]
edges=[0,300]
corners=[]
for freq,tr,tf,a1,a2,s1,s2 in product(freqs,edges,edges,af,af,[2,3],[2,3]):
 t=F(10**9,freq); p=(PRESC+1)*t
 high=a2+(DNF+s2)*t+(SCLH+1)*p
 low=a1+(DNF+s1)*t+(SCLL+1)*p
 period=tr+tf+high+low
 assert high>=600 and low>=1300 and period>=2500
 corners.append({'f_hz':freq,'tr_ns':tr,'tf_ns':tf,'af_low_ns':a1,'af_high_ns':a2,'sync_low_cycles':s1,'sync_high_cycles':s2,'high_ns':float(high),'low_ns':float(low),'period_ns':float(period)})
tmin=F(10**9,max(freqs)); tmax=F(10**9,min(freqs)); pmin=5*tmin;pmax=5*tmax
setup_min=(SCLDEL+1)*pmin-300
hold_min=50+(DNF+3)*tmin+SDADEL*pmin-300
valid_max=300+115+(DNF+4)*tmax+SDADEL*pmax
assert setup_min>=100 and hold_min>=0 and valid_max<=900
assert (SDADEL+SCLDEL+1)*(PRESC+1)+1 < (SCLL+1)*(PRESC+1)
stock_fastest_period=2*50+(19*5+41*5+4)*F(10**9,160_000_000)
assert stock_fastest_period==2000 and stock_fastest_period<2500
checks={
 'clock_period_ns':[float(tmin),float(tmax)],
 'prescaled_period_ns':[float(pmin),float(pmax)],
 'scl_high_ns':[min(x['high_ns'] for x in corners),max(x['high_ns'] for x in corners)],
 'scl_low_ns':[min(x['low_ns'] for x in corners),max(x['low_ns'] for x in corners)],
 'scl_period_ns':[min(x['period_ns'] for x in corners),max(x['period_ns'] for x in corners)],
 'scl_frequency_hz':[1e9/max(x['period_ns'] for x in corners),1e9/min(x['period_ns'] for x in corners)],
 'scldel_counter_ns':[float(15*pmin),float(15*pmax)],
 'sdadel_plus_one_clock_ns':[float(11*pmin+tmin),float(11*pmax+tmax)],
 'data_setup_min_ns':float(setup_min),
 'data_hold_min_ns':float(hold_min),
 'data_valid_max_ns':float(valid_max),
 'sda_delay_extra_stretch_max_ns':float(131*tmax),
 'scl_low_counter_min_ns':float(225*tmin),
 'scl_high_counter_min_ns':float(165*tmin),
 'kernel_constraint_low_rhs_ns':float((F(1300)-115)/4),
 'timing_envelope_only_no_observed_hardware':True,
}
tperiod=[min(x['period_ns'] for x in corners),max(x['period_ns'] for x in corners)]
transfers={}
for name,clocks in [('single_register_write',27),('single_register_read',36),('14_byte_read',153),('15_byte_read',162)]:
 transfers[name]={'scl_clocks':clocks,'modeled_clock_portion_us':[clocks*x/1000 for x in tperiod],'ideal_at_400khz_us':clocks/0.4}
deadlines={
 'request_us':600,'cleanup_us':50,'quantization_allowance_per_interval_us':1,
 'earliest_request_expiry_us':float(F(599,1)/F(101,100)),
 'latest_request_plus_cleanup_expiry_us':float(F(652,1)/F(99,100)),
 '15byte_worst_clock_portion_margin_to_earliest_request_us':float(F(599,1)/F(101,100))-transfers['15_byte_read']['modeled_clock_portion_us'][1],
 'remainder_before_800us_excluding_check_lateness_us':800-float(F(652,1)/F(99,100)),
 'shared_poll_count_backstop':8192,
 'count_caps_are_only_finite_not_proved_wall_time':True,
 'cleanup_policy':'owned PE disable only; no synthesized STOP or recovery',
 'nominal_800us_tick_allocation':{'request_plus_cleanup':650,'all_other_tick_work_before_tolerance_and_overheads':150},
}
assert transfers['15_byte_read']['scl_clocks']==162
assert deadlines['15byte_worst_clock_portion_margin_to_earliest_request_us']>0
out={'timingr':f'0x{timing:08X}','fields':fields,'analog_filter_enabled':True,'digital_filter_cycles':DNF,'conditional_clock_hz':freqs,'corner_count':len(corners),'checks':checks,'transfers':transfers,'deadline_proposal':deadlines,'negative_control_stock_period_ns':float(stock_fastest_period),'corners':corners}
(root/'calculation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='corners'},indent=2))

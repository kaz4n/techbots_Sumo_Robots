# HARDWARE.md

Source of truth for pins, wiring, electrical limits, mechanical constraints that affect code, and the physics numbers behind the speed governor.

Status tags: **[P]** proposal from research (22 Sep). **[V]** verified on hardware (update the tag and add the FACTS.md ID when checked). Rule R8 in AGENTS.md: humans own every wiring and pin change.

---

## 1. Parts

| Part | Qty | Key specs | FACTS ID |
|---|---|---|---|
| Arduino UNO Q | 1 | STM32U585 Cortex-M33 160 MHz (runs the sketch on Zephyr) + Qualcomm QRB2210 Linux. Header I/O is 3.3 V. 6 PWM pins. VIN 7 to 24 V | F-001, F-002, F-003 |
| Titan DC gearmotor 12 V 1000 RPM HP | 4 | No-load 240 mA, stall 5.9 A, stall torque 7.5 kg-cm, 37 mm diameter, 75 mm long, 6 mm D shaft | F-012 |
| JS5230 aluminum + silicone wheels | 4 | 52 mm diameter, 30 mm wide | F-013 |
| BTS7960 "double" module (IBT-2) | 2 used (4 owned) | One full H-bridge per board (one motor channel). 6 to 27 V. Inputs RPWM, LPWM, R_EN, L_EN. PWM up to 25 kHz. 74HC244 input buffer. About 66 g | F-014 |
| JS200XF long-range IR | 3 | 5 V, 15 mA max, digital output (1 = seen), 600 Hz, 1.68 ms response, 200 cm (120 cm with the rear pads bridged) | F-010 |
| MZ80 IR | 4 | 5 V, NPN output, range trimpot 10 to 80 cm on white targets (shorter on black), M18 thread, 20 g | F-011 |
| QTR-1RC reflectance | 4 | RC timing output read on a digital pin | F-017 |
| IMU on Qwiic | 1 | 3.3 V, I2C (Wire1). Gyro range 1000 dps or more | F-018 |
| 3S LiPo | 1 (+1) | 11.1 V nominal, 12.6 V full, 30C or more | |

Spares: the two unused IBT-2 boards are spares for match day.

---

## 2. Power architecture [P]

```
3S LiPo (12.6 V full, 11.1 V nominal)
   |
  XT60 --- 30 A fuse --- main switch (30 A or more)
   |
  BUS+ ----+--> IBT-2 LEFT  B+   (1000 uF + 100 nF across B+/B- at the terminals)
           +--> IBT-2 RIGHT B+   (1000 uF + 100 nF across B+/B- at the terminals)
           +--> 5 V buck, 3 A --> SENSOR 5V rail: 3x JS200XF, 4x MZ80, 4x QTR VIN
           +--> Schottky (SS34) --> UNO Q VIN ; 1000 uF from VIN to GND after the diode
           +--> 100 k --+-- 22 k --> GND ;  midpoint --> A0 (100 nF to GND at A0)

  BUS- = star ground point: IBT-2 B- (both), buck GND, UNO Q GND, sensor GND, IMU GND

  IBT-2 VCC (logic supply, both boards) <-- UNO Q 3V3 pin   (default; see section 5.4)
  IBT-2 GND (logic)                     <-- UNO Q GND
```

- **Why the diode and capacitor:** four motors reversing under load sag the pack. The diode stops the UNO Q's hold-up capacitor from draining into the motors; the capacitor rides through the dip. Bench test B7 proves it.
- **Battery sense math:** 12.6 V x 22 / 122 = 2.27 V at A0, inside the 3.3 V range. Source impedance about 18 k, under the 50 k guidance for the ADC. Calibrate against a multimeter in P2.
- **Wire gauge:** 14 AWG battery to drivers, 18 AWG drivers to motors, 22 to 26 AWG signals. Twist each motor pair. Solder a 100 nF ceramic across each motor's terminals.
- **Switch placement:** reachable from the top without touching the front.

---

## 3. Pin map [P] (P0 verifies against the official pinout; then the human replies "PINMAP OK")

| Signal | Pin | Direction | Electrical | Notes |
|---|---|---|---|---|
| L_FWD_PWM (left IBT-2 RPWM) | D3 | PWM out | 3.3 V | Must be PWM-capable |
| L_REV_PWM (left IBT-2 LPWM) | D5 | PWM out | 3.3 V | Same PWM frequency as D3 |
| R_FWD_PWM (right IBT-2 RPWM) | D6 | PWM out | 3.3 V | |
| R_REV_PWM (right IBT-2 LPWM) | D9 | PWM out | 3.3 V | |
| MOTOR_EN (R_EN + L_EN of both boards) | D10 | out | 10 k pull-down to GND | LOW = all motors off. Keeps motors dead during boot and reset (rule R1) |
| QTR_FL | D2 | in/out | direct | RC read |
| QTR_FR | D4 | in/out | direct | |
| QTR_RL | D7 | in/out | direct | |
| QTR_RR | D8 | in/out | direct | |
| OPP_FL15 (JS200XF left) | D11 | in | 10 k / 18 k divider | Active high |
| OPP_FC (JS200XF center) | D12 | in | 10 k / 18 k divider | Active high |
| OPP_FR15 (JS200XF right) | D13 | in | 10 k / 18 k divider | Active high |
| OPP_SL (MZ80 left 90) | A2 | in | 4.7 k pull-up to 3.3 V (or divider, see 5.2) | Active low |
| OPP_SR (MZ80 right 90) | A3 | in | same | Active low |
| OPP_RL (MZ80 rear-left 135) | A4 | in | same | Check whether A4 shares the SDA header pin |
| OPP_RR (MZ80 rear-right 135) | A5 | in | same | Check whether A5 shares the SCL header pin |
| VBAT_SENSE | A0 | ADC | 100 k / 22 k + 100 nF | ADC only |
| BUTTONS (START + MODE ladder) | A1 | ADC | 10 k pull-up to 3.3 V | ADC only |
| IMU | Qwiic (Wire1) | I2C | 3.3 V only | |
| D0, D1 | unused | | | Reserved (UART) |

If P0 finds the PWM set differs from D3, D5, D6, D9, D10, D11: keep the four motor PWM signals on real PWM pins (two per driver, matched frequency) and move other signals. Record the change in DECISIONS.md.

---

## 4. Opponent and edge sensor layout [P]

Bearing convention: 0 degrees = straight ahead, positive = clockwise (right), negative = left.

```
                        FRONT  (steel blade, matte black, full width)
            OPP_FL15 (-15)      OPP_FC (0)      OPP_FR15 (+15)
                 \                  |                  /
       [QTR_FL]  +------------------------------------+  [QTR_FR]
                 |                                    |
  OPP_SL (-90) <-|                                    |-> OPP_SR (+90)
                 |              ROBOT                 |
                 |         max 199 x 199 mm           |
                 |          IMU at the center         |
       [QTR_RL]  +------------------------------------+  [QTR_RR]
                /                                      \
      OPP_RL (-135)                                 OPP_RR (+135)
                               REAR
```

Mounting spec:
- **All 7 opponent sensors:** 3 to 5 cm above the ring, lenses parallel to the floor. They must see a low robot and must not see the ring surface. Verify with the P2 bench.
- **JS200XF:** center points straight ahead; left and right angled 15 degrees outward. Bridge the rear range pads (120 cm). Nothing white or shiny around the lenses.
- **MZ80:** set each trimpot with a matte black box at 40 cm: detected at 40 cm, not at 50 cm. Record the final range per sensor in TUNING_LOG.md.
- **QTR-1RC:** one per corner, facing down, 2 to 3 mm above the surface (check the Pololu recommendation in P0). Front pair just behind the blade edge. Rigid mounts: height changes shift the readings.
- **IMU:** near the geometric center, flat, screwed rigid (no foam), away from motor wires.

---

## 5. Wiring and pre-connect checks

Rule: **measure every 5 V sensor output with a multimeter before it touches a UNO Q pin.** One mistake can kill a pin you have no spare for.

### 5.1 JS200XF (3x) [P]
- Power from the 5 V sensor rail.
- OUT goes through 10 k (series) to the UNO Q pin, with 18 k from that pin to GND. High = 5.0 x 18 / 28 = 3.2 V.
- Pre-check: power the sensor, attach only the divider, and measure the midpoint with a black box in front (expect about 3.2 V) and without it (expect about 0 V).
- If OUT only pulls low or floats (open-collector output): replace the divider with a 4.7 k pull-up to 3.3 V and flip the polarity bit in config.h. Log it in DECISIONS.md.

### 5.2 MZ80 (4x) [P]
- Power from the 5 V sensor rail. Two wire-color variants exist (yellow/red/black or black/brown/blue); check yours.
- NPN output, active low (pulls to GND when it detects).
- Pre-check: power the sensor, connect nothing to OUT, measure OUT with no object. About 5 V means the module has an internal pull-up to 5 V: use the 10 k / 18 k divider. About 0 V or floating: add a 4.7 k pull-up to 3.3 V and connect directly.

### 5.3 QTR-1RC (4x) [P]
- VIN from the 5 V rail, GND, OUT directly to the UNO Q pin. The MCU charges the OUT line to 3.3 V and times the discharge.
- P0 confirms from Pololu documentation that OUT never rises above the MCU's drive level with VIN at 5 V. If it does, power the QTRs from 3.3 V.

### 5.4 IBT-2 drivers (2x) [P]
- RPWM and LPWM from the four PWM pins. R_EN and L_EN of both boards joined to MOTOR_EN (D10) with a 10 k pull-down. R_IS and L_IS unconnected.
- Pre-check: with MOTOR_EN disconnected, measure the EN line. If the board pulls EN high on its own, the pull-down must be stronger than that pull-up (try 4.7 k) so EN stays LOW while the MCU boots.
- Logic supply: IBT-2 VCC from the UNO Q 3V3 pin by default. A 74HC244 buffer powered at 5 V may not see 3.3 V as a reliable HIGH. Bench test B4 checks forward, reverse, and brake on both sides. If everything is solid with VCC at 5 V as well, either is fine; record the choice.
- Truth table (P0 verifies; EN high unless noted): RPWM = duty, LPWM = 0 gives forward. RPWM = 0, LPWM = duty gives reverse. Both 0 gives brake (both low sides on). EN low gives coast (outputs off).

### 5.5 Motors
- Front and rear motor of each side wired in parallel to that side's IBT-2 outputs.
- On the stand, check both wheels on a side turn the same direction. If one runs backward, swap its two leads at the motor.

### 5.6 Buttons on A1 [P]
```
3.3 V --- 10 k ---+--- A1 (100 nF to GND)
                  |
                  +--- START button --- GND                (pressed: about 0 V)
                  |
                  +--- MODE button --- 10 k --- GND        (pressed: about 1.65 V)
Nothing pressed: about 3.3 V. Both pressed: about 0 V (firmware treats "both held 1 s" as STOP).
```
Mount START where the operator can press and release it from the side or rear without leaning over the front.

---

## 6. Mechanical constraints that affect code and sensors

- **Footprint:** 200 x 200 mm including blade, sensors, wires, and anything that sticks out. Build to 199 mm and check with a square box.
- **Motor fit:** one motor (75 mm) plus one wheel (30 mm) is about 105 mm per side, so a left and right motor on the same axle line need about 210 mm. That exceeds 200 mm. Offset the left and right motors front-to-back by at least 40 mm (motor diameter 37 mm) so their bodies sit side by side. Measure your actual motor, shaft, and hub lengths before cutting.
- **Blade:** steel, full width, knife edge as low as the ring allows, matte black (rule 4.5).
- **Center of mass:** low and slightly forward. Use ballast to reach the weight target, mounted low.
- **Tires:** silicone collects dust and loses grip. Wipe before every round.

### Weight budget (estimates: weigh every part and replace the numbers)

| Item | Qty | Each (g) | Total (g) |
|---|---|---|---|
| Titan motor | 4 | ~180 | 720 |
| JS5230 wheel with hub | 4 | ~60 | 240 |
| 37 mm motor mounts | 4 | ~30 | 120 |
| IBT-2 board | 2 | 66 | 132 |
| UNO Q | 1 | ~25 | 25 |
| JS200XF | 3 | ~15 | 45 |
| MZ80 | 4 | 20 | 80 |
| QTR-1RC | 4 | ~2 | 8 |
| IMU | 1 | ~5 | 5 |
| 3S LiPo | 1 | 110 to 180 | 180 |
| Buck, fuse, switch, capacitors, wiring, connectors | | | 120 |
| **Subtotal** | | | **~1,675** |
| Chassis + blade + ballast | | | **~1,275** to reach 2,950 |

Target 2,950 g with a 20 g tolerance. That leaves 50 g of margin for a different scale at weigh-in.

---

## 7. Arena geometry (from the rulebook)

- Wooden ring, 1.5 m diameter, black surface, 3 cm white border.
- Two brown start lines, 2 cm thick, up to 20 cm long, 10 cm from the center. Robots start behind their line without touching it, so the fronts start about 20 cm apart.
- Safety zone 25 to 30 cm around the ring. Anything our sensors see beyond it is our problem.

---

## 8. Physics numbers behind the governor

| Quantity | Value | Basis |
|---|---|---|
| Top speed, no load | 2.7 m/s at 12 V (2.9 m/s at 12.6 V) | pi x 0.052 m x 1000 / 60 |
| Realistic top speed with 3 kg | about 2.2 to 2.5 m/s | Load and battery sag |
| Stopping distance d = v^2 / (2 mu g), mu 1.0 to 1.3 | 1.0 m/s: 4 to 5 cm; 1.5 m/s: 9 to 11 cm; 2.0 m/s: 16 to 20 cm; 2.5 m/s: 25 to 32 cm | Tire friction limits braking |
| Detection latency | 2 to 3 ms (QTR read up to 1.5 ms + 1 ms tick) | Under 1 cm at 2.5 m/s |
| Time to cross the white band | 12 ms at 2.5 m/s | 3 cm / 2.5 m/s |
| Motor push force at stall | about 11.5 kgf (4 x 7.5 kg-cm / 2.6 cm) | Torque / wheel radius |
| Traction limit | about 3 to 4 kgf (mu x 3 kg) | Wheels spin before motors stall |
| Charger crossing the 20 cm start gap | about 0.15 to 0.25 s | Including acceleration |

What this means for code:
1. **The robot cannot stop at the edge from full speed.** Set SEARCH_DUTY_MAX from the P3 stopping table so the worst stop stays under 70 % of R_room.
2. **R_room** = distance from the moment a front QTR sees white to the moment the robot would lose (tips over or touches the floor). Measure it in P3 by pushing the robot slowly over the edge by hand.
3. **Traction limits the push, so full duty from standstill only spins the tires.** Use the slew limit. Wedge geometry and weight win pushes, not extra duty.
4. **Approach at ATTACK_APPROACH_DUTY; switch to full duty only after contact.** A dodged robot at full speed flies out of the ring.

---

## 9. Hardware verification checklist (feeds P2)

- [ ] Every JS200XF output measured through its divider: about 3.2 V seen, about 0 V not seen
- [ ] Every MZ80 output type determined (internal pull-up or not) and wired accordingly
- [ ] QTR OUT maximum voltage confirmed safe
- [ ] MOTOR_EN stays LOW with the MCU unpowered and during boot (measure while powering up)
- [ ] IBT-2 logic supply choice tested (B4)
- [ ] Both wheels on each side spin the same direction
- [ ] Battery sense within 0.05 V of the multimeter
- [ ] All grounds meet at one star point
- [ ] Nothing white on the front; blade painted
- [ ] Weight and footprint recorded

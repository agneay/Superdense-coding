# Bill of Materials (BOM)

Approximate component list for the physical demo rig. Prices are rough
USD estimates for budgeting a capstone build and will vary by supplier.

| # | Component | Qty | Approx. unit price | Notes |
|---|-----------|-----|---------------------|-------|
| 1 | Raspberry Pi 4B (2GB+) or Pi 5 | 1 | $35-60 | Runs Python + Qiskit directly |
| 2 | microSD card, 16GB+ (A1/A2 rated) | 1 | $8 | Raspberry Pi OS Lite is sufficient |
| 3 | 16x2 character LCD with PCF8574 I2C backpack | 2 | $6 | One per side: "Alice" and "Bob" |
| 4 | Momentary tactile pushbutton | 2 | $0.20 | CYCLE and SEND |
| 5 | 5mm LED, assorted colors | 7 | $0.10 | 1x entangled, 1x sent, 1x match, 4x gate indicator |
| 6 | 330 ohm resistor (1/4W) | 7 | $0.05 | One per LED |
| 7 | Breadboard (half+ size) or perfboard | 1 | $5 | For prototyping before a permanent build |
| 8 | Jumper wire kit (M-M, M-F) | 1 set | $5 | |
| 9 | USB-C power bank, 10,000 mAh, 5V/3A output | 1 | $18-25 | Must support at least 3A output for Pi 4/5 |
| 10 | USB-A-to-USB-C or USB-C-to-USB-C cable | 1 | $4 | Power bank -> Pi |
| 11 | Enclosure / project box (optional) | 1 | $10-15 | For a polished, GitHub-photo-ready final build |

**Estimated total: ~$95-140**, most of which is the Pi itself and the
power bank -- both reusable beyond this project.

## Substitutions

* Any HD44780-compatible 16x2 LCD with an I2C backpack works; the exact
  address only matters for `hardware/config.py`.
* A Raspberry Pi Zero 2 W is a lower-cost, lower-power alternative to a
  Pi 4/5 (smaller power bank needed) but is slower to run Qiskit's
  transpiler -- expect ~1-2s extra latency per "SEND" press.
* LEDs and resistors can be swapped for a single 7-segment or small OLED
  status readout if preferred; `hardware/config.py` and
  `hardware/pi_superdense_demo.py` would need matching updates.

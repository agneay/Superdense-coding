# GPIO Pinout Reference

All pin numbers are **BCM numbering** (matches `hardware/config.py` and
gpiozero's default). See `hardware/wiring/wiring_diagram.svg` for the
matching schematic.

## Pushbuttons

| Signal          | BCM GPIO | Physical pin | Wiring |
|-----------------|----------|---------------|--------|
| `BTN_CYCLE`     | GPIO17   | Pin 11 | Button between GPIO17 and GND. Internal pull-up enabled in software (gpiozero default) -- no external resistor needed. |
| `BTN_SEND`      | GPIO27   | Pin 13 | Button between GPIO27 and GND. Internal pull-up enabled in software. |

## LEDs (status / gate indicators)

Each LED is wired GPIO -> 330 ohm resistor -> LED anode -> LED cathode -> GND.

| Signal            | BCM GPIO | Physical pin | Meaning |
|-------------------|----------|---------------|---------|
| `LED_ENTANGLED`   | GPIO5    | Pin 29 | On once the Bell pair is prepared |
| `LED_SENT`        | GPIO6    | Pin 31 | Blinks while the qubit is "in transit" |
| `LED_MATCH`       | GPIO13   | Pin 33 | On if Bob's decoded bits match Alice's input |
| `LED_GATE_I`      | GPIO19   | Pin 35 | On when Alice applied Identity (message = 00) |
| `LED_GATE_X`      | GPIO26   | Pin 37 | On when Alice applied X (message = 01) |
| `LED_GATE_Z`      | GPIO20   | Pin 38 | On when Alice applied Z (message = 10) |
| `LED_GATE_ZX`     | GPIO21   | Pin 40 | On when Alice applied Z then X (message = 11) |

## LCDs (I2C, shared bus)

Both LCD1602 modules share the Pi's single I2C bus but use **different**
I2C addresses (set via the solder-jumper pads on the PCF8574 backpack),
so both can be addressed independently over the same two wires.

| Signal | BCM GPIO | Physical pin | Notes |
|--------|----------|---------------|-------|
| `SDA`  | GPIO2    | Pin 3  | Shared by both LCDs |
| `SCL`  | GPIO3    | Pin 5  | Shared by both LCDs |
| 5V     | --       | Pin 2 or 4 | Powers both LCD backpacks |
| GND    | --       | Pin 6, 9, 14, 20, 25, 30, 34, or 39 | Common ground for LCDs, LEDs, buttons |

| Device            | I2C address |
|-------------------|-------------|
| LCD 1 ("Alice")   | `0x27` (default PCF8574 address) |
| LCD 2 ("Bob")     | `0x26` (A0 jumper bridged) |

Run `i2cdetect -y 1` on the Pi after wiring to confirm both addresses
show up on the bus before running the demo.

## Power

| Rail | Source |
|------|--------|
| Raspberry Pi 5V/GND | USB-C power bank (see `bom.md`) |
| LCDs, LEDs, buttons | Powered from the Pi's own 5V/3.3V and GND rails -- no separate battery needed |

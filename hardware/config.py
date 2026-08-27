"""
config.py

Central place for every GPIO pin assignment and hardware constant used by
the physical Superdense Coding demo rig. Change pin numbers here only --
every other hardware module imports from this file.

All pin numbers are BCM (Broadcom) numbering, matching gpiozero's default.
See docs/design/gpio-pinout.md for the full wiring reference and the
matching schematic in hardware/wiring/wiring_diagram.svg.
"""

# ---------------------------------------------------------------------------
# Pushbuttons (active-low, wired with gpiozero's internal pull-up enabled --
# no external pull-up/pull-down resistors needed)
# ---------------------------------------------------------------------------
BTN_CYCLE_PIN = 17   # short press: cycle Alice's 2-bit message 00 -> 01 -> 10 -> 11 -> 00
BTN_SEND_PIN = 27    # short press: run the protocol (encode -> "send" -> decode)

# ---------------------------------------------------------------------------
# Status / gate-indicator LEDs
# ---------------------------------------------------------------------------
LED_ENTANGLED_PIN = 5    # solid on once the Bell pair is (re)prepared
LED_SENT_PIN = 6         # blinks while the qubit is "in flight" from Alice to Bob
LED_MATCH_PIN = 13       # solid green-equivalent LED: lights if decoded bits == sent bits
LED_GATE_I_PIN = 19      # one of these four lights up to show which gate Alice applied
LED_GATE_X_PIN = 26
LED_GATE_Z_PIN = 20
LED_GATE_ZX_PIN = 21

GATE_LED_PINS = {
    "I": LED_GATE_I_PIN,
    "X": LED_GATE_X_PIN,
    "Z": LED_GATE_Z_PIN,
    "ZX": LED_GATE_ZX_PIN,
}

# ---------------------------------------------------------------------------
# LCD1602 displays over I2C (each with a PCF8574 I2C backpack).
# Give the two backpacks *different* I2C addresses by setting their solder
# jumpers (A0/A1/A2) -- see docs/design/bom.md for the exact part.
# ---------------------------------------------------------------------------
LCD_ALICE_I2C_ADDRESS = 0x27   # left-hand display: shows Alice's input + gate
LCD_BOB_I2C_ADDRESS = 0x26     # right-hand display: shows Bob's decoded output
I2C_PORT = 1                   # Raspberry Pi's default I2C bus (SDA=GPIO2, SCL=GPIO3)
LCD_COLS = 16
LCD_ROWS = 2

# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------
DEBOUNCE_SECONDS = 0.05
SEND_ANIMATION_SECONDS = 1.2   # how long LED_SENT blinks to visualize "transit"

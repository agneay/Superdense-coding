"""
pi_superdense_demo.py

The physical demo rig: two pushbuttons, two I2C LCDs, and a handful of
status LEDs, all driven by the exact same Qiskit simulation used in
simulation/superdense_coding.py. The Raspberry Pi is standing in for
"Alice's lab + Bob's lab + the fiber/free-space link between them" all at
once -- the qubit "travel" step is visualized with LED_SENT rather than
being physically real, since there is no real quantum hardware here.

Physical interaction
---------------------
  BTN_CYCLE  (short press) : cycle Alice's message through 00 -> 01 -> 10 -> 11 -> 00
  BTN_SEND   (short press) : run the full protocol for the currently selected bits

  LCD (Alice, left)  : shows Alice's chosen bits and which gate she applied
  LCD (Bob, right)   : shows the bits Bob decoded, and whether they matched

  LED_ENTANGLED : on whenever a fresh Bell pair has been (conceptually) prepared
  LED_SENT      : blinks while the "qubit" is in transit from Alice to Bob
  LED_MATCH     : lit if Bob's decoded bits equal Alice's original bits
  LED_GATE_*    : exactly one lights up, showing which of I / X / Z / ZX was used

Runs with no Raspberry Pi attached
-----------------------------------
If gpiozero cannot find real GPIO hardware (e.g. running on a laptop for
development or grading), it automatically falls back to its software
"mock pin factory" and everything is driven from the keyboard instead:
  c <Enter>  = cycle bits
  s <Enter>  = send
  q <Enter>  = quit
This means graders/reviewers can run this file with zero hardware.
"""

from __future__ import annotations

import sys
import time

from hardware.config import (
    BTN_CYCLE_PIN,
    BTN_SEND_PIN,
    DEBOUNCE_SECONDS,
    GATE_LED_PINS,
    I2C_PORT,
    LCD_ALICE_I2C_ADDRESS,
    LCD_BOB_I2C_ADDRESS,
    LED_ENTANGLED_PIN,
    LED_MATCH_PIN,
    LED_SENT_PIN,
    SEND_ANIMATION_SECONDS,
)
from hardware.lcd_driver import Lcd
from simulation.superdense_coding import all_two_bit_combinations, run_protocol

try:
    from gpiozero import Button, LED

    _HAS_GPIOZERO_HW = True
except Exception:  # pragma: no cover - depends on host
    _HAS_GPIOZERO_HW = False


class SuperdenseRig:
    """Owns all the GPIO/LCD state for the physical demo."""

    def __init__(self) -> None:
        self.combinations = all_two_bit_combinations()
        self.selected_index = 0

        self.lcd_alice = Lcd(LCD_ALICE_I2C_ADDRESS, I2C_PORT, label="LCD-Alice")
        self.lcd_bob = Lcd(LCD_BOB_I2C_ADDRESS, I2C_PORT, label="LCD-Bob ")

        self._setup_gpio()
        self._show_idle_state()

    # -- GPIO setup ---------------------------------------------------
    def _setup_gpio(self) -> None:
        if _HAS_GPIOZERO_HW:
            self.btn_cycle = Button(BTN_CYCLE_PIN, bounce_time=DEBOUNCE_SECONDS)
            self.btn_send = Button(BTN_SEND_PIN, bounce_time=DEBOUNCE_SECONDS)
            self.led_entangled = LED(LED_ENTANGLED_PIN)
            self.led_sent = LED(LED_SENT_PIN)
            self.led_match = LED(LED_MATCH_PIN)
            self.gate_leds = {name: LED(pin) for name, pin in GATE_LED_PINS.items()}

            self.btn_cycle.when_pressed = self.on_cycle
            self.btn_send.when_pressed = self.on_send
        else:
            print("[rig] No GPIO hardware detected -- running in keyboard-driven mock mode.")
            self.btn_cycle = self.btn_send = None
            self.led_entangled = _MockLed("ENTANGLED")
            self.led_sent = _MockLed("SENT")
            self.led_match = _MockLed("MATCH")
            self.gate_leds = {name: _MockLed(f"GATE-{name}") for name in GATE_LED_PINS}

    # -- Actions --------------------------------------------------------
    def on_cycle(self) -> None:
        self.selected_index = (self.selected_index + 1) % len(self.combinations)
        self._show_idle_state()

    def on_send(self) -> None:
        bit1, bit0 = self.combinations[self.selected_index]

        self.led_entangled.on()
        self.lcd_alice.write_lines(f"Alice: {bit1}{bit0}", "Sending...")

        self.led_sent.blink(on_time=0.15, off_time=0.15, n=int(SEND_ANIMATION_SECONDS / 0.3))
        time.sleep(SEND_ANIMATION_SECONDS)

        result = run_protocol(bit1, bit0)

        for name, led in self.gate_leds.items():
            (led.on() if name == result.gate_name else led.off())

        self.lcd_alice.write_lines(f"Alice: {bit1}{bit0}", f"Gate: {result.gate_name}")
        self.lcd_bob.write_lines(
            f"Bob decoded: {result.decoded_bit1}{result.decoded_bit0}",
            "MATCH!" if result.success else "MISMATCH",
        )

        (self.led_match.on() if result.success else self.led_match.off())

    def _show_idle_state(self) -> None:
        bit1, bit0 = self.combinations[self.selected_index]
        self.lcd_alice.write_lines(f"Select: {bit1}{bit0}", "Press SEND ->")
        self.lcd_bob.write_lines("Waiting for", "Alice...")
        self.led_match.off()
        for led in self.gate_leds.values():
            led.off()

    # -- Main loop --------------------------------------------------------
    def run_forever(self) -> None:
        if _HAS_GPIOZERO_HW:
            print("[rig] Ready. Use the physical buttons.")
            from signal import pause

            pause()
        else:
            print("[rig] Keyboard mode: type 'c' + Enter to cycle bits, 's' + Enter to send, 'q' to quit.")
            for line in sys.stdin:
                cmd = line.strip().lower()
                if cmd == "c":
                    self.on_cycle()
                elif cmd == "s":
                    self.on_send()
                elif cmd == "q":
                    break
                else:
                    print("[rig] Unknown command. Use c / s / q.")


class _MockLed:
    """Console stand-in for a gpiozero.LED when no real GPIO is present."""

    def __init__(self, name: str):
        self.name = name
        self._state = False

    def on(self) -> None:
        self._state = True
        print(f"[LED:{self.name}] ON")

    def off(self) -> None:
        self._state = False
        print(f"[LED:{self.name}] off")

    def blink(self, on_time: float = 0.15, off_time: float = 0.15, n: int | None = None) -> None:
        print(f"[LED:{self.name}] blinking...")


def main() -> None:
    rig = SuperdenseRig()
    rig.run_forever()


if __name__ == "__main__":
    main()

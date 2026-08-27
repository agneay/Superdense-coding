"""
lcd_driver.py

Thin, swappable wrapper around an I2C 16x2 character LCD (HD44780 controller
behind a PCF8574 I2C backpack), used for both the "Alice" and "Bob" displays.

Real hardware:
    Uses the RPLCD library (pip install RPLCD) talking over smbus2. This is
    the code path that runs on an actual Raspberry Pi.

No hardware attached (development / CI):
    Falls back to a console-printed "virtual LCD" so the exact same
    hardware.pi_superdense_demo module can be run and demoed on a laptop
    with no Raspberry Pi or wiring at all.
"""

from __future__ import annotations

from hardware.config import LCD_COLS, LCD_ROWS

try:
    from RPLCD.i2c import CharLCD

    _HAS_RPLCD = True
except (ImportError, NotImplementedError):
    # NotImplementedError is raised by smbus2 on non-Linux / non-Pi hosts.
    _HAS_RPLCD = False


class Lcd:
    """A 16x2 character display, real or simulated."""

    def __init__(self, i2c_address: int, i2c_port: int, label: str = "LCD"):
        self.label = label
        self._real: "CharLCD | None" = None

        if _HAS_RPLCD:
            try:
                self._real = CharLCD(
                    i2c_expander="PCF8574",
                    address=i2c_address,
                    port=i2c_port,
                    cols=LCD_COLS,
                    rows=LCD_ROWS,
                    auto_linebreaks=False,
                )
            except Exception as exc:  # pragma: no cover - only hit on real hw failures
                print(f"[{label}] Could not open real LCD ({exc}); using console fallback.")
                self._real = None

        self._lines = [" " * LCD_COLS for _ in range(LCD_ROWS)]

    def clear(self) -> None:
        if self._real is not None:
            self._real.clear()
        self._lines = [" " * LCD_COLS for _ in range(LCD_ROWS)]
        self._render_console()

    def write_lines(self, line1: str, line2: str = "") -> None:
        """Write up to two lines of text (each truncated/padded to LCD_COLS)."""
        self._lines = [line1[:LCD_COLS].ljust(LCD_COLS), line2[:LCD_COLS].ljust(LCD_COLS)]

        if self._real is not None:
            self._real.clear()
            self._real.cursor_pos = (0, 0)
            self._real.write_string(self._lines[0])
            self._real.cursor_pos = (1, 0)
            self._real.write_string(self._lines[1])

        self._render_console()

    def _render_console(self) -> None:
        border = "+" + "-" * LCD_COLS + "+"
        print(f"[{self.label}] {border}")
        for line in self._lines:
            print(f"[{self.label}] |{line}|")
        print(f"[{self.label}] {border}")

# Contributing

This started as a capstone project, but improvements are welcome.

## Getting set up

```bash
git clone <this-repo-url>
cd superdense-coding-project
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest
```

## Project layout

* `simulation/` -- the Qiskit protocol logic and its tests. Start here;
  it has no hardware dependencies and is the easiest place to verify a
  change.
* `hardware/` -- the Raspberry Pi rig. Runs in a keyboard/console mock
  mode with no GPIO hardware attached, so you can develop and test
  hardware logic changes without a physical Pi.
* `webapp/` -- the Flask web app. Same protocol logic as the other two,
  reached through `simulation/superdense_coding.py`; no new protocol
  code should be added here, only routes and presentation.
* `docs/` -- concept write-up and design docs (architecture, wiring,
  BOM). Update these alongside any behavioral change.

## Before opening a PR

1. `pytest` passes locally, including `webapp/tests/` (needs
   `pip install -r webapp/requirements-web.txt` first).
2. If you changed the protocol logic, regenerate the circuit diagrams:
   `python -m simulation.demo_cli --save-images`
3. If you changed pin assignments, update both
   `hardware/config.py` **and** `docs/design/gpio-pinout.md` **and**
   `hardware/wiring/wiring_diagram.svg` together -- they must stay in
   sync.

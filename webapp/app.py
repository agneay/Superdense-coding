"""
app.py

Flask web application for the superdense coding protocol.

This exposes the same functionality as the project's two terminal tools,
as a browser UI, with no CLI or hardware required:

  * simulation/demo_cli.py   -- pick a message and run it, or run all
                                 four combinations at once; the circuit
                                 diagram is rendered on demand instead
                                 of pre-saved to docs/images/.
  * hardware/pi_superdense_demo.py's keyboard-driven mock -- a CYCLE
                                 button to step through 00/01/10/11 and
                                 a SEND button, with the same LED/LCD
                                 states re-created in the browser (see
                                 webapp/static/app.js and style.css).

No new protocol logic lives here -- every route calls straight into
simulation/superdense_coding.py, the same module the CLI and the
Raspberry Pi rig use, so all three stay in sync by construction.

Run with:
    pip install -r requirements.txt -r webapp/requirements-web.txt
    python -m webapp.app
then open http://127.0.0.1:5000/
"""

from __future__ import annotations

import io

from flask import Flask, jsonify, render_template, request, send_file

from hardware.config import SEND_ANIMATION_SECONDS
from simulation.superdense_coding import (
    GATE_NAMES,
    ProtocolResult,
    all_two_bit_combinations,
    build_superdense_circuit,
    run_protocol,
)
from simulation.visualization import circuit_to_png_bytes

app = Flask(__name__)


def _parse_bits(bits: str) -> tuple[int, int]:
    if len(bits) != 2 or any(c not in "01" for c in bits):
        raise ValueError("bits must be a two-character string of 0s and 1s, e.g. '10'")
    return int(bits[0]), int(bits[1])


def _result_to_json(r: ProtocolResult) -> dict:
    return {
        "bit1": r.bit1,
        "bit0": r.bit0,
        "message": f"{r.bit1}{r.bit0}",
        "gate_name": r.gate_name,
        "bell_state_name": r.bell_state_name,
        "decoded_bit1": r.decoded_bit1,
        "decoded_bit0": r.decoded_bit0,
        "decoded_message": f"{r.decoded_bit1}{r.decoded_bit0}",
        "success": r.success,
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/config")
def api_config():
    """Static info the frontend needs so it never hardcodes protocol constants."""
    return jsonify(
        {
            "combinations": [f"{b1}{b0}" for b1, b0 in all_two_bit_combinations()],
            "gate_names": {f"{b1}{b0}": name for (b1, b0), name in GATE_NAMES.items()},
            "send_animation_seconds": SEND_ANIMATION_SECONDS,
        }
    )


@app.get("/api/run")
def api_run():
    """Run the protocol for one message -- the --bits <xy> path of demo_cli.py."""
    try:
        bit1, bit0 = _parse_bits(request.args.get("bits", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    result = run_protocol(bit1, bit0)
    return jsonify(_result_to_json(result))


@app.get("/api/run_all")
def api_run_all():
    """Run all four combinations -- the no-argument path of demo_cli.py."""
    results = [run_protocol(bit1, bit0) for bit1, bit0 in all_two_bit_combinations()]
    return jsonify([_result_to_json(r) for r in results])


@app.get("/api/circuit.png")
def api_circuit_png():
    """Render the circuit diagram for one message as a PNG, on demand.

    Equivalent to the images demo_cli.py --save-images writes under
    docs/images/, but generated per-request instead of to disk.
    """
    try:
        bit1, bit0 = _parse_bits(request.args.get("bits", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    circuit, _ = build_superdense_circuit(bit1, bit0)
    png_bytes = circuit_to_png_bytes(circuit)
    return send_file(io.BytesIO(png_bytes), mimetype="image/png")


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()

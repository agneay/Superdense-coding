"""
visualization.py

Shared circuit-diagram rendering, used by both simulation/demo_cli.py
(saves PNGs to docs/images/) and webapp/app.py (serves PNGs over HTTP
on demand). Keeping the drawing code in one place means the two never
drift into rendering the circuit differently.
"""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")  # non-interactive backend -- safe with no display (CI, web servers)

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit


def circuit_to_png_bytes(circuit: QuantumCircuit) -> bytes:
    """Render a circuit with Qiskit's matplotlib drawer and return PNG bytes."""
    fig = circuit.draw(output="mpl")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.read()

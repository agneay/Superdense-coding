"""
superdense_coding.py

Core implementation of the Superdense Coding quantum protocol using Qiskit.

Superdense coding lets Alice send Bob two classical bits of information by
transmitting a single qubit, provided Alice and Bob pre-share one qubit each
of an entangled Bell pair.

Protocol overview
------------------
1. (Setup, done once, before Alice knows which bits she wants to send)
   A source creates an entangled Bell pair |Phi+> = (|00> + |11>) / sqrt(2)
   and gives qubit 0 to Alice and qubit 1 to Bob.

2. (Encode) Alice wants to send two classical bits b1 b0. She applies a gate
   to *only her own qubit* (qubit 0) chosen from the table below:

       b1 b0 | Gate applied to Alice's qubit | Resulting Bell state
       ------+--------------------------------+----------------------
        0  0 | I  (identity)                  | |Phi+> = (|00>+|11>)/sqrt(2)
        0  1 | X  (bit flip)                   | |Psi+> = (|01>+|10>)/sqrt(2)
        1  0 | Z  (phase flip)                 | |Phi-> = (|00>-|11>)/sqrt(2)
        1  1 | Z then X                        | |Psi-> = (|01>-|10>)/sqrt(2)  (up to a global phase)

3. (Send) Alice physically sends her single, now-encoded qubit to Bob.
   This is the only quantum communication in the whole protocol -- one
   qubit travels, but two classical bits of information are recovered.

4. (Decode) Bob now holds both qubits. He performs a Bell-basis
   measurement: CNOT(control=Alice's qubit, target=Bob's qubit) followed
   by a Hadamard on Alice's qubit, then measures both qubits in the
   computational basis. The two measured bits exactly reproduce Alice's
   original b1 b0.

This module is deliberately split into small, independently testable
functions so the same building blocks can be reused by:
  * simulation/demo_cli.py      (software demo / circuit diagrams)
  * simulation/tests/*          (automated correctness tests)
  * hardware/pi_superdense_demo.py  (the physical Raspberry Pi rig)
"""

from __future__ import annotations

from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# ---------------------------------------------------------------------------
# Encoding table: classical bit pair -> which Pauli gate(s) Alice applies.
# ---------------------------------------------------------------------------
GATE_NAMES = {
    (0, 0): "I",
    (0, 1): "X",
    (1, 0): "Z",
    (1, 1): "ZX",
}

BELL_STATE_NAMES = {
    (0, 0): "|Phi+>",
    (0, 1): "|Psi+>",
    (1, 0): "|Phi->",
    (1, 1): "|Psi->",
}


@dataclass
class ProtocolResult:
    """Everything a caller (CLI, tests, hardware) needs from one run."""

    bit1: int
    bit0: int
    gate_name: str
    bell_state_name: str
    circuit: QuantumCircuit
    decoded_bit1: int
    decoded_bit0: int

    @property
    def success(self) -> bool:
        return (self.bit1, self.bit0) == (self.decoded_bit1, self.decoded_bit0)


def create_bell_pair(qc: QuantumCircuit) -> None:
    """Prepare the shared entangled resource |Phi+> on qubits 0 and 1."""
    qc.h(0)
    qc.cx(0, 1)


def encode(qc: QuantumCircuit, bit1: int, bit0: int) -> str:
    """Alice encodes two classical bits onto *her* qubit (qubit 0) only.

    Returns the human-readable name of the gate combination applied.
    """
    if bit1 not in (0, 1) or bit0 not in (0, 1):
        raise ValueError("bit1 and bit0 must each be 0 or 1")

    if bit1 == 1:
        qc.z(0)
    if bit0 == 1:
        qc.x(0)

    return GATE_NAMES[(bit1, bit0)]


def decode(qc: QuantumCircuit) -> None:
    """Bob's Bell-basis measurement: undoes the Bell-pair circuit, then measures."""
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])


def build_superdense_circuit(bit1: int, bit0: int) -> tuple[QuantumCircuit, str]:
    """Build the full end-to-end circuit for sending bits (bit1, bit0)."""
    qc = QuantumCircuit(2, 2, name=f"superdense_{bit1}{bit0}")
    create_bell_pair(qc)
    qc.barrier(label="encode")
    gate_name = encode(qc, bit1, bit0)
    qc.barrier(label="send+decode")
    decode(qc)
    return qc, gate_name


def run_protocol(bit1: int, bit0: int, shots: int = 1024, backend=None) -> ProtocolResult:
    """Run the full protocol on the Aer simulator and decode the result.

    Because the protocol is deterministic (no measurement randomness once
    encoded), a single shot is enough to recover the bits, but we run more
    shots by default so the result can also be used to sanity-check that
    the simulator always agrees with itself (100% one outcome).
    """
    circuit, gate_name = build_superdense_circuit(bit1, bit0)
    backend = backend or AerSimulator()
    job = backend.run(circuit, shots=shots)
    counts = job.result().get_counts()

    # Deterministic protocol -> exactly one outcome should appear.
    outcome = max(counts, key=counts.get)

    # Qiskit's classical bitstring is ordered c_{n-1} ... c_1 c_0 (little-endian:
    # rightmost character is classical bit 0). clbit0 <- qubit0 (Alice's qubit,
    # which after the decode circuit carries the X/"bit0" information), clbit1
    # <- qubit1 (Bob's qubit, which carries the Z/"bit1" information).
    decoded_bit1 = int(outcome[-1])
    decoded_bit0 = int(outcome[-2])

    return ProtocolResult(
        bit1=bit1,
        bit0=bit0,
        gate_name=gate_name,
        bell_state_name=BELL_STATE_NAMES[(bit1, bit0)],
        circuit=circuit,
        decoded_bit1=decoded_bit1,
        decoded_bit0=decoded_bit0,
    )


def all_two_bit_combinations() -> list[tuple[int, int]]:
    return [(0, 0), (0, 1), (1, 0), (1, 1)]

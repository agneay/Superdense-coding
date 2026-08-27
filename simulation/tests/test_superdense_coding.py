"""
Unit tests for the superdense coding simulation.

Run with:
    pytest
"""

import pytest

from simulation.superdense_coding import (
    GATE_NAMES,
    all_two_bit_combinations,
    build_superdense_circuit,
    run_protocol,
)


@pytest.mark.parametrize("bit1,bit0", all_two_bit_combinations())
def test_all_two_bit_combinations_round_trip(bit1, bit0):
    """Every 2-bit message Alice can send must be decoded correctly by Bob."""
    result = run_protocol(bit1, bit0, shots=64)
    assert (result.decoded_bit1, result.decoded_bit0) == (bit1, bit0)
    assert result.success


@pytest.mark.parametrize("bit1,bit0", all_two_bit_combinations())
def test_correct_gate_is_applied(bit1, bit0):
    result = run_protocol(bit1, bit0, shots=8)
    assert result.gate_name == GATE_NAMES[(bit1, bit0)]


def test_circuit_uses_exactly_two_qubits_and_two_clbits():
    circuit, _ = build_superdense_circuit(1, 0)
    assert circuit.num_qubits == 2
    assert circuit.num_clbits == 2


def test_circuit_is_deterministic():
    """Superdense coding has no measurement randomness -- one outcome, always."""
    result = run_protocol(1, 1, shots=512)
    circuit, _ = build_superdense_circuit(1, 1)
    from qiskit_aer import AerSimulator

    counts = AerSimulator().run(circuit, shots=512).result().get_counts()
    assert len(counts) == 1  # exactly one distinct outcome across all shots


def test_invalid_bits_raise():
    with pytest.raises(ValueError):
        run_protocol(2, 0)
    with pytest.raises(ValueError):
        run_protocol(0, -1)

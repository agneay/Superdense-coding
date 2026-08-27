# Superdense Coding: Concept & Theory

Superdense coding is one of the two "textbook" quantum communication
protocols (the other being quantum teleportation, its logical mirror
image). It shows that if two parties, conventionally named **Alice** and
**Bob**, share one qubit each of an entangled pair *before* they need to
communicate, Alice can later send Bob **two classical bits of
information by transmitting only one qubit**.

This document explains the physics and math behind the protocol this
project simulates and builds hardware around.

## 1. Why this is surprising

The Holevo bound says a single qubit, sent with no other resources,
can carry at most one classical bit of information reliably. Superdense
coding does not violate this -- it uses **pre-shared entanglement as a
resource** in addition to the one qubit sent later. Entanglement can't
transmit information by itself (no faster-than-light signalling), but it
can be "spent" alongside a later classical or quantum transmission to
double its capacity. This project's whole point is to make that
resource trade-off tangible: something you can watch happen on LEDs and
LCDs rather than only read about.

## 2. The four Bell states

The two-qubit Bell states form a basis for the space of a pair of
qubits:

| Name    | State                              |
|---------|-------------------------------------|
| \|Phi+> | (\|00> + \|11>) / sqrt(2)          |
| \|Phi-> | (\|00> - \|11>) / sqrt(2)          |
| \|Psi+> | (\|01> + \|10>) / sqrt(2)          |
| \|Psi-> | (\|01> - \|10>) / sqrt(2)          |

Crucially, these four states are **mutually orthogonal**, so a joint
("Bell-basis") measurement on both qubits can tell them apart perfectly.
That is the second key trick behind the protocol: information can be
hidden in *which* Bell state a shared pair is in, and that information
survives being "carried" by only one of the two qubits.

## 3. The protocol, step by step

**Setup (once, before Alice knows what she wants to send):**
A source prepares an entangled pair in the state `|Phi+>` and gives
qubit 0 to Alice and qubit 1 to Bob. They can be physically far apart
from this point on.

**Step 1 -- Encode.** Alice wants to send two classical bits, `b1 b0`.
She applies one, and only one, single-qubit gate to *her own* qubit
(qubit 0), never touching Bob's:

| b1 | b0 | Gate Alice applies | Resulting global state |
|----|----|---------------------|--------------------------|
| 0  | 0  | I (do nothing)      | `\|Phi+>` |
| 0  | 1  | X (bit flip)        | `\|Psi+>` |
| 1  | 0  | Z (phase flip)      | `\|Phi->` |
| 1  | 1  | Z then X            | `\|Psi->` (up to a global phase) |

Notice that Alice's single-qubit operation deterministically steers the
*joint, two-qubit* state into one of the four orthogonal Bell states --
even though she never touches Bob's qubit and the two qubits may be
light-years apart.

**Step 2 -- Send.** Alice physically sends her (now encoded) qubit to
Bob, over any quantum channel (optical fiber, free space, etc.). This is
the *only* qubit that physically travels between them.

**Step 3 -- Decode.** Bob now holds both qubits and performs a
Bell-basis measurement:

1. `CNOT` with Alice's qubit as control, Bob's qubit as target.
2. `Hadamard` on Alice's qubit.
3. Measure both qubits in the computational (Z) basis.

This circuit is exactly the inverse of the Bell-pair preparation circuit
(`H` then `CNOT`), so it maps each of the four Bell states back to a
distinct, deterministic two-bit computational-basis outcome -- which
turns out to exactly equal Alice's original `b1 b0`.

## 4. Why the bits come back correctly

Bell-basis measurement is, by construction, a *perfect* discriminator
between the four orthogonal Bell states -- there is no measurement
uncertainty involved, unlike naive single-qubit measurements. Because
Alice's four possible gate choices map to four *distinguishable* Bell
states, and Bob's circuit maps each Bell state to a unique, deterministic
classical outcome, the whole protocol has **zero measurement
randomness**: the same input bits always produce the same output bits,
100% of the time, verified over hundreds of simulated shots in
`simulation/tests/test_superdense_coding.py`.

## 5. What this project simulates vs. what real hardware would need

This is a **simulation and physical teaching demo**, not a real quantum
communication link:

* The entangled pair, gates, and Bell measurement are all simulated with
  Qiskit's Aer simulator (`simulation/superdense_coding.py`) -- there is
  no physical qubit anywhere in this build.
* The Raspberry Pi hardware (`hardware/`) visualizes each step of the
  protocol with pushbuttons, LEDs and LCDs so the abstract steps above
  become something you can press, watch, and read.
* A *real* superdense coding experiment (as first demonstrated with
  photon polarization by Mattle et al. in 1996) would replace the
  simulated Bell pair and gates with actual entangled photons, physical
  wave plates for the Pauli gates, and a physical Bell-state analyzer
  for the decode step.

## References

* C. H. Bennett and S. J. Wiesner, "Communication via one- and
  two-particle operators on Einstein-Podolsky-Rosen states," *Phys. Rev.
  Lett.* 69, 2881 (1992).
* K. Mattle, H. Weinfurter, P. G. Kwiat, A. Zeilinger, "Dense Coding in
  Experimental Quantum Communication," *Phys. Rev. Lett.* 76, 4656
  (1996).
* Nielsen & Chuang, *Quantum Computation and Quantum Information*,
  Section 2.3 ("Application: superdense coding").
* Qiskit Textbook, "Superdense Coding" chapter --
  https://qiskit.org/learn (algorithms for quantum computing).

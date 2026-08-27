"""
demo_cli.py

Command-line demo of the superdense coding protocol.

Usage
-----
    python -m simulation.demo_cli               # run all 4 combinations
    python -m simulation.demo_cli --bits 10      # run just one combination
    python -m simulation.demo_cli --save-images  # also save circuit diagrams
                                                  # to docs/images/

Each run prints:
  * the classical bits Alice wants to send
  * which gate she applies to her half of the entangled pair
  * the resulting Bell state
  * the bits Bob decodes after his Bell-basis measurement
  * whether they match (they always should -- the protocol is deterministic)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from simulation.superdense_coding import all_two_bit_combinations, run_protocol

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"


def print_result(r) -> None:
    print(f"  Alice's classical bits : b1={r.bit1} b0={r.bit0}")
    print(f"  Gate Alice applies     : {r.gate_name}")
    print(f"  Resulting Bell state   : {r.bell_state_name}")
    print(f"  Bob decodes            : b1={r.decoded_bit1} b0={r.decoded_bit0}")
    print(f"  Match                  : {'YES' if r.success else 'NO (unexpected!)'}")


def save_circuit_image(r) -> Path:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = IMAGES_DIR / f"circuit_{r.bit1}{r.bit0}.png"
    fig = r.circuit.draw(output="mpl")
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Superdense coding protocol demo")
    parser.add_argument(
        "--bits",
        type=str,
        default=None,
        help="Two-bit string to send, e.g. '01'. Omit to run all 4 combinations.",
    )
    parser.add_argument(
        "--save-images",
        action="store_true",
        help="Save each circuit diagram as a PNG under docs/images/",
    )
    args = parser.parse_args()

    if args.bits:
        if len(args.bits) != 2 or any(c not in "01" for c in args.bits):
            parser.error("--bits must be a two-character string of 0s and 1s, e.g. 10")
        combos = [(int(args.bits[0]), int(args.bits[1]))]
    else:
        combos = all_two_bit_combinations()

    all_success = True
    for bit1, bit0 in combos:
        result = run_protocol(bit1, bit0)
        print(f"\n=== Sending classical bits '{bit1}{bit0}' ===")
        print_result(result)
        all_success &= result.success

        if args.save_images:
            path = save_circuit_image(result)
            print(f"  Circuit diagram saved  : {path}")

    print("\nAll combinations transmitted successfully!" if all_success else "\nSomething went wrong.")


if __name__ == "__main__":
    main()

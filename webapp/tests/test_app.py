"""
Unit tests for the Flask web application.

Run with:
    pytest webapp/tests/ -v
"""

import pytest

from webapp.app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_index_page_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Superdense Coding" in resp.data


def test_api_config(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data["combinations"]) == {"00", "01", "10", "11"}
    assert data["gate_names"] == {"00": "I", "01": "X", "10": "Z", "11": "ZX"}
    assert data["send_animation_seconds"] > 0


@pytest.mark.parametrize(
    "bits,expected_gate",
    [("00", "I"), ("01", "X"), ("10", "Z"), ("11", "ZX")],
)
def test_api_run_all_combinations_round_trip(client, bits, expected_gate):
    resp = client.get(f"/api/run?bits={bits}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["gate_name"] == expected_gate
    assert data["decoded_message"] == bits
    assert data["success"] is True


@pytest.mark.parametrize("bad_bits", ["2x", "1", "111", "", "ab"])
def test_api_run_rejects_invalid_bits(client, bad_bits):
    resp = client.get(f"/api/run?bits={bad_bits}")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_api_run_all_runs_every_combination(client):
    resp = client.get("/api/run_all")
    assert resp.status_code == 200
    data = resp.get_json()
    assert {r["message"] for r in data} == {"00", "01", "10", "11"}
    assert all(r["success"] for r in data)


def test_api_circuit_png_returns_valid_png(client):
    resp = client.get("/api/circuit.png?bits=10")
    assert resp.status_code == 200
    assert resp.content_type == "image/png"
    assert resp.data[:8] == b"\x89PNG\r\n\x1a\n"


def test_api_circuit_png_rejects_invalid_bits(client):
    resp = client.get("/api/circuit.png?bits=xy")
    assert resp.status_code == 400

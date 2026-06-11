# pylint: disable=missing-function-docstring
"""
Tests for the T-Pot converter.
"""

import importlib

_tpot_module = importlib.import_module("idmefv2.connectors.t-pot.tpotconverter")
TpotConverter = _tpot_module.TpotConverter


SAMPLE_EVENT = {
    "@timestamp": "2026-02-02T12:40:01Z",
    "type": "cowrie",
    "src_ip": "192.0.2.10",
    "src_port": "34567",
    "dest_ip": "198.51.100.20",
    "dest_port": "22",
    "message": "login attempt failed",
}


def test_basic_conversion_and_fields():
    converter = TpotConverter()
    converted, out = converter.convert(SAMPLE_EVENT)
    assert converted
    assert out["Version"] == "2.D.V04"
    assert out["CreateTime"] == "2026-02-02T12:40:01Z"
    assert out["Category"] == ["Attempt.Login"]
    assert out["Priority"] == "Medium"
    assert out["Analyzer"]["Name"] == "tpot-cowrie"
    assert out["Source"][0]["IP"] == "192.0.2.10"
    assert out["Source"][0]["Port"] == [34567]
    assert out["Target"][0]["IP"] == "198.51.100.20"
    assert out["Target"][0]["Port"] == [22]
    assert out["Description"] == "Cowrie: login attempt failed"


def test_filter_rejects_missing_required_fields():
    converter = TpotConverter()
    event = SAMPLE_EVENT.copy()
    del event["dest_ip"]
    converted, _ = converter.convert(event)
    assert converted is False


def test_dionaea_description_contains_credentials():
    converter = TpotConverter()
    event = {
        "@timestamp": "2026-02-02T12:40:01Z",
        "type": "dionaea",
        "src_ip": "192.0.2.11",
        "src_port": "44444",
        "dest_ip": "198.51.100.21",
        "dest_port": "445",
        "connection": {"protocol": "smb"},
        "username": "admin",
        "password": "123456",
    }
    converted, out = converter.convert(event)
    assert converted
    assert "Dionaea: SMB login attempt" in out["Description"]
    assert "user 'admin'" in out["Description"]
    assert "password '123456'" in out["Description"]

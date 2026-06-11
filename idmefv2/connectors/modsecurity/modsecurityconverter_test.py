# pylint: disable=missing-function-docstring
"""
Tests for the ModSecurity converter.
"""

from .modsecurityconverter import ModSecurityConverter


SAMPLE_EVENT = {
    "transaction": {
        "time_stamp": "Mon Feb 02 12:40:01 2026",
        "client_ip": "10.0.0.10",
        "host_ip": "10.0.0.20",
        "request": {"uri": "/login"},
        "messages": [
            {
                "message": "SQL injection attempt detected",
                "details": {
                    "severity": 2,
                    "tags": ["application-multi", "attack-sqli"],
                },
            }
        ],
    }
}


def test_basic_conversion_and_mapping():
    converter = ModSecurityConverter()
    converted, out = converter.convert(SAMPLE_EVENT)
    assert converted
    assert out["Version"] == "2.D.V04"
    assert out["CreateTime"] == "2026-02-02T12:40:01"
    assert out["Category"] == ["Attempt.Exploit"]
    assert out["Priority"] == "High"
    assert out["Description"] == "SQL injection attempt detected"
    assert out["Source"][0]["IP"] == "10.0.0.10"
    assert out["Target"][0]["IP"] == "10.0.0.20"
    assert out["Target"][0]["URL"] == "/login"


def test_filter_rejects_missing_messages():
    converter = ModSecurityConverter()
    converted, _ = converter.convert({"transaction": {"time_stamp": "Mon Feb 02 12:40:01 2026"}})
    assert converted is False


def test_unknown_severity_and_default_category():
    converter = ModSecurityConverter()
    event = {
        "transaction": {
            "time_stamp": "Mon Feb 02 12:40:01 2026",
            "client_ip": "127.0.0.1",
            "host_ip": "127.0.0.1",
            "request": {"uri": "/"},
            "messages": [
                {
                    "message": "Generic warning",
                    "details": {"severity": "BOGUS", "tags": []},
                }
            ],
        }
    }
    converted, out = converter.convert(event)
    assert converted
    assert out["Priority"] == "Unknown"
    assert out["Category"] == ["Other.Uncategorised"]

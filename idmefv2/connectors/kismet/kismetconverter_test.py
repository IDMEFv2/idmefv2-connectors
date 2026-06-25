# pylint: disable=missing-function-docstring
"""
Tests for the Kismet converter.
"""

from .kismetconverter import KismetConverter


SAMPLE_ALERT = {
    "kismet.alert.timestamp": 0,
    "kismet.alert.severity": 12,
    "kismet.alert.header": "Rogue AP detected",
    "kismet.alert.source_mac": "aa:bb:cc:dd:ee:ff",
    "kismet.alert.text": "probe request flood",
}


def test_basic_conversion_and_defaults():
    converter = KismetConverter()
    converted, out = converter.convert(SAMPLE_ALERT)
    assert converted
    assert out["Version"] == "2.D.V04"
    assert out["CreateTime"] == "1970-01-01T00:00:00+00:00"
    assert out["Category"] == ["Recon.Sniffing"]
    assert out["Priority"] == "Medium"
    assert out["Description"] == "Rogue AP detected"
    assert out["Analyzer"]["Name"] == "kismet"
    assert out["Source"][0]["Note"] == "MAC: aa:bb:cc:dd:ee:ff - probe request flood"


def test_invalid_severity_is_mapped_to_unknown():
    converter = KismetConverter()
    alert = SAMPLE_ALERT.copy()
    alert["kismet.alert.severity"] = "not-a-number"
    converted, out = converter.convert(alert)
    assert converted
    assert out["Priority"] == "Unknown"

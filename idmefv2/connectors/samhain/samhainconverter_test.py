# pylint: disable=missing-function-docstring
"""
Tests for the Samhain converter.
"""

from .samhainconverter import SamhainConverter


def test_basic_conversion_and_attachment_generation():
    converter = SamhainConverter()
    line = (
        "CRIT : [2026-02-02T12:40:01+0000] "
        "msg=<policy violation detected> path=</etc/passwd> "
        "size_new=<123> chksum_new=<abc123>"
    )

    converted, out = converter.convert(line)
    assert converted
    assert out["Version"] == "2.D.V04"
    assert out["CreateTime"] == "2026-02-02T12:40:01+00:00"
    assert out["Priority"] == "High"
    assert out["Category"] == ["Information. UnauthorizedModification"]
    assert out["Description"] == "policy violation detected"
    assert out["Attachment"][0]["Name"] == "SamhainIntegrityDetail"
    assert "Path: /etc/passwd" in out["Attachment"][0]["Content"]


def test_invalid_line_is_rejected():
    converter = SamhainConverter()
    converted, out = converter.convert("this is not a samhain line")
    assert converted is False
    assert out is None


def test_non_string_input_is_rejected():
    converter = SamhainConverter()
    converted, out = converter.convert({"severity": "CRIT"})
    assert converted is False
    assert out is None

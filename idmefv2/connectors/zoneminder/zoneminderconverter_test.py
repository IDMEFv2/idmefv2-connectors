# pylint: disable=missing-function-docstring
"""
Tests for the Zoneminder converter.
"""

import base64

from .zoneminderconverter import ZoneminderConverter


def test_basic_conversion_and_snapshot_attachment(tmp_path):
    image_bytes = b"\xff\xd8\xfffake-jpeg"
    snapshot_path = tmp_path / "snapshot.jpg"
    snapshot_path.write_bytes(image_bytes)

    event = {
        "ET": "2026-02-02 12:40:01",
        "ED": "/event/100",
        "MN": "Camera-1",
        "EDP": str(tmp_path),
    }

    converter = ZoneminderConverter()
    converted, out = converter.convert(event)
    assert converted
    assert out["Version"] == "2.D.V04"
    assert out["CreateTime"] == "2026-02-02T12:40:01"
    assert out["Category"] == ["Intrusion.Burglary"]
    assert out["Priority"] == "High"
    assert out["Description"] == "Event /event/100 on monitor Camera-1"
    assert out["Attachment"][0]["FileName"] == str(tmp_path)
    assert out["Attachment"][1]["ContentType"] == "image/jpeg"
    assert out["Attachment"][1]["ContentEncoding"] == "base64"
    assert out["Attachment"][1]["Content"] == base64.b64encode(image_bytes).decode("ascii")


def test_invalid_date_falls_back_to_epoch_without_crashing(tmp_path):
    (tmp_path / "snapshot.jpg").write_bytes(b"dummy")
    event = {
        "ET": "not-a-date",
        "ED": "/event/101",
        "MN": "Camera-2",
        "EDP": str(tmp_path),
    }

    converter = ZoneminderConverter()
    converted, out = converter.convert(event)
    assert converted
    assert out["CreateTime"] == "1970-01-01T00:00:00"

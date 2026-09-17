# pylint: disable=missing-function-docstring
"""
Tests for the Motion converter.
"""

import base64
import json

from idmefv2.message import Message, SerializedMessage
from .motionconverter import MotionPictureSaveConverter

def _validate_idmefv2_message(message):
    payload = SerializedMessage("application/json", json.dumps(message).encode("utf-8"))
    Message.unserialize(payload)

def test_picture_save_conversion_and_snapshot_attachment(tmp_path):
    image_bytes = b"\xff\xd8\xfffake-jpeg"
    snapshot_path = tmp_path / "snapshot.jpg"
    snapshot_path.write_bytes(image_bytes)

    event = {
        "event_name": "picture_save",
        "date": "2026-02-02 12:40:01",
        "camera_id": "Camera-1",
        "event_id": "event-100",
        "file": str(snapshot_path),
    }

    converter = MotionPictureSaveConverter()
    converted, out = converter.convert(event)
    assert converted
    _validate_idmefv2_message(out)
    assert out["Version"] == "2.D.V08"
    assert out["CreateTime"] == "2026-02-02T12:40:01"
    assert out["Category"] == ["Access.Unauthorized"]
    assert out["Priority"] == "High"
    assert out["Description"] == "Event picture_save on monitor Camera-1"
    assert out["Attachment"][0]["FileName"] == str(snapshot_path)
    assert out["Attachment"][1]["ContentType"] == "image/jpeg"
    assert out["Attachment"][1]["ContentEncoding"] == "base64"
    assert out["Attachment"][1]["Content"] == base64.b64encode(image_bytes).decode("ascii")


def test_invalid_date_falls_back_to_epoch_without_crashing(tmp_path):
    snapshot_path = tmp_path / "snapshot.jpg"
    snapshot_path.write_bytes(b"dummy")

    event = {
        "event_name": "picture_save",
        "date": "not-a-date",
        "camera_id": "Camera-2",
        "event_id": "event-101",
        "file": str(snapshot_path),
    }

    converter = MotionPictureSaveConverter()
    converted, out = converter.convert(event)
    assert converted
    _validate_idmefv2_message(out)
    assert out["CreateTime"] == "1970-01-01T00:00:00"

# pylint: disable=missing-function-docstring
"""
Tests for the Prometheus converter.
"""

from .prometheusconverter import PrometheusConverter


SAMPLE_ALERT = {
    "state": "firing",
    "activeAt": "2018-07-04T20:27:12.60602144+02:00",
    "labels": {
        "alertname": "InstanceDown",
        "severity": "critical",
        "instance": "node-1:9100",
    },
}


def test_basic_conversion_and_mapping():
    converter = PrometheusConverter()
    converted, out = converter.convert(SAMPLE_ALERT)
    assert converted
    assert out["Version"] == "2.D.V04"
    assert out["CreateTime"] == "2018-07-04T20:27:12.606021+02:00"
    assert out["Category"] == ["Availability.Outage"]
    assert out["Priority"] == "High"
    assert out["Description"] == "InstanceDown"
    assert out["Source"][0]["Hostname"] == "node-1"


def test_filter_rejects_non_firing_alerts():
    converter = PrometheusConverter()
    alert = SAMPLE_ALERT.copy()
    alert["state"] = "resolved"
    converted, _ = converter.convert(alert)
    assert converted is False


def test_ipv6_instance_hostname_extraction():
    converter = PrometheusConverter()
    alert = {
        "state": "firing",
        "activeAt": "2026-02-02T12:40:01Z",
        "labels": {
            "alertname": "SomethingElse",
            "severity": "warning",
            "instance": "[2001:db8::1]:9090",
        },
    }
    converted, out = converter.convert(alert)
    assert converted
    assert out["Source"][0]["Hostname"] == "2001:db8::1"
    assert out["Priority"] == "Medium"
    assert out["Category"] == ["Other.Uncategorised"]

# pylint: disable=missing-function-docstring
'''
Tests for the Zabbix converter
'''
import re
from .zabbixconverter import ZabbixConverter

# A minimal sample event
SAMPLE_EVENT = {
    "clock": "0",  # epoch -> 1970-01-01T00:00:00+00:00
    "severity": "4",
    "name": "my-host unreachable",  # contains "down"/"unreachable"
    "hosts": [{"name": "my-host"}],
    "extra": {"ip": "10.0.0.1", "port": 10050},
    "extra_target": {"hostname": "zbx-server", "ip": "127.0.0.1", "port": 9090}
}

def test_basic_conversion_and_structure():
    converter = ZabbixConverter(["Polling"])
    ok, msg = converter.convert(SAMPLE_EVENT)
    assert ok is True
    assert isinstance(msg, dict)

    # Fixed fields and basic formats
    assert msg["Version"] == "2.D.V04"
    assert re.fullmatch(r"[0-9a-fA-F0-9\-]{36}", msg["ID"])
    assert msg["CreateTime"] == "1970-01-01T00:00:00+00:00"
    assert msg["Priority"] == "High"
    assert msg["Description"] == "my-host unreachable"

    # Analyzer section
    anl = msg["Analyzer"]
    assert anl["Name"] == "zabbix"
    assert anl["Model"] == "Zabbix Monitoring"
    assert anl["Type"] == "Monitor"
    assert anl["Category"] == ["NMS"]
    assert anl["Data"] == ["System"]
    assert anl["Method"] == ["Polling"]

    # Source section
    src0 = msg["Source"][0]
    assert src0["Hostname"] == "my-host"
    assert src0["IP"] == "10.0.0.1"
    assert src0["Port"] == [10050]

    # Target section
    tgt0 = msg["Target"][0]
    assert tgt0["Hostname"] == "zbx-server"
    assert tgt0["IP"] == "127.0.0.1"
    assert tgt0["Port"] == [9090]

def test_category_mapping_outage_failure_and_default():
    # "down" -> Availability.Outage
    ev1 = SAMPLE_EVENT.copy()
    ev1["name"] = "service down"
    ok1, msg1 = ZabbixConverter().convert(ev1)
    assert ok1
    assert msg1["Category"] == ["Availability.Outage"]

    # "cpu" -> Availability.Failure
    ev2 = SAMPLE_EVENT.copy()
    ev2["name"] = "High CPU load"
    ok2, msg2 = ZabbixConverter().convert(ev2)
    assert ok2
    assert msg2["Category"] == ["Availability.Failure"]

    # no keyword -> Other.Uncategorised
    ev3 = SAMPLE_EVENT.copy()
    ev3["name"] = "irrelevant trigger"
    ok3, msg3 = ZabbixConverter().convert(ev3)
    assert ok3
    assert msg3["Category"] == ["Other.Uncategorised"]

def test_missing_required_fields_are_filtered_out():
    # Without clock should not forward
    ok, _ = ZabbixConverter().convert({"severity": "4"})
    assert ok is False

    # Without severity same
    ok, _ = ZabbixConverter().convert({"clock": "0"})
    assert ok is False

# pylint: disable=missing-function-docstring
'''
Tests for the Zabbix converter
'''
import re
from .zabbixconverter import ZabbixConverter, ZabbixCloseConverter

# A minimal sample event
SAMPLE_EVENT = {
    "clock": "0",  # epoch -> 1970-01-01T00:00:00+00:00
    "severity": "4",
    "name": "my-host unreachable",  # contains "down"/"unreachable"
    "hosts": [{"name": "my-host"}],
    "extra": {"ip": "10.0.0.1", "port": 10050},
    "extra_target": {"hostname": "zbx-server", "ip": "127.0.0.1", "port": 9090},
    "pred_id": None,  # no predecessor alert (fresh problem, PredID chaining tested separately)
}

def test_basic_conversion_and_structure():
    converter = ZabbixConverter(["Polling"])
    ok, msg = converter.convert(SAMPLE_EVENT)
    assert ok is True
    assert isinstance(msg, dict)

    # Fixed fields and basic formats
    assert msg["Version"] == "2.D.V08"
    assert re.fullmatch(r"[0-9a-fA-F0-9\-]{36}", msg["ID"])
    assert msg["CreateTime"] == "1970-01-01T00:00:00+00:00"
    assert msg["Type"] == ["Availability"]
    assert msg["Status"] == ["Open"]
    assert msg["PredID"] == []
    assert msg["Priority"] == "High"
    assert msg["Description"] == "my-host unreachable"

    # Analyzer section
    anl = msg["Analyzer"]
    assert anl["Name"] == "zabbix"
    assert anl["Model"] == "Zabbix Monitoring"
    assert anl["Category"] == ["SIEM.NMS"]
    assert anl["Data"] == ["Data"]
    assert anl["Method"] == ["Monitor"]

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

    # no keyword -> Other.Undetermined
    ev3 = SAMPLE_EVENT.copy()
    ev3["name"] = "irrelevant trigger"
    ok3, msg3 = ZabbixConverter().convert(ev3)
    assert ok3
    assert msg3["Category"] == ["Other.Undetermined"]

def test_missing_required_fields_are_filtered_out():
    # Without clock should not forward
    ok, _ = ZabbixConverter().convert({"severity": "4"})
    assert ok is False

    # Without severity same
    ok, _ = ZabbixConverter().convert({"clock": "0"})
    assert ok is False

def test_pred_id_chains_to_previous_alert():
    ev = SAMPLE_EVENT.copy()
    ev["pred_id"] = "11111111-1111-1111-1111-111111111111"
    ok, msg = ZabbixConverter().convert(ev)
    assert ok
    assert msg["Status"] == ["Open"]
    assert msg["PredID"] == ["11111111-1111-1111-1111-111111111111"]

def test_close_converter_status_and_pred_id():
    close_src = {
        "clock": "0",
        "severity": "4",
        "name": "my-host unreachable",
        "pred_id": "22222222-2222-2222-2222-222222222222",
        "source": [{"ID": "s1", "IP": "10.0.0.1"}],
        "target": [{"ID": "t1", "IP": "127.0.0.1"}],
    }
    ok, msg = ZabbixCloseConverter().convert(close_src)
    assert ok
    assert msg["Status"] == ["Closed"]
    assert msg["PredID"] == ["22222222-2222-2222-2222-222222222222"]
    assert msg["Source"] == [{"ID": "s1", "IP": "10.0.0.1"}]
    assert msg["Target"] == [{"ID": "t1", "IP": "127.0.0.1"}]

def test_close_converter_missing_required_fields_are_filtered_out():
    ok, _ = ZabbixCloseConverter().convert({"severity": "4"})
    assert ok is False

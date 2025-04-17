# pylint: disable=missing-function-docstring
'''
Tests for the Wazuh converter
'''

from .wazuhconverter import WazuhConverter

def test_alert_1():
    converter = WazuhConverter()
    c, _ = converter.convert(WAZUH_ALERT_1)
    assert not c

def test_alert_2():
    converter = WazuhConverter()
    c, _ = converter.convert(WAZUH_ALERT_2)
    assert not c

def test_alert_3():
    converter = WazuhConverter()
    c, _ = converter.convert(WAZUH_ALERT_3)
    assert not c

def test_alert_4():
    converter = WazuhConverter()
    c, i = converter.convert(WAZUH_ALERT_4)
    assert c
    assert i['Priority'] == 'Low'
    assert i['Attachment']['Size'] == 29

def test_alert_5():
    converter = WazuhConverter()
    c, i = converter.convert(WAZUH_ALERT_5)
    assert c
    assert i['Priority'] == 'Medium'
    assert i['Attachment']['Hash'][0] == "c6ad41de8c6b30de49eb8bd196aebd078d2e3505"

def test_alert_6():
    converter = WazuhConverter()
    c, i = converter.convert(WAZUH_ALERT_6)
    assert c
    assert i['Priority'] == 'Medium'
    assert i['Attachment']['Size'] == 58

WAZUH_ALERT_1 = {
  "timestamp": "2025-04-16T09:02:57.556+0000",
  "rule": {
    "level": 3,
    "description": "Wazuh server started.",
    "id": "502",
    "firedtimes": 1,
    "mail": False,
    "groups": [
      "ossec"
    ],
    "pci_dss": [
      "10.6.1"
    ],
    "gpg13": [
      "10.1"
    ],
    "gdpr": [
      "IV_35.7.d"
    ],
    "hipaa": [
      "164.312.b"
    ],
    "nist_800_53": [
      "AU.6"
    ],
    "tsc": [
      "CC7.2",
      "CC7.3"
    ]
  },
  "agent": {
    "id": "000",
    "name": "wazuh.manager"
  },
  "manager": {
    "name": "wazuh.manager"
  },
  "id": "1744794177.4870",
  "full_log": "ossec: Manager started.",
  "decoder": {
    "name": "ossec"
  },
  "location": "wazuh-monitord"
}

WAZUH_ALERT_2 = {
  "timestamp": "2025-04-16T09:03:06.011+0000",
  "rule": {
    "level": 3,
    "description": "New wazuh agent connected.",
    "id": "501",
    "firedtimes": 1,
    "mail": False,
    "groups": [
      "ossec"
    ],
    "pci_dss": [
      "10.6.1"
    ],
    "gpg13": [
      "10.1"
    ],
    "gdpr": [
      "IV_35.7.d"
    ],
    "hipaa": [
      "164.312.b"
    ],
    "nist_800_53": [
      "AU.6"
    ],
    "tsc": [
      "CC7.2",
      "CC7.3"
    ]
  },
  "agent": {
    "id": "006",
    "name": "5e78ebb8ad04"
  },
  "manager": {
    "name": "wazuh.manager"
  },
  "id": "1744794186.5114",
  "full_log": "ossec: Agent started: '5e78ebb8ad04->any'.",
  "decoder": {
    "parent": "ossec",
    "name": "ossec"
  },
  "data": {
    "extra_data": "5e78ebb8ad04->any"
  },
  "location": "wazuh-agent"
}

WAZUH_ALERT_3 = {
  "timestamp": "2025-04-16T09:03:08.635+0000",
  "rule": {
    "level": 3,
    "description": "Wazuh agent stopped.",
    "id": "506",
    "mitre": {
      "id": [
        "T1562.001"
      ],
      "tactic": [
        "Defense Evasion"
      ],
      "technique": [
        "Disable or Modify Tools"
      ]
    },
    "firedtimes": 1,
    "mail": False,
    "groups": [
      "ossec"
    ],
    "pci_dss": [
      "10.6.1",
      "10.2.6"
    ],
    "gpg13": [
      "10.1"
    ],
    "gdpr": [
      "IV_35.7.d"
    ],
    "hipaa": [
      "164.312.b"
    ],
    "nist_800_53": [
      "AU.6",
      "AU.14",
      "AU.5"
    ],
    "tsc": [
      "CC7.2",
      "CC7.3",
      "CC6.8"
    ]
  },
  "agent": {
    "id": "006",
    "name": "5e78ebb8ad04"
  },
  "manager": {
    "name": "wazuh.manager"
  },
  "id": "1744794188.5392",
  "full_log": "ossec: Agent stopped: '5e78ebb8ad04->any'.",
  "decoder": {
    "parent": "ossec",
    "name": "ossec"
  },
  "data": {
    "extra_data": "5e78ebb8ad04->any"
  },
  "location": "wazuh-remoted"
}

WAZUH_ALERT_4 = {
  "timestamp": "2025-04-16T09:03:38.791+0000",
  "rule": {
    "level": 5,
    "description": "File added to the system.",
    "id": "554",
    "firedtimes": 1,
    "mail": False,
    "groups": [
      "ossec",
      "syscheck",
      "syscheck_entry_added",
      "syscheck_file"
    ],
    "pci_dss": [
      "11.5"
    ],
    "gpg13": [
      "4.11"
    ],
    "gdpr": [
      "II_5.1.f"
    ],
    "hipaa": [
      "164.312.c.1",
      "164.312.c.2"
    ],
    "nist_800_53": [
      "SI.7"
    ],
    "tsc": [
      "PI1.4",
      "PI1.5",
      "CC6.1",
      "CC6.8",
      "CC7.2",
      "CC7.3"
    ]
  },
  "agent": {
    "id": "006",
    "name": "5e78ebb8ad04",
    "ip": "172.18.0.2"
  },
  "manager": {
    "name": "wazuh.manager"
  },
  "id": "1744794218.6058",
  "full_log": "File '/test/test1.txt' added\nMode: realtime\n",
  "syscheck": {
    "path": "/test/test1.txt",
    "mode": "realtime",
    "size_after": "29",
    "perm_after": "rw-r--r--",
    "uid_after": "0",
    "gid_after": "0",
    "md5_after": "fc853869a9276994bbd6b965e422d235",
    "sha1_after": "c6ad41de8c6b30de49eb8bd196aebd078d2e3505",
    "sha256_after": "b1c2751ab1b0d9f67cd2c629aa87cde994ce0579c104fdf258865e31af0aaf60",
    "uname_after": "root",
    "gname_after": "root",
    "mtime_after": "2025-04-16T09:03:38",
    "inode_after": 22833396,
    "event": "added"
  },
  "decoder": {
    "name": "syscheck_new_entry"
  },
  "location": "syscheck"
}

# pylint: disable=line-too-long
WAZUH_ALERT_5 = {
  "timestamp": "2025-04-16T09:03:50.949+0000",
  "rule": {
    "level": 7,
    "description": "Integrity checksum changed.",
    "id": "550",
    "mitre": {
      "id": [
        "T1565.001"
      ],
      "tactic": [
        "Impact"
      ],
      "technique": [
        "Stored Data Manipulation"
      ]
    },
    "firedtimes": 1,
    "mail": False,
    "groups": [
      "ossec",
      "syscheck",
      "syscheck_entry_modified",
      "syscheck_file"
    ],
    "pci_dss": [
      "11.5"
    ],
    "gpg13": [
      "4.11"
    ],
    "gdpr": [
      "II_5.1.f"
    ],
    "hipaa": [
      "164.312.c.1",
      "164.312.c.2"
    ],
    "nist_800_53": [
      "SI.7"
    ],
    "tsc": [
      "PI1.4",
      "PI1.5",
      "CC6.1",
      "CC6.8",
      "CC7.2",
      "CC7.3"
    ]
  },
  "agent": {
    "id": "006",
    "name": "5e78ebb8ad04",
    "ip": "172.18.0.2"
  },
  "manager": {
    "name": "wazuh.manager"
  },
  "id": "1744794230.6742",
  "full_log": "File '/test/test1.txt' modified\nMode: realtime\nChanged attributes: permission\nPermissions changed from 'rw-r--r--' to 'rw-rw-r--'\n",
  "syscheck": {
    "path": "/test/test1.txt",
    "mode": "realtime",
    "size_after": "29",
    "perm_before": "rw-r--r--",
    "perm_after": "rw-rw-r--",
    "uid_after": "0",
    "gid_after": "0",
    "md5_after": "fc853869a9276994bbd6b965e422d235",
    "sha1_after": "c6ad41de8c6b30de49eb8bd196aebd078d2e3505",
    "sha256_after": "b1c2751ab1b0d9f67cd2c629aa87cde994ce0579c104fdf258865e31af0aaf60",
    "uname_after": "root",
    "gname_after": "root",
    "mtime_after": "2025-04-16T09:03:38",
    "inode_after": 22833396,
    "diff": "No content changes were found for this file.",
    "changed_attributes": [
      "permission"
    ],
    "event": "modified"
  },
  "decoder": {
    "name": "syscheck_integrity_changed"
  },
  "location": "syscheck"
}

# pylint: disable=line-too-long
WAZUH_ALERT_6 = {
  "timestamp": "2025-04-16T09:04:00.015+0000",
  "rule": {
    "level": 7,
    "description": "Integrity checksum changed.",
    "id": "550",
    "mitre": {
      "id": [
        "T1565.001"
      ],
      "tactic": [
        "Impact"
      ],
      "technique": [
        "Stored Data Manipulation"
      ]
    },
    "firedtimes": 2,
    "mail": False,
    "groups": [
      "ossec",
      "syscheck",
      "syscheck_entry_modified",
      "syscheck_file"
    ],
    "pci_dss": [
      "11.5"
    ],
    "gpg13": [
      "4.11"
    ],
    "gdpr": [
      "II_5.1.f"
    ],
    "hipaa": [
      "164.312.c.1",
      "164.312.c.2"
    ],
    "nist_800_53": [
      "SI.7"
    ],
    "tsc": [
      "PI1.4",
      "PI1.5",
      "CC6.1",
      "CC6.8",
      "CC7.2",
      "CC7.3"
    ]
  },
  "agent": {
    "id": "006",
    "name": "5e78ebb8ad04",
    "ip": "172.18.0.2"
  },
  "manager": {
    "name": "wazuh.manager"
  },
  "id": "1744794240.7577",
  "full_log": "File '/test/test1.txt' modified\nMode: realtime\nChanged attributes: size,mtime,md5,sha1,sha256\nSize changed from '29' to '58'\nOld modification time was: '1744794218', now it is '1744794240'\nOld md5sum was: 'fc853869a9276994bbd6b965e422d235'\nNew md5sum is : '5d38a5d2b5fad03f55ed8044713b346d'\nOld sha1sum was: 'c6ad41de8c6b30de49eb8bd196aebd078d2e3505'\nNew sha1sum is : '1309c4731b430cbab6c0bcf52f1869bec42993ce'\nOld sha256sum was: 'b1c2751ab1b0d9f67cd2c629aa87cde994ce0579c104fdf258865e31af0aaf60'\nNew sha256sum is : '95b1ec6786f7f090b1a1c5bf2afb45f37540e6b7108f57c80c84af33c66fe8b1'\n",
  "syscheck": {
    "path": "/test/test1.txt",
    "mode": "realtime",
    "size_before": "29",
    "size_after": "58",
    "perm_after": "rw-rw-r--",
    "uid_after": "0",
    "gid_after": "0",
    "md5_before": "fc853869a9276994bbd6b965e422d235",
    "md5_after": "5d38a5d2b5fad03f55ed8044713b346d",
    "sha1_before": "c6ad41de8c6b30de49eb8bd196aebd078d2e3505",
    "sha1_after": "1309c4731b430cbab6c0bcf52f1869bec42993ce",
    "sha256_before": "b1c2751ab1b0d9f67cd2c629aa87cde994ce0579c104fdf258865e31af0aaf60",
    "sha256_after": "95b1ec6786f7f090b1a1c5bf2afb45f37540e6b7108f57c80c84af33c66fe8b1",
    "uname_after": "root",
    "gname_after": "root",
    "mtime_before": "2025-04-16T09:03:38",
    "mtime_after": "2025-04-16T09:04:00",
    "inode_after": 22833396,
    "diff": "1a2\n> Wed Apr 16 09:04:00 UTC 2025\n",
    "changed_attributes": [
      "size",
      "mtime",
      "md5",
      "sha1",
      "sha256"
    ],
    "event": "modified"
  },
  "decoder": {
    "name": "syscheck_integrity_changed"
  },
  "location": "syscheck"
}

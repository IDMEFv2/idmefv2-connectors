# pylint: disable=missing-function-docstring
'''
Tests for the clamav converter
'''
from .clamavconverter import ClamavConverter

def test_alert_1():
    converter = ClamavConverter()
    c, i = converter.convert(CLAMAV_ALERT_1)
    assert c
    assert i['Priority'] == 'High'
    assert i['Attachment'][0]['Size'] == 6656
    assert i['Attachment'][0]['Hash'][0] == "md5:c6ccf4ddbccbcaa01b441690a329d1b0"
    assert i['Attachment'][0]['Note'] == 'Virus found: Clamav.Test.File-6'

def test_alert_2():
    converter = ClamavConverter()
    _, i = converter.convert(CLAMAV_ALERT_2)
    assert i['Attachment'][0]['Size'] == 362
    assert i['Attachment'][0]['FileName'] == "clam.7z"
    assert i['Attachment'][0]['Hash'][0] == "md5:30cc73fe9ec56e474c4d19c57ffe0546"
    assert i['Attachment'][0]['Note'] == 'Virus found: Clamav.Test.File-6'

# pylint: disable=line-too-long
CLAMAV_ALERT_1 = {
    "Magic": "CLAMJSONv0",
    "RootFileType": "CL_TYPE_MSEXE",
    "FileName": "clam-fsg.exe",
    "FileType": "CL_TYPE_MSEXE",
    "FileSize": 6656,
    "FileMD5": "c6ccf4ddbccbcaa01b441690a329d1b0",
    "EmbeddedObjects": [
        {
            "FileType": "CL_TYPE_MSEXE",
            "Offset": 6112,
            "ContainedObjects": [
                {
                    "FilePath": "/var/tmp/clamav/20250602_103214-clam-fsg.exe.9f0107b44b/clam-fsg.exe.fa0f0826fc/embedded-pe.8373dd8d0a",
                    "FileType": "CL_TYPE_MSEXE",
                    "FileSize": 544,
                    "FileMD5": "aa15bcf478d165efd2065190eb473bcb",
                    "Viruses": ["Clamav.Test.File-6"],
                }
            ],
        }
    ],
}

# pylint: disable=line-too-long
CLAMAV_ALERT_2 = {
    "Magic": "CLAMJSONv0",
    "RootFileType": "CL_TYPE_7Z",
    "FileName": "clam.7z",
    "FileType": "CL_TYPE_7Z",
    "FileSize": 362,
    "FileMD5": "30cc73fe9ec56e474c4d19c57ffe0546",
    "ContainedObjects": [
        {
            "FileName": "clam.exe",
            "FilePath": "/var/tmp/clamav/20250602_103220-clam.7z.f8feb03eb8/clam.7z.26c142e47a/clamav-3439100e80e88bd7bcccac352bf25db8.tmp",
            "FileType": "CL_TYPE_MSEXE",
            "FileSize": 544,
            "FileMD5": "aa15bcf478d165efd2065190eb473bcb",
            "Viruses": ["Clamav.Test.File-6"],
        }
    ],
}

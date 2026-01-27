# How to implement IDMEFv2 in your tool

## Introduction

This document explains how to implement IDMEFv2 into your tool.

"tool" is understood in this document as a cyber or physical security tool that generates security alerts, for instance:
- an intrusion detection system that generates an alert when detecting suspicious activity
- a motion detection system that detects suspicious motion inside a zone monitored by a camera
- an availability monitoring system that detects that a server is down

## Various ways of implementing IDMEFv2

This section describes the various ways of implementing IDMEFv2 into your tool. For now, the following paths have been identified:

- convert tool's JSON output to IDMEFv2
- convert tool's specific alert format to IDMEFv2
- generate IDMEFv2 directly inside the tool, if the tool provides an extension API

Once a IDMEFv2 message is generated, the message must be sent to a server using a HTTP POST request, this server being usually a SIEM or another server that "understands" IDMEFv2 format.

### Converting tool's JSON log output to IDMEFv2

This way of generating IDMEFv2 messages applies obviously to a tool that already generates a JSON output, either writing it into a file, a network socket... This is the case for example for the Suricata NIDS (https://suricata.io/).

### Converting tool's specific log format to IDMEFv2

Example: zoneminder

### Generating IDMEFv2 inside the tool

This way of implementing IDMEFv2 is prefered if tool has an extension API that allows to add "plugins" or "extensions" handling tool's alert.

Being very tool specific, this topic is not further developed.

### Sending IDMEFv2 messages

Final stage after generating a IDMEFv2 message is to send the generated message to a server using a HTTP/HTTPS POST request.

The most simple request is a POST request with request body being the raw JSON of the IDMEFv2 message. As there is no specific MIME type for IDMEFv2, the request Content-Type must be set to `application/json`.

Depending on the server, further authentication may be requested (see below [Concerto SIEM](#concerto-siem))

Below is an example of a Python class that can be used to send IDMEFv2 messages to a server using a HTTP POST request. The code uses the python `requests` module.

``` python
'''
A HTTP client POSTing IDMEFv2 messages and logging response
'''
import requests

class IDMEFv2Client2:
    '''
    Class storing client configuration and sending IDMEFv2 messages
    '''
    def __init__(self, url: str, login : str = None, password : str = None, verify : bool = True):
        self._url = url
        self._session = requests.Session()
        if login is not None and password is not None:
            self._session.auth = (login, password)
        self._session.verify = verify

    def post(self, idmefv2: dict):
        '''
        Sends a IDMEFv2 message as a HTTP POST request to server configured in constructor

        Args:
            idmefv2 (dict): the IDMEFv2 message, supposed to be valid
        '''
        kwargs = {'json' : idmefv2, 'timeout' : 1.0}
        r = self._session.post(self._url, **kwargs)
        r.raise_for_status()
```

## Generating IDMEFv2 messages


### IDMEFv2 mandatory fields

The following fields are mandatory in a IDMEFv2 message:

- `"Version"`: the version of the IDMEF format in use by this alert, an enum and respects the pattern `"2.D.V0[0-9]"`; example is `"2.D.V05"`
- `"ID"`: an UUID, as defined in RFC 4122; example is `"e5f9bbae-163e-42f9-a2f2-0daaf78fefb1"`
- `"CreateTime"`: timestamp indicating when the message was created, follows the syntax defined by the "date-time" production rule of the grammar in [RFC3339] ch 5.6.; example in Coordinated Universal Time (UTC) is `"1985-04-12T23:59:59.52Z"`.
- `"Analyzer"`: exactly one object of the `Analyzer` class

The following fields are mandatory in an `Analyzer` object:
- `"Name"`: the name of the analyzer, a string; example is `"foobar"`
- `"IP"`: an IP address, either V4 or V6; example is `"127.0.0.1"`

A minimal valid IDMEFv2 alert would therefore be, for version `"2.D.V05"` of the schema:
``` json
{
  "Version" : "2.D.V05",
  "ID" : "056666c6-9c04-43dd-b6bf-3d99fe490b08",
  "CreateTime" : "1985-04-12T23:59:59.52Z",
  "Analyzer" : {
    "Name" : "hello",
    "IP" : "127.0.0.1"
  }
}
```

### IDMEFv2 recommended fields

Some IDMEFv2 fields, though not mandatory, are recommended in order to generate a meaningful IMDEFv2 message. These fields are the following:

- `"Category"`: an enum, describing the alert category, for example `"Recon.Scanning"` for a network scanning detection or `"Vulnerable.System"` for the detection of a vulnerability
- `"Description"`: a string giving a human-readable description of the alert
- `"Analyzer.Category"`: an enum, describing the analyzer's category, such as `"AV"` for an AntiVirus or `"NIDS"` for a Network Intrusion Detection System
- `"Analyzer.Data"`: an enum, describing the type of data used by the analyzer, such as `"File"` for an AntiVirus scanning a file or `"Datagram"` for a Network Intrusion Detection System analyzing network trafic

An example for the Suricata NIDS can be:
``` json
{
    "Version": "2.D.V04",
    "ID": "da3f49dc-888a-4d75-a080-5d0f75049333",
    "CreateTime": "2001-12-31T23:59:59.52Z",
    "Category": [
        "Recon.Scanning"
    ],
    "Description": "suspicious network trafic detected - port scanning",
    "Analyzer": {
        "IP": "127.0.0.1",
        "Name": "suricata",
        "Model": "Suricata NIDS",
        "Type": "Cyber",
        "Category": [
            "NIDS"
        ],
        "Data": [
            "Network"
        ],
        "Method": [
            "Signature"
        ]
    }
}
```

### Using IDMEFv2 attachments

IDMEFv2 attachments are useful to add to a IDMEFv2 meaningful data such as network packet dumps or intrusion images.

Attachments are refered inside a IDMEFv2 message by name and can be refered from inside a `"Source"`, `"Target"` or `"Vector"` fields.

An attachment must contain the following fields:

- `"Name"`: unique identifier among attachments that can be used to reference this attachment from other classes using the `"Attachment"` attribute

An attachment can contain the following fields:

- `"ExternalURI"`: if the attachment's content is available and/or recognizable from an external resource, this is the URI (usually a URL) to that resource
- `"FileName"`: this will usually be the original name of the captured file or the name of the file containing the captured content (e.g. a packet capture file)
- `"ContentType"`: Internet Media Type of the attachment, using media types registered in IANA
- `"ContentEncoding"`: content encoding, one of "json" or "base64" (used when the content contains binary data)
- `"Content"`: the attachment's content, in case it is directly embedded inside the message

An example of using an attachment with a `"ExternalURI"` (some fields are omitted):
``` json
{
  "Attachment": [
    {
      "ExternalURI": "http://glpi/front/computer.form.php?id=2",
      "Name": "GlpiComputerLink2"
    },
  ],
  "Source": [
    {
      "Attachment": [
        "GlpiComputerLink2"
      ],
    }
  ]
}
```

An example of using attachments with filename or embedded content (some fields are omitted):
``` json
{
    "Target": [
        {
            "Attachment": [
                "EventDirectoryPath",
                "EventSnapshotImage"
            ],
            "GeoLocation": "43.967214059230514,5.576376914978028"
        }
    ],
    "Attachment": [
        {
            "Name": "EventDirectoryPath",
            "FileName": "/var/cache/zoneminder/events/1/2026-01-14/473"
        },
        {
            "Name": "EventSnapshotImage",
            "ContentType": "image/jpeg",
            "ContentEncoding": "base64",
            "Content": "/9j/4AA... base64 content truncated ...rtANFrAlc//Z"
        }
    ]
}
```

## Implementation helpers

Implementing IDMEFv2 can take advantage of libraries and classes:
- IDMEFv2 libraries, handling message creation, validation and serialization
- connector classes, including JSON tree transformation

### IDMEFv2 libraries

IDMEFv2 libraries currently exist in 2 flavours:

- https://github.com/IDMEFv2/python-idmefv2: a Python library for parsing, handling, and generating JSON IDMEFv2 messages
- https://github.com/IDMEFv2/java-idmefv2: a Java library for parsing, handling, and generating JSON IDMEFv2 messages

Refer to the corresponding gitub repositories for further documentation on how to use these libraries.

Note that for the Python language, a IDMEFv2 message is merely represented by a `dict`. Using the IDMEFv2 Python library is useful only if message must be validated against the IDMEFv2 JSON schema, which is an optional step.

### Connector classes

The Python `idmefv2.connectors` provide base classes that can be useful when implementing IDMEFv2 messages generation in Python. These classes are:
- [`JSONConverter`](../idmefv2/connectors/jsonconverter.py): Generic JSON to JSON converter
- [`FileTailer`](../idmefv2/connectors/filetailer.py): Python implementation of Unix 'tail -f'
- [`IDMEFv2Client`](../idmefv2/connectors/idmefv2client.py): A HTTP client POSTing IDMEFv2 messages and logging response

Refer to Python documentation of these classes and to source code using them for further information.

## Validating and testing

DUring the implementation of IDMEFv2, it is useful to validate generated messages against the JSON schema and to test sending them to either a SIEM understanding IDME>Fv2 or to a lightweight server that simply validates incoming messages.

### IDMEFv2 Validator

An online IDMEFv2 validator is available at https://safe4soc.eu/idmefv2-validator.

This validator can be very useful when establishing the template of the IDMEFv2 messages generated by your tool. However, it processes only one message at a time and cannot be automated. This functionality is provided by the IDMEFv2 test server.

### IDMEFv2 test server

The test server, located in [../idmefv2/connectors/testserver](./idmefv2/connectors/testserver/), provides a Python implementation of a test HTTP server serving POST requests containing IDMEFv2 messages. The server is based on Python `http.server` (https://docs.python.org/3/library/http.server.html) which, as the documentation says, is not recommended for production.

The test server handles IDMEFv2 messages received in a POST request with a content type of `application/json`. The body of the request is unserialized and validated using the IDMEFv2 Python library (https://github.com/IDMEFv2/python-idmefv2). If the message is valid, a HTTP 200 response is returned by the server. Otherwise, a HTTP 500 response is returned with a `text/plain` body containing the validation error message.

See [./idmefv2/connectors/testserver](./idmefv2/connectors/testserver/) for more information on how to launch and use the test server.

### Concerto SIEM

IDMEFv2 alerts can be uploaded to the IDMEFv2-compatible Concerto SIEM (https://github.com/IDMEFv2/Concerto-SIEM). Concerto SIEM uses *HTTP Basic Auth* for authentication.

An example of configuration for Concerto SIEM in `INI` syntax is given below.

``` ini
[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://1.2.3.4/api_idmefv2/   # Change 1.2.3.4 to server's real IP or name
# HTTP Basic Auth params
login = admin
password = password
```

## Conclusion
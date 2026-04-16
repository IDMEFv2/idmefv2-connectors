# IDMEFv2 suricata connector

This directory contains Python implementation of IDMEFv2 suricata (https://suricata.io/) connector.

## Overview

The connector uses suricata EVE JSON output (https://docs.suricata.io/en/latest/output/eve/eve-json-output.html).

The connector implements a server which can either, depending on Suricata configuration:
- receive EVE JSON objects using a Unix socket
- or poll a log file containing EVE JSON objects

The Suricata configuration file is parsed in order to extract the EVE output configuration.

Upon reception of a EVE alert, the alert is converted to IDMEFv2 and sent to a HTTP server using a POST request.

## Configuration

The Suricata connector uses a configuration file parsed by Python `configparser` module. An example of configuration file is given in [suricata-idmefv2.sample.conf](./suricata-idmefv2.sample.conf).

Example of Suricata connector configuration file:

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://127.0.0.1:8888

[suricata]
# Location of suricata configuration file
config = /etc/suricata/suricata.yaml
```

## Running

The `idmefv2.connectors.suricata` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.suricata -c /etc/suricata-idmefv2.conf
```

Once the connector running, a Suricata alert can be triggered using a HTTP request:

``` sh
curl http://testmynids.org/uid/index.html
```

This will trigger a Suricata alert which in turn will be converted to IDMEFv2 and forwarded either to the test server or to another server receiving IDMEFv2 alerts.

### Category Mapping

The connector attempts to categorize alerts based on the classification of the event:

- Not Suspicious Traffic → Access.Authorized
- Traffic → Other.Uncategorised
- Potentially Bad Traffic → Access.Unauthorized
- Attempted Information Leak → Theft.Data
- limited,Information Leak → Theft.Data
- largescale,Large Scale Information Leak → Theft.Breaches
- Attempted Denial of Service → Availability.DoS
- Denial of Service → Availability.DoS
- Attempted User Privilege Gain → Access.Escalation
- Unsuccessful User Privilege Gain → Access.Escalation
- Successful User Privilege Gain → Access.Escalation
- Attempted Administrator Privilege Gain → Access.Escalation
- Successful Administrator Privilege Gain → Access.Escalation
- Decode of an RPC Query → Other.Uncategorised
- Executable code was detected → Malware.Other
- A suspicious string was detected → Other.Uncategorised
- A suspicious filename was detected → Malware.Other
- An attempted login using a suspicious username was detected → Access.Forced
- A system call was detected → Other.Uncategorised
- A TCP connection was detected → Access.Authorized
- A Network Trojan was detected → Malware.Trojan
- A client was using an unusual port → Recon.Netword
- Detection of a Network Scan → Recon.Netword
- Detection of a Denial of Service Attack → Availability.DoS
- Detection of a non-standard protocol or event → Other.Uncategorised
- Generic Protocol Command Decode → Other.Uncategorised
- access to a potentially → Access.Unauthorized
- Web Application Attack → Access.Compromise
- Misc activity → Other.Uncategorised
- Misc Attack → Other.Uncategorised
- Generic ICMP event → Other.Uncategorised
- Inappropriate Content was Detected → Operational.Policy Violation
- Potential Corporate Privacy Violation → Theft.PII
- Attempt to login by a default username and password → Access.Forced
- Targeted Malicious Activity was Detected → National.Cyber
- Exploit Kit Activity Detected → Malware.Other
- Device Retrieving External IP Address Detected → Recon.Netword
- Domain Observed Used for C2 Detected → Access.Backdoor
- Possibly Unwanted Program Detected → Malware.Adware
- Successful Credential Theft Detected → Access.Compromise
- Possible Social Engineering Attempted → SocialEng.Other
- Crypto Currency Mining Activity Detected → Fraud.Usage
- Malware Command and Control Activity Detected → Access.Backdoor

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

- Not Suspicious Traffic → Other.Uncategorised
- Traffic → Other.Uncategorised
- Potentially Bad Traffic, → Other.Undetermined
- Attempted Information Leak → Information.DataLeak
- limited,Information Leak → Information.DataLeak
- largescale,Large Scale Information Leak → Information.DataLeak
- Attempted Denial of Service → Attempt.Exploit
- Denial of Service → Availability.DoS
- Attempted User Privilege Gain → Attempt.Exploit
- Unsuccessful User Privilege Gain → Attempt.Exploit
- Successful User Privilege Gain → Intrusion.UserCompromise
- Attempted Administrator Privilege Gain → Attempt.Exploit
- Successful Administrator Privilege Gain → Intrusion.AdminCompromise
- Decode of an RPC Query → Other.Uncategorised
- Executable code was detected → Attempt.Exploit
- A suspicious string was detected →
- A suspicious filename was detected →
- An attempted login using a suspicious username was detected → Attempt.Login
- A system call was detected → Malicious.System
- A TCP connection was detected →
- A Network Trojan was detected, → Malicious.Distribution
- A client was using an unusual port → Recon.Scanning
- Detection of a Network Scan → Recon.Scanning
- Detection of a Denial of Service Attack → Availability.DoS
- Detection of a non-standard protocol or event → Other.Undetermined
- Generic Protocol Command Decode → Other.Uncategorised
- access to a potentially vulnerable web application →
- Web Application Attack → Intrusion.AppCompromise
- Misc activity → Other.Uncategorised
- Misc Attack → Attempt.Exploit
- Generic ICMP event →
- Inappropriate Content was Detected → Abusive.Illicit
- Potential Corporate Privacy Violation → Information.UnauthorizedAccess
- Attempt to login by a default username and password → Attempt.Login
- Targeted Malicious Activity was Detected → Malicious.System
- Exploit Kit Activity Detected → Malicious.Distribution
- Device Retrieving External IP Address Detected → Recon.Scanning
- Domain Observed Used for C2 Detected →
- Possibly Unwanted Program Detected → Malicious.Configuration
- Successful Credential Theft Detected → Fraud.UnauthorizedUsage
- Possible Social Engineering Attempted → Recon.SocialEngineering
- Crypto Currency Mining Activity Detected → Fraud.UnauthorizedUsage
- Malware Command and Control Activity Detected → Malicious.Botnet

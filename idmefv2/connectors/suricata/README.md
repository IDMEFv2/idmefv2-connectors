# IDMEFv2 suricata connector

This repository contains Python implementation of IDMEFv2 suricata (https://suricata.io/) connector.

## Overview

The connector uses suricata EVE JSON output (https://docs.suricata.io/en/latest/output/eve/eve-json-output.html).

The connector implements a server which can either, depending on Suricata configuration:
- receive EVE JSON objects using a Unix socket
- or poll a log file containing EVE JSON objects

## Installation

Refer to [IDMEFv2 connectors](../../../README.md) for installation instructions.

## Configuration

The Suricata connector uses a configuration file parsed by Python `configparser` module. An example of configuration file is given in [suricata-idmefv2.sample.conf](./suricata-idmefv2.sample.conf).

```
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO

[suricata]
# Location of suricata configuration file
config=/etc/suricata/suricata.yaml

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://127.0.0.1:8888
```

## Running

The `idmefv2.connectors.suricata` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

```
python3 -m idmefv2.connectors.suricata -c /etc/suricata-idmefv2.conf
```

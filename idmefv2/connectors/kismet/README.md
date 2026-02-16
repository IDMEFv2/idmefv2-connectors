# IDMEFv2 Kismet connector

This directory contains a Python implementation of the IDMEFv2 Kismet (https://www.kismetwireless.net) connector. It retrieves Kismet alerts via the API and forwards them to an IDMEFv2 server.

## Overview

- **Polling**: connector polls the Kismet Alerts API at regular intervals (configured via `polling_interval`), retrieves alerts, converts them to IDMEFv2, and POSTs to the target HTTP endpoint.
- **De-duplication**: Uses a hash of the alert fields (timestamp, header, text) to avoid sending duplicate alerts.

## Configuration

The connector uses a configuration file parsed by Python’s `configparser` module. An example is provided in [kismet-idmefv2.sample.conf](./kismet-idmefv2.sample.conf).

### Sample configuration
```ini
[logging]
level = DEBUG

[idmefv2]
url = http://127.0.0.1:9991

[kismet]
url = http://localhost:2501/alerts/all_alerts.json
username = admin
password = admin
polling_interval = 10
```

## Running

The `idmefv2.connectors.kismet` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

```sh
python3 -m idmefv2.connectors.kismet -c kismet-idmefv2.sample.conf
```

In `idmefv2-connectors` root:
```sh
source venv/bin/activate
python3 -m idmefv2.connectors.kismet -c idmefv2/connectors/kismet/kismet-idmefv2.sample.conf
```

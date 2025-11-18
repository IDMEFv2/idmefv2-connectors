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

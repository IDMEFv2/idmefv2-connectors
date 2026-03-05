# IDMEFv2 T-Pot connector

This directory contains a Python implementation of the IDMEFv2 T-Pot (https://github.com/telekom-security/tpotce) connector.

## Overview

The T-Pot connector polls the Elasticsearch instance bundled with T-Pot for honeypot events and converts them to IDMEFv2 alerts.

The following T-Pot sensors are directly supported:

- **Cowrie** — SSH/Telnet honeypot (login attempts, session activity, command execution, file downloads)
- **Dionaea** — multi-protocol honeypot (connection attempts with optional credential capture)
- **Honeytrap** — generic TCP/UDP honeypot (connection events on arbitrary ports)

Each event is fingerprinted to avoid sending duplicate alerts across polling cycles. Queries are timestamp-anchored so only new events are fetched on each cycle.

Upon reception of a honeypot event, the alert is converted to IDMEFv2 and sent to an HTTP server using a POST request.

## Configuration

The connector uses an INI configuration file. An example is provided in [tpot-idmefv2.sample.conf](./tpot-idmefv2.sample.conf).

Example configuration file:

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = INFO

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://127.0.0.1:9999

[tpot]
# Elasticsearch URL (T-Pot default port: 64298)
elasticsearch_url = http://127.0.0.1:64298
# Polling interval in seconds
poll_interval = 30
# Elasticsearch index pattern for T-Pot events
index_pattern = logstash-*
# Set to true to forward events already present at startup (default: false)
catch_up = false
```

The `catch_up` option controls the behaviour on the first polling cycle: when `false` (the default), events already present in Elasticsearch at startup are silently consumed to set the baseline timestamp without being forwarded; when `true`, all existing events are forwarded immediately.

## Running

The `idmefv2.connectors.tpot` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.tpot -c /etc/tpot.conf
```

Once the connector is running, it will poll Elasticsearch every `poll_interval` seconds and forward any new honeypot events as IDMEFv2 alerts to the configured server.

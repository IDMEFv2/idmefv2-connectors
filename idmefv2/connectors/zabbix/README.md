
# IDMEFv2 Zabbix connector

This directory contains a Python implementation of the IDMEFv2 Zabbix (https://www.zabbix.com) connector. It retrieves Zabbix **problems** via the JSON-RPC API and forwards them to an IDMEFv2 server.

## Overview

- **Zabbix compatibility**: requires Zabbix **7.2+**.  
- **Two modes of operation**:  
  - **Polling**: connector polls the Zabbix JSON-RPC API at regular intervals (configured via `poll_interval`), retrieves new problem objects, converts them to IDMEFv2, and POSTs to the target HTTP endpoint.  
  - **Push**: connector runs an HTTP server on the address and port specified in the config. Zabbix can be configured to send alerts as a webhook (POST `/alert` with at least an `eventid` in the JSON). The connector enriches the payload via the Zabbix API (fetching timestamp, trigger details, host/interface info), converts it to IDMEFv2, and forwards it.

  To choose the mode (polling or push) simply modify the field in the .conf file.
  For detailed instructions on how to configure Zabbix to send alerts to the connector in push mode, including Media Type and Action setup, see (./ZABBIX_WEBHOOK_SETUP_README.md)

## Running

The connector uses a configuration file parsed by Python’s `configparser` module. An example is provided in [zabbix-idmefv2.sample.conf](./zabbix-idmefv2.sample.conf).

### Sample configuration
```ini
[logging]
# Logging level: DEBUG for verbose, INFO for minimal
level = DEBUG

[connector]
mode           = push        # polling or push
listen_address = 0.0.0.0     # only in push mode
listen_port    = 9090        # only in push mode

[zabbix]
# Zabbix API endpoint and credentials
url            = http://localhost:8080/api_jsonrpc.php
user           = Admin   #Zabbix user
password       = zabbix  #Zabbix user's password

# Interval between poll requests (in seconds)
poll_interval  = 30          # only in polling mode

[idmefv2]
# Destination for IDMEFv2 POSTs
url            = http://127.0.0.1:9999

```

The `idmefv2.connectors.zabbix` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.zabbix -c /etc/zabbix-idmefv2.conf
```

### Testing the Connector

**Polling mode**: simply wait for a Zabbix problem to occur (for example, stop the Zabbix agent on a monitored host to generate an outage). The connector will poll the API at the configured interval and automatically pick up and forward any new problem as an IDMEFv2 alert.

**Push mode**: For test push mode you can follow (./ZABBIX_WEBHOOK_SETUP_README.md).

For detailed instructions on how to configure Zabbix to send alerts to the connector in push mode, including Media Type and Action setup, see (./ZABBIX_WEBHOOK_SETUP_README.md)

In both modes, once an alert is retrieved, the connector will translate it into IDMEFv2 format and send it to the server configured under [idmefv2].
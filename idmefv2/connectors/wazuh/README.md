# IDMEFv2 wazuh connector

This directory contains Python implementation of IDMEFv2 Wazuh (https://wazuh.com/) connector.

## Overview


## Configuration

Example of Wazuh connector configuration file:

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://testserver.idmefv2:9999

[wazuh]
# Location of wazuh log file
logfile=/var/log/wazuh/wazuh-manager.log
```

## Running

The `idmefv2.connectors.wazuh` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.wazuh -c /etc/wazuh-idmefv2.conf
```

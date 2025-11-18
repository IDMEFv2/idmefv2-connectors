# IDMEFv2 Clamav connector

This directory contains Python implementation of IDMEFv2 Clamav (https://www.clamav.net/) connector.

## Overview


## Configuration

Example of Clamav connector configuration file:

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://testserver.idmefv2:9999

[clamav]
# Location of clamav temp dir
tempdir=/var/tmp/clamav
```

## Running

The `idmefv2.connectors.clamav` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.clamav -c /etc/clamav-idmefv2.conf
```

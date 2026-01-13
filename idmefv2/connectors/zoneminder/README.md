# IDMEFv2 zoneminder connector

This directory contains Python implementation of IDMEFv2 zoneminder (https://zoneminder.com/) connector.

## Overview

The zoneminder connector generates a IDMEFv2 message when a motion detection event is detected by zoneminder.

The connector is executed by zoneminder as a *filter* (see https://zoneminder.readthedocs.io/en/stable/userguide/filterevents.html).


## Configuration

The connector uses a INI configuration file. An example of configuration file is given in [zoneminder-idmefv2.sample.conf](./zoneminder-idmefv2.sample.conf).

Example of zoneminder connector configuration file:

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO
file=/var/log/idmefv2/zoneminder-connector.log

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://testserver.idmefv2:9999
```
### Zoneminder configuration

Once a monitor defined in zoneminder, its function must be set to `Modect` in order to enable motion detection.

## Running

The `idmefv2.connectors.zoneminder` Python module can be run directly.

``` sh
python3 -m idmefv2.connectors.zoneminder -c /etc/zoneminder-idmefv2.conf
```

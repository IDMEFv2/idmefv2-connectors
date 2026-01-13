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

Once a monitor defined in zoneminder, its function must be set to `Modect` in order to enable motion detection:
<img width="985" height="402" alt="image" src="https://github.com/user-attachments/assets/ecba7733-5311-4c2c-b12d-760a24fb14d7" />

Zones can be defined on this monitor:
<img width="1905" height="874" alt="image" src="https://github.com/user-attachments/assets/3fea502b-291b-4c6a-a37b-e64021d42bf2" />

A filter must then be added for motion detection events:
<img width="1907" height="744" alt="image" src="https://github.com/user-attachments/assets/aa6f3b8b-2ec3-414a-8072-d2a799364b29" />

Filter definition must include:
1. a name
2. Condition: `Alarmed Zone`
3. `equald to`
4. the zone previously defined
5. Execute command on all matches: `/usr/bin/python3 -m idmefv2.connectors.zoneminder -c /etc/zoneminder-idmefv2.conf ET "%ET%" ED "%ED%" MN "%MN%"`
6. Run filter in background

The command to execute is the following:
``` sh
/usr/bin/python3 -m idmefv2.connectors.zoneminder -c /etc/zoneminder-idmefv2.conf ET "%ET%" ED "%ED%" MN "%MN%"
```

The command line arguments are defined in note *More details on filter conditions:* in https://zoneminder.readthedocs.io/en/stable/userguide/filterevents.html#
- `%ET%`: Time of the event
- `%ED%`: Event description
- `%MN%`: Name of the monitor

## Running

The `idmefv2.connectors.zoneminder` Python module will be run directly by zoneminder when a motion detection event is triggered.

Below is an example of a IDMEFv2 message generated for a motion detection event:
``` sh
INFO:zoneminder-connector:zoneminder connector started
DEBUG:zoneminder-connector:zoneminder connector args ['ET', '2026-01-13 10:53:50', 'ED', 'Motion: Plafond', 'MN', 'Monitor-1', '/var/cache/zoneminder/events/1/2026-01-13/407']
DEBUG:zoneminder-connector:received {'ET': '2026-01-13 10:53:50', 'ED': 'Motion: Plafond', 'MN': 'Monitor-1', 'EFILE': '/var/cache/zoneminder/events/1/2026-01-13/407'}
INFO:zoneminder-connector:sending IDMEFv2 alert {'Version': '2.D.V04', 'ID': '4f6fbdeb-5b0b-4a81-b0e5-9e9d1dd36c41', 'CreateTime': '2026-01-13T10:53:50', 'Category': ['Intrusion.Burglary'], 'Priority': 'High', 'Description': 'Event Motion: Plafond on monitor Monitor-1', 'Analyzer': {'IP': '127.0.0.1', 'Name': 'zoneminder', 'Model': 'Zoneminder video surveillance system', 'Category': ['ODC'], 'Data': ['Images'], 'Method': ['Movement']}, 'Attachment': [{'Name': 'EventFilePath', 'FileName': '/var/cache/zoneminder/events/1/2026-01-13/407'}]}
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): testserver.idmefv2:9999
DEBUG:urllib3.connectionpool:http://testserver.idmefv2:9999 "POST / HTTP/1.1" 200 None
```

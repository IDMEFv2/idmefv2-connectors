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

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://testserver.idmefv2:9999

[zmjson]
logfile=/var/log/zmjson/events.json
```

### Zoneminder configuration

Once a monitor defined in zoneminder, its function must be set to `Modect` in order to enable motion detection:
<img width="985" height="402" alt="image" src="https://github.com/user-attachments/assets/ecba7733-5311-4c2c-b12d-760a24fb14d7" />

Zones can be defined on this monitor:
<img width="1905" height="874" alt="image" src="https://github.com/user-attachments/assets/3fea502b-291b-4c6a-a37b-e64021d42bf2" />

A filter must then be added for motion detection events:
<img width="1907" height="744" alt="image" src="https://github.com/user-attachments/assets/5dffb675-2f78-4248-99ae-231ad358c7ff" />

Filter definition must include:
1. a name
2. Condition: `Alarmed Zone`
3. `equald to`
4. the zone previously defined
5. Execute command on all matches: `/zm2json.sh /var/log/zmjson/events.json "%ET%" "%ED%" "%MN%"`
6. Run filter in background

The command to execute is the following:
``` sh
/zm2json.sh /var/log/zmjson/events.json "%ET%" "%ED%" "%MN%"
```

The command line arguments are defined in note *More details on filter conditions:* in https://zoneminder.readthedocs.io/en/stable/userguide/filterevents.html#
- `%ET%`: Time of the event
- `%ED%`: Event description
- `%MN%`: Name of the monitor

The path to the event directory will be automatically added by zoneminder.

The `zm2json.sh`script appends to a log file a JSON object containing a subset of event data. This log file will be "tailed" by the IDMEFv2 connector.

## Running

The `idmefv2.connectors.zoneminder` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.zoneminder -c /etc/zoneminder-idmefv2.conf
```

Below is an example of the log of a IDMEFv2 message generation for a motion detection event:
``` sh
INFO:zoneminder-connector:zoneminder connector started
INFO:zoneminder-connector:Tailing from file /var/log/zmjson/events.json
DEBUG:inotify.adapters:Inotify handle is (3).
DEBUG:inotify.adapters:Adding watch: [/var/log/zmjson/events.json]
DEBUG:inotify.adapters:Added watch (1): [/var/log/zmjson/events.json]

Freshening configuration in database
Migratings passwords, if any...
Loading config from DB 227 entries
Saving config to DB 227 entries
starting zm package scripts
starting apache
DEBUG:inotify.adapters:Events received from epoll: ['IN_ACCESS']
DEBUG:inotify.adapters:Events received in stream: ['IN_MODIFY']
DEBUG:zoneminder-connector:received b'{"ET":"2026-01-14 15:58:47","ED":"Motion: Plafond","MN":"Monitor-1","EDP":"/var/cache/zoneminder/events/1/2026-01-14/473"}'
INFO:zoneminder-connector:sending IDMEFv2 alert {'Version': '2.D.V04', 'ID': 'd8f489aa-d4aa-4fc3-84b9-530607a79d3b', 'CreateTime': '2026-01-14T15:58:47', 'Category': ['Intrusion.Burglary'], 'Priority': 'High', 'Description': 'Event Motion: Plafond on monitor Monitor-1', 'Analyzer': {'IP': '127.0.0.1', 'Name': 'zoneminder', 'Model': 'Zoneminder video surveillance system', 'Category': ['ODC'], 'Data': ['Images'], 'Method': ['Movement']}, 'Attachment': [{'Name': 'EventDirectoryPath', 'FileName': '/var/cache/zoneminder/events/1/2026-01-14/473'}, {'Name': 'EventSnapshotImage', 'ContentType': 'image/jpeg', 'ContentEncoding': 'base64', 'Content': '/9j/4AA... base64 content truncated ...rtANFrAlc//Z'}]}
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): testserver.idmefv2:9999
DEBUG:urllib3.connectionpool:http://testserver.idmefv2:9999 "POST / HTTP/1.1" 200 None


```

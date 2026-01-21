# IDMEFv2 motion connector

This directory contains Python implementation of IDMEFv2 motion (https://motion-project.github.io/) connector.

## Overview

The motion connector generates a IDMEFv2 message when a motion detection event is detected by motion.

The connector uses a *filter* shell script helper (see https://motion-project.github.io/).

## Configuration

The connector uses a INI configuration file. An example of configuration file is given in [motion-idmefv2.sample.conf](./motion-idmefv2.sample.conf).

Example of motion connector configuration file:

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://testserver.idmefv2:9999

[motionjson]
logfile=/var/log/motion/events.json
```

### Motion configuration

Once a monitor is defined in motion, it tracks for motion detection events. When an event is detected, motion can call a script with event information as command line arguments.

The command to execute is the following:
``` sh
/picture_save.sh /var/log/motion/events.json \"%Y-%m-%d %T\" %{host} %t %v \"%f\"
```

The command line arguments are defined in *Conversion specifiers:* section in https://motion-project.github.io/4.5.1/motion_config.html#conversion_specifiers
- `%Y`: Year of the event
- `%m`: month of the event
- `%d`: day of month of the event
- `%T`: time of the event
- `%{host}`: Hostname of the computer running motion
- `%t`: camera id
- `%v`: event name

The path to the event directory will be automatically added by motion.

The [`picture_save.sh`](./picture_save.sh) script appends to a log file a JSON object containing a subset of event data. This log file will be "tailed" by the IDMEFv2 connector.

## Running

The `idmefv2.connectors.motion` Python module can be run directly. The only mandatory command line argument is the path of the configuration file.

``` sh
python3 -m idmefv2.connectors.motion -c /etc/motion-idmefv2.conf
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

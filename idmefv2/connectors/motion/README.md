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
DEBUG:urllib3.connectionpool:http://testserver.idmefv2:9999 "POST / HTTP/1.1" 200 None
DEBUG:inotify.adapters:Events received from epoll: ['IN_ACCESS']
DEBUG:inotify.adapters:Events received in stream: ['IN_MODIFY']
DEBUG:motion-connector:received b'{"event_name":"picture_save", "date":"2026-01-30 13:28:12","host":"f54989725fcf","camera_id":"0","event_id":"01", "file":"/var/lib/motion/20260130132812-14.jpg"}'
INFO:motion-connector:sending IDMEFv2 alert {'Version': '2.D.V04', 'ID': '85925a7b-04c8-4000-a092-df23b5d5e15d', 'CreateTime': '2026-01-30T13:28:12', 'Category': ['Intrusion.Burglary'], 'Priority': 'High', 'Description': 'Event picture_save on monitor 0', 'Analyzer': {'IP': '127.0.0.1', 'Name': 'motion', 'Model': 'Motion video surveillance system', 'Category': ['ODC'], 'Data': ['Images'], 'Method': ['Movement']}, 'Attachment': [{'Name': 'EventDirectoryPath', 'FileName': '/var/lib/motion/20260130132812-14.jpg'}, {'Name': 'EventSnapshotImage', 'ContentType': 'image/jpeg', 'ContentEncoding': 'base64', 'Content': ''}]}
DEBUG:urllib3.connectionpool:Resetting dropped connection: testserver.idmefv2


```

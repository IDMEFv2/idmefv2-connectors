# IDMEFv2 connectors

This repository contains Python implementations of IDMEFv2 connectors for various probes and managers:
- Clamav antivirus (https://www.clamav.net/): see [./idmefv2/connectors/clamav](./idmefv2/connectors/clamav/#overview)
- Kismet (https://www.kismetwireless.net/): see [./idmefv2/connectors/kismet](./idmefv2/connectors/kismet/#overview)
- Modsecurity (https://modsecurity.org/): see [./idmefv2/connectors/modsecurity](./idmefv2/connectors/modsecurity/#overview)
- Prometheus (https://prometheus.io/): see [./idmefv2/connectors/prometheus](./idmefv2/connectors/prometheus/#overview)
- Suricata NIDS (https://suricata.io/): see [./idmefv2/connectors/suricata](./idmefv2/connectors/suricata/#overview)
- Wazuh (https://wazuh.com/): see [./idmefv2/connectors/wazuh](./idmefv2/connectors/wazuh/#overview)
- Zabbix (https://www.zabbix.com): see [./idmefv2/connectors/zabbix](./idmefv2/connectors/zabbix/#overview)
- Zoneminder (https://zoneminder.com): see [./idmefv2/connectors/zoneminder](./idmefv2/connectors/zoneminder/#overview)

Base classes for IDMEFv2 connectors implementations are provided:

- [`JSONConverter`](./idmefv2/connectors/jsonconverter.py): Generic JSON to JSON converter
- [`FileTailer`](./idmefv2/connectors/filetailer.py): Python implementation of Unix 'tail -f'
- [`IDMEFv2Client`](./idmefv2/connectors/idmefv2client.py): A HTTP client POSTing IDMEFv2 messages and logging response

A HTTP test server is also available in [./idmefv2/connectors/testserver](./idmefv2/connectors/testserver/#overview). This test server can be useful to test a new connector (see [Testing a connnector](#testing-a-connector))

## Overview

Connectors main loop does the following:
- peek an alert object in tool's JSON specific format
- convert this alert to IDMEFv2
- send the IDMEFv2 alert to a HTTP server using a POST request

Conversion is handled by classes derived from `JSONConverter` class.

The HTTP server to which the IDMEFv2 alert is sent can be either the HTTP test server provided in this repository or the Concerto SIEM (a fork of Prelude OSS), the first IDMEFv2-compatible SIEM (https://github.com/IDMEFv2/Concerto-SIEM )

## Prerequisites

The following prerequisites must be installed on your system to install and use this library:

- Python 3.10 or later
- The Python [setuptools](https://pypi.org/project/setuptools/) package (usually available as a system package under the name `python3-setuptools`)

Python dependencies are:
- inotify
- jsonpath_ng
- pyyaml
- requests

## Installation

### Installation from sources

It is highly recommended to install the library in a Python *virtualenv* https://virtualenv.pypa.io/en/latest/, unless running inside a container.

Installing the dependencies using `requirements.txt` is not supported; this repository provides a `pyproject.toml` which is the recommended alternative.

To install all modules, simply run in the root directory of the git clone:

``` sh
. /PATH/TO/YOUR/VIRTUALENV/bin/activate  # only if using a virtualenv
pip install --editable .
```

This will install as well the dependencies.

### Installation from packages

`idmefv2-connectors` provides packages currently hosted on [TestPyPI](https://test.pypi.org/).

To install using TestPyPI, use the following command:

```
pip install --extra-index-url https://test.pypi.org/simple/ idmefv2-connectors
```

### Installation from github

`idmefv2-connectors` releases can be installed directly from github repository without first cloning the repository. To install the latest release, run the following command:

``` sh
pip install git+https://github.com/IDMEFv2/idmefv2-connectors@latest
```

It is also possible to install a specific release:

``` sh
pip install git+https://github.com/IDMEFv2/idmefv2-connectors@V0.0.2
```

## Unit tests

Python unit tests using [`pytest`](https://docs.pytest.org/en/stable/) are provided:

```
$ pytest
================================================================= test session starts ==================================================================
platform win32 -- Python 3.11.9, pytest-8.3.5, pluggy-1.5.0
rootdir: /SOME/WHERE/idmefv2-connectors
configfile: pyproject.toml
collected 19 items

idmefv2/connectors/jsonconverter_test.py ......
   [ 31%]
...
    [100%]

================================================================== 19 passed in 0.67s ==================================================================
```

## Configuration

All connectors use a INI configuration file parsed by Python `configparser` module. Configuration file samples are provided for each connector.

Configuration file include a common configuration part and a tool specific configuration part.

### Common configuration

Common configuration part provide configuration entries for logging and for HTTP server URL.

An example of common configuration part is provided below.

``` ini
[logging]
# Logging level: change to DEBUG for more information, INFO for less information
level = DEBUG
# level = INFO

[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://127.0.0.1:8888
# HTTP Basic Auth params
# if not defined, the request will NOT include HTTP Basic Auth
# login = admin
# password = password
```

### Sending alerts to Concerto SIEM

IDMEFv2 alerts can be uploaded to the Concerto SIEM by changing the `[idmefv2]` configuration part. Concerto SIEM uses *HTTP Basic Auth* for authentication.

An example of configuration for Concerto SIEM is given below.

``` ini
[idmefv2]
# URL of server to POST IDMEFv2 alerts
url = http://1.2.3.4/api_idmefv2/   # Change 1.2.3.4 to server's real IP or name
# HTTP Basic Auth params
login = admin
password = password
```

### Specific configuration

* Clamav connector: see [./idmefv2/connectors/clamav](./idmefv2/connectors/clamav/#configuration)
* Kismet connector: see [./idmefv2/connectors/kismet](./idmefv2/connectors/kismet/#configuration)
* Modsecurity connector: see [./idmefv2/connectors/modsecurity](./idmefv2/connectors/modsecurity/#configuration)
* Prometheus connector: see [./idmefv2/connectors/prometheus](./idmefv2/connectors/prometheus/#configuration)
* Suricata connector: see [./idmefv2/connectors/suricata](./idmefv2/connectors/suricata/#configuration)
* Wazuh connector: see [./idmefv2/connectors/wazuh](./idmefv2/connectors/wazuh/#configuration)
* Zabbix connector: see [./idmefv2/connectors/zabbix](./idmefv2/connectors/zabbix/#configuration)
* Zoneminder connector: see [./idmefv2/connectors/zoneminder](./idmefv2/connectors/zoneminder/#configuration)

## Running

### Running connectors

* Clamav connector: see [./idmefv2/connectors/clamav](./idmefv2/connectors/clamav/#running)
* Kismet connector: see [./idmefv2/connectors/kismet](./idmefv2/connectors/kismet/#running)
* Modsecurity connector: see [./idmefv2/connectors/modsecurity](./idmefv2/connectors/modsecurity/#running)
* Prometheus connector: see [./idmefv2/connectors/prometheus](./idmefv2/connectors/prometheus/#running)
* Suricata connector: see [./idmefv2/connectors/suricata](./idmefv2/connectors/suricata/#running)
* Wazuh connector: see [./idmefv2/connectors/wazuh](./idmefv2/connectors/wazuh/#running)
* Zabbix connector: see [./idmefv2/connectors/zabbix](./idmefv2/connectors/zabbix/#running)
* Zoneminder connector: see [./idmefv2/connectors/zoneminder](./idmefv2/connectors/zoneminder/#running)

### Running the test server

See [./idmefv2/connectors/testserver](./idmefv2/connectors/testserver/#running)

## Testing a connector

When testing a new connector, using the test server can be useful in order to debug and validate IDMEFv2 messages emited by the new connector. Details are provided in test server [README](./idmefv2/connectors/testserver/#testing-using-the-test-server).

## Contributions

All contributions must be licensed under the Apache 2.0 license. See the LICENSE file inside this repository for more information.

To improve coordination between the various contributors, we kindly ask that new contributors subscribe to the [IDMEFv2 mailing list](https://www.freelists.org/list/idmefv2) as a way to introduce themselves.

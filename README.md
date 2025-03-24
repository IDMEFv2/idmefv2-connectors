# IDMEFv2 connectors

This repository contains Python implementations of IDMEFv2 connectors for various probes and managers:
- Suricata NIDS (https://suricata.io/): see [./idmefv2/connectors/suricata](./idmefv2/connectors/suricata/#overview)

Base classes for IDMEFv2 connectors implementations are provided:

- [`JSONConverter`](./idmefv2/connectors/jsonconverter.py): Generic JSON to JSON converter
- [`FileTailer`](./idmefv2/connectors/filetailer.py): Python implementation of Unix 'tail -f'
- [`IDMEFv2Client`](./idmefv2/connectors/idmefv2client.py): A HTTP client POSTing IDMEFv2 messages and logging response

A HTTP test server is also available in [./idmefv2/connectors/testserver](./idmefv2/connectors/testserver/#overview)

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

## Testing

Python unit tests using [`pytest`](https://docs.pytest.org/en/stable/) are provided:

``` sh
$ pytest
=========================================================================== test session starts ============================================================================
platform linux -- Python 3.12.3, pytest-8.3.4, pluggy-1.5.0
rootdir: /SOME/WHERE/idmefv2-connectors
configfile: pyproject.toml
collected 10 items

idmefv2/connectors/jsonconverter_test.py ......                                                                                                                      [ 60%]
idmefv2/connectors/suricata/suricataconverter_test.py ....                                                                                                           [100%]

============================================================================ 10 passed in 0.20s ============================================================================
```

## Running

## Running the Suricata connector

See [./idmefv2/connectors/suricata](./idmefv2/connectors/suricata/#running)

## Running the test server

See [./idmefv2/connectors/testserver](./idmefv2/connectors/testserver/#running)

# Contributions

All contributions must be licensed under the Apache 2.0 license. See the LICENSE file inside this repository for more information.

To improve coordination between the various contributors, we kindly ask that new contributors subscribe to the [IDMEFv2 mailing list](https://www.freelists.org/list/idmefv2) as a way to introduce themselves.

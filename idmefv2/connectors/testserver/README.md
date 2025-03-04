# IDMEFv2 test server

This directory contains a Python implementation of a test HTTP server serving POST requests containing IDMEFv2 messages.

## Overview

The server is based on Python `http.server` (https://docs.python.org/3/library/http.server.html) which, as the documentation says, is not recommended for production.

## Running

The `idmefv2.connectors.testserver` Python module can be run directly. Command line options are:

- `--port=PORT`: port to listen on
- `log-level=LEVEL`: logging lever, as in Python `logging`

For example:

``` sh
python3 -m idmefv2.connectors.testserver --port 9999 --log-level DEBUG

```

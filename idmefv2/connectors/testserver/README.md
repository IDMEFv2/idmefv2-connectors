# IDMEFv2 test server

This repository contains a Python implementation of a test HTTP server serving POST requests containing IDMEFv2 messages.

## Overview

The server is based on Python `http.server` (https://docs.python.org/3/library/http.server.html) which, as the documentation says, is not recommended for production.

## Installation

Refer to [IDMEFv2 connectors](../../../README.md) for installation instructions.

## Standalone installing

It is possible to run the server without installing the enclosing packages, as long as the following Python packages are installed:

- `jsonschema`
- `idmefv2`

## Running the server

The `idmefv2.connectors.testserver` Python module can be run directly. Command line options are:

- `--port=PORT`: gives port to listen on
- `log-level=LEVEL`: gives logging lever, as in Python `logging`

For example:
```
python3 -m idmefv2.connectors.testserver --port 9999 --log-level DEBUG

```

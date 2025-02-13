# IDMEFv2 connectors

This repository contains Python implementations of IDMEFv2 connectors for various probes and managers:
- [Suricata NIDS](./idmefv2/connectors/suricata)

Base classes for IDMEFv2 connectors implementations are provided:

- `JSONConverter`: base class for converting JSON input to other JSON output
- `FileTailer`: a Python generator yielding lines as in Unix command `tail -f`

A HTTP test server is also available in [./idmefv2/connectors/testserver](./idmefv2/connectors/testserver)

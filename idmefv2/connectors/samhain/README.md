# Samhain to IDMEFv2 Connector

This connector monitors Samhain HIDS log files and converts alerts to IDMEFv2 format.

## Features

- Tails the Samhain log file in real-time
- Parses Samhain text-based alert format
- Converts alerts to IDMEFv2
- Supports severity mapping and category classification

## Requirements

- Python 3.9+
- Samhain HIDS installed and running (or a log file to monitor)
- IDMEFv2 server to receive converted alerts

## Installation

Install the connector package (if not already installed):

```bash
pip install -e .
```

## Configuration

Copy the sample configuration file and edit it:

```bash
cp samhain-idmefv2.sample.conf samhain-idmefv2.conf
```

### Configuration Options

#### [logging]

| Option | Description | Default |
|--------|-------------|---------|
| `level` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `file` | Optional log file path | (console) |

#### [idmefv2]

| Option | Description | Default |
|--------|-------------|---------|
| `url` | URL of the IDMEFv2 server | (required) |
| `login` | Optional HTTP basic auth username | (none) |
| `password` | Optional HTTP basic auth password | (none) |
| `verify` | Verify SSL certificates | true |

#### [samhain]

| Option | Description | Default |
|--------|-------------|---------|
| `logfile` | Path to the Samhain log file | (required) |

## Usage

Run the connector:

```bash
python -m idmefv2.connectors.samhain -c samhain-idmefv2.conf
```

## IDMEFv2 Field Mapping

| Samhain Field | IDMEFv2 Field |
|---------------|---------------|
| `Severity` | `Priority` |
| `Timestamp` | `CreateTime` |
| `msg` / `Policy` | `Description` |
| `path` | `Target.File.Name` |
| `size_new` | `Target.File.Size` |
| `Activity Type` | `Category` |

### Severity Mapping

| Samhain Severity | IDMEFv2 Priority |
|------------------|------------------|
| CRIT, ALERT, ERR | High |
| WARN | Medium |
| NOTICE | Low |
| INFO, MARK | Info |

### Category Mapping

- Policy violation (ReadOnly, LogFiles) → `Information.UnauthorizedModification`
- File modification (checksum change) → `Information.UnauthorizedModification`
- Other → `Other.Uncategorised`

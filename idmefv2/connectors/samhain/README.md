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

Each Samhain log line has the form `SEVERITY : [TIMESTAMP] key=<value> ...`.

| Samhain Field | IDMEFv2 Field |
|---------------|---------------|
| `SEVERITY` prefix | `Priority` (see mapping below) |
| `TIMESTAMP` | `CreateTime` |
| `msg=<...>` | `Description`, and `Category` (see mapping below) |
| `path=<...>`, `size_new=<...>`, `chksum_new=<...>` | `Attachment[0].Content` (as free text, e.g. `"Path: ... | Size: ... | Hash: ..."`), when a `path` is present |

### Severity Mapping

| Samhain Severity | IDMEFv2 Priority |
|------------------|------------------|
| CRIT, ALERT, ERR | High |
| WARN | Medium |
| NOTICE | Low |
| INFO, MARK | Info |

### Category Mapping

Samhain policy events are logged as `msg=<POLICY [Tag] ...>`; the tag identifies which check module raised the event and is mapped as follows:

| Samhain Tag | IDMEFv2 Category |
|---|---|
| `SuidCheck` | Access.Escalation |
| `Process` (hidden/fake pid, missing) | Access.Backdoor |
| `ServiceNew`, `ServiceRestarted`, `ServicePortSwitch`, `ServiceMissing` | Access.Backdoor |
| `Kernel` | Access.Compromise |
| `Mounts` | Sabotage.Tampering |
| `RegistryKeyMissing`, `RegistryKeyNew`, `RegistryKeyChanged` | Sabotage.Tampering |
| `Logfile` | Other.Undetermined |
| `ReadOnly`, `LogFiles`, `GrowingLogFiles`, `Attributes`, `IgnoreAll`, `IgnoreNone` | Sabotage.Tampering |
| `Prelink` | Access.Compromise |
| `User0`-`User4` (site-defined policies) | Other.Undetermined |
| Untagged `POLICY` message (file integrity: missing/added/changed) or checksum change | Sabotage.Tampering |
| Other | Other.Undetermined |

`ReadOnly`, `LogFiles`, `GrowingLogFiles`, `Attributes`, `IgnoreAll`, `IgnoreNone`, `User0`-`User4` and `Prelink` are Samhain's built-in policy classes, assigned to monitored paths in `samhainrc` (e.g. a `[ReadOnly]` section); they are the classes most real-world deployments actually generate events for, alongside the module-specific tags above.

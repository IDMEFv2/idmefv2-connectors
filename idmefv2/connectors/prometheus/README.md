# Prometheus to IDMEFv2 Connector

This connector polls the Prometheus API for active alerts and converts them to IDMEFv2 format.

## Features

- Polls Prometheus `/api/v1/alerts` endpoint at configurable intervals (in config file)
- Converts Prometheus alerts to IDMEFv2 format
- Tracks seen alerts to avoid duplicates
- Automatically removes resolved alerts from tracking

## Requirements

- Python 3.9+
- Prometheus server with alerting rules configured
- IDMEFv2 server to receive converted alerts

## Installation

Install the connector package:

```bash
pip install -e .
```

## Configuration

Copy the sample configuration file and edit it:

```bash
cp prometheus-idmefv2.sample.conf prometheus-idmefv2.conf
```

### Configuration Options

#### [logging]

| Option | Description | Default |
|--------|-------------|---------|
| `level` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

#### [idmefv2]

| Option | Description | Default |
|--------|-------------|---------|
| `url` | URL of the IDMEFv2 server | (required) |
| `login` | Optional HTTP basic auth username | (none) |
| `password` | Optional HTTP basic auth password | (none) |
| `verify` | Verify SSL certificates | true |

#### [prometheus]

| Option | Description | Default |
|--------|-------------|---------|
| `url` | Base URL of Prometheus server | (required) |
| `poll_interval` | Seconds between polling cycles | 30 |

## Usage

Run the connector:

```bash
python -m idmefv2.connectors.prometheus -c prometheus-idmefv2.conf
```

## IDMEFv2 Field Mapping

| Prometheus Field | IDMEFv2 Field |
|-----------------|---------------|
| `labels.alertname` | `Description` |
| `labels.severity` | `Priority` |
| `activeAt` | `CreateTime` |
| `labels.instance` | `Source[0].Hostname` |
| `state` | (filter: only "firing" alerts) |

### Severity Mapping

| Prometheus Severity | IDMEFv2 Priority |
|--------------------|------------------|
| critical | High |
| high | High |
| warning | Medium |
| medium | Medium |
| low | Low |
| info | Info |
| (other) | Unknown |

### Category Mapping

The connector attempts to categorize alerts based on the alert name:

- Alerts containing "down" or "unreachable" → `Availability.Outage`
- Alerts containing "cpu", "memory", "disk", "latency" → `Availability.Failure`
- Other alerts → `Other.Uncategorised`

## Example Prometheus Alert Rule

```yaml
groups:
  - name: example
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected on {{ $labels.instance }}"
```

## Testing

To test the connector, you can run a simple HTTP server to receive IDMEFv2 messages:

```bash
python -m idmefv2.connectors.testserver
```

Then run the connector pointing to your Prometheus instance and trigger a new alert.

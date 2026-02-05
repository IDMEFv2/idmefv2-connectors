# ModSecurity Connector for IDMEFv2

This connector reads ModSecurity Web Application Firewall (WAF) audit logs in JSON format and converts security events to IDMEFv2 messages.

## Overview

The modsecurity connector generates a IDMEFv2 message when a detection event is detected by modsecurity.

## Features

- **Real-time log monitoring** using file tailing
- **Automatic severity mapping** from ModSecurity levels to IDMEFv2 Priority
- **Attack categorization** based on ModSecurity rule tags
- **Complete field mapping** including source IP, target URL, and attack details
- **Filtering** to process only relevant security events

## Requirements

- **Python 3.10 or later**
- **ModSecurity** configured with JSON audit logging
- **IDMEFv2 server** to receive alerts

## Installation

### From Source

```bash
cd idmefv2-connectors
pip install -e .
```

## Configuration

### ModSecurity JSON Logging Setup

Configure ModSecurity to output audit logs in JSON format:

```apache
SecAuditEngine On
SecAuditLogType Serial
SecAuditLogFormat JSON
SecAuditLog /var/log/modsecurity/modsec_audit.json
```

For Nginx with ModSecurity:

```nginx
modsecurity on;
modsecurity_rules_file /etc/nginx/modsec/main.conf;
```

### Connector Configuration

Create a configuration file (e.g., `modsecurity-idmefv2.conf`):

```ini
[logging]
level = INFO

[idmefv2]
url = http://your-idmefv2-server:9999

[connector]
log_file = /var/log/modsecurity/modsec_audit.json
```

## Usage

### Running the Connector

```bash
python -m idmefv2.connectors.modsecurity -c modsecurity-idmefv2.conf
```

### Docker Setup Example

```yaml
version: '3'
services:
  modsecurity:
    image: owasp/modsecurity-crs:nginx-alpine
    volumes:
      - ./modsec_logs:/var/log/modsecurity
    ports:
      - "80:80"

  modsecurity-connector:
    image: idmefv2-connectors
    volumes:
      - ./modsec_logs:/var/log/modsecurity:ro
      - ./modsecurity-idmefv2.conf:/etc/modsecurity-idmefv2.conf:ro
    command: python -m idmefv2.connectors.modsecurity -c /etc/modsecurity-idmefv2.conf
```

## Field Mapping

### ModSecurity to IDMEFv2

| ModSecurity Field | IDMEFv2 Field | Description |
|------------------|---------------|-------------|
| `transaction.time_stamp` | `CreateTime` | Event timestamp |
| `messages[0].message` | `Description` | Attack description |
| `messages[0].details.severity` | `Priority` | Severity level (numeric 0-7, mapped) |
| `transaction.client_ip` | `Source[0].IP` | Attacker IP address |
| `transaction.host_ip` | `Target[0].IP` | Target server IP |
| `transaction.request.uri` | `Target[0].URL` | Attacked URL |
| `messages[0].details.tags` | `Category` | Attack category (mapped) |

### Severity Mapping

ModSecurity uses numeric severity levels (0-7) which are mapped to IDMEFv2 Priority values aligned with the Prometheus connector scheme:

| ModSecurity Severity (Numeric) | ModSecurity Level | IDMEFv2 Priority |
|-------------------------------|-------------------|------------------|
| 0 | EMERGENCY | High |
| 1 | ALERT | High |
| 2 | CRITICAL | High |
| 3 | ERROR | High |
| 4 | WARNING | Medium |
| 5 | NOTICE | Low |
| 6 | INFO | Info |
| 7 | DEBUG | Info |

### Category Mapping

| ModSecurity Tags | IDMEFv2 Category |
|-----------------|------------------|
| attack-sqli | Attempt.Exploit |
| attack-xss | Attempt.Exploit |
| attack-rce | Attempt.Exploit |
| attack-lfi, attack-rfi | Attempt.Exploit |
| attack-injection | Attempt.Exploit |
| protocol-violation | Attempt.Exploit |
| (other) | Other.Uncategorised |

## Example

### ModSecurity Log Entry

```json
{
  "transaction": {
    "time": "2026-01-30T16:00:00.123Z",
    "client_ip": "192.168.1.100",
    "host_ip": "10.0.0.5",
    "request": {
      "method": "GET",
      "uri": "/admin.php?id=1' OR '1'='1"
    }
  },
  "messages": [
    {
      "message": "SQL Injection Attack Detected",
      "details": {
        "severity": "CRITICAL",
        "ruleId": "942100",
        "tags": ["attack-sqli", "OWASP_CRS"]
      }
    }
  ]
}
```

### Converted IDMEFv2 Message

```json
{
  "Version": "2.D.V04",
  "ID": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "CreateTime": "2026-01-30T16:00:00.123Z",
  "Category": ["Attempt.Exploit"],
  "Priority": "High",
  "Description": "SQL Injection Attack Detected",
  "Analyzer": {
    "IP": "10.0.0.5",
    "Name": "modsecurity",
    "Model": "ModSecurity WAF",
    "Type": "Cyber",
    "Category": ["WAF"],
    "Data": ["Application"],
    "Method": ["Signature"]
  },
  "Source": [
    {
      "IP": "192.168.1.100"
    }
  ],
  "Target": [
    {
      "IP": "10.0.0.5",
      "URL": "/admin.php?id=1' OR '1'='1"
    }
  ]
}
```

## Troubleshooting

### Connector Not Detecting New Logs

- Verify ModSecurity is writing to the configured log file
- Check file permissions (connector needs read access)
- Ensure JSON format is enabled in ModSecurity configuration

### No Alerts Being Sent

- Check IDMEFv2 server URL in configuration
- Verify network connectivity to IDMEFv2 server
- Review connector logs for errors (set `level = DEBUG`)

### Missing Fields in IDMEFv2 Output

- Verify ModSecurity log contains expected fields
- Check that ModSecurity rules include proper tags
- Review field mapping in converter code

## License

This connector follows the same license as the idmefv2-connectors project.

## See Also

- [ModSecurity Documentation](https://github.com/SpiderLabs/ModSecurity)
- [OWASP ModSecurity Core Rule Set](https://github.com/coreruleset/coreruleset)
- [IDMEFv2 Specification](https://github.com/IDMEFv2/IDMEFv2-spec)

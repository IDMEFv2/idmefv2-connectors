# IDMEFv2 Hello World Python Application

## Overview

This is an enhanced Python "Hello World" application that demonstrates how to build and send **IDMEFv2 (Intrusion Detection Message Exchange Format v2)** messages to a remote HTTP(S) server.

Instead of simply printing "Hello, World!" to the console, the application:
1. **Builds** an IDMEFv2-compliant alert message
2. **Embeds** the greeting "Hello world" in the message's `Description` field
3. **Sends** the message to a specified HTTP(S) server endpoint

## Key Features

✓ **IDMEFv2 Draft 7 Compliant** - Uses the official IDMEFv2 schema (version 2.D.V07)
✓ **Template-Based** - Loads message template from embedded resource file
✓ **Automatic IDs** - Generates unique UUIDs for message and analyzer
✓ **Timestamp** - Includes RFC 3339 formatted creation timestamp
✓ **HTTP(S) Support** - Sends messages via HTTP POST to any server
✓ **Clean Architecture** - Separated concerns with dedicated classes
✓ **Test Server Included** - Python test server for demonstrating functionality
✓ **Modern Python** - Uses Python 3.8+, pyproject.toml, and type hints

## Project Structure

```
HelloWorld/
├── pyproject.toml                    # Modern Python packaging configuration
├── src/
│   └── hello_world/
│       ├── __init__.py               # Package initialization
│       ├── app.py                    # Main application entry point
│       ├── message_builder.py        # Message builder class
│       ├── client.py                 # HTTP client class
│       └── hello-world-idmefv2.json  # IDMEFv2 message template
└── README.md                         # This file
```

## Building and Running the Application

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download** this project
2. **Navigate** to the project directory:
   ```bash
   cd doc/code/python/HelloWorld
   ```
3. **Create and activate** a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -e .
   ```

### Usage

First, activate the virtual environment:

```bash
cd doc/code/python/HelloWorld
source venv/bin/activate
```

The application accepts a server URL as a command-line argument:

```bash
hello-world http://localhost:8080/api/events
```

Or run directly with Python:

```bash
python -m hello_world.app http://localhost:8080/api/events
```

### Examples

```bash
# Send to local test server
hello-world http://localhost:8080/api/events

# Send to remote server
hello-world https://alert-server.example.com/v2/messages
```

## Testing with the Included Test Server

A test server is included in the main project that validates IDMEFv2 messages. It returns HTTP 200 for valid messages and HTTP 500 for invalid ones.

The test server should be running in Docker on port 9999. If not, you can start it using:

```bash
# From the project root directory
python -m idmefv2.connectors.testserver --port 9999
```

### Usage Examples

```bash
# Send to the test server (assuming it's running on port 9999)
hello-world http://localhost:9999

# Send to a remote server
hello-world https://alert-server.example.com/v2/messages
```

**Note**: The test server validates messages against the IDMEFv2 schema. If you receive a 500 error, it means the message doesn't conform to the expected schema.

## Dependencies

- **requests** - HTTP library for sending messages
- **Python 3.8+** - Modern Python with type hints and dataclasses

## Development

### Running Tests

```bash
python -m pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Related Projects

- [IDMEFv2 Specification](https://datatracker.ietf.org/doc/draft-ietf-mile-idmefv2/)
- [Java Hello World Version](../java/HelloWorld/)
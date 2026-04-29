# IDMEFv2 Hello World Java Application

## Overview

This is an enhanced Java "Hello World" application that demonstrates how to build and send **IDMEFv2 (Intrusion Detection Message Exchange Format v2)** messages to a remote HTTP(S) server.

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

## Project Structure

```
HelloWorld/
├── pom.xml                           # Maven POM with dependencies
├── src/
│   ├── main/
│   │   ├── java/com/example/
│   │   │   ├── App.java              # Main application entry point
│   │   │   ├── IDMEFv2MessageBuilder.java  # Message builder class
│   │   │   └── IDMEFv2Client.java    # HTTP client class
│   │   └── resources/
│   │       └── hello-world-idmefv2.json    # IDMEFv2 message template
│   └── test/
└── target/
    ├── hello-world-1.0-SNAPSHOT.jar  # Regular JAR
    └── hello-world-all.jar           # Executable FAT JAR with dependencies
```

## Building the Application

### Prerequisites

- Java 11 or higher
- Maven 3.6 or higher

### Build Steps

```bash
cd HelloWorld
mvn clean package
```

This will create two JAR files in the `target/` directory:
- `hello-world-1.0-SNAPSHOT.jar` - Application classes only
- `hello-world-all.jar` - Executable "fat JAR" with all dependencies included

## Running the Application

### Basic Usage

The application requires a server URL as a command-line argument:

```bash
java -jar target/hello-world-all.jar <SERVER_URL>
```

### Examples

#### Send to local test server (port 8080):
```bash
java -jar target/hello-world-all.jar http://127.0.0.1:8080/api/events
```

#### Send to remote IDMEF server:
```bash
java -jar target/hello-world-all.jar https://alert-server.example.com/v2/messages
```

#### Using the Java class directly:
```bash
java -cp target/hello-world-all.jar com.example.App http://localhost:8080/alerts
```

## Testing the Application

### Option 1: Using the IDMEFv2 Project Test Server

The idmefv2-connectors project includes an official test server that validates IDMEFv2 messages.

Start the test server in one terminal:
```bash
# From the project root directory
python3 -m idmefv2.connectors.testserver --port 9999
```

In another terminal, run the application:
```bash
cd doc/code/java/HelloWorld
java -jar target/hello-world-all.jar http://127.0.0.1:9999/
```

The test server will:
- Receive the HTTP POST request containing the IDMEFv2 message
- Validate the message using the official IDMEFv2 library
- Return **HTTP 200** if the message is valid
- Return **HTTP 500** with error details if the message is invalid
- Log detailed information about the request

### Option 2: Using curl

First, start the test server, then test with curl:
```bash
curl -X POST http://127.0.0.1:8888/ \
  -H "Content-Type: application/json" \
  -d @src/main/resources/hello-world-idmefv2.json
```

### Option 3: Included Python Test Server (for reference only)

For development/demonstration purposes, a simple Python test server is included:
```bash
python3 test-server.py 8080
```

## Generated IDMEFv2 Message

The application generates a message following this structure:

```json
{
  "Version": "2.D.V07",
  "ID": "938b487e-64fa-48e1-ad69-8f4dbe21c169",
  "CreateTime": "2026-04-17T07:03:15.755661460Z",
  "Description": "Hello world",
  "Type": ["Cyber"],
  "Category": ["Other.Test"],
  "Cause": "Normal",
  "Status": "Event",
  "Priority": "Info",
  "Confidence": 1.0,
  "Analyzer": {
    "ID": "652f326d-2378-4234-bb23-99bc4a4c4458",
    "Name": "HelloWorld-IDMEFv2-Client",
    "Model": "1.0.0",
    "Category": ["ID.UEBA"]
  }
}
```

### Message Fields Explanation

| Field | Value | Purpose |
|-------|-------|---------|
| **Version** | `2.D.V07` | IDMEFv2 Draft 7 specification |
| **ID** | UUID | Unique message identifier (auto-generated) |
| **CreateTime** | ISO 8601 | Message creation timestamp (auto-generated) |
| **Description** | "Hello world" | The greeting message - best candidate for this use case |
| **Type** | Cyber | Message type classification |
| **Category** | Other.Test | Indicates this is a test/demo message |
| **Cause** | Normal | No malicious cause |
| **Status** | Event | Raw event status |
| **Priority** | Info | Low priority informational message |
| **Confidence** | 1.0 | Complete confidence in the message |
| **Analyzer.Name** | HelloWorld-IDMEFv2-Client | Application identifier |
| **Analyzer.ID** | UUID | Analyzer unique identifier (auto-generated) |

## Code Structure

### App.java
The main application class that:
- Accepts server URL from command-line arguments
- Orchestrates message building and sending
- Displays progress messages and results
- Handles errors gracefully

### IDMEFv2MessageBuilder.java
Responsible for:
- Loading the `hello-world-idmefv2.json` template from resources
- Generating unique UUIDs for message ID and analyzer ID
- Creating the current timestamp in RFC 3339 format
- Merging the template with generated values
- Returning a formatted JSON string

### IDMEFv2Client.java
Handles HTTP communication:
- Creates an HTTP POST request
- Sets appropriate headers (Content-Type: application/json)
- Sends the JSON message to the server
- Processes the response and reports success/failure

## Dependencies

The application uses the following libraries (managed by Maven):

| Library | Version | Purpose |
|---------|---------|---------|
| jackson-databind | 2.15.2 | JSON processing and manipulation |
| httpclient5 | 5.2.1 | HTTP client for sending requests |
| slf4j-simple | 2.0.7 | Logging framework |
| junit | 4.13.2 | Unit testing framework |

## Message Field Selection Rationale

### Why "Description" for the greeting?

The IDMEFv2 schema provides several fields where text could be placed:

1. **Description** ✓ Selected
   - "Short free text human-readable description of the event"
   - Best for the primary message content
   - Appears in alert summaries
   - Concise and focused

2. **Note** (alternative)
   - "Free text human-readable additional note"
   - Better for supplementary information
   - Less prominent in typical UIs

3. **AltNames** (alternative)
   - Array of alternative identifiers
   - Intended for pairing with external systems
   - Not suitable for human-readable text

The **Description** field is the optimal choice because:
- It's designed for human-readable event summaries
- It's a primary field displayed in alert interfaces
- It's concise and focused (exactly what a greeting should be)
- It aligns with the IDMEFv2 specification's intended use

## Error Handling

The application gracefully handles various error scenarios:

- **Missing argument**: Displays usage instructions
- **Invalid URL**: HTTP client catches connection errors
- **Server errors**: Reports HTTP status codes (4xx, 5xx)
- **Resource loading**: Handles missing template files
- **JSON processing**: Catches and reports JSON parsing errors

## Exit Codes

- `0` - Success: message sent successfully
- `1` - Failure: connection error, server error, or missing arguments

## Example Output

When successfully sending a message:

```
═══════════════════════════════════════════════════════════════
IDMEFv2 Hello World Message Sender
═══════════════════════════════════════════════════════════════

📋 Building IDMEFv2 Hello World message...
✓ Message built successfully

📦 Generated Message:
───────────────────────────────────────────────────────────────
{
  "Version" : "2.D.V07",
  "ID" : "938b487e-64fa-48e1-ad69-8f4dbe21c169",
  ...
}
───────────────────────────────────────────────────────────────

🚀 Sending message to: http://127.0.0.1:8080/api/events
Server response status: 200
✓ IDMEFv2 message sent successfully to http://127.0.0.1:8080/api/events

✓ IDMEFv2 Hello World message sent successfully!
═══════════════════════════════════════════════════════════════
```

## Integration with IDMEFv2 Systems

This application can send messages to:

- **IDMEFv2 collectors** - for centralized alert storage
- **SIEM systems** - that support IDMEFv2 ingestion
- **Alert processors** - for further analysis and correlation
- **Custom servers** - that accept HTTP POST with JSON bodies
- **Test environments** - for validating IDMEFv2 message processing

Any HTTP(S) endpoint that accepts JSON POST requests can receive these messages.

## Notes

- The "Hello world" text is placed in the **Description** field, as it's the most appropriate field for this greeting message according to the IDMEFv2 specification
- The application generates unique identifiers (UUIDs) for each message, ensuring each invocation produces a distinct message
- Timestamps follow RFC 3339 format as required by the IDMEFv2 specification
- The message is classified as "Other.Test" category to clearly indicate it's a test/demonstration message

## References

- [IDMEFv2 Drafts Repository](https://github.com/IDMEFv2/IDMEFv2-Drafts)
- [IDMEFv2 Draft 7 Schema](https://github.com/IDMEFv2/IDMEFv2-Drafts/blob/main/IDMEFv2/07/IDMEFv2.schema)
- [IDMEFv2 Official Website](https://www.idmefv2.org)
- [Jackson JSON Library](https://github.com/FasterXML/jackson)
- [Apache HttpClient](https://hc.apache.org/httpcomponents-client-ga/)

## License

This application is part of the idmefv2-connectors project and follows the same license (Apache 2.0).

### Using the packaged JAR
```bash
java -jar target/hello-world-all.jar
```

## Expected Output

```
Hello, World!
```

## Configuration

### Java Version
You can change the target Java version by modifying the `maven.compiler.source` and `maven.compiler.target` properties in `pom.xml`.

### Dependencies
Additional dependencies can be added to the `<dependencies>` section in `pom.xml`.

## Development

### IDE Support
This project is compatible with:
- IntelliJ IDEA
- Eclipse
- VS Code (with Java extension)
- NetBeans

Simply open the project folder and the IDE will auto-detect the Maven configuration.

### Clean Build
```bash
mvn clean
```

### Full Build and Test
```bash
mvn clean install
```

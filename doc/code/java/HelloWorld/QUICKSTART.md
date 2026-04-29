# Quick Start Guide - IDMEFv2 Hello World

## 5-Minute Setup

### 1. Build the Application
```bash
cd doc/code/java/HelloWorld
mvn clean package
```

### 2. Run with IDMEFv2 Project Test Server (in terminal 1)
```bash
# From the project root directory
python3 -m idmefv2.connectors.testserver --port 8888
```

### 3. Send Message (in terminal 2)
```bash
java -jar target/hello-world-all.jar http://127.0.0.1:8888/
```

### 4. Watch the Magic Happen!
- Java app builds IDMEFv2 message with "Hello world" in Description
- Message is sent to test server via HTTP
- Test server validates the message using the official IDMEFv2 library
- Returns HTTP 200 (valid) or HTTP 500 (invalid with error details)
- Both client and server confirm success

## What You'll See

**In the Java application:**
```
✓ Message built successfully
📦 Generated Message:
[JSON output with Description: "Hello world"]
🚀 Sending message to: http://127.0.0.1:8080/api/events
Server response status: 200
✓ IDMEFv2 message sent successfully!
```

**In the test server:**
```
✓ Received IDMEFv2 Message:
[Complete formatted JSON]
📌 Message ID: [UUID]
📝 Description: Hello world
⏰ Created: [Timestamp]
🔧 Analyzer: HelloWorld-IDMEFv2-Client
```

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Main App | `App.java` | Orchestrates message building and sending |
| Message Builder | `IDMEFv2MessageBuilder.java` | Creates IDMEFv2 JSON from template |
| HTTP Client | `IDMEFv2Client.java` | Sends message to server |
| Template | `hello-world-idmefv2.json` | IDMEFv2 message template (embedded) |
| Test Server | `../../../idmefv2-connectors/testserver/__main__.py` | Simple Python server for testing |

## Message Template Location

The IDMEFv2 message template is stored as:
```
src/main/resources/hello-world-idmefv2.json
```

Packaged in the JAR as a classpath resource and loaded automatically.

## How "Hello world" is Integrated

The greeting "Hello world" is placed in the **Description** field:
- **Field**: `Description`
- **Value**: `"Hello world"`
- **Rationale**: This is the primary human-readable field for event summaries
- **Schema**: IDMEFv2 Draft 7 (version 2.D.V07)

## Architecture Diagram

```
App.java (main)
    ↓
    ├─→ IDMEFv2MessageBuilder
    │       ↓
    │       Loads: hello-world-idmefv2.json
    │       Generates: UUID, Timestamp
    │       Outputs: Complete JSON message
    │
    └─→ IDMEFv2Client
            ↓
            HTTP POST to server
            Returns: Success/Failure
```

## Important Files Created

### Core Application Files
- `src/main/java/com/example/App.java`
- `src/main/java/com/example/IDMEFv2MessageBuilder.java`
- `src/main/java/com/example/IDMEFv2Client.java`

### Resources
- `src/main/resources/hello-world-idmefv2.json`

### Supporting Files
- `README.md` - Full documentation
- `QUICKSTART.md` - This file
- `pom.xml` - Maven configuration with dependencies

## Dependencies Added

```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.15.2</version>
</dependency>

<dependency>
    <groupId>org.apache.httpcomponents.client5</groupId>
    <artifactId>httpclient5</artifactId>
    <version>5.2.1</version>
</dependency>

<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-simple</artifactId>
    <version>2.0.7</version>
</dependency>
```

## Troubleshooting

### "JAVA_HOME not defined"
```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

### "Connection refused"
Make sure test server is running. From the root directory of this repository: `python3 -m idmefv2.connectors.testserver --port 8888`

### "Template resource not found"
Run `mvn clean compile` to ensure resources are copied

## Example Usage Scenarios

### Scenario 1: Local Testing with IDMEFv2 Test Server
```bash
# Terminal 1
python3 -m idmefv2.connectors.testserver --port 8888

# Terminal 2
java -jar target/hello-world-all.jar http://127.0.0.1:8888/
```

### Scenario 2: Remote Server
```bash
java -jar target/hello-world-all.jar https://idmef-collector.company.com/api/alerts
```

### Scenario 3: HTTPS with Custom Port
```bash
java -jar target/hello-world-all.jar https://alert-server.local:8443/messages
```

## Verification Checklist

- ✓ Application compiles without errors
- ✓ JSON template resource is embedded in JAR
- ✓ Message includes unique UUID and timestamp
- ✓ Description field contains "Hello world"
- ✓ HTTP client successfully sends to server
- ✓ Server responds with HTTP 200/201/202
- ✓ Test server receives and displays message

## Next Steps

1. ✅ Verify the application works with included test server
2. 📝 Review the generated IDMEFv2 message format
3. 🔌 Integrate with your IDMEFv2 collector/SIEM
4. 📊 Test with different servers and endpoints
5. 🚀 Customize message fields as needed (see README.md)

## For More Information

See `README.md` for detailed documentation including:
- Full project structure
- Dependency details
- Error handling
- Exit codes
- Integration guide
- References and links

---

**Happy messaging!** 🎉

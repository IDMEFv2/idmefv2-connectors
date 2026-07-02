# IDMEFv2 Alert Plugin for Graylog

The IDMEFv2 Alert Plugin for Graylog automatically sends alert notifications in the IDMEFv2 (Intrusion Detection Message Exchange Format version 2) format to configurable HTTP(S) endpoints. When Graylog triggers an alert that is not filtered out by Graylog's filter rules, this plugin collects relevant alert data and formats it according to the IDMEFv2 specification before sending it via HTTP POST.

## Features

- **Automatic Alert Detection**: Triggers on Graylog alerts that pass through filters
- **IDMEFv2 Compliance**: Formats messages according to IDMEFv2 draft version 08-Dev
- **HTTP(S) Transmission**: Sends JSON-formatted IDMEFv2 messages to configurable endpoints
- **Configurable Organization Info**: Customizable organization name and ID for messages
- **Rich Alert Data**: Includes stream information, alert conditions, timestamps, and more

**Required Graylog version:** 7.0 and later

## Installation

### Build from Source

If you want to build the plugin yourself:

1. Clone this repository:
   ```bash
   git clone https://github.com/IDMEFv2/idmefv2-alert-plugin.git
   cd idmefv2-alert-plugin
   ```

2. Build the plugin:
   ```bash
   mvn package
   ```

You may need to install maven

   ```bash
   sudo apt install maven
   ```


3. Copy the generated JAR file from the `target/` directory to your Graylog plugin directory

4. Restart Graylog server

## Configuration

### Plugin Configuration

After installation, configure the plugin through Graylog's web interface:

1. Go to **Alerts** → **Notifications** in the Graylog web interface
2. Click **Create notification**
3. Select **IDMEFv2 Alert Notification** from the notification type dropdown
4. Configure the following settings:

   | Setting | Description | Required | Default |
   |---------|-------------|----------|---------|
   | **HTTP URL** | The HTTP(S) endpoint URL where IDMEFv2 messages will be sent via POST | Yes | - |
   | **Organization Name** | Name of your organization for IDMEFv2 messages | No | "Graylog" |
   | **Organization ID** | Unique identifier for your organization | No | "graylog" |

### Example Configuration

```
HTTP URL: https://your-siem.example.com/idmefv2/alerts
Organization Name: ACME Corporation
Organization ID: ACME-001
```

## Usage

### Setting Up Alert Notifications

1. **Create an Event Definition**:
   - Go to **Alerts** → **Event Definitions**
   - Create a new event definition (e.g., message count threshold, field value condition)

2. **Create a Notification**:
   - Go to **Alerts** → **Notifications**
   - Select **IDMEFv2 Alert Notification** as the notification type
   - Configure the HTTP endpoint and organization details
   - Attach the notification to your event definition

3. **Test the Configuration**:
   - Trigger a test alert or wait for a real alert
   - Check your HTTP endpoint for incoming IDMEFv2 messages

### IDMEFv2 Message Format

The plugin sends JSON messages in the following format (based on IDMEFv2 draft 08-Dev):

```json
{
  "Version": "2.D.V08-Dev",
  "ID": "550e8400-e29b-41d4-a716-446655440000",
  "OrganisationName": "ACME Corporation",
  "OrganisationId": "ACME-001",
  "Description": "Alert condition triggered: High error rate detected",
  "Status": "Event",
  "Priority": "Medium",
  "Type": ["Cyber"],
  "Category": ["Access.Unauthorized"],
  "CreateTime": "2024-01-15T10:30:00.000Z",
  "StartTime": "2024-01-15T10:29:45.000Z",
  "Note": "Event Definition: High error rate detected\nDescription: Triggers when error rate exceeds threshold\nEvent: High error rate detected\nBacklog size: 5",
  "Analyzer": {
    "Name": "Graylog SIEM",
    "Model": "Graylog 7.x",
    "Category": ["SIEM.SIEM"]
  }
}
```

### HTTP Request Details

- **Method**: POST
- **Content-Type**: application/json
- **Body**: IDMEFv2 JSON message
- **Authentication**: Not included (configure at your HTTP endpoint if needed)

## Development

### Prerequisites

- Java 21+
- Maven **3.9.6+** — Ubuntu's default `apt` package is 3.8.x and will be rejected by the `graylog2-server` build enforcer.

Install Maven 3.9.x without `sudo`:
```bash
curl -O https://dlcdn.apache.org/maven/maven-3/3.9.16/binaries/apache-maven-3.9.16-bin.tar.gz
tar -xzf apache-maven-3.9.16-bin.tar.gz -C ~/.local/share/
echo 'export PATH="$HOME/.local/share/apache-maven-3.9.16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
mvn -version  # should print 3.9.16
```

### Initial Setup

The plugin's parent POM (`graylog-plugin-web-parent`) is part of the `graylog2-server` source tree and is **not published to Maven Central**. Both repositories must be cloned side-by-side under the same parent directory:

```
workspace/
├── graylog2-server/          ← required sibling
└── graylog-plugin-idmefv2-alert/
```

```bash
cd /path/to/your/workspace
git clone --depth=1 https://github.com/Graylog2/graylog2-server.git
git clone https://github.com/IDMEFv2/idmefv2-alert-plugin.git
```

Then install the parent POM into your local Maven cache. This is only needed once (or after pulling a new version of `graylog2-server`):

```bash
cd graylog2-server
mvn install \
  -pl graylog-plugin-parent/graylog-plugin-web-parent \
  -am \
  -DskipTests \
  -Dskip.web.build=true
```

### Building

```bash
cd graylog-plugin-idmefv2-alert

# Backend only — fast, skips Node/Yarn/Webpack
mvn package -Dskip.web.build=true

# Full build including the React web interface (see note below)
mvn package

# Produce .deb / .rpm packages
mvn jdeb:jdeb
mvn rpm:rpm
```

The plugin JAR is written to `target/graylog-plugin-idmefv2-alert-<version>.jar`.

**Web build prerequisite (one-time):** The React build requires a vendor bundle from the `graylog2-server` web interface. Generate it once after cloning:

```bash
cd ../graylog2-server/graylog2-web-interface
yarn install
npx webpack --config webpack.vendor.ts
```

This produces `manifests/vendor-manifest.json`. After that, `mvn package` (without `-Dskip.web.build=true`) works. Re-run only when pulling a new version of `graylog2-server`.

The JAR built with `-Dskip.web.build=true` works fine for backend changes; the notification type will still appear in the Graylog UI because the frontend bundle is already included from a previous full build.

The warnings from `maven-shade-plugin` about overlapping `module-info` between `jackson-databind` and `jackson-core` are harmless and can be ignored.

### Deploying to a local Graylog instance

```bash
cp target/graylog-plugin-idmefv2-alert-*.jar /usr/share/graylog-server/plugin/
sudo systemctl restart graylog-server
tail -f /var/log/graylog-server/server.log | grep -i idmefv2
```

### Hot Reloading for Web Interface

For iterating on the React UI without a full Maven build:

```bash
cd /path/to/workspace/graylog2-server/graylog2-web-interface
ln -s /path/to/graylog-plugin-idmefv2-alert plugin/
yarn install && yarn start
```

## Running a local Graylog instance for testing

Two approaches are available depending on your needs:

| | Docker | graylog-project |
|---|---|---|
| Setup time | ~5 min | ~30 min (initial clone) |
| Rebuild cycle | `mvn package` + container restart | No restart needed (plugin on classpath) |
| Best for | Quick functional tests | Active plugin development |

---

### Approach 1 — Docker

A `docker-compose.yml` is provided at the root of the repository. It starts MongoDB, OpenSearch and Graylog 7.1 with the plugin JAR mounted directly.

**Prerequisites:** Docker and Docker Compose.

Install on Ubuntu:

```bash
sudo apt-get install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Apply the group change without a full logout:
newgrp docker
```

**First run:**

```bash
# Build the plugin JAR (full build with web UI — requires vendor bundle, see Building section)
mvn package
# Or backend-only if you haven't generated the vendor bundle yet:
# mvn package -Dskip.web.build=true

# Start all services
docker compose up -d

# Confirm the plugin loaded
docker compose logs graylog | grep -i idmefv2
```

Graylog web UI is available at http://localhost:9000 (login: `admin` / `admin`).

**After a code change:**

```bash
mvn package -Dskip.web.build=true
docker compose restart graylog
docker compose logs -f graylog | grep -i idmefv2
```

> The JAR is volume-mounted read-only. The container picks up the new JAR on restart without rebuilding the image.

---

### Approach 2 — graylog-project (no restart needed)

The [graylog-project](https://github.com/Graylog2/graylog-project) meta-project compiles our plugin alongside Graylog in the same Maven reactor. The plugin is loaded directly from compiled classes — no JAR packaging or container restart required after a Java change.

**1. Install the graylog-project CLI**

Download the latest binary from the [releases page](https://github.com/Graylog2/graylog-project-cli/releases):

```bash
mkdir -p ~/.local/bin
curl -L https://github.com/Graylog2/graylog-project-cli/releases/latest/download/graylog-project.linux \
  -o ~/.local/bin/graylog-project
chmod +x ~/.local/bin/graylog-project
# Make sure ~/.local/bin is in your PATH
graylog-project version
```

**2. Bootstrap the meta-project**

Use the manifest provided in this repo (`dev/graylog-project-manifest.json`), which includes both `graylog2-server` (master) and this plugin:

```bash
cd /path/to/your/workspace

# Bootstrap using the manifest from this repo (pass an absolute path)
graylog-project bootstrap \
  github://Graylog2/graylog-project.git \
  --manifest /absolute/path/to/graylog-plugin-idmefv2-alert/dev/graylog-project-manifest.json \
  --force-https-repos
```

This clones `graylog2-server` and our plugin into `graylog-project-repos/`, then generates a unified `pom.xml`.

**3. Initial build**

```bash
cd graylog-project
./mvnw compile -DskipTests -Dskip.web.build=true
```

**4. Start services and server**

```bash
# Start MongoDB + OpenSearch in Docker
graylog-project run dev:services

# In a second terminal, start the Graylog server (built from sources)
graylog-project run dev:server
```

Graylog web UI is available at http://localhost:9000 (login: `admin` / `admin`).

**5. After a code change**

Because the plugin is part of the Maven reactor, recompile and the running server picks up the changes on next request (or restart dev:server for a full reload):

```bash
cd graylog-project-repos/graylog-plugin-idmefv2-alert
mvn compile -Dskip.web.build=true
# Restart dev:server if needed
```

**Updating the manifest after a graylog2-server pull:**

```bash
cd graylog-project
git pull
graylog-project apply-manifest manifests/master.json
./mvnw compile -DskipTests -Dskip.web.build=true
```

---

## Troubleshooting

### Common Issues

1. **Plugin not loading**:
   - Check that the JAR file is in the correct plugin directory
   - Verify the Graylog server logs for plugin loading errors
   - Ensure the plugin version matches your Graylog version

2. **OpenSearch fails to start (`No custom admin password found`)**:
   OpenSearch 2.12+ requires `OPENSEARCH_INITIAL_ADMIN_PASSWORD` at first launch.
   The provided `docker-compose.yml` already includes this variable; if you customise the
   compose file make sure to keep it.

3. **MongoDB version rejected by Graylog**:
   Graylog 7.1+ requires MongoDB 7.0+. The provided `docker-compose.yml` uses `mongo:7`.
   If you see `You're running MongoDB X.Y but Graylog requires at least MongoDB 7.0.0`,
   update the image tag in your compose file.

4. **HTTP requests failing**:
   - Verify the configured URL is accessible
   - Check Graylog server logs for connection errors
   - Ensure the endpoint accepts POST requests with JSON content

5. **No alerts being sent**:
   - Confirm alert conditions are properly configured
   - Check that alerts are actually triggering
   - Verify the notification is linked to the alert condition

### Logs

Check the Graylog server logs for plugin-related messages:
```bash
tail -f /var/log/graylog-server/server.log | grep -i idmefv2
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Server Side Public License - see the LICENSE file for details.

## Support

For support and questions:
- [GitHub Issues](https://github.com/IDMEFv2/idmefv2-alert-plugin/issues)
- [IDMEFv2 Documentation](https://github.com/IDMEFv2/IDMEFv2-Drafts-IETF)

## Plugin Release

We are using the maven release plugin:

```
$ mvn release:prepare
[...]
$ mvn release:perform
```

This sets the version numbers, creates a tag and pushes to GitHub.

# How to implement IDMEFv2 in your tool

## Introduction

This document explains how to implement IDMEFv2 into your tool.

"tool" is understood in this document as a cyber or physical security tool that generates security alerts, for instance:
- an intrusion detection system that generates an alert when detecting suspicious activity
- a motion detection system that detects suspicious motion inside a zone monitored by a camera
- an availability monitoring system that detects that a server is down

## Various ways of implementing IDMEFv2

This section describes the various ways of implementing IDMEFv2 into your tool. For now, the following paths have been identified:

- convert tool's JSON output to IDMEFv2: this applies obviously to a tool that already generates a JSON output, either writing it into a file, a network socket...
- convert tool's specific alert format to IDMEFv2
- generate IDMEFv2 directly inside the tool, if the tool provides an extension API

Once a IDMEFv2 message is generated, the message must be sent to a server using a HTTP POST request, this server being usually a SIEM or another server that "understand" IDMEFv2 format.

### Converting tool's JSON log output to IDMEFv2

Example: suricata

### Converting tool's specific log format to IDMEFv2

Example: zoneminder

### Generating IDMEFv2 inside the tool

This way of implementing IDMEFv2 is prefered if tool has an extension API that allows to add "plugins" or "extensions" that handle tool's alert.

Being very tool specific, this topic is not further developed.

### Sending IDMEFv2 messages

Final stage after generating a IDMEFv2 message is to send the generated message to a server using a HTTP/HTTPS POST request.

The most simple request is a POST request with request body being the raw JSON of the IDMEFv2 message.

As there is no specific MIME type for IDMEFv2, the request Content-Type must be set to `application/json`.

Depending on the server, further authentication may be requested (see below []())

## Generating IDMEFv2 messages

### IDMEFv2 mandatory fields

### Using IDMEFv2 attachments

## Implementation helpers

### IDMEFv2 libraries

### Converter classes

## Validating and testing

### IDMEFv2 Validator

### IDMEFv2 test server

### Concerto SIEM

## Conclusion
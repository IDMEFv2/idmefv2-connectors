# IDMEFv2 test server

This directory contains a Python implementation of a test HTTP server serving POST requests containing IDMEFv2 messages.

## Overview

The server is based on Python `http.server` (https://docs.python.org/3/library/http.server.html) which, as the documentation says, is not recommended for production.

The test server handles IDMEFv2 messages received in a POST request with a content type of `application/json`. The body of the request is unserialized and validated using the IDMEFv2 Python library (https://github.com/IDMEFv2/python-idmefv2).

If the message is valid, a HTTP 200 response is returned by the server. Otherwise, a HTTP 500 response is returned with a `text/plain` body containing the validation error message.

If receiving any request with a method other than POST, the test server returns a HTTP 501 `Not Implemented` response.

## Running

The `idmefv2.connectors.testserver` Python module can be run directly. Command line options are:

- `--port=PORT`: port to listen on
- `log-level=LEVEL`: logging lever, as in Python `logging`

For example:

``` sh
python3 -m idmefv2.connectors.testserver --port 9999 --log-level DEBUG

```

## Testing using the test server

Once the test server running (see above), IDMEFv2 messages can be sent to the server.

Examples of sending HTTP POST requests with `curl` are provided below, with both invalid and valid messages. Corresponding data files are provided in this directory: [`./idmefv2.unvalid.json`](./idmefv2.unvalid.json) and [`./idmefv2.valid.json`](./idmefv2.valid.json).

**Sending an unvalid message**

Curl:
```
$ curl --verbose --data @idmefv2.bad.json --header "Content-Type: application/json" http://localhost:9999/
* Host localhost:9999 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:9999...
* Connected to localhost (::1) port 9999
> POST / HTTP/1.1
> Host: localhost:9999
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 13
>
* HTTP 1.0, assume close after body
< HTTP/1.0 500 Internal Server Error
< Server: BaseHTTP/0.6 Python/3.12.3
< Date: Wed, 26 Nov 2025 10:31:46 GMT
< Content-Type: text/plain; charset=utf-8
< Content-Length: 61
<
Additional properties are not allowed ('foo' was unexpected)
* Closing connection
```

Test server log output:
```
INFO:root:POST request
Path: /
Headers:
Host: localhost:9999
User-Agent: curl/8.5.0
Accept: */*
Content-Type: application/json
Content-Length: 13


Body:
{"foo":"bar"}

ERROR:root:Additional properties are not allowed ('foo' was unexpected)
172.19.0.1 - - [26/Nov/2025 10:31:46] "POST / HTTP/1.1" 500 -
```

**Sending a valid message**

Curl:
```
$ curl --verbose --data @idmefv2.valid.json --header "Content-Type: application/json" http://localhost:9999/
* Host localhost:9999 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:9999...
* Connected to localhost (::1) port 9999
> POST / HTTP/1.1
> Host: localhost:9999
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 287
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: BaseHTTP/0.6 Python/3.12.3
< Date: Wed, 26 Nov 2025 10:49:07 GMT
<
* Closing connection
```

Test server log output:
```
INFO:root:POST request
Path: /
Headers:
Host: localhost:9999
User-Agent: curl/8.5.0
Accept: */*
Content-Type: application/json
Content-Length: 287


Body:
{  "Version" : "2.D.V04",  "ID" : "09db946e-673e-49af-b4b2-a8cd9da58de6",  "CreateTime" : "2021-11-22T14:42:51.881033Z",  "Analyzer" : {    "IP" : "127.0.0.1",    "Name" : "foobar",    "Model" : "generic",    "Category" : [ "LOG" ],    "Data" : [ "Log" ],    "Method" : [ "Monitor" ]  }}

172.19.0.1 - - [26/Nov/2025 10:49:07] "POST / HTTP/1.1" 200 -
```

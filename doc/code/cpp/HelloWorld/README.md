# IDMEFv2 Hello World C++ Application

This example creates a valid IDMEFv2 "Hello world" message and sends it to a remote HTTP server using a plain POSIX socket HTTP client.

## Requirements

- Linux with `cmake` and a C++17 compiler

On Debian/Ubuntu:

```bash
sudo apt install cmake build-essential
```

## Build

```bash
cd /path/to/project/doc/code/cpp/HelloWorld
mkdir -p build
cd build
cmake ..
cmake --build .
```

## Run

Start the repository test server:

```bash
cd /path/to/project/
python3 -m idmefv2.connectors.testserver --port 8888
```

Then run the C++ client:

```bash
cd doc/code/cpp/HelloWorld/build
./hello-world http://127.0.0.1:8888/
```

The program prints the generated IDMEFv2 payload and reports the server response.

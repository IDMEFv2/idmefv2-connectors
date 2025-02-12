# IDMEFv2 suricata connector

This repository contains Python implementation of IDMEFv2 suricata (https://suricata.io/) connector.

## Overview

The connector uses suricata EVE JSON output (https://docs.suricata.io/en/latest/output/eve/eve-json-output.html).

The connector implements a server which can either, depending on Suricata configuration:
- receive EVE JSON objects using a Unix socket
- or poll a log file containing EVE JSON objects

## Installation

## Running


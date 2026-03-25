# IDMEFv2 elastalert2 alerter

This directory contains the implementation of an IDMEFv2 alerter for elastalert2 (https://github.com/jertel/elastalert2).

## Overview

The IDMEFv2 alerter implements an `Alerter` (https://elastalert2.readthedocs.io/en/latest/recipes/adding_alerts.html) that is passed matches through the `alert` method when a rule matches.

The IDMEFv2 alerter converts a match to an IDMEFv2 alert using a predefined template and sends a HTTP POST request to a server receiving IDMEFv2 alerts.

The template is specified using Jinja2 (https://jinja.palletsprojects.com/en/stable/).

## IDMEFv2 alerter

Specifying IDMEFv2 alerter in a `elastalert2` rule is done by adding to the rule the following line:

``` yaml
alert: "idmefv2.connectors.elastalert2.IDMEFv2Alerter"
```

`elastalert2` will import the python module from the `idmefv2-connectors` package, which must therefore have been installed using the methods described in [../../../README.md](../../../#installation).

### IDMEFv2 alerter parameters

Required:

`idmefv2_url`: URL of the IDMEFv2 server to which the alert will be posted

`idmefv2_template`: inline Jinja2 (https://jinja.palletsprojects.com/en/stable/) template for IDMEFv2 message generation

Optional:

`idmefv2_login`: login for HTTP base authentication

`idmefv2_password`: password for HTTP base authentication

`idmefv2_verify`: HTTPS certificate validation, defaults to `True`. Set to `False` if using self-signed certificates.

### IDMEFv2 alert Jinja2 template

The Jinja2 template specified in the rule is a JSON string that can contain Jinja2 variable expansions https://jinja.palletsprojects.com/en/stable/templates/#variables specified between `{{` and `}}`.

The context dictionary passed to the template when performing template rendering contains 2 toplevel variables:

- `rule`: the rule that triggered the match, containing in particular attribute `rule.name`
- `match`: the match python object that is passed to the `alert()` method

To access attributes of a variable, both dot (.) syntax and Python subscript syntax ([]) can be used. Therefore `{{ foo.bar }}` and `{{ foo['bar'] }}` achieve the same final expansion.

> [!IMPORTANT]
> To access the `@timestamp` attribute of the `match` variable, the subscript syntax **must** be used, as Jinja2 does not allow an attribute name to start with `@` character; thus `{{ match['@timestamp'] }}` is the only available way to access this attribute.

### Rule example

Below is an example of a rule using the IDMEFv2 alerter. This rule example is also available in [example_rule.yaml](./example_rule.yaml)

``` yaml
name: "name of the rule"

index: theindex-*

type: any

alert: "idmefv2.connectors.elastalert2.IDMEFv2Alerter"

# URL of the IDMEFv2 server
idmefv2_url: http://1.2.3.4:9999

# Jinja2 template for IDMEFv2 message generation
idmefv2_template:  |-
  {
    "Version": "2.D.V04",
    "ID": "{{ match.agent.id }}",
    "CreateTime": "{{ match['@timestamp'] }}",
    "Category": ["Malicious.System"],
    "Description": "{{ rule.name }}",
    "Analyzer": {
      "Name": "{{ match.agent.type }}",
      "IP": "{{ match.source.ip }}"
    }
  }

# login for HTTP base authentication
# idmefv2_login: foo

# password for HTTP base authentication
# idmefv2_password: bar

# HTTPS certificate validation
# idmefv2_verify: False
```

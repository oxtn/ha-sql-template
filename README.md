# SQL Template Sensor Integration

This integration builds on the functionality provided by the [SQL integration](https://www.home-assistant.io/integrations/sql) and allows the `query` configuration variable to accept a template instead of solely a static value.

## Quick start

1. Download the
   [latest release](https://github.com/oxtn/ha-sql-template/releases/latest).
2. Unpack the release and copy the `custom_components/sql_template` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Restart Home Assistant.
4. Go to Settings->Devices and Services->Add Integration and select the `SQL Template` integration to launch the config flow.

## Configuration
[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)

<img src="https://raw.githubusercontent.com/oxtn/ha-sql-template/main/images/config_flow.png">

## Troubleshooting

* `SQL Query invalid` during integration setup
    * This error occurs during integration setup during the following 2 scenarios:
        * You've entered a query that does not begin with the string `SELECT` (this value *cannot* be within a template string value)
        * Your query is invalid in someway and could not be executed.  Check your `home-assistant.log` for details on the specific error that was encountered.

## Debug Logging

To enable debug logging to see query details during sensor refreshes, ensure the following section is added to your `configuration.yaml` (or if the section already exists, merge in the line for this component):

```yaml
logger:
  default: info
  logs:
    custom_components.sql_template: debug
```
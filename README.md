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

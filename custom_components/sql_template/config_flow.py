"""Adds config flow for SQL integration."""
from __future__ import annotations

import logging
from typing import Any

import sqlalchemy
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session, sessionmaker
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.recorder import CONF_DB_URL, get_instance
from homeassistant.const import CONF_NAME, CONF_UNIT_OF_MEASUREMENT, CONF_VALUE_TEMPLATE
from homeassistant.core import callback, HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.template import Template

from .const import CONF_COLUMN_NAME, CONF_QUERY, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Select SQL Query"): selector.TextSelector(),
        vol.Optional(CONF_DB_URL): selector.TextSelector(),
        vol.Required(CONF_COLUMN_NAME): selector.TextSelector(),
        # Currently vol.Required throws 'Error: Selector not supported in initial form data' on the front end ??
        vol.Optional(CONF_QUERY): selector.TemplateSelector(),
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): selector.TextSelector(),
        vol.Optional(CONF_VALUE_TEMPLATE): selector.TemplateSelector(),
    }
)


def validate_sql_select(value: str) -> str | None:
    """Validate that value is a SQL SELECT query."""
    if not value.lstrip().lower().startswith("select"):
        raise ValueError("Only SELECT queries allowed")
    return value


def validate_query(hass: HomeAssistant, db_url: str, query: str, column: str) -> bool:
    """Validate SQL query."""

    engine = sqlalchemy.create_engine(db_url, future=True)
    sessmaker = scoped_session(sessionmaker(bind=engine, future=True))
    sess: Session = sessmaker()

    query_template: Template = Template(query)
    query_template.hass = hass

    try:
        query_text = query_template.render(parse_result=False)
        _LOGGER.debug(f"Validating query: {query_text}")
        result: Result = sess.execute(sqlalchemy.text(query_text))
    except SQLAlchemyError as error:
        _LOGGER.error(f"Execution error {error}")
        if sess:
            sess.close()
        raise ValueError(error) from error

    for res in result.mappings():
        data = res[column]
        _LOGGER.debug(f"Return value from query: {data}")

    if sess:
        sess.close()

    return True


class SQLConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SQL integration."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SQLOptionsFlowHandler:
        """Get the options flow for this handler."""
        return SQLOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step."""
        errors = {}
        db_url_default = get_instance(self.hass).db_url

        if user_input is not None:
            db_url = user_input.get(CONF_DB_URL, db_url_default)
            query = user_input[CONF_QUERY]
            column = user_input[CONF_COLUMN_NAME]
            uom = user_input.get(CONF_UNIT_OF_MEASUREMENT)
            value_template = user_input.get(CONF_VALUE_TEMPLATE)
            name = user_input[CONF_NAME]

            try:
                validate_sql_select(query)
                await self.hass.async_add_executor_job(
                    validate_query, self.hass, db_url, query, column
                )
            except SQLAlchemyError:
                errors["db_url"] = "db_url_invalid"
            except ValueError:
                errors["query"] = "query_invalid"

            if not errors:
                return self.async_create_entry(
                    title=name,
                    data={},
                    options={
                        CONF_DB_URL: db_url,
                        CONF_QUERY: query,
                        CONF_COLUMN_NAME: column,
                        CONF_UNIT_OF_MEASUREMENT: uom,
                        CONF_VALUE_TEMPLATE: value_template,
                        CONF_NAME: name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class SQLOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle SQL options."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        """Initialize SQL options flow."""
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage SQL options."""
        errors = {}
        db_url_default = get_instance(self.hass).db_url

        if user_input is not None:
            db_url = user_input.get(CONF_DB_URL, db_url_default)
            query = user_input[CONF_QUERY]
            column = user_input[CONF_COLUMN_NAME]
            name = self.entry.options.get(CONF_NAME, self.entry.title)

            try:
                validate_sql_select(query)
                await self.hass.async_add_executor_job(
                    validate_query, self.hass, db_url, query, column
                )
            except SQLAlchemyError:
                errors["db_url"] = "db_url_invalid"
            except ValueError:
                errors["query"] = "query_invalid"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_NAME: name,
                        CONF_DB_URL: db_url,
                        **user_input,
                    },
                )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DB_URL,
                        description={
                            "suggested_value": self.entry.options[CONF_DB_URL]
                        },
                    ): selector.TextSelector(),
                    vol.Required(
                        CONF_QUERY,
                        description={"suggested_value": self.entry.options[CONF_QUERY]},
                    ): selector.TemplateSelector(),
                    vol.Required(
                        CONF_COLUMN_NAME,
                        description={
                            "suggested_value": self.entry.options[CONF_COLUMN_NAME]
                        },
                    ): selector.TextSelector(),
                    vol.Optional(
                        CONF_UNIT_OF_MEASUREMENT,
                        description={
                            "suggested_value": self.entry.options.get(
                                CONF_UNIT_OF_MEASUREMENT
                            )
                        },
                    ): selector.TextSelector(),
                    vol.Optional(
                        CONF_VALUE_TEMPLATE,
                        description={
                            "suggested_value": self.entry.options.get(
                                CONF_VALUE_TEMPLATE
                            )
                        },
                    ): selector.TemplateSelector(),
                }
            ),
            errors=errors,
        )

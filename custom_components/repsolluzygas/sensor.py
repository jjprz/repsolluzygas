"""Platform for sensor integration."""
from .repsol_api import RepsolLuzYGasSensor
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CURRENCY_EURO, POWER_KILO_WATT
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
import requests
import logging

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=120)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    client = RepsolLuzYGasSensor(username, password)
    add_entities([RepsolLuzYGazEntity(client, 'Consumo acumulado', 'consumption', POWER_KILO_WATT, 'mdi:home-lightning-bolt', True, True),
                  RepsolLuzYGazEntity(client, 'Last invoice', 'last_invoice_amount', CURRENCY_EURO, 'mdi:receipt', False, False),
                  RepsolLuzYGazEntity(client, 'Last invoice was paid', 'last_invoice_paid', '', 'mdi:receipt', False, False)], True)

class RepsolLuzYGazEntity(Entity):

    def __init__(self, client, name, variable, unit, icon, is_master, has_attr):
        _LOGGER.debug('Initalizing Entity {}'.format(name))
        self.client = client
        self._name = name
        self.variable = variable
        self.is_master = is_master
        self.has_attr = has_attr
        self.unit = unit
        self._icon = icon
        self._entity_id = 'sensor.repsol_' + name

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Repsol - {}'.format(self._name)

    @property
    def unique_id(self):
        return self._entity_id

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.client is not None:
            data = self.client.data.get(self.variable, 0)
            _LOGGER.debug('{} has value: {}'.format(self._name, data))
        else:
            data = None
            _LOGGER.debug('{} has not value'.format(self._name))
        return data

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.unit

    @property
    def icon(self):
        """Return the icon to display."""
        return self._icon

    def update(self):
        """ This is the updater  """
        if self.is_master:
            self.client.update()

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.client is not None and self.has_attr:
            attr = self.client.data.get('attributes_' + self.variable, 0)
        else:
            attr = None
        return attr

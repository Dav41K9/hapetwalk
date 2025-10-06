"""DataUpdateCoordinator per PetWALK."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

from .const import (
    CONF_INCLUDE_ALL_EVENTS,
    CONF_PORT,
    COORDINATOR_KEY_API_DATA,
    COORDINATOR_KEY_PET_STATUS,
    DEFAULT_INCLUDE_ALL_EVENTS,
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
)
from .petwalk_api import PetwalkClient

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=5)
UPDATE_INTERVAL_PET = timedelta(seconds=120)


class PetwalkCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """PetWALK coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.entry = entry
        self.client = PetwalkClient(
            host=entry.data[CONF_IP_ADDRESS],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        )
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_IP_ADDRESS])},
            name=entry.title,
            manufacturer=MANUFACTURER,
        )

    async def initialize(self) -> None:
        """First setup."""
        try:
            modes = await self.client.get_modes()
            states = await self.client.get_states()
        except Exception as err:
            raise ConfigEntryNotReady from err
        # Aggiorniamo subito i dati
        await self.async_config_entry_first_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self._device_info

    async def set_mode(self, key: str, value: bool) -> None:
        """Change single mode."""
        await self.client.set_modes(**{key: value})
        await self.async_request_refresh()

    async def set_state(self, key: str, value: bool) -> None:
        """Change door/system state."""
        if key == "door":
            await self.client.set_states(door="open" if value else "closed")
        elif key == "system":
            await self.client.set_states(system="on" if value else "off")
        else:
            _LOGGER.warning("Unknown state key %s", key)
        await self.async_request_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data."""
        try:
            async with asyncio.timeout(10):
                data = self.data or {}
                data[COORDINATOR_KEY_API_DATA] = {
                    **await self.client.get_modes(),
                    **await self.client.get_states(),
                }
                # Pet status mock – sostituirai con chiamata reale quando avrai l’endpoint
                if COORDINATOR_KEY_PET_STATUS not in data:
                    data[COORDINATOR_KEY_PET_STATUS] = {}
                return data
        except Exception as err:
            raise UpdateFailed(f"Errore comunicazione API: {err}") from err
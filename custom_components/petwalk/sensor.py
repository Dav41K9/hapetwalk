"""Sensor per PetWALK."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant import config_entries
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_INCLUDE_ALL_EVENTS, COORDINATOR_KEY_PET_STATUS, DOMAIN, NAME
from .coordinator import PetwalkCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up sensor platform."""
    coordinator: PetwalkCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    if not config_entry.data.get(CONF_INCLUDE_ALL_EVENTS, False):
        return

    entities = []
    for pet in coordinator.pets:
        if not pet.name:
            continue
        entity_id = f"pet_{(pet.species or 'unknown').lower()}_{pet.name.lower()}"
        entities.append(
            PetwalkTimestampSensor(
                coordinator,
                pet_id=pet.id,
                species=pet.species,
                entity_name=f"{pet.name} last event",
                entity_id=entity_id,
            )
        )
    add_entities(entities, True)


class PetwalkTimestampSensor(CoordinatorEntity[PetwalkCoordinator], SensorEntity):
    """Pet timestamp sensor."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: PetwalkCoordinator,
        pet_id: str,
        species: str | None,
        entity_name: str | None,
        entity_id: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self._pet_id = pet_id
        self._attr_name = f"{NAME} {coordinator.device_info['name']} {entity_name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.device_info['name']}_{entity_id}"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = {
            "cat": "mdi:cat",
            "dog": "mdi:dog",
        }.get((species or "").lower(), "mdi:paw")

    @property
    def native_value(self) -> datetime | None:
        """Return last event time."""
        event = self.coordinator.data.get(COORDINATOR_KEY_PET_STATUS, {}).get(self._pet_id)
        return getattr(event, "date", None) if event else None
"""Device tracker per PetWALK."""
from __future__ import annotations

import logging

from homeassistant import config_entries
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.const import STATE_HOME, STATE_NOT_HOME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR_KEY_PET_STATUS, DOMAIN, NAME
from .coordinator import PetwalkCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up device tracker."""
    coordinator: PetwalkCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Pet mock – quando avrai l’endpoint reale sostituisci
    entities = []
    for pet in coordinator.pets:
        if pet.unknown or not pet.name:
            continue
        entity_id = f"pet_{(pet.species or 'unknown').lower()}_{pet.name.lower()}"
        entities.append(
            PetwalkDeviceTracker(
                coordinator,
                pet_id=pet.id,
                species=pet.species,
                entity_name=pet.name,
                entity_id=entity_id,
            )
        )
    add_entities(entities, True)


class PetwalkDeviceTracker(CoordinatorEntity[PetwalkCoordinator], TrackerEntity):
    """Pet device tracker."""

    _attr_source_type = SourceType.ROUTER

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
    def location_name(self) -> str:
        """Return state."""
        data = self.coordinator.data.get(COORDINATOR_KEY_PET_STATUS, {})
        event = data.get(self._pet_id)
        if not event:
            return STATE_NOT_HOME
        # direction mock – usa l’enum reale quando avrai l’endpoint
        return STATE_HOME if getattr(event, "direction", None) == "in" else STATE_NOT_HOME
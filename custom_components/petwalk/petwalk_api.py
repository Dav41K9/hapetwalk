"""Async PetWALK REST client."""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientSession, BasicAuth, ClientTimeout, ClientResponseError

_LOGGER = logging.getLogger(__name__)


class PetwalkClient:
    """Minimal async client for PetWALK local REST API."""

    def __init__(
        self, host: str, username: str, password: str, port: int = 8080
    ) -> None:
        """Initialize."""
        self._base_url = f"http://{host}:{port}"
        self._auth = BasicAuth(username, password)
        self._timeout = ClientTimeout(total=10)

    async def get_modes(self) -> dict[str, bool]:
        """Return active modes."""
        async with ClientSession(auth=self._auth, timeout=self._timeout) as session:
            async with session.get(f"{self._base_url}/modes") as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_states(self) -> dict[str, str]:
        """Return current states (door, system)."""
        async with ClientSession(auth=self._auth, timeout=self._timeout) as session:
            async with session.get(f"{self._base_url}/states") as resp:
                resp.raise_for_status()
                return await resp.json()

    async def set_modes(self, **kwargs: bool) -> None:
        """Change modes (brightnessSensor, motion_in, ...)."""
        async with ClientSession(auth=self._auth, timeout=self._timeout) as session:
            async with session.put(f"{self._base_url}/modes", json=kwargs) as resp:
                resp.raise_for_status()

    async def set_states(self, *, door: str | None = None, system: str | None = None) -> None:
        """Change states (door: open/closed, system: on/off)."""
        payload = {}
        if door is not None:
            payload["door"] = door
        if system is not None:
            payload["system"] = system
        async with ClientSession(auth=self._auth, timeout=self._timeout) as session:
            async with session.put(f"{self._base_url}/states", json=payload) as resp:
                resp.raise_for_status()

    async def close(self) -> None:
        """Close underlying session (opzionale, aiohttp lo fa da sé)."""
        pass
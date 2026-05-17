from __future__ import annotations

from typing import Any

from .const import DEFAULT_API_BASE_URL


class BrightSkyApiError(Exception):
    """Raised when Bright Sky returns an error or unusable payload."""


class BrightSkyClient:
    def __init__(
        self,
        session: Any,
        *,
        base_url: str = DEFAULT_API_BASE_URL,
        timeout: int = 20,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch_current_weather(
        self,
        *,
        latitude: float,
        longitude: float,
        timezone: str,
        max_distance: int | None,
    ) -> dict[str, Any]:
        return await self._get(
            "current_weather",
            {
                "lat": latitude,
                "lon": longitude,
                "tz": timezone,
                "units": "dwd",
                "max_dist": max_distance,
            },
        )

    async def fetch_weather(
        self,
        *,
        latitude: float,
        longitude: float,
        start: str,
        end: str,
        timezone: str,
        max_distance: int | None,
    ) -> dict[str, Any]:
        return await self._get(
            "weather",
            {
                "lat": latitude,
                "lon": longitude,
                "date": start,
                "last_date": end,
                "tz": timezone,
                "units": "dwd",
                "max_dist": max_distance,
            },
        )

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        clean_params = {
            key: value for key, value in params.items() if value is not None
        }
        url = f"{self._base_url}/{path}"
        try:
            async with self._session.get(
                url, params=clean_params, timeout=self._timeout
            ) as response:
                if response.status >= 400:
                    detail = await response.text()
                    raise BrightSkyApiError(
                        "Bright Sky request failed with HTTP "
                        f"{response.status}: {detail}"
                    )
                payload = await response.json()
        except TimeoutError as err:
            raise BrightSkyApiError("Bright Sky request timed out") from err
        except BrightSkyApiError:
            raise
        except Exception as err:
            raise BrightSkyApiError(f"Bright Sky request failed: {err}") from err

        if not isinstance(payload, dict):
            raise BrightSkyApiError("Bright Sky returned a non-object response")
        return payload

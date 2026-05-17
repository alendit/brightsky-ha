from typing import Any

import pytest

from custom_components.brightsky.api import BrightSkyApiError, BrightSkyClient


class FakeResponse:
    def __init__(
        self, status: int, payload: dict[str, Any], text: str = ""
    ) -> None:
        self.status = status
        self._payload = payload
        self._text = text

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def json(self) -> dict[str, Any]:
        return self._payload

    async def text(self) -> str:
        return self._text


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get(
        self, url: str, *, params: dict[str, Any], timeout: int
    ) -> FakeResponse:
        self.calls.append((url, {"params": params, "timeout": timeout}))
        return self.response


@pytest.mark.asyncio
async def test_fetch_weather_builds_expected_request() -> None:
    session = FakeSession(FakeResponse(200, {"weather": [], "sources": []}))
    client = BrightSkyClient(session, base_url="https://example.test", timeout=7)

    payload = await client.fetch_weather(
        latitude=52.0,
        longitude=7.6,
        start="2026-05-17T00:00:00+02:00",
        end="2026-05-18T00:00:00+02:00",
        timezone="Europe/Berlin",
        max_distance=40000,
    )

    assert payload == {"weather": [], "sources": []}
    assert session.calls == [
        (
            "https://example.test/weather",
            {
                "params": {
                    "lat": 52.0,
                    "lon": 7.6,
                    "date": "2026-05-17T00:00:00+02:00",
                    "last_date": "2026-05-18T00:00:00+02:00",
                    "tz": "Europe/Berlin",
                    "units": "dwd",
                    "max_dist": 40000,
                },
                "timeout": 7,
            },
        )
    ]


@pytest.mark.asyncio
async def test_fetch_current_weather_omits_unset_optional_params() -> None:
    session = FakeSession(FakeResponse(200, {"weather": {}, "sources": []}))
    client = BrightSkyClient(session, base_url="https://example.test")

    await client.fetch_current_weather(
        latitude=52.0,
        longitude=7.6,
        timezone="Europe/Berlin",
        max_distance=None,
    )

    assert session.calls[0][1]["params"] == {
        "lat": 52.0,
        "lon": 7.6,
        "tz": "Europe/Berlin",
        "units": "dwd",
    }


@pytest.mark.asyncio
async def test_raises_api_error_for_non_success_response() -> None:
    session = FakeSession(FakeResponse(503, {}, "maintenance"))
    client = BrightSkyClient(session, base_url="https://example.test")

    with pytest.raises(BrightSkyApiError, match="503"):
        await client.fetch_current_weather(
            latitude=52.0,
            longitude=7.6,
            timezone="Europe/Berlin",
            max_distance=None,
        )

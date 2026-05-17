from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

WeatherRecord = dict[str, Any]
SourceRecord = dict[str, Any]
ForecastRecord = dict[str, Any]


@dataclass(frozen=True)
class BrightSkyData:
    current: WeatherRecord
    current_sources: list[SourceRecord]
    hourly_records: list[WeatherRecord]
    forecast_sources: list[SourceRecord]
    hourly_forecast: list[ForecastRecord] = field(default_factory=list)
    daily_forecast: list[ForecastRecord] = field(default_factory=list)

    @property
    def primary_source(self) -> SourceRecord | None:
        source_id = self.current.get("source_id")
        for source in self.current_sources + self.forecast_sources:
            if source.get("id") == source_id:
                return source
        if self.current_sources:
            return self.current_sources[0]
        if self.forecast_sources:
            return self.forecast_sources[0]
        return None

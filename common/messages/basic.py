from dataclasses import dataclass

from common.messages import End, RecordType


@dataclass()
class BasicStation:
    record_type = RecordType.STATION
    code: str
    name: str
    latitude: float | None
    longitude: float | None
    year: int
    city: str


@dataclass()
class BasicTrip:
    record_type = RecordType.TRIP
    start_date: str
    end_date: str
    end_station_code: str
    duration_sec: float
    year: int
    city: str


@dataclass()
class BasicWeather:
    record_type = RecordType.WEATHER
    date: str
    precipitation: float
    city: str


BasicRecord = BasicStation | BasicTrip | BasicWeather | End

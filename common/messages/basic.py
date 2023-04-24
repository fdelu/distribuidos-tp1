from dataclasses import dataclass

from common.messages import End, RecordType


@dataclass()
class BasicStation:
    code: str
    name: str
    latitude: float | None
    longitude: float | None
    year: str
    city: str

    def get_routing_key(self) -> str:
        return RecordType.STATION


@dataclass()
class BasicTrip:
    start_date: str
    duration_sec: float
    city: str
    start_station_code: str
    end_station_code: str
    year: str

    def get_routing_key(self) -> str:
        return RecordType.TRIP


@dataclass()
class BasicWeather:
    date: str
    precipitation: float
    city: str

    def get_routing_key(self) -> str:
        return RecordType.WEATHER


BasicRecord = BasicStation | BasicTrip | BasicWeather | End

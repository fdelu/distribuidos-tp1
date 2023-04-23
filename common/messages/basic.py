from dataclasses import dataclass


@dataclass()
class BasicStation:
    code: str
    name: str
    latitude: float | None
    longitude: float | None
    year: int
    city: str


@dataclass()
class BasicTrip:
    start_date: str
    end_date: str
    end_station_code: str
    duration_sec: float
    year: int
    city: str


@dataclass()
class BasicWeather:
    date: str
    precipitation: float
    city: str


BasicRecord = BasicStation | BasicTrip | BasicWeather

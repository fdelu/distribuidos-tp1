from dataclasses import dataclass


@dataclass()
class Station:
    code: str
    name: str
    latitude: float
    longitude: float
    year: int


@dataclass()
class Trip:
    start_date: str
    start_station_code: str
    end_date: str
    end_station_code: str
    duration_sec: int
    is_member: bool
    year: int


@dataclass()
class Weather:
    date: str
    precipitation: float


Record = Station | Trip | Weather

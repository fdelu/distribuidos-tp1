from dataclasses import dataclass


@dataclass()
class Station:
    code: str
    name: str
    latitude: float | None
    longitude: float | None
    year: int
    city: str


@dataclass()
class Trip:
    start_date: str
    start_station_code: str
    end_date: str
    end_station_code: str
    duration_sec: float
    is_member: bool
    year: int
    city: str


@dataclass()
class Weather:
    date: str
    precipitation: float
    city: str


BasicRecord = Station | Trip | Weather


@dataclass()
class Batch:
    values: list[BasicRecord]


class End:
    pass


Record = BasicRecord | Batch | End

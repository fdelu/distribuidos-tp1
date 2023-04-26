from typing import Protocol, TypeVar
from dataclasses import dataclass

from common.messages import End, RecordType

T = TypeVar("T", covariant=True)


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

    def be_handled_by(self, handler: "BasicRecordHandler[T]") -> T:
        return handler.handle_station(self)


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

    def be_handled_by(self, handler: "BasicRecordHandler[T]") -> T:
        return handler.handle_trip(self)


@dataclass()
class BasicWeather:
    date: str
    precipitation: float
    city: str

    def get_routing_key(self) -> str:
        return RecordType.WEATHER

    def be_handled_by(self, handler: "BasicRecordHandler[T]") -> T:
        return handler.handle_weather(self)


@dataclass
class TripsStart:
    def get_routing_key(self) -> str:
        return RecordType.TRIPS_START

    def be_handled_by(self, handler: "BasicRecordHandler[T]") -> T:
        return handler.handle_trips_start()


class BasicRecordHandler(Protocol[T]):
    def handle_weather(self, weather: BasicWeather) -> T:
        ...

    def handle_station(self, station: BasicStation) -> T:
        ...

    def handle_trip(self, trip: BasicTrip) -> T:
        ...

    def handle_trips_start(self) -> T:
        ...


BasicRecord = BasicStation | BasicTrip | BasicWeather | TripsStart | End

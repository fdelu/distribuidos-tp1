from typing import Protocol, TypeVar
from dataclasses import dataclass

from common.messages import End, RecordType

T = TypeVar("T", covariant=True)
U = TypeVar("U", contravariant=True)


@dataclass
class StationInfo:
    name: str
    latitude: float | None
    longitude: float | None


@dataclass()
class JoinedRainTrip:
    city: str
    start_date: str
    duration_sec: float

    def be_handled_by(self, handler: "JoinedRecordHandler[T, JoinedRainTrip]") -> T:
        return handler.handle_joined(self)

    def get_routing_key(self):
        return RecordType.TRIP


JoinedRainRecord = JoinedRainTrip | End


@dataclass
class JoinedCityTrip:
    def be_handled_by(self, handler: "JoinedRecordHandler[T, JoinedCityTrip]") -> T:
        return handler.handle_joined(self)

    def get_routing_key(self):
        return RecordType.TRIP


JoinedCityRecord = JoinedCityTrip | End


class JoinedRecordHandler(Protocol[T, U]):
    def handle_joined(self, trip: U) -> T:
        ...


JoinedRecord = JoinedRainRecord | JoinedCityRecord
GenericJoinedRecord = TypeVar(
    "GenericJoinedRecord", JoinedRainTrip, JoinedCityTrip, contravariant=True
)

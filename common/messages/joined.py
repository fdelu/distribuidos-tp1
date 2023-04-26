from typing import Protocol, TypeVar
from dataclasses import dataclass

from common.messages import End, RecordType

T = TypeVar("T", covariant=True)


@dataclass
class StationInfo:
    name: str
    latitude: float | None
    longitude: float | None


@dataclass()
class JoinedTrip:
    start_date: str
    start_station: StationInfo
    end_station: StationInfo
    rained: bool
    duration_sec: float
    year: str
    city: str

    def get_routing_key(self) -> str:
        return ".".join(
            str(x).lower() for x in (RecordType.TRIP, self.city, self.year, self.rained)
        )

    def be_handled_by(self, handler: "JoinedRecordHandler[T]") -> T:
        return handler.handle_trip(self)


class JoinedRecordHandler(Protocol[T]):
    def handle_trip(self, trip: JoinedTrip) -> T:
        ...


JoinedRecord = JoinedTrip | End

from dataclasses import dataclass

from common.messages import End, RecordType


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


JoinedRecord = JoinedTrip | End

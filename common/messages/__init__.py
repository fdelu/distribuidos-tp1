from typing import Protocol, TypeVar
from enum import StrEnum

T = TypeVar("T", covariant=True)


class RecordType(StrEnum):
    STATION = "station"
    TRIP = "trip"
    WEATHER = "weather"
    RAW_BATCH = "raw_batch"
    TRIPS_START = "trips_start"
    END = "end"


class End:
    def get_routing_key(self) -> str:
        return RecordType.END

    def be_handled_by(self, handler: "EndHandler[T]") -> T:
        return handler.handle_end()


class EndHandler(Protocol[T]):
    def handle_end(self) -> T:
        ...

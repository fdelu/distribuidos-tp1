from enum import StrEnum


class RecordType(StrEnum):
    STATION = "station"
    TRIP = "trip"
    WEATHER = "weather"
    END = "end"


class End:
    def get_routing_key(self) -> str:
        return RecordType.END

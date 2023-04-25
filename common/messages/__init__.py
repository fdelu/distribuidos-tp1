from enum import StrEnum


class RecordType(StrEnum):
    STATION = "station"
    TRIP = "trip"
    WEATHER = "weather"
    RAW_BATCH = "raw_batch"
    END = "end"


class End:
    def get_routing_key(self) -> str:
        return RecordType.END

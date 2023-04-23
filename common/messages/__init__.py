from enum import StrEnum


class RecordType(StrEnum):
    STATION = "station"
    TRIP = "trip"
    WEATHER = "weather"
    End = "end"


class End:
    record_type = RecordType.End

from dataclasses import dataclass
from enum import StrEnum

HEADER_SPLIT_CHAR = "|"
ATTRS_SPLIT_CHAR = ","
RECORDS_SPLIT_CHAR = "\n"


class RecordType(StrEnum):
    STATION = "station"
    TRIP = "trip"
    WEATHER = "weather"
    End = "end"


@dataclass
class RawRecord:
    record_type: RecordType
    city: str
    headers: list[str]
    lines: list[str]

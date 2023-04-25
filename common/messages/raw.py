from dataclasses import dataclass

from common.messages import RecordType

HEADER_SPLIT_CHAR = "|"
ATTRS_SPLIT_CHAR = ","
RECORDS_SPLIT_CHAR = "\n"


@dataclass
class RawRecord:
    record_type: RecordType
    city: str
    headers: list[str]
    lines: list[str]

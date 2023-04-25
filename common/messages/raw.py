from dataclasses import dataclass

from common.messages import End, RecordType

HEADER_SPLIT_CHAR = "|"
ATTRS_SPLIT_CHAR = ","
RECORDS_SPLIT_CHAR = "\n"


@dataclass
class RawBatch:
    record_type: RecordType
    city: str
    headers: str
    lines: list[str]

    def get_routing_key(self) -> str:
        return RecordType.RAW_BATCH


RawRecord = RawBatch | End

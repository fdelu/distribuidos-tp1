from common.messages.basic import BasicRecord, BasicStation, BasicTrip, BasicWeather
from common.messages.raw import ATTRS_SPLIT_CHAR, RawRecord, RecordType
import types
from typing import Type, get_type_hints, get_args, Any

MAX_FUTURES = 5000


def __get_type(record_type: RecordType) -> Type[BasicRecord]:
    if record_type == RecordType.STATION:
        return BasicStation
    elif record_type == RecordType.TRIP:
        return BasicTrip
    elif record_type == RecordType.WEATHER:
        return BasicWeather
    else:
        raise ValueError(f"Unknown record type {record_type}")


def parse_rows(record: RawRecord) -> list[BasicRecord]:
    type = __get_type(record.record_type)
    type_hints = get_type_hints(type.__init__)
    index = {x: i for i, x in enumerate(record.headers)}
    out = []

    rows = (x.strip().split(ATTRS_SPLIT_CHAR) for x in record.lines)
    for row in rows:
        args: list[Any] = []
        for name, type_hint in type_hints.items():
            if name == "city":
                args.append(record.city)
                continue

            value = row[index[name]]

            if isinstance(type_hint, types.UnionType):
                if value == "" and types.NoneType in get_args(type_hint):
                    args.append(None)
                    continue
                type_hint = get_args(type)[0]

            if type_hint == bool:
                args.append(value == "1")
            elif type_hint in (int, float):
                args.append(type_hint(value))
            else:
                args.append(value)
        out.append(type(*args))
    return out

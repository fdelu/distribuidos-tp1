from common.messages import RecordType
from common.messages.basic import BasicRecord, BasicStation, BasicTrip, BasicWeather
from common.messages.raw import ATTRS_SPLIT_CHAR, RawRecord
from datetime import date, timedelta


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def parse_station(row: list[str], index: dict[str, int], city: str) -> BasicStation:
    return BasicStation(
        code=row[index["code"]],
        name=row[index["name"]],
        latitude=parse_optional_float(row[index["latitude"]]),
        longitude=parse_optional_float(row[index["longitude"]]),
        year=int(row[index["yearid"]]),
        city=city,
    )


def parse_trip(row: list[str], index: dict[str, int], city: str) -> BasicTrip:
    return BasicTrip(
        start_date=row[index["start_date"]],
        end_date=row[index["end_date"]],
        end_station_code=row[index["end_station_code"]],
        duration_sec=float(row[index["duration_sec"]]),
        year=int(row[index["yearid"]]),
        city=city,
    )


def parse_weather(row: list[str], index: dict[str, int], city: str) -> BasicWeather:
    day_minus_1 = date.fromisoformat(row[index["date"]]) - timedelta(days=1)
    return BasicWeather(
        date=day_minus_1.isoformat(),
        precipitation=float(row[index["precipitation"]]),
        city=city,
    )


def parse_rows(record: RawRecord) -> list[BasicRecord]:
    index = {x: i for i, x in enumerate(record.headers)}
    rows = (x.split(ATTRS_SPLIT_CHAR) for x in record.lines)
    if record.record_type == RecordType.STATION:
        return [parse_station(row, index, record.city) for row in rows]
    if record.record_type == RecordType.TRIP:
        return [parse_trip(row, index, record.city) for row in rows]
    if record.record_type == RecordType.WEATHER:
        return [parse_weather(row, index, record.city) for row in rows]
    raise ValueError(f"Unknown record type: {record.record_type}")

import logging
import zmq
from enum import StrEnum
from common.messages.record import BasicRecord, End, Record, Station, Weather
from common.serde import deserialize
from common.log import setup_logs

setup_logs()
PORT = "5555"

Amounts = dict[str, dict[str, int]]  # dict[record_type, dict[city, count]


class Phase(StrEnum):
    WEATHER_STATIONS = "weather_stations"
    TRIPS = "trips"
    END = "end"


def process_record(record: BasicRecord, amounts: Amounts, phase: Phase) -> Phase:
    if isinstance(record, Weather):
        if phase != Phase.WEATHER_STATIONS:
            logging.error(f"Received weather record after phase {phase} started")
        amounts_weather = amounts["weather"]
        amounts_weather[record.city] = amounts_weather.get(record.city, 0) + 1
    elif isinstance(record, Station):
        if phase != Phase.WEATHER_STATIONS:
            logging.error(f"Received station record after phase {phase} started")
        amounts_stations = amounts["stations"]
        amounts_stations[record.city] = amounts_stations.get(record.city, 0) + 1
    else:  # Trip
        if phase == Phase.WEATHER_STATIONS:
            logging.info(f"Phase {phase} | Expecting trip records")
            phase = Phase.TRIPS
        amounts_trips = amounts["trips"]
        amounts_trips[record.city] = amounts_trips.get(record.city, 0) + 1

    return phase


def main():
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(f"tcp://*:{PORT}")

    amounts: Amounts = {
        "stations": {},
        "weather": {},
        "trips": {},
    }

    phase = Phase.WEATHER_STATIONS
    logging.info(f"Phase {phase} | Expecting weather and station records")
    while phase != Phase.END:
        msg = socket.recv()
        record: Record = deserialize(Record, msg.decode())
        if isinstance(record, list):
            for item in record:
                phase = process_record(item, amounts, phase)
        elif isinstance(record, End):
            phase = Phase.END
        else:
            phase = process_record(record, amounts, phase)

    logging.info(
        "Finished receiving records. Printing results:\n"
        + "\n".join(f"{type}: {', '.join(f'{x}={y}' for x,y in amounts_type.items())}")
        for type, amounts_type in amounts.items()
    )


main()

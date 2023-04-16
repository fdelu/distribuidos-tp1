#!/usr/bin/python3
import logging
import types
from typing import Any, Type, TypeVar, get_type_hints
import zmq
import os
import csv
from common.log import setup_logs
from common.serde import serialize
from common.messages.record import (
    BasicRecord,
    Batch,
    End,
    Station,
    Record,
    Trip,
    Weather,
)

setup_logs()
DATA_PATH = "/tmp/data"
IP = "input"
PORT = "5555"
BATCH_SIZE = 50
T = TypeVar("T", Station, Trip, Weather)


def deserialize_row(row: list[str], type: Type[T]) -> T:
    type_hints = get_type_hints(type).values()
    if len(row) < len(type_hints):
        raise ValueError(
            f"Expected {len(type_hints)} values but got {len(row)} in {row} for type"
            f" {type}"
        )
    args: list[Any] = []
    for value, type_hint in zip(row, type_hints):
        if isinstance(type_hint, types.UnionType):
            # It's the float | None for the missing coordinates
            if value == "":
                args.append(None)
                continue
            else:
                type_hint = type_hint.__args__[0]
        if type_hint == bool:
            args.append(value == "1")
        elif type_hint in (int, float):
            args.append(type_hint(value))
        else:
            args.append(value)
    return type(*args)


def send_from_file(
    socket: zmq.Socket,
    city: str,
    file: str,
    record_type: Type[T],
    keep_only_first: int | None = None,
) -> int:
    count = 0
    batch: list[BasicRecord] = []
    with open(f"{DATA_PATH}/{city}/{file}.csv") as f:
        reader = csv.reader(f)
        next(reader)  # skip header

        for row in reader:
            if keep_only_first is not None:
                row = row[:keep_only_first]
            row.append(city)
            try:
                station = deserialize_row(row, record_type)
            except Exception:
                logging.exception(f"Failed to deserialize {row} for {record_type}")
                continue
            batch.append(station)
            count += 1
            if len(batch) == BATCH_SIZE:
                socket.send(serialize(Batch(batch), set_type=Record).encode())
                batch = []
    if batch:
        socket.send(serialize(Batch(batch), set_type=Record).encode())
    return count


def main():
    context = zmq.Context()

    #  Socket to talk to server
    logging.info("Connecting to the server")
    socket = context.socket(zmq.PAIR)
    socket.connect(f"tcp://{IP}:{PORT}")

    cities = os.listdir(DATA_PATH)

    logging.info("Phase 1 | Sending stations and weather")
    for city in cities:
        amount = send_from_file(socket, city, "stations", Station)
        logging.info(f"Sent {amount} station records for {city}")

    for city in cities:
        amount = send_from_file(socket, city, "weather", Weather, keep_only_first=2)
        logging.info(f"Sent {amount} weather records for {city}")

    logging.info("Phase 2 | Sending trips")
    for city in cities:
        logging.info(f"Sending trips for {city}")
        amount = send_from_file(socket, city, "trips", Trip)
        logging.info(f"Sent {amount} trip records for {city}")

    socket.send(serialize(End(), set_type=Record).encode())


main()

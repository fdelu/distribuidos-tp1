#!/usr/bin/python3
import logging
from typing import Type, TypeVar, get_type_hints
import zmq
import os
import csv
from common.log import setup_logs
from common.serde import serialize
from common.messages.record import Station, Record, Trip, Weather

setup_logs()
DATA_PATH = "/tmp/data"
T = TypeVar("T")


def deserialize_row(row: list[str], type: Type[T]) -> T:
    type_hints = get_type_hints(type).values()
    if len(row) < len(type_hints):
        raise ValueError(
            f"Expected {len(type_hints)} values but got {len(row)} in {row} for type"
            f" {type}"
        )
    output = []
    for value, type_hint in zip(row, type_hints):
        typed_value = type_hint(value)
        output.append(typed_value)
    return type(*output)


def send_from_file(socket: zmq.Socket, city: str, file: str, type: Type[T]):
    with open(f"{DATA_PATH}/{city}/{file}.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            station: T = deserialize_row(row, type)
            socket.send_string(serialize(station, set_type=Record))


def main():
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to the server")
    socket = context.socket(zmq.REQ)

    socket.connect("tcp://input:5555")

    # print contents of directory DATA_PATH
    cities = os.listdir(DATA_PATH)

    for city in cities:
        logging.info(f"Sending stations and weather for {city}")
        send_from_file(socket, city, "stations", Station)
        send_from_file(socket, city, "weather", Weather)

    for city in cities:
        logging.info(f"Sending trips for {city}")
        send_from_file(socket, city, "trips", Trip)


main()

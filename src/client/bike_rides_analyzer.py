import json
import logging
from typing import Any
import zmq

from shared.messages import RecordType
from shared.messages import Phase, SplitChar, StatType
from .config import Config


class BikeRidesAnalyzer:
    phase: Phase
    config: Config

    context: zmq.Context
    input_socket: zmq.Socket | None = None
    output_socket: zmq.Socket | None = None

    def __init__(self, config: Config):
        self.config = config
        self.phase = Phase.StationsWeather
        self.context = zmq.Context()

    def send_stations(self, city: str, file_path: str):
        logging.info(f"Sending stations for {city}")
        if self.phase != Phase.StationsWeather:
            raise ValueError(f"Can't send stations in this phase: {self.phase}")

        self.__send_from_file(city, file_path, RecordType.STATION)

    def send_weather(self, city: str, file_path: str):
        logging.info(f"Sending weather for {city}")
        if self.phase != Phase.StationsWeather:
            raise ValueError(f"Can't send weather in this phase: {self.phase}")

        self.__send_from_file(city, file_path, RecordType.WEATHER)

    def send_trips(self, city: str, file_path: str):
        logging.info(f"Sending trips for {city}")
        if self.phase == Phase.StationsWeather:
            self.phase = Phase.Trips

        if self.phase != Phase.Trips:
            raise ValueError(f"Can't send trips in this phase: {self.phase}")

        self.__send_from_file(city, file_path, RecordType.TRIP)

    def process_results(self):
        if self.phase != Phase.Trips:
            raise ValueError(f"Can't process results in this phase: {self.phase}")
        if self.input_socket is None:
            self.input_socket = self.__connect_input_socket()
        self.phase = Phase.End
        self.input_socket.send_string(RecordType.END)

    def get_rain_averages(self) -> dict[str, float]:
        return self.__get_stat(StatType.RAIN)

    def __connect_input_socket(self) -> zmq.Socket:
        input_socket = self.context.socket(zmq.PAIR)
        logging.info(f"Connecting to input on {self.config.input_address}")
        input_socket.connect(self.config.input_address)
        return input_socket

    def __connect_output_socket(self) -> zmq.Socket:
        output_socket = self.context.socket(zmq.REQ)
        logging.info(f"Connecting to output on {self.config.output_address}")
        output_socket.connect(self.config.output_address)
        return output_socket

    def __get_stat(self, stat: StatType) -> Any:
        if self.phase != Phase.End:
            raise ValueError(f"Can't get stat in this phase: {self.phase}")
        if self.output_socket is None:
            self.output_socket = self.__connect_output_socket()

        self.output_socket.send_string(stat)
        logging.info(f"Requesting stat {stat}")
        response = self.output_socket.recv_string()
        logging.info(f"Stat {stat} received")
        return json.loads(response)

    def __send_from_file(self, city: str, path: str, type: RecordType) -> int:
        count = -1  # don't count the header
        batch = []

        if self.input_socket is None:
            self.input_socket = self.__connect_input_socket()

        self.input_socket.send_string(f"{type}{SplitChar.HEADER}{city}")

        with open(path) as f:
            lines = (x.strip() for x in f.readlines())
            for line in lines:
                batch.append(line)
                count += 1
                if len(batch) == self.config.batch_size:
                    self.input_socket.send_string(SplitChar.RECORDS.join(batch))
                    batch = []

        if batch:
            self.input_socket.send_string(SplitChar.RECORDS.join(batch))

        self.input_socket.send_string(RecordType.END)
        logging.info(f"{self.phase} | {city} | Sent {count} {type} records")
        return count

import json
import logging
from typing import Any
import zmq

from common.log import setup_logs
from common.messages import RecordType
from common.phase import Phase
from common.messages.raw import RECORDS_SPLIT_CHAR, HEADER_SPLIT_CHAR
from common.messages.stats import StatType

from config import Config


class BikeRidesAnalyzer:
    phase: Phase
    config: Config

    def __init__(self):
        self.phase = Phase.StationsWeather
        self.config = Config()
        setup_logs(self.config.log_level)

        context = zmq.Context()
        self.input_socket = context.socket(zmq.PAIR)
        self.input_socket.connect(self.config.input_address)
        self.output_socket = context.socket(zmq.REQ)
        self.output_socket.connect(self.config.output_address)

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
        self.phase = Phase.End
        self.input_socket.send_string(RecordType.END)

    def get_rain_averages(self) -> dict[str, float]:
        return self.__get_stat(StatType.RAIN)

    def __get_stat(self, stat: StatType) -> Any:
        if self.phase != Phase.End:
            raise ValueError(f"Can't get stat in this phase: {self.phase}")

        logging.info(f"Requesting stat {stat}")
        self.output_socket.send_string(stat)
        response = self.output_socket.recv_string()
        logging.info(f"Stat {stat} received")
        return json.loads(response)

    def __send_from_file(self, city: str, path: str, type: RecordType) -> int:
        count = -1  # don't count the header
        batch = []

        self.input_socket.send_string(f"{type}{HEADER_SPLIT_CHAR}{city}")

        with open(path) as f:
            lines = (x.strip() for x in f.readlines())
            for line in lines:
                batch.append(line)
                count += 1
                if len(batch) == self.config.batch_size:
                    self.input_socket.send_string(RECORDS_SPLIT_CHAR.join(batch))
                    batch = []

        if batch:
            self.input_socket.send_string(RECORDS_SPLIT_CHAR.join(batch))

        self.input_socket.send_string(RecordType.END)
        logging.info(f"{self.phase} | {city} | Sent {count} {type} records")
        return count

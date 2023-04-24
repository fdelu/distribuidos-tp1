import logging
import zmq

from common.log import setup_logs
from common.messages import RecordType
from common.phase import Phase
from common.messages.raw import RECORDS_SPLIT_CHAR, HEADER_SPLIT_CHAR

from config import Config


class BikeRidesAnalyzer:
    context: zmq.Context
    socket: zmq.Socket
    phase: Phase
    config: Config

    def __init__(self):
        self.phase = Phase.StationsWeather
        self.config = Config()
        setup_logs(self.config.log_level)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect(self.config.input_address)

    def __send_from_file(self, city: str, path: str, type: RecordType) -> int:
        count = -1  # don't count the header
        batch = []

        self.socket.send(f"{type}{HEADER_SPLIT_CHAR}{city}".encode())

        with open(path) as f:
            lines = (x.strip() for x in f.readlines())
            for line in lines:
                batch.append(line)
                count += 1
                if len(batch) == self.config.batch_size:
                    self.socket.send(RECORDS_SPLIT_CHAR.join(batch).encode())
                    batch = []

        if batch:
            self.socket.send(RECORDS_SPLIT_CHAR.join(batch).encode())

        self.socket.send(RecordType.END.encode())
        logging.info(f"{self.phase} | {city} | Sent {count} {type} records")
        return count

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

    def get_results(self):
        if self.phase != Phase.Trips:
            raise ValueError(f"Can't get results in this phase: {self.phase}")
        self.phase = Phase.End
        self.socket.send(RecordType.END.encode())

        raise NotImplementedError("Not implemented yet")

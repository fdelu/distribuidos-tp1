import logging
import zmq

from common.phase import Phase
from common.messages.raw import (
    ATTRS_SPLIT_CHAR,
    HEADER_SPLIT_CHAR,
    RECORDS_SPLIT_CHAR,
    RawRecord,
    RecordType,
)
from common.serde import serialize

from config import Config
from input.communication import SystemCommunication


class ClientHandler:
    config: Config
    phase: Phase
    socket: zmq.Socket

    def __init__(self, config: Config, socket: zmq.Socket):
        self.config = config
        self.phase = Phase.StationsWeather
        self.socket = socket
        self.comms = SystemCommunication(config)

    def __send_record(self, record_type: RecordType, city: str):
        pass

    def __get_record_data(self, header: str) -> tuple[RecordType, str]:
        record_type, city = header.split(HEADER_SPLIT_CHAR)
        return RecordType(record_type), city

    def __handle_records(self, record_type: RecordType, city: str):
        count = 0
        msg = self.socket.recv().decode()
        h, msg = msg.split(RECORDS_SPLIT_CHAR, 1)
        headers = h.split(ATTRS_SPLIT_CHAR)
        while msg != RecordType.End:
            message = RawRecord(
                record_type,
                city,
                headers,
                msg.splitlines(),
            )
            self.comms.send_record(serialize(message))
            count += len(msg.splitlines())
            msg = self.socket.recv().decode()
        logging.info(f"{self.phase} | {city} | Received {count} {record_type} records")

    def __phase_err(self, received: RecordType):
        logging.error(f"Received {received} record in invalid phase {self.phase}")

    def __validate_phase(self, record_type: RecordType) -> bool:
        if (
            self.phase == Phase.Trips and record_type != RecordType.TRIP
        ) or self.phase == Phase.End:
            self.__phase_err(record_type)
            return False
        return True

    def get_records(self):
        logging.info(f"{self.phase} | Receiving weather and stations")
        msg = self.socket.recv().decode()
        while msg != RecordType.End:
            record_type, city = self.__get_record_data(msg)
            if not self.__validate_phase(record_type):
                break

            if self.phase == Phase.StationsWeather and record_type == RecordType.TRIP:
                logging.info(
                    f"{self.phase} | "
                    "Waiting for all weather and stations to be processed"
                )
                self.comms.wait_for_weather_stations()
                self.phase = Phase.Trips
                logging.info(f"{self.phase} | Sending trips")

            self.__handle_records(record_type, city)
            msg = self.socket.recv().decode()
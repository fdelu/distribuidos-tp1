import logging
import zmq

from common.phase import Phase
from common.messages import RecordType
from common.messages.raw import (
    ATTRS_SPLIT_CHAR,
    HEADER_SPLIT_CHAR,
    RECORDS_SPLIT_CHAR,
    RawRecord,
)

from config import Config
from comms import SystemCommunication


class ClientHandler:
    config: Config
    phase: Phase
    socket: zmq.Socket

    def __init__(self, config: Config, socket: zmq.Socket):
        self.config = config
        self.phase = Phase.StationsWeather
        self.socket = socket
        self.comms = SystemCommunication(config)

    def __get_record_data(self, header: str) -> tuple[RecordType, str]:
        record_type, city = header.split(HEADER_SPLIT_CHAR)
        return RecordType(record_type), city

    def __handle_records(self, record_type: RecordType, city: str):
        count = 0
        msg = self.socket.recv_string()
        h, msg = msg.split(RECORDS_SPLIT_CHAR, 1)
        headers = h.split(ATTRS_SPLIT_CHAR)
        while msg != RecordType.END:
            message = RawRecord(
                record_type,
                city,
                headers,
                msg.splitlines(),
            )
            self.comms.send(message)
            count += len(msg.splitlines())
            msg = self.socket.recv_string()
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
        msg = self.socket.recv_string()
        while msg != RecordType.END:
            record_type, city = self.__get_record_data(msg)
            if not self.__validate_phase(record_type):
                break

            if self.phase == Phase.StationsWeather and record_type == RecordType.TRIP:
                self.phase = Phase.Trips
                logging.info(f"{self.phase} | Sending trips")

            self.__handle_records(record_type, city)
            msg = self.socket.recv_string()

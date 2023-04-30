import logging
from threading import Event
import zmq

from shared.messages import SplitChar

from common.phase import Phase
from common.messages import RecordType, End
from common.messages.raw import RawBatch

from .config import Config
from .comms import SystemCommunication


class ClientHandler:
    config: Config
    phase: Phase
    socket: zmq.Socket

    stop_event: Event

    def __init__(self, config: Config, socket: zmq.Socket):
        self.config = config
        self.phase = Phase.StationsWeather
        self.socket = socket
        self.comms = SystemCommunication(config)
        self.stop_event = Event()

    def __get_record_data(self, header: str) -> tuple[RecordType, str]:
        if header == RecordType.END:
            return RecordType.END, ""
        record_type, city = header.split(SplitChar.HEADER)
        return RecordType(record_type), city

    def __handle_batch(self, record_type: RecordType, city: str):
        count = 0
        msg = self.socket.recv_string()
        headers, msg = msg.split(SplitChar.RECORDS, 1)
        while msg != RecordType.END:
            message = RawBatch(
                record_type,
                city,
                headers,
                msg.splitlines(),
            )
            self.comms.send(message)
            count += len(msg.splitlines())
            msg = self.socket.recv_string()
        logging.info(
            f"{self.phase} | {city} | Received and sent {count} {record_type} records"
        )

    def __handle_end(self):
        self.comms.send(End())
        self.stop_event.set()

    def __validate_phase(self, record_type: RecordType) -> bool:
        if (
            self.phase == Phase.Trips
            and record_type not in (RecordType.TRIP, RecordType.END)
        ) or self.phase == Phase.End:
            logging.error(
                f"Received {record_type} record in invalid phase {self.phase}"
            )
            return False
        return True

    def run(self):
        logging.info(f"{self.phase} | Receiving weather and stations")

        while not self.stop_event.is_set():
            msg = self.socket.recv_string()
            record_type, city = self.__get_record_data(msg)
            if not self.__validate_phase(record_type):
                continue

            if self.phase == Phase.StationsWeather and record_type == RecordType.TRIP:
                self.phase = Phase.Trips
                logging.info(f"{self.phase} | Sending trips")

            if record_type == RecordType.END:
                self.__handle_end()
            else:
                self.__handle_batch(record_type, city)
        logging.info("Finished receiving data")
        self.comms.close()

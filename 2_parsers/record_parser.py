import logging


from common.messages import End, RecordType
from common.messages.raw import RawRecord

from config import Config
from parse import parse_rows
from comms import SystemCommunication


class RecordParser:
    receiving_trips: bool
    comms: SystemCommunication

    def __init__(self, config: Config):
        self.receiving_trips = False
        self.comms = SystemCommunication(config)

    def run(self):
        logging.info("Receiving weather & stations")
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()

    def handle_record(self, raw_record: RawRecord):
        if (not self.receiving_trips) and raw_record.record_type == RecordType.TRIP:
            self.receiving_trips = True
            logging.info("Receiving trips")
            self.comms.send(End())

        x = parse_rows(raw_record)
        for record in x:
            self.comms.send(record)

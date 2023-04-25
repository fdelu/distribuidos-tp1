import logging


from common.messages import End, RecordType
from common.messages.raw import RawBatch, RawRecord

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

    def handle_batch(self, raw_batch: RawBatch):
        if (not self.receiving_trips) and raw_batch.record_type == RecordType.TRIP:
            self.receiving_trips = True
            logging.info("Receiving trips")
            self.comms.send(End())

        x = parse_rows(raw_batch)
        for record in x:
            self.comms.send(record)

    def handle_end(self, end: End):
        if self.receiving_trips:
            logging.info("Finished parsing all trips")
            self.comms.send(End())

    def handle_record(self, raw_record: RawRecord):
        if isinstance(raw_record, RawBatch):
            self.handle_batch(raw_record)
        elif isinstance(raw_record, End):
            self.handle_end(raw_record)
        else:
            logging.error(f"Unknown record type: {type(raw_record)}")

import logging

from common.messages import End, RecordType
from common.messages.raw import RawRecord
from parse import parse_rows
from comms import SystemCommunication


class RecordParser:
    receiving_trips: bool
    comms: SystemCommunication

    def __init__(self, comms: SystemCommunication):
        self.receiving_trips = False
        self.comms = comms

        logging.info("Receiving weather & stations")

    def handle_record(self, raw_record: RawRecord):
        if (not self.receiving_trips) and raw_record.record_type == RecordType.TRIP:
            self.receiving_trips = True
            logging.info("Receiving trips")
            self.comms.send_record(End())

        x = parse_rows(raw_record)
        for record in x:
            self.comms.send_record(record)

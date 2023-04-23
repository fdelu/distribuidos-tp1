import logging

from common.messages.raw import RawRecord, RecordType
from parsers.parse import parse_rows


class RecordParser:
    receiving_trips: bool

    def __init__(self):
        self.receiving_trips = False

    def handle_record(self, raw_record: RawRecord):
        if (not self.receiving_trips) and raw_record.record_type == RecordType.TRIP:
            self.receiving_trips = True
            logging.info("Started receiving trips")

        x = parse_rows(raw_record)
        raise NotImplementedError(x)

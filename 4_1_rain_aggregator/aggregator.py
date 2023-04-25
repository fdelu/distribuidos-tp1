from common.messages import End
from common.messages.joined import JoinedRecord, JoinedTrip
from common.messages.rain import DateInfo, PartialRainAverages
from comms import SystemCommunication

from config import Config


class RainedAggregator:
    def __init__(self, config: Config):
        self.comms = SystemCommunication(config)
        self.averages: dict[str, DateInfo] = {}

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()

    def handle_trip(self, trip: JoinedTrip):
        date_average = self.averages.setdefault(trip.start_date, DateInfo(0, 0))
        date_average.count += 1
        delta = (trip.duration_sec - date_average.average_duration) / date_average.count
        date_average.average_duration += delta

    def handle_end(self):
        self.comms.send(PartialRainAverages(self.averages))
        self.comms.send(End())

    def handle_record(self, record: JoinedRecord):
        if isinstance(record, JoinedTrip):
            self.handle_trip(record)
        elif isinstance(record, End):
            self.handle_end()
        else:
            raise ValueError(f"Unexpected record type: {type(record)}")

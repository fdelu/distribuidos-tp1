import logging
from typing import Any
from common.messages import End
from common.messages.joined import JoinedRecord, JoinedTrip
from common.messages.rain import DateInfo, PartialRainAverages
from comms import SystemCommunication

from config import Config


class RainedAggregator:
    comms: SystemCommunication
    averages: dict[str, DateInfo]
    timer: Any | None
    config: Config
    ends_received: int

    def __init__(self, config: Config):
        self.comms = SystemCommunication(config)
        self.config = config
        self.averages: dict[str, DateInfo] = {}
        self.ends_received = 0
        self.timer = None

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.timer = self.comms.set_timer(
            self.periodic_send_averages, self.config.send_interval_seconds
        )
        self.comms.start_consuming()

    def handle_trip(self, trip: JoinedTrip):
        date_average = self.averages.setdefault(trip.start_date, DateInfo(0, 0))
        date_average.count += 1
        delta = (trip.duration_sec - date_average.average_duration) / date_average.count
        date_average.average_duration += delta

    def handle_end(self):
        self.ends_received += 1
        if self.ends_received < self.config.joiners_count:
            logging.info(
                "A joiner finished sending trips, waiting for others"
                f" ({self.ends_received}/{self.config.joiners_count})"
            )
            return

        logging.info("All trips processed, stopping...")
        if self.timer is not None:
            self.comms.cancel_timer(self.timer)
            self.timer = None

        self.send_averages()
        self.comms.send(End())
        self.comms.stop_consuming()

    def handle_record(self, record: JoinedRecord):
        record.be_handled_by(self)

    def periodic_send_averages(self):
        self.send_averages()
        self.timer = self.comms.set_timer(
            self.periodic_send_averages, self.config.send_interval_seconds
        )

    def send_averages(self):
        logging.info("Sending partial averages")
        self.comms.send(PartialRainAverages(self.averages))
        self.averages = {}

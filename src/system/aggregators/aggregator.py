import logging
from typing import Any

from common.messages import End
from common.messages.joined import JoinedRecord, JoinedTrip
from common.messages.rain import DateInfo, PartialRainAverages

from .comms import SystemCommunication
from .config import Config


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
        self.comms.start_consuming()
        self.comms.close()

    def handle_trip(self, trip: JoinedTrip):
        date_average = self.averages.setdefault(trip.start_date, DateInfo(0, 0))
        date_average.count += 1
        delta = (trip.duration_sec - date_average.average_duration) / date_average.count
        date_average.average_duration += delta

        if self.timer is None:
            self.setup_timer()

    def handle_end(self):
        self.ends_received += 1
        logging.info(
            "A joiner finished sending trips"
            f" ({self.ends_received}/{self.config.joiners_count})"
        )
        if self.ends_received < self.config.joiners_count:
            return
        logging.info("Waiting for all trips to be processed")
        self.comms.set_all_trips_done_callback(self.finished)

    def handle_record(self, record: JoinedRecord):
        record.be_handled_by(self)

    def finished(self):
        logging.info("All trips processed, sending final partial averages")
        if self.timer is not None:
            self.comms.cancel_timer(self.timer)
            self.timer = None

        self.send_averages()
        self.comms.send(End())
        self.comms.stop_consuming()

    def timer_callback(self):
        self.send_averages()
        self.setup_timer()

    def setup_timer(self):
        self.timer = self.comms.set_timer(
            self.timer_callback, self.config.send_interval_seconds
        )

    def send_averages(self):
        logging.info("Sending partial averages")
        logging.debug(f"Values sent: {self.averages}")
        self.comms.send(PartialRainAverages(self.averages))
        self.averages = {}

import logging
from common.messages.rain import DateInfo, PartialRainAverages, PartialRainRecords
from common.messages.stats import RainAverages

from .comms import SystemCommunication
from .config import Config


class AverageReducer:
    averages: dict[str, DateInfo]
    config: Config
    comms: SystemCommunication
    ends_received: int

    def __init__(self, config: Config):
        self.comms = SystemCommunication(config)
        self.averages = {}
        self.ends_received = 0
        self.config = config

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()
        self.comms.close()

    def handle_average(self, avg: PartialRainAverages):
        for date, date_average in avg.averages.items():
            current = self.averages.setdefault(date, DateInfo(0, 0))
            logging.debug(f"Merging {current} with {date_average}")

            total_count = current.count + date_average.count
            current_factor = current.count / total_count
            new_factor = date_average.count / total_count

            current.average_duration = (
                current.average_duration * current_factor
                + date_average.average_duration * new_factor
            )
            current.count = total_count

    def handle_end(self):
        self.ends_received += 1
        if self.ends_received < self.config.aggregators_count:
            logging.info(
                "An aggregator finished sending averages"
                f" ({self.ends_received}/{self.config.aggregators_count})"
            )
            return

        logging.info("All averages processed, stopping...")
        out = {x: y.average_duration for x, y in self.averages.items()}
        self.comms.send(RainAverages(out))
        self.comms.stop_consuming()

    def handle_record(self, record: PartialRainRecords):
        record.be_handled_by(self)

from common.messages import End
from common.messages.rain import DateInfo, PartialRainAverages, PartialRainRecords
from common.messages.stats import RainAverages

from comms import SystemCommunication
from config import Config


class AverageReducer:
    def __init__(self, config: Config):
        self.comms = SystemCommunication(config)
        self.averages: dict[str, DateInfo] = {}

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()

    def handle_average(self, avg: PartialRainAverages):
        for date, date_average in avg.averages.items():
            current = self.averages.setdefault(date, DateInfo(0, 0))

            total_count = current.count + date_average.count
            current_factor = current.count / total_count
            new_factor = date_average.count / total_count

            current.average_duration = (
                current.average_duration * current_factor
                + date_average.average_duration * new_factor
            )
            current.count = total_count

    def handle_end(self):
        out = {x: y.average_duration for x, y in self.averages.items()}
        self.comms.send(RainAverages(out))
        self.comms.send(End())

    def handle_record(self, record: PartialRainRecords):
        if isinstance(record, PartialRainAverages):
            self.handle_average(record)
        elif isinstance(record, End):
            self.handle_end()
        else:
            raise ValueError(f"Unexpected record type: {type(record)}")

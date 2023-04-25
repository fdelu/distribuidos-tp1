from common.comms_base import SystemCommunicationBase
from common.messages.rain import PartialRainRecords
from common.messages.stats import StatsRecord


class SystemCommunication(SystemCommunicationBase[PartialRainRecords, StatsRecord]):
    def load_definitions(self):
        # in
        self.channel.queue_declare("partial_rain_averages")

        # out
        self.channel.queue_declare("stats")

    def send(self, record: StatsRecord):
        self._send_to(record, "", "stats")

    def start_consuming(self):
        self._start_consuming_from("partial_rain_averages")

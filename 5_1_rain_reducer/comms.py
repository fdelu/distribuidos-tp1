from common.comms_base import SystemCommunicationBase
from common.messages.rain import PartialRainRecords
from common.messages.stats import StatsRecord


class SystemCommunication(SystemCommunicationBase[PartialRainRecords, StatsRecord]):
    AVERAGES_QUEUE = "partial_rain_averages"

    OUT_QUEUE = "stats"

    def load_definitions(self):
        # in
        self._start_consuming_from(self.AVERAGES_QUEUE)

    def send(self, record: StatsRecord):
        self._send_to(record, "", self.OUT_QUEUE)

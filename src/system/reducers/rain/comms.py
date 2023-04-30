from common.comms_base import SystemCommunicationBase
from common.messages.aggregated import PartialRainRecords
from common.messages.stats import StatsRecord


class SystemCommunication(SystemCommunicationBase[PartialRainRecords, StatsRecord]):
    AVERAGES_QUEUE = "rain_aggregated"

    OUT_QUEUE = "stats"

    def _load_definitions(self):
        # in
        self._start_consuming_from(self.AVERAGES_QUEUE)

    def _get_routing_details(self, record: StatsRecord):
        return "", self.OUT_QUEUE

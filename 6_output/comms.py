from common.comms_base import SystemCommunicationBase
from common.messages.stats import StatsRecord


class SystemCommunication(SystemCommunicationBase[StatsRecord, None]):
    STATS_QUEUE = "stats"

    def load_definitions(self):
        # in
        self._start_consuming_from(self.STATS_QUEUE)

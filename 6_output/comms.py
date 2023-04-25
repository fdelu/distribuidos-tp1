from common.comms_base import SystemCommunicationBase
from common.messages.stats import StatsRecord


class SystemCommunication(SystemCommunicationBase[StatsRecord, None]):
    def load_definitions(self):
        # in
        self.channel.queue_declare(queue="stats")
        self._start_consuming_from("stats")

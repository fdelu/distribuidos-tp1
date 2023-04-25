from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.rain import PartialRainRecords
from common.messages.stats import StatsRecord


class SystemCommunication(SystemCommunicationBase[PartialRainRecords, StatsRecord]):
    def load_definitions(self):
        # in
        exchange_name = "joined_trips"

        self.channel.exchange_declare(exchange=exchange_name, exchange_type="topic")
        self.channel.queue_declare("trips_rained")
        self.channel.queue_bind(
            "trips_rained", exchange_name, f"{RecordType.TRIP}.*.*.true"
        )
        self.channel.queue_bind("trips_rained", exchange_name, RecordType.END)

        # out
        self.channel.queue_declare("stats")

    def send(self, record: StatsRecord):
        self._send_to(record, "", "stats")

    def start_consuming(self):
        self._start_consuming_from("trips_rained")

from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.joined import JoinedRecord
from common.messages.rain import PartialRainRecords


class SystemCommunication(SystemCommunicationBase[JoinedRecord, PartialRainRecords]):
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
        self.channel.queue_declare("partial_rain_averages")

    def send(self, record: PartialRainRecords):
        self._send_to(record, "", "partial_rain_averages")

    def start_consuming(self):
        self._start_consuming_from("trips_rained")

from common.messages.basic import BasicRecord
from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[RawRecord, BasicRecord]):
    def _load_definitions(self):
        # in
        self.channel.queue_declare(queue="raw_records")
        self.channel.basic_consume(queue="raw_records")

        # out
        self.channel.exchange_declare(exchange="basic_records", exchange_type="direct")
        self.channel.queue_declare(queue="basic_trips")
        self.channel.queue_bind("basic_trips", "basic_records", RecordType.TRIP)

    def start_consuming(self):
        self._start_consuming_from("raw_records")

    def send(self, record: BasicRecord):
        self._send_to(record, "basic_records", record.get_routing_key())

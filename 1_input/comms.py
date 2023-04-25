from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[None, RawRecord]):
    def _load_definitions(self):
        # out
        self.channel.exchange_declare(exchange="raw_records", exchange_type="direct")
        self.channel.queue_declare(queue="raw_batchs")
        self.channel.queue_bind("raw_batchs", "raw_records", RecordType.RAW_BATCH)

    def send(self, record: RawRecord):
        self._send_to(record, "raw_records", record.get_routing_key())

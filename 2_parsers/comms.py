from common.messages.basic import BasicRecord
from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[RawRecord, BasicRecord]):
    def _load_definitions(self):
        # in
        exchange_name = "raw_records"
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        self.channel.queue_declare(queue="raw_batchs")
        self.channel.queue_bind("raw_batchs", exchange_name, RecordType.RAW_BATCH)
        self._start_consuming_from("raw_batchs")

        r = self.channel.queue_declare("")  # for end
        q_name = r.method.queue
        self.channel.queue_bind(q_name, exchange_name, RecordType.END)
        self._start_consuming_from(q_name)

        # out
        self.channel.exchange_declare(exchange="basic_records", exchange_type="direct")
        self.channel.queue_declare(queue="basic_trips")
        self.channel.queue_bind("basic_trips", "basic_records", RecordType.TRIP)

    def send(self, record: BasicRecord):
        self._send_to(record, "basic_records", record.get_routing_key())

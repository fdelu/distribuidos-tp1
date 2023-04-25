from common.messages.basic import BasicRecord
from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[RawRecord, BasicRecord]):
    end_queue: str | None

    def _load_definitions(self):
        # in
        exchange_name = "raw_records"
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        self.channel.queue_declare(queue="raw_batchs")
        self.channel.queue_bind("raw_batchs", exchange_name, RecordType.RAW_BATCH)

        r = self.channel.queue_declare("")  # for end
        q_name = r.method.queue
        self.channel.queue_bind(q_name, exchange_name, RecordType.END)
        self.end_queue = q_name

        # out
        self.channel.exchange_declare(exchange="basic_records", exchange_type="direct")
        self.channel.queue_declare(queue="basic_trips")
        self.channel.queue_bind("basic_trips", "basic_records", RecordType.TRIP)

    def start_consuming(self):
        self._start_consuming_from("raw_records")
        if self.end_queue is None:
            raise Exception("End queue not initialized")
        self._start_consuming_from(self.end_queue)

    def send(self, record: BasicRecord):
        self._send_to(record, "basic_records", record.get_routing_key())

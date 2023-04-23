from typing import Callable
from pika import BlockingConnection, ConnectionParameters, spec, adapters
from common.messages.basic import BasicRecord
from config import Config

from common.messages import RecordType
from common.messages.raw import RawRecord
from common.serde import serialize, deserialize


class SystemCommunication:
    def __init__(self, config: Config, callback: Callable[[RawRecord], None]):
        self.connection = BlockingConnection(
            ConnectionParameters(host=config.rabbit_host)
        )
        self.channel = self.connection.channel()
        self.setup_queues()

        self.callback = callback

    def setup_queues(self):
        # in
        self.channel.queue_declare(queue="raw_records")
        self.channel.basic_consume(
            queue="raw_records", on_message_callback=self.__handle_record
        )

        # out
        self.channel.exchange_declare(exchange="basic_records", exchange_type="direct")
        self.channel.queue_declare(queue="basic_trips")
        self.channel.queue_bind("basic_trips", "basic_records", RecordType.TRIP)

    def __handle_record(
        self,
        _ch: adapters.BlockingConnection,
        _method: spec.Basic.Deliver,
        _props: spec.BasicProperties,
        body: bytes,
    ):
        record = deserialize(RawRecord, body.decode())
        self.callback(record)

    def start_consuming(self):
        self.channel.start_consuming()

    def send_record(self, record: BasicRecord):
        self.channel.basic_publish(
            "basic_records", record.record_type, serialize(record)
        )

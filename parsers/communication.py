from typing import Callable
from pika import BlockingConnection, ConnectionParameters, spec, adapters
from config import Config

from common.messages.raw import RawRecord
from common.serde import deserialize


class SystemCommunication:
    def __init__(self, config: Config, callback: Callable[[RawRecord], None]):
        self.connection = BlockingConnection(
            ConnectionParameters(host=config.rabbit_host)
        )
        self.channel = self.connection.channel()
        self.setup_queues()

        self.callback = callback

    def setup_queues(self):
        self.channel.queue_declare(queue="raw_records")
        self.channel.queue_declare(queue="raw_records_callback")
        self.channel.basic_consume(
            queue="raw_records", on_message_callback=self.__handle_record
        )

    def __handle_record(
        self,
        _ch: adapters.BlockingConnection,
        _method: spec.Basic.Deliver,
        _props: spec.BasicProperties,
        body: bytes,
    ):
        record = deserialize(RawRecord, body.decode())
        self.channel.basic_publish("", "raw_records_callback", "")
        self.callback(record)

    def start_consuming(self):
        self.channel.start_consuming()

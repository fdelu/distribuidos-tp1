import os
from typing import Callable, TypeVar, Generic, get_args, Protocol
from pika import BlockingConnection, ConnectionParameters, spec
from pika.adapters.blocking_connection import BlockingChannel
from common.config import ConfigBase

from common.serde import serialize, deserialize


class WithRoutingKey(Protocol):
    def get_routing_key(self) -> str:
        ...


IN = TypeVar("IN")
OUT = TypeVar("OUT", bound=WithRoutingKey)
STATUS_FILE = os.getenv("STATUS_FILE", "status.txt")


class SystemCommunicationBase(Generic[IN, OUT]):
    connection: BlockingConnection
    channel: BlockingChannel
    callback: Callable[[IN], None] | None

    def __init__(self, config: ConfigBase):
        self.connection = BlockingConnection(
            ConnectionParameters(host=config.rabbit_host)
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=config.prefetch_count)

        self.callback = None

    def load_definitions(self):
        raise NotImplementedError()

    def setup(self):
        self.load_definitions()
        with open(STATUS_FILE, "w") as f:
            f.write("OK")

    def get_output_names(self) -> tuple[str, str | None]:
        """
        Should return a tuple of (exchange_name, routing_key).
        If routing_key is None, then it will be obtained from the record.
        """
        raise NotImplementedError()

    def deserialize_record(self, body: str) -> IN:
        in_type = get_args(self.__orig_bases__[0])[0]  # type: ignore
        return deserialize(in_type, body)

    def serialize_record(self, record: OUT) -> str:
        out_type = get_args(self.__orig_bases__[0])[1]  # type: ignore
        return serialize(record, set_type=out_type)

    def handle_record(
        self,
        ch: BlockingChannel,
        method: spec.Basic.Deliver,
        _props: spec.BasicProperties,
        body: bytes,
    ):
        if self.callback is not None:
            self.callback(self.deserialize_record(body.decode()))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self, callback: Callable[[IN], None]):
        self.callback = callback
        self.channel.start_consuming()

    def send_record(self, record: OUT):
        exchange, routing_key = self.get_output_names()
        if routing_key is None:
            routing_key = record.get_routing_key()
        self.channel.basic_publish(
            exchange,
            routing_key,
            self.serialize_record(record),
        )

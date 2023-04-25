import os
from typing import Callable, TypeVar, Generic, get_args
from pika import BlockingConnection, ConnectionParameters, spec
from pika.adapters.blocking_connection import BlockingChannel
from common.config import ConfigBase

from common.serde import serialize, deserialize


IN = TypeVar("IN")
OUT = TypeVar("OUT")
STATUS_FILE = os.getenv("STATUS_FILE", "status.txt")
TIMEOUT_SECONDS = 1


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
        self.__setup()

    def start_consuming(self):
        """
        Start consuming messages from the queues
        """
        self.channel.start_consuming()

    def stop_consuming(self):
        """
        Safe way to stop consuming
        """
        self.connection.add_callback_threadsafe(lambda: self.channel.stop_consuming())

    def set_callback(self, callback: Callable[[IN], None]):
        """
        Sets the callback to be called when a record is received
        """
        self.callback = callback

    def _send_to(self, record: OUT, exchange: str, routing_key: str):
        """
        Sends a record with the given exchange and routing keys
        """
        self.channel.basic_publish(
            exchange,
            routing_key,
            self.__serialize_record(record),
        )

    def _load_definitions(self):
        """
        Declares the exchanges, queues and bindings required for the communication
        """
        raise NotImplementedError()

    def _get_output_names(self, record: OUT) -> tuple[str, str]:
        """
        Should return a tuple of (exchange_name, routing_key) for this record
        """
        raise NotImplementedError()

    def _start_consuming_from(self, queue: str):
        """
        Starts consuming from the given queue.
        This method returns when stop_consuming() is called.
        """
        self.channel.basic_consume(queue=queue, on_message_callback=self._handle_record)

    def _handle_record(
        self,
        ch: BlockingChannel,
        method: spec.Basic.Deliver,
        _props: spec.BasicProperties,
        body: bytes,
    ):
        """
        Handles a message received from the queue, calling the callback
        if set and acknowledging the message afterwards.
        This method returns when stop_consuming() is called.
        """
        if self.callback is not None:
            self.callback(self.__deserialize_record(body.decode()))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __setup(self):
        """
        Loads the definitions. When done, writes "OK" to the status file.
        """
        self._load_definitions()
        with open(STATUS_FILE, "w") as f:
            f.write("OK")

    def __deserialize_record(self, message: str) -> IN:
        """
        Deserialize the given message into the input type
        """
        in_type = get_args(self.__orig_bases__[0])[0]  # type: ignore
        return deserialize(in_type, message)

    def __serialize_record(self, message: OUT) -> str:
        """
        Serializes the given message into a string
        """
        out_type = get_args(self.__orig_bases__[0])[1]  # type: ignore
        return serialize(message, set_type=out_type)

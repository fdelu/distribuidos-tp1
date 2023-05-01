from dataclasses import dataclass
from abc import ABC, abstractmethod
from threading import Event
from typing import Any, Callable, TypeVar, Generic, get_args
import os
from functools import partial
from signal import signal, SIGTERM
import time
import logging

from pika import BlockingConnection, ConnectionParameters, spec
from pika.adapters.blocking_connection import BlockingChannel

from common.config_base import ConfigBase
from common.serde import serialize, deserialize

IN = TypeVar("IN")
OUT = TypeVar("OUT", contravariant=True)
STATUS_FILE = os.getenv("STATUS_FILE", "status.txt")
TIMEOUT_SECONDS = 1


class SystemCommunicationBase(ABC, Generic[IN, OUT]):
    connection: BlockingConnection
    channel: BlockingChannel
    callback: Callable[[IN], None] | None

    # queue name -> (callback, timer)
    timeout_callbacks: dict[str, "TimeoutInfo"]
    stopped: Event

    def __init__(self, config: ConfigBase, with_interrupt: bool = True):
        self.connection = BlockingConnection(
            ConnectionParameters(host=config.rabbit_host)
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=config.prefetch_count)

        self.stopped = Event()
        self.timeout_callbacks = {}
        self.callback = None
        if with_interrupt:
            self.__setup_interrupt()
        self.__setup()

    def start_consuming(self):
        """
        Start consuming messages from the queues
        """
        self.channel.start_consuming()

    def stop_consuming(self):
        """
        Signal/Thread-Safe way to stop consuming
        """
        self.stopped.set()
        # In case there are no messages being consumed, this will unblock the loop:
        self.connection.add_callback_threadsafe(lambda: self.channel.stop_consuming())

    def close(self):
        """
        Closes the connection
        """
        self.connection.close()

    def set_callback(self, callback: Callable[[IN], None]):
        """
        Sets the callback to be called when a record is received
        """
        self.callback = callback

    def set_timer(self, callback: Callable[[], None], timeout_seconds: float) -> Any:
        """
        Calls the callback after timeout seconds.
        Returns an object that can be used to cancel the timer.
        """
        return self.connection.call_later(timeout_seconds, callback)

    def cancel_timer(self, timer: Any):
        """
        Cancels the timer
        """
        self.connection.remove_timeout(timer)

    def send(self, record: OUT):
        """
        Sends a record to the appropriate queue
        """
        exchange, routing_key = self._get_routing_details(record)
        self.__send_to(record, exchange, routing_key)

    def is_stopped(self) -> bool:
        """
        Returns whether the consuming was stopped (or will be soon)
        """
        return self.stopped.is_set()

    @abstractmethod
    def _load_definitions(self):
        """
        Declares the exchanges, queues and bindings required for the communication
        """
        ...

    @abstractmethod
    def _get_routing_details(self, record: OUT) -> tuple[str, str]:
        """
        Should return a tuple of (exchange_name, routing_key) for this record
        """
        ...

    def _start_consuming_from(self, queue: str):
        """
        Starts consuming from the given queue.
        This method returns when stop_consuming() is called.
        """
        callback = partial(self.__handle_record, queue)
        self.channel.basic_consume(queue=queue, on_message_callback=callback)

    def _set_timeout_callback(
        self, queue: str, callback: Callable[[], None], timeout: float = TIMEOUT_SECONDS
    ):
        """
        Sets a callback to be called after timeout seconds passed since the last message
        of the given queue was received. If no message is received after the call to
        this method, the callback will be called after timeout seconds.
        """
        prev = self.timeout_callbacks.get(queue, None)
        if prev is not None:
            self.connection.remove_timeout(prev.timer)

        info = TimeoutInfo(callback, timeout, None)
        self.timeout_callbacks[queue] = info
        info.timer = self.connection.call_later(
            info.time_seconds, lambda: self.__timeout_handler(info)
        )

    def _set_empty_queue_callback(
        self, queue: str, callback: Callable[[], None], **queue_kwargs
    ):
        """
        Sets a callback to be called when the given queue is empty.
        """
        self._set_timeout_callback(
            queue,
            lambda: self.__check_messages_left(queue, callback, **queue_kwargs),
        )

    def __setup_interrupt(self):
        signal(SIGTERM, lambda *_: self.stop_consuming())

    def __send_to(self, record: OUT, exchange: str, routing_key: str):
        """
        Sends a record with the given exchange and routing keys
        """
        self.channel.basic_publish(
            exchange,
            routing_key,
            self.__serialize_record(record).encode(),
        )

    def __check_messages_left(
        self, queue: str, callback: Callable[[], None], **queue_kwargs
    ):
        """
        Checks if there are messages left in the given queue. If not, calls the
        callback. If there are, calls _set_empty_queue_callback() again.
        """
        res = self.channel.queue_declare(queue=queue, passive=True, **queue_kwargs)
        messages_left = res.method.message_count
        if messages_left == 0:
            callback()
        else:
            # for some reason the queue is not empty but the timeout expired
            # set the timer again:
            self._set_empty_queue_callback(queue, callback, **queue_kwargs)

    def __setup(self):
        """
        Loads the definitions. When done, writes "OK" to the status file.
        """
        self._load_definitions()
        with open(STATUS_FILE, "w") as f:
            f.write("OK")

    def __handle_record(
        self,
        queue: str,
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
        if self.stopped.is_set():
            self.channel.stop_consuming()
            return

        timeout_info = self.timeout_callbacks.get(queue, None)
        if timeout_info is not None:
            timeout_info.last_message_on = time.time()

        if self.callback is not None:
            self.callback(self.__deserialize_record(body.decode()))
        if method.delivery_tag is not None:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def __timeout_handler(self, info: "TimeoutInfo"):
        """
        Handles a timeout for the given timeout info
        """
        now = time.time()
        logging.debug(
            f"Timeout handler | delay: {info.time_seconds}, last:"
            f" {info.last_message_on}, now: {now}"
        )
        if info.last_message_on is None:
            info.callback()
            return

        seconds_remaining = info.time_seconds - (now - info.last_message_on)
        if seconds_remaining <= 0:
            info.callback()
        else:
            info.timer = self.connection.call_later(
                seconds_remaining, lambda: self.__timeout_handler(info)
            )

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


@dataclass
class TimeoutInfo:
    """
    Stores information about a timeout callback.
    See SystemCommunicationBase._set_timeout_callback()
    """

    callback: Callable[[], None]
    time_seconds: float  # timeout after this many seconds
    last_message_on: float | None  # time.time() when the last message was received
    timer: Any | None = None  # the timer object

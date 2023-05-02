from typing import TypeVar, Generic, get_args
from abc import ABC, abstractmethod

from ..serde import serialize

from .protocol import CommsProtocol

OUT = TypeVar("OUT", contravariant=True)


class CommsSend(CommsProtocol, Generic[OUT], ABC):
    """
    Comms with send capabilities. See protocol.py for more details about the methods.
    """

    def send(self, record: OUT):
        exchange, routing_key = self._get_routing_details(record)
        self.__send_to(record, exchange, routing_key)

    def __send_to(self, record: OUT, exchange: str, routing_key: str):
        self.channel.basic_publish(
            exchange,
            routing_key,
            self.__serialize_record(record).encode(),
        )

    def __serialize_record(self, message: OUT) -> str:
        out_type = get_args(self.__orig_bases__[0])[1]  # type: ignore
        return serialize(message, set_type=out_type)

    @abstractmethod
    def _get_routing_details(self, record: OUT) -> tuple[str, str]:
        ...

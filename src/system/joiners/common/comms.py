from typing import Callable, TypeVar, Generic
from abc import abstractmethod, ABC

from common.comms_base import CommsReceive, SystemCommunicationBase
from common.comms_base.protocol import CommsSendProtocol
from common.messages.joined import JoinedRecord

OUT = TypeVar("OUT", bound=JoinedRecord)


class JoinerComms(
    SystemCommunicationBase,
    CommsReceive[JoinedRecord],
    Generic[OUT],
    CommsSendProtocol[OUT],
    ABC,
):
    EXCHANGE = "basic_records"

    @property
    @abstractmethod
    def TRIPS_QUEUE(self):
        ...

    @property
    @abstractmethod
    def OUT_EXCHANGE(self):
        ...

    def _get_routing_details(self, record: OUT):
        return self.OUT_EXCHANGE, record.get_routing_key()

    def start_consuming_trips(self):
        self._start_consuming_from(self.TRIPS_QUEUE)

    def set_all_trips_done_callback(self, callback: Callable[[], None]):
        self._set_empty_queue_callback(self.TRIPS_QUEUE, callback)

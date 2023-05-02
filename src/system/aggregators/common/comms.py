from typing import Callable, Generic
from abc import ABC, abstractmethod
from uuid import uuid4

from common.config_base import ConfigBase
from common.messages import RecordType
from common.comms_base import SystemCommunicationBase
from common.comms_base.protocol import CommsReceiveProtocol, IN, CommsSendProtocol, OUT


class AggregatorComms(
    SystemCommunicationBase,
    Generic[IN, OUT],
    CommsReceiveProtocol[IN],
    CommsSendProtocol[OUT],
    ABC,
):
    @property
    @abstractmethod
    def NAME(self) -> str:
        ...

    EXCHANGE = f"{NAME}_joined_records"
    TRIPS_QUEUE = f"{NAME}_joined_trips"
    END_QUEUE = f"{NAME}_aggregators_ends_{uuid4()}"

    OUT_QUEUE = f"{NAME}_aggregated"

    def __init__(self, config: ConfigBase):
        super().__init__(config)

    def _load_definitions(self):
        # in
        self._start_consuming_from(self.TRIPS_QUEUE)

        end_queue = self.END_QUEUE
        self.channel.queue_declare(end_queue, exclusive=True)  # end
        self.channel.queue_bind(end_queue, self.EXCHANGE, RecordType.END)
        self._start_consuming_from(end_queue)

    def _get_routing_details(self, _: OUT):
        return "", self.OUT_QUEUE

    def set_all_trips_done_callback(self, callback: Callable[[], None]):
        self._set_empty_queue_callback(self.TRIPS_QUEUE, callback)

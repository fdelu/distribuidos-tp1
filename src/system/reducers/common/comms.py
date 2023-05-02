from typing import Generic
from abc import abstractmethod, ABC

from common.comms_base.protocol import CommsReceiveProtocol, CommsSendProtocol, IN, OUT


class ReducerComms(
    Generic[IN, OUT],
    CommsReceiveProtocol[IN],
    CommsSendProtocol[OUT],
    ABC,
):
    @property
    @abstractmethod
    def INPUT_QUEUE(self) -> str:
        ...

    OUT_QUEUE = "stats"

    def _load_definitions(self):
        # in
        self._start_consuming_from(self.INPUT_QUEUE)

    def _get_routing_details(self, record: OUT):
        return "", self.OUT_QUEUE

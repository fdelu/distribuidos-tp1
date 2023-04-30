from typing import Callable

from common.comms_base import SystemCommunicationBase
from common.messages.basic import BasicRecord
from common.messages.joined import JoinedRecord


class JoinerComms(SystemCommunicationBase[BasicRecord, JoinedRecord]):
    EXCHANGE = "basic_records"

    @property
    def TRIPS_QUEUE(self):
        ...

    @property
    def OUT_EXCHANGE(self):
        ...

    def _get_routing_details(self, record: JoinedRecord):
        return self.OUT_EXCHANGE, record.get_routing_key()

    def start_consuming_trips(self):
        self._start_consuming_from(self.TRIPS_QUEUE)

    def set_all_trips_done_callback(self, callback: Callable[[], None]):
        self._set_empty_queue_callback(self.TRIPS_QUEUE, callback)

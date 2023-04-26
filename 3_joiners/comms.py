from typing import Callable
from uuid import uuid4

from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.basic import BasicRecord
from common.messages.joined import JoinedRecord


class SystemCommunication(SystemCommunicationBase[BasicRecord, JoinedRecord]):
    EXCHANGE = "basic_records"
    TRIPS_QUEUE = "basic_trips"
    OTHER_QUEUE = f"joiner_other_{uuid4()}"
    OUT_EXCHANGE = "joined_records"

    def _load_definitions(self):
        # in

        self.channel.queue_declare(
            self.OTHER_QUEUE, exclusive=True
        )  # for weather, stations & end
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.WEATHER)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.STATION)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.TRIPS_START)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.END)
        self._start_consuming_from(self.OTHER_QUEUE)

    def send(self, record: JoinedRecord):
        self._send_to(record, self.OUT_EXCHANGE, record.get_routing_key())

    def start_consuming_trips(self):
        self._start_consuming_from(self.TRIPS_QUEUE)

    def set_all_trips_done_callback(self, callback: Callable[[], None]):
        self._set_empty_queue_callback(self.TRIPS_QUEUE, callback)

from typing import Callable
from uuid import uuid4

from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.joined import JoinedRecord
from common.messages.rain import PartialRainRecords


class SystemCommunication(SystemCommunicationBase[JoinedRecord, PartialRainRecords]):
    EXCHANGE = "joined_records"
    TRIPS_QUEUE = "rained_trips"
    END_QUEUE = f"rained_ends_{uuid4()}"

    OUT_QUEUE = "partial_rain_averages"

    def load_definitions(self):
        # in
        self._start_consuming_from(self.TRIPS_QUEUE)

        self.channel.queue_declare(self.END_QUEUE, exclusive=True)  # end
        self.channel.queue_bind(self.END_QUEUE, self.EXCHANGE, RecordType.END)
        self._start_consuming_from(self.END_QUEUE)

    def send(self, record: PartialRainRecords):
        self._send_to(record, "", self.OUT_QUEUE)

    def set_all_trips_done_callback(self, callback: Callable[[], None]):
        self._set_empty_queue_callback(self.TRIPS_QUEUE, callback)

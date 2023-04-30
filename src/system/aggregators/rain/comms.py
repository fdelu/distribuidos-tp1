from typing import Callable
from uuid import uuid4

from common.config_base import ConfigBase
from common.messages import RecordType
from common.comms_base import SystemCommunicationBase
from common.messages.joined import JoinedRainRecord
from common.messages.aggregated import PartialRainRecords


class SystemCommunication(
    SystemCommunicationBase[JoinedRainRecord, PartialRainRecords]
):
    EXCHANGE = "rain_joined_records"
    TRIPS_QUEUE = "rain_joined_trips"
    END_QUEUE = f"rain_aggregators_ends_{uuid4()}"

    OUT_QUEUE = "rain_aggregated"

    def __init__(self, config: ConfigBase):
        super().__init__(config)

    def _load_definitions(self):
        # in
        self._start_consuming_from(self.TRIPS_QUEUE)

        end_queue = self.END_QUEUE
        self.channel.queue_declare(end_queue, exclusive=True)  # end
        self.channel.queue_bind(end_queue, self.EXCHANGE, RecordType.END)
        self._start_consuming_from(end_queue)

    def _get_routing_details(self, _: PartialRainRecords):
        return "", self.OUT_QUEUE

    def set_all_trips_done_callback(self, callback: Callable[[], None]):
        self._set_empty_queue_callback(self.TRIPS_QUEUE, callback)

from uuid import uuid4

from common.comms_base import CommsSend
from common.messages import RecordType
from common.messages.joined import JoinedRainRecords

from ..common.comms import JoinerComms


class SystemCommunication(CommsSend[JoinedRainRecords], JoinerComms[JoinedRainRecords]):
    EXCHANGE = "basic_records"
    TRIPS_QUEUE = "rain_basic_trips"
    OTHER_QUEUE = f"rain_joiner_other_{uuid4()}"
    OUT_EXCHANGE = "rain_joined_records"

    def _load_definitions(self):
        # in

        self.channel.queue_declare(
            self.OTHER_QUEUE, exclusive=True
        )  # for weather, tripstart & end
        self.channel.queue_bind(
            self.OTHER_QUEUE, self.EXCHANGE, f"{RecordType.WEATHER}.#"
        )
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.TRIPS_START)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.END)
        self._start_consuming_from(self.OTHER_QUEUE)

from uuid import uuid4

from common.messages import RecordType

from ..common.comms import JoinerComms


class SystemCommunication(JoinerComms):
    EXCHANGE = "basic_records"
    TRIPS_QUEUE = "rain_basic_trips"
    OTHER_QUEUE = f"rain_joiner_other_{uuid4()}"
    OUT_EXCHANGE = "rain_joined_records"

    def _load_definitions(self):
        # in

        self.channel.queue_declare(
            self.OTHER_QUEUE, exclusive=True
        )  # for weather & end
        self.channel.queue_bind(
            self.OTHER_QUEUE, self.EXCHANGE, f"{RecordType.WEATHER}.#"
        )
        # self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.STATION)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.TRIPS_START)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.END)
        self._start_consuming_from(self.OTHER_QUEUE)

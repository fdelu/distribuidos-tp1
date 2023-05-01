from uuid import uuid4

from common.messages import RecordType

from .config import Config
from ..common.comms import JoinerComms


class SystemCommunication(JoinerComms):
    EXCHANGE = "basic_records"
    TRIPS_QUEUE = "year_basic_trips"
    OTHER_QUEUE = f"year_joiner_other_{uuid4()}"
    OUT_EXCHANGE = "year_joined_records"

    config: Config

    def __init__(self, config: Config):
        self.config = config
        super().__init__(config)

    def _load_definitions(self):
        # in

        self.channel.queue_declare(
            self.OTHER_QUEUE, exclusive=True
        )  # for station, tripstart & end
        self.__bind_years(self.OTHER_QUEUE, RecordType.STATION)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.TRIPS_START)
        self.channel.queue_bind(self.OTHER_QUEUE, self.EXCHANGE, RecordType.END)

        self.__bind_years(self.TRIPS_QUEUE, RecordType.TRIP)
        self._start_consuming_from(self.OTHER_QUEUE)

    def __bind_years(self, queue: str, record: RecordType):
        for year in (self.config.year_base, self.config.year_compared):
            self.channel.queue_bind(queue, self.EXCHANGE, f"{record}.*.{year}")

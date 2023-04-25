from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.basic import BasicRecord
from common.messages.joined import JoinedRecord


class SystemCommunication(SystemCommunicationBase[BasicRecord, JoinedRecord]):
    weather_stations_queue: str | None

    def _load_definitions(self):
        # in
        exchange_name = "basic_records"

        self.channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        self.channel.queue_declare(queue="basic_trips")
        self.channel.queue_bind("basic_trips", exchange_name, RecordType.TRIP)

        r = self.channel.queue_declare("")  # for weather, stations & end
        q_name = r.method.queue
        self.channel.queue_bind(q_name, exchange_name, RecordType.WEATHER)
        self.channel.queue_bind(q_name, exchange_name, RecordType.STATION)
        self.channel.queue_bind(q_name, exchange_name, RecordType.END)
        self.weather_stations_queue = q_name

        # out
        self.channel.exchange_declare(exchange="joined_trips", exchange_type="topic")

    def send(self, record: JoinedRecord):
        self._send_to(record, "joined_trips", record.get_routing_key())

    def start_consuming_weather_stations(self):
        if self.weather_stations_queue is None:
            raise Exception("Weather stations queue not initialized")
        self._start_consuming_from(self.weather_stations_queue)

    def start_consuming_trips(self):
        self._start_consuming_from("basic_trips")

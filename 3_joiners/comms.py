from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.basic import BasicRecord
from common.messages.joined import JoinedRecord


class SystemCommunication(SystemCommunicationBase[BasicRecord, JoinedRecord]):
    def load_definitions(self):
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
        self.channel.basic_consume(queue=q_name, on_message_callback=self.handle_record)

        # out
        self.channel.exchange_declare(exchange="joined_trips", exchange_type="topic")

    def consume_trips(self):
        self.channel.basic_consume(
            queue="basic_trips", on_message_callback=self.handle_record
        )

    def get_output_names(self) -> tuple[str, str | None]:
        return "joined_trips", None

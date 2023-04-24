from common.messages.basic import BasicRecord
from common.comms_base import SystemCommunicationBase
from common.messages import RecordType
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[RawRecord, BasicRecord]):
    def load_definitions(self):
        # in
        self.channel.queue_declare(queue="raw_records")
        self.channel.basic_consume(
            queue="raw_records", on_message_callback=self.handle_record
        )

        # out
        self.channel.exchange_declare(exchange="basic_records", exchange_type="direct")
        self.channel.queue_declare(queue="basic_trips")
        self.channel.queue_bind("basic_trips", "basic_records", RecordType.TRIP)

    def get_output_names(self) -> tuple[str, str | None]:
        return "basic_records", None

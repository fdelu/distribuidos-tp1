from common.comms_base import SystemCommunicationBase
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[None, RawRecord]):
    def load_definitions(self):
        # out
        self.channel.queue_declare(queue="raw_records")

    def get_output_names(self) -> tuple[str, str | None]:
        return "", "raw_records"

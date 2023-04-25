from common.comms_base import SystemCommunicationBase
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[None, RawRecord]):
    def _load_definitions(self):
        # out
        self.channel.queue_declare(queue="raw_records")

    def send(self, record: RawRecord):
        self._send_to(record, "", "raw_records")

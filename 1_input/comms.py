from common.comms_base import SystemCommunicationBase
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[None, RawRecord]):
    OUT_EXCHANGE = "raw_records"

    def _load_definitions(self):
        pass

    def send(self, record: RawRecord):
        self._send_to(record, self.OUT_EXCHANGE, record.get_routing_key())

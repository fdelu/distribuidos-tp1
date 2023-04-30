from common.comms_base import SystemCommunicationBase
from common.messages.raw import RawRecord


class SystemCommunication(SystemCommunicationBase[None, RawRecord]):
    OUT_EXCHANGE = "raw_records"

    def _load_definitions(self):
        pass

    def _get_routing_details(self, record: RawRecord):
        return self.OUT_EXCHANGE, record.get_routing_key()

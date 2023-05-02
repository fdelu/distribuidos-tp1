from common.comms_base import CommsSend, CommsReceive
from common.messages.joined import JoinedRainRecords
from common.messages.aggregated import PartialRainRecords

from ..common.comms import AggregatorComms


class SystemCommunication(
    CommsReceive[JoinedRainRecords],
    CommsSend[PartialRainRecords],
    AggregatorComms[JoinedRainRecords, PartialRainRecords],
):
    NAME = "rain"

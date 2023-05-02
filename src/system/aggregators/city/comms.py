from common.comms_base import CommsSend, CommsReceive
from common.messages.joined import JoinedCityRecords
from common.messages.aggregated import PartialCityRecords

from ..common.comms import AggregatorComms


class SystemCommunication(
    CommsReceive[JoinedCityRecords],
    CommsSend[PartialCityRecords],
    AggregatorComms[JoinedCityRecords, PartialCityRecords],
):
    NAME = "city"

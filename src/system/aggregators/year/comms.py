from common.comms_base import CommsSend, CommsReceive
from common.messages.joined import JoinedYearRecords
from common.messages.aggregated import PartialYearRecords

from ..common.comms import AggregatorComms


class SystemCommunication(
    CommsReceive[JoinedYearRecords],
    CommsSend[PartialYearRecords],
    AggregatorComms[JoinedYearRecords, PartialYearRecords],
):
    NAME = "year"

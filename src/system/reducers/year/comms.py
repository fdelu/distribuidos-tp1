from common.comms_base import CommsSend, CommsReceive, SystemCommunicationBase
from common.messages.aggregated import PartialYearRecords
from common.messages.stats import YearCounts

from ..common.comms import ReducerComms


class SystemCommunication(
    SystemCommunicationBase,
    CommsReceive[PartialYearRecords],
    CommsSend[YearCounts],
    ReducerComms[PartialYearRecords, YearCounts],
):
    INPUT_QUEUE: str = "year_aggregated"

from common.comms_base import CommsSend, CommsReceive
from common.messages.aggregated import PartialRainRecords
from common.messages.stats import RainAverages

from ..common.comms import ReducerComms


class SystemCommunication(
    ReducerComms[PartialRainRecords, RainAverages],
    CommsSend[RainAverages],
    CommsReceive[PartialRainRecords],
):
    INPUT_QUEUE: str = "rain_aggregated"

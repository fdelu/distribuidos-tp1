from common.comms_base import CommsSend, CommsReceive
from common.messages.aggregated import PartialCityRecords
from common.messages.stats import CityAverages

from ..common.comms import ReducerComms


class SystemCommunication(
    ReducerComms[PartialCityRecords, CityAverages],
    CommsSend[CityAverages],
    CommsReceive[PartialCityRecords],
):
    INPUT_QUEUE: str = "city_aggregated"

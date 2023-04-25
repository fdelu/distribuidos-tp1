from dataclasses import dataclass
from enum import StrEnum

from common.messages import End


class StatType(StrEnum):
    RAIN = "rain"


# For 4_1_rained and 4_1_rained_reducer


@dataclass
class RainAverages:
    data: dict[str, float]


# For 4_2_


# ...

StatsRecord = RainAverages | End

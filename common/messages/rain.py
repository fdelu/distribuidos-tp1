from dataclasses import dataclass

from common.messages import End


@dataclass
class DateInfo:
    count: int
    average_duration: float


@dataclass
class PartialRainAverages:
    averages: dict[str, DateInfo]  # start_date -> DateInfo


PartialRainRecords = PartialRainAverages | End

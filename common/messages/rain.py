from typing import TypeVar, Protocol
from dataclasses import dataclass

from common.messages import End

T = TypeVar("T", covariant=True)


@dataclass
class DateInfo:
    count: int
    average_duration: float


@dataclass
class PartialRainAverages:
    averages: dict[str, DateInfo]  # start_date -> DateInfo

    def be_handled_by(self, handler: "RainRecordHandler[T]") -> T:
        return handler.handle_average(self)


class RainRecordHandler(Protocol[T]):
    def handle_average(self, trip: PartialRainAverages) -> T:
        ...


PartialRainRecords = PartialRainAverages | End

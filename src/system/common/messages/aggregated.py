from typing import TypeVar, Protocol
from dataclasses import dataclass

from common.messages import End

T = TypeVar("T", covariant=True)
U = TypeVar("U", contravariant=True)


@dataclass
class DateInfo:
    count: int
    average_duration: float


@dataclass
class PartialRainAverages:
    averages: dict[str, DateInfo]  # start_date -> DateInfo

    def be_handled_by(self, handler: "AggregatedHandler[T, PartialRainAverages]") -> T:
        return handler.handle_aggregated(self)


PartialRainRecords = PartialRainAverages | End


@dataclass
class PartialCityCounts:
    def be_handled_by(self, handler: "AggregatedHandler[T, PartialCityCounts]") -> T:
        return handler.handle_aggregated(self)


PartialCityRecords = PartialCityCounts | End


class AggregatedHandler(Protocol[T, U]):
    def handle_aggregated(self, aggregated: U) -> T:
        ...


GenericAggregatedRecord = TypeVar(
    "GenericAggregatedRecord",
    PartialRainAverages,
    PartialCityCounts,
    contravariant=True,
)

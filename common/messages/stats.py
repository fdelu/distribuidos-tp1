from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, TypeVar

T = TypeVar("T", covariant=True)


class StatType(StrEnum):
    RAIN = "rain"


# For 4_1_rained and 4_1_rained_reducer


@dataclass
class RainAverages:
    data: dict[str, float]  # date -> average duration

    def be_handled_by(self, handler: "StatHandler[T]") -> T:
        return handler.handle_rain_averages(self)


# For 4_2_


# ...


class StatHandler(Protocol[T]):
    def handle_rain_averages(self, averages: RainAverages) -> T:
        ...


StatsRecord = RainAverages

from threading import Lock
from dataclasses import dataclass

from common.messages.stats import RainAverages


@dataclass
class Stats:
    rain_averages: RainAverages | None = None
    lock: Lock = Lock()

    def all_done(self):
        return self.rain_averages is not None

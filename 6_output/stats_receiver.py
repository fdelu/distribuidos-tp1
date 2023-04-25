import json
import logging
from typing import Protocol
from dataclasses import dataclass
from threading import Lock
from common.messages.stats import RainAverages, StatType, StatsRecord

from config import Config
from comms import SystemCommunication


class StatListener(Protocol):
    def received(self, type: StatType):
        """
        This method is called when a new stat is received
        """
        ...


@dataclass
class Stats:
    rain_averages: dict[str, float] | None = None
    lock: Lock = Lock()


class StatsReceiver:
    comms: SystemCommunication
    stats: Stats
    listeners: list[StatListener] = []

    def __init__(self, config: Config):
        self.comms = SystemCommunication(config)
        self.stats = Stats()

    def add_listener(self, listener: StatListener):
        self.listeners.append(listener)

    def __notify_listeners(self, type: StatType):
        for listener in self.listeners:
            listener.received(type)

    def get(self, type: StatType) -> str | None:
        with self.stats.lock:
            result = getattr(self.stats, type.value)

        return json.dumps(result) if result else None

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()

    def handle_rain(self, stat: RainAverages):
        logging.info("Received rain averages")
        with self.stats.lock:
            self.stats.rain_averages = stat.data
        self.__notify_listeners(StatType.RAIN)

    def handle_record(self, record: StatsRecord):
        if isinstance(record, RainAverages):
            self.handle_rain(record)

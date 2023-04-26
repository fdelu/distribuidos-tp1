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
    rain_averages: RainAverages | None = None
    lock: Lock = Lock()

    def all_done(self):
        return self.rain_averages is not None


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
        result: StatsRecord | None = None
        with self.stats.lock:
            if type == StatType.RAIN:
                result = self.stats.rain_averages
            else:
                raise NotImplementedError()

        if result is None:
            return None
        return json.dumps(result.data)

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()

    def handle_rain_averages(self, stat: RainAverages):
        logging.info("Received rain averages")
        with self.stats.lock:
            self.stats.rain_averages = stat
        self.__notify_listeners(StatType.RAIN)

    def handle_record(self, record: StatsRecord):
        record.be_handled_by(self)
        if self.stats.all_done():
            self.comms.stop_consuming()
            logging.info("Received all stats, stopped consuming")

import logging
from typing import Protocol

from common.messages.stats import RainAverages, StatsRecord, StatType

from . import Stats
from ..config import Config
from ..comms import SystemCommunication


class StatListener(Protocol):
    def received(self, type: StatType):
        """
        This method is called when a new stat is received
        """
        ...


class StatsReceiver:
    comms: SystemCommunication
    stats: Stats
    listeners: list[StatListener] = []

    def __init__(self, config: Config, stats: Stats):
        self.comms = SystemCommunication(config)
        self.stats = stats

    def add_listener(self, listener: StatListener):
        self.listeners.append(listener)

    def __notify_listeners(self, type: StatType):
        for listener in self.listeners:
            listener.received(type)

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
            logging.info("Received all stats")

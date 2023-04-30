from typing import Generic, TypeVar, Protocol
import logging

from common.messages.rain import PartialRainRecords
from common.messages.stats import StatsRecord
from system.common.comms_base import SystemCommunicationBase

from ..rain.comms import SystemCommunication
from .config import Config


T = TypeVar("T")


class Reducer(Protocol[T]):
    def handle_aggregated(self, aggregated: T):
        ...

    def get_value(self) -> StatsRecord:
        ...


class ReductionHandler(Generic[T]):
    reducer: Reducer[T]
    config: Config
    comms: SystemCommunication
    ends_received: int

    def __init__(
        self,
        config: Config,
        reducer: Reducer[T],
        comms: SystemCommunicationBase[T, StatsRecord],
    ):
        self.comms = comms
        self.reducer = reducer
        self.ends_received = 0
        self.config = config

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()
        self.comms.close()

    def handle_aggregated(self, aggregated: T):
        self.reducer.handle_aggregated(aggregated)

    def handle_end(self):
        self.ends_received += 1
        if self.ends_received < self.config.aggregators_count:
            logging.debug(
                "An aggregator finished sending averages"
                f" ({self.ends_received}/{self.config.aggregators_count})"
            )
            return

        logging.info("All records reduced, stopping...")
        self.comms.send(self.reducer.get_value())
        self.comms.stop_consuming()

    def handle_record(self, record: PartialRainRecords):
        record.be_handled_by(self)

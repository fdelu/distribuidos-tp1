from typing import Generic, Protocol
import logging

from common.messages.aggregated import GenericAggregatedRecord
from common.messages.stats import StatsRecord
from common.comms_base import SystemCommunicationBase
from common.messages import End

from .config import Config


class Reducer(Protocol[GenericAggregatedRecord]):
    def handle_aggregated(self, aggregated: GenericAggregatedRecord):
        ...

    def get_value(self) -> StatsRecord:
        ...


class ReductionHandler(Generic[GenericAggregatedRecord]):
    reducer: Reducer[GenericAggregatedRecord]
    config: Config
    comms: SystemCommunicationBase[GenericAggregatedRecord | End, StatsRecord]
    ends_received: int

    def __init__(
        self,
        config: Config,
        reducer: Reducer[GenericAggregatedRecord],
        comms: SystemCommunicationBase[GenericAggregatedRecord | End, StatsRecord],
    ):
        self.comms = comms
        self.reducer = reducer
        self.ends_received = 0
        self.config = config

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()
        self.comms.close()

    def handle_aggregated(self, aggregated: GenericAggregatedRecord):
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

    def handle_record(self, record: GenericAggregatedRecord | End):
        record.be_handled_by(self)
